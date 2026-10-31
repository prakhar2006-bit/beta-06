"""Synthetic published snapshots and approvals. No live database or government approval."""
from contextlib import contextmanager
from copy import deepcopy
from datetime import date
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch
from uuid import NAMESPACE_URL, uuid5

import httpx
from pydantic import ValidationError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import app
from app.core.errors import APIError
from app.db.policies import PublishedPolicy, PublishedPolicyRepository, snapshot_digest
from app.eligibility.approvals import ApprovalManifest, ExecutionApproval, load_approvals
from app.eligibility.engine import evaluate
from app.eligibility.provider import TrustedPolicyProvider, get_rule_provider
from test_eligibility import ANSWERS, TODAY, fixture


def uid(key):return str(uuid5(NAMESPACE_URL,'synthetic-policy-provider:'+key))


def published():
    data=fixture()
    fields=deepcopy(data['fields']);fields[0]['unit']='years'
    rows=[];annotations=[];links=[]
    for n in data['nodes']:
        predicate=n['node_type']=='predicate'
        rows.append(dict(id=uid(n['rule_id']),rule_key=n['rule_id'],parent_id=uid(n['parent_id']) if n['parent_id'] else None,
            node_type=n['node_type'],attribute=n['attribute'],operator=n['operator'],expected_value=n['expected_value'],
            unit='years' if n['attribute']=='age' else 'INR' if n['attribute']=='monthly_income' else None,
            time_basis='synthetic_application',confidence='VERIFIED',uncertainty_reason=None))
        annotations.append(dict(rule_id=uid(n['rule_id']),label=n['label'],enabled=True,applicability_confirmed=True))
        if predicate:links.append(dict(rule_id=uid(n['rule_id']),evidence_id=uid('evidence')))
    snapshot=PublishedPolicy.model_validate(dict(scheme_id='synthetic-only',scheme_database_id=uid('scheme'),lifecycle_status='active',
        version_id=uid('version'),version_number=1,effective_from='2026-01-01',effective_to=None,last_checked_date='2026-01-02',
        published_at='2026-01-03T00:00:00Z',rules=rows,rule_evidence=links,sources=[dict(id=uid('evidence'),
            locator='Synthetic clauses',supporting_text='Synthetic policy, not government guidance.',last_checked_date='2026-01-01',
            content_sha256='a'*64,fetched_at='2026-01-01T00:00:00Z',source_updated_at=None,
            original_url='https://example.invalid/synthetic-policy',source_title='Synthetic fixture',license_url=None)]))
    approval=ExecutionApproval.model_validate(dict(scheme_id='synthetic-only',version_id=uid('version'),version_number=1,
        snapshot_sha256=snapshot_digest(snapshot),execution_approved=True,complete=True,reviewer_reference='synthetic-reviewer',
        reviewed_on='2026-01-04',valid_until='2027-01-01',effective_from='2026-01-01',allowed_source_hosts=['example.invalid'],
        fields=fields,nodes=annotations))
    return snapshot,approval


def provider(snapshot=None,approval=None):
    original,entry=published()
    repo=Mock();repo.get_latest.return_value=original if snapshot is None else snapshot
    manifest=ApprovalManifest(schema_version='1.0',approvals=(entry if approval is None else approval,))
    return TrustedPolicyProvider(repo,manifest,as_of=TODAY),repo


