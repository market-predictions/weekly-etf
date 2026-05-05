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

CANONICAL_ENGLISH_REPORT_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")


def matching_lane_artifact_path(report_path: Path) -> Path:
    stem = report_path.stem
    for prefix in ("weekly_analysis_pro_", "weekly_analysis_"):
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
            break
    return report_path.parent / "lane_reviews" / f"etf_lane_assessment_{stem}.json"


def validate_report_breadth_proof(md_text: str, report_path: Path) -> None:
    if "### Notable lanes assessed but not promoted this week" not in md_text:
        raise RuntimeError(
            "Breadth proof missing: report must include 'Notable lanes assessed but not promoted this week'."
        )

    artifact_path = matching_lane_artifact_path(report_path)
    if not artifact_path.exists():
        raise RuntimeError(
            f"Breadth artifact missing: expected matching lane assessment file at {artifact_path}."
        )

    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    if data.get("report_filename") != report_path.name:
        raise RuntimeError(
            f"Breadth artifact mismatch: artifact report_filename={data.get('report_filename')} but report is {report_path.name}."
        )

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

    challengers = [lane for lane in lanes if lane.get("challenger") is True]
    if len(challengers) < 4:
        raise RuntimeError(
            f"Breadth artifact incomplete: expected at least 4 challengers, found {len(challengers)}."
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
    validate_report_breadth_proof(latest.read_text(encoding="utf-8"), latest)
    print(f"BREADTH_OK | report={latest.name}")
