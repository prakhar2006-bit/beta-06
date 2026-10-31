"""Offline-first, separately authorized PostgreSQL draft import. Never used by FastAPI."""
import argparse
from copy import deepcopy
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from uuid import UUID, uuid5

from ingestion.batch import validate_collection
from ingestion.prepare import InputError, digest, encode, parse_json

ENGINE = Path(__file__).resolve().parents[1]
VERSION = 'postgres-draft-v1'
WRITER = 'scheme_draft_importer'
ORDER = ('organizations', 'jurisdictions', 'official_sources', 'source_snapshots',
         'evidence', 'schemes', 'scheme_versions', 'scheme_jurisdictions', 'translations',
         'benefits', 'application_routes', 'required_documents', 'eligibility_rules', 'rule_evidence')
NATURAL = {'organizations': ('code',), 'jurisdictions': ('code',),
           'official_sources': ('original_url',), 'source_snapshots': ('source_id', 'content_sha256'),
           'evidence': ('snapshot_id', 'locator'), 'schemes': ('stable_id',)}
REFERENCES = {'organization_id': 'organizations', 'source_id': 'official_sources',
              'snapshot_id': 'source_snapshots', 'scheme_id': 'schemes',
              'scheme_version_id': 'scheme_versions', 'jurisdiction_id': 'jurisdictions',
              'evidence_id': 'evidence', 'rule_id': 'eligibility_rules'}
NAMESPACE = UUID('796b56f7-7d73-45e2-96c3-e7a0f7744421')


class PreflightError(InputError):
    """Static, credential-free diagnostic messages owned by this module."""


def verify_client_tls(connection):
    # pg_stat_ssl behind Supavisor describes a DIFFERENT (pooler -> DB) hop.
    # libpq completed the client -> Supabase handshake with verify-full/our CA.
    if not connection.pgconn.ssl_in_use:
        raise PreflightError('TLS is not active on the client connection; refusing database access')


def fingerprint(value):
    return digest(encode(value))


def target_label(target):
    return f"{target['project_ref']}/{target['host']}:{target['port']}/{target['database']}"


def validate_target(target):
    if (set(target) != {'host', 'port', 'database', 'project_ref'}
            or not re.fullmatch(r'[a-z0-9.-]+', target['host'])
            or not re.fullmatch(r'[a-z0-9]+', target['project_ref'])
            or not re.fullmatch(r'[a-zA-Z0-9_]+', target['database'])
            or type(target['port']) is not int or not 1 <= target['port'] <= 65535):
        raise InputError('Invalid non-secret target identity')
    host = target['host']
    if host != f"db.{target['project_ref']}.supabase.co" and not host.endswith('.pooler.supabase.com'):
        raise InputError('Expected official Supabase direct or pooler host')
    return target


def make_plan(bundles, target, expected=None):
    validate_target(target)
    expected = expected or {}
    entries = []
    for bundle in bundles:
        payload = bundle['payload']; scheme = payload['rows']['schemes'][0]['stable_id']
        n = expected.get(scheme, 0)
        if type(n) is not int or n < 0:
            raise InputError('Expected versions must be nonnegative integers')
        entries.append({'scheme_id': scheme, 'payload_sha256': fingerprint(payload),
                        'expected_current_version': n, 'new_version': n + 1})
    entries.sort(key=lambda e: e['scheme_id'])
    ids = [e['scheme_id'] for e in entries]
    if not ids or len(ids) != len(set(ids)) or set(expected) - set(ids):
        raise InputError('Duplicate, empty or unknown scheme identifier')
    return {'format': VERSION, 'target': target, 'expected_role': WRITER,
            'draft_only': True, 'schemes': entries}


def validate_plan(plan, bundles):
    rebuilt = make_plan(bundles, plan['target'],
                        {e['scheme_id']: e['expected_current_version'] for e in plan['schemes']})
    if plan != rebuilt:
        raise InputError('Plan differs from validated collection; prepare and approve again')


def archive_collection(collection, plan):
    """Preserve original payloads, conflicts and captures; SQL receipt binds this archive."""
    root = ENGINE / '.phase3-output' / 'postgres-import' / fingerprint(plan)
    index = parse_json(collection.read_bytes())
    files = {'collection.json': collection.read_bytes(), 'plan.json': encode(plan)}
    for entry in index['schemes']:
        relative = Path(entry['path']); source = collection.parent / relative
        files[relative.as_posix()] = source.read_bytes()
        payload = parse_json(source.read_bytes())
        for row in payload['rows']['source_snapshots']:
            artifact = Path(row['artifact_path'])
            files[(relative.parent / artifact).as_posix()] = (source.parent / artifact).read_bytes()
    # validate_collection has already checked all source paths/hashes. Never follow output links.
    for name, data in files.items():
        dest = root / name
        for part in (dest, *dest.parents):
            if part.is_symlink() or (part.exists() and part.is_junction()):
                raise InputError('Archive links forbidden')
        if not dest.resolve().is_relative_to(root.resolve()):
            raise InputError('Archive path escape')
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if dest.read_bytes() != data:
                raise InputError('Archive drift; nothing overwritten')
        else:
            with dest.open('xb') as stream:
                stream.write(data)
    validate_plan(plan, validate_collection(root / 'collection.json'))
    return root


