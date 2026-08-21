"""Small SQLite store for traceable reference-analysis records."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence
from uuid import uuid4

from .analytics import PriceObservation


class AnalysisStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS price_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    observed_on TEXT NOT NULL,
                    region TEXT NOT NULL,
                    commodity TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    price REAL NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS analysis_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL UNIQUE,
                    analysis_type TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def save_price_batch(self, observations: Sequence[PriceObservation]) -> str:
        batch_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        rows = [
            (
                batch_id,
                item.source,
                item.observed_on.isoformat(),
                item.region,
                item.commodity,
                item.unit,
                item.price,
                created_at,
            )
            for item in observations
        ]
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO price_observations (
                    batch_id, source, observed_on, region, commodity, unit, price, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return batch_id

    def save_analysis(self, analysis_type: str, result: dict[str, object]) -> str:
        analysis_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO analysis_audit (
                    analysis_id, analysis_type, result_json, created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (analysis_id, analysis_type, json.dumps(result, ensure_ascii=False), created_at),
            )
        return analysis_id

    def list_audit(self, limit: int = 50) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT analysis_id, analysis_type, result_json, created_at
                FROM analysis_audit
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "analysis_id": row["analysis_id"],
                "analysis_type": row["analysis_type"],
                "result": json.loads(row["result_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
