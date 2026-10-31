"""Controlled isolated PMJJBY-shaped platform tests, never government approval."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import httpx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pmjjby_workflow_fixture import create_app,ID


class PMJJBYWorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.no_network=patch('psycopg.connect',side_effect=AssertionError('No remote database allowed'));self.no_network.start()
        self.addCleanup(self.no_network.stop)
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app()),base_url='http://test')
        self.addAsyncCleanup(self.client.aclose)

    async def start(self,language='en',scheme_id=ID):
        response=await self.client.post('/api/v1/questionnaire/start',json=dict(scheme_id=scheme_id,language=language))
        self.assertEqual(response.status_code,200,response.text);return response.json()

    async def answer(self,state,value):
        response=await self.client.post('/api/v1/questionnaire/answer',json=dict(state=state['state'],
            question_id=state['current_question']['question_id'],action='answer',value=value))
        self.assertEqual(response.status_code,200,response.text);return response.json()

    async def test_english_and_hindi_complete_fixture_journeys(self):
        for language in ('en','hi'):
            result=await self.start(language);asked=[]
            while not result['completed']:
                self.assertEqual(result['current_question']['content_language'],language)
                asked.append(result['current_question']['question_id']);result=await self.answer(result,True)
            self.assertEqual(len(asked),3);self.assertEqual(len(set(asked)),3)
            self.assertEqual(result['evaluation']['status'],'ELIGIBLE')
            response=await self.client.post('/api/v1/results/explain',json={'state':result['state']})
            self.assertEqual(response.status_code,200,response.text);data=response.json()
            self.assertEqual(data['eligibility_status'],'ELIGIBLE');self.assertTrue(data['sources'])
            self.assertTrue(data['required_documents']['items']);self.assertTrue(data['application_guidance']['items'])
            self.assertFalse(data['official_application_urls']['items'])
            self.assertIn('government',data['assessment_notice']['text'].lower()) if language=='en' else None
            if language=='hi':self.assertTrue(data['required_documents']['items'][0]['title']['translation_fallback'])

    async def test_early_ineligible_fixture_and_unknown_case(self):
        result=await self.answer(await self.start(),False)
        self.assertEqual(result['evaluation']['status'],'INELIGIBLE');self.assertTrue(result['completed'])
        result=await self.start()
        while not result['completed']:result=await self.answer(result,None)
        self.assertEqual(result['evaluation']['status'],'NEEDS_VERIFICATION')
        self.assertEqual(result['completion_reason'],'VERIFICATION_REQUIRED')

    async def test_real_unpublished_pmjjby_unavailable_and_injection_rejected(self):
        real=await self.start(scheme_id='in-cen-000001')
        self.assertEqual(real['evaluation']['status'],'NEEDS_VERIFICATION');self.assertTrue(real['completed'])
        response=await self.client.get('/api/v1/schemes/in-cen-000001');self.assertEqual(response.status_code,404)
        result=await self.start()
        response=await self.client.post('/api/v1/results/explain',json={'state':result['state'],'eligibility_status':'ELIGIBLE'})
        self.assertEqual(response.status_code,422)

    async def test_fixture_catalog_detail_and_loopback_access(self):
        listing=(await self.client.get('/api/v1/schemes')).json();self.assertEqual(listing['items'][0]['id'],ID)
        detail=(await self.client.get('/api/v1/schemes/'+ID)).json();self.assertIn('SIMULATED',detail['name'])
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(),client=('203.0.113.1',1)),base_url='http://test') as remote:
            self.assertEqual((await remote.get('/api/v1/schemes')).status_code,403)


if __name__=='__main__':unittest.main()
