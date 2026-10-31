"""Synthetic policies only. No real scheme rules, database or network calls."""
from copy import deepcopy
from datetime import date
from pathlib import Path
from itertools import product
import sys
import unittest
from unittest.mock import Mock, patch

import httpx
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app
from app.eligibility.engine import InvalidAnswers, evaluate
from app.eligibility.provider import get_rule_provider
from app.schemas.eligibility import EvaluationRequest, RuleSet

TODAY = date(2026, 10, 31)
APPROVED = dict(enabled=True, confidence='VERIFIED', applicability_confirmed=True)


def node(key, attribute=None, op=None, value=None, *, parent='root', kind='predicate'):
    return dict(rule_id=key, parent_id=parent, node_type=kind,
        label={'en': 'Synthetic condition: ' + key, 'hi': 'परीक्षण की शर्त: ' + key},
        attribute=attribute, operator=op, expected_value=value,
        source_ids=['fixture-source'] if kind == 'predicate' else [], **APPROVED)


def fixture():
    return dict(scheme_id='synthetic-only', version='fixture-1', publication_status='published',
        approval_status='approved', execution_enabled=True, complete=True,
        reviewer_reference='synthetic-test-review', reviewed_on='2026-01-02',
        applicability_confirmed=True, effective_from='2026-01-01',
        fields=[
            dict(key='age', kind='age', question={'en':'Age at application?', 'hi':'आवेदन के समय आयु?'}, reference_basis='Completed years at synthetic application date'),
            dict(key='monthly_income', kind='income', question={'en':'Monthly individual income in fixture units?'}, unit='INR', period='monthly', scope='individual'),
            dict(key='state', kind='category', question={'en':'Synthetic state code?'}, choices=['state_a','state_b']),
            dict(key='gender', kind='category', question={'en':'Synthetic gender category?'}, choices=['female','male','other']),
            dict(key='occupation', kind='category', question={'en':'Synthetic occupation?'}, choices=['worker','other']),
            dict(key='category', kind='category', question={'en':'Synthetic membership category?'}, choices=['group_a','group_b','group_c']),
            dict(key='has_existing_benefit', kind='boolean', question={'en':'Existing synthetic benefit?'})],
        nodes=[node('root', parent=None, kind='and'), node('age_min','age','gte',18),
               node('age_max','age','lte',60), node('income','monthly_income','lte','1000.00'),
               node('state','state','in',('state_a',)), node('gender','gender','eq','female'),
               node('occupation','occupation','eq','worker'), node('category','category','in',('group_a','group_b')),
               node('boolean','has_existing_benefit','eq',False)],
        sources=[dict(reference_id='fixture-source',original_url='https://example.invalid/synthetic-policy',
                      title='Synthetic test fixture; not government guidance',locator='Synthetic clauses',last_checked_date='2026-01-01')])


ANSWERS = dict(age=30,monthly_income='999.99',state='state_a',gender='female',occupation='worker',category='group_a',has_existing_benefit=False)


def run(data=None, answers=None, language='en'):
    policy = RuleSet.model_validate(fixture() if data is None else data)
    return evaluate(policy,policy.scheme_id,deepcopy(ANSWERS if answers is None else answers),language,as_of=TODAY)


