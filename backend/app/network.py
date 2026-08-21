"""Distribution-network validation and descriptive analytics."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from statistics import fmean
from typing import Iterable, Mapping, Sequence


REQUIRED_ROUTE_FIELDS = (
    "source_node",
    "target_node",
    "distance_km",
    "lead_time_hours",
    "frequency_per_week",
)


@dataclass(frozen=True, slots=True)
class DistributionRoute:
    source_node: str
    target_node: str
    distance_km: float
    lead_time_hours: float
    frequency_per_week: float
    mode: str = "tidak_ditentukan"
    active: bool = True

    @classmethod
    def from_mapping(cls, row: Mapping[str, object], row_number: int = 1) -> "DistributionRoute":
        missing = [field for field in REQUIRED_ROUTE_FIELDS if row.get(field) in (None, "")]
        if missing:
            raise ValueError(
                f"Rute {row_number}: kolom wajib kosong atau tidak tersedia: {', '.join(missing)}"
            )
        source = str(row["source_node"]).strip()
        target = str(row["target_node"]).strip()
        if not source or not target:
            raise ValueError(f"Rute {row_number}: simpul asal dan tujuan wajib diisi")
        if source.casefold() == target.casefold():
            raise ValueError(f"Rute {row_number}: simpul asal dan tujuan tidak boleh sama")

        numeric: dict[str, float] = {}
        for field in ("distance_km", "lead_time_hours", "frequency_per_week"):
            try:
                numeric[field] = float(row[field])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Rute {row_number}: {field} harus berupa angka") from exc
            if numeric[field] <= 0:
                raise ValueError(f"Rute {row_number}: {field} harus lebih besar dari nol")

        active_value = row.get("active", True)
        if isinstance(active_value, str):
            active = active_value.strip().casefold() not in {"0", "false", "tidak", "nonaktif"}
        else:
            active = bool(active_value)
        return cls(
            source_node=source,
            target_node=target,
            distance_km=numeric["distance_km"],
            lead_time_hours=numeric["lead_time_hours"],
            frequency_per_week=numeric["frequency_per_week"],
            mode=str(row.get("mode", "tidak_ditentukan")).strip() or "tidak_ditentukan",
            active=active,
        )


def parse_distribution_routes(rows: Iterable[Mapping[str, object]]) -> list[DistributionRoute]:
    routes = [
        DistributionRoute.from_mapping(row, row_number=index)
        for index, row in enumerate(rows, start=1)
    ]
    if not routes:
        raise ValueError("Analisis jaringan memerlukan sedikitnya satu rute")
    return routes


def _components(nodes: set[str], adjacency: Mapping[str, set[str]]) -> list[list[str]]:
    unseen = set(nodes)
    components: list[list[str]] = []
    while unseen:
        start = min(unseen)
        queue: deque[str] = deque([start])
        unseen.remove(start)
        component: list[str] = []
        while queue:
            node = queue.popleft()
            component.append(node)
            for neighbor in sorted(adjacency[node]):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return components


def analyze_distribution_network(routes: Sequence[DistributionRoute]) -> dict[str, object]:
    active_routes = [route for route in routes if route.active]
    if not active_routes:
        raise ValueError("Tidak ada rute aktif untuk dianalisis")

    adjacency: dict[str, set[str]] = defaultdict(set)
    in_degree: dict[str, int] = defaultdict(int)
    out_degree: dict[str, int] = defaultdict(int)
    nodes: set[str] = set()
    for route in active_routes:
        nodes.update((route.source_node, route.target_node))
        adjacency[route.source_node].add(route.target_node)
        adjacency[route.target_node].add(route.source_node)
        out_degree[route.source_node] += 1
        in_degree[route.target_node] += 1

    components = _components(nodes, adjacency)
    node_metrics = {
        node: {
            "in_degree": in_degree[node],
            "out_degree": out_degree[node],
            "total_degree": in_degree[node] + out_degree[node],
        }
        for node in sorted(nodes)
    }
    low_connectivity = [
        node for node, values in node_metrics.items() if values["total_degree"] <= 1
    ]
    total_frequency = sum(route.frequency_per_week for route in active_routes)
    weighted_lead_time = (
        sum(route.lead_time_hours * route.frequency_per_week for route in active_routes)
        / total_frequency
    )
    warnings: list[str] = []
    if len(components) > 1:
        warnings.append("Jaringan aktif terdiri atas lebih dari satu komponen")
    if low_connectivity:
        warnings.append("Terdapat simpul berkonektivitas rendah yang perlu ditinjau")
    if any(route.frequency_per_week <= 1 for route in active_routes):
        warnings.append("Terdapat rute dengan frekuensi satu kali per minggu atau kurang")

    return {
        "active_route_count": len(active_routes),
        "inactive_route_count": len(routes) - len(active_routes),
        "node_count": len(nodes),
        "component_count": len(components),
        "components": components,
        "total_distance_km": round(sum(route.distance_km for route in active_routes), 4),
        "mean_lead_time_hours": round(
            fmean(route.lead_time_hours for route in active_routes), 4
        ),
        "frequency_weighted_lead_time_hours": round(weighted_lead_time, 4),
        "total_frequency_per_week": round(total_frequency, 4),
        "modes": sorted({route.mode for route in active_routes}),
        "node_metrics": node_metrics,
        "low_connectivity_nodes": low_connectivity,
        "warnings": warnings,
        "methodology": {
            "network_type": "directed distribution network with weak-connectivity check",
            "degree": "jumlah hubungan masuk dan keluar per simpul",
            "lead_time": "rata-rata sederhana dan rata-rata berbobot frekuensi",
            "scope": "analisis deskriptif, bukan optimasi rute atau rekomendasi kebijakan",
        },
    }
