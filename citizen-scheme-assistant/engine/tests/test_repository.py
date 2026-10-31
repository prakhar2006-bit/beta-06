from contextlib import contextmanager
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.errors import APIError
from app.db.connection import open_connection
from app.db.repository import SchemeRepository
from test_api import SUMMARY


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cursor = self.conn.cursor.return_value.__enter__.return_value
        @contextmanager
        def connection():
            yield self.conn
        self.patch = patch('app.db.repository.open_connection', connection)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_list_search_escaping_and_pagination(self):
        self.cursor.fetchone.return_value = {'total': 1}
        self.cursor.fetchall.return_value = [SUMMARY]
        result = SchemeRepository().list_schemes('hi', "' OR 1=1 -- %_!", 'state', 1, 0)
        self.assertEqual(result.total, 1)
        calls = self.cursor.execute.call_args_list
        self.assertEqual(len(calls), 2)
        for call in calls:
            sql, params = call.args
            self.assertNotIn("OR 1=1", sql)
            self.assertIn('!%!_!!', params['search'])
            self.assertIn('scheme_catalog.published_', sql)
            self.assertIn('DISTINCT ON (scheme_id)', sql)
        self.assertIn('ORDER BY id, database_id', calls[-1].args[0])

    def test_offset_beyond_end_retains_total(self):
        self.cursor.fetchone.return_value = {'total': 3}
        self.cursor.fetchall.return_value = []
        result = SchemeRepository().list_schemes('en', None, None, 20, 100)
        self.assertEqual(result.total, 3)
        self.assertEqual(result.items, [])
        self.assertFalse(result.has_more)

    def test_no_translation_preserves_record(self):
        self.cursor.fetchone.return_value = {'total': 1}
        self.cursor.fetchall.return_value = [SUMMARY | {'language': None, 'name': None, 'description': None, 'translation_fallback': True}]
        self.assertIsNone(SchemeRepository().list_schemes('en', None, None, 20, 0).items[0].name)

    def test_unknown_details(self):
        self.cursor.fetchone.return_value = None
        self.assertIsNone(SchemeRepository().get_scheme('unknown', 'en'))

    def test_detail_queries_share_one_connection(self):
        self.cursor.fetchone.return_value = SUMMARY | {'eligibility_text': None, 'translation_evidence_id': None}
        self.cursor.fetchall.return_value = []
        result = SchemeRepository().get_scheme('synthetic-test', 'en')
        self.assertEqual(result.id, 'synthetic-test')
        self.conn.cursor.assert_called_once()
        self.assertEqual(self.cursor.execute.call_count, 8)


class ConnectionTests(unittest.TestCase):
    def setUp(self):
        self.settings = patch('app.db.connection.connection_settings', return_value=(
            'postgresql://scheme_api:synthetic@example.invalid/postgres', 'scheme_api', 'synthetic-ca'))
        self.settings.start()
        self.addCleanup(self.settings.stop)
        self.connect = patch('app.db.connection.psycopg.connect').start()
        self.addCleanup(patch.stopall)
        self.conn = self.connect.return_value.__enter__.return_value
        self.cursor = self.conn.cursor.return_value.__enter__.return_value
        self.cursor.fetchone.side_effect = [dict(username='scheme_api', read_only='on', reader=True, privileged=False), {'unsafe': False}]

    def test_tls_read_only_repeatable_read_and_cleanup(self):
        with open_connection() as conn:
            self.assertIs(conn, self.conn)
        self.assertTrue(self.conn.read_only)
        self.assertEqual(self.conn.isolation_level, psycopg.IsolationLevel.REPEATABLE_READ)
        self.conn.rollback.assert_called_once()
        self.assertEqual(self.connect.call_args.kwargs['sslmode'], 'verify-full')
        self.assertEqual(self.connect.call_args.kwargs['connect_timeout'], 10)
        self.assertIn('statement_timeout=5000', self.connect.call_args.kwargs['options'])
        self.assertIsNone(self.connect.call_args.kwargs['prepare_threshold'])

    def test_driver_errors_mapped_without_details(self):
        for error, code in [(psycopg.OperationalError('synthetic-secret'), 'DATABASE_UNAVAILABLE'),
                            (psycopg.errors.QueryCanceled('synthetic-secret'), 'DATABASE_TIMEOUT'),
                            (psycopg.errors.UndefinedTable('synthetic-secret'), 'DATABASE_QUERY_FAILED')]:
            with self.subTest(code=code):
                self.connect.side_effect = error
                with self.assertRaises(APIError) as caught:
                    with open_connection():
                        self.fail('Connection should fail')
                self.assertEqual(caught.exception.code, code)
                self.assertNotIn('synthetic-secret', caught.exception.message)

    def test_wrong_role_is_rejected(self):
        self.cursor.fetchone.side_effect = [dict(username='postgres', read_only='on', reader=True, privileged=True)]
        with self.assertRaises(APIError):
            with open_connection():
                self.fail('Privileged login accepted')