def parameter(field, value):
    import json
    return json.dumps(value, ensure_ascii=False) if field == 'expected_value' and value is not None else value


def matching(db, table, row):
    keys = list(row)
    return len(db.query(f"SELECT id FROM scheme_catalog.{table} WHERE " +
                        ' AND '.join(f'{k} IS NOT DISTINCT FROM %s' for k in keys),
                        [parameter(k, row[k]) for k in keys])) == 1


def maximum(db, scheme_id):
    return int(db.query('SELECT coalesce(max(v.version_number),0) AS n FROM scheme_catalog.scheme_versions v '
                        'JOIN scheme_catalog.schemes s ON s.id=v.scheme_id WHERE s.stable_id=%s', [scheme_id])[0]['n'])


def import_transaction(db, bundles, plan, *, commit=False):
    """Parameterized INSERT/SELECT only; called only after separate connection/approval gates.

    Adapter query(sql, params) returns dict rows. Tests run this exact implementation
    against isolated PGlite. Default rollback rehearsal is internal, not CLI dry-run.
    """
    validate_plan(plan, bundles)
    results = []
    db.query('BEGIN ISOLATION LEVEL SERIALIZABLE')
    try:
        db.query("SET LOCAL lock_timeout='5000ms'")
        db.query("SET LOCAL statement_timeout='15000ms'")
        db.query('SET CONSTRAINTS ALL DEFERRED')
        # Stable order and per-scheme advisory locks serialize cooperating importers.
        for entry in plan['schemes']:
            db.query('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))', [entry['scheme_id']])
        for bundle, entry in zip(sorted(bundles, key=lambda b: b['payload']['rows']['schemes'][0]['stable_id']), plan['schemes']):
            payload = bundle['payload']; rows = deepcopy(payload['rows'])
            if any(r['status'] != 'draft' for r in rows['scheme_versions']) or any(r['enabled'] is not False for r in payload['rule_review']):
                raise InputError('Draft-only invariant')
            key = f"{VERSION}:{entry['scheme_id']}:{entry['new_version']}:{entry['payload_sha256']}"
            receipts = db.query('SELECT id,status,importer_version FROM scheme_catalog.ingestion_runs WHERE idempotency_key=%s', [key])
            if len(receipts) > 1 or (receipts and (receipts[0]['status'] != 'succeeded' or receipts[0]['importer_version'] != VERSION + ':' + fingerprint(plan))):
                raise InputError('Receipt conflict or changed approval plan')
            current = maximum(db, entry['scheme_id'])
            if current != (entry['new_version'] if receipts else entry['expected_current_version']):
                raise InputError('Version conflict; inspect target and approve a new plan')
            maps = {t: {r['id']: str(uuid5(NAMESPACE, key + ':' + t + ':' + r['id']))
                        for r in rows.get(t, [])} for t in ORDER}
            written = 0
            for table in ORDER:
                for row in rows.get(table, []):
                    provisional = row['id']; row['id'] = maps[table][provisional]
                    for field, target in REFERENCES.items():
                        if row.get(field) is not None:
                            row[field] = maps[target][row[field]]
                    if row.get('parent_id') is not None:
                        row['parent_id'] = maps[table][row['parent_id']]
                    if table == 'scheme_versions':
                        row['version_number'] = entry['new_version']
                    keys = NATURAL.get(table, ('id',))
                    found = db.query(f'SELECT id FROM scheme_catalog.{table} WHERE ' +
                                     ' AND '.join(f'{k}=%s' for k in keys), [row[k] for k in keys])
                    if found:
                        if len(found) != 1:
                            raise InputError('Duplicate natural identifier')
                        row['id'] = str(found[0]['id']); maps[table][provisional] = row['id']
                        if not matching(db, table, row):
                            raise InputError('Existing content drift/conflict: ' + table)
                        if not receipts and table not in NATURAL:
                            raise InputError('Unexpected existing version child')
                    else:
                        if receipts:
                            raise InputError('Receipt exists but imported row is missing')
                        fields = list(row)
                        if not set(fields) <= set(bundle['columns'][table]) or any(not re.fullmatch(r'[a-z_][a-z_0-9]*', f) for f in fields):
                            raise InputError('Unknown SQL column')
                        db.query(f"INSERT INTO scheme_catalog.{table} ({','.join(fields)}) VALUES ({','.join(['%s'] * len(fields))})",
                                 [parameter(f, row[f]) for f in fields])
                        written += 1
            version_id = rows['scheme_versions'][0]['id']
            metadata = db.query('SELECT status,reviewed_at,reviewer_reference,published_at '
                                'FROM scheme_catalog.scheme_versions WHERE id=%s', [version_id])[0]
            if metadata['status'] != 'draft' or any(metadata[k] is not None for k in ('reviewed_at', 'reviewer_reference', 'published_at')):
                raise InputError('Draft review metadata drift')
            # Detect extra children as well as edits/deletions on idempotent retries.
            for table in ('scheme_jurisdictions', 'translations', 'benefits', 'application_routes', 'required_documents', 'eligibility_rules', 'rule_evidence'):
                count = db.query(f'SELECT count(*) AS n FROM scheme_catalog.{table} WHERE scheme_version_id=%s', [version_id])[0]['n']
                if int(count) != len(rows.get(table, [])):
                    raise InputError('Unexpected version children: ' + table)
            if db.query('SELECT id FROM scheme_catalog.published_versions WHERE id=%s', [version_id]):
                raise InputError('Draft exposed in published view')
            if not receipts:
                db.query('INSERT INTO scheme_catalog.ingestion_runs '
                         '(source_id,idempotency_key,importer_version,status,finished_at,records_read,records_written) '
                         "VALUES (%s,%s,%s,'succeeded',now(),1,%s)",
                         [rows['official_sources'][0]['id'], key, VERSION + ':' + fingerprint(plan), written])
            results.append({'scheme_id': entry['scheme_id'], 'version_id': version_id,
                            'version_number': entry['new_version'], 'status': 'draft',
                            'outcome': 'already_imported' if receipts else 'inserted', 'rows_inserted': written,
                            'publicly_visible': False})
        db.query('SET CONSTRAINTS ALL IMMEDIATE')
        db.query('COMMIT' if commit else 'ROLLBACK')
        return {'committed': commit, 'published': False, 'schemes': results}
    except BaseException:
        db.query('ROLLBACK')
        raise


