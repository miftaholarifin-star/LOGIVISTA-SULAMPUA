from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from backend.app.analytics import parse_price_observations
from backend.app.database import AnalysisStore


class AnalysisStoreTests(unittest.TestCase):
    def test_persists_batch_and_audit_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = AnalysisStore(Path(directory) / "test.db")
            observations = parse_price_observations(
                [
                    {
                        "source": "A",
                        "date": "2026-01-01",
                        "region": "X",
                        "commodity": "Cabai",
                        "unit": "kg",
                        "price": 40_000,
                    },
                    {
                        "source": "A",
                        "date": "2026-01-01",
                        "region": "Y",
                        "commodity": "Cabai",
                        "unit": "kg",
                        "price": 45_000,
                    },
                ]
            )
            batch_id = store.save_price_batch(observations)
            analysis_id = store.save_analysis("price_disparity", {"batch_id": batch_id})
            records = store.list_audit()
            self.assertEqual(records[0]["analysis_id"], analysis_id)
            self.assertEqual(records[0]["result"]["batch_id"], batch_id)


if __name__ == "__main__":
    unittest.main()
