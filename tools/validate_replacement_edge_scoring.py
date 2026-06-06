from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "replacement_edge_scoring_v1"
ARTIFACT_TYPE = "direct_challenger_vs_current_holding_scoring"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "artifact_type",
    "run_id",
    "created_at_utc",
    "inputs",
    "diagnostic_only",
    "portfolio_action_authority",
    "fundability_authority",
    "lane_scoring_authority",
    "funding_authority",
    "portfolio_mutation",
    "production_recommendation_authority",
    "edges",
}

REQUIRED_EDGE_FIELDS = {
    "current_holding",
    "challenger",
    "1m_relative_strength_edge",
    "3m_relative_strength_edge",
    "drawdown_edge",
    "volatility_edge",
    "replacement_edge_score",
    "diagnostic_only",
    "portfolio_action_authority",
    "fundability_authority",
    "lane_scoring_authority",
}

AUTHORITY_FALSE_FIELDS = {
    "portfolio_action_authority",
    "fundability_authority",
    "lane_scoring_authority",
    "funding_authority",
    "portfolio_mutation",
    "production_recommendation_authority",
}

EDGE_AUTHORITY_FALSE_FIELDS = {
    "portfolio_action_authority",
    "fundability_authority",
    "lane_scoring_authority",
}

NUMERIC_OR_NULL_FIELDS = {
    "1m_relative_strength_edge",
    "3m_relative_strength_edge",
    "drawdown_edge",
    "volatility_edge",
    "replacement_edge_score",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _require_non_empty_string(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"replacement edge scoring failed: {key} must be a non-empty string")


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"replacement edge scoring failed: {key} must remain false")


def _require_true(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not True:
        raise RuntimeError(f"replacement edge scoring failed: {key} must be true")


def _validate_edge(edge: dict[str, Any], index: int) -> None:
    missing = _missing(REQUIRED_EDGE_FIELDS, edge)
    if missing:
        raise RuntimeError(f"replacement edge scoring failed: edge[{index}] missing key(s): " + ", ".join(missing))
    for key in ("current_holding", "challenger"):
        _require_non_empty_string(edge, key)
    if edge["current_holding"] == edge["challenger"]:
        raise RuntimeError(f"replacement edge scoring failed: edge[{index}] compares a holding with itself")
    _require_true(edge, "diagnostic_only")
    for key in EDGE_AUTHORITY_FALSE_FIELDS:
        _require_false(edge, key)
    for key in NUMERIC_OR_NULL_FIELDS:
        value = edge.get(key)
        if value is not None and not isinstance(value, (int, float)):
            raise RuntimeError(f"replacement edge scoring failed: edge[{index}].{key} must be numeric or null")
    score = edge.get("replacement_edge_score")
    if score is not None and not -1.0 <= float(score) <= 1.0:
        raise RuntimeError(f"replacement edge scoring failed: edge[{index}].replacement_edge_score outside [-1, 1]")


def validate_replacement_edge_scoring(path: Path) -> None:
    payload = _load(path)
    missing = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing:
        raise RuntimeError("replacement edge scoring failed: missing top-level key(s): " + ", ".join(missing))
    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"replacement edge scoring failed: unsupported schema_version={payload['schema_version']}")
    if payload["artifact_type"] != ARTIFACT_TYPE:
        raise RuntimeError(f"replacement edge scoring failed: unsupported artifact_type={payload['artifact_type']}")
    for key in ("run_id", "created_at_utc"):
        _require_non_empty_string(payload, key)
    if not isinstance(payload["inputs"], dict):
        raise RuntimeError("replacement edge scoring failed: inputs must be an object")
    _require_true(payload, "diagnostic_only")
    for key in AUTHORITY_FALSE_FIELDS:
        _require_false(payload, key)
    if not isinstance(payload["edges"], list):
        raise RuntimeError("replacement edge scoring failed: edges must be a list")
    for index, edge in enumerate(payload["edges"]):
        if not isinstance(edge, dict):
            raise RuntimeError(f"replacement edge scoring failed: edge[{index}] must be an object")
        _validate_edge(edge, index)
    print(
        "REPLACEMENT_EDGE_SCORING_OK | "
        f"artifact={path} | edges={len(payload['edges'])} | diagnostic_only=true | "
        "portfolio_action_authority=false | fundability_authority=false | lane_scoring_authority=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_replacement_edge_scoring(Path(args.artifact))


if __name__ == "__main__":
    main()
