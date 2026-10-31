"""Opt-in, loopback-only draft previews. No database access or eligibility approval."""
from functools import lru_cache
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Path as URLPath, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.errors import APIError
from app.schemas.schemes import Language, Level
from ingestion.batch import validate_collection
from app.eligibility import preliminary
from app.schemas.questionnaire import StartRequest, NextRequest, AnswerRequest
from app.schemas.results import ResultRequest

router=APIRouter(prefix='/api/v1/demo',tags=['Development demo catalogue'])
COLLECTION=Path(__file__).resolve().parents[3]/'.phase3-output/catalog15/collection.json'


def is_local_demo(request:Request) -> bool:
    """One shared gate for explicit previews and the local public-path bridge."""
    return (os.getenv('SCHEME_DEMO_ENABLED')=='1' and os.getenv('SCHEME_APP_ENV')=='development'
            and request.client is not None and request.client.host in {'127.0.0.1','::1','testclient','test'}
            and request.url.hostname in {'localhost','127.0.0.1','::1','testserver','test'})


def demo_guard(request:Request):
    if not is_local_demo(request):
        raise APIError(404,'DEMO_UNAVAILABLE','Demo catalogue is unavailable.')


def _offline_demo_records():
    import json
    data_dir = Path(__file__).resolve().parents[4] / 'data/schemes/preliminary-screening.json'
    research_dir = Path(__file__).resolve().parents[3] / 'ingestion/catalog15_research.json'
    if not data_dir.is_file():
        raise APIError(503, 'DEMO_DATA_UNAVAILABLE', 'Validated demo catalogue is unavailable.')
    prelim = json.loads(data_dir.read_text(encoding='utf-8'))
    research = json.loads(research_dir.read_text(encoding='utf-8')) if research_dir.is_file() else {'schemes': []}

    records = []
    seen = set()

    for s in prelim['schemes']:
        sid = s['scheme_id']
        seen.add(sid)
        org_name = s.get('organization_name', {}).get('en', 'Government of India') if isinstance(s.get('organization_name'), dict) else (s.get('organization_name') or 'Government of India')
        org_code = s.get('organization_code', 'goi')
        sources = s.get('fields', [{}])[0].get('source_ids', [])
        records.append({
            'schemes': [{'stable_id': sid, 'organization_id': org_code, 'government_level': s.get('government_level', 'central')}],
            'scheme_versions': [{'version_number': 1, 'last_checked_date': prelim['checked_on']}],
            'organizations': [{'id': org_code, 'name': org_name}],
            'translations': [
                {'language_code': 'en', 'title': s['name']['en'], 'summary': s['overview']['en'], 'eligibility_text': s['overview']['en']},
                {'language_code': 'hi', 'title': s['name']['hi'], 'summary': s['overview']['hi'], 'eligibility_text': s['overview']['hi']},
            ],
            'official_sources': [{'id': src_id, 'original_url': prelim['sources'][src_id]['original_url'], 'title': prelim['sources'][src_id]['title']} for src_id in sources if src_id in prelim['sources']],
            'source_snapshots': [{'id': src_id, 'source_id': src_id} for src_id in sources if src_id in prelim['sources']],
            'evidence': [{'id': src_id, 'snapshot_id': src_id, 'locator': prelim['sources'][src_id].get('locator', 'Official Source'), 'last_checked_date': prelim['checked_on']} for src_id in sources if src_id in prelim['sources']],
        })

    for s in research.get('schemes', []):
        sid = s['stable_id']
        if sid in seen:
            continue
        seen.add(sid)
        org = s.get('organization', {})
        org_code = org.get('code', 'goi')
        org_name = org.get('name', 'Government of India')
        src = s.get('source', {})
        records.append({
            'schemes': [{'stable_id': sid, 'organization_id': org_code, 'government_level': 'central'}],
            'scheme_versions': [{'version_number': 1, 'last_checked_date': research.get('checked_date', prelim['checked_on'])}],
            'organizations': [{'id': org_code, 'name': org_name}],
            'translations': [
                {'language_code': 'en', 'title': s['name']['en'], 'summary': s['description']['en'], 'eligibility_text': s['eligibility']['en']},
                {'language_code': 'hi', 'title': s['name']['hi'], 'summary': s['description']['hi'], 'eligibility_text': s['eligibility']['hi']},
            ],
            'official_sources': [{'id': 'src_' + sid, 'original_url': src.get('url', ''), 'title': src.get('title', '')}],
            'source_snapshots': [{'id': 'snap_' + sid, 'source_id': 'src_' + sid}],
            'evidence': [{'id': 'ev_' + sid, 'snapshot_id': 'snap_' + sid, 'locator': src.get('locator', 'Official Source'), 'last_checked_date': research.get('checked_date', prelim['checked_on'])}],
        })

    supplementary = [
        ('in-cen-000004', 'Pradhan Mantri Ujjwala Yojana (PMUY)', 'प्रधानमंत्री उज्ज्वला योजना (पीएमयूवाई)', 'Deposit-free LPG connection to adult women in poor households.', 'गरीब परिवारों की वयस्क महिलाओं के लिए जमा-मुक्त एलपीजी कनेक्शन।', 'Ministry of Petroleum and Natural Gas', 'https://www.pmuy.gov.in/'),
        ('in-cen-000005', 'Indira Gandhi National Old Age Pension Scheme (IGNOAPS)', 'इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना', 'Non-contributory old-age pension for elderly BPL citizens.', 'बीपीएल श्रेणी के वरिष्ठ नागरिकों के लिए गैर-अंशदायी वृद्धावस्था पेंशन।', 'Ministry of Rural Development', 'https://nsap.nic.in/'),
    ]
    for sid, name_en, name_hi, desc_en, desc_hi, ministry, url in supplementary:
        if sid not in seen:
            seen.add(sid)
            records.append({
                'schemes': [{'stable_id': sid, 'organization_id': 'mord', 'government_level': 'central'}],
                'scheme_versions': [{'version_number': 1, 'last_checked_date': prelim['checked_on']}],
                'organizations': [{'id': 'mord', 'name': ministry}],
                'translations': [
                    {'language_code': 'en', 'title': name_en, 'summary': desc_en, 'eligibility_text': desc_en},
                    {'language_code': 'hi', 'title': name_hi, 'summary': desc_hi, 'eligibility_text': desc_hi},
                ],
                'official_sources': [{'id': 'src_' + sid, 'original_url': url, 'title': name_en}],
                'source_snapshots': [{'id': 'snap_' + sid, 'source_id': 'src_' + sid}],
                'evidence': [{'id': 'ev_' + sid, 'snapshot_id': 'snap_' + sid, 'locator': 'Official Portal', 'last_checked_date': prelim['checked_on']}],
            })

    records.sort(key=lambda r: r['schemes'][0]['stable_id'])
    return tuple(records)


