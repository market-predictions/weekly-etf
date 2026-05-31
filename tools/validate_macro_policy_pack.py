from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path("schemas/macro_policy_pack.schema.json")
DEFAULT_PACK_PATH = Path("output/macro/latest.json")
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "generated_at_utc",
    "report_date",
    "source_files",
    "authority",
    "macro_data_audit_summary",
    "regime",
    "confidence_decomposition",
    "central_banks",
    "macro_signals",
    "policy_catalysts",
    "cross_asset_confirmation",
    "portfolio_implications",
    "lane_adjustments",
    "active_drivers",
    "regime_memory",
    "report_transfer",
}
REQUIRED_SOURCE_FILES = {"pricing_audit", "relative_strength", "macro_context", "macro_data_audit"}
REQUIRED_CENTRAL_BANKS = {"fed", "ecb", "boe", "boj", "pboc"}
ALLOWED_MACRO_AUDIT_IMPACT = {"none_phase2_audit_only"}
ALLOWED_AUTHORITY_IMPACT = {"legacy_lane_adjustments_only"}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required JSON file is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _num(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"{label} must be numeric") from exc


def _validate_authority(pack: dict[str, Any]) -> None:
    authority = pack.get("authority") or {}
    for key in ("decision_framework", "input_state_contract", "output_contract", "operational_runbook"):
        _require(isinstance(authority.get(key), str) and authority.get(key).strip(), f"authority.{key} is required")
    _require(authority.get("shadow_only") is True, "authority.shadow_only must be true")
    _require(authority.get("client_facing_authority") is False, "authority.client_facing_authority must be false")
    _require(authority.get("decision_impact") in ALLOWED_AUTHORITY_IMPACT, "authority.decision_impact is invalid")


def _validate_macro_audit_summary(pack: dict[str, Any]) -> None:
    summary = pack.get("macro_data_audit_summary") or {}
    for key in ("present", "status", "mode", "reference_date", "observation_count", "shadow_only", "client_facing_authority", "decision_impact"):
        _require(key in summary, f"macro_data_audit_summary.{key} is required")
    _require(isinstance(summary.get("present"), bool), "macro_data_audit_summary.present must be boolean")
    _require(summary.get("shadow_only") is True, "macro_data_audit_summary.shadow_only must be true")
    _require(summary.get("client_facing_authority") is False, "macro_data_audit_summary.client_facing_authority must be false")
    _require(summary.get("decision_impact") in ALLOWED_MACRO_AUDIT_IMPACT, "macro_data_audit_summary.decision_impact is invalid")
    if summary.get("present") is True:
        _require(summary.get("status") == "passed", "present macro data audit must have status=passed")
        _require(summary.get("mode") in {"live", "fixture"}, "present macro data audit mode must be live or fixture")
        _require(isinstance(summary.get("observation_count"), int) and summary.get("observation_count") > 0, "present macro audit needs positive observation_count")
    else:
        _require(summary.get("mode") in {"none", None}, "absent macro audit mode must be none/null")
        _require(summary.get("observation_count") in {0, None}, "absent macro audit observation_count must be 0/null")


def _validate_regime(pack: dict[str, Any]) -> None:
    regime = pack.get("regime") or {}
    for key in ("current", "previous", "confidence", "confidence_source", "what_changed"):
        _require(key in regime, f"regime.{key} is required")
    _require(isinstance(regime.get("current"), str) and regime.get("current").strip(), "regime.current must be non-empty")
    confidence = _num(regime.get("confidence"), "regime.confidence")
    _require(0 <= confidence <= 1, "regime.confidence must be between 0 and 1")
    _require(regime.get("confidence_source") in {"legacy_proxy_static", "shadow_deterministic_candidate"}, "regime.confidence_source is invalid")
    _require(isinstance(regime.get("what_changed"), list), "regime.what_changed must be a list")


def _validate_confidence_decomposition(pack: dict[str, Any]) -> None:
    payload = pack.get("confidence_decomposition") or {}
    for key in ("method", "shadow_only", "client_facing_authority", "decision_impact", "components", "notes"):
        _require(key in payload, f"confidence_decomposition.{key} is required")
    _require(payload.get("shadow_only") is True, "confidence_decomposition.shadow_only must be true")
    _require(payload.get("client_facing_authority") is False, "confidence_decomposition.client_facing_authority must be false")
    _require(payload.get("decision_impact") == "none_shadow_explanation_only", "confidence_decomposition.decision_impact is invalid")
    _require(isinstance(payload.get("components"), dict), "confidence_decomposition.components must be an object")
    _require(isinstance(payload.get("notes"), list), "confidence_decomposition.notes must be a list")


def _validate_central_banks(pack: dict[str, Any]) -> None:
    banks = pack.get("central_banks") or {}
    missing = sorted(REQUIRED_CENTRAL_BANKS - set(banks))
    _require(not missing, "central_banks missing required keys: " + ", ".join(missing))
    for key, payload in banks.items():
        _require(isinstance(payload, dict), f"central_banks.{key} must be an object")
        for field in ("stance", "likely_direction", "main_risk", "etf_implication", "confidence"):
            _require(field in payload, f"central_banks.{key}.{field} is required")
        confidence = _num(payload.get("confidence"), f"central_banks.{key}.confidence")
        _require(0 <= confidence <= 1, f"central_banks.{key}.confidence must be between 0 and 1")


