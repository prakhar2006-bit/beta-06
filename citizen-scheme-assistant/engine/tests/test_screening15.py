"""All fifteen local screens, using synthetic answers and existing official evidence."""
from datetime import date
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app
from app.eligibility import preliminary
from app.schemas.questionnaire import QuestionnaireState
from screening15_fixtures import ALL_IDS, ORIGINAL_IDS, ADDITIONAL_IDS, sample_answers

TODAY = date(2026, 10, 31)


class FifteenScreeningTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        for context in [patch.dict(os.environ, SCHEME_APP_ENV='development', SCHEME_DEMO_ENABLED='1'),
                        patch('app.api.routes.demo.today', return_value=TODAY),
                        patch('psycopg.connect', side_effect=AssertionError('No database access'))]:
            context.start()
            self.addCleanup(context.stop)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://127.0.0.1')
        self.addAsyncCleanup(self.client.aclose)

    async def post(self, path, body, *, prefix='/api/v1', status=200):
        response = await self.client.post(prefix + '/' + path, json=body)
        self.assertEqual(response.status_code, status, response.text)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        return response.json()

    async def journey(self, sid, language='en', overrides=None, *, prefix='/api/v1', skip=False):
        q = await self.post('questionnaire/start', dict(scheme_id=sid, language=language), prefix=prefix)
        answers = sample_answers(sid) | (overrides or {})
        asked = []
        while not q['completed']:
            question = q['current_question']
            key = question['question_id']
            self.assertNotIn(key, asked)
            asked.append(key)
            self.assertLess(len(asked), 16)
            self.assertEqual(question['content_language'], language)
            self.assertTrue(question['text'])
            body = dict(state=q['state'], question_id=key, action='skip' if skip else 'answer')
            if not skip:
                body['value'] = answers[key]
            q = await self.post('questionnaire/answer', body, prefix=prefix)
        result = await self.post('results/explain', dict(state=q['state']), prefix=prefix)
        self.assertEqual(result, await self.post('results/explain', dict(state=q['state']), prefix=prefix))
        return q, result, asked

    async def test_all_fifteen_complete_bilingually_through_both_existing_namespaces(self):
        for prefix in ('/api/v1', '/api/v1/demo'):
            for sid in ALL_IDS:
                for language in ('en', 'hi'):
                    with self.subTest(prefix=prefix, scheme_id=sid, language=language):
                        q, result, asked = await self.journey(sid, language, prefix=prefix)
                        expected = 'ELIGIBLE_LIKELY' if sid in ORIGINAL_IDS else 'NEEDS_VERIFICATION'
                        self.assertEqual(result['eligibility_status'], expected)
                        self.assertTrue(q['completed'])
                        self.assertEqual(len(asked), len(preliminary.policy_for(sid)['fields']))
                        self.assertEqual(result['screening_scope'], 'preliminary_only')
                        self.assertFalse(result['evaluation']['policy_review']['execution_enabled'])
                        self.assertFalse(result['evaluation']['policy_review']['complete'])
                        for key in ('scheme_name', 'explanation', 'assessment_notice'):
                            self.assertEqual(result[key]['content_language'], language)
                            self.assertFalse(result[key]['is_official_translation'])
                        if sid in ADDITIONAL_IDS:
                            self.assertEqual(q['completion_reason'], 'VERIFICATION_REQUIRED')
                            self.assertIn('INCOMPLETE_PRELIMINARY_CRITERIA', result['missing_information']['review_blockers'])
                            self.assertTrue(result['missing_information_labels'])

    async def test_every_additional_screen_preserves_source_provenance_and_unavailable_guidance(self):
        for sid in ADDITIONAL_IDS:
            _, result, _ = await self.journey(sid)
            refs = {source['reference_id'] for source in result['sources']}
            self.assertTrue(refs)
            for condition in result['evaluation']['evaluated_conditions']:
                self.assertTrue(set(condition['source_ids']) <= refs)
            for key in ('benefits', 'required_documents', 'application_guidance'):
                for row in result[key]['items']:
                    self.assertTrue(set(row['source_ids']) <= refs)
            policy = preliminary.policy_for(sid)
            self.assertEqual(result['last_verification_date'], policy['checked_on'])
            self.assertEqual(result['required_documents']['status'], 'partial' if policy['documents'] else 'unavailable')
            self.assertEqual(result['official_application_urls']['status'], 'available' if policy['application']['url'] else 'unavailable')
            self.assertTrue(all(row['url'] for row in result['official_application_urls']['items']))

    async def test_verified_mandatory_failures_stop_without_unnecessary_questions(self):
        cases = [('in-cen-000004', {'age': 17}, ['age']),
                 ('in-cen-000005', {'age': 59}, ['age']),
                 ('in-cen-000009', {'has_pucca_roof_or_wall': True}, ['has_pucca_roof_or_wall']),
                 ('in-cen-000011', {'age': 17}, ['age']),
                 ('in-cen-000012', {'is_street_vendor': False}, ['is_street_vendor']),
                 ('in-cen-000014', {'indian_citizen': False}, ['indian_citizen'])]
        for sid, changes, expected in cases:
            for language in ('en', 'hi'):
                _, result, asked = await self.journey(sid, language, changes)
                self.assertEqual(result['eligibility_status'], 'NOT_ELIGIBLE_LIKELY')
                self.assertEqual(asked, expected)
                self.assertTrue(result['conditions_not_satisfied'])

    async def test_under_seventy_is_an_alternative_pmjay_route_not_ineligibility(self):
        for age in (0, 35, 69, 70, 90):
            _, result, asked = await self.journey('in-cen-000010', overrides={'age': age})
            self.assertEqual(result['eligibility_status'], 'NEEDS_VERIFICATION')
            self.assertEqual(asked, ['age'])
            self.assertFalse(result['conditions_not_satisfied'])

    async def test_missing_documents_legacy_exceptions_and_alternative_credit_routes_are_not_rejections(self):
        for sid, values in [('in-cen-000005', {'bpl_household': False}),
                            ('in-cen-000006', {'family_has_cultivable_land': False}),
                            ('in-cen-000011', {'similar_credit_last_five_years': True}),
                            ('in-cen-000012', {'has_cov_or_lor': False}),
                            ('in-cen-000015', {'cultivator_or_allied_activity': False})]:
            _, result, _ = await self.journey(sid, overrides=values)
            self.assertEqual(result['eligibility_status'], 'NEEDS_VERIFICATION')
        self.assertNotIn('land_owner', {f['key'] for f in preliminary.policy_for('in-cen-000015')['fields']})

    async def test_unknown_skipped_and_changed_answers_never_approve_incomplete_guides(self):
        for sid in ADDITIONAL_IDS:
            q, result, _ = await self.journey(sid, skip=True)
            self.assertEqual(result['eligibility_status'], 'NEEDS_VERIFICATION')
            key = q['state']['skipped'][0]
            q = await self.post('questionnaire/answer', dict(state=q['state'], question_id=key,
                                                           value=sample_answers(sid)[key]))
            self.assertNotEqual(q['evaluation']['status'], 'ELIGIBLE_LIKELY')
            field = preliminary.policy_for(sid)['fields'][0]['key']
            _, result, _ = await self.journey(sid, overrides={field: None})
            self.assertEqual(result['eligibility_status'], 'NEEDS_VERIFICATION')

    async def test_numeric_loan_question_keeps_units_types_and_boundary_uncertainty(self):
        for amount in (1, 1000000, 1000000.01, 2000000, 2000001, -1):
            _, result, _ = await self.journey('in-cen-000013', overrides={'requested_loan_amount': amount})
            self.assertEqual(result['eligibility_status'], 'NEEDS_VERIFICATION')
        q = await self.post('questionnaire/start', dict(scheme_id='in-cen-000013'))
        q = await self.post('questionnaire/answer', dict(state=q['state'], question_id='income_generating_business_plan', value=True))
        self.assertEqual(q['current_question']['unit'], 'INR')
        self.assertEqual(q['current_question']['answer_type'], 'number')
        for value in (True, 'private-invalid-value'):
            data = await self.post('questionnaire/answer', dict(state=q['state'], question_id='requested_loan_amount', value=value), status=422)
            self.assertNotIn('private-invalid-value', str(data))

    async def test_sources_are_fresh_but_not_publication_attestations(self):
        data, policies = preliminary.catalog(include_additions=True)
        self.assertEqual(set(policies), set(ALL_IDS))
        self.assertEqual(set(preliminary.catalog()[1]), set(ORIGINAL_IDS))
        for sid in ADDITIONAL_IDS:
            p = policies[sid]
            self.assertFalse(p['preliminary_complete'])
            self.assertFalse(p['human_publication_approved'])
            for field in p['fields']:
                self.assertIsNone(field['effective_from'])
            for ref in preliminary.source_ids(p):
                self.assertEqual(data['sources'][ref]['last_checked_date'], TODAY.isoformat())
                self.assertFalse(data['sources'][ref]['publication_approval'])
        with patch('app.api.routes.demo.today', return_value=date(2027, 3, 1)):
            for sid in ADDITIONAL_IDS:
                result = await self.post('questionnaire/start', dict(scheme_id=sid), status=503)
                self.assertEqual(result['error']['code'], 'PRELIMINARY_REVIEW_REQUIRED')

    async def test_original_five_data_and_fingerprints_are_unchanged(self):
        original = json.loads(preliminary.CATALOG.read_text(encoding='utf-8'))
        for policy in original['schemes']:
            self.assertEqual(policy, preliminary.policy_for(policy['scheme_id']))
            bound = dict(policy=policy, sources={k: original['sources'][k] for k in preliminary.source_ids(policy)})
            old = sha256(json.dumps(bound, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            self.assertEqual(old, preliminary.fingerprint(policy))

    async def test_extension_cannot_enable_positive_outcomes_or_inject_approval(self):
        original = preliminary.ADDITIONS.read_text(encoding='utf-8')
        for mutation in ('complete', 'missing_gate', 'duplicate', 'uncited', 'unofficial_host'):
            data = json.loads(original)
            if mutation == 'complete': data['schemes'][0]['preliminary_complete'] = True
            elif mutation == 'missing_gate': data['schemes'][0]['verification_requirements'] = []
            elif mutation == 'duplicate': data['schemes'][1]['scheme_id'] = data['schemes'][0]['scheme_id']
            elif mutation == 'uncited': data['schemes'][0]['fields'][0]['source_ids'] = []
            else: data['sources']['extra-pmuy']['original_url'] = 'https://example.invalid/unofficial'
            preliminary.catalog.cache_clear()
            try:
                with patch.object(preliminary, 'ADDITIONS', Mock(read_text=Mock(return_value=json.dumps(data)))):
                    with self.assertRaises(ValueError): preliminary.catalog(include_additions=True)
            finally:
                preliminary.catalog.cache_clear()
        q = await self.post('questionnaire/start', dict(scheme_id='in-cen-000004'))
        await self.post('results/explain', dict(state=q['state'], eligibility_status='ELIGIBLE'), status=422)
        q['state']['policy_fingerprint'] = '0' * 64
        await self.post('questionnaire/next', dict(state=q['state']), status=409)

    async def test_runtime_does_not_persist_answers(self):
        preliminary.catalog(include_additions=True)  # Warm server-owned definitions before IO guards.
        with patch.object(Path, 'write_text', side_effect=AssertionError('No answer persistence')), \
             patch.object(Path, 'write_bytes', side_effect=AssertionError('No answer persistence')):
            for sid in ALL_IDS:
                _, result, _ = await self.journey(sid)
                self.assertNotEqual(result['eligibility_status'], 'ELIGIBLE')


if __name__ == '__main__':
    unittest.main()
