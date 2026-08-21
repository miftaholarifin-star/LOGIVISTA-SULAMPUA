from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_health_and_methodology(self) -> None:
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["version"], "0.1.0")
        methodology = self.client.get("/api/v1/methodology")
        self.assertEqual(methodology.status_code, 200)
        self.assertIn("usulan", methodology.json()["status"])

    def test_price_analysis_endpoint(self) -> None:
        response = self.client.post(
            "/api/v1/analysis/prices",
            json={
                "observations": [
                    {
                        "source": "Sintetis",
                        "date": "2026-01-01",
                        "region": "A",
                        "commodity": "Cabai",
                        "unit": "kg",
                        "price": 40000,
                    },
                    {
                        "source": "Sintetis",
                        "date": "2026-01-01",
                        "region": "B",
                        "commodity": "Cabai",
                        "unit": "kg",
                        "price": 50000,
                    },
                ],
                "persist": False,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["region_count"], 2)
        self.assertIn("pdi_v01_percent", response.json())

    def test_network_analysis_endpoint(self) -> None:
        response = self.client.post(
            "/api/v1/analysis/network",
            json={
                "routes": [
                    {
                        "source_node": "A",
                        "target_node": "B",
                        "distance_km": 10,
                        "lead_time_hours": 2,
                        "frequency_per_week": 3,
                        "mode": "laut",
                        "active": True,
                    }
                ],
                "persist": False,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["active_route_count"], 1)


if __name__ == "__main__":
    unittest.main()