def _validate_lane_adjustments(pack: dict[str, Any]) -> None:
    adjustments = pack.get("lane_adjustments") or {}
    _require(isinstance(adjustments, dict) and adjustments, "lane_adjustments must be a non-empty object for backward compatibility")
    for lane, payload in adjustments.items():
        _require(isinstance(payload, dict), f"lane_adjustments.{lane} must be an object")
        _require("score_adjustment" in payload, f"lane_adjustments.{lane}.score_adjustment is required")
        score = _num(payload.get("score_adjustment"), f"lane_adjustments.{lane}.score_adjustment")
        _require(-0.20 <= score <= 0.20, f"lane_adjustments.{lane}.score_adjustment must be within [-0.20, 0.20]")
        _require(isinstance(payload.get("reason"), str) and payload.get("reason").strip(), f"lane_adjustments.{lane}.reason is required")


def _validate_active_drivers(pack: dict[str, Any]) -> None:
    drivers = pack.get("active_drivers")
    _require(isinstance(drivers, list), "active_drivers must be a list")
    seen: set[str] = set()
    for index, driver in enumerate(drivers):
        _require(isinstance(driver, dict), f"active_drivers[{index}] must be an object")
        for key in ("driver_id", "status", "source", "shadow_only", "client_facing_authority", "decision_impact"):
            _require(key in driver, f"active_drivers[{index}].{key} is required")
        driver_id = str(driver.get("driver_id") or "").strip()
        _require(bool(driver_id), f"active_drivers[{index}].driver_id is empty")
        _require(driver_id not in seen, f"duplicate active driver id: {driver_id}")
        seen.add(driver_id)
        _require(driver.get("shadow_only") is True, f"active_drivers[{index}].shadow_only must be true")
        _require(driver.get("client_facing_authority") is False, f"active_drivers[{index}].client_facing_authority must be false")
        _require(str(driver.get("decision_impact")) == "none_wp9_not_promoted", f"active_drivers[{index}].decision_impact is invalid")


def _validate_pack(pack: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED_TOP_LEVEL - set(pack))
    _require(not missing, "macro policy pack missing top-level fields: " + ", ".join(missing))
    _require(pack.get("schema_version") == "1.0", "macro policy pack schema_version must be 1.0")
    source_files = pack.get("source_files") or {}
    missing_source_files = sorted(REQUIRED_SOURCE_FILES - set(source_files))
    _require(not missing_source_files, "source_files missing keys: " + ", ".join(missing_source_files))
    _require(isinstance(source_files.get("pricing_audit"), str) and source_files.get("pricing_audit"), "source_files.pricing_audit is required")
    _require(isinstance(source_files.get("relative_strength"), str) and source_files.get("relative_strength"), "source_files.relative_strength is required")
    _validate_authority(pack)
    _validate_macro_audit_summary(pack)
    _validate_regime(pack)
    _validate_confidence_decomposition(pack)
    _validate_central_banks(pack)
    _validate_lane_adjustments(pack)
    _validate_active_drivers(pack)
    _require(isinstance(pack.get("policy_catalysts"), list), "policy_catalysts must be a list")
    _require(isinstance(pack.get("cross_asset_confirmation"), list), "cross_asset_confirmation must be a list")
    _require(isinstance(pack.get("portfolio_implications"), list), "portfolio_implications must be a list")
    _require(isinstance(pack.get("regime_memory"), dict), "regime_memory must be an object")
    return {
        "report_date": pack.get("report_date"),
        "regime": (pack.get("regime") or {}).get("current"),
        "confidence": (pack.get("regime") or {}).get("confidence"),
        "lane_adjustments": len(pack.get("lane_adjustments") or {}),
        "active_drivers": len(pack.get("active_drivers") or []),
        "macro_audit_present": (pack.get("macro_data_audit_summary") or {}).get("present"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Weekly ETF macro policy pack schema/compatibility contract.")
    parser.add_argument("--pack", default=str(DEFAULT_PACK_PATH))
    parser.add_argument("--schema", default=str(SCHEMA_PATH))
    args = parser.parse_args()

    schema_path = Path(args.schema)
    _require(schema_path.exists(), f"Macro policy pack schema is missing: {schema_path}")
    _load_json(schema_path)
    pack = _load_json(Path(args.pack))
    result = _validate_pack(pack)
    print(
        "ETF_MACRO_POLICY_PACK_SCHEMA_OK | "
        f"report_date={result['report_date']} | regime={result['regime']} | "
        f"confidence={result['confidence']} | lane_adjustments={result['lane_adjustments']} | "
        f"active_drivers={result['active_drivers']} | macro_audit_present={result['macro_audit_present']}"
    )


if __name__ == "__main__":
    main()
