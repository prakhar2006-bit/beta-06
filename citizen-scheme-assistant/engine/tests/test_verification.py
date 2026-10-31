"""Synthetic local verification fixtures; no online requests or live DB writes."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ingestion.prepare import InputError, digest, encode
from ingestion.verification import build_verified_draft, prepare_verified, table_columns, validate_draft
from test_ingestion import record, source


def fixture():
    org, src, snap, ev, scheme, version, rule = [str(uuid4()) for _ in range(7)]
    data = b'Synthetic source only'
    original = record()
    manifest = {'records': [{'original_record': original}], 'source_register': [source()]}
    ledger = {'external_scheme_id': original['scheme_id'], 'input_record_sha256': digest(encode(original)),
        'sources': [{'source_id': 'test', 'url': source()['url'], 'reuse_status': 'attribution_permitted',
                     'snapshot': {'artifact_path': 'source.txt', 'content_sha256': digest(data), 'fetched_at': '2026-10-31T00:00:00+00:00'}}],
        'claims': [{'claim_id': 'test', 'assertion': 'Synthetic assertion', 'status': 'verified_official_guidance', 'source_ids': ['test'], 'checked_date': '2026-10-31'}],
        'rows': {
            'organizations': [{'id': org, 'code': 'test', 'name': 'Synthetic', 'government_level': 'central', 'official_url': source()['url']}],
            'official_sources': [{'id': src, 'organization_id': org, 'original_url': source()['url'], 'title': 'Synthetic', 'source_kind': 'webpage'}],
            'source_snapshots': [{'id': snap, 'source_id': src, 'content_sha256': digest(data), 'media_type': 'text/plain', 'fetched_at': '2026-10-31T00:00:00+00:00'}],
            'evidence': [{'id': ev, 'snapshot_id': snap, 'locator': 'test', 'supporting_text': 'Synthetic', 'last_checked_date': '2026-10-31'}],
            'schemes': [{'id': scheme, 'organization_id': org, 'stable_id': 'test-only', 'government_level': 'central'}],
            'scheme_versions': [{'id': version, 'scheme_id': scheme, 'version_number': 1, 'status': 'draft'}],
            'eligibility_rules': [{'id': rule, 'scheme_version_id': version, 'rule_key': 'test', 'parent_id': None, 'node_type': 'predicate', 'attribute': 'synthetic', 'operator': 'eq', 'expected_value': True, 'confidence': 'UNCERTAIN', 'uncertainty_reason': 'Synthetic draft'}],
            'rule_evidence': [{'id': str(uuid4()), 'scheme_version_id': version, 'rule_id': rule, 'evidence_id': ev}]},
        'rule_review': [{'rule_key': 'test', 'enabled': False, 'claim_ids': ['test']}],
        'bilingual_content': {'en': 'Synthetic draft', 'hi': None}, 'blockers': ['Synthetic review pending']}
    return manifest, ledger, data


class VerificationTests(unittest.TestCase):
    def test_uses_actual_schema_columns(self):
        self.assertEqual(len(table_columns()), 15)
        self.assertIn('content_sha256', table_columns()['source_snapshots'])
        self.assertNotIn('enabled', table_columns()['eligibility_rules'])

    def build(self, manifest, ledger, data):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            (path / 'source.txt').write_bytes(data)
            return build_verified_draft(manifest, ledger, path)[0]

    def test_source_conflicts_and_determinism_preserved(self):
        manifest, ledger, data = fixture()
        manifest['records'][0]['original_record']['conflicts'] = [{'assertions': ['A', 'B']}]
        ledger['input_record_sha256'] = digest(encode(manifest['records'][0]['original_record']))
        before = deepcopy(ledger)
        first = self.build(manifest, ledger, data)
        second = self.build(manifest, ledger, data)
        self.assertEqual(encode(first), encode(second))
        self.assertEqual(ledger, before)
        self.assertEqual(first['unresolved_archive_conflicts'], [{'assertions': ['A', 'B']}])
        self.assertFalse(first['eligible_for_execution'])

    def test_rejects_duplicate_ids_and_unknown_columns(self):
        manifest, ledger, data = fixture()
        payload = self.build(manifest, ledger, data)
        for change in ['duplicate', 'unknown']:
            bad = deepcopy(payload)
            if change == 'duplicate': bad['rows']['schemes'] *= 2
            else: bad['rows']['schemes'][0]['unsupported'] = True
            with self.assertRaises(InputError): validate_draft(bad)

    def test_unverified_rules_cannot_map_as_confirmed(self):
        manifest, ledger, data = fixture()
        ledger['claims'][0]['status'] = 'unverified'
        with self.assertRaises(InputError): self.build(manifest, ledger, data)

    def test_enabled_or_published_records_are_rejected(self):
        manifest, ledger, data = fixture()
        for kind in ['enabled', 'published']:
            bad = deepcopy(ledger)
            if kind == 'enabled': bad['rule_review'][0]['enabled'] = True
            else: bad['rows']['scheme_versions'][0]['status'] = 'published'
            with self.assertRaises(InputError): self.build(manifest, bad, data)

    def test_source_hash_path_and_record_binding(self):
        manifest, ledger, data = fixture()
        for kind in ['hash', 'path', 'record']:
            bad = deepcopy(ledger)
            if kind == 'hash': bad['sources'][0]['snapshot']['content_sha256'] = '0' * 64
            elif kind == 'path': bad['sources'][0]['snapshot']['artifact_path'] = '../outside.txt'
            else: bad['input_record_sha256'] = 'wrong'
            with self.assertRaises(InputError): self.build(manifest, bad, data)

    def test_offline_dry_run_never_overwrites(self):
        manifest, ledger, data = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'source.txt').write_bytes(data)
            (root / 'manifest.json').write_bytes(encode(manifest))
            (root / 'ledger.json').write_bytes(encode(ledger))
            with patch('socket.socket', side_effect=AssertionError('No network')), patch('psycopg.connect', side_effect=AssertionError('No database')):
                target = prepare_verified(root / 'manifest.json', root / 'ledger.json', root / 'out')
                self.assertTrue((target / 'draft.json').exists())
                with self.assertRaises(FileExistsError):
                    prepare_verified(root / 'manifest.json', root / 'ledger.json', root / 'out')
