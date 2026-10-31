"""Explicitly SIMULATED local PMJJBY UI harness; never a real scheme approval.

Run only on loopback with --factory create_app. No production app or manifest is
modified. Three synthetic boolean rules test plumbing, NOT complete PMJJBY policy.
"""
from datetime import date
from pathlib import Path
import sys
from unittest.mock import Mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.schemes import router as schemes_router
from app.api.routes.questionnaire import router as questionnaire_router
from app.api.routes.eligibility import router as eligibility_router
from app.api.routes.results import router as results_router
from app.core.errors import register_errors
from app.db.repository import get_repository
from app.db.policies import PublishedPolicy,snapshot_digest
from app.db.guidance import PublishedGuidance,guidance_digest
from app.eligibility.approvals import ExecutionApproval,ApprovalManifest
from app.eligibility.provider import TrustedPolicyProvider,get_rule_provider
from app.schemas.schemes import SchemeDetail,SchemeList
from test_policy_provider import published,uid
from test_results import guidance_data
from test_api import SUMMARY

ID='pmjjby-workflow-fixture'
LABEL='SIMULATED PMJJBY workflow — NOT government eligibility'
QUESTIONS=[('participating_account','Synthetic fixture: participating account?','परीक्षण: सहभागी खाता है?'),
           ('consent','Synthetic fixture: enrolment consent?','परीक्षण: नामांकन की सहमति है?'),
           ('single_account','Synthetic fixture: one enrolment account?','परीक्षण: एक नामांकन खाता है?')]


def fixture_provider():
    policy,entry=published();data=policy.model_dump(mode='json');a=entry.model_dump(mode='json')
    data['scheme_id']=ID;data['rules']=[];data['rule_evidence']=[];annotations=[];fields=[]
    root=uid(ID+':root');evidence=data['sources'][0]['id']
    data['sources'][0]['source_title']='Synthetic PMJJBY workflow fixture, not an official policy'
    data['sources'][0]['supporting_text']='Synthetic boolean conditions for isolated platform testing only.'
    for key,en,hi in [('root','Synthetic AND group','परीक्षण समूह'),*QUESTIONS]:
        rid=root if key=='root' else uid(ID+':'+key)
        data['rules'].append(dict(id=rid,rule_key=key,parent_id=None if key=='root' else root,
            node_type='and' if key=='root' else 'predicate',attribute=None if key=='root' else key,
            operator=None if key=='root' else 'eq',expected_value=None if key=='root' else True,
            unit=None,time_basis='isolated_synthetic_test',confidence='VERIFIED',uncertainty_reason=None))
        annotations.append(dict(rule_id=rid,label=dict(en=en,hi=hi),enabled=True,applicability_confirmed=True))
        if key!='root':
            fields.append(dict(key=key,kind='boolean',question=dict(en=en,hi=hi),question_reviewed_languages=['en','hi']))
            data['rule_evidence'].append(dict(rule_id=rid,evidence_id=evidence))
    policy=PublishedPolicy.model_validate(data)
    gd=guidance_data();gd['scheme_id']=ID;gd['sources']=data['sources']
    for t in gd['translations']:
        t['title']=LABEL if t['language_code']=='en' else 'सिमुलेटेड पीएमजेजेबीवाई परीक्षण — सरकारी पात्रता निर्णय नहीं'
        t['summary']='SIMULATED local workflow test. No real PMJJBY eligibility is evaluated.'
    gd['benefits'][0]['description']='Synthetic display-only benefit; not a government promise.'
    gd['documents'][0]['document_type']='Synthetic enrolment checklist — test only'
    gd['application_routes'][0]['instructions']='Synthetic test: review the fictional checklist. Do not apply for a real scheme here.'
    guidance=PublishedGuidance.model_validate(gd)
    meta=dict(snapshot_sha256=guidance_digest(guidance),reviewer_reference='synthetic-test-guidance-only',
              reviewed_on='2026-01-04',valid_until='2027-01-01',
              benefits=[dict(item_id=str(r.id),language='en') for r in guidance.benefits],
              documents=[dict(item_id=str(r.id),language='en') for r in guidance.documents],
              application_routes=[dict(item_id=str(r.id),language='en',application_url_verified=False) for r in guidance.application_routes],
              allowed_application_hosts=[])
    a.update(scheme_id=ID,snapshot_sha256=snapshot_digest(policy),nodes=annotations,fields=fields,guidance=meta)
    approval=ExecutionApproval.model_validate(a)
    repository=Mock();repository.get_latest.side_effect=lambda sid:policy if sid==ID else None
    guidance_repository=Mock();guidance_repository.get_for_version.return_value=guidance
    provider=TrustedPolicyProvider(repository,ApprovalManifest(schema_version='1.0',approvals=(approval,)),
                                   as_of=date(2026,10,31),guidance_repository=guidance_repository)
    return provider,guidance


class FixtureRepository:
    def get_scheme(self,scheme_id,lang):
        if scheme_id!=ID:return None
        return SchemeDetail.model_validate(SUMMARY|dict(id=ID,level='central',language=lang,requested_language=lang,
            name=LABEL if lang=='en' else 'सिमुलेटेड पीएमजेजेबीवाई परीक्षण — सरकारी पात्रता निर्णय नहीं',
            description='SIMULATED local UI/API harness. Real PMJJBY remains unpublished and unapproved.',
            eligibility_text=None,translation_evidence_id=None,benefits=[],application_routes=[],required_documents=[],
            eligibility_rules=[],rule_evidence=[],sources=[],jurisdictions=[]))

    def list_schemes(self,lang,search,level,limit,offset):
        items=[self.get_scheme(ID,lang)] if not search or 'pmjjby' in search.lower() else []
        if level and level!='central':items=[]
        return SchemeList(items=items[offset:offset+limit],total=len(items),limit=limit,offset=offset,has_more=False)

    def health(self):return None


def create_app():
    app=FastAPI(title='SIMULATED PMJJBY workflow fixture ONLY')
    app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3011','http://127.0.0.1:3011'],
                       allow_methods=['GET','POST'],allow_headers=['Accept','Content-Type'])
    register_errors(app)
    for router in [schemes_router,questionnaire_router,eligibility_router,results_router]:app.include_router(router)
    provider,_=fixture_provider()
    app.dependency_overrides[get_repository]=lambda:FixtureRepository()
    app.dependency_overrides[get_rule_provider]=lambda:provider
    @app.middleware('http')
    async def local_only(request,call_next):
        from starlette.responses import JSONResponse
        if request.client and request.client.host not in {'127.0.0.1','::1','testclient','test'}:
            return JSONResponse({'error':'Loopback fixture only'},status_code=403)
        response=await call_next(request);response.headers['X-YojanaMitra-Fixture']='synthetic-not-government-policy'
        return response
    @app.get('/health')
    def health():return {'status':'ok','scope':'SIMULATED FIXTURE ONLY'}
    return app
