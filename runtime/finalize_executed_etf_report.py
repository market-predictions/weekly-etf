from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from runtime.build_etf_report_state import build_runtime_state
from runtime.render_etf_report_from_state import render_en, render_nl

RUNTIME_DIR = Path("output/runtime")
AUTHORITY_FIELDS = {
    "shares",
    "current_price_local",
    "previous_price_local",
    "continuity_current_price_local",
    "currency",
    "market_value_local",
    "previous_market_value_local",
    "market_value_eur",
    "previous_market_value_eur",
    "current_weight_pct",
    "previous_weight_pct",
    "weight_inherited_pct",
    "target_weight_pct",
    "shares_delta_this_run",
    "weight_change_pct",
    "action_executed_this_run",
    "funding_source_note",
    "pricing_source",
    "pricing_status",
    "pricing_tier",
    "pricing_close_type",
    "price_date",
    "selected_close",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _market_value_eur(row: dict[str, Any]) -> float:
    return _float(row.get("market_value_eur") if row.get("market_value_eur") not in (None, "") else row.get("previous_market_value_eur"))


def _executed_model_changes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    rows = ((artifact.get("guarded_auto_result") or {}).get("official_ledger_rows") or [])
    out: list[dict[str, Any]] = []
    for row in rows:
        ticker = _ticker(row.get("ticker"))
        if not ticker:
            continue
        out.append({
            "ticker": ticker,
            "action": str(row.get("action") or "None").strip(),
            "shares_delta": _float(row.get("shares_delta")),
            "previous_weight_pct": _float(row.get("previous_weight_pct")),
            "new_weight_pct": _float(row.get("new_weight_pct")),
            "weight_change_pct": _float(row.get("weight_change_pct")),
            "target_weight_pct": _float(row.get("target_weight_pct")),
            "funding_source_note": str(row.get("funding_source_note") or "Guarded model rotation executed and persisted.").strip(),
            "trade_date": row.get("trade_date"),
            "trade_id": row.get("trade_id"),
        })
    return out


def _overlay_executed_portfolio_authority(final_state: dict[str, Any], portfolio_state_path: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    if not portfolio_state_path.exists():
        return final_state
    portfolio_state = _read_json(portfolio_state_path)
    changes = _executed_model_changes(artifact)
    change_by_ticker = {row["ticker"]: row for row in changes}
    final_by_ticker = {_ticker(row.get("ticker")): dict(row) for row in final_state.get("positions", []) or [] if _ticker(row.get("ticker"))}
    positions: list[dict[str, Any]] = []
    for official in portfolio_state.get("positions", []) or []:
        ticker = _ticker(official.get("ticker"))
        if not ticker:
            continue
        merged = dict(final_by_ticker.get(ticker, {}))
        for field in AUTHORITY_FIELDS:
            if field in official:
                merged[field] = official.get(field)
        merged["ticker"] = ticker
        change = change_by_ticker.get(ticker)
        if change:
            merged["previous_weight_pct"] = change["previous_weight_pct"]
            merged["weight_inherited_pct"] = change["previous_weight_pct"]
            merged["target_weight_pct"] = change["new_weight_pct"]
            merged["shares_delta_this_run"] = change["shares_delta"]
            merged["weight_change_pct"] = change["weight_change_pct"]
            merged["action_executed_this_run"] = change["action"]
            merged["funding_source_note"] = change["funding_source_note"]
        else:
            merged["shares_delta_this_run"] = 0.0
            merged["weight_change_pct"] = 0.0
            merged["action_executed_this_run"] = "None"
            merged["funding_source_note"] = "No model trade executed this run."
        positions.append(merged)

    cash = round(_float(portfolio_state.get("cash_eur")), 2)
    invested = round(sum(_market_value_eur(row) for row in positions), 2)
    nav = round(invested + cash, 2)
    for row in positions:
        ticker = _ticker(row.get("ticker"))
        final_weight = round(_market_value_eur(row) / nav * 100.0, 2) if nav else 0.0
        row["current_weight_pct"] = final_weight
        if ticker in change_by_ticker:
            row["target_weight_pct"] = change_by_ticker[ticker]["new_weight_pct"] or final_weight
        else:
            row["previous_weight_pct"] = final_weight
            row["weight_inherited_pct"] = final_weight
            row.setdefault("target_weight_pct", final_weight)

    final_state = dict(final_state)
    final_state["positions"] = positions
    final_state["portfolio"] = {"cash_eur": cash, "total_portfolio_value_eur": nav, "base_currency": "EUR"}
    final_state["rotation_plan"] = {}
    final_state["rotation_decisions"] = []
    final_state["target_weights"] = []
    final_state["trade_intents"] = []
    final_state["executed_model_changes"] = changes
    final_state["execution_context"] = {
        "report_phase": "post_execution",
        "execution_mode": artifact.get("execution_mode"),
        "execution_status": artifact.get("execution_status"),
        "model_execution_artifact": str(artifact.get("artifact_path") or ""),
        "portfolio_state": str(portfolio_state_path),
        "executed_change_count": len(changes),
    }
    flags = dict(final_state.get("validation_flags") or {})
    flags["executed_portfolio_authority_overlay"] = True
    flags["executed_portfolio_authority_source"] = str(portfolio_state_path)
    flags["post_execution_report"] = True
    flags["rotation_plan_present"] = False
    flags["rotation_warning_mode"] = False
    final_state["validation_flags"] = flags
    return final_state


def _output_root_from_artifact(path: Path) -> Path:
    if path.parent.name == "runtime":
        return path.parent.parent
    return Path("output")


def _report_path_from_env(env_name: str) -> Path | None:
    raw = os.environ.get(env_name, "").strip()
    return Path(raw) if raw else None


def _latest_report(output_dir: Path, prefix: str) -> Path | None:
    files = sorted(output_dir.glob(prefix))
    return files[-1] if files else None


def _run_post_processors(output_dir: Path, runtime_state_path: Path, pricing_audit_path: str | None, en_path: Path, nl_path: Path) -> None:
    env = os.environ.copy()
    env["MRKT_RPRTS_EXPLICIT_REPORT_PATH"] = str(en_path)
    env["MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL"] = str(nl_path)
    env["MRKT_RPRTS_RUNTIME_STATE_PATH"] = str(runtime_state_path)
    env["ETF_RUNTIME_STATE_PATH"] = str(runtime_state_path)
    commands = []
    if pricing_audit_path:
        commands.append([sys.executable, "-m", "runtime.add_etf_pricing_basis_section", "--output-dir", str(output_dir), "--runtime-state", str(runtime_state_path), "--pricing-audit", pricing_audit_path])
    commands.extend([
        [sys.executable, "-m", "runtime.polish_runtime_reports", "--output-dir", str(output_dir), "--runtime-state", str(runtime_state_path)],
        [sys.executable, "-m", "runtime.fix_report_output_contract", "--output-dir", str(output_dir), "--runtime-state", str(runtime_state_path)],
        [sys.executable, "-m", "runtime.add_etf_position_performance_section", "--output-dir", str(output_dir)],
        [sys.executable, "-m", "runtime.apply_nl_localization", "--output-dir", str(output_dir)],
        [sys.executable, "-m", "runtime.scrub_nl_client_language", "--output-dir", str(output_dir)],
        [sys.executable, "-m", "runtime.scrub_nl_pdf_audit_leaks", "--output-dir", str(output_dir)],
        [sys.executable, "-m", "runtime.localize_nl_report_dates", "--output-dir", str(output_dir)],
        [sys.executable, "-m", "runtime.link_runtime_report_tickers", "--output-dir", str(output_dir)],
    ])
    for command in commands:
        subprocess.run(command, check=True, env=env)


def _run_executed_report_contract(runtime_state_path: Path, en_path: Path, nl_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "runtime.fix_executed_report_contract",
            "--runtime-state",
            str(runtime_state_path),
            "--english-report",
            str(en_path),
            "--dutch-report",
            str(nl_path),
        ],
        check=True,
    )


def finalize_from_artifact(artifact_path: Path) -> dict[str, Any]:
    artifact = _read_json(artifact_path)
    if artifact.get("execution_mode") != "guarded_auto" or artifact.get("execution_status") != "executed":
        return {"finalized": False, "reason": "artifact_not_executed_guarded_auto"}

    source_files = artifact.get("source_files") or {}
    pricing_audit = source_files.get("pricing_audit")
    portfolio_state_path = Path(source_files.get("portfolio_state") or "output/etf_portfolio_state.json")
    lane_artifact = source_files.get("lane_assessment") or source_files.get("lane_artifact")
    if not lane_artifact:
        runtime_state_path = Path(source_files.get("runtime_state") or "")
        if runtime_state_path.exists():
            runtime_state = _read_json(runtime_state_path)
            lane_artifact = (runtime_state.get("source_files") or {}).get("lane_assessment")
            pricing_audit = pricing_audit or (runtime_state.get("source_files") or {}).get("pricing_audit")

    output_dir = _output_root_from_artifact(artifact_path)
    final_state = build_runtime_state(
        pricing_audit_path=pricing_audit,
        lane_assessment_path=lane_artifact,
        rotation_plan_path=None,
        disable_rotation_plan=True,
    )
    final_state = _overlay_executed_portfolio_authority(final_state, portfolio_state_path, artifact)
    report_date = str(final_state.get("report_date") or "unknown").replace("-", "")
    run_id = str(final_state.get("run_id") or artifact.get("run_id") or "unknown")
    final_state_path = RUNTIME_DIR / f"etf_report_state_{report_date}_{run_id}_executed.json"
    final_state_path.parent.mkdir(parents=True, exist_ok=True)
    final_state_path.write_text(json.dumps(final_state, indent=2), encoding="utf-8")
    (RUNTIME_DIR / "latest_etf_report_state_path.txt").write_text(str(final_state_path) + "\n", encoding="utf-8")

    en_path = _report_path_from_env("MRKT_RPRTS_EXPLICIT_REPORT_PATH") or _latest_report(output_dir, "weekly_analysis_pro_*.md")
    nl_path = _report_path_from_env("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL") or _latest_report(output_dir, "weekly_analysis_pro_nl_*.md")
    if en_path is None or nl_path is None:
        raise RuntimeError("Cannot finalize executed ETF report: current EN/NL report paths are missing.")
    en_path.write_text(render_en(final_state), encoding="utf-8")
    nl_path.write_text(render_nl(final_state), encoding="utf-8")
    _run_post_processors(output_dir, final_state_path, pricing_audit, en_path, nl_path)
    _run_executed_report_contract(final_state_path, en_path, nl_path)

    result = {
        "finalized": True,
        "runtime_state": str(final_state_path),
        "english_report": str(en_path),
        "dutch_report": str(nl_path),
        "position_count": len(final_state.get("positions") or []),
        "executed_change_count": len(final_state.get("executed_model_changes") or []),
    }
    print(
        "ETF_EXECUTED_REPORT_FINALIZED | "
        f"runtime_state={result['runtime_state']} | en={result['english_report']} | nl={result['dutch_report']} | positions={result['position_count']} | executed_changes={result['executed_change_count']}"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    finalize_from_artifact(Path(args.artifact))


if __name__ == "__main__":
    main()
