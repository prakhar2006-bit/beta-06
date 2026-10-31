"""Local-only rehearsal of actual bundles through the PostgreSQL importer core."""
import argparse
from copy import deepcopy
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion.postgres_import import check_role, import_transaction, make_plan, validate_plan, InputError
from ingestion.batch import validate_collection
from ingestion.prepare import encode, parse_json
from test_postgres_import import LocalDB


def main():
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collection',type=Path,required=True)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--with-reviewed-supabase-hook',action='store_true')
    args=parser.parse_args()
    bundles=validate_collection(args.collection);plan=parse_json(args.plan.read_bytes());validate_plan(plan,bundles)
    with patch('psycopg.connect',side_effect=AssertionError('No network allowed')):
        db=LocalDB(supabase_hook=args.with_reviewed_supabase_hook)
        try:
            check_role(db)
            initial=import_transaction(db,bundles,plan)
            assert db.query('SELECT count(*) AS n FROM scheme_catalog.schemes')[0]['n']==0
            damaged=deepcopy(bundles)
            damaged[-1]['payload']['rows']['translations'][0]['language_code']='invalid'
            try:import_transaction(db,damaged,make_plan(damaged,plan['target']),commit=True)
            except InputError:pass
            else:raise AssertionError('Constraint failure expected')
            assert db.query('SELECT count(*) AS n FROM scheme_catalog.schemes')[0]['n']==0
            first=import_transaction(db,bundles,plan,commit=True)
            repeat=import_transaction(db,bundles,plan,commit=True)
            assert all(r['rows_inserted']==0 for r in repeat['schemes'])
            assert db.query('SELECT count(*) AS n FROM scheme_catalog.published_versions')[0]['n']==0
            assert all(r['enabled'] is False for b in bundles for r in b['payload']['rule_review'])
            report={'scope':'isolated_PGlite_not_Supabase','live_database_access':False,
                    'reviewed_supabase_hook_installed_locally':args.with_reviewed_supabase_hook,
                    'dry_run_rollback':True,'late_failure_rollback':True,'duplicates_on_repeat':0,
                    'all_rules_disabled_in_sidecar':True,'first':first,'repeat':repeat,
                    'pmjjby_draft_retrieval':db.query("SELECT s.stable_id,v.version_number,v.status,t.language_code,t.title "
                        "FROM scheme_catalog.schemes s JOIN scheme_catalog.scheme_versions v ON v.scheme_id=s.id "
                        "JOIN scheme_catalog.translations t ON t.scheme_version_id=v.id "
                        "WHERE s.stable_id='in-cen-000001' ORDER BY t.language_code"),
                    'counts':{t:int(db.query(f'SELECT count(*) AS n FROM scheme_catalog.{t}')[0]['n'])
                              for t in ['schemes','scheme_versions','published_versions','ingestion_runs','evidence']}}
            with args.output.open('xb') as stream:stream.write(encode(report))
            print(encode(report).decode())
        finally:db.close()


if __name__=='__main__':main()
