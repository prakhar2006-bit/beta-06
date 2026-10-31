"""Pure bounded three-valued logic. No network, SQL, LLM, logging or storage."""
from datetime import date
from decimal import Decimal
import operator
import re

from app.schemas.eligibility import (AnswerField, ConditionResult, EvaluationResponse,
    PolicyReview, Question, RuleSet, Text)


class InvalidAnswers(ValueError):
    def __init__(self, fields):
        self.fields = tuple(sorted(set(fields)))
        super().__init__('Invalid answer types or fields')


def localized(text: Text, language):
    return (text.hi, 'hi', False) if language == 'hi' and text.hi else (text.en, 'en', language != 'en')


def value_for(field: AnswerField, value):
    """No implicit Boolean/string/category or income-unit coercion."""
    if field.kind == 'boolean':
        if type(value) is not bool:
            raise ValueError('Expected Boolean')
    elif field.kind == 'category':
        if type(value) is not str or value not in field.choices:
            raise ValueError('Expected a reviewed category code')
    elif field.kind == 'age':
        if type(value) is not int or not 0 <= value <= 10**18:
            raise ValueError('Expected a nonnegative integer age at the reviewed reference date')
    else:
        if type(value) not in (int, float, str) or (type(value) is str and
                (field.kind != 'income' or not re.fullmatch(r'[0-9]{1,19}(?:\.[0-9]{1,6})?', value))):
            raise ValueError('Expected numeric answer')
        value = Decimal(str(value))
        if not value.is_finite() or abs(value) > 10**18 or field.kind == 'income' and value < 0:
            raise ValueError('Numeric value outside supported bounds')
        if field.kind == 'income' and value.as_tuple().exponent < -6:
            raise ValueError('Income precision exceeds six decimal places; no rounding is performed')
    return value


def expected_for(node, field):
    if node.operator in ('gt', 'gte', 'lt', 'lte') and field.kind not in ('age', 'income', 'number'):
        raise ValueError('Ordering is numeric only')
    if isinstance(node.expected_value, tuple):
        return tuple(value_for(field, v) for v in node.expected_value)
    return value_for(field, node.expected_value)


COMPARE = {'eq': operator.eq, 'ne': operator.ne, 'gt': operator.gt,
           'gte': operator.ge, 'lt': operator.lt, 'lte': operator.le,
           'in': lambda value, expected: value in expected,
           'not_in': lambda value, expected: value not in expected}
INVERSE = {'eq': 'ne', 'ne': 'eq', 'gt': 'lte', 'gte': 'lt', 'lt': 'gte',
           'lte': 'gt', 'in': 'not_in', 'not_in': 'in'}


def _conflicting_mandatory_clauses(root, children, expected, fields):
    """Find impossible unconditional AND bounds/sets; do not flatten OR branches."""
    clauses = []

    def collect(node):
        if node.node_type == 'and':
            for child in children[node.rule_id]:
                collect(child)
        elif node.node_type == 'predicate' and node.rule_id in expected:
            clauses.append((node.attribute, node.operator, expected[node.rule_id]))
        elif node.node_type == 'not':
            child = children[node.rule_id][0]
            if child.node_type == 'predicate' and child.rule_id in expected:
                clauses.append((child.attribute, INVERSE[child.operator], expected[child.rule_id]))

    collect(root)
    for attribute in sorted({a for a, _, _ in clauses}):
        field = fields[attribute]
        allowed = set(field.choices) if field.kind == 'category' else {True, False} if field.kind == 'boolean' else None
        forbidden, lower, upper = set(), None, None
        for a, op, value in clauses:
            if a != attribute:
                continue
            if op in ('eq', 'in'):
                values = set(value) if op == 'in' else {value}
                allowed = values if allowed is None else allowed & values
            elif op in ('ne', 'not_in'):
                forbidden.update(value if op == 'not_in' else (value,))
            elif op in ('gt', 'gte'):
                bound = (value, op == 'gte')
                if lower is None or value > lower[0] or value == lower[0] and not bound[1]:
                    lower = bound
            elif op in ('lt', 'lte'):
                bound = (value, op == 'lte')
                if upper is None or value < upper[0] or value == upper[0] and not bound[1]:
                    upper = bound
        if lower and upper and (lower[0] > upper[0] or lower[0] == upper[0] and not (lower[1] and upper[1])):
            return True
        if field.kind == 'age' and lower and upper and lower[0] + (not lower[1]) > upper[0] - (not upper[1]):
            return True
        if allowed is not None:
            allowed -= forbidden
            if lower:
                allowed = {v for v in allowed if v > lower[0] or lower[1] and v == lower[0]}
            if upper:
                allowed = {v for v in allowed if v < upper[0] or upper[1] and v == upper[0]}
            if not allowed:
                return True
        elif lower and upper and lower == upper and lower[0] in forbidden:
            return True
    return False


