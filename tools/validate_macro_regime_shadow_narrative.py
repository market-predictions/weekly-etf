from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "macro_regime_shadow_narrative_v1"
ALLOWED_STATUS = {"shadow_candidate_only"}
REQUIRED_FALSE_FLAGS = {
    "client_facing",
    "production_report",
    "portfolio_action_authority",
    "lane_scoring_authority",
    "fundability_authority",
}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "artifact_type",
    "run_id",
    "created_at_utc",
    "report_date",
    "status",
    "shadow_only",
    "authority",
    "inputs",
    "current_macro_narrative",
    "deterministic_regime_shadow_narrative_candidate",
    "comparison_markdown",
    "blockers",
    *REQUIRED_FALSE_FLAGS,
}
FORBIDDEN_TOP_LEVEL_KEYS = {
    "portfolio_action",
    "trade_instruction",
    "lane_score",
    "fundability_decision",
    "client_distribution",
    "production_report_path",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("macro regime shadow narrative failed: artifact must be a JSON object")
    return payload


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _require_non_empty_string(payload: dict[str, Any], key: str) -> None:
    if not isinstance(payload.get(key), str) or not payload[key].strip():
        raise RuntimeError(f"macro regime shadow narrative failed: {key} must be a non-empty string")


def _require_false_mapping(mapping: dict[str, Any], *, prefix: str = "") -> None:
    for key in REQUIRED_FALSE_FLAGS:
        if mapping.get(key) is not False:
            name = f"{prefix}{key}" if prefix else key
            raise RuntimeError(f"macro regime shadow narrative failed: {name} must remain false")


def validate_macro_regime_shadow_narrative(path: Path) -> None:
    payload = _load(path)
    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(f"macro regime shadow narrative failed: missing top-level key(s): {', '.join(missing_top)}")

    forbidden = sorted(FORBIDDEN_TOP_LEVEL_KEYS & set(payload))
    if forbidden:
        raise RuntimeError(f"macro regime shadow narrative failed: forbidden production/action key(s): {', '.join(forbidden)}")

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"macro regime shadow narrative failed: unsupported schema_version={payload['schema_version']}")
    if payload["status"] not in ALLOWED_STATUS:
        raise RuntimeError(f"macro regime shadow narrative failed: unsupported status={payload['status']}")
    if payload["shadow_only"] is not True:
        raise RuntimeError("macro regime shadow narrative failed: shadow_only must remain true")

    _require_false_mapping(payload)
    authority = payload["authority"]
    if not isinstance(authority, dict):
        raise RuntimeError("macro regime shadow narrative failed: authority must be an object")
    missing_authority = _missing(REQUIRED_FALSE_FLAGS, authority)
    if missing_authority:
        raise RuntimeError(
            f"macro regime shadow narrative failed: authority missing required key(s): {', '.join(missing_authority)}"
        )
    _require_false_mapping(authority, prefix="authority.")

    for key in ("run_id", "report_date", "created_at_utc"):
        _require_non_empty_string(payload, key)

    current = payload["current_macro_narrative"]
    if not isinstance(current, dict) or not {"en", "nl"} <= set(current):
        raise RuntimeError("macro regime shadow narrative failed: current_macro_narrative must include en and nl")

    candidate = payload["deterministic_regime_shadow_narrative_candidate"]
    if not isinstance(candidate, dict) or not {"en", "nl"} <= set(candidate):
        raise RuntimeError(
            "macro regime shadow narrative failed: deterministic_regime_shadow_narrative_candidate must include en and nl"
        )

    for language in ("en", "nl"):
        text = candidate[language]
        if not isinstance(text, str) or "SHADOW-ONLY" not in text:
            raise RuntimeError(f"macro regime shadow narrative failed: {language} candidate must clearly state SHADOW-ONLY")
        for boundary in REQUIRED_FALSE_FLAGS:
            if f"{boundary}=false" not in text:
                raise RuntimeError(f"macro regime shadow narrative failed: {language} candidate missing {boundary}=false boundary")

    comparison = payload["comparison_markdown"]
    if not isinstance(comparison, str) or "SHADOW-ONLY" not in comparison:
        raise RuntimeError("macro regime shadow narrative failed: comparison_markdown must state SHADOW-ONLY")
    for marker in ("Current macro narrative", "Deterministic regime shadow narrative candidate"):
        if marker not in comparison:
            raise RuntimeError("macro regime shadow narrative failed: comparison_markdown must compare current and deterministic narratives")

    blockers = payload["blockers"]
    if not isinstance(blockers, list) or not blockers:
        raise RuntimeError("macro regime shadow narrative failed: blockers must be a non-empty list")
    for boundary in REQUIRED_FALSE_FLAGS:
        if f"{boundary}=false" not in blockers:
            raise RuntimeError(f"macro regime shadow narrative failed: blockers missing {boundary}=false")

    print(
        "MACRO_REGIME_SHADOW_NARRATIVE_OK | "
        f"artifact={path} | client_facing=false | production_report=false | "
        "portfolio_action_authority=false | lane_scoring_authority=false | fundability_authority=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_macro_regime_shadow_narrative(Path(args.artifact))


if __name__ == "__main__":
    main()