class ProviderTests(unittest.TestCase):
    def test_approved_published_tree_and_sources_preserved(self):
        p,repo=provider();rules=p.get_rule_set('synthetic-only')
        self.assertIsNotNone(rules)
        self.assertEqual(evaluate(rules,'synthetic-only',ANSWERS,as_of=TODAY).status,'ELIGIBLE')
        self.assertEqual({n.rule_id for n in rules.nodes},{uid(n['rule_id']) for n in fixture()['nodes']})
        self.assertEqual(rules.sources[0].original_url,'https://example.invalid/synthetic-policy')
        self.assertTrue(all(n.source_ids for n in rules.nodes if n.node_type=='predicate'))
        repo.get_latest.assert_called_once_with('synthetic-only')

    def test_absent_unapproved_incomplete_conflicted_or_expired_approval_skips_database(self):
        _,approval=published()
        for change in ({'execution_approved':False},{'complete':False},{'conflicts':['Conflict']},
                       {'unresolved_conditions':['Manual requirement']},{'valid_until':date(2026,2,1)}):
            p,repo=provider(approval=approval.model_copy(update=change))
            self.assertIsNone(p.get_rule_set('synthetic-only'));repo.get_latest.assert_not_called()
        p,repo=provider();self.assertIsNone(p.get_rule_set('unknown'));repo.get_latest.assert_not_called()

    def test_unpublished_or_latest_version_substitution_is_unavailable(self):
        p,repo=provider();repo.get_latest.return_value=None
        self.assertIsNone(p.get_rule_set('synthetic-only'))
        snapshot,_=published()
        for change in ({'version_id':uid('other-version')},{'version_number':2},{'scheme_id':'another'},
                       {'lifecycle_status':'closed'},{'effective_from':None},{'last_checked_date':None}):
            p,_=provider(snapshot=PublishedPolicy.model_validate(snapshot.model_dump()|change))
            self.assertIsNone(p.get_rule_set('synthetic-only'))

    def test_content_digest_rejects_missing_condition_or_changed_provenance(self):
        snapshot,_=published()
        for kind in ('condition','source','link','body'):
            data=snapshot.model_dump(mode='json')
            if kind=='condition':data['rules'].pop()
            elif kind=='source':data['sources']=[]
            elif kind=='link':data['rule_evidence'].pop()
            else:data['sources'][0]['supporting_text']='Changed source meaning'
            p,_=provider(snapshot=PublishedPolicy.model_validate(data))
            self.assertIsNone(p.get_rule_set('synthetic-only'))

    def test_malformed_unverified_unsupported_incomplete_or_uncited_even_with_matching_digest(self):
        snapshot,approval=published()
        for kind in ('cycle','arity','unsupported','unverified','source','source-host','hash','uncertain','missing-node','conflict'):
            data=snapshot.model_dump(mode='json');a=approval.model_dump(mode='json')
            target=next(n for n in data['rules'] if n['rule_key']=='age_min')
            if kind=='cycle':target['parent_id']=target['id']
            elif kind=='arity':next(n for n in data['rules'] if n['parent_id'] is None)['node_type']='not'
            elif kind=='unsupported':target['operator']='exists'
            elif kind=='unverified':target['confidence']='UNCERTAIN'
            elif kind=='uncertain':target['uncertainty_reason']='Policy unresolved'
            elif kind=='source':data['rule_evidence']=[];data['sources']=[]
            elif kind=='source-host':data['sources'][0]['original_url']='https://unapproved.invalid/policy'
            elif kind=='hash':data['sources'][0]['content_sha256']='invalid'
            elif kind=='missing-node':a['nodes'].pop()
            elif kind=='conflict':next(n for n in data['rules'] if n['rule_key']=='age_max')['expected_value']=10
            changed=PublishedPolicy.model_validate(data);a['snapshot_sha256']=snapshot_digest(changed)
            p,_=provider(changed,ExecutionApproval.model_validate(a))
            with self.subTest(kind=kind):self.assertIsNone(p.get_rule_set('synthetic-only'))

    def test_and_or_not_semantics_loaded_without_flattening(self):
        snapshot,approval=published();data=snapshot.model_dump(mode='json')
        # Add a NOT wrapper to the existing Boolean predicate, then an OR group
        # around state/occupation. These remain explicitly synthetic rules.
        target=next(n for n in data['rules'] if n['rule_key']=='boolean');target['expected_value']=True;target['parent_id']=uid('not')
        extra=dict(id=uid('not'),rule_key='exclusion',parent_id=uid('root'),node_type='not',attribute=None,operator=None,expected_value=None,
                   unit=None,time_basis=None,confidence='VERIFIED',uncertainty_reason=None)
        data['rules'].append(extra)
        extra_or=extra|dict(id=uid('or'),rule_key='alternative',node_type='or');data['rules'].append(extra_or)
        for n in data['rules']:
            if n['rule_key'] in ('state','occupation'):n['parent_id']=uid('or')
        changed=PublishedPolicy.model_validate(data)
        annotations=approval.model_dump(mode='json')['nodes']+[dict(rule_id=uid(key),label={'en':'Synthetic '+key},enabled=True,applicability_confirmed=True) for key in ('not','or')]
        a=ExecutionApproval.model_validate(approval.model_dump(mode='json')|dict(nodes=annotations,snapshot_sha256=snapshot_digest(changed)))
        p,_=provider(changed,a);rules=p.get_rule_set('synthetic-only')
        self.assertIsNotNone(rules)
        self.assertEqual(evaluate(rules,'synthetic-only',ANSWERS|{'state':None},as_of=TODAY).status,'ELIGIBLE')
        self.assertEqual(evaluate(rules,'synthetic-only',ANSWERS|{'has_existing_benefit':True},as_of=TODAY).status,'INELIGIBLE')

    def test_database_failure_propagates_sanitized_without_fallback(self):
        p,repo=provider();repo.get_latest.side_effect=APIError(503,'DATABASE_UNAVAILABLE','Database service is unavailable.')
        with self.assertRaises(APIError) as error:p.get_rule_set('synthetic-only')
        self.assertEqual(error.exception.code,'DATABASE_UNAVAILABLE')

    def test_server_manifest_is_empty_and_reloaded_with_no_database(self):
        self.assertEqual(load_approvals().approvals,())
        with patch('app.eligibility.provider.PublishedPolicyRepository') as repo:
            self.assertIsNone(get_rule_provider().get_rule_set('in-cen-000002'))
            repo.return_value.get_latest.assert_not_called()
        with patch('app.eligibility.approvals.APPROVAL_FILE') as path:
            path.stat.return_value.st_size=20
            path.read_text.return_value='{"schema_version":"1.0","approvals":[],"approvals":[]}'
            with self.assertRaises(APIError):load_approvals()


