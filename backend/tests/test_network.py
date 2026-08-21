from __future__ import annotations

import unittest

from backend.app.network import analyze_distribution_network, parse_distribution_routes


class NetworkAnalyticsTests(unittest.TestCase):
    def test_connected_network_metrics(self) -> None:
        routes = parse_distribution_routes(
            [
                {
                    "source_node": "Pelabuhan A",
                    "target_node": "Hub B",
                    "distance_km": 20,
                    "lead_time_hours": 2,
                    "frequency_per_week": 3,
                    "mode": "laut",
                },
                {
                    "source_node": "Hub B",
                    "target_node": "Pasar C",
                    "distance_km": 15,
                    "lead_time_hours": 1,
                    "frequency_per_week": 2,
                    "mode": "darat",
                },
            ]
        )
        result = analyze_distribution_network(routes)
        self.assertEqual(result["component_count"], 1)
        self.assertEqual(result["active_route_count"], 2)
        self.assertEqual(result["node_metrics"]["Hub B"]["total_degree"], 2)
        self.assertEqual(result["low_connectivity_nodes"], ["Pasar C", "Pelabuhan A"])
        self.assertAlmostEqual(result["frequency_weighted_lead_time_hours"], 1.6)

    def test_detects_disconnected_components(self) -> None:
        routes = parse_distribution_routes(
            [
                {
                    "source_node": "A",
                    "target_node": "B",
                    "distance_km": 1,
                    "lead_time_hours": 1,
                    "frequency_per_week": 2,
                },
                {
                    "source_node": "C",
                    "target_node": "D",
                    "distance_km": 1,
                    "lead_time_hours": 1,
                    "frequency_per_week": 2,
                },
            ]
        )
        result = analyze_distribution_network(routes)
        self.assertEqual(result["component_count"], 2)
        self.assertTrue(any("lebih dari satu komponen" in item for item in result["warnings"]))

    def test_rejects_self_loop(self) -> None:
        with self.assertRaisesRegex(ValueError, "tidak boleh sama"):
            parse_distribution_routes(
                [
                    {
                        "source_node": "A",
                        "target_node": "A",
                        "distance_km": 1,
                        "lead_time_hours": 1,
                        "frequency_per_week": 2,
                    }
                ]
            )


if __name__ == "__main__":
    unittest.main()
