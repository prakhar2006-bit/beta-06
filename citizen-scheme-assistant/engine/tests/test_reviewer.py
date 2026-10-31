"""Local reviewer diagnostics; no public review interface or live database."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import httpx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import app
from app.eligibility.approvals import ApprovalManifest, ExecutionApproval
from app.db.guidance import PublishedGuidance
from reviewer.preview import main, review_record, runtime_preview
from test_eligibility import TODAY
from test_policy_provider import published
from test_results import guidance_data, setup_provider
from test_verification import fixture
from ingestion.verification import build_verified_draft


def payload():
    manifest,ledger,data=fixture()
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp);(path/'source.txt').write_bytes(data)
        return build_verified_draft(manifest,ledger,path)[0]


class ReviewerTests(unittest.TestCase):
    def test_real_gate_failure_and_draft_blockers_not_ready(self):
        record=payload();version=record['rows']['scheme_versions'][0]
        gate=dict(scheme_id='test-only',version_number=1,current_status='draft',guard_passed=False,
                  transition='draft_to_reviewed',blocker='Reviewed English and Hindi translations required')
        result=review_record(record,gate,ApprovalManifest(schema_version='1.0',approvals=()),as_of=TODAY)
        self.assertFalse(result['ready_for_publication']);self.assertFalse(result['live_verified'])
        self.assertIn('EXECUTION_APPROVAL_MISSING',result['blocker_codes'])
        self.assertIn('UNVERIFIED_RULE_NODES',result['blocker_codes'])
        self.assertIsNone(result['runtime']['policy_snapshot_sha256'])
        self.assertIsNone(result['runtime']['guidance_snapshot_sha256'])
        self.assertNotIn('artifact_path',str(result))

    def test_incomplete_and_stale_policy_hash_reuse_trusted_provider_rejection(self):
        policy,approval=published()
        for update in ({'complete':False},{'execution_approved':False},{'snapshot_sha256':'0'*64}):
            changed=approval.model_copy(update=update)
            result=runtime_preview(policy.scheme_id,ApprovalManifest(schema_version='1.0',approvals=(changed,)),policy,as_of=TODAY)
            self.assertFalse(result['trusted_provider_accepted'])
            if 'snapshot_sha256' in update:self.assertFalse(result['policy_hash_matches'])

    def test_fully_reviewed_runtime_record_uses_provider_and_guidance_service(self):
        provider,guidance=setup_provider();policy,_=published()
        manifest=ApprovalManifest(schema_version='1.0',approvals=tuple(provider.approvals.values()))
        result=runtime_preview(policy.scheme_id,manifest,policy,guidance,as_of=TODAY)
        self.assertTrue(result['ready_for_live_eligibility'])
        self.assertTrue(result['policy_hash_matches']);self.assertTrue(result['guidance_hash_matches'])
        self.assertEqual(result['guidance_sections']['required_documents']['status'],'available')
        self.assertEqual(result['missing_guidance_attestations']['documents'],[])
        self.assertNotIn('synthetic-reviewer',str(result))

    def test_missing_guidance_attestation_and_stale_guidance_hash(self):
        policy,approval=published();guidance=PublishedGuidance.model_validate(guidance_data())
        result=runtime_preview(policy.scheme_id,ApprovalManifest(schema_version='1.0',approvals=(approval,)),policy,guidance,as_of=TODAY)
        self.assertTrue(result['trusted_provider_accepted'])
        self.assertFalse(result['guidance_approval_present'])
        self.assertTrue(result['missing_guidance_attestations']['documents'])
        self.assertEqual(result['guidance_sections']['required_documents']['status'],'unavailable')
        provider,guidance=setup_provider();a=provider.approvals[policy.scheme_id].model_dump(mode='json')
        a['guidance']['snapshot_sha256']='0'*64
        result=runtime_preview(policy.scheme_id,ApprovalManifest(schema_version='1.0',approvals=(ExecutionApproval.model_validate(a),)),policy,guidance,as_of=TODAY)
        self.assertFalse(result['guidance_hash_matches'])
        self.assertEqual(result['guidance_sections']['benefits']['status'],'unavailable')

    def test_reviewed_record_sql_success_never_bypasses_unverified_rules(self):
        record=payload();record['blockers']=[]
        record['verification'].update(human_approval=True,publication_ready=True)
        record['rows']['scheme_versions'][0].update(status='reviewed',reviewer_reference='private-reviewer-secret',reviewed_at='2026-10-31',last_checked_date='2026-10-31')
        gate=dict(scheme_id='test-only',version_number=1,current_status='reviewed',guard_passed=True,transition='reviewed_to_published',blocker=None)
        result=review_record(record,gate,ApprovalManifest(schema_version='1.0',approvals=()),as_of=TODAY)
        self.assertFalse(result['ready_for_publication'])
        self.assertNotIn('private-reviewer-secret',str(result))

    def test_cli_requires_local_review_flag_before_reading_files(self):
        with patch('reviewer.preview.validate_collection',side_effect=AssertionError('Must not read')):
            with self.assertRaises(SystemExit) as error:main(['--collection','missing','--output','missing'])
            self.assertEqual(error.exception.code,2)

    def test_private_snapshot_preview_cannot_connect_to_database(self):
        policy,approval=published()
        with patch('psycopg.connect',side_effect=AssertionError('No live DB')),patch('socket.create_connection',side_effect=AssertionError('No network')):
            result=runtime_preview(policy.scheme_id,ApprovalManifest(schema_version='1.0',approvals=(approval,)),policy,as_of=TODAY)
            self.assertTrue(result['trusted_provider_accepted'])


class PublicIsolationTests(unittest.IsolatedAsyncioTestCase):
    async def test_reviewer_is_not_exposed_to_public_clients(self):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://test') as client:
            for path in ('/api/v1/reviewer','/api/v1/reviewer/preview','/api/v1/admin/readiness'):
                response=await client.get(path)
                self.assertEqual(response.status_code,404)
                self.assertNotIn('reviewer_reference',response.text)
            paths=(await client.get('/openapi.json')).json()['paths']
            self.assertFalse(any('reviewer' in p or 'admin' in p for p in paths))


if __name__=='__main__':unittest.main()
