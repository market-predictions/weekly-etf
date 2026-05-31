from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_MANIFEST_POINTER = Path("output/run_manifests/latest_weekly_etf_run_manifest_path.txt")
PRICED_STATUSES = {"fresh_exact_close", "fresh_exact_unverified", "prior_valid_close"}
FRESH_EXACT_STATUSES = {"fresh_exact_close", "fresh_exact_unverified"}
LEGACY_FRESH_STATUSES = {"fresh_close", "fresh_fallback_source"}
VALUATION_GRADE = "valuation_grade"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required JSON file does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"Required text file does not exist: {path}")
    return path.read_text(encoding="utf-8")


def _float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return default


def _money(value: Any) -> float:
    parsed = _float(value, None)
    if parsed is None:
        raise RuntimeError(f"Expected numeric value, got {value!r}")
    return round(parsed, 2)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _ticker(value: Any) -> str:
    raw = _text(value)
    match = re.search(r"symbol=([A-Z][A-Z0-9./_-]{0,14})", raw, flags=re.IGNORECASE)
    if match:
        return match.group(1).upper()
    cleaned = re.sub(r"[^A-Za-z0-9./_-]", "", raw).upper()
    return cleaned


def _manifest_path(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    if not DEFAULT_MANIFEST_POINTER.exists():
        raise RuntimeError(f"Run manifest pointer missing: {DEFAULT_MANIFEST_POINTER}")
    raw = DEFAULT_MANIFEST_POINTER.read_text(encoding="utf-8").strip()
    if not raw:
        raise RuntimeError(f"Run manifest pointer is empty: {DEFAULT_MANIFEST_POINTER}")
    path = Path(raw)
    if not path.exists():
        candidate = DEFAULT_MANIFEST_POINTER.parent / path.name
        if candidate.exists():
            return candidate
    return path


def _price_rows(audit: dict[str, Any]) -> list[dict[str, Any]]:
    rows = audit.get("price_results") or audit.get("prices") or []
    return [dict(row) for row in rows]


def _price_index(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in _price_rows(audit):
        symbol = _ticker(row.get("symbol"))
        if symbol:
            indexed[symbol] = row
    return indexed


def _holding_symbols(audit: dict[str, Any], runtime: dict[str, Any]) -> list[str]:
    symbols: list[str] = []
    for row in audit.get("holdings", []) or []:
        symbol = _ticker(row.get("ticker"))
        if symbol and symbol not in symbols:
            symbols.append(symbol)
    if not symbols:
        for row in runtime.get("positions", []) or []:
            symbol = _ticker(row.get("ticker"))
            if symbol and symbol != "CASH" and symbol not in symbols:
                symbols.append(symbol)
    if not symbols:
        raise RuntimeError("No holding symbols found in audit or runtime state.")
    return symbols


def _runtime_positions(runtime: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in runtime.get("positions", []) or []:
        ticker = _ticker(row.get("ticker"))
        if ticker and ticker != "CASH":
            indexed[ticker] = dict(row)
    return indexed


def _client_status(status: str) -> str:
    mapping = {
        "fresh_exact_close": "Fresh exact close",
        "fresh_exact_unverified": "Fresh exact close, unverified",
        "prior_valid_close": "Prior valid market close",
        "carried_forward": "Carried forward",
        "unresolved": "Unresolved",
        "blocked": "Blocked",
    }
    return mapping.get(status, status.replace("_", " ").title())


def _parse_markdown_table_after_heading(md_text: str, heading: str) -> list[dict[str, str]]:
    marker = md_text.find(heading)
    if marker < 0:
        raise RuntimeError(f"Could not find markdown heading/table marker: {heading}")
    lines = md_text[marker:].splitlines()
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in lines:
        if line.startswith("## ") and rows:
            break
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if any(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if header is None:
            header = cells
            continue
        if header and len(cells) >= len(header):
            rows.append(dict(zip(header, cells)))
    if not rows:
        raise RuntimeError(f"No markdown table rows found after marker: {heading}")
    return rows


def _section_scalar(md_text: str, label: str) -> float:
    match = re.search(rf"^-\s*{re.escape(label)}\s*:\s*([-0-9.,]+)", md_text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not find report scalar: {label}")
    value = _float(match.group(1), None)
    if value is None:
        raise RuntimeError(f"Could not parse report scalar {label}: {match.group(1)!r}")
    return value


def _validate_manifest(manifest_path: Path, manifest: dict[str, Any]) -> tuple[Path, Path, Path, Path, Path]:
    required = ["run_id", "requested_close_date", "pricing_audit_path", "runtime_state_path", "english_report_path", "portfolio_state_path", "valuation_history_path"]
    missing = [key for key in required if not _text(manifest.get(key))]
    if missing:
        raise RuntimeError(f"Pricing-lineage manifest missing required fields: {', '.join(missing)}")
    pricing_audit = Path(_text(manifest["pricing_audit_path"]))
    runtime_state = Path(_text(manifest["runtime_state_path"]))
    english_report = Path(_text(manifest["english_report_path"]))
    portfolio_state = Path(_text(manifest["portfolio_state_path"]))
    valuation_history = Path(_text(manifest["valuation_history_path"]))
    for path in [manifest_path, pricing_audit, runtime_state, english_report, portfolio_state, valuation_history]:
        if not path.exists():
            raise RuntimeError(f"Pricing-lineage manifest points to missing file: {path}")
    return pricing_audit, runtime_state, english_report, portfolio_state, valuation_history


def _validate_audit_identity(manifest: dict[str, Any], audit_path: Path, runtime: dict[str, Any], audit: dict[str, Any]) -> None:
    requested = _text(manifest.get("requested_close_date"))
    run_id = _text(manifest.get("run_id"))
    if _text(audit.get("requested_close_date")) != requested:
        raise RuntimeError(f"Audit requested_close_date={audit.get('requested_close_date')}, manifest expected {requested}")
    if _text(audit.get("run_id")) != run_id:
        raise RuntimeError(f"Audit run_id={audit.get('run_id')}, manifest expected {run_id}")
    if _text(runtime.get("requested_close_date")) != requested:
        raise RuntimeError(f"Runtime requested_close_date={runtime.get('requested_close_date')}, manifest expected {requested}")
    if _text(runtime.get("run_id")) != run_id:
        raise RuntimeError(f"Runtime run_id={runtime.get('run_id')}, manifest expected {run_id}")
    runtime_audit_path = _text((runtime.get("source_files") or {}).get("pricing_audit"))
    if runtime_audit_path != str(audit_path):
        raise RuntimeError(f"Runtime source_files.pricing_audit={runtime_audit_path}, expected exact audit {audit_path}")


def _validate_price_rows(audit: dict[str, Any]) -> None:
    for row in _price_rows(audit):
        symbol = _ticker(row.get("symbol")) or "<unknown>"
        status = _text(row.get("status"))
        requested = _text(row.get("requested_close_date") or audit.get("requested_close_date"))
        returned = _text(row.get("returned_close_date"))
        if status in FRESH_EXACT_STATUSES or status in LEGACY_FRESH_STATUSES:
            if not requested or returned != requested:
                raise RuntimeError(f"{symbol}: status={status} but returned_close_date={returned!r}, requested={requested!r}")
        if status in PRICED_STATUSES:
            for field in ["provider_symbol", "selected_close", "selected_close_type", "currency", "source", "pricing_tier"]:
                if row.get(field) in (None, ""):
                    raise RuntimeError(f"{symbol}: priced row missing required lineage field {field}")
            if row.get("is_final_eod_bar") is not True:
                raise RuntimeError(f"{symbol}: priced row is not marked as a final EOD bar")


def _validate_runtime_vs_audit(runtime: dict[str, Any], audit: dict[str, Any], *, price_tolerance: float, value_tolerance: float) -> None:
    prices = _price_index(audit)
    positions = _runtime_positions(runtime)
    for symbol in _holding_symbols(audit, runtime):
        price_row = prices.get(symbol)
        if not price_row:
            raise RuntimeError(f"Holding {symbol} missing from pricing audit price_results")
        if _text(price_row.get("pricing_tier")) != VALUATION_GRADE:
            raise RuntimeError(f"Holding {symbol} is not valuation-grade priced")
        if _text(price_row.get("status")) not in PRICED_STATUSES:
            raise RuntimeError(f"Holding {symbol} has non-priced audit status: {price_row.get('status')}")
        runtime_row = positions.get(symbol)
        if not runtime_row:
            raise RuntimeError(f"Holding {symbol} missing from runtime positions")
        audit_price = _float(price_row.get("selected_close") if price_row.get("selected_close") is not None else price_row.get("price"), None)
        runtime_price = _float(runtime_row.get("selected_close") if runtime_row.get("selected_close") is not None else runtime_row.get("current_price_local"), None)
        if audit_price is None or runtime_price is None or abs(audit_price - runtime_price) > price_tolerance:
            raise RuntimeError(f"Holding {symbol} runtime price {runtime_price} does not match audit selected close {audit_price}")
        audit_status = _text(price_row.get("status"))
        runtime_status = _text(runtime_row.get("pricing_status"))
        if runtime_status != audit_status:
            raise RuntimeError(f"Holding {symbol} runtime pricing_status={runtime_status}, audit status={audit_status}")
        mv = _float(runtime_row.get("previous_market_value_eur") if runtime_row.get("previous_market_value_eur") is not None else runtime_row.get("market_value_eur"), None)
        if mv is None or mv <= 0:
            raise RuntimeError(f"Holding {symbol} runtime market value missing or invalid: {mv}")
    cash = _money((runtime.get("portfolio") or {}).get("cash_eur"))
    invested = round(sum(_money(row.get("previous_market_value_eur") if row.get("previous_market_value_eur") is not None else row.get("market_value_eur")) for row in positions.values()), 2)
    nav = _money((runtime.get("portfolio") or {}).get("total_portfolio_value_eur"))
    if abs((invested + cash) - nav) > value_tolerance:
        raise RuntimeError(f"Runtime NAV mismatch: invested {invested} + cash {cash} != nav {nav}")


def _validate_report_tables(report_path: Path, runtime: dict[str, Any], audit: dict[str, Any], *, price_tolerance: float, value_tolerance: float) -> None:
    md_text = _read_text(report_path)
    prices = _price_index(audit)
    runtime_positions = _runtime_positions(runtime)
    requested = _text(audit.get("requested_close_date"))

    disclosure_rows = _parse_markdown_table_after_heading(md_text, "| Holding | Requested close | Close date used | Close used | Currency | Market-data source | Status |")
    disclosure_by_symbol = {_ticker(row.get("Holding")): row for row in disclosure_rows}
    for symbol in _holding_symbols(audit, runtime):
        report_row = disclosure_by_symbol.get(symbol)
        if not report_row:
            raise RuntimeError(f"Report pricing disclosure missing holding {symbol}")
        price_row = prices[symbol]
        if _text(report_row.get("Requested close")) != requested:
            raise RuntimeError(f"Report disclosure {symbol} requested close mismatch")
        if _text(report_row.get("Close date used")) != _text(price_row.get("returned_close_date")):
            raise RuntimeError(f"Report disclosure {symbol} close-date-used mismatch")
        report_price = _float(report_row.get("Close used"), None)
        audit_price = _float(price_row.get("selected_close") if price_row.get("selected_close") is not None else price_row.get("price"), None)
        if report_price is None or audit_price is None or abs(report_price - audit_price) > price_tolerance:
            raise RuntimeError(f"Report disclosure {symbol} close {report_price} does not match audit {audit_price}")
        if _text(report_row.get("Currency")) != _text(price_row.get("currency")):
            raise RuntimeError(f"Report disclosure {symbol} currency mismatch")
        expected_status = _client_status(_text(price_row.get("status")))
        if _text(report_row.get("Status")) != expected_status:
            raise RuntimeError(f"Report disclosure {symbol} status={report_row.get('Status')!r}, expected {expected_status!r}")

    section15_nav = _section_scalar(md_text, "Total portfolio value (EUR)")
    section7_nav = _section_scalar(md_text, "Current portfolio value (EUR)")
    runtime_nav = _money((runtime.get("portfolio") or {}).get("total_portfolio_value_eur"))
    if abs(section15_nav - runtime_nav) > value_tolerance:
        raise RuntimeError(f"Section 15 NAV {section15_nav} does not match runtime NAV {runtime_nav}")
    if abs(section7_nav - section15_nav) > value_tolerance:
        raise RuntimeError(f"Section 7 NAV {section7_nav} does not match Section 15 NAV {section15_nav}")

    section15_rows = _parse_markdown_table_after_heading(md_text, "| Ticker | Shares | Price (local) | Currency | Market value (local) | Market value (EUR) | Weight % |")
    section15_by_symbol = {_ticker(row.get("Ticker")): row for row in section15_rows}
    for symbol, runtime_row in runtime_positions.items():
        report_row = section15_by_symbol.get(symbol)
        if not report_row:
            raise RuntimeError(f"Section 15 missing runtime holding {symbol}")
        for label, runtime_key in [("Price (local)", "current_price_local"), ("Market value (EUR)", "previous_market_value_eur")]:
            report_value = _float(report_row.get(label), None)
            runtime_value = _float(runtime_row.get(runtime_key), None)
            if report_value is None or runtime_value is None or abs(report_value - runtime_value) > value_tolerance:
                raise RuntimeError(f"Section 15 {symbol} {label}={report_value}, runtime {runtime_key}={runtime_value}")


def _validate_recalculated_nav(runtime: dict[str, Any], audit: dict[str, Any], *, value_tolerance: float) -> None:
    prices = _price_index(audit)
    positions = _runtime_positions(runtime)
    fx_rate = _float((audit.get("fx_basis") or {}).get("rate") or (runtime.get("fx_basis") or {}).get("rate"), None)
    if not fx_rate:
        raise RuntimeError("FX rate missing for NAV recalculation")
    cash = _money((runtime.get("portfolio") or {}).get("cash_eur"))
    invested = 0.0
    for symbol, position in positions.items():
        price_row = prices.get(symbol)
        if not price_row:
            raise RuntimeError(f"Cannot recalculate NAV: missing audit price for {symbol}")
        shares = _float(position.get("shares"), None)
        price = _float(price_row.get("selected_close") if price_row.get("selected_close") is not None else price_row.get("price"), None)
        currency = _text(price_row.get("currency") or position.get("currency") or "USD").upper()
        if shares is None or price is None:
            raise RuntimeError(f"Cannot recalculate NAV for {symbol}: shares={shares}, price={price}")
        local_value = shares * price
        invested += local_value if currency == "EUR" else local_value / fx_rate
    recalculated = round(invested + cash, 2)
    reported = _money((runtime.get("portfolio") or {}).get("total_portfolio_value_eur"))
    if abs(recalculated - reported) > value_tolerance:
        raise RuntimeError(f"Recalculated NAV {recalculated} does not match reported runtime NAV {reported}")


def _validate_persisted_state(portfolio_state_path: Path, valuation_history_path: Path, runtime: dict[str, Any], audit_path: Path, *, value_tolerance: float) -> None:
    portfolio_state = _read_json(portfolio_state_path)
    report_date = _text(runtime.get("requested_close_date") or runtime.get("report_date"))
    runtime_nav = _money((runtime.get("portfolio") or {}).get("total_portfolio_value_eur"))
    runtime_cash = _money((runtime.get("portfolio") or {}).get("cash_eur"))
    runtime_invested = round(sum(_money(row.get("previous_market_value_eur") if row.get("previous_market_value_eur") is not None else row.get("market_value_eur")) for row in _runtime_positions(runtime).values()), 2)
    checks = {
        "nav_eur": (portfolio_state.get("nav_eur"), runtime_nav),
        "cash_eur": (portfolio_state.get("cash_eur"), runtime_cash),
        "invested_market_value_eur": (portfolio_state.get("invested_market_value_eur"), runtime_invested),
        "last_valuation.date": ((portfolio_state.get("last_valuation") or {}).get("date"), report_date),
        "last_valuation.nav_eur": ((portfolio_state.get("last_valuation") or {}).get("nav_eur"), runtime_nav),
    }
    for label, (actual, expected) in checks.items():
        if isinstance(expected, str):
            if _text(actual) != expected:
                raise RuntimeError(f"Portfolio state mismatch for {label}: actual={actual!r}, expected={expected!r}")
        elif abs(_float(actual, -1.0) - expected) > value_tolerance:
            raise RuntimeError(f"Portfolio state mismatch for {label}: actual={actual}, expected={expected}")
    if _text(portfolio_state.get("pricing_audit_file")) != str(audit_path):
        raise RuntimeError(f"Portfolio state pricing_audit_file={portfolio_state.get('pricing_audit_file')}, expected {audit_path}")

    if not valuation_history_path.exists():
        raise RuntimeError(f"Valuation history missing: {valuation_history_path}")
    with valuation_history_path.open("r", encoding="utf-8", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
    matches = [row for row in rows if _text(row.get("date")) == report_date]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one valuation-history row for {report_date}; found {len(matches)}")
    row = matches[0]
    if abs(_float(row.get("nav_eur"), -1.0) - runtime_nav) > value_tolerance:
        raise RuntimeError(f"Valuation history nav_eur={row.get('nav_eur')}, expected {runtime_nav}")


def _validate_fundable_challengers(runtime: dict[str, Any], audit: dict[str, Any]) -> None:
    prices = _price_index(audit)
    lane_artifact_path = _text((runtime.get("source_files") or {}).get("lane_assessment"))
    if not lane_artifact_path:
        return
    lane_path = Path(lane_artifact_path)
    if not lane_path.exists():
        raise RuntimeError(f"Runtime lane assessment source missing: {lane_path}")
    lane_artifact = _read_json(lane_path)
    for lane in lane_artifact.get("assessed_lanes", []) or []:
        if lane.get("is_fundable_candidate") is not True:
            continue
        primary = _ticker(lane.get("primary_etf"))
        if not primary:
            raise RuntimeError("Fundable lane has no primary_etf")
        price_row = prices.get(primary)
        if not price_row:
            raise RuntimeError(f"Fundable challenger {primary} missing from pricing audit")
        if _text(price_row.get("pricing_tier")) != VALUATION_GRADE or _text(price_row.get("status")) not in PRICED_STATUSES:
            raise RuntimeError(f"Fundable challenger {primary} lacks valuation-grade priced audit row")


def _update_manifest_status(manifest_path: Path, manifest: dict[str, Any], status: str, summary: dict[str, Any]) -> None:
    manifest = dict(manifest)
    manifest["pricing_lineage_status"] = status
    manifest["pricing_lineage_validated_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["pricing_lineage_validation"] = summary
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest_path(
    manifest_path: Path,
    *,
    price_tolerance: float = 0.02,
    value_tolerance: float = 0.75,
    update_manifest_status: bool = False,
) -> dict[str, Any]:
    manifest = _read_json(manifest_path)
    pricing_audit_path, runtime_state_path, english_report_path, portfolio_state_path, valuation_history_path = _validate_manifest(manifest_path, manifest)
    audit = _read_json(pricing_audit_path)
    runtime = _read_json(runtime_state_path)

    _validate_audit_identity(manifest, pricing_audit_path, runtime, audit)
    _validate_price_rows(audit)
    _validate_runtime_vs_audit(runtime, audit, price_tolerance=price_tolerance, value_tolerance=value_tolerance)
    _validate_report_tables(english_report_path, runtime, audit, price_tolerance=price_tolerance, value_tolerance=value_tolerance)
    _validate_recalculated_nav(runtime, audit, value_tolerance=value_tolerance)
    _validate_persisted_state(portfolio_state_path, valuation_history_path, runtime, pricing_audit_path, value_tolerance=value_tolerance)
    _validate_fundable_challengers(runtime, audit)

    summary = {
        "run_id": manifest.get("run_id"),
        "requested_close_date": manifest.get("requested_close_date"),
        "pricing_audit_path": str(pricing_audit_path),
        "runtime_state_path": str(runtime_state_path),
        "english_report_path": str(english_report_path),
        "holdings_validated": _holding_symbols(audit, runtime),
        "total_portfolio_value_eur": (runtime.get("portfolio") or {}).get("total_portfolio_value_eur"),
    }
    if update_manifest_status:
        _update_manifest_status(manifest_path, manifest, "passed", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF pricing lineage from manifest to audit, runtime, report, persisted state, and valuation history.")
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--price-tolerance", type=float, default=0.02)
    parser.add_argument("--value-tolerance", type=float, default=0.75)
    parser.add_argument("--no-update-manifest-status", action="store_true")
    args = parser.parse_args()

    manifest_path = _manifest_path(args.manifest)
    summary = validate_manifest_path(
        manifest_path,
        price_tolerance=args.price_tolerance,
        value_tolerance=args.value_tolerance,
        update_manifest_status=not args.no_update_manifest_status,
    )
    print(
        "ETF_PRICING_LINEAGE_CONTRACT_OK | "
        f"run_id={summary.get('run_id')} | requested_close={summary.get('requested_close_date')} | "
        f"holdings={len(summary.get('holdings_validated') or [])} | manifest={manifest_path}"
    )


if __name__ == "__main__":
    main()
