"""Explicit read-only target inspection using the existing restricted API connection."""
import argparse
import os
from pathlib import Path
from urllib.parse import unquote, urlsplit

from dotenv import load_dotenv
from app.db.connection import open_connection
from ingestion.prepare import InputError, encode
from ingestion.postgres_import import WRITER


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--read-only',action='store_true',required=True)
    parser.add_argument('--project-ref',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    load_dotenv(Path(__file__).resolve().parents[1]/'.env',override=False)
    url=urlsplit(os.environ.get('DATABASE_URL',''))
    if not ((url.hostname or '')==f'db.{args.project_ref}.supabase.co' or
            (url.hostname or '').endswith('.pooler.supabase.com') and unquote(url.username or '').endswith('.'+args.project_ref)):
        raise InputError('Target project identity mismatch')
    with open_connection() as conn,conn.cursor() as cursor:
        cursor.execute("SELECT current_database() AS database,current_user AS role,current_setting('transaction_read_only') AS read_only")
        identity=cursor.fetchone()
        cursor.execute('SELECT s.stable_id,max(v.version_number) AS published_version FROM scheme_catalog.published_schemes s '
                       'JOIN scheme_catalog.published_versions v ON v.scheme_id=s.id GROUP BY s.stable_id ORDER BY s.stable_id')
        published=cursor.fetchall()
        cursor.execute('SELECT rolname,rolsuper,rolbypassrls,rolcreaterole,rolcreatedb,rolreplication,rolcanlogin FROM pg_roles WHERE rolname=%s',[WRITER])
        writer=cursor.fetchone()
        permissions=[]
        if writer:
            cursor.execute("SELECT c.relname,c.relrowsecurity,has_table_privilege(%s,c.oid,'SELECT') AS can_select,"
                           "has_table_privilege(%s,c.oid,'INSERT') AS can_insert FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                           "WHERE n.nspname='scheme_catalog' AND c.relkind='r' ORDER BY c.relname",[WRITER,WRITER])
            permissions=cursor.fetchall()
        cursor.execute("SELECT p.oid::regprocedure::text AS signature,p.prorettype::regtype::text AS returns,"
                       "p.prokind,p.prosecdef,p.pronargs,p.proacl IS NULL AS uses_default_acl,"
                       "pg_get_userbyid(p.proowner) AS owner,p.proconfig,pg_get_functiondef(p.oid) AS definition,"
                       "encode(sha256(convert_to(p.prosrc,'UTF8')),'hex') AS source_sha256,"
                       "EXISTS(SELECT 1 FROM aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a "
                       "WHERE a.grantee=0 AND a.privilege_type='EXECUTE') AS public_execute,"
                       "(SELECT jsonb_agg(jsonb_build_object('grantee',CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,"
                       "'privilege',a.privilege_type,'grantable',a.is_grantable)) "
                       "FROM aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a) AS effective_acl "
                       "FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace "
                       "WHERE n.nspname='public' AND p.proname='rls_auto_enable'")
        routines=cursor.fetchall()
        cursor.execute("SELECT e.evtname,e.evtevent,e.evtenabled,e.evttags,pg_get_userbyid(e.evtowner) AS owner "
                       "FROM pg_event_trigger e JOIN pg_proc p ON p.oid=e.evtfoid JOIN pg_namespace n ON n.oid=p.pronamespace "
                       "WHERE n.nspname='public' AND p.proname='rls_auto_enable'")
        bindings=cursor.fetchall()
        report=dict(scope='live_read_only_metadata_and_published_views',project_ref=args.project_ref,
                    host=url.hostname,port=url.port or 5432,identity=identity,published=published,
                    writer_role=writer,writer_table_permissions=permissions,
                    unpublished_versions_visible=False,expected_current_versions_verified=False,
                    limitation='scheme_api cannot inspect drafts or full current version maxima; writer preflight still required.',
                    remote_writes=0,routine_metadata=routines,event_trigger_bindings=bindings)
    with args.output.open('xb') as stream:stream.write(encode(report))
    # Definitions are retained privately for review, never echoed (they may contain literals).
    printable=report | {'routine_metadata':[{k:v for k,v in r.items() if k!='definition'} for r in routines]}
    print(encode(printable).decode())


if __name__=='__main__':main()
