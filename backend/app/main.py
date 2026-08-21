"""FastAPI application for LOGIVISTA SULAMPUA v0.1.0."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .analytics import analyze_prices, parse_price_observations
from .config import settings
from .database import AnalysisStore
from .models import HealthResponse, NetworkAnalysisRequest, PriceAnalysisRequest
from .network import analyze_distribution_network, parse_distribution_routes


PRIORITY_COMMODITIES = (
    "Beras medium",
    "Gula pasir",
    "Minyak goreng",
    "Telur ayam ras",
    "Daging ayam ras",
    "Cabai",
    "Bawang merah",
)

app = FastAPI(
    title="LOGIVISTA SULAMPUA API",
    description=(
        "Implementasi referensi analitik visibilitas jaringan distribusi dan "
        "disparitas harga komoditas antarpulau. Cakupan awal: Halmahera Barat."
    ),
    version=__version__,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
store = AnalysisStore(settings.database_path)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="LOGIVISTA SULAMPUA API",
        version=__version__,
        implementation_status="reference_prototype",
    )


@app.get("/api/v1/commodities", tags=["master-data"])
def commodities() -> dict[str, object]:
    return {
        "initial_region": "Kabupaten Halmahera Barat",
        "commodities": list(PRIORITY_COMMODITIES),
        "coverage_note": "Sulampua adalah arah pengembangan, bukan klaim cakupan operasional saat ini",
    }


@app.get("/api/v1/methodology", tags=["methodology"])
def methodology() -> dict[str, object]:
    return {
        "version": "0.1",
        "cv": "simpangan baku populasi harga rata-rata wilayah / rata-rata * 100%",
        "pdi_v01": "(maksimum - minimum) / rata-rata harga wilayah * 100%",
        "status": "PDI v0.1 merupakan formula operasional usulan yang perlu diratifikasi",
        "default_thresholds": {
            "cv_percent": settings.cv_warning_threshold,
            "pdi_v01_percent": settings.pdi_warning_threshold,
            "classification": "illustrative_configuration",
        },
    }


@app.post("/api/v1/analysis/prices", tags=["analytics"])
def price_analysis(payload: PriceAnalysisRequest) -> dict[str, object]:
    try:
        observations = parse_price_observations(
            item.to_mapping() for item in payload.observations
        )
        result = analyze_prices(
            observations,
            cv_threshold=(
                settings.cv_warning_threshold
                if payload.cv_threshold is None
                else payload.cv_threshold
            ),
            pdi_threshold=(
                settings.pdi_warning_threshold
                if payload.pdi_threshold is None
                else payload.pdi_threshold
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if payload.persist:
        result["batch_id"] = store.save_price_batch(observations)
        result["analysis_id"] = store.save_analysis("price_disparity", result)
    return result


@app.post("/api/v1/analysis/network", tags=["analytics"])
def network_analysis(payload: NetworkAnalysisRequest) -> dict[str, object]:
    try:
        routes = parse_distribution_routes(item.to_mapping() for item in payload.routes)
        result = analyze_distribution_network(routes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if payload.persist:
        result["analysis_id"] = store.save_analysis("distribution_network", result)
    return result


@app.get("/api/v1/audit", tags=["traceability"])
def audit(limit: int = Query(default=50, ge=1, le=200)) -> list[dict[str, object]]:
    return store.list_audit(limit)