class PsycopgAdapter:
    def __init__(self, connection):
        self.connection = connection

    def query(self, sql, parameters=()):
        cursor = self.connection.execute(sql, parameters)
        return cursor.fetchall() if cursor.description else []


def connection_config(env, target):
    """Only separate writer environment settings; no .env loading, URLs in arguments or logs."""
    url = env.get('SCHEME_IMPORT_DATABASE_URL', '')
    if not url:
        raise PreflightError('SCHEME_IMPORT_DATABASE_URL is unavailable to this process')
    parsed = urlsplit(url)
    cert = env.get('SCHEME_IMPORT_SSLROOTCERT', '')
    if (parsed.scheme not in ('postgres', 'postgresql') or parsed.query or parsed.fragment
            or not parsed.password or parsed.hostname != target['host']
            or (parsed.port or 5432) != target['port'] or unquote(parsed.path.lstrip('/')) != target['database']
            or not cert or not Path(cert).is_file()):
        raise PreflightError('Writer target settings or CA certificate path are missing or do not match the plan')
    username = unquote(parsed.username or '')
    direct = target['host'] == f"db.{target['project_ref']}.supabase.co"
    if username != (WRITER if direct else WRITER + '.' + target['project_ref']):
        raise PreflightError('Expected dedicated draft writer, never scheme_api or an owner login')
    return url, cert


