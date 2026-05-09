from __future__ import annotations

import json
import re
from pathlib import Path

REQUIRED_BREADTH_BUCKETS = {
    "ai_digital_infrastructure",
    "defense_resilience",
    "grid_power_electrification",
    "uranium_nuclear",
    "agriculture_food_security",
    "water",
    "china",
    "india_regional_industrialization",
    "biotech_healthcare_innovation",
    "fintech_financial_infrastructure",
    "robotics_automation",
    "critical_minerals_materials",
}

DISCOVERY_REQUIRED_FIELDS = {
    "discovery_source",
    "novelty_status",
    "portfolio_gap_score",
    "pricing_confidence",
    "primary_price_status",
    "alternative_price_status",
    "evidence_summary",
    "why_now",
    "freshness_note",
}

CANONICAL_ENGLISH_REPORT_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
REPORT_STEM_RE = re.compile(r"^(?:weekly_analysis_pro_|weekly_analysis_)(\d{6})(?:_(\d{2}))?$")
LANE_ARTIFACT_RE = re.compile(r"^etf_lane_assessment_(\d{6})(?:_(\d{2}))?\.json$")


def report_date_version(report_path: Path) -> tuple[str, int]:
    match = REPORT_STEM_RE.match(report_path.stem)
    if not match:
        raise RuntimeError(f"Unsupported report filename for breadth artifact matching: {report_path.name}")
    return match.group(1), int(match.group(2) or "1")


def matching_lane_artifact_path(report_path: Path) -> Path:
    stem = report_path.stem
    for prefix in ("weekly_analysis_pro_", "weekly_analysis_"):
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
            break
    return report_path.parent / "lane_reviews" / f"etf_lane_assessment_{stem}.json"


def _artifact_date_version(path: Path) -> tuple[str, int] | None:
    match = LANE_ARTIFACT_RE.match(path.name)
    if not match:
        return None
    return match.group(1), int(match.group(2) or "1")


def _load_artifact(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def select_lane_artifact_path(report_path: Path) -> Path:
    exact = matching_lane_artifact_path(report_path)
    if exact.exists():
        return exact

    report_day, _report_version = report_date_version(report_path)
    lane_dir = report_path.parent / "lane_reviews"
    candidates: list[tuple[int, Path, dict]] = []
    for path in lane_dir.glob(f"etf_lane_assessment_{report_day}*.json"):
        parsed = _artifact_date_version(path)
        if not parsed:
            continue
        day, version = parsed
        if day != report_day:
            continue
        try:
            data = _load_artifact(path)
        except json.JSONDecodeError:
            continue
        if not data.get("discovery_engine_version") or not data.get("discovery_inputs"):
            continue
        candidates.append((version, path, data))

    if not candidates:
        raise RuntimeError(
            f"Breadth artifact missing: expected matching lane assessment file at {exact}, "
            f"and no valid same-day artifact was found for {report_day}."
        )

    candidates.sort(key=lambda item: item[0])
    return candidates[-1][1]


def validate_report_breadth_proof(md_text: str, report_path: Path) -> None:
    if "### Notable lanes assessed but not promoted this week" not in md_text:
        raise RuntimeError(
            "Breadth proof missing: report must include 'Notable lanes assessed but not promoted this week'."
        )

    artifact_path = select_lane_artifact_path(report_path)
    data = _load_artifact(artifact_path)

    artifact_report_filename = data.get("report_filename")
    if artifact_report_filename and artifact_report_filename != report_path.name:
        artifact_day, _artifact_version = _artifact_date_version(artifact_path) or (None, None)
        report_day, _report_version = report_date_version(report_path)
        if artifact_day != report_day:
            raise RuntimeError(
                f"Breadth artifact mismatch: artifact report_filename={artifact_report_filename} "
                f"but report is {report_path.name}, and artifact date does not match report date."
            )

    if not data.get("discovery_engine_version"):
        raise RuntimeError("Breadth artifact missing discovery_engine_version; lane discovery engine did not run.")
    if not data.get("discovery_inputs"):
        raise RuntimeError("Breadth artifact missing discovery_inputs; discovery provenance is unavailable.")

    lanes = data.get("assessed_lanes", [])
    if len(lanes) < len(REQUIRED_BREADTH_BUCKETS):
        raise RuntimeError(
            f"Breadth artifact incomplete: expected at least {len(REQUIRED_BREADTH_BUCKETS)} assessed lanes, found {len(lanes)}."
        )

    buckets = {lane.get("bucket") for lane in lanes if lane.get("bucket")}
    missing_buckets = REQUIRED_BREADTH_BUCKETS - buckets
    if missing_buckets:
        raise RuntimeError(
            "Breadth artifact incomplete: missing assessed lanes for required breadth buckets: "
            + ", ".join(sorted(missing_buckets))
        )

    for lane in lanes:
        missing_fields = [field for field in DISCOVERY_REQUIRED_FIELDS if field not in lane]
        if missing_fields:
            raise RuntimeError(
                f"Breadth artifact lane {lane.get('lane_name')} missing discovery fields: "
                + ", ".join(sorted(missing_fields))
            )

    challengers = [lane for lane in lanes if lane.get("challenger") is True]
    if len(challengers) < 4:
        raise RuntimeError(
            f"Breadth artifact incomplete: expected at least 4 challengers, found {len(challengers)}."
        )

    non_memory_challengers = [
        lane for lane in challengers
        if str(lane.get("novelty_status", "")).lower() not in {"retained", "retained_memory", "retained_under_review"}
    ]
    if len(non_memory_challengers) < 2:
        raise RuntimeError(
            f"Discovery artifact too static: expected at least 2 non-memory challengers, found {len(non_memory_challengers)}."
        )

    promoted = [lane for lane in lanes if lane.get("promoted_to_live_radar") is True]
    if not (5 <= len(promoted) <= 8):
        raise RuntimeError(
            f"Live radar size invalid: expected 5-8 promoted lanes, found {len(promoted)}."
        )


def latest_canonical_english_pro_report(output_dir: Path) -> Path:
    reports = sorted(
        path
        for path in output_dir.glob("weekly_analysis_pro_*.md")
        if CANONICAL_ENGLISH_REPORT_RE.match(path.name)
    )
    if not reports:
        raise RuntimeError("No canonical English ETF pro reports found in output/.")
    return reports[-1]


if __name__ == "__main__":
    output_dir = Path("output")
    latest = latest_canonical_english_pro_report(output_dir)
    artifact = select_lane_artifact_path(latest)
    validate_report_breadth_proof(latest.read_text(encoding="utf-8"), latest)
    print(f"BREADTH_OK | report={latest.name} | artifact={artifact.name}")
