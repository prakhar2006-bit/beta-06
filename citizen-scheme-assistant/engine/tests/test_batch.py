"""Offline collection preparation reuses synthetic verification fixtures."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ingestion.batch import prepare_collection, validate_collection
from ingestion.prepare import InputError, digest, encode, parse_json
from test_verification import fixture


class CollectionTests(unittest.TestCase):
    def inputs(self, root):
        manifest, ledger, data = fixture()
        (root / 'source.txt').write_bytes(data)
        (root / 'manifest.json').write_bytes(encode(manifest))
        (root / 'ledger.json').write_bytes(encode(ledger))
        return root / 'manifest.json', root / 'ledger.json'

    def test_deterministic_collection_preserves_bundle_and_is_offline(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest, ledger = self.inputs(root)
            with patch('socket.socket', side_effect=AssertionError('Network forbidden')), patch('psycopg.connect', side_effect=AssertionError('Live DB forbidden')):
                a = prepare_collection(manifest, [ledger], root / 'a')
                b = prepare_collection(manifest, [ledger], root / 'b')
                self.assertEqual(a.read_bytes(), b.read_bytes())
                self.assertEqual(encode(validate_collection(a)), encode(validate_collection(b)))
                with self.assertRaises(FileExistsError): prepare_collection(manifest, [ledger], root / 'a')

    def test_duplicate_scheme_identifiers_rejected_before_preparation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); manifest, ledger = self.inputs(root)
            with self.assertRaises(InputError): prepare_collection(manifest, [ledger, ledger], root / 'out')
            self.assertFalse((root / 'out').exists())

    def test_collection_hash_identity_and_path_guards(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); manifest, ledger = self.inputs(root)
            index_path = prepare_collection(manifest, [ledger], root / 'out')
            original = parse_json(index_path.read_bytes())
            for kind in ['hash', 'identity', 'path', 'duplicate']:
                index = parse_json(encode(original))
                if kind == 'hash': index['schemes'][0]['sha256'] = '0' * 64
                elif kind == 'identity': index['schemes'][0]['stable_id'] = 'different-id'
                elif kind == 'path': index['schemes'][0]['path'] = '../ledger.json'
                else: index['schemes'] *= 2
                index_path.write_bytes(encode(index))
                with self.assertRaises(InputError): validate_collection(index_path)
