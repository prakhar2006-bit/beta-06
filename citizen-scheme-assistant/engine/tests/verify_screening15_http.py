"""Real loopback HTTP integration check; synthetic answers remain in memory only."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from screening15_fixtures import ALL_IDS, ORIGINAL_IDS, sample_answers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://127.0.0.1:8001')
    parser.add_argument('--prefix', choices=('/api/v1', '/api/v1/demo'), default='/api/v1')
    parser.add_argument('--output', type=Path, help='Optional summary only; never contains answers/state.')
    args = parser.parse_args()
    target = urlsplit(args.base)
    if (target.scheme != 'http' or target.hostname not in ('127.0.0.1', 'localhost', '::1')
            or target.username or target.password or target.query or target.fragment or target.path not in ('', '/')):
        parser.error('Only an explicit loopback HTTP service is permitted.')
    report = dict(base_url=args.base, prefix=args.prefix, catalogue_count=0, screening_count=0, journeys=[])
    with httpx.Client(base_url=args.base, trust_env=False, timeout=30) as client:
        def request(method, path, body=None, expected=200):
            response = client.request(method, args.prefix + path, **({'json':body} if body is not None else {}))
            assert response.status_code == expected, (path, response.status_code)
            if method == 'POST':
                assert response.headers.get('cache-control') == 'no-store'
            return response

        assert client.get('/health').status_code == 200
        for language in ('en','hi'):
            response = request('GET', '/schemes?limit=100&lang='+language)
            data = response.json()
            assert response.headers.get('x-scheme-catalog') == 'DEMO-UNVERIFIED', 'Explicit local demo mode required.'
            assert data['total'] == len(data['items']) == 15
            assert {s['id'] for s in data['items']} == set(ALL_IDS)
            assert all(s['screening_available'] and s['preliminary_screening_enabled'] for s in data['items'])
            assert all(s['publication_status']=='draft' and s['verification_status']=='UNVERIFIED'
                       and s['published_at'] is None and not s['eligibility_execution_enabled'] for s in data['items'])
        report.update(catalogue_count=15, screening_count=15)

        def journey(sid, language, overrides=None, expected=None):
            q = request('POST','/questionnaire/start',dict(scheme_id=sid,language=language)).json()
            refreshed = request('POST','/questionnaire/next',dict(state=q['state'])).json()
            assert q == refreshed
            answers = sample_answers(sid) | (overrides or {})
            asked = []
            while not q['completed']:
                current = q['current_question']
                key = current['question_id']
                assert key not in asked and len(asked)<15
                assert current['content_language'] == language
                asked.append(key)
                q = request('POST','/questionnaire/answer',dict(state=q['state'],question_id=key,
                                                               action='answer',value=answers[key])).json()
            result = request('POST','/results/explain',dict(state=q['state'])).json()
            assert result == request('POST','/results/explain',dict(state=q['state'])).json()
            expected = expected or ('ELIGIBLE_LIKELY' if sid in ORIGINAL_IDS else 'NEEDS_VERIFICATION')
            assert result['eligibility_status'] == expected
            assert result['screening_scope'] == 'preliminary_only'
            assert result['evaluation']['policy_review']['execution_enabled'] is False
            assert result['assessment_notice']['text'] and result['assessment_notice']['content_language']==language
            refs = {s['reference_id'] for s in result['sources']}
            assert refs
            for section in ('benefits','required_documents','application_guidance'):
                for row in result[section]['items']:
                    assert set(row['source_ids']) <= refs
            if sid not in ORIGINAL_IDS and expected=='NEEDS_VERIFICATION':
                assert 'INCOMPLETE_PRELIMINARY_CRITERIA' in result['missing_information']['review_blockers']
                assert result['missing_information_labels']
            summary = dict(scheme_id=sid,language=language,outcome=result['eligibility_status'],questions=len(asked),
                documents_status=result['required_documents']['status'],documents=len(result['required_documents']['items']),
                official_urls_status=result['official_application_urls']['status'],sources=len(refs))
            report['journeys'].append(summary)

        for sid in ALL_IDS:
            for language in ('en','hi'):
                detail = request('GET',f'/schemes/{sid}?lang={language}').json()
                assert detail['screening_available'] and detail['publication_status']=='draft'
                assert detail['language']==language
                journey(sid,language)
        for sid,values in [('in-cen-000004',{'age':17}),('in-cen-000005',{'age':59}),
                           ('in-cen-000009',{'has_pucca_roof_or_wall':True}),('in-cen-000011',{'age':17}),
                           ('in-cen-000012',{'is_street_vendor':False}),('in-cen-000014',{'indian_citizen':False})]:
            journey(sid,'en',values,'NOT_ELIGIBLE_LIKELY')
        journey('in-cen-000010','hi',{'age':35},'NEEDS_VERIFICATION')
        q = request('POST','/questionnaire/start',dict(scheme_id='in-cen-000004')).json()
        request('POST','/results/explain',dict(state=q['state']),expected=409)
        bad = request('POST','/questionnaire/answer',dict(state=q['state'],question_id='age',value='private-sentinel'),expected=422)
        assert 'private-sentinel' not in bad.text
        q['state']['policy_fingerprint']='0'*64
        request('POST','/questionnaire/next',dict(state=q['state']),expected=409)
        request('POST','/results/explain',dict(state=q['state'],eligibility_status='ELIGIBLE'),expected=422)
    report.update(passed=True, complete_bilingual_journeys=30, additional_decision_cases=7)
    if args.output:
        args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='journeys'}))


if __name__=='__main__':
    main()
