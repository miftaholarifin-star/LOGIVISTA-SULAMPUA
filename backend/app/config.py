"""Environment-based configuration for the reference implementation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} harus berupa angka") from exc
    if value < 0:
        raise ValueError(f"{name} tidak boleh negatif")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: Path
    cv_warning_threshold: float
    pdi_warning_threshold: float
    allowed_origins: tuple[str, ...]


def load_settings() -> Settings:
    origins = tuple(
        item.strip()
        for item in os.getenv("ALLOWED_ORIGINS", "http://localhost:5500").split(",")
        if item.strip()
    )
    return Settings(
        database_path=Path(os.getenv("DATABASE_PATH", "logivista.db")),
        cv_warning_threshold=_float_env("CV_WARNING_THRESHOLD", 10.0),
        pdi_warning_threshold=_float_env("PDI_WARNING_THRESHOLD", 15.0),
        allowed_origins=origins,
    )


settings = load_settings()
