from pathlib import Path
import sys
import unittest

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app


class HealthTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        )
        self.addAsyncCleanup(self.client.aclose)

    async def test_health(self):
        response = await self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "ok",
            "service": "Scheme Navigator",
            "version": "0.1.0",
        })

    async def test_swagger_and_openapi(self):
        response = await self.client.get("/docs")
        self.assertEqual(response.status_code, 200)
        self.assertIn("swagger-ui", response.text)
        response = await self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["info"], {
            "title": "Scheme Navigator API",
            "description": "Multilingual Government Scheme Eligibility Assistant",
            "version": "0.1.0",
        })


if __name__ == "__main__":
    unittest.main()
