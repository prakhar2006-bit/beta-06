"""Local read-only review; no live database adapter, credentials or publication API."""
import argparse
from datetime import date
from pathlib import Path
import subprocess
import sys

from app.db.guidance import guidance_digest
from app.db.policies import snapshot_digest
from app.eligibility.approvals import load_approvals
from app.eligibility.provider import TrustedPolicyProvider
from app.eligibility.engine import evaluate
from app.core.errors import APIError
from app.eligibility.questionnaire import fingerprint
from app.eligibility.results import explain
from app.schemas.results import ResultRequest
from ingestion.batch import validate_collection
from ingestion.prepare import InputError, digest, encode, parse_json

ENGINE=Path(__file__).resolve().parents[1]


def runtime_preview(scheme_id,manifest,policy=None,guidance=None,*,as_of):
    """Private diagnostics reuse the real provider and result service, with local snapshots."""
    class LocalRepository:
        def get_latest(self,key):
            return policy if policy is not None and policy.scheme_id==key else None
        def get_for_version(self,key,version):
            return guidance
    provider=TrustedPolicyProvider(LocalRepository(),manifest,as_of=as_of,guidance_repository=LocalRepository())
    approval=provider.approvals.get(scheme_id)
    rules=provider.get_rule_set(scheme_id)
    policy_hash=snapshot_digest(policy) if policy else None
    guidance_hash=guidance_digest(guidance) if guidance else None
    response=None
    if rules is None or guidance is not None:
        response=explain(ResultRequest(state={'scheme_id':scheme_id,'policy_fingerprint':fingerprint(rules)}),provider,as_of=as_of)
    evaluated=response.evaluation if response else evaluate(rules,scheme_id,{},as_of=as_of)
    attestation=approval.guidance if approval else None
    missing={}
    for key in ('benefits','documents','application_routes'):
        actual={str(r.id) for r in getattr(guidance,key)} if guidance else set()
        reviewed={str(r.item_id) for r in getattr(attestation,key)} if attestation else set()
        missing[key]=sorted(actual-reviewed)
    return {
        'execution_approval_present':approval is not None,
        'execution_reviewer_reference_present':bool(approval and approval.reviewer_reference),
        'execution_approved_flag':bool(approval and approval.execution_approved),
        'complete_attestation':bool(approval and approval.complete),
        'trusted_provider_accepted':rules is not None,
        'policy_snapshot_sha256':policy_hash,
        'policy_hash_matches':policy_hash==approval.snapshot_sha256 if approval and policy_hash else None,
        'guidance_snapshot_sha256':guidance_hash,
        'guidance_approval_present':attestation is not None,
        'guidance_hash_matches':guidance_hash==attestation.snapshot_sha256 if attestation and guidance_hash else None,
        'missing_guidance_attestations':missing,
        'guidance_sections':{k:({'status':getattr(response,k).status,'reason_code':getattr(response,k).reason_code} if response
            else {'status':'unavailable','reason_code':'GUIDANCE_SNAPSHOT_NOT_AVAILABLE'})
            for k in ('benefits','required_documents','application_guidance','official_application_urls')},
        'policy_review_blockers':list(evaluated.policy_review.blockers),
        'ready_for_live_eligibility':rules is not None,
    }


def review_record(payload,gate,manifest,*,as_of):
    rows=payload['rows'];scheme=rows['schemes'][0];version=rows['scheme_versions'][0]
    if (gate.get('scheme_id')!=scheme['stable_id'] or gate.get('version_number')!=version['version_number']
            or gate.get('current_status')!=version['status']):
        raise InputError('Local database probe does not match the reviewed record')
    runtime=runtime_preview(scheme['stable_id'],manifest,as_of=as_of)
    # Draft item identities are available even though no published projection exists.
    runtime['missing_guidance_attestations']={key:[r['id'] for r in rows.get(table,[])]
        for key,table in [('benefits','benefits'),('documents','required_documents'),('application_routes','application_routes')]}
    evidence_ids={e['id'] for e in rows.get('evidence',[])}
    linked={e['rule_id'] for e in rows.get('rule_evidence',[]) if e['evidence_id'] in evidence_ids}
    missing_evidence=[r['rule_key'] for r in rows.get('eligibility_rules',[]) if r['node_type']=='predicate' and r['id'] not in linked]
    unchecked_claims=[{'claim_id':c['claim_id'],'status':c['status']} for c in payload['verification']['claims'] if c['status']!='verified_official_guidance']
    translations={t['language_code']:t['review_status'] for t in rows.get('translations',[])}
    blockers=list(payload.get('blockers',[]))
    codes=[]
    if gate.get('guard_passed') is not True:codes.append('DATABASE_REVIEW_GUARD_NOT_PASSED')
    if version['status']!='reviewed':codes.append('HUMAN_REVIEW_TRANSITION_NOT_COMPLETED')
    if not payload['verification'].get('human_approval'):codes.append('HUMAN_POLICY_APPROVAL_MISSING')
    if not payload['verification'].get('publication_ready'):codes.append('PUBLICATION_ATTESTATION_MISSING')
    if unchecked_claims:codes.append('UNRESOLVED_OR_UNVERIFIED_CLAIMS')
    if missing_evidence:codes.append('PREDICATE_EVIDENCE_MISSING')
    if any(r['confidence']!='VERIFIED' for r in rows.get('eligibility_rules',[])):codes.append('UNVERIFIED_RULE_NODES')
    if any(translations.get(language)!='reviewed' for language in ('en','hi')):codes.append('UNREVIEWED_TRANSLATIONS')
    if not runtime['execution_approval_present']:codes.append('EXECUTION_APPROVAL_MISSING')
    if not runtime['guidance_approval_present']:codes.append('GUIDANCE_ATTESTATIONS_MISSING')
    # Execution approval is a separate gate, not a prerequisite imposed by SQL publication.
    publication_codes=[c for c in codes if c not in ('EXECUTION_APPROVAL_MISSING','GUIDANCE_ATTESTATIONS_MISSING')]
    ready=not publication_codes and not blockers
    return {'scheme_id':scheme['stable_id'],'version_number':version['version_number'],
        'version_id':version['id'],'version_identity_scope':'provisional_local_draft',
        'lifecycle_status':scheme.get('lifecycle_status'),'publication_status':version['status'],
        'live_verified':False,'input_payload_sha256':digest(encode(payload)),
        'source_bundle_validation':'passed_offline',
        'policy_review':{'human_approval':payload['verification'].get('human_approval',False),
            'publication_attestation':payload['verification'].get('publication_ready',False),
            'version_review_date_present':bool(version.get('reviewed_at')),
            'version_reviewer_reference_present':bool(version.get('reviewer_reference')),
            'last_checked_date':version.get('last_checked_date'),
            'translations':translations,'unresolved_claims':unchecked_claims,
            'preserved_conflict_ids':[c['conflict_id'] for c in payload['unresolved_archive_conflicts']],
            'uncertain_rule_nodes':sum(r['confidence']!='VERIFIED' for r in rows.get('eligibility_rules',[])),
            'disabled_rule_nodes':sum(r.get('enabled') is False for r in payload['rule_review'])},
        'missing_predicate_evidence':missing_evidence,
        'database_transition_probe':gate,'runtime':runtime,
        'blocker_codes':sorted(codes),'publication_blockers':blockers,
        'ready_for_publication':ready,'readiness_scope':'local_evidence_only_not_authorization',
        'guidance_item_counts':{k:len(rows.get(t,[])) for k,t in [('benefits','benefits'),('documents','required_documents'),('application_routes','application_routes')]}}


