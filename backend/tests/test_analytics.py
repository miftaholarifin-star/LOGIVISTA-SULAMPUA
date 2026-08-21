from __future__ import annotations

import unittest

from backend.app.analytics import (
    analyze_prices,
    coefficient_of_variation,
    parse_price_observations,
    proposed_pdi_v01,
)


class PriceAnalyticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            {
                "source": "Sumber A",
                "date": "2026-01-01",
                "region": "Wilayah A",
                "commodity": "Beras medium",
                "unit": "kg",
                "price": 10_000,
            },
            {
                "source": "Sumber A",
                "date": "2026-01-01",
                "region": "Wilayah B",
                "commodity": "Beras medium",
                "unit": "kg",
                "price": 20_000,
            },
            {
                "source": "Sumber B",
                "date": "2026-01-08",
                "region": "Wilayah A",
                "commodity": "Beras medium",
                "unit": "kg",
                "price": 12_000,
            },
            {
                "source": "Sumber B",
                "date": "2026-01-08",
                "region": "Wilayah B",
                "commodity": "Beras medium",
                "unit": "kg",
                "price": 22_000,
            },
        ]

    def test_formula_values(self) -> None:
        self.assertAlmostEqual(coefficient_of_variation([11_000, 21_000]), 31.25)
        self.assertAlmostEqual(proposed_pdi_v01([11_000, 21_000]), 62.5)

    def test_analysis_aggregates_per_region(self) -> None:
        result = analyze_prices(parse_price_observations(self.rows))
        self.assertEqual(result["regional_mean_prices"], {"Wilayah A": 11000.0, "Wilayah B": 21000.0})
        self.assertEqual(result["status"], "PERLU_PRIORITAS")
        self.assertAlmostEqual(result["trend_percent"], 13.3333, places=4)
        self.assertEqual(result["traceability"]["sources"], ["Sumber A", "Sumber B"])

    def test_rejects_missing_required_field(self) -> None:
        invalid = dict(self.rows[0])
        invalid.pop("source")
        with self.assertRaisesRegex(ValueError, "source"):
            parse_price_observations([invalid, self.rows[1]])

    def test_rejects_mixed_commodities(self) -> None:
        rows = [dict(self.rows[0]), dict(self.rows[1])]
        rows[1]["commodity"] = "Gula pasir"
        with self.assertRaisesRegex(ValueError, "satu komoditas"):
            analyze_prices(parse_price_observations(rows))

    def test_rejects_single_region(self) -> None:
        rows = [dict(self.rows[0]), dict(self.rows[2])]
        with self.assertRaisesRegex(ValueError, "dua wilayah"):
            analyze_prices(parse_price_observations(rows))


if __name__ == "__main__":
    unittest.main()
