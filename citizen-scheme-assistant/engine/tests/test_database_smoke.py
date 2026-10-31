import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import database_smoke


class SmokeTests(unittest.TestCase):
    def test_configuration_requires_tls_certificate_and_dedicated_user(self):
        with tempfile.NamedTemporaryFile() as cert:
            env = {'DATABASE_URL': 'postgresql://scheme_api:synthetic@db.example.invalid/postgres',
                   'DATABASE_EXPECTED_USER': 'scheme_api', 'DATABASE_SSL_ROOT_CERT': cert.name}
            self.assertEqual(database_smoke.connection_settings(env)[1], 'scheme_api')
            for changes in [{'DATABASE_URL': ''}, {'DATABASE_EXPECTED_USER': 'postgres'},
                            {'DATABASE_SSL_ROOT_CERT': 'missing'},
                            {'DATABASE_URL': env['DATABASE_URL'] + '?sslmode=disable'}]:
                with self.assertRaises(ValueError):
                    database_smoke.connection_settings(env | changes)

    def test_connection_is_read_only_bounded_and_rolled_back(self):
        connect = MagicMock()
        conn = connect.return_value.__enter__.return_value
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.side_effect = [('scheme_api', 'on', True), (False,) * 4, (False,), None]
        database_smoke.check_connection(connect, 'synthetic-dsn', 'scheme_api', 'synthetic-cert')
        self.assertTrue(conn.read_only)
        self.assertEqual(connect.call_args.kwargs['sslmode'], 'verify-full')
        self.assertEqual(connect.call_args.kwargs['connect_timeout'], 10)
        self.assertIsNone(connect.call_args.kwargs['prepare_threshold'])
        conn.rollback.assert_called_once()
        self.assertTrue(all(call.args[0].startswith('SELECT ') for call in cursor.execute.call_args_list))

    def test_errors_do_not_print_connection_details(self):
        with patch.object(database_smoke, 'connection_settings', side_effect=ValueError('synthetic-secret')), contextlib.redirect_stderr(io.StringIO()) as output:
            self.assertEqual(database_smoke.main(), 1)
        self.assertNotIn('synthetic-secret', output.getvalue())


if __name__ == '__main__':
    unittest.main()
