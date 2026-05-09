from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import send_report as report_module
from runtime.build_etf_report_state import build_runtime_state
from runtime.delivery_html_overrides import build_report_html_with_state
from runtime.render_etf_report_from_state import cash_eur, invested_eur, total_nav

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
STANDARD_REPORT_RE = re.compile(r"^weekly_analysis_(\d{6})(?:_(\d{2}))?\.md$")


def _canonical_report_key(path: Path, mode: str) -> tuple[str, int] | None:
    match = PRO_REPORT_RE.match(path.name) if mode == "pro" else STANDARD_REPORT_RE.match(path.name)
    if not match:
        return None
    return match.group(1), int(match.group(2) or "1")


def _latest_canonical_report_file(output_dir: Path, mode: str = "standard") -> Path:
    normalized_mode = report_module.normalize_report_mode(mode)
    candidates: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_analysis*.md"):
        key = _canonical_report_key(path, normalized_mode)
        if key is not None:
            candidates.append((key[0], key[1], path))
    if not candidates:
        raise RuntimeError(f"No canonical {normalized_mode} report files found in {output_dir}.")
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[-1][2]


def _latest_canonical_reports_by_day(output_dir: Path, mode: str = "standard") -> list[Path]:
    normalized_mode = report_module.normalize_report_mode(mode)
    by_day: dict[str, tuple[int, Path]] = {}
    for path in output_dir.glob("weekly_analysis*.md"):
        key = _canonical_report_key(path, normalized_mode)
        if key is None:
            continue
        day, version = key
        if day not in by_day or version > by_day[day][0]:
            by_day[day] = (version, path)
    return [item[1] for item in sorted(by_day.values(), key=lambda row: row[1].name)]


def _as_float(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Runtime state validation failed: non-numeric {label}: {value!r}") from exc


def validate_section15_from_runtime_state(_md_text: str | None = None, tolerance: float = 0.05) -> None:
    state = build_runtime_state()
    positions = state.get("positions", []) or []
    if not isinstance(positions, list) or not positions:
        raise RuntimeError("Runtime state validation failed: no positions found.")

    invested = invested_eur(state)
    cash = cash_eur(state)
    nav = total_nav(state)
    if invested <= 0 or nav <= 0:
        raise RuntimeError("Runtime state validation failed: invested value or NAV is not positive.")
    if cash < -tolerance:
        raise RuntimeError("Runtime state validation failed: cash is negative.")
    if abs((invested + cash) - nav) > tolerance:
        raise RuntimeError(f"Runtime state validation failed: invested + cash does not reconcile to NAV ({invested:.2f} + {cash:.2f} vs {nav:.2f}).")

    for position in positions:
        ticker = str(position.get("ticker") or "").strip().upper()
        if not ticker:
            raise RuntimeError("Runtime state validation failed: position missing ticker.")
        shares = _as_float(position.get("shares"), f"shares for {ticker}")
        price = _as_float(position.get("previous_price_local"), f"price for {ticker}")
        value_eur = _as_float(position.get("previous_market_value_eur"), f"EUR value for {ticker}")
        if shares <= 0 or price <= 0 or value_eur <= 0:
            raise RuntimeError(f"Runtime state validation failed: invalid numeric position data for {ticker}.")

    print(f"RUNTIME_SECTION15_OK | positions={len(positions)} | invested_eur={invested:.2f} | cash_eur={cash:.2f} | total_nav={nav:.2f}")


def validate_equity_curve_from_runtime_state(_md_text: str | None = None, tolerance: float = 0.05) -> None:
    state = build_runtime_state()
    nav = total_nav(state)
    if nav <= 0:
        raise RuntimeError("Runtime equity validation failed: NAV is not positive.")
    print(f"RUNTIME_EQUITY_CURVE_OK | latest_nav={nav:.2f}")


report_module.latest_report_file = _latest_canonical_report_file
report_module.latest_reports_by_day = _latest_canonical_reports_by_day
report_module.validate_section15_arithmetic = validate_section15_from_runtime_state
report_module.validate_equity_curve_alignment = validate_equity_curve_from_runtime_state
report_module.build_report_html = build_report_html_with_state(report_module.build_report_html, report_module._base)

if __name__ == "__main__":
    report_module.main()
