"""Local source-based advice, separate from approved published-policy execution.

Uses the existing engine's bounded types and comparison primitives. Never loads
draft rule proposals, creates approval attestations or returns ELIGIBLE.
"""
from datetime import date, timedelta
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.core.errors import APIError
from app.eligibility.engine import COMPARE, expected_for, value_for
from app.schemas.eligibility import AnswerField, SourceReference
from app.schemas.questionnaire import QuestionnaireState

CATALOG = Path(__file__).resolve().parents[3] / 'data/schemes/preliminary-screening.json'
ADDITIONS = Path(__file__).resolve().parent / 'data/preliminary-additions.json'
MESSAGES = {
    'en': {
        'ELIGIBLE_LIKELY': 'Your answers meet the listed entry conditions. You are likely to be eligible to apply; the provider must verify your documents and enrolment.',
        'NOT_ELIGIBLE_LIKELY': 'Your answers do not meet at least one listed entry condition. Review the explanation before contacting the provider.',
        'NEEDS_VERIFICATION': 'We cannot give a clear preliminary result. The unanswered or exceptional conditions below need confirmation.',
        'notice': 'Preliminary guidance only — not government approval, enrolment or guaranteed payment. The official provider makes the final decision.',
        'information': 'Information from official sources. Confirm current requirements with the provider.',
        'unavailable': 'This information is not yet confirmed. Ask the official implementing agency.',
        'partial_documents': 'This is a partial checklist. Ask the official provider for its current document requirements.',
        'matched': 'This entry condition is met by your answer.',
        'failed': 'This entry condition is not met by your answer.',
        'unknown': 'Confirm this condition with the provider or update your answer.',
    },
    'hi': {
        'ELIGIBLE_LIKELY': 'आपके उत्तर दी गई प्रवेश शर्तों को पूरा करते हैं। आप आवेदन के लिए संभवतः पात्र हैं; संस्था को दस्तावेज़ और नामांकन की पुष्टि करनी होगी।',
        'NOT_ELIGIBLE_LIKELY': 'आपके उत्तर कम से कम एक प्रवेश शर्त को पूरा नहीं करते। संस्था से संपर्क करने से पहले नीचे कारण देखें।',
        'NEEDS_VERIFICATION': 'अभी स्पष्ट प्रारंभिक नतीजा देना संभव नहीं है। नीचे दिए अधूरे उत्तरों या विशेष स्थितियों की पुष्टि आवश्यक है।',
        'notice': 'केवल प्रारंभिक मार्गदर्शन — सरकारी मंज़ूरी, नामांकन या भुगतान की गारंटी नहीं। अंतिम निर्णय आधिकारिक संस्था करती है।',
        'information': 'आधिकारिक स्रोतों पर आधारित जानकारी। वर्तमान आवश्यकताएँ संस्था से पुष्ट करें।',
        'unavailable': 'इस जानकारी की अभी पुष्टि नहीं हुई है। आधिकारिक कार्यान्वयन संस्था से पूछें।',
        'partial_documents': 'यह आंशिक सूची है। वर्तमान दस्तावेज़ आवश्यकताओं के लिए आधिकारिक संस्था से पूछें।',
        'matched': 'आपके उत्तर के अनुसार यह प्रवेश शर्त पूरी होती है।',
        'failed': 'आपके उत्तर के अनुसार यह प्रवेश शर्त पूरी नहीं होती।',
        'unknown': 'संस्था से इस शर्त की पुष्टि करें या अपना उत्तर बदलें।',
    },
}


def localized(text, language):
    return text[language]


