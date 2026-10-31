"""Local draft previews never use database connections or approve policies."""
import copy
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app
from app.api.routes.demo import item


ROWS = {
    'schemes': [{'stable_id': 'synthetic-only', 'organization_id': 'org', 'government_level': 'central'}],
    'scheme_versions': [{'version_number': 1}],
    'organizations': [{'id': 'org', 'name': 'Synthetic organization'}],
    'translations': [
        {'language_code': 'en', 'title': 'Synthetic only', 'summary': 'Not government policy', 'eligibility_text': 'Unreviewed'},
        {'language_code': 'hi', 'title': 'केवल परीक्षण', 'summary': 'सरकारी नीति नहीं', 'eligibility_text': 'समीक्षा शेष'},
    ],
    'official_sources': [{'id': 'source', 'original_url': 'https://example.invalid', 'title': 'Synthetic evidence'}],
    'source_snapshots': [{'id': 'snapshot', 'source_id': 'source'}],
    'evidence': [{'id': 'evidence', 'snapshot_id': 'snapshot', 'locator': 'Synthetic', 'last_checked_date': '2026-10-31'}],
}


class DemoTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.env = patch.dict(os.environ, SCHEME_DEMO_ENABLED='1', SCHEME_APP_ENV='development')
        self.env.start()
        self.addCleanup(self.env.stop)
        self.records = patch('app.api.routes.demo.demo_records', return_value=(ROWS,))
        self.records.start()
        self.addCleanup(self.records.stop)
        self.db = patch('app.db.connection.psycopg.connect', side_effect=AssertionError('No database access allowed'))
        self.db.start()
        self.addCleanup(self.db.stop)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://127.0.0.1')
        self.addAsyncCleanup(self.client.aclose)

    async def test_disabled_and_production_are_unavailable(self):
        for setting in [{'SCHEME_DEMO_ENABLED': '0'}, {'SCHEME_APP_ENV': 'production'}]:
            with patch.dict(os.environ, setting):
                self.assertEqual((await self.client.get('/api/v1/demo/schemes')).status_code, 404)

    async def test_non_loopback_and_public_hostname_are_unavailable(self):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app, client=('203.0.113.1', 1234)), base_url='http://localhost') as client:
            self.assertEqual((await client.get('/api/v1/demo/schemes')).status_code, 404)
        self.assertEqual((await self.client.get('http://example.invalid/api/v1/demo/schemes')).status_code, 404)

    async def test_list_labels_languages_and_no_database_access(self):
        for lang, title in [('en', 'Synthetic only'), ('hi', 'केवल परीक्षण')]:
            response = await self.client.get('/api/v1/demo/schemes', params={'lang': lang})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['cache-control'], 'no-store')
            data = response.json()
            self.assertEqual(data['total'], 1)
            scheme = data['items'][0]
            self.assertEqual(scheme['name'], title)
            self.assertEqual(scheme['verification_status'], 'UNVERIFIED')
            self.assertEqual(scheme['publication_status'], 'draft')
            self.assertIsNone(scheme['published_at'])
            self.assertFalse(scheme['eligibility_execution_enabled'])
            self.assertEqual(scheme['translation_review_status'], 'draft')
        self.assertNotIn('.phase3-output', response.text)

    async def test_detail_source_provenance_and_unknown_identifier(self):
        data = (await self.client.get('/api/v1/demo/schemes/synthetic-only?lang=hi')).json()
        self.assertEqual(data['sources'][0]['original_url'], 'https://example.invalid')
        self.assertEqual(data['sources'][0]['last_checked_date'], '2026-10-31')
        self.assertEqual((await self.client.get('/api/v1/demo/schemes/missing')).status_code, 404)

    async def test_filter_pagination_and_invalid_language(self):
        self.assertEqual((await self.client.get('/api/v1/demo/schemes?search=absent')).json()['total'], 0)
        self.assertEqual((await self.client.get('/api/v1/demo/schemes?level=state')).json()['total'], 0)
        data = (await self.client.get('/api/v1/demo/schemes?offset=1')).json()
        self.assertEqual(data['items'], [])
        self.assertEqual(data['total'], 1)
        for query in ['lang=xx', 'limit=0', 'offset=-1']:
            self.assertEqual((await self.client.get('/api/v1/demo/schemes?' + query)).status_code, 422)

    async def test_missing_translation_uses_labelled_english(self):
        rows = copy.deepcopy(ROWS)
        rows['translations'] = rows['translations'][:1]
        result = item(rows, 'hi')
        self.assertEqual(result['requested_language'], 'hi')
        self.assertEqual(result['language'], 'en')
        self.assertTrue(result['translation_fallback'])