def markdown(report):
    text=['# Local publication-readiness preview','','Scope: local drafts and isolated SQL guard probes. **Not live-verified.**',
        'No original scheme record was approved, published or modified. No reviewer identities or artifact paths are included.','',
        '| Scheme | Version | Lifecycle | Publication | Ready | SQL guard |',
        '| --- | --- | --- | --- | --- | --- |']
    for record in report['schemes']:
        text.append(f"| {record['scheme_id']} | {record['version_number']} | {record['lifecycle_status']} | {record['publication_status']} | {record['ready_for_publication']} | {record['database_transition_probe']['guard_passed']} |")
    for record in report['schemes']:
        text+=['','## '+record['scheme_id'],'',f"Draft payload SHA-256: `{record['input_payload_sha256']}`.",
            'Executable policy/guidance hashes: unavailable until actual published projections exist.',
            f"SQL guard result: {record['database_transition_probe']['blocker'] or 'No error from isolated probe'}.",
            '','Blocking gates: '+', '.join(record['blocker_codes']), '']
        text+=['- '+b for b in record['publication_blockers']]
        text+=['','Unresolved/unverified claims: '+', '.join(c['claim_id'] for c in record['policy_review']['unresolved_claims'])+'.',
            'Preserved conflict IDs (not automatically resolved): '+', '.join(record['policy_review']['preserved_conflict_ids'])+'.']
    return '\n'.join(text)+'\n'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-review',action='store_true',required=True)
    parser.add_argument('--collection',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--as-of',type=date.fromisoformat,default=date.today())
    args=parser.parse_args(argv)
    try:
        base=(ENGINE/'.phase3-output').resolve();target=args.output.resolve()
        if not target.is_relative_to(base) or target==base or target.exists():
            raise InputError('Use a fresh ignored local review output directory')
        for path in (args.output.absolute(),*args.output.absolute().parents):
            if path.is_symlink() or path.exists() and path.is_junction():raise InputError('Output links forbidden')
        bundles=validate_collection(args.collection)
        manifest=load_approvals()
        result=subprocess.run(['node',str(ENGINE/'db-validation/reviewer-preview.mjs'),str(args.collection.resolve()),'--local-review'],
            cwd=ENGINE,capture_output=True,encoding='utf-8',check=True,timeout=120)
        probes=parse_json(result.stdout.encode('utf-8'))
        if probes.get('live_database_access') is not False or probes.get('original_versions_unchanged') is not True:
            raise InputError('Local guard rehearsal did not validate')
        records=[]
        for bundle in bundles:
            payload=bundle['payload'];scheme_id=payload['rows']['schemes'][0]['stable_id']
            gate=next(g for g in probes['versions'] if g['scheme_id']==scheme_id)
            records.append(review_record(payload,gate,manifest,as_of=args.as_of))
        report={'schema_version':'1.0','as_of':args.as_of.isoformat(),'scope':'local_draft_review',
            'live_verified':False,'live_database_access':False,'public_api_added':False,'schemes':records}
        target.mkdir(parents=True,exist_ok=False)
        (target/'readiness.json').write_bytes(encode(report))
        (target/'readiness.md').write_text(markdown(report),encoding='utf-8')
        print(f'Local reviewer preview completed: {len(records)} records; {sum(r["ready_for_publication"] for r in records)} ready. Not live-verified.')
        return 0
    except (InputError,OSError,ValueError,KeyError,StopIteration,APIError,subprocess.SubprocessError) as error:
        print('Local reviewer preview rejected: '+type(error).__name__,file=sys.stderr)
        return 1


if __name__=='__main__':raise SystemExit(main())
