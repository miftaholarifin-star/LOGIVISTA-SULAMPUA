"""Pydantic request models for the HTTP API."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    implementation_status: str


class PriceObservationInput(BaseModel):
    source: str = Field(min_length=1, max_length=120)
    date: date
    region: str = Field(min_length=1, max_length=120)
    commodity: str = Field(min_length=1, max_length=120)
    unit: str = Field(min_length=1, max_length=40)
    price: float = Field(gt=0)

    def to_mapping(self) -> dict[str, object]:
        return {
            "source": self.source,
            "date": self.date.isoformat(),
            "region": self.region,
            "commodity": self.commodity,
            "unit": self.unit,
            "price": self.price,
        }


class PriceAnalysisRequest(BaseModel):
    observations: list[PriceObservationInput] = Field(min_length=2, max_length=10_000)
    cv_threshold: float | None = Field(default=None, ge=0)
    pdi_threshold: float | None = Field(default=None, ge=0)
    persist: bool = False


class DistributionRouteInput(BaseModel):
    source_node: str = Field(min_length=1, max_length=120)
    target_node: str = Field(min_length=1, max_length=120)
    distance_km: float = Field(gt=0)
    lead_time_hours: float = Field(gt=0)
    frequency_per_week: float = Field(gt=0)
    mode: str = Field(default="tidak_ditentukan", min_length=1, max_length=60)
    active: bool = True

    def to_mapping(self) -> dict[str, object]:
        return self.model_dump()


class NetworkAnalysisRequest(BaseModel):
    routes: list[DistributionRouteInput] = Field(min_length=1, max_length=10_000)
    persist: bool = False
