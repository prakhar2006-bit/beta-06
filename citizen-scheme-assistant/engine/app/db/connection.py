"""One bounded read-only connection per request, never one per catalogue row."""
from contextlib import contextmanager
import os
from typing import Iterator
from urllib.parse import unquote, urlsplit

import psycopg
from psycopg.rows import dict_row

from database_smoke import connection_settings
from app.core.errors import APIError


@contextmanager
def open_connection() -> Iterator[psycopg.Connection]:
    try:
        url, expected, cert = connection_settings(os.environ)
        username = unquote(urlsplit(url).username or "")
        if username != expected and not username.startswith(expected + "."):
            raise ValueError("Unexpected configured login")
    except (ValueError, OSError):
        raise APIError(503, "DATABASE_UNAVAILABLE", "Database service is unavailable.") from None
    try:
        with psycopg.connect(
            url, sslmode="verify-full", sslrootcert=cert, connect_timeout=10,
            prepare_threshold=None, row_factory=dict_row,
            options="-c default_transaction_read_only=on -c statement_timeout=5000",
        ) as conn:
            conn.read_only = True
            conn.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
            with conn.cursor() as cursor:
                cursor.execute("SELECT current_user AS username, current_setting('transaction_read_only') AS read_only, "
                               "pg_has_role(current_user, 'scheme_catalog_reader', 'MEMBER') AS reader, "
                               "rolsuper OR rolcreaterole OR rolcreatedb OR rolbypassrls AS privileged "
                               "FROM pg_roles WHERE rolname = current_user")
                role = cursor.fetchone()
                if (not role or role["username"] != expected or role["read_only"] != "on"
                        or not role["reader"] or role["privileged"]):
                    raise APIError(503, "DATABASE_UNAVAILABLE", "Database service is unavailable.")
                cursor.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'scheme_catalog' "
                               "AND (has_table_privilege(current_user, schemaname || '.' || tablename, 'SELECT') "
                               "OR has_table_privilege(current_user, schemaname || '.' || tablename, 'INSERT,UPDATE,DELETE,TRUNCATE'))) AS unsafe")
                if cursor.fetchone()["unsafe"]:
                    raise APIError(503, "DATABASE_UNAVAILABLE", "Database service is unavailable.")
            try:
                yield conn
            finally:
                conn.rollback()
    except psycopg.errors.QueryCanceled:
        raise APIError(503, "DATABASE_TIMEOUT", "Database request timed out.") from None
    except (psycopg.OperationalError, psycopg.InterfaceError):
        raise APIError(503, "DATABASE_UNAVAILABLE", "Database service is unavailable.") from None
    except psycopg.Error:
        raise APIError(503, "DATABASE_QUERY_FAILED", "Database request could not be completed.") from None
