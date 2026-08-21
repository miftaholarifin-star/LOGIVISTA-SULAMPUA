"""Price-disparity analytics used by LOGIVISTA SULAMPUA.

The PDI formula implemented here is the proposed operational formula v0.1
from the HKI draft. It is intentionally named as a proposal and must not be
presented as a universal or government-standard index.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from statistics import fmean, pstdev
from typing import Iterable, Mapping, Sequence


REQUIRED_PRICE_FIELDS = (
    "source",
    "date",
    "region",
    "commodity",
    "unit",
    "price",
)


@dataclass(frozen=True, slots=True)
class PriceObservation:
    source: str
    observed_on: date
    region: str
    commodity: str
    unit: str
    price: float

    @classmethod
    def from_mapping(cls, row: Mapping[str, object], row_number: int = 1) -> "PriceObservation":
        missing = [field for field in REQUIRED_PRICE_FIELDS if row.get(field) in (None, "")]
        if missing:
            raise ValueError(
                f"Baris {row_number}: kolom wajib kosong atau tidak tersedia: {', '.join(missing)}"
            )

        try:
            observed_on = date.fromisoformat(str(row["date"]).strip())
        except ValueError as exc:
            raise ValueError(f"Baris {row_number}: tanggal harus berformat YYYY-MM-DD") from exc

        try:
            price = float(row["price"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Baris {row_number}: harga harus berupa angka") from exc
        if price <= 0:
            raise ValueError(f"Baris {row_number}: harga harus lebih besar dari nol")

        values = {
            field: str(row[field]).strip()
            for field in ("source", "region", "commodity", "unit")
        }
        for field, value in values.items():
            if not value:
                raise ValueError(f"Baris {row_number}: {field} tidak boleh kosong")

        return cls(
            source=values["source"],
            observed_on=observed_on,
            region=values["region"],
            commodity=values["commodity"],
            unit=values["unit"],
            price=price,
        )


def parse_price_observations(rows: Iterable[Mapping[str, object]]) -> list[PriceObservation]:
    observations = [
        PriceObservation.from_mapping(row, row_number=index)
        for index, row in enumerate(rows, start=1)
    ]
    if len(observations) < 2:
        raise ValueError("Analisis memerlukan sedikitnya dua observasi harga")
    return observations


def coefficient_of_variation(values: Sequence[float]) -> float:
    """Return population CV in percent for a complete regional comparison set."""

    clean = [float(value) for value in values]
    if len(clean) < 2:
        raise ValueError("CV memerlukan sedikitnya dua nilai")
    mean = fmean(clean)
    if mean <= 0:
        raise ValueError("Rata-rata harga harus lebih besar dari nol")
    return pstdev(clean) / mean * 100.0


def proposed_pdi_v01(values: Sequence[float]) -> float:
    """Return proposed PDI v0.1: (maximum - minimum) / mean * 100%."""

    clean = [float(value) for value in values]
    if len(clean) < 2:
        raise ValueError("PDI memerlukan sedikitnya dua nilai")
    mean = fmean(clean)
    if mean <= 0:
        raise ValueError("Rata-rata harga harus lebih besar dari nol")
    return (max(clean) - min(clean)) / mean * 100.0


def _round(value: float) -> float:
    return round(value, 4)


def analyze_prices(
    observations: Sequence[PriceObservation],
    *,
    cv_threshold: float = 10.0,
    pdi_threshold: float = 15.0,
) -> dict[str, object]:
    if len(observations) < 2:
        raise ValueError("Analisis memerlukan sedikitnya dua observasi harga")
    if cv_threshold < 0 or pdi_threshold < 0:
        raise ValueError("Ambang peringatan tidak boleh negatif")

    commodities = {item.commodity.casefold(): item.commodity for item in observations}
    units = {item.unit.casefold(): item.unit for item in observations}
    if len(commodities) != 1:
        raise ValueError("Satu analisis hanya boleh memuat satu komoditas")
    if len(units) != 1:
        raise ValueError("Satuan harga harus seragam dalam satu analisis")

    by_region: dict[str, list[float]] = defaultdict(list)
    by_date: dict[date, list[float]] = defaultdict(list)
    for item in observations:
        by_region[item.region].append(item.price)
        by_date[item.observed_on].append(item.price)
    if len(by_region) < 2:
        raise ValueError("Perbandingan disparitas memerlukan sedikitnya dua wilayah")

    regional_means = {region: fmean(values) for region, values in by_region.items()}
    comparison_values = list(regional_means.values())
    mean_price = fmean(comparison_values)
    cv = coefficient_of_variation(comparison_values)
    pdi = proposed_pdi_v01(comparison_values)
    min_region = min(regional_means, key=regional_means.get)
    max_region = max(regional_means, key=regional_means.get)

    dates = sorted(by_date)
    first_mean = fmean(by_date[dates[0]])
    last_mean = fmean(by_date[dates[-1]])
    trend_percent = 0.0 if len(dates) == 1 else (last_mean - first_mean) / first_mean * 100.0

    cv_alert = cv >= cv_threshold
    pdi_alert = pdi >= pdi_threshold
    if cv_alert and pdi_alert:
        status = "PERLU_PRIORITAS"
    elif cv_alert or pdi_alert:
        status = "PERLU_PERHATIAN"
    else:
        status = "TERKENDALI"

    return {
        "commodity": next(iter(commodities.values())),
        "unit": next(iter(units.values())),
        "record_count": len(observations),
        "region_count": len(regional_means),
        "regional_mean_prices": {
            region: _round(value) for region, value in sorted(regional_means.items())
        },
        "mean_regional_price": _round(mean_price),
        "population_standard_deviation": _round(pstdev(comparison_values)),
        "cv_percent": _round(cv),
        "pdi_v01_percent": _round(pdi),
        "minimum_region": min_region,
        "maximum_region": max_region,
        "trend_percent": _round(trend_percent),
        "status": status,
        "alerts": {
            "cv": cv_alert,
            "pdi_v01": pdi_alert,
        },
        "thresholds": {
            "cv_percent": cv_threshold,
            "pdi_v01_percent": pdi_threshold,
            "classification": "illustrative_configuration",
        },
        "traceability": {
            "sources": sorted({item.source for item in observations}),
            "period_start": dates[0].isoformat(),
            "period_end": dates[-1].isoformat(),
        },
        "methodology": {
            "aggregation": "Rata-rata harga per wilayah, lalu perbandingan antarrata-rata wilayah",
            "cv": "simpangan baku populasi / rata-rata * 100%",
            "pdi_v01": "(harga wilayah maksimum - minimum) / rata-rata wilayah * 100%",
            "disclaimer": "PDI v0.1 adalah formula operasional usulan dalam draf HKI",
        },
    }
