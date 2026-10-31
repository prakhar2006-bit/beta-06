"""Client-held synthetic questionnaires; never government criteria or live IO."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

import httpx
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app
from app.eligibility import questionnaire
from app.eligibility.provider import get_rule_provider
from app.schemas.eligibility import RuleSet
from app.schemas.questionnaire import AnswerRequest, QuestionnaireState, StartRequest
from test_eligibility import TODAY, fixture, node


def policy(kind='age'):
    data = fixture()
    if kind == 'age':
        data['nodes'] = [node('age_min', 'age', 'gte', 18, parent=None)]
    elif kind == 'and':
        data['nodes'] = [node('root', parent=None, kind='and'), node('age_min','age','gte',18),
                         node('age_max','age','lte',60), node('income','monthly_income','lte','1000.00')]
    elif kind == 'or':
        data['nodes'] = [node('root',parent=None,kind='or'),node('state','state','eq','state_a'),
                         node('occupation','occupation','eq','worker')]
    elif kind == 'not':
        data['nodes'] = [node('root',parent=None,kind='and'),node('excluded',kind='not'),
                        node('existing','has_existing_benefit','eq',True,parent='excluded'),node('age','age','gte',18)]
    return data


class QuestionnaireTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://test')
        self.addAsyncCleanup(self.client.aclose)
        self.addCleanup(app.dependency_overrides.clear)
        self.provider = Mock()
        self.set_policy()
        app.dependency_overrides[get_rule_provider] = lambda:self.provider

    def set_policy(self, data=None):
        self.provider.get_rule_set.return_value = RuleSet.model_validate(policy() if data is None else data)

    async def start(self, language='en'):
        response = await self.client.post('/api/v1/questionnaire/start',json={'scheme_id':'synthetic-only','language':language})
        self.assertEqual(response.status_code,200,response.text)
        return response.json()

    async def act(self, result, question_id, action='answer', value=30):
        payload={'state':result['state'],'question_id':question_id,'action':action}
        if action=='answer':payload['value']=value
        response=await self.client.post('/api/v1/questionnaire/answer',json=payload)
        self.assertEqual(response.status_code,200,response.text)
        return response.json()

    async def test_simple_age_state_and_completed_eligible(self):
        initial=await self.start()
        self.assertEqual(initial['current_question']['question_id'],'age')
        self.assertEqual(initial['current_question']['answer_type'],'integer')
        self.assertFalse(initial['completed'])
        result=await self.act(initial,'age',value=18)
        self.assertTrue(result['completed'])
        self.assertEqual(result['completion_reason'],'DECISION_REACHED')
        self.assertEqual(result['evaluation']['status'],'ELIGIBLE')
        self.assertEqual(result['progress'],{'answered':1,'unknown':0,'skipped':0,'remaining':0})
        self.assertEqual(result['evaluation']['sources'][0]['original_url'],'https://example.invalid/synthetic-policy')
        self.assertEqual(initial['state']['answers'],{})

    async def test_and_multiple_conditions_and_duplicate_age_question_prevention(self):
        self.set_policy(policy('and'))
        result=await self.start()
        self.assertEqual(result['current_question']['question_id'],'age')
        self.assertEqual(len(result['current_question']['rule_ids']),2)
        result=await self.act(result,'age')
        self.assertEqual(result['current_question']['question_id'],'monthly_income')
        self.assertEqual(result['progress']['remaining'],1)
        self.assertEqual(result['current_question']['answer_type'],'decimal')
        result=await self.act(result,'monthly_income',value='999.99')
        self.assertEqual(result['evaluation']['status'],'ELIGIBLE')

    async def test_or_short_circuit_does_not_ask_other_branch(self):
        self.set_policy(policy('or'))
        result=await self.start()
        question=result['current_question']['question_id']
        value='state_a' if question=='state' else 'worker'
        result=await self.act(result,question,value=value)
        self.assertTrue(result['completed'])
        self.assertIsNone(result['current_question'])
        self.assertEqual(result['evaluation']['status'],'ELIGIBLE')
        self.assertEqual(result['evaluation']['questions_needed'],[])

    async def test_not_exclusion_priority_and_early_ineligibility(self):
        self.set_policy(policy('not'))
        result=await self.start()
        self.assertEqual(result['current_question']['question_id'],'has_existing_benefit')
        self.assertEqual(result['current_question']['allowed_values'],[True,False])
        result=await self.act(result,'has_existing_benefit',value=True)
        self.assertEqual(result['evaluation']['status'],'INELIGIBLE')
        self.assertTrue(result['completed'])
        self.assertNotIn('age',result['state']['answers'])

    async def test_unknown_answer_is_not_false_and_not_reasked(self):
        result=await self.act(await self.start(),'age',value=None)
        self.assertEqual(result['state']['answers'],{'age':None})
        self.assertTrue(result['completed'])
        self.assertEqual(result['completion_reason'],'VERIFICATION_REQUIRED')
        self.assertEqual(result['evaluation']['status'],'NEEDS_VERIFICATION')
        self.assertEqual(result['missing_information']['unknown_fields'],['age'])
        again=await self.client.post('/api/v1/questionnaire/next',json={'state':result['state']})
        self.assertEqual(again.json(),result)

    async def test_skip_advances_and_all_skipped_remains_unknown(self):
        self.set_policy(policy('and'))
        result=await self.act(await self.start(),'age',action='skip')
        self.assertEqual(result['current_question']['question_id'],'monthly_income')
        result=await self.act(result,'monthly_income',action='skip')
        self.assertTrue(result['completed'])
        self.assertEqual(result['evaluation']['status'],'NEEDS_VERIFICATION')
        self.assertEqual(result['progress']['skipped'],2)
        self.assertEqual(result['state']['answers'],{})

    async def test_changed_answers_reopen_decision_and_clear_reasks(self):
        result=await self.act(await self.start(),'age',value=17)
        self.assertEqual(result['evaluation']['status'],'INELIGIBLE')
        result=await self.act(result,'age',value=30)
        self.assertEqual(result['evaluation']['status'],'ELIGIBLE')
        result=await self.act(result,'age',action='clear')
        self.assertFalse(result['completed'])
        self.assertEqual(result['current_question']['question_id'],'age')
        result=await self.act(result,'age',action='skip')
        result=await self.act(result,'age',value=30)
        self.assertEqual(result['state']['skipped'],[])
        self.assertEqual(result['evaluation']['status'],'ELIGIBLE')

    async def test_changed_or_answer_reopens_only_remaining_branch(self):
        self.set_policy(policy('or'))
        result=await self.act(await self.start(),'occupation',value='worker')
        self.assertTrue(result['completed'])
        result=await self.act(result,'occupation',value='other')
        self.assertFalse(result['completed'])
        self.assertEqual(result['current_question']['question_id'],'state')
        result=await self.act(result,'state',value='state_b')
        self.assertEqual(result['evaluation']['status'],'INELIGIBLE')
        result=await self.act(result,'occupation',value='worker')
        self.assertEqual(result['evaluation']['status'],'ELIGIBLE')

    async def test_reviewed_hindi_and_unreviewed_or_missing_hindi_fallback(self):
        for reviewed,exists in [(True,True),(False,True),(False,False)]:
            data=policy();field=data['fields'][0]
            field['question']['hi']='समीक्षित परीक्षण आयु प्रश्न?' if exists else None
            field['question_reviewed_languages']=['en','hi'] if reviewed else ['en']
            self.set_policy(data)
            result=await self.start('hi')
            question=result['current_question']
            self.assertEqual(question['content_language'],'hi' if reviewed else 'en')
            self.assertEqual(question['translation_fallback'],not reviewed)
            if not reviewed:self.assertNotIn('समीक्षित परीक्षण आयु प्रश्न',str(result))
        data=policy();data['fields'][0]['question_reviewed_languages']=[];self.set_policy(data)
        result=await self.start()
        self.assertTrue(result['completed'])
        self.assertEqual(result['missing_information']['unreviewed_question_fields'],['age'])
        self.assertIn('QUESTION_TEXT_NOT_REVIEWED',result['missing_information']['review_blockers'])
        response=await self.client.post('/api/v1/questionnaire/answer',json={'state':result['state'],'question_id':'age','value':30})
        self.assertEqual(response.status_code,409)
        self.assertEqual(response.json()['error']['code'],'QUESTION_NOT_REVIEWED')

    async def test_unpublished_unverified_incomplete_and_empty_questionnaires(self):
        for change,value in [('publication_status','draft'),('execution_enabled',False),('conflicts',['Unresolved synthetic conflict'])]:
            data=policy();data[change]=value;self.set_policy(data)
            result=await self.start()
            self.assertTrue(result['completed'])
            self.assertIsNone(result['current_question'])
            self.assertEqual(result['evaluation']['status'],'NEEDS_VERIFICATION')
        data=policy();data['nodes'][0]['confidence']='UNCERTAIN';self.set_policy(data)
        self.assertIsNone((await self.start())['current_question'])
        data=policy();data['complete']=False;self.set_policy(data)
        result=await self.act(await self.start(),'age',value=30)
        self.assertTrue(result['completed'])
        self.assertEqual(result['evaluation']['status'],'NEEDS_VERIFICATION')
        self.assertIn('INCOMPLETE_RULE_SET',result['missing_information']['review_blockers'])
        self.provider.get_rule_set.return_value=None
        result=await self.start()
        self.assertTrue(result['completed'])
        self.assertEqual(result['progress']['remaining'],0)

    async def test_invalid_answer_types_state_and_no_rule_injection(self):
        result=await self.start()
        payload={'state':result['state'],'question_id':'age','value':True}
        response=await self.client.post('/api/v1/questionnaire/answer',json=payload)
        self.assertEqual(response.status_code,422)
        self.assertEqual(response.headers['cache-control'],'no-store')
        for field,value in [('rules',[]),('eligibility_status','ELIGIBLE'),('progress',{}),('approved',True)]:
            state=deepcopy(result['state']);state[field]=value
            response=await self.client.post('/api/v1/questionnaire/next',json={'state':state})
            self.assertEqual(response.status_code,422)
        state=deepcopy(result['state']);state['answers']={'age':'sensitive-value'}
        response=await self.client.post('/api/v1/questionnaire/next',json={'state':state})
        self.assertEqual(response.status_code,422)
        self.assertNotIn('sensitive-value',response.text)
        state=deepcopy(result['state']);state['answers']={'sensitive-key':{'secret':'sensitive-value'}}
        response=await self.client.post('/api/v1/questionnaire/next',json={'state':state})
        self.assertEqual(response.status_code,422)
        self.assertNotIn('sensitive-key',response.text)
        self.assertNotIn('sensitive-value',response.text)
        for skipped in [['age','age'],['occupation']]:
            state=deepcopy(result['state']);state['skipped']=skipped
            response=await self.client.post('/api/v1/questionnaire/next',json={'state':state})
            self.assertEqual(response.status_code,422)

    async def test_invalid_operations_and_language_change(self):
        result=await self.start()
        invalid=[{'action':'answer'}, {'action':'skip','value':None}, {'action':'clear','value':30},
                 {'action':'answer','value':30.5}, {'action':'answer','value':{'nested':'secret'}},
                 {'action':'answer','value':10**500}]
        for operation in invalid:
            response=await self.client.post('/api/v1/questionnaire/answer',json={
                'state':result['state'],'question_id':'age',**operation})
            self.assertEqual(response.status_code,422,response.text)
        state=deepcopy(result['state']);state['answers']={'age':30};state['skipped']=['age']
        self.assertEqual((await self.client.post('/api/v1/questionnaire/next',json={'state':state})).status_code,422)
        state=deepcopy(result['state']);state['language']='hi'
        response=await self.client.post('/api/v1/questionnaire/next',json={'state':state})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['state']['language'],'hi')
        self.assertEqual(response.json()['current_question']['content_language'],'en')

    async def test_pure_workflow_has_no_filesystem_network_or_database_access(self):
        with patch('builtins.open',side_effect=AssertionError('No file IO')), \
             patch('pathlib.Path.write_text',side_effect=AssertionError('No file writes')), \
             patch('pathlib.Path.write_bytes',side_effect=AssertionError('No file writes')), \
             patch('psycopg.connect',side_effect=AssertionError('No DB')), \
             patch('socket.create_connection',side_effect=AssertionError('No network')):
            initial=questionnaire.start(StartRequest(scheme_id='synthetic-only'),self.provider,as_of=TODAY)
            changed=questionnaire.answer(AnswerRequest(state=initial.state,question_id='age',value=30),self.provider,as_of=TODAY)
            self.assertEqual(changed.evaluation.status,'ELIGIBLE')
            self.assertEqual(initial.state.answers,{})

    async def test_policy_version_or_approval_change_requires_restart(self):
        result=await self.start()
        for change,value in [('version','fixture-2'),('execution_enabled',False)]:
            data=policy();data[change]=value;self.set_policy(data)
            response=await self.client.post('/api/v1/questionnaire/next',json={'state':result['state']})
            self.assertEqual(response.status_code,409)
            self.assertEqual(response.json()['error']['code'],'POLICY_CHANGED')
        self.provider.get_rule_set.return_value=None
        self.assertEqual((await self.client.post('/api/v1/questionnaire/next',json={'state':result['state']})).status_code,409)

    async def test_out_of_scope_question_rejected_and_next_is_idempotent(self):
        result=await self.start()
        response=await self.client.post('/api/v1/questionnaire/answer',json={'state':result['state'],'question_id':'occupation','value':'worker'})
        self.assertEqual(response.status_code,409)
        for _ in range(2):
            response=await self.client.post('/api/v1/questionnaire/next',json={'state':result['state']})
            self.assertEqual(response.json(),result)

    async def test_no_storage_logging_or_cross_client_state(self):
        with patch('psycopg.connect',side_effect=AssertionError('No DB')),patch('socket.create_connection',side_effect=AssertionError('No network')),patch('logging.Logger._log') as log:
            result=await self.act(await self.start(),'age',value=47)
            self.assertEqual(result['state']['answers'],{'age':47})
            self.assertEqual((await self.start())['state']['answers'],{})
            for call in log.call_args_list:
                self.assertNotIn("'age': 47",str(call))
        # Nothing about answers is passed to the policy provider.
        self.assertTrue(all(call.args==('synthetic-only',) for call in self.provider.get_rule_set.call_args_list))

    async def test_default_government_drafts_and_docs_no_cache(self):
        app.dependency_overrides.clear()
        for i in range(1,6):
            response=await self.client.post('/api/v1/questionnaire/start',json={'scheme_id':f'in-cen-00000{i}','language':'hi'})
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.headers['cache-control'],'no-store')
            self.assertEqual(response.json()['evaluation']['status'],'NEEDS_VERIFICATION')
            self.assertIsNone(response.json()['current_question'])
            self.assertTrue(response.json()['completed'])
        paths=(await self.client.get('/openapi.json')).json()['paths']
        for action in ('start','next','answer'):self.assertIn('/api/v1/questionnaire/'+action,paths)
        self.assertEqual((await self.client.get('/health')).status_code,200)


if __name__=='__main__':unittest.main()