@lru_cache(maxsize=2)
def catalog(*, include_additions=False):
    """Preserve five-guide inventory callers; runtime explicitly loads all fifteen."""
    data = json.loads(CATALOG.read_text(encoding='utf-8'))
    if data['format'] != 'preliminary-screening-v1':
        raise ValueError('Unsupported preliminary content')
    date.fromisoformat(data['checked_on'])
    # Preserve the original five guides verbatim, including their fingerprints.
    if len(data['schemes']) != 5:
        raise ValueError('Incomplete original preliminary content')
    if include_additions:
        extra = json.loads(ADDITIONS.read_text(encoding='utf-8'))
        if (extra['format'] != 'preliminary-screening-extension-v1' or len(extra['schemes']) != 10
                or set(data['sources']) & set(extra['sources'])):
            raise ValueError('Invalid preliminary extension')
        for policy in extra['schemes']:
            # These are deliberately incomplete screens, never positive approvals.
            if policy.get('preliminary_complete') is not False or not policy.get('verification_requirements'):
                raise ValueError('Incomplete guides require explicit verification gates')
            date.fromisoformat(policy['checked_on'])
        data = data | {'sources': data['sources'] | extra['sources'], 'schemes': data['schemes'] + extra['schemes']}
    policies = {p['scheme_id']: p for p in data['schemes']}
    expected_ids = ({f'in-cen-{i:06}' for i in range(1,16)} if include_additions else
                    {'in-cen-000001','in-cen-000002','in-cen-000003','in-cen-000007','in-cen-000008'})
    if len(policies) != len(data['schemes']) or set(policies) != expected_ids:
        raise ValueError('Duplicate or incomplete preliminary content')
    for policy in policies.values():
        if policy['scope'] != 'new_enrolment_preliminary' or policy['human_publication_approved'] is not False:
            raise ValueError('This feature cannot supply publication approval')
        keys = set()
        for field in policy['fields']:
            if field['key'] in keys or not field['source_ids'] or not field['predicates']:
                raise ValueError('Duplicate or uncited question')
            if field.get('failure_outcome', 'fail') not in ('fail', 'verify'):
                raise ValueError('Unsupported failure outcome')
            if field.get('failure_outcome') == 'verify' and not field.get('manual_reason'):
                raise ValueError('Manual checks require explanations')
            keys.add(field['key'])
            typed = answer_field(field)
            for condition in field['predicates']:
                if condition['operator'] not in COMPARE:
                    raise ValueError('Unsupported comparison')
                expected_for(SimpleNamespace(**condition), typed)
        for source_id in source_ids(policy):
            source = data['sources'][source_id]
            SourceReference(**{k: source[k] for k in SourceReference.model_fields if k in source})
            host = urlsplit(source['original_url']).hostname
            if not (host.endswith(('.gov.in', '.nic.in')) or host == 'www.pfrda.org.in'):
                raise ValueError('Unsupported source host')
    return data, policies


def answer_field(field):
    return AnswerField(key=field['key'], kind=field['kind'], question=field['question'],
        # Reuse strict answer typing, without creating translation attestations
        # that could later be mistaken for published-policy question approval.
        question_reviewed_languages=(),
        choices=tuple(field.get('choices', ())),
        reference_basis='Completed years on planned enrolment day' if field['kind'] == 'age' else None,
        unit='INR' if field['kind'] == 'income' else field.get('unit'),
        period='monthly' if field['kind'] == 'income' else None,
        scope='individual' if field['kind'] == 'income' else None)


def source_ids(policy):
    groups = policy['fields'] + policy['benefits'] + policy['documents'] + [policy['application']]
    return sorted({s for group in groups for s in group['source_ids']})


def policy_for(scheme_id, as_of=None):
    data, policies = catalog(include_additions=True)
    policy = policies.get(scheme_id)
    if policy is not None and as_of is not None:
        checked = date.fromisoformat(policy.get('checked_on', data['checked_on']))
        if not checked <= as_of <= checked + timedelta(days=90):
            raise APIError(503, 'PRELIMINARY_REVIEW_REQUIRED', 'The source-based guide needs a fresh review.')
    return policy


def fingerprint(policy):
    data, _ = catalog(include_additions=True)
    bound = {'policy': policy, 'sources': {key: data['sources'][key] for key in source_ids(policy)}}
    return sha256(json.dumps(bound, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sources_for(policy):
    data, _ = catalog(include_additions=True)
    return [{k: source[k] for k in SourceReference.model_fields if k in source}
            for key in source_ids(policy) for source in [data['sources'][key]]]


def canonical_url(url):
    parsed = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in ('fbclid', 'gclid')]
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or '/', urlencode(sorted(query)), ''))


def distinct_sources(sources):
    result = {}
    for source in sources:
        key = canonical_url(source['original_url'])
        ref = source.get('reference_id', source.get('id'))
        if key in result:
            result[key]['reference_ids'].append(ref)
        else:
            result[key] = dict(source, reference_ids=[ref])
    return list(result.values())


