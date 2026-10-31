"""Stateless orchestration around Phase 4A. No session store, tokens or IO."""
from datetime import date
from hashlib import sha256

from app.core.errors import APIError
from app.eligibility.engine import InvalidAnswers, evaluate, value_for
from app.schemas.eligibility import RuleSet
from app.schemas.eligibility import Question
from app.schemas.questionnaire import (AnswerRequest, CurrentQuestion, MissingInformation,
    Progress, QuestionnaireResponse, QuestionnaireState, StartRequest)


def resolve(provider, scheme_id):
    rules = provider.get_rule_set(scheme_id)
    if rules is not None and (not isinstance(rules, RuleSet) or rules.scheme_id != scheme_id):
        raise APIError(503, 'RULE_SET_INVALID', 'Approved rule definitions are unavailable.')
    return rules


def fingerprint(rules):
    # Public version binding only, not a signature/authentication or proof of truth.
    return sha256(rules.model_dump_json().encode('utf-8')).hexdigest() if rules else None


def validate_state(state, rules):
    if state.policy_fingerprint != fingerprint(rules):
        raise APIError(409, 'POLICY_CHANGED', 'The policy changed. Start a new questionnaire.')
    used = set(state.answers) | set(state.skipped)
    fields = {f.key: f for f in rules.fields} if rules else {}
    referenced = {n.attribute for n in rules.nodes if n.attribute is not None} if rules else set()
    if used - referenced:
        raise APIError(422, 'INVALID_STATE', 'The answer state does not match the reviewed questions.')
    try:
        for key, value in state.answers.items():
            if value is not None:
                value_for(fields[key], value)
    except (ValueError, TypeError, ArithmeticError):
        raise APIError(422, 'INVALID_ANSWERS', 'Answer fields or types do not match the reviewed questions.') from None


def present(question, rules, language):
    field = next(f for f in rules.fields if f.key == question.attribute)
    reviewed = field.question_reviewed_languages
    if language == 'hi' and 'hi' in reviewed and field.question.hi:
        text, actual_language = field.question.hi, 'hi'
    elif 'en' in reviewed:
        text, actual_language = field.question.en, 'en'
    else:
        return None
    nodes = {n.rule_id: n for n in rules.nodes}
    source_ids = tuple(sorted({source for rule in question.rule_ids for source in nodes[rule].source_ids}))
    return CurrentQuestion(**(question.model_dump() | {
        'text': text, 'content_language': actual_language, 'translation_fallback': actual_language != language}),
        question_id=question.attribute,
        answer_type={'age': 'integer', 'income': 'decimal', 'number': 'number', 'category': 'category', 'boolean': 'boolean'}[question.kind],
        allowed_values=(True, False) if question.kind == 'boolean' else question.choices,
        source_ids=source_ids)


def priority(question, rules):
    """Reviewed NOT paths, rule coverage, answer burden, then stable field key."""
    nodes = {n.rule_id: n for n in rules.nodes}
    under_not = False
    for rule_id in question.rule_ids:
        current = nodes[rule_id]
        while current.parent_id is not None:
            current = nodes[current.parent_id]
            under_not |= current.node_type == 'not'
    burden = {'boolean': 0, 'age': 1, 'category': 2, 'number': 3, 'income': 4}
    return (not under_not, -len(question.rule_ids), burden[question.kind], question.attribute)


def render(state, rules, *, as_of: date):
    validate_state(state, rules)
    try:
        evaluation = evaluate(rules, state.scheme_id, state.answers, state.language, as_of=as_of)
    except InvalidAnswers:
        raise APIError(422, 'INVALID_ANSWERS', 'Answer fields or types do not match the reviewed questions.') from None
    candidates, unreviewed = [], []
    if rules:
        for question in evaluation.questions_needed:
            # Null is an explicit unknown; skip is a separate disposition. Neither is re-asked.
            if question.attribute in state.answers or question.attribute in state.skipped:
                continue
            displayed = present(question, rules, state.language)
            if displayed is None:
                unreviewed.append(question.attribute)
            else:
                candidates.append(displayed)
    candidates.sort(key=lambda q: priority(q, rules))
    # Do not leak unreviewed translations or disposed questions through the
    # nested evaluator DTO. Only current, reviewed candidate prompts are exposed.
    evaluation = evaluation.model_copy(update={'questions_needed': tuple(
        Question(**{key: value for key, value in q.model_dump().items() if key in Question.model_fields})
        for q in candidates)})
    current = candidates[0] if candidates else None
    definitive = evaluation.status in ('ELIGIBLE', 'INELIGIBLE')
    # The evaluator supplies no questions for definitive outcomes.
    reason = 'DECISION_REACHED' if definitive else 'QUESTIONS_REMAIN' if current else 'VERIFICATION_REQUIRED'
    unknown = tuple(sorted(k for k, value in state.answers.items() if value is None))
    unanswered = tuple(sorted(k for k in evaluation.missing_answers if k not in state.answers and k not in state.skipped))
    blockers = set(evaluation.policy_review.blockers)
    if unreviewed:
        blockers.add('QUESTION_TEXT_NOT_REVIEWED')
    return QuestionnaireResponse(state=state, current_question=current, completed=current is None,
        completion_reason=reason,
        progress=Progress(answered=len(state.answers)-len(unknown), unknown=len(unknown), skipped=len(state.skipped), remaining=len(candidates)),
        missing_information=MissingInformation(unanswered_fields=unanswered, unknown_fields=unknown,
            skipped_fields=tuple(sorted(state.skipped)), unreviewed_question_fields=tuple(sorted(unreviewed)),
            review_blockers=tuple(sorted(blockers))), evaluation=evaluation)


def start(request: StartRequest, provider, *, as_of: date):
    rules = resolve(provider, request.scheme_id)
    state = QuestionnaireState(scheme_id=request.scheme_id, language=request.language, policy_fingerprint=fingerprint(rules))
    return render(state, rules, as_of=as_of)


def next_question(state: QuestionnaireState, provider, *, as_of: date):
    return render(state, resolve(provider, state.scheme_id), as_of=as_of)


def answer(request: AnswerRequest, provider, *, as_of: date):
    state = request.state
    rules = resolve(provider, state.scheme_id)
    before = render(state, rules, as_of=as_of)
    previously_answered = request.question_id in state.answers or request.question_id in state.skipped
    if not previously_answered and request.question_id in before.missing_information.unreviewed_question_fields:
        raise APIError(409, 'QUESTION_NOT_REVIEWED', 'Reviewed question text is unavailable.')
    currently_pending = {q.attribute for q in before.evaluation.questions_needed}
    # A change can reopen a completed questionnaire; a new arbitrary field cannot.
    if not previously_answered and (request.question_id not in currently_pending or request.action == 'clear'):
        raise APIError(409, 'QUESTION_NOT_PENDING', 'This question is not pending or previously answered.')
    answers, skipped = dict(state.answers), set(state.skipped)
    answers.pop(request.question_id, None)
    skipped.discard(request.question_id)
    if request.action == 'answer':
        answers[request.question_id] = request.value
    elif request.action == 'skip':
        skipped.add(request.question_id)
    # Revalidate rather than using model_copy(update=...), which bypasses validators.
    updated = QuestionnaireState(**(state.model_dump() | {'answers': answers, 'skipped': tuple(sorted(skipped))}))
    return render(updated, rules, as_of=as_of)
