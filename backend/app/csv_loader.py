"""CSV import helpers with explicit column validation."""

from __future__ import annotations

import csv
from pathlib import Path

from .analytics import PriceObservation, parse_price_observations
from .network import DistributionRoute, parse_distribution_routes


def load_price_csv(path: str | Path) -> list[PriceObservation]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return parse_price_observations(csv.DictReader(handle))


def load_route_csv(path: str | Path) -> list[DistributionRoute]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return parse_distribution_routes(csv.DictReader(handle))
