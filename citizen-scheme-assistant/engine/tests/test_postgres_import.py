"""Exact remote importer SQL exercised locally; never connects to Supabase."""
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ingestion.postgres_import import (ENGINE, InputError, VERSION, WRITER, check_role,
    archive_collection, connection_config, fingerprint, import_transaction, main, make_plan, validate_plan)
from ingestion.batch import validate_collection
from ingestion.prepare import digest, encode
from ingestion.verification import prepare_verified
from test_verification import fixture

TARGET = dict(host='db.testproject.supabase.co', port=5432, database='postgres', project_ref='testproject')


class LocalDB:
    def __init__(self, *, supabase_hook=False):
        self.process = subprocess.Popen(['node', str(ENGINE/'db-validation/postgres-import-bridge.mjs'),
                                        *(['--reviewed-supabase-hook'] if supabase_hook else [])],
                                        cwd=ENGINE, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True, encoding='utf-8')
        if json.loads(self.process.stdout.readline()) != {'ready': True}:
            raise RuntimeError('Local bridge not ready')

    def query(self, sql, parameters=()):
        self.process.stdin.write(json.dumps(dict(sql=sql, parameters=parameters))+'\n'); self.process.stdin.flush()
        response = json.loads(self.process.stdout.readline())
        if 'error' in response:
            raise InputError(response['error'])
        return response['rows']

    def close(self):
        self.process.stdin.close(); self.process.wait(timeout=30)
        self.process.stdout.close(); self.process.stderr.close()


class PostgresImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); root=Path(cls.temp.name); entries=[]
        for i in range(5):
            folder=root/str(i); folder.mkdir(); manifest,ledger,data=fixture()
            manifest['records'][0]['original_record']['scheme_id']='IN-CEN-99000'+str(i)
            manifest['records'][0]['original_record']['conflicts']=[{'assertions':['Synthetic A','Synthetic B']}]
            ledger['external_scheme_id']='IN-CEN-99000'+str(i)
            ledger['input_record_sha256']=digest(encode(manifest['records'][0]['original_record']))
            ledger['rows']['schemes'][0]['stable_id']='synthetic-import-'+str(i)
            (folder/'source.txt').write_bytes(data)
            (folder/'manifest.json').write_bytes(encode(manifest)); (folder/'ledger.json').write_bytes(encode(ledger))
            draft=prepare_verified(folder/'manifest.json',folder/'ledger.json',folder/'out')/'draft.json'
            entries.append(dict(stable_id='synthetic-import-'+str(i),path=draft.relative_to(root).as_posix(),sha256=digest(draft.read_bytes())))
        cls.collection=root/'collection.json'
        cls.collection.write_bytes(encode(dict(mode='local_draft_collection',publish_allowed=False,schemes=entries)))
        cls.bundles=validate_collection(cls.collection); cls.plan=make_plan(cls.bundles,TARGET)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def local(self):
        db=LocalDB(); self.addCleanup(db.close); return db

    def count(self,db,table): return int(db.query(f'SELECT count(*) AS n FROM scheme_catalog.{table}')[0]['n'])

    def test_offline_dry_run_does_not_connect_or_use_api_credentials(self):
        with patch('psycopg.connect',side_effect=AssertionError('network forbidden')), patch('ingestion.postgres_import.archive_collection'), redirect_stdout(io.StringIO()) as output:
            plan_path=Path(self.temp.name)/'plan.json'
            self.assertEqual(main(['--collection',str(self.collection),'--plan',str(plan_path),'--prepare',
                                   '--target-host',TARGET['host'],'--project-ref',TARGET['project_ref']]),0)
        self.assertFalse(json.loads(output.getvalue())['database_connected'])

    def test_commit_requires_exact_approval_before_connecting(self):
        path=Path(self.temp.name)/'approval-plan.json';path.write_bytes(encode(self.plan))
        for extra in [[],['--approve-plan-sha256','0'*64],['--approve-plan-sha256',fingerprint(self.plan),'--confirm-target','wrong']]:
            with patch('psycopg.connect',side_effect=AssertionError('network forbidden')), redirect_stderr(io.StringIO()):
                self.assertEqual(main(['--collection',str(self.collection),'--plan',str(path),'--commit',*extra]),1)

    def test_exact_sql_five_drafts_repeat_and_public_exclusion(self):
        db=self.local();check_role(db)
        result=import_transaction(db,self.bundles,self.plan,commit=True)
        self.assertTrue(result['committed']);self.assertEqual(self.count(db,'schemes'),5)
        self.assertEqual(self.count(db,'published_versions'),0)
        self.assertTrue(all(r['status']=='draft' for r in result['schemes']))
        repeat=import_transaction(db,self.bundles,self.plan,commit=True)
        self.assertTrue(all(r['rows_inserted']==0 and r['outcome']=='already_imported' for r in repeat['schemes']))
        self.assertEqual(self.count(db,'ingestion_runs'),5)
        self.assertTrue(all(b['payload']['rule_review'][0]['enabled'] is False for b in self.bundles))

    def test_internal_rehearsal_rolls_back_every_table(self):
        db=self.local();result=import_transaction(db,self.bundles,self.plan)
        self.assertFalse(result['committed']);self.assertEqual(self.count(db,'schemes'),0)
        self.assertEqual(self.count(db,'ingestion_runs'),0)

    def test_late_constraint_failure_rolls_back_whole_batch(self):
        db=self.local();bundles=deepcopy(self.bundles)
        # Force a genuinely late failure, after preceding schemes and receipts.
        bundles[-1]['payload']['rows']['eligibility_rules'][0]['confidence']='invalid'
        with self.assertRaises(InputError): import_transaction(db,bundles,make_plan(bundles,TARGET),commit=True)
        self.assertEqual(self.count(db,'schemes'),0);self.assertEqual(self.count(db,'ingestion_runs'),0)

    def test_stale_expected_version_rolls_back(self):
        db=self.local();expected={self.plan['schemes'][-1]['scheme_id']:1}
        with self.assertRaisesRegex(InputError,'Version conflict'):
            import_transaction(db,self.bundles,make_plan(self.bundles,TARGET,expected),commit=True)
        self.assertEqual(self.count(db,'schemes'),0)

    def test_conflicting_natural_key_never_overwrites(self):
        db=self.local();import_transaction(db,self.bundles[:1],make_plan(self.bundles[:1],TARGET),commit=True)
        changed=deepcopy(self.bundles[1:2]); changed[0]['payload']['rows']['organizations'][0]['name']='Conflicting synthetic owner'
        with self.assertRaisesRegex(InputError,'conflict'):
            import_transaction(db,changed,make_plan(changed,TARGET),commit=True)
        self.assertEqual(self.count(db,'schemes'),1)

    def test_plan_tampering_duplicate_ids_and_published_input_rejected(self):
        with self.assertRaises(InputError): make_plan(self.bundles*2,TARGET)
        plan=deepcopy(self.plan);plan['schemes'][0]['payload_sha256']='0'*64
        with self.assertRaises(InputError): validate_plan(plan,self.bundles)
        db=self.local();bundles=deepcopy(self.bundles);bundles[0]['payload']['rows']['scheme_versions'][0]['status']='published'
        with self.assertRaisesRegex(InputError,'Draft-only'): import_transaction(db,bundles,make_plan(bundles,TARGET),commit=True)
        self.assertEqual(self.count(db,'schemes'),0)

    def test_connection_settings_reject_reader_wrong_project_query_and_missing_cert(self):
        cert=Path(self.temp.name)/'ca.crt';cert.write_text('test-only-not-a-real-certificate')
        url='postgresql://scheme_draft_importer:secret@db.testproject.supabase.co:5432/postgres'
        good={'SCHEME_IMPORT_DATABASE_URL':url,'SCHEME_IMPORT_SSLROOTCERT':str(cert)}
        self.assertEqual(connection_config(good,TARGET)[0],url)
        for value in [url.replace(WRITER,'scheme_api'),url.replace('testproject','wrong'),url+'?sslmode=disable']:
            with self.assertRaises(InputError): connection_config({**good,'SCHEME_IMPORT_DATABASE_URL':value},TARGET)
        with self.assertRaises(InputError): connection_config({'DATABASE_URL':url},TARGET)

    def test_preflight_checks_actual_client_tls_and_preserves_verify_full(self):
        path=Path(self.temp.name)/'tls-plan.json';path.write_bytes(encode(self.plan))
        for encrypted in (True,False):
            with self.subTest(encrypted=encrypted):
                conn=MagicMock();conn.pgconn.ssl_in_use=encrypted
                conn.execute.return_value.description=None
                connect=MagicMock();connect.return_value.__enter__.return_value=conn
                with (patch('ingestion.postgres_import.connection_config',return_value=('sensitive-test-DSN','test-CA')),
                     patch('ingestion.postgres_import.archive_collection'),patch('psycopg.connect',connect),
                     patch('ingestion.postgres_import.check_role') as role,patch('ingestion.postgres_import.maximum',return_value=0),
                     redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()) as errors):
                    code=main(['--collection',str(self.collection),'--plan',str(path),'--check-target'])
                self.assertEqual(code,0 if encrypted else 1)
                self.assertEqual(connect.call_args.kwargs['sslmode'],'verify-full')
                self.assertEqual(connect.call_args.kwargs['sslrootcert'],'test-CA')
                self.assertFalse(any('pg_stat_ssl' in str(c) for c in conn.execute.call_args_list))
                self.assertNotIn('sensitive-test-DSN',errors.getvalue())
                if encrypted:role.assert_called_once()
                else:self.assertIn('TLS is not active',errors.getvalue());role.assert_not_called()

    def test_missing_writer_diagnostic_is_actionable_without_printing_secrets(self):
        path=Path(self.temp.name)/'diagnostic-plan.json';path.write_bytes(encode(self.plan))
        with (patch.dict('os.environ',{},clear=True),patch('ingestion.postgres_import.archive_collection'),
             patch('psycopg.connect') as connect,redirect_stderr(io.StringIO()) as error):
            self.assertEqual(main(['--collection',str(self.collection),'--plan',str(path),'--check-target']),1)
        self.assertIn('SCHEME_IMPORT_DATABASE_URL is unavailable',error.getvalue());connect.assert_not_called()

    def test_writer_preflight_rejects_reader_and_owner(self):
        db=self.local();check_role(db)
        db.query('RESET ROLE')
        with self.assertRaises(InputError):check_role(db)

    def test_writer_preflight_distinguishes_column_grants_and_role_escalation(self):
        mutations=[
            'GRANT UPDATE(status) ON scheme_catalog.scheme_versions TO scheme_draft_importer',
            'GRANT UPDATE ON scheme_catalog.scheme_versions TO scheme_draft_importer',
            'GRANT REFERENCES(id) ON scheme_catalog.schemes TO scheme_draft_importer',
            'GRANT INSERT(id) ON scheme_catalog.published_versions TO scheme_draft_importer',
            'GRANT SELECT(id) ON scheme_catalog.schemes TO scheme_draft_importer WITH GRANT OPTION',
            'CREATE ROLE synthetic_extra NOLOGIN; GRANT synthetic_extra TO scheme_draft_importer',
            'ALTER ROLE scheme_draft_importer INHERIT',
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                db=self.local();check_role(db);db.query('RESET ROLE')
                # Bridge uses one SQL statement per message.
                for statement in mutation.split(';'):
                    if statement.strip():db.query(statement.strip())
                db.query('SET ROLE scheme_draft_importer')
                with self.assertRaises(InputError):check_role(db)

    def test_writer_cannot_approve_publish_delete_or_change_api_role(self):
        db=self.local();import_transaction(db,self.bundles[:1],make_plan(self.bundles[:1],TARGET),commit=True)
        for sql in ["UPDATE scheme_catalog.scheme_versions SET status='reviewed'",
                    'DELETE FROM scheme_catalog.schemes', 'TRUNCATE scheme_catalog.schemes',
                    'ALTER ROLE scheme_catalog_reader LOGIN']:
            with self.assertRaises(InputError): db.query(sql)
        self.assertEqual(self.count(db,'published_versions'),0)

    def test_archive_preserves_conflicts_captures_and_is_repeatable(self):
        with patch('ingestion.postgres_import.ENGINE',Path(self.temp.name)/'archive-engine'):
            archive=archive_collection(self.collection,self.plan)
            self.assertEqual(archive_collection(self.collection,self.plan),archive)
            copies=validate_collection(archive/'collection.json')
            self.assertEqual(copies,self.bundles)

    def test_idempotent_retry_rejects_content_and_review_metadata_drift(self):
        for mutation in ["UPDATE scheme_catalog.eligibility_rules SET uncertainty_reason='changed'",
                         "UPDATE scheme_catalog.scheme_versions SET reviewer_reference='unapproved'"]:
            with self.subTest(mutation=mutation):
                db=self.local();bundles=self.bundles[:1];plan=make_plan(bundles,TARGET)
                import_transaction(db,bundles,plan,commit=True)
                db.query('RESET ROLE');db.query(mutation);db.query('SET ROLE scheme_draft_importer')
                with self.assertRaisesRegex(InputError,'drift'):import_transaction(db,bundles,plan,commit=True)


if __name__=='__main__': unittest.main()