class EngineTests(unittest.TestCase):
    def test_complete_reviewed_fixture_is_eligible_and_deterministic(self):
        answers = deepcopy(ANSWERS)
        result = run(answers=answers)
        self.assertEqual(result.status,'ELIGIBLE')
        self.assertEqual(result,run(answers=answers))
        self.assertEqual(answers,ANSWERS)
        self.assertNotIn('999.99',result.model_dump_json())
        self.assertEqual(result.failed_rules,())
        self.assertEqual(result.sources[0].original_url,'https://example.invalid/synthetic-policy')

    def test_age_and_income_boundaries(self):
        for age,status in [(17,'INELIGIBLE'),(18,'ELIGIBLE'),(60,'ELIGIBLE'),(61,'INELIGIBLE')]:
            with self.subTest(age=age): self.assertEqual(run(answers=ANSWERS|{'age':age}).status,status)
        for amount,status in [('999.99','ELIGIBLE'),('1000.00','ELIGIBLE'),('1000.000001','INELIGIBLE')]:
            with self.subTest(amount=amount): self.assertEqual(run(answers=ANSWERS|{'monthly_income':amount}).status,status)

    def test_missing_age_income_and_unknown_state_are_not_false(self):
        for key in ('age','monthly_income','state'):
            absent = {k:v for k,v in ANSWERS.items() if k != key}
            unknown = ANSWERS|{key:None}
            self.assertEqual(run(answers=absent),run(answers=unknown))
            result = run(answers=unknown)
            self.assertEqual(result.status,'NEEDS_VERIFICATION')
            self.assertIn(key,result.missing_answers)
            self.assertEqual([q.attribute for q in result.questions_needed],[key])

    def test_incomplete_unreviewed_unpublished_or_disabled_never_eligible(self):
        cases=[('complete',False),('approval_status','unreviewed'),('publication_status','draft'),
               ('publication_status','reviewed'),('execution_enabled',False),('applicability_confirmed',False),
               ('reviewer_reference',None),('reviewed_on',None),('effective_from',None)]
        for key,value in cases:
            data=fixture();data[key]=value
            for age in (17,30):
                with self.subTest(key=key,value=value,age=age):
                    result=run(data,ANSWERS|{'age':age})
                    self.assertNotEqual(result.status,'ELIGIBLE')
                    if key!='complete':self.assertEqual(result.status,'NEEDS_VERIFICATION')
        data=fixture();data['complete']=False
        self.assertEqual(run(data,ANSWERS|{'age':17}).status,'NEEDS_VERIFICATION')
        data['root_failure_is_decisive']=True
        self.assertEqual(run(data,ANSWERS|{'age':17}).status,'INELIGIBLE')

    def test_unverified_disabled_missing_source_and_future_source_are_unknown(self):
        for change in ('unverified','disabled','source','future_source','applicability'):
            data=fixture()
            if change=='unverified':data['nodes'][1]['confidence']='UNCERTAIN'
            elif change=='disabled':data['nodes'][1]['enabled']=False
            elif change=='source':data['nodes'][1]['source_ids']=[]
            elif change=='applicability':data['nodes'][1]['applicability_confirmed']=False
            else:data['sources'][0]['last_checked_date']='2099-01-01'
            result=run(data,ANSWERS|{'age':17})
            self.assertEqual(result.status,'NEEDS_VERIFICATION')
            self.assertIn('age_min',result.unknown_conditions)

    def test_declared_conflicts_and_impossible_mandatory_conditions_need_review(self):
        for kind in ('declared','bounds','integer_gap','category','not'):
            data=fixture()
            if kind=='declared':data['conflicts']=['Synthetic conflicting policy clauses']
            elif kind=='bounds':data['nodes'][2]['expected_value']=10
            elif kind=='integer_gap':
                data['nodes'][1].update(operator='gt',expected_value=18)
                data['nodes'][2].update(operator='lt',expected_value=19)
            elif kind=='category':data['nodes'].append(node('other_state','state','eq','state_b'))
            else:
                data['nodes'] += [node('exclusion',kind='not'),node('excluded_category','category','in',('group_a','group_b'),parent='exclusion')]
            result=run(data)
            self.assertEqual(result.status,'NEEDS_VERIFICATION')
            self.assertIn('POLICY_CONFLICT',result.policy_review.blockers)

    def test_nested_and_or_and_not_groups_and_unused_missing_answer(self):
        data=fixture()
        data['nodes']=[node('root',parent=None,kind='and'), node('age','age','gte',18),
            node('alternative',kind='or'),node('state','state','eq','state_a',parent='alternative'),
            node('occupation','occupation','eq','worker',parent='alternative'),
            node('exclusion',kind='not'),node('excluded','has_existing_benefit','eq',True,parent='exclusion')]
        self.assertEqual(run(data).status,'ELIGIBLE')
        self.assertEqual(run(data,ANSWERS|{'state':None}).status,'ELIGIBLE')
        self.assertEqual(run(data,ANSWERS|{'state':'state_b','occupation':'other'}).status,'INELIGIBLE')
        result=run(data,ANSWERS|{'state':None,'occupation':'other'})
        self.assertEqual(result.status,'NEEDS_VERIFICATION')
        self.assertEqual([q.attribute for q in result.questions_needed],['state'])
        # A completed OR branch must not generate questions when another group is unknown.
        result=run(data,ANSWERS|{'age':None,'state':None})
        self.assertEqual([q.attribute for q in result.questions_needed],['age'])

    def test_verified_exclusion_decisive_but_unverified_exclusion_never_rejects(self):
        data=fixture();data['complete']=False;data['root_failure_is_decisive']=True
        data['nodes']=[node('root',parent=None,kind='and'),node('exclusion',kind='not'),
                       node('excluded','has_existing_benefit','eq',True,parent='exclusion')]
        result=run(data,ANSWERS|{'has_existing_benefit':True})
        self.assertEqual(result.status,'INELIGIBLE')
        self.assertIn('exclusion',result.failed_rules)
        data['nodes'][2]['confidence']='UNCERTAIN'
        self.assertEqual(run(data,ANSWERS|{'has_existing_benefit':True}).status,'NEEDS_VERIFICATION')
        data['nodes'][2]['confidence']='VERIFIED';data['nodes'][1]['enabled']=False
        self.assertEqual(run(data,ANSWERS|{'has_existing_benefit':True}).status,'NEEDS_VERIFICATION')

    def test_or_with_unverified_alternative_cannot_create_eligible(self):
        data=fixture();data['nodes']=[node('root',parent=None,kind='or'),node('age','age','gte',18),node('other','state','eq','state_b')]
        data['nodes'][2]['confidence']='UNCERTAIN'
        self.assertEqual(run(data).status,'NEEDS_VERIFICATION')

    def test_all_operators_and_exact_decimal_comparison(self):
        for op,value,answer,expected in [('eq',18,18,'ELIGIBLE'),('ne',18,18,'INELIGIBLE'),('gt',18,18,'INELIGIBLE'),
            ('gte',18,18,'ELIGIBLE'),('lt',18,18,'INELIGIBLE'),('lte',18,18,'ELIGIBLE'),
            ('in',(18,19),18,'ELIGIBLE'),('not_in',(18,19),18,'INELIGIBLE')]:
            data=fixture();data['nodes']=[node('age','age',op,value,parent=None)]
            self.assertEqual(run(data,ANSWERS|{'age':answer}).status,expected)
        data=fixture();data['nodes']=[node('income','monthly_income','eq','0.30',parent=None)]
        self.assertEqual(run(data,ANSWERS|{'monthly_income':'0.30'}).status,'ELIGIBLE')
        self.assertEqual(run(data,ANSWERS|{'monthly_income':0.3}).status,'ELIGIBLE')

    def test_three_valued_truth_tables_and_no_incomplete_positive_decisions(self):
        for kind, values, complete in product(('and','or'),product((True,False,None),repeat=2),(True,False)):
            data=fixture();data['complete']=complete
            data['fields']=[dict(key=k,kind='boolean',question={'en':'Synthetic '+k}) for k in ('first','second')]
            data['nodes']=[node('root',parent=None,kind=kind),node('first','first','eq',True),node('second','second','eq',True)]
            result=run(data,dict(zip(('first','second'),values)))
            truth=('FAILED' if False in values else 'UNKNOWN' if None in values else 'SATISFIED') if kind=='and' else (
                'SATISFIED' if True in values else 'UNKNOWN' if None in values else 'FAILED')
            self.assertEqual(next(r.result for r in result.evaluated_conditions if r.rule_id=='root'),truth)
            expected='NEEDS_VERIFICATION' if not complete or truth=='UNKNOWN' else 'ELIGIBLE' if truth=='SATISFIED' else 'INELIGIBLE'
            self.assertEqual(result.status,expected)

    def test_policy_periods_review_deadline_and_rule_periods(self):
        for key,value in [('effective_from','2099-01-01'),('effective_to','2025-01-01'),('review_valid_until','2025-01-01'),('reviewed_on','2099-01-01')]:
            data=fixture();data[key]=value
            self.assertEqual(run(data).status,'NEEDS_VERIFICATION')
        data=fixture();data['nodes'][1]['effective_to']='2025-01-01'
        self.assertEqual(run(data).status,'NEEDS_VERIFICATION')
        data=fixture();data['unresolved_conditions']=['Provider confirmation still required']
        self.assertEqual(run(data).status,'NEEDS_VERIFICATION')

    def test_invalid_answer_types_never_coerce_and_do_not_echo_values(self):
        for key,value in [('age',True),('age','18'),('age',18.5),('age',-1),('monthly_income',False),
                          ('monthly_income',-1),('monthly_income','1e3'),('monthly_income',0.0000001),
                          ('monthly_income',"__import__('os').system('anything')"),('state','unknown'),('gender',False),('has_existing_benefit',0)]:
            with self.subTest(key=key,value=value), self.assertRaises(InvalidAnswers):run(answers=ANSWERS|{key:value})
        with self.assertRaises(InvalidAnswers):run(answers=ANSWERS|{'unexpected':True})

    def test_invalid_rule_trees_and_references_rejected(self):
        for kind in ('duplicate','cycle','parent','source','arity','attribute','expression'):
            data=fixture()
            if kind=='duplicate':data['nodes'].append(data['nodes'][1])
            elif kind=='cycle':data['nodes'][0]['parent_id']='age_min'
            elif kind=='parent':data['nodes'][1]['parent_id']='nonexistent'
            elif kind=='source':data['nodes'][1]['source_ids']=['invented']
            elif kind=='arity':data['nodes'][0]['node_type']='not'
            elif kind=='attribute':data['nodes'][1]['attribute']='undefined'
            else:data['nodes'][1]['operator']='python_eval'
            with self.subTest(kind=kind), self.assertRaises(ValidationError):RuleSet.model_validate(data)

    def test_malformed_expected_types_and_disabled_groups_fail_closed(self):
        data=fixture();data['nodes'][1]['expected_value']=True
        self.assertEqual(run(data).status,'NEEDS_VERIFICATION')
        data=fixture();data['nodes'][0]['confidence']='UNCERTAIN'
        self.assertEqual(run(data).status,'NEEDS_VERIFICATION')

    def test_hindi_explanations_and_explicit_question_fallback(self):
        result=run(answers=ANSWERS|{'monthly_income':None},language='hi')
        self.assertIn('पात्रता',result.explanation)
        self.assertTrue(result.questions_needed[0].translation_fallback)
        self.assertEqual(result.questions_needed[0].content_language,'en')


class EligibilityAPITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://test')
        self.addAsyncCleanup(self.client.aclose)
        self.addCleanup(app.dependency_overrides.clear)

    def provider(self,data=None):
        provider=Mock();provider.get_rule_set.return_value=RuleSet.model_validate(fixture() if data is None else data)
        app.dependency_overrides[get_rule_provider]=lambda:provider
        return provider

    async def test_default_provider_blocks_all_five_drafts_and_unknown_ids_without_database(self):
        with patch('psycopg.connect',side_effect=AssertionError('No database')),patch('socket.create_connection',side_effect=AssertionError('No network')):
            for identifier in [f'in-cen-00000{i}' for i in range(1,6)]+['unknown-scheme']:
                response=await self.client.post('/api/v1/eligibility/evaluate',json={'scheme_id':identifier,'answers':{'age':35}})
                self.assertEqual(response.status_code,200)
                self.assertEqual(response.json()['status'],'NEEDS_VERIFICATION')
                self.assertEqual(response.json()['evaluated_conditions'],[])
                self.assertEqual(response.headers['cache-control'],'no-store')

    async def test_synthetic_fixture_api_explanations_questions_and_source_preservation(self):
        provider=self.provider()
        response=await self.client.post('/api/v1/eligibility/evaluate',json={'scheme_id':'synthetic-only','answers':ANSWERS})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['status'],'ELIGIBLE')
        self.assertEqual(response.json()['sources'][0]['reference_id'],'fixture-source')
        provider.get_rule_set.assert_called_once_with('synthetic-only')
        response=await self.client.post('/api/v1/eligibility/evaluate',json={'scheme_id':'synthetic-only','answers':ANSWERS|{'age':None},'language':'hi'})
        self.assertEqual(response.json()['status'],'NEEDS_VERIFICATION')
        self.assertEqual(response.json()['missing_answers'],['age'])

    async def test_unpublished_provider_record_cannot_be_approved_by_client(self):
        data=fixture();data['publication_status']='draft';self.provider(data)
        response=await self.client.post('/api/v1/eligibility/evaluate',json={'scheme_id':'synthetic-only','answers':ANSWERS})
        self.assertEqual(response.json()['status'],'NEEDS_VERIFICATION')
        self.assertTrue(all(r['result']=='UNKNOWN' for r in response.json()['evaluated_conditions']))
        response=await self.client.post('/api/v1/eligibility/evaluate',json={'scheme_id':'synthetic-only','answers':ANSWERS,'approval_status':'approved'})
        self.assertEqual(response.status_code,422)

    async def test_invalid_request_and_answers_are_sanitized(self):
        self.provider()
        invalid=[{'scheme_id':'../bad'}, {'scheme_id':'synthetic-only','language':'xx'},
                 {'scheme_id':'synthetic-only','sensitive-value':'secret'},
                 {'scheme_id':'synthetic-only','answers':{'age':['sensitive-value']}},
                 {'scheme_id':'synthetic-only','answers':{'age':True}},
                 {'scheme_id':'synthetic-only','answers':{'age':'sensitive-value'}},
                 {'scheme_id':'synthetic-only','answers':{'age':10**500}},
                 {'scheme_id':'synthetic-only','answers':{'sensitive-value':{'nested':'secret'}}},
                 {'scheme_id':'synthetic-only','answers':{f'field_{i}':1 for i in range(65)}}]
        for payload in invalid:
            response=await self.client.post('/api/v1/eligibility/evaluate',json=payload)
            self.assertEqual(response.status_code,422,response.text)
            self.assertNotIn('sensitive-value',response.text)
            self.assertNotIn('secret',response.text)
        for body in ('{"scheme_id":"synthetic-only","answers":{"age":NaN}}','{broken'):
            response=await self.client.post('/api/v1/eligibility/evaluate',content=body,headers={'Content-Type':'application/json'})
            self.assertEqual(response.status_code,422)

    async def test_cors_docs_and_existing_health(self):
        response=await self.client.options('/api/v1/eligibility/evaluate',headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'POST'})
        self.assertEqual(response.status_code,200)
        self.assertIn('POST',response.headers['access-control-allow-methods'])
        self.assertIn('/api/v1/eligibility/evaluate',(await self.client.get('/openapi.json')).json()['paths'])
        self.assertEqual((await self.client.get('/health')).status_code,200)

    async def test_provider_cannot_substitute_another_scheme(self):
        self.provider()
        response=await self.client.post('/api/v1/eligibility/evaluate',json={'scheme_id':'different','answers':ANSWERS})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json()['error']['code'],'RULE_SET_INVALID')


if __name__=='__main__':unittest.main()