def render(state, *, as_of):
    policy = policy_for(state.scheme_id, as_of)
    if policy is None:
        raise APIError(404, 'SCREENING_UNAVAILABLE', 'Preliminary screening is not available for this scheme.')
    if state.policy_fingerprint != fingerprint(policy):
        raise APIError(409, 'POLICY_CHANGED', 'The guide changed. Start a new questionnaire.')
    definitions = {f['key']: f for f in policy['fields']}
    if (set(state.answers) | set(state.skipped)) - set(definitions):
        raise APIError(422, 'INVALID_STATE', 'The answer state contains an unrelated field.')
    normalized = {}
    try:
        for key, value in state.answers.items():
            if value is not None:
                normalized[key] = value_for(answer_field(definitions[key]), value)
    except (ValueError, TypeError, ArithmeticError):
        raise APIError(422, 'INVALID_ANSWERS', 'The answer does not match the question type.') from None

    language = state.language
    conditions, candidates, manual = [], [], []
    failed = False
    for field in policy['fields']:
        key = field['key']
        reason = 'unknown'
        result = 'UNKNOWN'
        if key in normalized:
            typed = answer_field(field)
            matches = all(COMPARE[c['operator']](normalized[key], expected_for(SimpleNamespace(**c), typed))
                          for c in field['predicates'])
            exceptional = normalized[key] in field.get('manual_values', [])
            if exceptional or not matches and field.get('failure_outcome') == 'verify':
                manual.append(localized(field['manual_reason'], language))
            else:
                result = 'SATISFIED' if matches else 'FAILED'
                reason = 'matched' if matches else 'failed'
                failed |= not matches
        elif key not in state.answers and key not in state.skipped:
            candidates.append(field)
        conditions.append(dict(rule_id='preliminary-' + key, node_type='predicate', attribute=key,
            result=result, reason_code=reason.upper(), label=localized(field['label'], language),
            explanation=MESSAGES[language][reason], content_language=language, translation_fallback=False,
            source_ids=field['source_ids']))

    # All checks are necessary AND conditions. A known failure or unresolvable
    # provider-only exception makes further questions unnecessary.
    if failed or manual:
        candidates = []
    unknown = [c for c in conditions if c['result'] == 'UNKNOWN']
    complete = policy.get('preliminary_complete', True)
    status = ('NOT_ELIGIBLE_LIKELY' if failed else 'ELIGIBLE_LIKELY'
              if complete and not unknown and not manual else 'NEEDS_VERIFICATION')
    current = None
    if candidates:
        field = candidates[0]
        current = dict(question_id=field['key'], attribute=field['key'], rule_ids=['preliminary-' + field['key']],
            text=localized(field['question'], language), kind=field['kind'], choices=field.get('choices', []), unit=field.get('unit'),
            period=None, scope=None, reference_basis=None, content_language=language, translation_fallback=False,
            answer_type={'age': 'integer', 'income': 'decimal', 'number': 'number', 'category': 'category',
                         'boolean': 'boolean'}[field['kind']],
            allowed_values=[True, False] if field['kind'] == 'boolean' else field.get('choices', []), source_ids=field['source_ids'])
    unknown_fields = [k for k, v in state.answers.items() if v is None]
    missing = dict(unanswered_fields=[f['key'] for f in candidates], unknown_fields=unknown_fields,
                   skipped_fields=list(state.skipped), unreviewed_question_fields=[],
                   review_blockers=[] if complete else ['INCOMPLETE_PRELIMINARY_CRITERIA'])
    if not candidates and not failed and not complete:
        manual.extend(localized(reason, language) for reason in policy['verification_requirements'])
    evaluation = dict(scheme_id=state.scheme_id, status=status, language=language,
        rule_set_version=fingerprint(policy), evaluated_conditions=conditions,
        sources=sources_for(policy), explanation=MESSAGES[language][status], scope='preliminary_only',
        policy_review=dict(publication_status='draft', approval_status='not_publication_approved',
                           execution_enabled=False, complete=False, applicable=True))
    return dict(schema_version='1.0', state=state.model_dump(mode='json'), current_question=current,
        field_labels={f['key']:localized(f['label'],language) for f in policy['fields']},
        completed=current is None, completion_reason='QUESTIONS_REMAIN' if current else
        'VERIFICATION_REQUIRED' if status == 'NEEDS_VERIFICATION' else 'DECISION_REACHED',
        progress=dict(answered=len(state.answers)-len(unknown_fields), unknown=len(unknown_fields),
                      skipped=len(state.skipped), remaining=len(candidates)),
        missing_information=missing, missing_information_labels=manual + [c['label'] for c in unknown
            if c['attribute'] in state.answers or c['attribute'] in state.skipped], evaluation=evaluation)


def start(request, *, as_of):
    policy = policy_for(request.scheme_id, as_of)
    if policy is None:
        raise APIError(404, 'SCREENING_UNAVAILABLE', 'Preliminary screening is not available for this scheme.')
    return render(QuestionnaireState(scheme_id=request.scheme_id, language=request.language,
                  policy_fingerprint=fingerprint(policy)), as_of=as_of)


