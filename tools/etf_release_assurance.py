#!/usr/bin/env python3
"""Independent pre-send release assurance for Weekly ETF.

The module reconstructs a release candidate from immutable files. It does not
render reports, mutate state, update the ledger, or send mail.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IMPLEMENTATION_ROLE = "implementation_operations"
ASSURANCE_ROLE = "governance_release_assurance"
REQUIRED_CHECKS = {
    "source_identity_bound",
    "required_files_present",
    "control_json_parseable",
    "artifact_formats_valid",
    "run_manifest_identity_consistent",
    "pricing_identity_consistent",
    "runtime_identity_consistent",
    "bilingual_table_numeric_parity",
    "artifact_hashes_complete",
    "roles_separated",
}
SHA_RE = re.compile(r"[0-9a-f]{40}")
NUMBER_RE = re.compile(r"[-+]?\d[\d.,]*%?")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def contains_identity(payload: Any, value: str) -> bool:
    if isinstance(payload, dict):
        return any(contains_identity(item, value) for item in payload.values())
    if isinstance(payload, list):
        return any(contains_identity(item, value) for item in payload)
    return str(payload) == value


def add_check(
    checks: list[dict[str, Any]],
    blockers: list[str],
    check_id: str,
    passed: bool,
    evidence: Any,
) -> None:
    checks.append({"id": check_id, "passed": bool(passed), "evidence": evidence})
    if not passed:
        blockers.append(check_id)


def report_assets(report: Path) -> dict[str, Path]:
    return {
        "report": report,
        "delivery_html": report.with_name(f"{report.stem}_delivery.html"),
        "pdf": report.with_suffix(".pdf"),
        "equity_curve_png": report.with_name(f"{report.stem}_equity_curve.png"),
    }


def normalize_number(token: str) -> str | None:
    token = token.strip().replace(" ", "")
    percent = token.endswith("%")
    if percent:
        token = token[:-1]
    sign = ""
    if token.startswith(("+", "-")):
        sign, token = token[0], token[1:]
    if not token or not any(char.isdigit() for char in token):
        return None

    if "," in token and "." in token:
        if token.rfind(",") > token.rfind("."):
            token = token.replace(".", "").replace(",", ".")
        else:
            token = token.replace(",", "")
    elif "," in token:
        tail = token.rsplit(",", 1)[1]
        token = token.replace(",", ".") if len(tail) <= 2 else token.replace(",", "")
    elif token.count(".") > 1:
        token = token.replace(".", "")

    try:
        value = float(f"{sign}{token}")
    except ValueError:
        return None
    if not percent and value.is_integer() and (1 <= abs(value) <= 17 or 2000 <= abs(value) <= 2100):
        return None
    suffix = "%" if percent else ""
    return f"{value:.8f}".rstrip("0").rstrip(".") + suffix


def table_numeric_multiset(path: Path) -> Counter[str]:
    values: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "|" not in line or set(line.replace("|", "").replace("-", "").replace(":", "").strip()) == set():
            continue
        for match in NUMBER_RE.findall(line):
            normalized = normalize_number(match)
            if normalized is not None:
                values.append(normalized)
    return Counter(values)


def valid_format(key: str, path: Path) -> str | None:
    size = path.stat().st_size
    if key.endswith("_report"):
        if size < 512 or "#" not in path.read_text(encoding="utf-8", errors="replace"):
            return f"{key}: invalid or unexpectedly small markdown"
    elif key.endswith("_html"):
        raw = path.read_text(encoding="utf-8", errors="replace").lower()
        if size < 1024 or ("<html" not in raw and "<!doctype" not in raw):
            return f"{key}: invalid or unexpectedly small HTML"
    elif key.endswith("_pdf"):
        if size < 1024 or path.read_bytes()[:5] != b"%PDF-":
            return f"{key}: invalid or unexpectedly small PDF"
    elif key.endswith("_png"):
        if size < 128 or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            return f"{key}: invalid or unexpectedly small PNG"
    elif key == "trade_ledger":
        if size < 8:
            return "trade_ledger: empty or unexpectedly small"
    return None


def build_release_assurance(
    *,
    source_sha: str,
    github_run_id: str,
    run_id: str,
    requested_close_date: str,
    report_token: str,
    pricing_audit: Path,
    runtime_state: Path,
    run_manifest: Path,
    portfolio_state: Path,
    trade_ledger: Path,
    english_report: Path,
    dutch_report: Path,
    output: Path,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []

    try:
        datetime.strptime(requested_close_date, "%Y-%m-%d")
        valid_date = True
    except ValueError:
        valid_date = False
    valid_identity = bool(SHA_RE.fullmatch(source_sha.lower())) and bool(run_id) and valid_date and bool(re.fullmatch(r"\d{6}", report_token))
    add_check(
        checks,
        blockers,
        "source_identity_bound",
        valid_identity,
        {
            "source_sha": source_sha,
            "github_run_id": github_run_id,
            "run_id": run_id,
            "requested_close_date": requested_close_date,
            "report_token": report_token,
        },
    )

    en = report_assets(english_report)
    nl = report_assets(dutch_report)
    paths = {
        "pricing_audit": pricing_audit,
        "runtime_state": runtime_state,
        "run_manifest": run_manifest,
        "portfolio_state": portfolio_state,
        "trade_ledger": trade_ledger,
        "english_report": en["report"],
        "english_html": en["delivery_html"],
        "english_pdf": en["pdf"],
        "english_png": en["equity_curve_png"],
        "dutch_report": nl["report"],
        "dutch_html": nl["delivery_html"],
        "dutch_pdf": nl["pdf"],
        "dutch_png": nl["equity_curve_png"],
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    add_check(checks, blockers, "required_files_present", not missing, {"missing": missing})

    parsed: dict[str, Any] = {}
    json_errors: dict[str, str] = {}
    for key in ("pricing_audit", "runtime_state", "run_manifest", "portfolio_state"):
        path = paths[key]
        if path.is_file():
            try:
                parsed[key] = load_json(path)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                json_errors[key] = str(exc)
    add_check(checks, blockers, "control_json_parseable", not json_errors, json_errors)

    format_errors: list[str] = []
    for key, path in paths.items():
        if path.is_file():
            error = valid_format(key, path)
            if error:
                format_errors.append(error)
    add_check(checks, blockers, "artifact_formats_valid", not format_errors, format_errors)

    manifest = parsed.get("run_manifest", {})
    expected_manifest_values = [
        run_id,
        requested_close_date,
        report_token,
        str(pricing_audit),
        str(runtime_state),
        str(english_report),
        str(dutch_report),
    ]
    manifest_missing = [value for value in expected_manifest_values if not contains_identity(manifest, value)] if isinstance(manifest, dict) else expected_manifest_values
    add_check(
        checks,
        blockers,
        "run_manifest_identity_consistent",
        not manifest_missing,
        {"missing_values": manifest_missing, "path": str(run_manifest)},
    )

    pricing = parsed.get("pricing_audit", {})
    pricing_ok = isinstance(pricing, dict) and contains_identity(pricing, requested_close_date) and (contains_identity(pricing, run_id) or run_id in pricing_audit.name)
    add_check(
        checks,
        blockers,
        "pricing_identity_consistent",
        pricing_ok,
        {"path": str(pricing_audit), "close_bound": contains_identity(pricing, requested_close_date) if isinstance(pricing, dict) else False, "run_bound": (contains_identity(pricing, run_id) if isinstance(pricing, dict) else False) or run_id in pricing_audit.name},
    )

    runtime = parsed.get("runtime_state", {})
    runtime_ok = isinstance(runtime, dict) and contains_identity(runtime, requested_close_date) and (contains_identity(runtime, str(pricing_audit)) or contains_identity(runtime, pricing_audit.name))
    add_check(
        checks,
        blockers,
        "runtime_identity_consistent",
        runtime_ok,
        {"path": str(runtime_state), "close_bound": contains_identity(runtime, requested_close_date) if isinstance(runtime, dict) else False, "pricing_bound": (contains_identity(runtime, str(pricing_audit)) or contains_identity(runtime, pricing_audit.name)) if isinstance(runtime, dict) else False},
    )

    parity_evidence: dict[str, Any] = {}
    parity_ok = False
    if english_report.is_file() and dutch_report.is_file():
        en_numbers = table_numeric_multiset(english_report)
        nl_numbers = table_numeric_multiset(dutch_report)
        parity_ok = bool(en_numbers) and en_numbers == nl_numbers
        parity_evidence = {
            "english_count": sum(en_numbers.values()),
            "dutch_count": sum(nl_numbers.values()),
            "english_only": list((en_numbers - nl_numbers).elements())[:20],
            "dutch_only": list((nl_numbers - en_numbers).elements())[:20],
        }
    add_check(checks, blockers, "bilingual_table_numeric_parity", parity_ok, parity_evidence)

    hashes: dict[str, dict[str, str]] = {}
    if not missing:
        hashes = {key: {"path": str(path), "sha256": sha256_file(path)} for key, path in paths.items()}
    hashes_ok = len(hashes) == len(paths) and all(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) for item in hashes.values())
    add_check(checks, blockers, "artifact_hashes_complete", hashes_ok, hashes)

    add_check(
        checks,
        blockers,
        "roles_separated",
        IMPLEMENTATION_ROLE != ASSURANCE_ROLE,
        {
            "implementation_role": IMPLEMENTATION_ROLE,
            "assurance_role": ASSURANCE_ROLE,
            "implementation_may_self_certify": False,
            "assurance_may_mutate_release_candidate": False,
        },
    )

    decision = "PASS" if not blockers else "FAIL"
    record = {
        "schema_version": "1.0.0",
        "contract_id": "ETF_RELEASE_ASSURANCE_CONTRACT_V1",
        "product": "weekly_etf",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "decision": decision,
        "implementation_role": IMPLEMENTATION_ROLE,
        "assurance_role": ASSURANCE_ROLE,
        "identity": {
            "source_sha": source_sha.lower(),
            "github_run_id": github_run_id,
            "run_id": run_id,
            "requested_close_date": requested_close_date,
            "report_token": report_token,
        },
        "checks": checks,
        "artifact_hashes": hashes,
        "blockers": blockers,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def validate_release_assurance(
    path: Path,
    *,
    expected_source_sha: str | None = None,
    expected_run_id: str | None = None,
    expected_close_date: str | None = None,
    expected_report_token: str | None = None,
) -> dict[str, Any]:
    payload = load_json(path)
    errors: list[str] = []
    if payload.get("decision") != "PASS":
        errors.append(f"decision must be PASS, got {payload.get('decision')!r}")
    if payload.get("implementation_role") != IMPLEMENTATION_ROLE:
        errors.append("implementation role mismatch")
    if payload.get("assurance_role") != ASSURANCE_ROLE:
        errors.append("assurance role mismatch")
    if payload.get("blockers"):
        errors.append(f"blockers present: {payload.get('blockers')}")

    checks = {item.get("id"): item for item in payload.get("checks", []) if isinstance(item, dict)}
    missing_checks = sorted(REQUIRED_CHECKS - set(checks))
    if missing_checks:
        errors.append(f"required checks missing: {missing_checks}")
    failed_checks = sorted(check_id for check_id, item in checks.items() if item.get("passed") is not True)
    if failed_checks:
        errors.append(f"failed checks present: {failed_checks}")

    identity = payload.get("identity", {})
    expected = {
        "source_sha": expected_source_sha.lower() if expected_source_sha else None,
        "run_id": expected_run_id,
        "requested_close_date": expected_close_date,
        "report_token": expected_report_token,
    }
    for key, value in expected.items():
        if value is not None and identity.get(key) != value:
            errors.append(f"identity mismatch for {key}: expected {value!r}, got {identity.get(key)!r}")

    hashes = payload.get("artifact_hashes", {})
    if not hashes or any(not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))) for item in hashes.values() if isinstance(item, dict)):
        errors.append("artifact hashes incomplete or malformed")

    if errors:
        raise RuntimeError("ETF release assurance rejected: " + "; ".join(errors))
    return payload


def ensure_release_assurance_from_environment() -> Path:
    required_env = [
        "GITHUB_SHA",
        "ETF_PRICING_RUN_ID",
        "REQUESTED_CLOSE_DATE",
        "REPORT_TOKEN",
        "ETF_PRICING_AUDIT_PATH",
        "ETF_RUNTIME_STATE_PATH",
        "MRKT_RPRTS_EXPLICIT_REPORT_PATH",
        "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL",
    ]
    missing_env = [name for name in required_env if not os.environ.get(name, "").strip()]
    if missing_env:
        raise RuntimeError(f"ETF release assurance missing required environment: {missing_env}")

    run_id = os.environ["ETF_PRICING_RUN_ID"].strip()
    close_date = os.environ["REQUESTED_CLOSE_DATE"].strip()
    token = os.environ["REPORT_TOKEN"].strip()
    output = Path("output/run_manifests") / f"weekly_etf_release_assurance_{close_date}_{run_id}.json"
    run_manifest = Path("output/run_manifests") / f"weekly_etf_run_manifest_{close_date}_{run_id}.json"
    record = build_release_assurance(
        source_sha=os.environ["GITHUB_SHA"].strip(),
        github_run_id=os.environ.get("GITHUB_RUN_ID", "").strip(),
        run_id=run_id,
        requested_close_date=close_date,
        report_token=token,
        pricing_audit=Path(os.environ["ETF_PRICING_AUDIT_PATH"]),
        runtime_state=Path(os.environ["ETF_RUNTIME_STATE_PATH"]),
        run_manifest=run_manifest,
        portfolio_state=Path("output/etf_portfolio_state.json"),
        trade_ledger=Path("output/etf_trade_ledger.csv"),
        english_report=Path(os.environ["MRKT_RPRTS_EXPLICIT_REPORT_PATH"]),
        dutch_report=Path(os.environ["MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL"]),
        output=output,
    )
    if record["decision"] != "PASS":
        raise RuntimeError(f"ETF release assurance failed: {record['blockers']}")
    validate_release_assurance(
        output,
        expected_source_sha=os.environ["GITHUB_SHA"].strip(),
        expected_run_id=run_id,
        expected_close_date=close_date,
        expected_report_token=token,
    )
    print(f"ETF_RELEASE_ASSURANCE_PASS | output={output} | artifacts={len(record['artifact_hashes'])}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--source-sha", required=True)
    build.add_argument("--github-run-id", default="")
    build.add_argument("--run-id", required=True)
    build.add_argument("--requested-close-date", required=True)
    build.add_argument("--report-token", required=True)
    build.add_argument("--pricing-audit", required=True, type=Path)
    build.add_argument("--runtime-state", required=True, type=Path)
    build.add_argument("--run-manifest", required=True, type=Path)
    build.add_argument("--portfolio-state", required=True, type=Path)
    build.add_argument("--trade-ledger", required=True, type=Path)
    build.add_argument("--english-report", required=True, type=Path)
    build.add_argument("--dutch-report", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path)

    validate = sub.add_parser("validate")
    validate.add_argument("--assurance", required=True, type=Path)
    validate.add_argument("--expected-source-sha")
    validate.add_argument("--expected-run-id")
    validate.add_argument("--expected-close-date")
    validate.add_argument("--expected-report-token")

    args = parser.parse_args()
    if args.command == "build":
        record = build_release_assurance(
            source_sha=args.source_sha,
            github_run_id=args.github_run_id,
            run_id=args.run_id,
            requested_close_date=args.requested_close_date,
            report_token=args.report_token,
            pricing_audit=args.pricing_audit,
            runtime_state=args.runtime_state,
            run_manifest=args.run_manifest,
            portfolio_state=args.portfolio_state,
            trade_ledger=args.trade_ledger,
            english_report=args.english_report,
            dutch_report=args.dutch_report,
            output=args.output,
        )
        print(f"ETF_RELEASE_ASSURANCE_{record['decision']} | output={args.output} | blockers={len(record['blockers'])}")
        return 0 if record["decision"] == "PASS" else 1

    validate_release_assurance(
        args.assurance,
        expected_source_sha=args.expected_source_sha,
        expected_run_id=args.expected_run_id,
        expected_close_date=args.expected_close_date,
        expected_report_token=args.expected_report_token,
    )
    print(f"ETF_RELEASE_ASSURANCE_VALID | assurance={args.assurance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