def check_role(db):
    role = db.query("SELECT current_user AS name, rolinherit, rolsuper OR rolbypassrls OR rolcreaterole OR rolcreatedb OR rolreplication AS unsafe "
                    "FROM pg_roles WHERE rolname=current_user")[0]
    if role['name'] != WRITER or role['unsafe'] or role['rolinherit']:
        raise PreflightError('Unsafe or unexpected writer role')
    if db.query('SELECT 1 FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=current_user)'):
        raise PreflightError('Writer must not be a member of other roles')
    tables = db.query("SELECT c.relname, c.relrowsecurity, pg_has_role(current_user,c.relowner,'USAGE') AS owner, "
                      "has_table_privilege(c.oid,'SELECT') AS can_read, has_table_privilege(c.oid,'INSERT') AS can_insert, "
                      "has_table_privilege(c.oid,'UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') AS can_mutate, "
                      "has_any_column_privilege(c.oid,'REFERENCES') AS column_references, "
                      "has_any_column_privilege(c.oid,'SELECT WITH GRANT OPTION,INSERT WITH GRANT OPTION,UPDATE WITH GRANT OPTION') AS can_grant "
                      "FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                      "WHERE n.nspname='scheme_catalog' AND c.relkind='r'")
    expected = set(ORDER) | {'ingestion_runs'}
    if {t['relname'] for t in tables} != expected or any(
            t['owner'] or not t['relrowsecurity'] or not t['can_read'] or not t['can_insert']
            or t['can_mutate'] or t['column_references'] or t['can_grant'] for t in tables):
        raise PreflightError('Writer needs reviewed SELECT/INSERT grants and RLS policies; no ownership or mutation grants')
    updates = db.query("SELECT c.relname,a.attname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                       "JOIN pg_attribute a ON a.attrelid=c.oid WHERE n.nspname='scheme_catalog' AND c.relkind IN ('r','p','v','m','f') "
                       "AND a.attnum>0 AND NOT a.attisdropped AND has_column_privilege(c.oid,a.attnum,'UPDATE')")
    if {(r['relname'], r['attname']) for r in updates} != {('scheme_versions', 'id')}:
        raise PreflightError('Only scheme_versions UPDATE(id) is needed by the existing row-lock trigger')
    if db.query("SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                "WHERE n.nspname='scheme_catalog' AND c.relkind IN ('v','m','f') AND "
                "(has_table_privilege(c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR "
                "has_any_column_privilege(c.oid,'INSERT,UPDATE,REFERENCES'))"):
        raise PreflightError('Writer must not mutate catalogue views or foreign relations')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collection', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--target-host'); parser.add_argument('--project-ref')
    parser.add_argument('--target-port', type=int, default=5432)
    parser.add_argument('--target-database', default='postgres')
    parser.add_argument('--expected-versions', type=Path)
    parser.add_argument('--check-target', action='store_true')
    parser.add_argument('--commit', action='store_true')
    parser.add_argument('--approve-plan-sha256'); parser.add_argument('--confirm-target')
    args = parser.parse_args(argv)
    try:
        bundles = validate_collection(args.collection)
        if args.prepare:
            if args.commit or args.check_target:
                raise InputError('Preparation cannot connect')
            plan = make_plan(bundles, {'host': args.target_host or '', 'port': args.target_port,
                                     'database': args.target_database, 'project_ref': args.project_ref or ''},
                             parse_json(args.expected_versions.read_bytes()) if args.expected_versions else None)
            with args.plan.open('xb') as stream:
                stream.write(encode(plan))
        else:
            plan = parse_json(args.plan.read_bytes())
        validate_plan(plan, bundles)
        sha = fingerprint(plan)
        if args.commit and (args.check_target or args.approve_plan_sha256 != sha or args.confirm_target != target_label(plan['target'])):
            raise InputError('Commit requires approved exact plan SHA-256 and target confirmation')
        archive = archive_collection(args.collection, plan)
        if not args.commit and not args.check_target:
            print(encode({'mode': 'offline_dry_run', 'database_connected': False, 'plan_sha256': sha,
                          'confirm_target': target_label(plan['target']), 'schemes': plan['schemes'],
                          'archive': str(archive.relative_to(ENGINE))}).decode())
            return 0
        url, cert = connection_config(os.environ, plan['target'])
        import psycopg
        from psycopg.rows import dict_row
        with psycopg.connect(url, autocommit=True, sslmode='verify-full', sslrootcert=cert,
                              connect_timeout=10, prepare_threshold=None, row_factory=dict_row,
                              options='-c statement_timeout=15000 -c lock_timeout=5000') as conn:
            verify_client_tls(conn)
            db = PsycopgAdapter(conn)
            # Check-only is genuinely read-only; remote rollback-write rehearsals are not exposed.
            db.query('BEGIN READ ONLY')
            try:
                check_role(db)
                versions = {e['scheme_id']: maximum(db, e['scheme_id']) for e in plan['schemes']}
            finally:
                db.query('ROLLBACK')
            if args.check_target:
                print(encode({'mode': 'read_only_target_check', 'current_versions': versions,
                              'plan_sha256': sha}).decode())
            else:
                print(encode(import_transaction(db, bundles, plan, commit=True)).decode())
        return 0
    except Exception as error:
        # psycopg/server exception text can contain connection secrets or source text.
        message = str(error) if isinstance(error, PreflightError) else 'Error class: ' + type(error).__name__
        print('Draft import rejected; no success claimed. ' + message, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