def answer(request, *, as_of):
    before = render(request.state, as_of=as_of)
    old = request.state
    previous = request.question_id in old.answers or request.question_id in old.skipped
    if not previous and (request.action == 'clear' or not before['current_question']
                        or request.question_id != before['current_question']['question_id']):
        raise APIError(409, 'QUESTION_NOT_PENDING', 'This question is not pending or previously answered.')
    answers, skipped = dict(old.answers), set(old.skipped)
    answers.pop(request.question_id, None)
    skipped.discard(request.question_id)
    if request.action == 'answer':
        answers[request.question_id] = request.value
    elif request.action == 'skip':
        skipped.add(request.question_id)
    state = QuestionnaireState(**(old.model_dump() | {'answers': answers, 'skipped': tuple(sorted(skipped))}))
    return render(state, as_of=as_of)


def shown(text, language, source_ids=()):
    return dict(text=localized(text, language), requested_language=language, content_language=language,
        translation_fallback=False, review_status='source_checked', origin='project_authored',
        is_official_translation=False, source_ids=source_ids)


def detail_content(policy, language):
    return dict(name=localized(policy['name'], language), description=localized(policy['overview'], language),
        language=language, translation_fallback=False,
        benefit_highlight=localized(policy['benefit_highlight'], language), audience=localized(policy['audience'], language),
        screening_available=True, screening_scope='new_enrolment_preliminary',
        translation_origin=policy['translation_origin'], government_policy_execution_enabled=False,
        benefits=[dict(description=shown(b['text'],language,b['source_ids']),source_ids=b['source_ids']) for b in policy['benefits']],
        criteria=[dict(text=localized(f['label'], language),source_ids=f['source_ids']) for f in policy['fields']],
        required_documents=[dict(title=shown(d['text'],language,d['source_ids']),requirement=d['requirement'],
                                 source_ids=d['source_ids']) for d in policy['documents']],
        application_guidance=dict(steps=[shown(t,language,policy['application']['source_ids']) for t in policy['application']['steps']],
            url=policy['application']['url'],link_kind=policy['application']['link_kind']),
        manual_notes=[localized(t,language) for t in policy['manual_notes']],
        assessment_notice=MESSAGES[language]['notice'], sources=distinct_sources(sources_for(policy)),
        last_checked_date=policy.get('checked_on', catalog()[0]['checked_on']))


def explain(state, *, as_of):
    q = render(state, as_of=as_of)
    if not q['completed']:
        raise APIError(409, 'QUESTIONNAIRE_INCOMPLETE', 'Finish the remaining questions before requesting results.')
    policy = policy_for(state.scheme_id, as_of)
    language = state.language
    checked = policy.get('checked_on', catalog()[0]['checked_on'])
    def section(items, *, complete=True):
        message = 'partial_documents' if items and not complete else 'information' if items else 'unavailable'
        return dict(status=('available' if complete else 'partial') if items else 'unavailable',
            message=shown({k:MESSAGES[k][message] for k in ('en','hi')},language), items=items)
    def common(row):
        return dict(item_id=row['item_key'],item_key=row['item_key'],source_ids=row['source_ids'],last_verified_date=checked)
    app = policy['application']
    return dict(scheme_id=state.scheme_id,language=language,screening_scope='preliminary_only',
        scheme_name=shown(policy['name'],language), eligibility_status=q['evaluation']['status'],
        explanation=shown({k:MESSAGES[k][q['evaluation']['status']] for k in ('en','hi')},language),
        assessment_notice=shown({k:MESSAGES[k]['notice'] for k in ('en','hi')},language),
        conditions_satisfied=[c for c in q['evaluation']['evaluated_conditions'] if c['result']=='SATISFIED'],
        conditions_not_satisfied=[c for c in q['evaluation']['evaluated_conditions'] if c['result']=='FAILED'],
        missing_information=q['missing_information'],missing_information_labels=q['missing_information_labels'],
        manual_notes=[localized(t,language) for t in policy['manual_notes']],
        benefits=section([dict(**common(b),description=shown(b['text'],language,b['source_ids'])) for b in policy['benefits']]),
        required_documents=section([dict(**common(d),title=shown(d['text'],language,d['source_ids']),requirement=d['requirement'],
            condition=shown(d['text'],language,d['source_ids']) if d['requirement']=='conditional' else dict(text=None)) for d in policy['documents']],
            complete=policy.get('documents_complete',True)),
        application_guidance=section([dict(item_id='enrolment',mode=app['mode'],steps=[shown(t,language,app['source_ids']) for t in app['steps']],source_ids=app['source_ids'])]),
        official_application_urls=section([dict(route_id='enrolment',url=app['url'],link_kind=app['link_kind'],source_ids=app['source_ids'])]
                                         if app['url'] else []),
        sources=distinct_sources(sources_for(policy)),last_verification_date=checked,evaluation=q['evaluation'])
