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


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _output_root_from_artifact(path: Path) -> Path:
    # artifact normally lives in output/runtime/...
    if path.parent.name == "runtime":
        return path.parent.parent
    return Path("output")


def _report_path_from_env(env_name: str) -> Path | None:
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        return None
    return Path(raw)


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
    commands.extend(
        [
            [sys.executable, "-m", "runtime.polish_runtime_reports", "--output-dir", str(output_dir), "--runtime-state", str(runtime_state_path)],
            [sys.executable, "-m", "runtime.fix_report_output_contract", "--output-dir", str(output_dir), "--runtime-state", str(runtime_state_path)],
            [sys.executable, "-m", "runtime.add_etf_position_performance_section", "--output-dir", str(output_dir)],
            [sys.executable, "-m", "runtime.apply_nl_localization", "--output-dir", str(output_dir)],
            [sys.executable, "-m", "runtime.scrub_nl_client_language", "--output-dir", str(output_dir)],
            [sys.executable, "-m", "runtime.scrub_nl_pdf_audit_leaks", "--output-dir", str(output_dir)],
            [sys.executable, "-m", "runtime.localize_nl_report_dates", "--output-dir", str(output_dir)],
            [sys.executable, "-m", "runtime.link_runtime_report_tickers", "--output-dir", str(output_dir)],
        ]
    )
    for command in commands:
        subprocess.run(command, check=True, env=env)


def finalize_from_artifact(artifact_path: Path) -> dict[str, Any]:
    artifact = _read_json(artifact_path)
    if artifact.get("execution_mode") != "guarded_auto" or artifact.get("execution_status") != "executed":
        return {"finalized": False, "reason": "artifact_not_executed_guarded_auto"}

    source_files = artifact.get("source_files") or {}
    pricing_audit = source_files.get("pricing_audit")
    lane_artifact = source_files.get("lane_assessment") or source_files.get("lane_artifact")
    if not lane_artifact:
        # Runtime-state source keeps lane path inside source_files.
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

    result = {
        "finalized": True,
        "runtime_state": str(final_state_path),
        "english_report": str(en_path),
        "dutch_report": str(nl_path),
        "position_count": len(final_state.get("positions") or []),
    }
    print(
        "ETF_EXECUTED_REPORT_FINALIZED | "
        f"runtime_state={result['runtime_state']} | en={result['english_report']} | nl={result['dutch_report']} | positions={result['position_count']}"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    finalize_from_artifact(Path(args.artifact))


if __name__ == "__main__":
    main()
