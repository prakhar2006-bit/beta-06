"""Offline expansion safety and deterministic mapping, with synthetic captures only."""
from copy import deepcopy
from pathlib import Path
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion.catalog15 import ROOT,expand,read_research,capture
from ingestion.batch import validate_collection
from ingestion.prepare import InputError,encode,digest
import test_postgres_import as postgres_fixtures


class Catalog15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        postgres_fixtures.PostgresImportTests.setUpClass()
        cls.original=postgres_fixtures.PostgresImportTests.collection
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        cls.research=ROOT/'ingestion/catalog15_research.json';data=read_research(cls.research)
        for item in data['schemes']:
            folder=cls.root/'captures'/item['key'];folder.mkdir(parents=True)
            body=b'Synthetic structural-test capture only, not government evidence.'
            (folder/'source.bin').write_bytes(body)
            (folder/'capture.json').write_bytes(encode(dict(url=item['source']['url'],resolved_url=item['source']['url'],
                sha256=digest(body),fetched_at='2026-10-31T00:00:00+00:00',media_type='text/plain')))

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup();postgres_fixtures.PostgresImportTests.tearDownClass()

    def test_offline_expansion_is_reproducible_preserves_five_and_never_enables(self):
        with patch('httpx.Client',side_effect=AssertionError('No network')):
            a=expand(self.original,self.research,self.root/'captures',self.root/'a')
            b=expand(self.original,self.research,self.root/'captures',self.root/'b')
        first=validate_collection(a);second=validate_collection(b)
        self.assertEqual(first,second);self.assertEqual(len(first),15)
        old={x['payload']['rows']['schemes'][0]['stable_id']:x for x in validate_collection(self.original)}
        for item in first:
            payload=item['payload'];sid=payload['rows']['schemes'][0]['stable_id']
            if sid in old:self.assertEqual(item,old[sid])
            self.assertFalse(payload['publish_allowed']);self.assertFalse(payload['eligible_for_execution'])
            self.assertTrue(all(r['enabled'] is False for r in payload['rule_review']))
            self.assertTrue(all(r['status']=='draft' for r in payload['rows']['scheme_versions']))
        new=[x['payload'] for x in first if x['payload']['rows']['schemes'][0]['stable_id'] not in old]
        for item in new:
            self.assertEqual({t['language_code'] for t in item['rows']['translations']},{'en','hi'})
            self.assertTrue(all(t['review_status']=='draft' for t in item['rows']['translations']))
        for sid in ['in-cen-000010','in-cen-000013','in-cen-000015']:
            self.assertFalse(next(p for p in new if p['rows']['schemes'][0]['stable_id']==sid)['rows']['eligibility_rules'])

    def test_unsafe_source_path_duplicate_and_capture_drift_rejected(self):
        for mutation in ('path','source','duplicate'):
            data=deepcopy(read_research(self.research))
            if mutation=='path':data['schemes'][0]['key']='../escape'
            elif mutation=='source':data['schemes'][0]['source']['url']='https://www.myscheme.gov.in/'
            else:data['schemes'][1]['stable_id']=data['schemes'][0]['stable_id']
            file=self.root/(mutation+'.json');file.write_bytes(encode(data))
            with patch('httpx.Client',side_effect=AssertionError('No network')),self.assertRaises(InputError):
                capture(file,self.root/'rejected')
        copied=self.root/'damaged-captures';shutil.copytree(self.root/'captures',copied)
        (copied/'pm-kisan/source.bin').write_bytes(b'Corrupted synthetic capture')
        with self.assertRaises(InputError):expand(self.original,self.research,copied,self.root/'damaged-output')

    def test_existing_output_and_identifier_collisions_rejected(self):
        output=self.root/'exists';output.mkdir()
        with self.assertRaises(InputError):expand(self.original,self.research,self.root/'captures',output)
        data=deepcopy(read_research(self.research));data['schemes'][0]['stable_id']=data['schemes'][1]['stable_id']
        path=self.root/'collision.json';path.write_bytes(encode(data))
        with self.assertRaises(InputError):expand(self.original,path,self.root/'captures',self.root/'collision-out')


if __name__=='__main__':unittest.main()
