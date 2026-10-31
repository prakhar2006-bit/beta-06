"""Local public-path compatibility; synthetic catalogue rows, no live database IO."""
from copy import deepcopy
from datetime import date
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app
from app.core.errors import APIError
from app.db.repository import get_repository
from app.eligibility.provider import get_rule_provider
from app.schemas.schemes import SchemeList
from test_demo import ROWS
from test_preliminary import ANSWERS, IDS


class LocalDemoBridgeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        records = []
        for number in range(1, 16):
            rows = deepcopy(ROWS)
            rows['schemes'][0]['stable_id'] = f'in-cen-{number:06}'
            records.append(rows)
        for context in [
            patch.dict(os.environ, SCHEME_DEMO_ENABLED='1', SCHEME_APP_ENV='development'),
            patch('app.api.routes.demo.today', return_value=date(2026, 10, 31)),
            patch('app.api.routes.demo.demo_records', return_value=tuple(records)),
            patch('psycopg.connect', side_effect=AssertionError('No database IO allowed')),
        ]:
            context.start()
            self.addCleanup(context.stop)
        self.repo = Mock()
        self.repo.list_schemes.return_value = SchemeList(items=[], total=0, limit=20, offset=0, has_more=False)
        self.repo.get_scheme.return_value = None
        self.provider = Mock()
        self.provider.get_rule_set.return_value = None
        app.dependency_overrides[get_repository] = lambda: self.repo
        app.dependency_overrides[get_rule_provider] = lambda: self.provider
        self.addCleanup(app.dependency_overrides.clear)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://127.0.0.1')
        self.addAsyncCleanup(self.client.aclose)

    async def post(self, path, body, status=200):
        response = await self.client.post('/api/v1/' + path, json=body)
        self.assertEqual(response.status_code, status, response.text)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        return response.json()

    async def journey(self, scheme_id, language='en', overrides=None):
        q = await self.post('questionnaire/start', dict(scheme_id=scheme_id, language=language))
        same = await self.post('questionnaire/next', dict(state=q['state']))
        self.assertEqual(q, same)
        answers = ANSWERS | ({'age': 5} if scheme_id == IDS[-1] else {}) | (overrides or {})
        asked = []
        while not q['completed']:
            current = q['current_question']
            key = current['question_id']
            self.assertNotIn(key, asked)
            self.assertEqual(current['content_language'], language)
            asked.append(key)
            self.assertLess(len(asked), 12)
            q = await self.post('questionnaire/answer', dict(state=q['state'], question_id=key, value=answers[key]))
        result = await self.post('results/explain', dict(state=q['state']))
        self.assertEqual(result, await self.post('results/explain', dict(state=q['state'])))
        self.assertEqual(result['screening_scope'], 'preliminary_only')
        self.assertFalse(result['evaluation']['policy_review']['execution_enabled'])
        self.assertEqual(result['assessment_notice']['content_language'], language)
        self.assertTrue(result['assessment_notice']['text'])
        return q, result, asked

    async def test_all_fifteen_are_discoverable_with_honest_metadata_in_both_languages(self):
        for language in ('en', 'hi'):
            response = await self.client.get('/api/v1/schemes', params={'lang': language})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['x-scheme-catalog'], 'DEMO-UNVERIFIED')
            self.assertEqual(response.headers['cache-control'], 'no-store')
            data = response.json()
            self.assertEqual(data['total'], 15)
            self.assertEqual({s['id'] for s in data['items']}, {f'in-cen-{i:06}' for i in range(1, 16)})
            self.assertEqual(data, (await self.client.get('/api/v1/demo/schemes', params={'lang': language})).json())
            self.assertEqual(data['catalog_mode'], 'DEMO_UNVERIFIED')
            self.assertFalse(data['eligibility_execution_enabled'])
            self.assertTrue(data['preliminary_screening_enabled'])
            self.assertEqual({s['id'] for s in data['items'] if s['preliminary_screening_enabled']},
                             {f'in-cen-{i:06}' for i in range(1, 16)})
            for scheme in data['items']:
                self.assertEqual(scheme['publication_status'], 'draft')
                self.assertEqual(scheme['verification_status'], 'UNVERIFIED')
                self.assertEqual(scheme['translation_review_status'], 'draft')
                self.assertIsNone(scheme['published_at'])
                self.assertFalse(scheme['eligibility_execution_enabled'])
                self.assertEqual(scheme['language'], language)
        self.repo.list_schemes.assert_not_called()
        self.provider.get_rule_set.assert_not_called()

    async def test_all_detail_paths_resolve_without_claiming_publication(self):
        for number in range(1, 16):
            for language in ('en', 'hi'):
                response = await self.client.get(f'/api/v1/schemes/in-cen-{number:06}?lang={language}')
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data['is_demo'])
                self.assertEqual(data['publication_status'], 'draft')
                self.assertIsNone(data['published_at'])
                self.assertTrue(data['sources'])
                self.assertNotIn('.phase3-output', response.text)
        self.assertEqual((await self.client.get('/api/v1/schemes/missing')).status_code, 404)
        self.repo.get_scheme.assert_not_called()

    async def test_existing_pagination_filters_and_input_validation_work(self):
        response = await self.client.get('/api/v1/schemes?limit=2&offset=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 2)
        self.assertTrue(response.json()['has_more'])
        self.assertEqual(response.json()['total'], 15)
        self.assertEqual((await self.client.get('/api/v1/schemes?level=state')).json()['total'], 0)
        self.assertEqual((await self.client.get('/api/v1/schemes?search=in-cen-000015')).json()['total'], 1)
        for query in ('lang=xx', 'limit=0', 'offset=-1'):
            self.assertEqual((await self.client.get('/api/v1/schemes?' + query)).status_code, 422)

    async def test_full_five_bilingual_journeys_return_cited_checklists_and_guidance(self):
        for scheme_id in IDS:
            for language in ('en', 'hi'):
                with self.subTest(scheme_id=scheme_id, language=language):
                    _, result, _ = await self.journey(scheme_id, language)
                    self.assertEqual(result['eligibility_status'], 'ELIGIBLE_LIKELY')
                    self.assertTrue(result['required_documents']['items'])
                    self.assertTrue(result['application_guidance']['items'][0]['steps'])
                    self.assertTrue(result['official_application_urls']['items'])
                    refs = {s['reference_id'] for s in result['sources']}
                    for section in ('benefits', 'required_documents', 'application_guidance'):
                        for item in result[section]['items']:
                            self.assertTrue(set(item['source_ids']) <= refs)
        self.provider.get_rule_set.assert_not_called()

    async def test_decisive_failure_stops_early_for_all_five(self):
        for scheme_id in IDS:
            _, result, asked = await self.journey(scheme_id, overrides={'age': 10 if scheme_id == IDS[-1] else 16})
            self.assertEqual(result['eligibility_status'], 'NOT_ELIGIBLE_LIKELY')
            self.assertEqual(asked, ['age'])

    async def test_unknowns_skips_and_changed_answers_cannot_prematurely_approve(self):
        _, result, _ = await self.journey(IDS[2], overrides={'monthly_income': None})
        self.assertEqual(result['eligibility_status'], 'NEEDS_VERIFICATION')
        _, result, _ = await self.journey(IDS[0], overrides={'age': 50})
        self.assertEqual(result['eligibility_status'], 'NEEDS_VERIFICATION')
        q = await self.post('questionnaire/start', dict(scheme_id=IDS[0]))
        q = await self.post('questionnaire/answer', dict(state=q['state'], question_id='age', action='skip'))
        self.assertNotEqual(q['current_question']['question_id'], 'age')
        while not q['completed']:
            key = q['current_question']['question_id']
            q = await self.post('questionnaire/answer', dict(state=q['state'], question_id=key, value=ANSWERS[key]))
        self.assertEqual(q['evaluation']['status'], 'NEEDS_VERIFICATION')
        q = await self.post('questionnaire/answer', dict(state=q['state'], question_id='age', value=30))
        self.assertEqual(q['evaluation']['status'], 'ELIGIBLE_LIKELY')

    async def test_stale_tampered_and_premature_results_fail_safely(self):
        q = await self.post('questionnaire/start', dict(scheme_id=IDS[0]))
        await self.post('results/explain', dict(state=q['state']), 409)
        data = await self.post('questionnaire/answer', dict(state=q['state'], question_id='age', value='private-sentinel'), 422)
        self.assertNotIn('private-sentinel', str(data))
        await self.post('results/explain', dict(state=q['state'], eligibility_status='ELIGIBLE'), 422)
        q['state']['policy_fingerprint'] = '0' * 64
        await self.post('questionnaire/next', dict(state=q['state']), 409)

    async def test_additional_schemes_require_verification_and_approved_execution_stays_disabled(self):
        for number in range(1, 16):
            scheme_id = f'in-cen-{number:06}'
            if scheme_id not in IDS:
                data = await self.post('questionnaire/start', dict(scheme_id=scheme_id))
                self.assertEqual(data['evaluation']['status'], 'NEEDS_VERIFICATION')
                self.assertIn('INCOMPLETE_PRELIMINARY_CRITERIA', data['missing_information']['review_blockers'])
        data = await self.post('eligibility/evaluate', dict(scheme_id=IDS[0], answers={}))
        self.assertEqual(data['status'], 'NEEDS_VERIFICATION')
        self.assertFalse(data['policy_review']['execution_enabled'])

    async def test_missing_data_and_expired_guides_fail_closed_without_database_fallback(self):
        with patch('app.api.routes.demo.demo_records', side_effect=APIError(503, 'DEMO_DATA_UNAVAILABLE', 'Unavailable.')):
            self.assertEqual((await self.client.get('/api/v1/schemes')).status_code, 503)
        with patch('app.api.routes.demo.today', return_value=date(2027, 3, 1)):
            await self.post('questionnaire/start', dict(scheme_id=IDS[0]), 503)
            response = await self.client.get('/api/v1/schemes')
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json()['error']['code'], 'PRELIMINARY_REVIEW_REQUIRED')
        self.repo.list_schemes.assert_not_called()

    async def test_disabled_or_production_mode_uses_only_existing_reviewed_paths(self):
        for values in ({'SCHEME_DEMO_ENABLED': '0'}, {'SCHEME_APP_ENV': 'production'}):
            with patch.dict(os.environ, values):
                listing = await self.client.get('/api/v1/schemes')
                self.assertEqual(listing.json(), dict(items=[], total=0, limit=20, offset=0, has_more=False))
                self.assertNotIn('x-scheme-catalog', listing.headers)
                self.assertEqual((await self.client.get('/api/v1/schemes/' + IDS[0])).status_code, 404)
                q = await self.post('questionnaire/start', dict(scheme_id=IDS[0]))
                self.assertEqual(q['evaluation']['status'], 'NEEDS_VERIFICATION')
                self.assertTrue(q['completed'])
        self.repo.list_schemes.assert_called()
        self.provider.get_rule_set.assert_called()

    async def test_remote_host_and_forwarded_headers_cannot_expose_drafts_or_preliminary_rules(self):
        for peer, host in [('203.0.113.1', 'localhost'), ('127.0.0.1', 'example.invalid')]:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app, client=(peer, 1234)),
                                        base_url='http://' + host) as client:
                response = await client.get('/api/v1/schemes', headers={'X-Forwarded-For': '127.0.0.1', 'X-Forwarded-Host': 'localhost'})
                self.assertEqual(response.json()['total'], 0)
                self.assertNotIn('x-scheme-catalog', response.headers)
                q = await client.post('/api/v1/questionnaire/start', json=dict(scheme_id=IDS[0]))
                self.assertEqual(q.json()['evaluation']['status'], 'NEEDS_VERIFICATION')
                self.assertNotIn('scope', q.json()['evaluation'])


if __name__ == '__main__':
    unittest.main()
