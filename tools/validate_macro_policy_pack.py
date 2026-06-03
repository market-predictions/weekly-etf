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
    "field_authority",
    "promotion_gates",
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
REQUIRED_FIELD_AUTHORITY = {
    "regime",
    "confidence_decomposition",
    "central_banks",
    "macro_signals",
    "policy_catalysts",
    "portfolio_implications",
    "lane_adjustments",
    "macro_data_audit_summary",
    "deterministic_regime_shadow",
    "active_drivers",
    "report_transfer",
}
ALLOWED_MACRO_AUDIT_IMPACT = {"none_phase2_audit_only"}
ALLOWED_AUTHORITY_IMPACT = {"legacy_lane_adjustments_only"}
ALLOWED_AUTHORITY_CLASS = {"legacy_compatibility_pack"}
ALLOWED_DECISION_AUTHORITY = {"legacy_lane_adjustments_only"}
CLIENT_SURFACE_ALLOWED_FIELDS = {"regime", "central_banks", "policy_catalysts", "portfolio_implications", "report_transfer"}
CLIENT_SURFACE_BLOCKED_FIELDS = {"confidence_decomposition", "macro_signals", "lane_adjustments", "macro_data_audit_summary", "deterministic_regime_shadow", "active_drivers"}
DECISION_AUTHORITY_BY_FIELD = {
    "regime": "descriptive_only",
    "confidence_decomposition": "none_shadow_explanation_only",
    "central_banks": "descriptive_only",
    "macro_signals": "none_internal_evidence_only",
    "policy_catalysts": "descriptive_only",
    "portfolio_implications": "descriptive_only",
    "lane_adjustments": "legacy_lane_adjustments_only",
    "macro_data_audit_summary": "none_phase2_audit_only",
    "deterministic_regime_shadow": "none_shadow_comparison_only",
    "active_drivers": "none_wp9_not_promoted",
    "report_transfer": "output_contract_only",
}
PROMOTION_BLOCKED_AUTHORITY = {
    "raw_macro_axes_client_surface",
    "raw_macro_axis_scores_client_surface",
    "deterministic_regime_shadow_client_surface",
    "stage1_thesis_candidates_client_surface",
    "macro_direct_lane_scoring_authority",
    "macro_direct_fundability_authority",
    "macro_direct_portfolio_trade_authority",
}
PROMOTION_REQUIRED_GATES = {
    "macro_policy_pack_schema_contract_green",
    "deterministic_regime_fixture_replay_green",
    "macro_audit_fixture_replay_green",
    "macro_compliance_validator_green",
    "bilingual_report_surface_validation_green",
    "production_report_validation_green",
    "explicit_control_layer_promotion_decision",
}


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
    for key in ("authority_class", "client_surface_allowed", "decision_authority", "decision_framework", "input_state_contract", "output_contract", "operational_runbook"):
        _require(key in authority, f"authority.{key} is required")
    for key in ("decision_framework", "input_state_contract", "output_contract", "operational_runbook"):
        _require(isinstance(authority.get(key), str) and authority.get(key).strip(), f"authority.{key} is required")
    _require(authority.get("authority_class") in ALLOWED_AUTHORITY_CLASS, "authority.authority_class is invalid")
    _require(authority.get("client_surface_allowed") is True, "authority.client_surface_allowed must be true for the client-safe descriptive surface")
    _require(authority.get("decision_authority") in ALLOWED_DECISION_AUTHORITY, "authority.decision_authority is invalid")
    _require(authority.get("shadow_only") is True, "authority.shadow_only must be true")
    _require(authority.get("client_facing_authority") is False, "authority.client_facing_authority must be false")
    _require(authority.get("decision_impact") in ALLOWED_AUTHORITY_IMPACT, "authority.decision_impact is invalid")


