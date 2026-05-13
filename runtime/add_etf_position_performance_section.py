from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from runtime.build_etf_report_state import build_runtime_state

MARKET_HISTORY_PATH = Path("output/market_history/etf_relative_strength.json")
EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

SECTION_START_RE = re.compile(
    r"\n## 7A\. (?:ETF Position Performance|ETF-positieperformance)\n.*?(?=\n## 8\. )",
    re.DOTALL,
)

ETF_NAMES = {
    "SPY": "SPDR S&P 500 ETF Trust",
    "SMH": "VanEck Semiconductor ETF",
    "PPA": "Invesco Aerospace & Defense ETF",
    "PAVE": "Global X U.S. Infrastructure Development ETF",
    "URNM": "Sprott Uranium Miners ETF",
    "GLD": "SPDR Gold Shares",
}


def _latest_report(output_dir: Path, language: str) -> Path:
    env_key = "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL" if language == "nl" else "MRKT_RPRTS_EXPLICIT_REPORT_PATH"
    explicit = os.environ.get(env_key, "").strip()
    pattern = NL_RE if language == "nl" else EN_RE
    if explicit:
        path = Path(explicit)
        if path.exists() and pattern.match(path.name):
            return path
    glob = "weekly_analysis_pro_nl_*.md" if language == "nl" else "weekly_analysis_pro_*.md"
    reports = sorted(path for path in output_dir.glob(glob) if pattern.match(path.name))
    if not reports:
        raise RuntimeError(f"No {language} ETF pro report found in {output_dir}")
    return reports[-1]


def _load_market_metrics(path: Path = MARKET_HISTORY_PATH) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("metrics") or {}


def _float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def _fmt_pct(value: Any, signed: bool = True) -> str:
    number = _float(value)
    if number is None:
        return "n/a"
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.2f}%"


def _fmt_eur(value: Any) -> str:
    number = _float(value)
    if number is None:
        return "n/a"
    sign = "-" if number < 0 else ""
    return f"{sign}{abs(number):,.2f}"


def _weight_map(state: dict[str, Any]) -> dict[str, float]:
    nav = _float((state.get("portfolio") or {}).get("total_portfolio_value_eur")) or 1.0
    out: dict[str, float] = {}
    for position in state.get("positions", []) or []:
        ticker = str(position.get("ticker") or "").upper()
        value = _float(position.get("previous_market_value_eur") or position.get("market_value_eur")) or 0.0
        if ticker:
            out[ticker] = round(value / nav * 100.0, 2)
    return out


def _position_pl_eur(position: dict[str, Any], state: dict[str, Any]) -> float | None:
    shares = _float(position.get("shares"))
    avg_entry = _float(position.get("avg_entry_local"))
    current_value_eur = _float(position.get("previous_market_value_eur") or position.get("market_value_eur"))
    currency = str(position.get("currency") or "USD").upper()
    fx_rate = _float((state.get("fx_basis") or {}).get("rate"))
    if shares is not None and avg_entry is not None and current_value_eur is not None:
        entry_value_local = shares * avg_entry
        if currency == "EUR":
            entry_value_eur = entry_value_local
        elif fx_rate:
            entry_value_eur = entry_value_local / fx_rate
        else:
            entry_value_eur = None
        if entry_value_eur is not None:
            return round(current_value_eur - entry_value_eur, 2)

    pnl_pct = _float(position.get("pnl_pct"))
    if current_value_eur is not None and pnl_pct is not None and abs(100.0 + pnl_pct) > 0.001:
        return round(current_value_eur * (pnl_pct / (100.0 + pnl_pct)), 2)
    return None


def _contribution_pct(pl_eur: float | None, state: dict[str, Any]) -> float | None:
    starting = _float((state.get("portfolio") or {}).get("starting_capital_eur"))
    if starting is None:
        # Current production portfolio starts at EUR 100,000; keep this fallback
        # local to the presentation layer until the runtime state exposes it.
        starting = 100000.0
    if pl_eur is None or not starting:
        return None
    return round(pl_eur / starting * 100.0, 2)


