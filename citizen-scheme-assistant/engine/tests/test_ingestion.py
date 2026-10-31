"""Synthetic safety fixtures only; the real archive is audited by the CLI."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ingestion.prepare import (ACTIVE, InputError, build_manifest, encode,
                               inspect_archive, main, parse_artifacts, parse_json,
                               prepare, safe_name, validate_records)


def source():
    return {'source_id': 'TEST', 'url': 'https://example.invalid/source', 'title': 'Synthetic', 'publisher': 'Synthetic'}


def record():
    return {'scheme_id': 'TEST-ONLY', 'official_name': 'Synthetic test only', 'classification': 'central',
            'jurisdiction': 'Synthetic', 'record_stage': 'discovered', 'source_ids': ['TEST'],
            'discovery_evidence': [{'source_id': 'TEST', 'url': source()['url'], 'locator': 'test'}],
            **{k: [] for k in ['benefits', 'eligibility_conditions', 'exclusions', 'documents', 'guidelines',
                               'translations', 'missing_information', 'conflicts', 'unresolved_questions']},
            'application': {}, 'unknown_future_field': {'preserve': True}}


def zip_bytes(entries):
    output = io.BytesIO()
    with ZipFile(output, 'w') as archive:
        for name, value in entries:
            archive.writestr(name, value)
    return output.getvalue()


def fixture_archive():
    return zip_bytes([(ACTIVE + 'scheme_records.json', encode({'records': [record()]})),
                      (ACTIVE + 'detailed_scheme_records.json', encode({'records': []})),
                      (ACTIVE + 'sources.json', encode([source()])),
                      (ACTIVE + 'record_schema.json', encode({'required': ['scheme_id']})),
                      ('untrusted.py', b'raise RuntimeError("MUST NOT EXECUTE")')])


class IngestionTests(unittest.TestCase):
    def test_zip_traversal_windows_reserved_and_duplicate_names(self):
        for name in ['../escape.json', '/absolute.json', 'C:/drive.json', 'a\\b.json', 'CON.txt', 'a:stream', 'a./b']:
            with self.subTest(name=name), self.assertRaises(InputError):
                safe_name(name)  # ZipInfo itself normalizes backslashes on Windows.
        with self.assertRaises(InputError):
            inspect_archive(zip_bytes([('a.json', b'{}'), ('A.JSON', b'{}')]))

    def test_symlinks_binaries_corruption_and_expansion_limits(self):
        link = ZipInfo('link')
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        for content in [b'not a zip', zip_bytes([('bad.exe', b'bad')]), zip_bytes([(link, b'../outside')])]:
            with self.assertRaises(InputError):
                inspect_archive(content)
        with patch('ingestion.prepare.MAX_FILE', 1), self.assertRaises(InputError):
            inspect_archive(zip_bytes([('large.json', b'{}')]))
        corrupt = zip_bytes([('crc.txt', b'uniqueCRC')]).replace(b'uniqueCRC', b'uniqueCRD')
        with self.assertRaises(InputError):
            inspect_archive(corrupt)
        with self.assertRaises(InputError):
            inspect_archive(zip_bytes([('nested.zip', zip_bytes([('../unsafe', b'bad')]))]))

    def test_valid_and_invalid_json(self):
        self.assertEqual(parse_json(b'{"test":1}'), {'test': 1})
        for data in [b'{', b'{"x":1,"x":2}', b'{"x":NaN}']:
            with self.assertRaises(InputError):
                parse_json(data)

    def test_csv_width_and_nested_json_validation(self):
        for data in [b'a,b\n1\n', b'a\n"{bad}"\n']:
            with self.assertRaises(InputError):
                parse_artifacts({'x.csv': data})

    def test_malformed_missing_fields_and_duplicate_scheme(self):
        for records in [[{}], [record(), record()], [record() | {'benefits': ['bad']}], [record() | {'eligibility_conditions': 'bad'}]]:
            with self.assertRaises(InputError):
                validate_records(records, [source()])

    def test_source_integrity(self):
        bad = record()
        bad['discovery_evidence'][0]['url'] = 'https://example.invalid/changed'
        with self.assertRaises(InputError):
            validate_records([bad], [source()])

    def test_source_conflict_and_unknown_field_preservation(self):
        item = record()
        item['conflicts'] = [{'field': 'income', 'assertions': [{'text': '< limit'}, {'text': '<= limit'}]}]
        item['eligibility_conditions'] = [{'rule_id': 'r', 'text': 'Synthetic assertion', 'field': 'income', 'operator': '<=', 'value': 1}]
        result = build_manifest([item], [source()], 'test', [], [])
        prepared = result['records'][0]
        self.assertEqual(prepared['original_record'], item)
        self.assertEqual(prepared['conflicts_preserved'], item['conflicts'])
        self.assertEqual(prepared['condition_proposals'][0]['category'], 'ambiguous_or_conflicting')
        self.assertFalse(prepared['condition_proposals'][0]['enabled'])
        self.assertEqual(result['summary']['publication_ready'], 0)

    def test_dry_run_determinism_quarantine_and_no_database_or_network(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'fixture.zip'
            archive.write_bytes(fixture_archive())
            with patch('socket.socket', side_effect=AssertionError('Network forbidden')), patch('psycopg.connect', side_effect=AssertionError('Database forbidden')):
                first, manifest = prepare(archive, root / 'one')
                second, again = prepare(archive, root / 'two')
                self.assertEqual((first / 'manifest.json').read_bytes(), (second / 'manifest.json').read_bytes())
                self.assertEqual(manifest['database_operations'], [])
                self.assertTrue((first / 'quarantine/untrusted.py.disabled').is_file())
                self.assertFalse((first / 'extracted/untrusted.py').exists())
            with self.assertRaises(FileExistsError):
                prepare(archive, root / 'one')
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(['--archive', str(archive), '--output-root', str(root / 'cli'), '--dry-run']), 0)

    def test_detailed_conflicting_copy_is_rejected(self):
        files = [('scheme_records.json', {'records': [record()]}), ('detailed_scheme_records.json', {'records': [record() | {'official_name': 'Changed'}]}),
                 ('sources.json', [source()]), ('record_schema.json', {'required': ['scheme_id']})]
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / 'fixture.zip'
            archive.write_bytes(zip_bytes([(ACTIVE + name, encode(data)) for name, data in files]))
            with self.assertRaises(InputError):
                prepare(archive, Path(temporary) / 'out')