MESSAGES = {
    'en': {
        'MATCHED': 'This condition is satisfied.', 'NOT_MATCHED': 'This condition is not satisfied.',
        'MISSING_ANSWER': 'An answer is still needed.', 'RULE_NOT_APPROVED': 'This rule is disabled or unverified.',
        'APPLICABILITY_UNKNOWN': 'The applicability of this rule has not been confirmed.',
        'OUTSIDE_EFFECTIVE_PERIOD': 'This rule is outside its approved effective period.',
        'SOURCE_NOT_VERIFIED': 'A checked supporting source is required.',
        'RULE_DEFINITION_INVALID': 'The rule definition needs policy review.',
        'PARENT_NOT_APPROVED': 'The containing rule group cannot be evaluated safely.',
        'POLICY_BLOCKED': 'Policy review is required before this condition can be evaluated.',
        'GROUP_SATISFIED': 'This rule group is satisfied.',
        'GROUP_FAILED': 'This rule group is not satisfied.',
        'GROUP_UNKNOWN': 'This group cannot be resolved from the approved conditions and available answers.',
        'ELIGIBLE': 'The complete approved rule set is satisfied for the stated answers. This is not enrolment or a provider approval.',
        'INELIGIBLE': 'A verified, applicable mandatory condition is not satisfied under this approved rule set.',
        'NEEDS_VERIFICATION': 'Eligibility cannot be confirmed. Missing answers or policy review may still be required.',
    },
    'hi': {
        'MATCHED': 'यह शर्त पूरी होती है।', 'NOT_MATCHED': 'यह शर्त पूरी नहीं होती।',
        'MISSING_ANSWER': 'इस प्रश्न का उत्तर अभी आवश्यक है।', 'RULE_NOT_APPROVED': 'यह नियम निष्क्रिय है या सत्यापित नहीं है।',
        'APPLICABILITY_UNKNOWN': 'इस नियम के लागू होने की पुष्टि नहीं हुई है।',
        'OUTSIDE_EFFECTIVE_PERIOD': 'यह नियम अपनी स्वीकृत प्रभावी अवधि के बाहर है।',
        'SOURCE_NOT_VERIFIED': 'जाँचा गया सहायक स्रोत आवश्यक है।',
        'RULE_DEFINITION_INVALID': 'नियम की परिभाषा की समीक्षा आवश्यक है।',
        'PARENT_NOT_APPROVED': 'इस नियम समूह का सुरक्षित मूल्यांकन संभव नहीं है।',
        'POLICY_BLOCKED': 'इस शर्त के मूल्यांकन से पहले नीति की समीक्षा आवश्यक है।',
        'GROUP_SATISFIED': 'यह नियम समूह पूरा होता है।', 'GROUP_FAILED': 'यह नियम समूह पूरा नहीं होता।',
        'GROUP_UNKNOWN': 'स्वीकृत शर्तों और उपलब्ध उत्तरों से इस समूह का निष्कर्ष नहीं निकाला जा सकता।',
        'ELIGIBLE': 'दिए गए उत्तरों के लिए पूरा स्वीकृत नियम समूह संतुष्ट है। यह नामांकन या प्रदाता की मंज़ूरी नहीं है।',
        'INELIGIBLE': 'स्वीकृत नियम समूह की एक सत्यापित और लागू अनिवार्य शर्त पूरी नहीं होती।',
        'NEEDS_VERIFICATION': 'पात्रता की पुष्टि नहीं हो सकती। कुछ उत्तर या नीति की समीक्षा अभी आवश्यक हो सकती है।',
    },
}