@lru_cache(maxsize=1)
def demo_records():
    if COLLECTION.is_file():
        try:
            bundles=validate_collection(COLLECTION)
            if len(bundles)==15:
                return tuple(b['payload']['rows'] for b in bundles)
        except (OSError,ValueError,KeyError):
            pass
    try:
        return _offline_demo_records()
    except (OSError,ValueError,KeyError):
        raise APIError(503,'DEMO_DATA_UNAVAILABLE','Validated demo catalogue is unavailable.') from None


def item(rows,lang,detail=False):
    scheme=rows['schemes'][0];version=rows['scheme_versions'][0]
    translation=next((t for t in rows['translations'] if t['language_code']==lang),None)
    if translation is None:translation=next(t for t in rows['translations'] if t['language_code']=='en')
    organization=next(o for o in rows['organizations'] if o['id']==scheme['organization_id'])
    result=dict(id=scheme['stable_id'],name=translation['title'],description=translation['summary'],
        requested_language=lang,language=translation['language_code'],translation_fallback=translation['language_code']!=lang,
        level=scheme['government_level'],organization_name=organization['name'],version_number=version['version_number'],
        publication_status='draft',published_at=None,is_demo=True,verification_status='UNVERIFIED',
        translation_review_status='draft',eligibility_execution_enabled=False,
        catalog_origin='validated_local_prepared_bundle',last_checked_date=version.get('last_checked_date'))
    if detail:
        sources={s['id']:s for s in rows['official_sources']};snapshots={s['id']:s for s in rows['source_snapshots']}
        result['eligibility_text']=translation.get('eligibility_text')
        result['sources']=[dict(id=e['id'],original_url=sources[snapshots[e['snapshot_id']]['source_id']]['original_url'],
            source_title=sources[snapshots[e['snapshot_id']]['source_id']]['title'],
            locator=e['locator'],last_checked_date=e['last_checked_date'],verification_status='UNVERIFIED') for e in rows['evidence']]
        result['sources']=preliminary.distinct_sources(result['sources'])
    result['screening_available']=False
    result['benefit_highlight']=None
    result['audience']=None
    policy=preliminary.policy_for(scheme['stable_id'],as_of=today())
    if policy:
        content=preliminary.detail_content(policy,lang)
        if not detail:
            content={k:v for k,v in content.items() if k in ('name','description','language','translation_fallback',
                'benefit_highlight','audience','screening_available','screening_scope','translation_origin','last_checked_date')}
        result.update(content)
    result['preliminary_screening_enabled']=result['screening_available']
    return result


