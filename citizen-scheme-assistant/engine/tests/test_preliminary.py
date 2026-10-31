"""Source-backed advisory checks; synthetic citizen answers, no DB access."""
from datetime import date
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import httpx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import app
from app.eligibility import preliminary
from app.eligibility.provider import get_rule_provider
from app.schemas.questionnaire import StartRequest, QuestionnaireState
from app.core.errors import APIError

ANSWERS = dict(age=30,existing_account=False,savings_account=True,contributions=True,
    indian_citizen=True,unorganised_worker=True,monthly_income='10000',statutory_cover=False,
    income_taxpayer=False,other_pension=False,ever_income_taxpayer=False,girl_child=True,
    guardian=True,resident_indian=True,family_limit=False)
IDS = ['in-cen-000001','in-cen-000002','in-cen-000003','in-cen-000007','in-cen-000008']


class PreliminaryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        for context in [patch.dict(os.environ,SCHEME_DEMO_ENABLED='1',SCHEME_APP_ENV='development'),
                        patch('app.api.routes.demo.today',return_value=date(2026,10,31)),
                        patch('psycopg.connect',side_effect=AssertionError('No database allowed'))]:
            context.start();self.addCleanup(context.stop)
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://127.0.0.1')
        self.addAsyncCleanup(self.client.aclose)

    async def post(self,path,body,code=200):
        response=await self.client.post('/api/v1/demo/'+path,json=body)
        self.assertEqual(response.status_code,code,response.text)
        self.assertIn('no-store',response.headers['cache-control'])
        return response.json()

    async def journey(self,scheme_id,language='en',overrides=None):
        q=await self.post('questionnaire/start',dict(scheme_id=scheme_id,language=language))
        answers=ANSWERS | ({'age':5} if scheme_id.endswith('000008') else {}) | (overrides or {})
        asked=[]
        while not q['completed']:
            question=q['current_question'];key=question['question_id']
            self.assertEqual(question['content_language'],language)
            self.assertNotIn(key,asked);asked.append(key)
            self.assertLess(len(asked),12)
            q=await self.post('questionnaire/answer',dict(state=q['state'],question_id=key,action='answer',value=answers[key]))
        return q,asked

    async def test_all_five_complete_in_english_and_hindi_with_checklist_and_guidance(self):
        for scheme_id in IDS:
            for language in ('en','hi'):
                with self.subTest(scheme_id=scheme_id,language=language):
                    q,asked=await self.journey(scheme_id,language)
                    self.assertEqual(q['evaluation']['status'],'ELIGIBLE_LIKELY')
                    self.assertEqual(len(asked),len(preliminary.policy_for(scheme_id)['fields']))
                    result=await self.post('results/explain',dict(state=q['state']))
                    self.assertEqual(result['eligibility_status'],'ELIGIBLE_LIKELY')
                    self.assertTrue(result['required_documents']['items'])
                    self.assertTrue(result['application_guidance']['items'][0]['steps'])
                    self.assertTrue(result['official_application_urls']['items'])
                    self.assertEqual(result['scheme_name']['content_language'],language)
                    refs={s['reference_id'] for s in result['sources']}
                    for kind in ('benefits','required_documents','application_guidance'):
                        for item in result[kind]['items']:self.assertTrue(set(item['source_ids'])<=refs)
                    self.assertFalse(result['evaluation']['policy_review']['execution_enabled'])

    async def test_age_failure_stops_after_one_question_for_all_five(self):
        for scheme_id in IDS:
            q,asked=await self.journey(scheme_id,overrides={'age':10 if scheme_id.endswith('000008') else 16})
            self.assertEqual(q['evaluation']['status'],'NOT_ELIGIBLE_LIKELY')
            self.assertEqual(asked,['age'])

    async def test_missing_income_unknown_and_skip_never_produce_likely_eligible(self):
        q,_=await self.journey(IDS[2],overrides={'monthly_income':None})
        self.assertEqual(q['evaluation']['status'],'NEEDS_VERIFICATION')
        self.assertIn('monthly_income',q['missing_information']['unknown_fields'])
        q=await self.post('questionnaire/start',dict(scheme_id=IDS[0]))
        q=await self.post('questionnaire/answer',dict(state=q['state'],question_id='age',action='skip'))
        self.assertNotEqual(q['current_question']['question_id'],'age')
        while not q['completed']:
            key=q['current_question']['question_id']
            q=await self.post('questionnaire/answer',dict(state=q['state'],question_id=key,value=ANSWERS[key]))
        self.assertEqual(q['evaluation']['status'],'NEEDS_VERIFICATION')

    async def test_exact_boundaries_and_exceptions_require_verification(self):
        for scheme_id,overrides in [(IDS[0],{'age':50}),(IDS[1],{'age':69}),(IDS[1],{'age':70}),
            (IDS[2],{'age':40}),(IDS[2],{'monthly_income':15000}),(IDS[3],{'age':40}),
            (IDS[4],{'family_limit':True}),(IDS[0],{'existing_account':True})]:
            q,_=await self.journey(scheme_id,overrides=overrides)
            self.assertEqual(q['evaluation']['status'],'NEEDS_VERIFICATION')
            self.assertTrue(q['missing_information_labels'])

    async def test_tax_exclusion_and_income_above_limit(self):
        for scheme_id,overrides in [(IDS[3],{'ever_income_taxpayer':True}),
            (IDS[2],{'monthly_income':15001}),(IDS[2],{'statutory_cover':True})]:
            q,_=await self.journey(scheme_id,overrides=overrides)
            self.assertEqual(q['evaluation']['status'],'NOT_ELIGIBLE_LIKELY')

    async def test_change_previous_answer_reopens_and_stale_state_fails(self):
        q,_=await self.journey(IDS[0],overrides={'age':16})
        q=await self.post('questionnaire/answer',dict(state=q['state'],question_id='age',value=30))
        self.assertFalse(q['completed'])
        q['state']['policy_fingerprint']='0'*64
        await self.post('questionnaire/next',dict(state=q['state']),409)

    async def test_injection_bad_type_and_premature_results_are_rejected_without_echo(self):
        q=await self.post('questionnaire/start',dict(scheme_id=IDS[0]))
        await self.post('results/explain',dict(state=q['state']),409)
        body=dict(state=q['state'],question_id='age',value='private-invalid-input')
        result=await self.post('questionnaire/answer',body,422)
        self.assertNotIn('private-invalid-input',str(result))
        await self.post('results/explain',dict(state=q['state'],eligibility_status='ELIGIBLE'),422)
        q['state']['answers']={'injected_rule':True}
        await self.post('questionnaire/next',dict(state=q['state']),422)

    async def test_informational_scheme_and_original_execution_provider_remain_unavailable(self):
        await self.post('questionnaire/start',dict(scheme_id='in-cen-999999'),404)
        for scheme_id in IDS:self.assertIsNone(get_rule_provider().get_rule_set(scheme_id))
        response=await self.client.post('/api/v1/eligibility/evaluate',json=dict(scheme_id=IDS[0],answers={}))
        self.assertEqual(response.json()['status'],'NEEDS_VERIFICATION')

    async def test_development_and_loopback_guards_cover_advice_endpoints(self):
        with patch.dict(os.environ,SCHEME_DEMO_ENABLED='0'):
            await self.post('questionnaire/start',dict(scheme_id=IDS[0]),404)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,client=('203.0.113.1',123)),base_url='http://localhost') as client:
            self.assertEqual((await client.post('/api/v1/demo/questionnaire/start',json=dict(scheme_id=IDS[0]))).status_code,404)

    async def test_source_canonicalisation_preserves_aliases(self):
        refs=preliminary.distinct_sources([
            dict(reference_id='one',original_url='https://example.gov.in/page?a=1&utm_source=x#top'),
            dict(reference_id='two',original_url='https://example.gov.in/page?a=1')])
        self.assertEqual(len(refs),1)
        self.assertEqual(refs[0]['reference_ids'],['one','two'])

    async def test_expired_source_review_fails_closed(self):
        with self.assertRaises(APIError):
            preliminary.start(StartRequest(scheme_id=IDS[0]),as_of=date(2027,3,1))