class PolicyRepositoryTests(unittest.TestCase):
    def test_one_read_only_snapshot_parameterized_published_view_queries(self):
        snapshot,_=published();raw=snapshot.model_dump(mode='python')
        conn=MagicMock();cursor=conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value={k:v for k,v in raw.items() if k not in ('rules','rule_evidence','sources')}
        cursor.fetchall.side_effect=[list(raw['rules']),list(raw['rule_evidence']),list(raw['sources'])]
        @contextmanager
        def connection():yield conn
        with patch('app.db.policies.open_connection',connection):
            result=PublishedPolicyRepository().get_latest("' OR 1=1 --")
        self.assertEqual(result,snapshot)
        conn.cursor.assert_called_once();self.assertEqual(cursor.execute.call_count,4)
        for call in cursor.execute.call_args_list:
            sql,params=call.args
            self.assertIn('scheme_catalog.published_',sql)
            self.assertNotIn("' OR 1=1",sql)
            self.assertNotIn('scheme_catalog.scheme_versions',sql)
            self.assertNotRegex(sql,r'\b(INSERT|UPDATE|DELETE|GRANT|ALTER)\b')
        self.assertEqual(cursor.execute.call_args_list[0].args[1],{'scheme_id':"' OR 1=1 --"})

    def test_unpublished_no_child_reads(self):
        conn=MagicMock();cursor=conn.cursor.return_value.__enter__.return_value;cursor.fetchone.return_value=None
        @contextmanager
        def connection():yield conn
        with patch('app.db.policies.open_connection',connection):self.assertIsNone(PublishedPolicyRepository().get_latest('unpublished'))
        self.assertEqual(cursor.execute.call_count,1)


class ProviderAPITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://test')
        self.addAsyncCleanup(self.client.aclose);self.addCleanup(app.dependency_overrides.clear)
        self.provider,self.repo=provider()
        app.dependency_overrides[get_rule_provider]=lambda:self.provider

    async def test_evaluate_and_multistep_questionnaire_connected(self):
        response=await self.client.post('/api/v1/eligibility/evaluate',json={'scheme_id':'synthetic-only','answers':ANSWERS})
        self.assertEqual(response.status_code,200,response.text);self.assertEqual(response.json()['status'],'ELIGIBLE')
        version=response.json()['rule_set_version']
        response=await self.client.post('/api/v1/questionnaire/start',json={'scheme_id':'synthetic-only'})
        q=response.json();seen=set()
        while q['current_question']:
            key=q['current_question']['question_id'];self.assertNotIn(key,seen);seen.add(key)
            response=await self.client.post('/api/v1/questionnaire/answer',json={'state':q['state'],'question_id':key,'value':ANSWERS[key]})
            self.assertEqual(response.status_code,200,response.text);q=response.json()
            self.assertEqual(q['evaluation']['rule_set_version'],version)
        self.assertEqual(q['evaluation']['status'],'ELIGIBLE')
        response=await self.client.post('/api/v1/questionnaire/next',json={'state':q['state']})
        self.assertEqual(response.json(),q)

    async def test_stale_or_substituted_policy_and_client_rules_rejected(self):
        q=(await self.client.post('/api/v1/questionnaire/start',json={'scheme_id':'synthetic-only'})).json()
        snapshot,_=published();self.repo.get_latest.return_value=snapshot.model_copy(update={'version_number':2})
        response=await self.client.post('/api/v1/questionnaire/next',json={'state':q['state']})
        self.assertEqual(response.status_code,409)
        self.assertEqual(response.json()['error']['code'],'POLICY_CHANGED')
        for payload in ({'scheme_id':'synthetic-only','answers':ANSWERS,'rules':[]},
                        {'scheme_id':'synthetic-only','answers':ANSWERS,'version_id':uid('version')}):
            self.assertEqual((await self.client.post('/api/v1/eligibility/evaluate',json=payload)).status_code,422)

    async def test_unapproved_and_database_failure_do_not_produce_eligibility(self):
        self.provider.approvals={}
        result=await self.client.post('/api/v1/eligibility/evaluate',json={'scheme_id':'synthetic-only','answers':ANSWERS})
        self.assertEqual(result.json()['status'],'NEEDS_VERIFICATION')
        self.provider,self.repo=provider();self.repo.get_latest.side_effect=APIError(503,'DATABASE_UNAVAILABLE','Database service is unavailable.')
        result=await self.client.post('/api/v1/eligibility/evaluate',json={'scheme_id':'synthetic-only','answers':ANSWERS})
        self.assertEqual(result.status_code,503);self.assertNotIn('postgres',result.text)


if __name__=='__main__':unittest.main()
