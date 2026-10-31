"""Opt-in, read-only database smoke check. Never loads .env or prints credentials."""
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit


def connection_settings(environ):
    url = environ.get('DATABASE_URL', '')
    expected = environ.get('DATABASE_EXPECTED_USER', '')
    cert = environ.get('DATABASE_SSL_ROOT_CERT', '')
    parsed = urlsplit(url)
    # No URI query parameters: prohibit overriding TLS/options through the URL.
    if (parsed.scheme not in ('postgres', 'postgresql') or not parsed.hostname
            or not parsed.username or not parsed.password or parsed.query
            or parsed.fragment or not parsed.path.strip('/')
            or 'REPLACE_WITH' in url):
        raise ValueError('Invalid database configuration')
    if expected != 'scheme_api' or not Path(cert).is_file():
        raise ValueError('Expected scheme_api login and an existing CA certificate')
    return url, expected, cert


def check_connection(connect, url, expected, cert):
    with connect(url, sslmode='verify-full', sslrootcert=cert,
                 connect_timeout=10, prepare_threshold=None,
                 options='-c default_transaction_read_only=on -c statement_timeout=5000') as conn:
        conn.read_only = True
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_user, current_setting('transaction_read_only'), "
                           "pg_has_role(current_user, 'scheme_catalog_reader', 'MEMBER')")
            user, read_only, reader = cursor.fetchone()
            if user != expected or read_only != 'on' or not reader:
                raise ValueError('Unexpected connection role or transaction mode')
            cursor.execute("SELECT rolsuper, rolcreaterole, rolcreatedb, rolbypassrls "
                           "FROM pg_roles WHERE rolname = current_user")
            if any(cursor.fetchone()):
                raise ValueError('Privileged runtime role refused')
            cursor.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'scheme_catalog' "
                           "AND (has_table_privilege(current_user, schemaname || '.' || tablename, 'SELECT') "
                           "OR has_table_privilege(current_user, schemaname || '.' || tablename, 'INSERT,UPDATE,DELETE,TRUNCATE')))")
            if cursor.fetchone()[0]:
                raise ValueError('Runtime role has unexpected base-table access')
            cursor.execute('SELECT id FROM scheme_catalog.published_versions LIMIT 1')
            cursor.fetchone()  # Empty catalogue is a successful connection test.
        conn.rollback()


def main():
    try:
        settings = connection_settings(os.environ)
        import psycopg
        check_connection(psycopg.connect, *settings)
    except Exception:
        # Driver exceptions may contain passwords, DSNs, hostnames or server text.
        print('Database smoke check FAILED. Check local configuration, TLS, migrations and role grants.', file=sys.stderr)
        return 1
    print('Database smoke check passed: verified TLS, read-only backend access, published view reachable.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
