"""Synthetic response fixtures only; no government records or database writes."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app
from app.core.errors import APIError
from app.db.repository import get_repository
from app.schemas.schemes import SchemeDetail, SchemeList, SchemeSummary

SUMMARY = {
    "id": "synthetic-test", "database_id": "00000000-0000-4000-8000-000000000001",
    "version_id": "00000000-0000-4000-8000-000000000002", "version_number": 1,
    "requested_language": "en", "language": "en", "translation_fallback": False,
    "name": "Synthetic test only", "description": "Not a government scheme",
    "level": "state", "lifecycle_status": "unknown", "organization_code": "test",
    "organization_name": "Synthetic organization", "organization_url": "https://example.invalid",
    "last_checked_date": "2026-10-31", "effective_from": None, "effective_to": None,
    "published_at": "2026-10-31T00:00:00Z",
}


class APITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.repo = Mock()
        app.dependency_overrides[get_repository] = lambda: self.repo
        self.addCleanup(app.dependency_overrides.clear)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test")
        self.addAsyncCleanup(self.client.aclose)

    async def test_language_metadata(self):
        response = await self.client.get('/api/v1/meta/languages')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([x['code'] for x in response.json()['items']], ['en', 'hi'])
        self.repo.health.assert_not_called()

    async def test_empty_catalog(self):
        self.repo.list_schemes.return_value = SchemeList(items=[], total=0, limit=20, offset=0, has_more=False)
        response = await self.client.get('/api/v1/schemes')
        self.assertEqual(response.json(), {"items": [], "total": 0, "limit": 20, "offset": 0, "has_more": False})
        self.repo.list_schemes.assert_called_once_with('en', None, None, 20, 0)

    async def test_listing_pagination_search_and_filter(self):
        self.repo.list_schemes.return_value = SchemeList(items=[SchemeSummary(**SUMMARY)], total=5, limit=1, offset=2, has_more=True)
        response = await self.client.get('/api/v1/schemes', params={"lang": "hi", "search": "test", "level": "state", "limit": 1, "offset": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['items'][0]['id'], 'synthetic-test')
        self.assertTrue(response.json()['has_more'])
        self.repo.list_schemes.assert_called_once_with('hi', 'test', 'state', 1, 2)

    async def test_details_missing_translation_explicit(self):
        self.repo.get_scheme.return_value = SchemeDetail(**(SUMMARY | {
            "requested_language": "hi", "translation_fallback": True,
            "eligibility_text": None, "translation_evidence_id": None,
            "benefits": [], "application_routes": [], "required_documents": [],
            "eligibility_rules": [], "rule_evidence": [], "sources": [], "jurisdictions": [],
        }))
        response = await self.client.get('/api/v1/schemes/synthetic-test?lang=hi')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['language'], 'en')
        self.assertTrue(response.json()['translation_fallback'])

    async def test_unknown_or_unpublished_scheme(self):
        self.repo.get_scheme.return_value = None
        response = await self.client.get('/api/v1/schemes/unknown')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error']['code'], 'SCHEME_NOT_FOUND')

    async def test_invalid_request_parameters(self):
        for query in ['lang=xx', 'limit=0', 'limit=101', 'offset=-1', 'level=other', 'limit=no', 'search=' + 'x' * 201]:
            with self.subTest(query=query):
                response = await self.client.get('/api/v1/schemes?' + query)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()['error']['code'], 'INVALID_REQUEST')
        self.repo.list_schemes.assert_not_called()

    async def test_database_failures_are_sanitized(self):
        for code in ['DATABASE_UNAVAILABLE', 'DATABASE_TIMEOUT', 'DATABASE_QUERY_FAILED']:
            self.repo.list_schemes.side_effect = APIError(503, code, 'Database request failed.')
            response = await self.client.get('/api/v1/schemes')
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json()['error']['code'], code)

    async def test_unexpected_error_is_sanitized(self):
        self.repo.list_schemes.side_effect = RuntimeError('synthetic-secret SQL host')
        response = await self.client.get('/api/v1/schemes')
        self.assertEqual(response.status_code, 500)
        self.assertNotIn('synthetic-secret', response.text)

    async def test_database_health(self):
        self.assertEqual((await self.client.get('/api/v1/meta/health/db')).json(), {"status": "ok"})
        self.repo.health.side_effect = APIError(503, 'DATABASE_UNAVAILABLE', 'Database service is unavailable.')
        self.assertEqual((await self.client.get('/api/v1/meta/health/db')).status_code, 503)
        self.assertEqual((await self.client.get('/health')).status_code, 200)

    async def test_cors_and_openapi(self):
        allowed = await self.client.options('/api/v1/schemes', headers={
            'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'GET'})
        self.assertEqual(allowed.headers.get('access-control-allow-origin'), 'http://localhost:5173')
        denied = await self.client.options('/api/v1/schemes', headers={
            'Origin': 'https://example.invalid', 'Access-Control-Request-Method': 'GET'})
        self.assertNotIn('access-control-allow-origin', denied.headers)
        paths = (await self.client.get('/openapi.json')).json()['paths']
        self.assertIn('/api/v1/schemes/{scheme_id}', paths)
        self.assertIn('/api/v1/meta/health/db', paths)
