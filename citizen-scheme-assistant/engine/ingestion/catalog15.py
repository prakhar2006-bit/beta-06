"""Bounded public PIB captures and offline expansion of the existing validated catalogue."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import sys
import time
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL, uuid5

from ingestion.batch import validate_collection
from ingestion.prepare import InputError, digest, encode, parse_json
from ingestion.verification import prepare_verified

POLICY = 'https://www.pib.gov.in/content/132_2_Copyright-Policy.aspx?lang=1&reg=1'
ROOT = Path(__file__).resolve().parents[1]


def uid(key): return str(uuid5(NAMESPACE_URL, 'catalog15-draft:' + key))


def read_research(path):
    data=parse_json(path.read_bytes())
    ids=[];keys=[]
    for item in data['schemes']:
        parsed=urlsplit(item['source']['url'])
        if (not re.fullmatch(r'in-cen-[0-9]{6}',item['stable_id'])
                or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',item['key'])
                or parsed.scheme!='https' or parsed.username or parsed.password
                or parsed.hostname not in {'www.pib.gov.in','static.pib.gov.in'}):
            raise InputError('Unsafe or unsupported research identifier/source')
        ids.append(item['stable_id']);keys.append(item['key'])
    if len(set(ids))!=len(ids) or len(set(keys))!=len(keys):raise InputError('Duplicate research identifiers')
    return data


def capture(research_path, output):
    """Opt-in serial requests to already inspected reusable PIB publications only."""
    import httpx
    research = read_research(research_path); output.mkdir(parents=True, exist_ok=True)
    for item in research['schemes']:
        source = item['source']; folder = output/item['key']; metadata = folder/'capture.json'
        if metadata.exists():
            existing=parse_json(metadata.read_bytes())
            if existing['url'] != source['url'] or digest((folder/'source.bin').read_bytes()) != existing['sha256']:
                raise InputError('Cached source drift; nothing overwritten')
            continue
        if folder.exists() and any(folder.iterdir()):raise InputError('Incomplete capture needs separate review')
        folder.mkdir(exist_ok=True)
        url=source['url']
        with httpx.Client(timeout=20, follow_redirects=False, trust_env=False,
                          headers={'User-Agent':'YojanaMitra-PolicyResearch/1.0 (bounded public-document review)'}) as client:
            for attempt in range(4):
                if urlsplit(url).scheme!='https' or urlsplit(url).hostname not in {'www.pib.gov.in','static.pib.gov.in'}:
                    raise InputError('Only inspected PIB publications allowed')
                with client.stream('GET',url) as response:
                    if response.is_redirect:
                        url=str(response.url.join(response.headers['location'])); continue
                    response.raise_for_status(); data=bytearray()
                    for chunk in response.iter_bytes():
                        data.extend(chunk)
                        if len(data)>3_000_000:raise InputError('Source size limit')
                    body=bytes(data)
                    if len(body)<1000 or b'captcha' in body.lower() or b'access denied' in body.lower():
                        raise InputError('Restricted/empty source; stop without bypass')
                    (folder/'source.bin').write_bytes(body)
                    metadata.write_bytes(encode(dict(url=source['url'],resolved_url=url,
                        sha256=digest(body),fetched_at=datetime.now(timezone.utc).isoformat(),
                        media_type=response.headers.get('content-type','application/octet-stream').split(';')[0],
                        reuse_status='attribution_permitted',reuse_policy_url=POLICY)))
                    break
            else:raise InputError('Redirect limit')
        print('Captured '+item['key']);time.sleep(1)


def build_one(item, checked, capture_dir, output):
    sid=item['stable_id']; source=item['source']; cap=parse_json((capture_dir/'capture.json').read_bytes())
    data=(capture_dir/'source.bin').read_bytes()
    if cap['url']!=source['url'] or digest(data)!=cap['sha256']:
        raise InputError('Source capture attribution mismatch')
    org=item['organization']; orgid=uid('org:'+org['code']); pibid=uid('org:pib')
    sourceid=uid(source['url']); snapid=uid(source['url']+':'+cap['sha256']); evid=uid(snapid+':summary')
    schemeid=uid(sid); versionid=uid(sid+':v1'); countryid=uid('country:IN')
    mapped_application=item['key'] not in {'apy','pmay-g','pm-jay'}
    claims=[]
    for key in ['description','eligibility','benefit','geography','application']:
        status='unverified' if key=='application' and not mapped_application else 'verified_official_guidance'
        claims.append(dict(claim_id=key,assertion=item[key]['en'],status=status,source_ids=['primary'],
                           checked_date=checked,effective_date=None,publication_date=source['published_on'],
                           locator=source['locator'],uncertainty='Summary only; full policy review incomplete.'))
    claims.append(dict(claim_id='complete-documents',assertion='Complete current route-specific document list is not established.',
                       status='unverified',source_ids=['primary'],checked_date=checked,effective_date=None))
    conflicts=[dict(conflict_id=sid+'-C'+str(i+1),field='policy',assertions=[{'text':text}],status='unresolved')
               for i,text in enumerate(item.get('conflicts',[]))]
    source_register=[dict(source_id='primary',url=source['url'],title=source['title'],publisher='Press Information Bureau',
                          publication_date=source['published_on'],retrieved_at=cap['fetched_at'])]
    original=dict(scheme_id=sid.upper(),official_name=item['name']['en'],classification='central',
                  jurisdiction=item['geography']['en'],record_stage='discovered',source_ids=['primary'],
                  discovery_evidence=[dict(source_id='primary',url=source['url'],locator=source['locator'])],
                  benefits=[dict(text=item['benefit']['en'],source_ids=['primary'])],
                  eligibility_conditions=[dict(rule_id='summary',text=item['eligibility']['en'],source_ids=['primary'])],
                  exclusions=[],documents=[dict(text=d['en'],source_ids=['primary']) for d in item['documents']],
                  guidelines=[],translations=[],missing_information=list(item['blockers']),conflicts=conflicts,
                  unresolved_questions=list(item['blockers']),application=item['application'])
    rows=dict(organizations=[dict(id=orgid,**org,government_level='central'),
                             dict(id=pibid,code='pib',name='Press Information Bureau',government_level='central',official_url='https://www.pib.gov.in/')],
              jurisdictions=[dict(id=countryid,code='IN',name='India',kind='country',parent_id=None)],
              official_sources=[dict(id=sourceid,organization_id=pibid,original_url=source['url'],title=source['title'],
                                     source_kind='webpage',access_status='manual_only',license_url=POLICY,
                                     access_policy_url=POLICY,policy_checked_date=checked)],
              source_snapshots=[dict(id=snapid,source_id=sourceid,content_sha256=cap['sha256'],fetched_at=cap['fetched_at'],
                                     resolved_url=cap['resolved_url'],media_type=cap['media_type'])],
              evidence=[dict(id=evid,snapshot_id=snapid,locator=source['locator'],
                             supporting_text='; '.join(c['assertion'] for c in claims if c['status']=='verified_official_guidance'),last_checked_date=checked)],
              schemes=[dict(id=schemeid,stable_id=sid,organization_id=orgid,government_level='central',lifecycle_status='unknown')],
              scheme_versions=[dict(id=versionid,scheme_id=schemeid,version_number=1,status='draft',last_checked_date=checked)],
              scheme_jurisdictions=[dict(id=uid(sid+':country'),scheme_version_id=versionid,jurisdiction_id=countryid)],
              translations=[dict(id=uid(sid+':'+lang),scheme_version_id=versionid,language_code=lang,title=item['name'][lang],
                                 summary=item['description'][lang],eligibility_text=item['eligibility'][lang],
                                 translation_origin='machine',review_status='draft',evidence_id=evid) for lang in ('en','hi')],
              benefits=[dict(id=uid(sid+':benefit'),scheme_version_id=versionid,item_key='summary',benefit_type='conditional_support',
                             description=item['benefit']['en'],evidence_id=evid)],
              required_documents=[dict(id=uid(sid+':doc:'+str(i)),scheme_version_id=versionid,item_key='document_'+str(i),
                                       document_type=d['en'],requirement='conditional',
                                       condition_text='Only for the route/stage described in the source; confirm current alternatives with the authority.',evidence_id=evid)
                                  for i,d in enumerate(item['documents'])],
              application_routes=[],eligibility_rules=[],rule_evidence=[])
    if mapped_application:
        rows['application_routes']=[dict(id=uid(sid+':application'),scheme_version_id=versionid,item_key='source_route',
                                        mode=item['application']['mode'],original_url=item['application']['url'],
                                        instructions=item['application']['en'],last_checked_date=checked,evidence_id=evid)]
    reviews=[]; predicate=item['predicate']
    if predicate:
        ruleid=uid(sid+':predicate')
        rows['eligibility_rules']=[dict(id=ruleid,scheme_version_id=versionid,rule_key='necessary_condition_proposal',parent_id=None,
                                        node_type='predicate',attribute=predicate['attribute'],operator=predicate['operator'],
                                        expected_value=predicate['value'],confidence='UNCERTAIN',
                                        uncertainty_reason='Source-backed proposal only; complete policy and human approval missing.')]
        rows['rule_evidence']=[dict(id=uid(sid+':rule-evidence'),scheme_version_id=versionid,rule_id=ruleid,evidence_id=evid)]
        reviews=[dict(rule_key='necessary_condition_proposal',enabled=False,claim_ids=['eligibility'])]
    blocks=item['blockers']+['Complete policy, source applicability, English and Hindi review, publication and execution approval are missing.',
                             'Bilingual child content remains in the sidecar; not all child fields have normalized language columns.']
    ledger=dict(external_scheme_id=original['scheme_id'],input_record_sha256=digest(encode(original)),
                sources=[dict(source_id='primary',url=source['url'],title=source['title'],publication_date=source['published_on'],
                              effective_date=None,checked_date=checked,reuse_status='attribution_permitted',reuse_policy_url=POLICY,
                              snapshot=dict(artifact_path='source.bin',content_sha256=cap['sha256'],fetched_at=cap['fetched_at']))],
                claims=claims,rows=rows,rule_review=reviews,
                bilingual_content=dict(translation_status='machine_draft_requires_independent_review',name=item['name'],
                    description=item['description'],eligibility=item['eligibility'],benefits=item['benefit'],
                    documents=item['documents'],application=item['application'],geography=item['geography'],
                    question=predicate['question'] if predicate else None,is_official_translation=False),
                blockers=blocks,additional_source_observations=item.get('additional_sources',[]))
    work=output/'research'/sid;work.mkdir(parents=True,exist_ok=False)
    (work/'source.bin').write_bytes(data)
    (work/'manifest.json').write_bytes(encode(dict(records=[dict(original_record=original)],source_register=source_register)))
    (work/'ledger.json').write_bytes(encode(ledger))
    return prepare_verified(work/'manifest.json',work/'ledger.json',output/'schemes'/sid)/'draft.json'


def expand(existing, research_path, captures, output):
    old=validate_collection(existing); research=read_research(research_path)
    ids=[b['payload']['rows']['schemes'][0]['stable_id'] for b in old]
    newids=[s['stable_id'] for s in research['schemes']]
    if len(ids)!=5 or len(newids)!=10 or len(set(ids+newids))!=15:raise InputError('Expected 5+10 unique scheme IDs')
    if output.exists():raise InputError('Fresh output directory required; never overwrite bundles')
    output.mkdir(parents=True); entries=[]
    for entry in parse_json(existing.read_bytes())['schemes']:
        path=Path(entry['path']);target=output/path
        target.parent.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree((existing.parent/path).parent,target.parent)
        entries.append(deepcopy(entry))
    for item in research['schemes']:
        draft=build_one(item,research['checked_date'],captures/item['key'],output)
        entries.append(dict(stable_id=item['stable_id'],path=draft.relative_to(output).as_posix(),sha256=digest(draft.read_bytes())))
    collection=output/'collection.json'
    collection.write_bytes(encode(dict(mode='local_draft_collection',publish_allowed=False,schemes=sorted(entries,key=lambda x:x['stable_id']))))
    validate_collection(collection)
    return collection


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--research',type=Path,default=ROOT/'ingestion/catalog15_research.json')
    parser.add_argument('--captures',type=Path,required=True)
    parser.add_argument('--capture-public-pib',action='store_true')
    parser.add_argument('--existing',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    if args.capture_public_pib:capture(args.research,args.captures)
    elif args.existing and args.output:print(expand(args.existing,args.research,args.captures,args.output))
    else:parser.error('Choose explicit --capture-public-pib or offline --existing and --output')


if __name__=='__main__':main()