def _performance_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    metrics = _load_market_metrics()
    weights = _weight_map(state)
    rows: list[dict[str, Any]] = []
    for position in state.get("positions", []) or []:
        ticker = str(position.get("ticker") or "").upper()
        if not ticker or ticker == "CASH":
            continue
        metric = metrics.get(ticker, {})
        pl_eur = _position_pl_eur(position, state)
        rows.append(
            {
                "portfolio_sleeve": position.get("portfolio_role") or "Position",
                "investment_thesis": position.get("original_thesis") or ETF_NAMES.get(ticker, ticker),
                "ticker": ticker,
                "weight_pct": weights.get(ticker),
                "return_1w_pct": metric.get("return_1w_pct"),
                "return_1m_pct": metric.get("return_1m_pct"),
                "return_3m_pct": metric.get("return_3m_pct"),
                "since_entry_pct": position.get("pnl_pct"),
                "pl_eur": pl_eur,
                "contribution_pct": _contribution_pct(pl_eur, state),
            }
        )
    return rows


def _table(state: dict[str, Any], language: str = "en") -> str:
    rows = _performance_rows(state)
    if language == "nl":
        lines = [
            "## 7A. ETF-positieperformance",
            "",
            "Performance wordt berekend op de huidige ETF-posities op basis van de meest recente gevalideerde slotkoers-audit en beschikbare markthistorie.",
            "",
            "| Portefeuillesegment | Beleggingsthese | ETF | Gewicht % | 1w rendement | 1m rendement | 3m rendement | Sinds instap | P/L EUR | Bijdrage % |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    else:
        lines = [
            "## 7A. ETF Position Performance",
            "",
            "Performance is calculated on the current ETF holdings using the latest validated close-price audit and available market-history inputs.",
            "",
            "| Portfolio sleeve | Investment thesis | Tradable ETF | Weight % | 1w return | 1m return | 3m return | Since-entry | P/L EUR | Contribution % |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    for row in rows:
        lines.append(
            f"| {row['portfolio_sleeve']} | {row['investment_thesis']} | {row['ticker']} | "
            f"{_fmt_pct(row['weight_pct'], signed=False)} | {_fmt_pct(row['return_1w_pct'])} | "
            f"{_fmt_pct(row['return_1m_pct'])} | {_fmt_pct(row['return_3m_pct'])} | "
            f"{_fmt_pct(row['since_entry_pct'])} | {_fmt_eur(row['pl_eur'])} | {_fmt_pct(row['contribution_pct'])} |"
        )
    return "\n".join(lines)


def _insert_or_replace(report_text: str, section: str) -> str:
    report_text = SECTION_START_RE.sub("", report_text)
    anchor = "`EQUITY_CURVE_CHART_PLACEHOLDER`"
    if anchor not in report_text:
        raise RuntimeError("Could not find equity-curve chart placeholder anchor for ETF performance section insertion.")
    return report_text.replace(anchor, anchor + "\n\n" + section, 1)


def update_report(path: Path, state: dict[str, Any], language: str) -> None:
    report_text = path.read_text(encoding="utf-8")
    updated = _insert_or_replace(report_text, _table(state, language))
    path.write_text(updated, encoding="utf-8")
    print(f"ETF_POSITION_PERFORMANCE_SECTION_OK | report={path.name} | language={language} | rows={len(_performance_rows(state))}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    state = build_runtime_state()
    update_report(_latest_report(output_dir, "en"), state, "en")
    try:
        update_report(_latest_report(output_dir, "nl"), state, "nl")
    except RuntimeError as exc:
        print(f"ETF_POSITION_PERFORMANCE_SECTION_NL_SKIPPED | reason={exc}")


if __name__ == "__main__":
    main()
