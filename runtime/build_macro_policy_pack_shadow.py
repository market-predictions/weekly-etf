from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from macro_regime.classify import classify_regime_shadow
from runtime import build_macro_policy_pack as legacy
from tools.validate_macro_policy_pack import _validate_pack
from tools.validate_macro_regime_shadow import validate_shadow_payload

REGIME_THRESHOLDS_PATH = Path("config/regime_thresholds.yml")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def add_shadow_regime(pack: dict[str, Any], relative_strength_path: Path, macro_data_audit_path: Path | None = None) -> dict[str, Any]:
    metrics = dict((_load_json(relative_strength_path).get("metrics") or {}))
    regime = pack.get("regime") or {}
    macro_data_audit = _load_json(macro_data_audit_path)
    shadow = classify_regime_shadow(
        metrics=metrics,
        macro_data_audit_summary=pack.get("macro_data_audit_summary") or {},
        macro_data_audit=macro_data_audit,
        thresholds=_load_yaml(REGIME_THRESHOLDS_PATH),
        legacy_regime=str(regime.get("current") or "Unknown"),
        legacy_confidence=float(regime.get("confidence") or 0.0),
    )
    shadow["threshold_config"] = str(REGIME_THRESHOLDS_PATH)
    validate_shadow_payload(shadow)
    out = dict(pack)
    out["deterministic_regime_shadow"] = shadow
    _validate_pack(out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--relative-strength", default=str(legacy.RS_PATH))
    parser.add_argument("--macro-context", default=str(legacy.MACRO_CONTEXT_PATH))
    parser.add_argument("--macro-data-audit", default=None)
    parser.add_argument("--output-dir", default=str(legacy.MACRO_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--reference-date", default=None)
    args = parser.parse_args()

    pricing_audit_path = Path(args.pricing_audit) if args.pricing_audit else legacy.latest_file(legacy.PRICING_DIR, "price_audit_*.json")
    pricing = legacy.load_json(pricing_audit_path)
    reference_date = args.reference_date or os.environ.get("REQUESTED_CLOSE_DATE") or str(pricing.get("requested_close_date") or datetime.now(timezone.utc).date().isoformat())
    run_id = args.run_id or os.environ.get("ETF_PRICING_RUN_ID") or os.environ.get("MRKT_RPRTS_RUN_ID") or _default_run_id()
    output_dir = Path(args.output_dir)
    macro_data_audit_path = legacy.resolve_macro_data_audit_path(args.macro_data_audit, reference_date=reference_date, run_id=run_id, output_dir=output_dir)
    pack = legacy.build_pack(pricing_audit_path, Path(args.relative_strength), Path(args.macro_context), macro_data_audit_path)
    pack = add_shadow_regime(pack, Path(args.relative_strength), macro_data_audit_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = str(pack.get("report_date", "unknown")).replace("-", "")
    out_path = output_dir / f"etf_macro_policy_pack_{suffix}_{run_id}.json"
    latest_path = output_dir / "latest.json"
    out_path.write_text(json.dumps(pack, indent=2, sort_keys=True), encoding="utf-8")
    latest_path.write_text(json.dumps(pack, indent=2, sort_keys=True), encoding="utf-8")

    memory = pack.get("regime_memory", {})
    audit_summary = pack.get("macro_data_audit_summary", {})
    shadow = pack.get("deterministic_regime_shadow", {})
    print(
        "ETF_MACRO_POLICY_PACK_OK | "
        f"report_date={pack.get('report_date')} | regime={pack.get('regime', {}).get('current')} | "
        f"shadow_regime={shadow.get('candidate_regime')} | shadow_confidence={shadow.get('candidate_confidence')} | "
        f"macro_axes={','.join(sorted((shadow.get('macro_axes') or {}).keys())) or 'none'} | "
        f"transition={memory.get('transition_state')} | weeks={memory.get('weeks_in_regime')} | "
        f"macro_audit_present={audit_summary.get('present')} | schema={pack.get('schema_version')} | output={out_path}"
    )


if __name__ == "__main__":
    main()