def evaluate(rule_set: RuleSet | None, scheme_id: str, answers: dict, language='en', *, as_of: date):
    """All returned facts derive from the supplied trusted rule set; no answers echoed."""
    if rule_set is None:
        return EvaluationResponse(scheme_id=scheme_id, language=language, status='NEEDS_VERIFICATION',
            policy_review=PolicyReview(publication_status='unavailable', approval_status='unavailable',
                execution_enabled=False, complete=False, applicable=False, blockers=('RULE_SET_UNAVAILABLE',)),
            explanation=MESSAGES[language]['NEEDS_VERIFICATION'])
    if rule_set.scheme_id != scheme_id:
        raise ValueError('Provider returned a different scheme')
    nodes = {n.rule_id: n for n in rule_set.nodes}
    fields = {f.key: f for f in rule_set.fields}
    sources = {s.reference_id: s for s in rule_set.sources}
    children = {n.rule_id: sorted([c for c in rule_set.nodes if c.parent_id == n.rule_id], key=lambda c: c.rule_id)
                for n in rule_set.nodes}
    root = next(n for n in rule_set.nodes if n.parent_id is None)
    blockers = []
    if rule_set.publication_status != 'published': blockers.append('SCHEME_UNPUBLISHED')
    if rule_set.approval_status != 'approved' or not rule_set.execution_enabled: blockers.append('EXECUTION_NOT_APPROVED')
    if not rule_set.reviewer_reference or not rule_set.reviewed_on or rule_set.reviewed_on > as_of:
        blockers.append('REVIEW_NOT_CONFIRMED')
    applicable = (rule_set.applicability_confirmed and rule_set.effective_from is not None
                  and rule_set.effective_from <= as_of and (rule_set.effective_to is None or as_of <= rule_set.effective_to))
    if not applicable: blockers.append('POLICY_APPLICABILITY_UNKNOWN')
    if rule_set.review_valid_until and as_of > rule_set.review_valid_until: blockers.append('REVIEW_EXPIRED')
    if rule_set.conflicts: blockers.append('POLICY_CONFLICT')
    globally_blocked = bool(blockers)

    expected, readiness = {}, {}
    for node in rule_set.nodes:
        reason = None
        if not node.enabled or node.confidence != 'VERIFIED': reason = 'RULE_NOT_APPROVED'
        elif not node.applicability_confirmed: reason = 'APPLICABILITY_UNKNOWN'
        elif node.effective_from and as_of < node.effective_from or node.effective_to and as_of > node.effective_to:
            reason = 'OUTSIDE_EFFECTIVE_PERIOD'
        elif node.node_type == 'predicate':
            if not node.source_ids or any(sources[s].last_checked_date > as_of for s in node.source_ids):
                reason = 'SOURCE_NOT_VERIFIED'
            else:
                try: expected[node.rule_id] = expected_for(node, fields[node.attribute])
                except (ValueError, TypeError, ArithmeticError): reason = 'RULE_DEFINITION_INVALID'
        readiness[node.rule_id] = reason

    # Only ready predicates can establish a contradiction. Disabled proposals are not facts.
    if not globally_blocked and _conflicting_mandatory_clauses(root, children, expected, fields):
        blockers.append('POLICY_CONFLICT')
        globally_blocked = True

    normalized = {}
    if not globally_blocked:
        invalid = set(answers) - set(fields)
        for key, value in answers.items():
            if key not in fields or value is None:
                continue
            try: normalized[key] = value_for(fields[key], value)
            except (ValueError, TypeError, ArithmeticError): invalid.add(key)
        if invalid: raise InvalidAnswers(invalid)

    evaluated, missing = {}, set()

    def visit(node, parent_blocked=False):
        reason = 'POLICY_BLOCKED' if globally_blocked else 'PARENT_NOT_APPROVED' if parent_blocked else readiness[node.rule_id]
        results = [visit(child, parent_blocked or bool(reason)) for child in children[node.rule_id]]
        truth = 'UNKNOWN'
        if reason is None:
            if node.node_type == 'predicate':
                if node.attribute not in normalized:
                    reason = 'MISSING_ANSWER'; missing.add(node.attribute)
                else:
                    truth = 'SATISFIED' if COMPARE[node.operator](normalized[node.attribute], expected[node.rule_id]) else 'FAILED'
                    reason = 'MATCHED' if truth == 'SATISFIED' else 'NOT_MATCHED'
            else:
                if node.node_type == 'and':
                    truth = 'FAILED' if 'FAILED' in results else 'UNKNOWN' if 'UNKNOWN' in results else 'SATISFIED'
                elif node.node_type == 'or':
                    truth = 'SATISFIED' if 'SATISFIED' in results else 'UNKNOWN' if 'UNKNOWN' in results else 'FAILED'
                else:
                    truth = {'SATISFIED': 'FAILED', 'FAILED': 'SATISFIED', 'UNKNOWN': 'UNKNOWN'}[results[0]]
                reason = {'SATISFIED': 'GROUP_SATISFIED', 'FAILED': 'GROUP_FAILED', 'UNKNOWN': 'GROUP_UNKNOWN'}[truth]
        label, actual_language, fallback = localized(node.label, language)
        evaluated[node.rule_id] = ConditionResult(rule_id=node.rule_id, node_type=node.node_type,
            attribute=node.attribute, result=truth, reason_code=reason, label=label,
            explanation=MESSAGES[language][reason], content_language=actual_language,
            translation_fallback=fallback, source_ids=node.source_ids)
        return truth

    root_result = visit(root)
    for node in rule_set.nodes:
        if readiness[node.rule_id]: blockers.append(readiness[node.rule_id] + ':' + node.rule_id)
    if not rule_set.complete: blockers.append('INCOMPLETE_RULE_SET')
    if rule_set.unresolved_conditions: blockers.append('UNRESOLVED_POLICY_CONDITIONS')
    status = 'NEEDS_VERIFICATION'
    if not globally_blocked:
        if root_result == 'FAILED' and (rule_set.complete or rule_set.root_failure_is_decisive):
            status = 'INELIGIBLE'
        elif root_result == 'SATISFIED' and not blockers:
            status = 'ELIGIBLE'

    questions = []
    if status == 'NEEDS_VERIFICATION' and root_result == 'UNKNOWN' and not globally_blocked:
        needed = set()

        def needed_answers(node):
            result = evaluated[node.rule_id]
            if result.result != 'UNKNOWN':
                return
            if result.reason_code == 'MISSING_ANSWER':
                needed.add(node.attribute)
            elif result.reason_code == 'GROUP_UNKNOWN':
                for child in children[node.rule_id]:
                    needed_answers(child)

        needed_answers(root)
        for key in sorted(needed):
            rule_ids = tuple(sorted(r.rule_id for r in evaluated.values() if r.attribute == key and r.reason_code == 'MISSING_ANSWER'))
            field = fields[key]
            text, actual_language, fallback = localized(field.question, language)
            questions.append(Question(attribute=key, rule_ids=rule_ids, text=text, kind=field.kind,
                choices=field.choices, unit=field.unit, period=field.period, scope=field.scope,
                reference_basis=field.reference_basis, content_language=actual_language, translation_fallback=fallback))
    results = tuple(evaluated[key] for key in sorted(evaluated))
    return EvaluationResponse(scheme_id=scheme_id, rule_set_version=rule_set.version, language=language, status=status,
        policy_review=PolicyReview(publication_status=rule_set.publication_status, approval_status=rule_set.approval_status,
            execution_enabled=rule_set.execution_enabled, complete=rule_set.complete, applicable=applicable,
            reviewed_on=rule_set.reviewed_on, blockers=tuple(sorted(set(blockers)))),
        evaluated_conditions=results, satisfied_rules=tuple(r.rule_id for r in results if r.result == 'SATISFIED'),
        failed_rules=tuple(r.rule_id for r in results if r.result == 'FAILED'),
        unknown_conditions=tuple(r.rule_id for r in results if r.result == 'UNKNOWN'),
        missing_answers=tuple(sorted(missing)), questions_needed=tuple(questions), sources=rule_set.sources,
        explanation=MESSAGES[language][status])