def _validate_field_authority(pack: dict[str, Any]) -> None:
    payload = pack.get("field_authority") or {}
    _require(isinstance(payload, dict), "field_authority must be an object")
    missing = sorted(REQUIRED_FIELD_AUTHORITY - set(payload))
    _require(not missing, "field_authority missing required fields: " + ", ".join(missing))
    extras = sorted(set(payload) - REQUIRED_FIELD_AUTHORITY)
    _require(not extras, "field_authority has unsupported fields: " + ", ".join(extras))
    for field, authority in payload.items():
        _require(isinstance(authority, dict), f"field_authority.{field} must be an object")
        for key in ("authority_class", "client_surface_allowed", "decision_authority"):
            _require(key in authority, f"field_authority.{field}.{key} is required")
        _require(isinstance(authority.get("authority_class"), str) and authority.get("authority_class").strip(), f"field_authority.{field}.authority_class is required")
        _require(authority.get("decision_authority") == DECISION_AUTHORITY_BY_FIELD[field], f"field_authority.{field}.decision_authority is invalid")
        expected_surface = field in CLIENT_SURFACE_ALLOWED_FIELDS
        _require(authority.get("client_surface_allowed") is expected_surface, f"field_authority.{field}.client_surface_allowed must be {expected_surface}")
        if field in CLIENT_SURFACE_BLOCKED_FIELDS:
            _require(authority.get("client_surface_allowed") is False, f"field_authority.{field} must not be client-surface allowed")
        if "notes" in authority:
            _require(isinstance(authority.get("notes"), list), f"field_authority.{field}.notes must be a list")


def _validate_promotion_gates(pack: dict[str, Any]) -> None:
    gates = pack.get("promotion_gates") or {}
    _require(isinstance(gates, dict), "promotion_gates must be an object")
    _require(gates.get("status") == "not_promoted", "promotion_gates.status must remain not_promoted")
    _require(gates.get("client_surface_status") == "descriptive_surface_only", "promotion_gates.client_surface_status is invalid")
    _require(gates.get("decision_authority_status") == "legacy_lane_adjustments_only", "promotion_gates.decision_authority_status is invalid")
    required = set(gates.get("required_before_decision_authority") or [])
    blocked = set(gates.get("blocked_authority") or [])
    _require(PROMOTION_REQUIRED_GATES <= required, "promotion_gates.required_before_decision_authority is missing required gates")
    _require(PROMOTION_BLOCKED_AUTHORITY <= blocked, "promotion_gates.blocked_authority is missing required blockers")


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


def _validate_shadow_promotion_firewall(pack: dict[str, Any]) -> None:
    shadow = pack.get("deterministic_regime_shadow")
    if shadow is None:
        return
    _require(isinstance(shadow, dict), "deterministic_regime_shadow must be an object when present")
    field_authority = (pack.get("field_authority") or {}).get("deterministic_regime_shadow") or {}
    _require(field_authority.get("client_surface_allowed") is False, "deterministic_regime_shadow must not be client-surface allowed")
    _require(field_authority.get("decision_authority") == "none_shadow_comparison_only", "deterministic_regime_shadow decision authority must remain none_shadow_comparison_only")
    _require(shadow.get("shadow_only") is True, "deterministic_regime_shadow.shadow_only must be true")
    _require(shadow.get("client_facing_authority") is False, "deterministic_regime_shadow.client_facing_authority must be false")
    _require(shadow.get("decision_impact") == "none_shadow_comparison_only", "deterministic_regime_shadow.decision_impact must remain none_shadow_comparison_only")


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
    _validate_field_authority(pack)
    _validate_promotion_gates(pack)
    _validate_macro_audit_summary(pack)
    _validate_regime(pack)
    _validate_confidence_decomposition(pack)
    _validate_central_banks(pack)
    _validate_lane_adjustments(pack)
    _validate_active_drivers(pack)
    _validate_shadow_promotion_firewall(pack)
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
        "promotion_status": (pack.get("promotion_gates") or {}).get("status"),
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
        f"active_drivers={result['active_drivers']} | macro_audit_present={result['macro_audit_present']} | "
        f"promotion_status={result['promotion_status']}"
    )


if __name__ == "__main__":
    main()
