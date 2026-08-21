from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from backend.app.csv_loader import load_price_csv, load_route_csv


class CsvLoaderTests(unittest.TestCase):
    def test_loads_price_and_route_samples(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            price_path = Path(directory) / "prices.csv"
            price_path.write_text(
                "source,date,region,commodity,unit,price\n"
                "Sumber,2026-01-01,A,Beras medium,kg,15000\n"
                "Sumber,2026-01-01,B,Beras medium,kg,17000\n",
                encoding="utf-8",
            )
            route_path = Path(directory) / "routes.csv"
            route_path.write_text(
                "source_node,target_node,distance_km,lead_time_hours,frequency_per_week,mode,active\n"
                "Pelabuhan,Pasar,25,3,2,laut,true\n",
                encoding="utf-8",
            )
            self.assertEqual(len(load_price_csv(price_path)), 2)
            self.assertEqual(len(load_route_csv(route_path)), 1)


if __name__ == "__main__":
    unittest.main()
