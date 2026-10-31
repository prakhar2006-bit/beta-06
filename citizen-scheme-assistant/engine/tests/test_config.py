"""Fresh-checkout CORS integration; no .env, database or frontend writes."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.config import cors_origins


class ConfigurationTests(unittest.IsolatedAsyncioTestCase):
    async def preflight(self, allowed, origin):
        app = FastAPI()
        app.add_middleware(CORSMiddleware, allow_origins=allowed, allow_credentials=False,
                           allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
            return await client.options('/api/v1/demo/questionnaire/start', headers={
                'Origin': origin, 'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'content-type'})

    async def test_documented_frontend_port_works_without_environment_overrides(self):
        with patch.dict(os.environ, {}, clear=True):
            allowed = cors_origins()
        for origin in ('http://localhost:3001', 'http://127.0.0.1:3001', 'http://localhost:5173'):
            response = await self.preflight(allowed, origin)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['access-control-allow-origin'], origin)
            self.assertNotIn('access-control-allow-credentials', response.headers)

    async def test_explicit_deployment_origins_override_local_defaults(self):
        with patch.dict(os.environ, {'CORS_ORIGINS': 'https://example.invalid'}, clear=True):
            allowed = cors_origins()
        self.assertEqual(allowed, ['https://example.invalid'])
        self.assertEqual((await self.preflight(allowed, 'https://example.invalid')).status_code, 200)
        denied = await self.preflight(allowed, 'http://localhost:3001')
        self.assertEqual(denied.status_code, 400)
        self.assertNotIn('access-control-allow-origin', denied.headers)

    async def test_unsafe_origins_are_rejected_without_echoing_configuration(self):
        for origin in ('*', 'https://*.example.invalid', 'https://user:private-placeholder@example.invalid',
                       'https://example.invalid/path', 'file:///tmp/demo'):
            with patch.dict(os.environ, {'CORS_ORIGINS': origin}, clear=True):
                with self.assertRaises(ValueError) as error:
                    cors_origins()
                self.assertNotIn('private-placeholder', str(error.exception))
