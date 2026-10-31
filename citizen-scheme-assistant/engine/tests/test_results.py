"""Synthetic reviewed published guidance; no live data or execution approvals."""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

import httpx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import app
from app.db.guidance import PublishedGuidance, PublishedGuidanceRepository, guidance_digest
from app.eligibility.approvals import ExecutionApproval
from app.eligibility.provider import get_rule_provider
from app.eligibility.questionnaire import fingerprint
from test_policy_provider import published, provider, uid
from test_eligibility import ANSWERS


def guidance_data():
    snapshot,approval=published()
    evidence=str(snapshot.sources[0].id)
    translation=dict(id=uid('translation-en'),language_code='en',title='Synthetic scheme',summary='Synthetic scheme only',
        translation_origin='human',review_status='reviewed',evidence_id=evidence)
    return dict(scheme_id='synthetic-only',version_id=str(snapshot.version_id),version_number=1,last_checked_date='2026-01-02',
        translations=[translation,translation|dict(id=uid('translation-hi'),language_code='hi',title='परीक्षण योजना')],
        benefits=[dict(id=uid('benefit'),item_key='support',benefit_type='synthetic',description='Synthetic conditional support',amount_min=100,
            amount_max=100,currency='INR',frequency='monthly',evidence_id=evidence)],
        documents=[dict(id=uid('document'),item_key='proof',document_type='Synthetic proof',requirement='conditional',condition_text='Only if the synthetic condition applies.',evidence_id=evidence)],
        application_routes=[dict(id=uid('route'),item_key='application',mode='both',original_url='https://apply.example.invalid/start',
            instructions='Submit the reviewed synthetic form to the fictional test provider.',last_checked_date='2026-01-01',evidence_id=evidence)],
        sources=[e.model_dump(mode='json') for e in snapshot.sources])


def setup_provider(data=None,review=True):
    data=guidance_data() if data is None else data
    snapshot=PublishedGuidance.model_validate(data)
    policy,approval=published()
    meta=dict(snapshot_sha256=guidance_digest(snapshot),reviewer_reference='synthetic-guidance-review',reviewed_on='2026-01-04',valid_until='2027-01-01',
        benefits=[dict(item_id=str(r.id),language='en') for r in snapshot.benefits],
        documents=[dict(item_id=str(r.id),language='en') for r in snapshot.documents],
        application_routes=[dict(item_id=str(r.id),language='en',application_url_verified=True) for r in snapshot.application_routes],
        allowed_application_hosts=['apply.example.invalid'])
    approval=ExecutionApproval.model_validate(approval.model_dump(mode='json')|{'guidance':meta if review else None})
    p,repo=provider(policy,approval)
    return p,snapshot


class ResultTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://test')
        self.addAsyncCleanup(self.client.aclose);self.addCleanup(app.dependency_overrides.clear)
        self.query=patch('app.eligibility.provider.PublishedGuidanceRepository').start()
        self.addCleanup(patch.stopall)
        self.set_guidance()

    def set_guidance(self,data=None,review=True):
        self.policy,self.snapshot=setup_provider(data,review)
        self.query.return_value.get_for_version.return_value=self.snapshot
        app.dependency_overrides[get_rule_provider]=lambda:self.policy

    def state(self,language='en',answers=None):
        return dict(scheme_id='synthetic-only',answers=deepcopy(ANSWERS if answers is None else answers),language=language,
                    policy_fingerprint=fingerprint(self.policy.get_rule_set('synthetic-only')),skipped=[])

    async def explain(self,state=None):
        response=await self.client.post('/api/v1/results/explain',json={'state':state or self.state()})
        self.assertEqual(response.status_code,200,response.text)
        return response.json()

    async def test_english_eligible_result_and_exact_provenance(self):
        result=await self.explain()
        self.assertEqual(result['eligibility_status'],'ELIGIBLE')
        self.assertEqual(result['scheme_name']['text'],'Synthetic scheme')
        self.assertEqual(result['benefits']['status'],'available')
        self.assertEqual(result['required_documents']['items'][0]['requirement'],'conditional')
        self.assertEqual(result['official_application_urls']['items'][0]['url'],'https://apply.example.invalid/start')
        self.assertIn('does not guarantee',result['assessment_notice']['text'])
        evidence=uid('evidence')
        self.assertEqual(result['benefits']['items'][0]['source_ids'],[evidence])
        self.assertEqual(result['sources'][0]['original_url'],'https://example.invalid/synthetic-policy')
        self.assertEqual(result['last_verification_date'],'2026-01-01')
        self.assertNotIn('answers',result)
        self.assertNotIn('999.99',str(result))
        self.query.return_value.get_for_version.assert_called_once_with('synthetic-only',self.snapshot.version_id)

    async def test_hindi_name_system_messages_and_explicit_english_child_fallback(self):
        result=await self.explain(self.state('hi'))
        self.assertEqual(result['scheme_name']['text'],'परीक्षण योजना')
        self.assertEqual(result['scheme_name']['content_language'],'hi')
        self.assertFalse(result['scheme_name']['is_official_translation'])
        child=result['benefits']['items'][0]['description']
        self.assertEqual(child['content_language'],'en');self.assertTrue(child['translation_fallback'])
        self.assertEqual(result['assessment_notice']['content_language'],'hi')
        self.assertIn('गारंटी',result['assessment_notice']['text'])

    async def test_hindi_name_missing_falls_back_to_reviewed_english(self):
        data=guidance_data();data['translations']=data['translations'][:1];self.set_guidance(data)
        result=await self.explain(self.state('hi'))
        self.assertEqual(result['scheme_name']['content_language'],'en')
        self.assertTrue(result['scheme_name']['translation_fallback'])

    async def test_hindi_child_is_used_only_when_the_review_attests_hindi(self):
        data=guidance_data();data['benefits'][0]['description']='परीक्षण सहायता';self.set_guidance(data)
        approval=self.policy.approvals['synthetic-only'].model_dump(mode='json')
        approval['guidance']['benefits'][0]['language']='hi'
        self.policy.approvals['synthetic-only']=ExecutionApproval.model_validate(approval)
        result=await self.explain(self.state('hi'))
        self.assertEqual(result['benefits']['items'][0]['description']['content_language'],'hi')
        self.assertFalse(result['benefits']['items'][0]['description']['translation_fallback'])
        self.assertEqual((await self.explain(self.state('en')))['benefits']['status'],'unavailable')

    async def test_ineligible_and_needs_verification_recomputed(self):
        result=await self.explain(self.state(answers=ANSWERS|{'age':17}))
        self.assertEqual(result['eligibility_status'],'INELIGIBLE')
        self.assertTrue(result['conditions_not_satisfied'])
        result=await self.explain(self.state(answers=ANSWERS|{'age':None}))
        self.assertEqual(result['eligibility_status'],'NEEDS_VERIFICATION')
        self.assertIn('age',result['missing_information']['unknown_fields'])

    async def test_missing_documents_explicitly_unavailable_not_no_documents_needed(self):
        data=guidance_data();data['documents']=[];self.set_guidance(data)
        result=await self.explain()
        self.assertEqual(result['required_documents']['status'],'unavailable')
        self.assertEqual(result['required_documents']['items'],[])
        self.assertIn('unavailable',result['required_documents']['message']['text'])

    async def test_missing_or_unverified_application_url_is_not_fabricated(self):
        data=guidance_data();data['application_routes'][0].update(mode='offline',original_url=None);self.set_guidance(data)
        result=await self.explain(self.state('hi'))
        route=result['application_guidance']['items'][0]
        self.assertIsNone(route['official_application_url'])
        self.assertEqual(route['url_status'],'unavailable')
        self.assertEqual(result['official_application_urls']['status'],'unavailable')
        self.assertEqual(result['official_application_urls']['items'],[])
        self.set_guidance()
        approval=self.policy.approvals['synthetic-only'].model_dump(mode='json')
        approval['guidance']['application_routes'][0]['application_url_verified']=False
        self.policy.approvals['synthetic-only']=ExecutionApproval.model_validate(approval)
        self.assertEqual((await self.explain())['official_application_urls']['items'],[])

    async def test_unreviewed_or_changed_guidance_is_unavailable(self):
        self.set_guidance(review=False)
        result=await self.explain()
        self.assertEqual(result['benefits']['status'],'unavailable')
        self.assertEqual(result['scheme_name']['text'],'Synthetic scheme')
        self.set_guidance()
        data=self.snapshot.model_dump(mode='json');data['benefits'][0]['description']='Unreviewed changed wording'
        self.query.return_value.get_for_version.return_value=PublishedGuidance.model_validate(data)
        result=await self.explain()
        self.assertEqual(result['benefits']['status'],'unavailable')
        self.assertNotIn('Unreviewed changed wording',str(result))

    async def test_missing_guidance_evidence_is_not_borrowed_from_policy(self):
        data=guidance_data();data['sources']=[];self.set_guidance(data)
        result=await self.explain()
        self.assertEqual(result['scheme_name']['review_status'],'unavailable')
        self.assertEqual(result['benefits']['status'],'unavailable')

    async def test_unapproved_and_unpublished_scheme_do_not_load_guidance(self):
        self.policy.approvals={}
        result=await self.explain(dict(scheme_id='synthetic-only',answers={},language='en',policy_fingerprint=None))
        self.assertEqual(result['eligibility_status'],'NEEDS_VERIFICATION')
        self.assertIsNone(result['scheme_name']['text'])
        self.query.return_value.get_for_version.assert_not_called()
        self.set_guidance()
        self.policy.repository.get_latest.return_value=None
        result=await self.explain(dict(scheme_id='synthetic-only',answers={},language='en',policy_fingerprint=None))
        self.assertEqual(result['eligibility_status'],'NEEDS_VERIFICATION')
        self.query.return_value.get_for_version.assert_not_called()
        # Actual default provider: all five real draft schemes remain blocked.
        app.dependency_overrides.clear()
        for i in range(1,6):
            result=await self.explain(dict(scheme_id=f'in-cen-00000{i}',answers={},language='hi',policy_fingerprint=None))
            self.assertEqual(result['eligibility_status'],'NEEDS_VERIFICATION')
            self.assertEqual(result['application_guidance']['status'],'unavailable')

    async def test_invalid_language_tampered_result_and_stale_policy(self):
        state=self.state()
        payloads=[{'state':state|{'language':'xx'}},{'state':state,'status':'ELIGIBLE'},
                  {'state':state|{'rules':[]}},{'state':state,'evaluation':{'status':'ELIGIBLE'}}]
        for payload in payloads:
            response=await self.client.post('/api/v1/results/explain',json=payload)
            self.assertEqual(response.status_code,422)
            self.assertEqual(response.headers['cache-control'],'no-store')
        self.policy.approvals={}
        response=await self.client.post('/api/v1/results/explain',json={'state':state})
        self.assertEqual(response.status_code,409)
        self.assertEqual(response.json()['error']['code'],'POLICY_CHANGED')

    async def test_application_host_review_expiry_and_version_mismatch_fail_safely(self):
        data=guidance_data();data['application_routes'][0]['original_url']='https://unapproved.invalid/apply';self.set_guidance(data)
        self.assertEqual((await self.explain())['official_application_urls']['items'],[])
        self.set_guidance()
        approval=self.policy.approvals['synthetic-only'].model_dump(mode='json')
        approval['guidance']['valid_until']='2026-02-01'
        self.policy.approvals['synthetic-only']=ExecutionApproval.model_validate(approval)
        self.assertEqual((await self.explain())['required_documents']['status'],'unavailable')
        self.set_guidance()
        self.query.return_value.get_for_version.return_value=self.snapshot.model_copy(update={'version_number':2})
        response=await self.client.post('/api/v1/results/explain',json={'state':self.state()})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json()['error']['code'],'GUIDANCE_INVALID')

    async def test_no_answer_logging_storage_or_network_and_docs(self):
        with patch('psycopg.connect',side_effect=AssertionError('No DB')),patch('socket.create_connection',side_effect=AssertionError('No network')),patch('logging.Logger._log') as log:
            response=await self.client.post('/api/v1/results/explain',json={'state':self.state()})
            self.assertEqual(response.status_code,200,response.text)
            self.assertEqual(response.headers['cache-control'],'no-store')
            for call in log.call_args_list:self.assertNotIn('999.99',str(call))
        self.assertIn('/api/v1/results/explain',(await self.client.get('/openapi.json')).json()['paths'])


class GuidanceRepositoryTests(unittest.TestCase):
    def test_exact_version_reviewed_published_only_parameterized_reads(self):
        snapshot=PublishedGuidance.model_validate(guidance_data());raw=snapshot.model_dump(mode='python')
        conn=MagicMock();cursor=conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value={k:v for k,v in raw.items() if k not in ('translations','benefits','documents','application_routes','sources')}
        cursor.fetchall.side_effect=[raw[k] for k in ('translations','benefits','documents','application_routes','sources')]
        @contextmanager
        def connection():yield conn
        with patch('app.db.guidance.open_connection',connection):
            result=PublishedGuidanceRepository().get_for_version("' OR 1=1 --",snapshot.version_id)
        self.assertEqual(result,snapshot)
        conn.cursor.assert_called_once();self.assertEqual(cursor.execute.call_count,6)
        for call in cursor.execute.call_args_list:
            sql,params=call.args
            self.assertIn('scheme_catalog.published_',sql)
            self.assertNotIn("' OR 1=1",sql)
            self.assertEqual(params['version_id'],snapshot.version_id)
        self.assertIn("review_status='reviewed'",cursor.execute.call_args_list[1].args[0])


if __name__=='__main__':unittest.main()