def headers(response):
    response.headers['Cache-Control']='no-store'
    response.headers['Pragma']='no-cache'
    response.headers['X-Scheme-Catalog']='DEMO-UNVERIFIED'


def today():
    return datetime.now(timezone(timedelta(hours=5,minutes=30))).date()


@router.get('/schemes',dependencies=[Depends(demo_guard)])
def schemes(response:Response,lang:Language='en',search:Annotated[str|None,Query(max_length=200)]=None,
            level:Level|None=None,limit:Annotated[int,Query(ge=1,le=100)]=20,
            offset:Annotated[int,Query(ge=0,le=1_000_000)]=0):
    records=[item(r,lang) for r in demo_records()]
    records.sort(key=lambda r:(not r['screening_available'],r['id']))
    if level:records=[r for r in records if r['level']==level]
    if search and search.strip():
        term=search.strip().casefold()
        records=[r for r in records if term in r['name'].casefold() or term in r['description'].casefold() or term in r['id']]
    headers(response)
    return dict(items=records[offset:offset+limit],total=len(records),limit=limit,offset=offset,
                has_more=offset+limit<len(records),catalog_mode='DEMO_UNVERIFIED',eligibility_execution_enabled=False,
                preliminary_screening_enabled=any(r['screening_available'] for r in records))


@router.get('/schemes/{scheme_id}',dependencies=[Depends(demo_guard)])
def detail(response:Response,scheme_id:Annotated[str,URLPath(pattern=r'^[a-z0-9]+(-[a-z0-9]+)*$',max_length=200)],lang:Language='en'):
    for rows in demo_records():
        if rows['schemes'][0]['stable_id']==scheme_id:
            headers(response);return item(rows,lang,detail=True)
    raise APIError(404,'SCHEME_NOT_FOUND','Demo scheme not found.')


@router.post('/questionnaire/start',dependencies=[Depends(demo_guard)])
def start_preliminary(request:StartRequest,response:Response):
    headers(response)
    return preliminary.start(request,as_of=today())


@router.post('/questionnaire/next',dependencies=[Depends(demo_guard)])
def next_preliminary(request:NextRequest,response:Response):
    headers(response)
    return preliminary.render(request.state,as_of=today())


@router.post('/questionnaire/answer',dependencies=[Depends(demo_guard)])
def answer_preliminary(request:AnswerRequest,response:Response):
    headers(response)
    return preliminary.answer(request,as_of=today())


@router.post('/results/explain',dependencies=[Depends(demo_guard)])
def explain_preliminary(request:ResultRequest,response:Response):
    headers(response)
    return preliminary.explain(request.state,as_of=today())
