from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime.build_etf_report_state import build_runtime_state

ETF_NAMES = {
    "SPY": "SPDR S&P 500 ETF Trust",
    "SMH": "VanEck Semiconductor ETF",
    "PPA": "Invesco Aerospace & Defense ETF",
    "PAVE": "Global X U.S. Infrastructure Development ETF",
    "URNM": "Sprott Uranium Miners ETF",
    "GLD": "SPDR Gold Shares",
}


def f2(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""


def f4(value: Any) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return ""


def eurusd_used(state: dict[str, Any]) -> str:
    return f4((state.get("fx_basis") or {}).get("rate")) or "0.0000"


def position_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    return list(state.get("positions", []))


def cash_eur(state: dict[str, Any]) -> float:
    return float(state.get("portfolio", {}).get("cash_eur") or 0.0)


def invested_eur(state: dict[str, Any]) -> float:
    return round(sum(float(p.get("previous_market_value_eur") or 0.0) for p in position_rows(state)), 2)


def total_nav(state: dict[str, Any]) -> float:
    return round(invested_eur(state) + cash_eur(state), 2)


def weights(state: dict[str, Any]) -> dict[str, float]:
    nav = total_nav(state) or 1.0
    return {
        str(p.get("ticker", "")).upper(): round(float(p.get("previous_market_value_eur") or 0.0) / nav * 100.0, 2)
        for p in position_rows(state)
    }


def price_by_symbol(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(p.get("symbol", "")).upper(): p for p in state.get("pricing", [])}


def promoted_lanes(state: dict[str, Any]) -> list[dict[str, Any]]:
    lanes = state.get("lane_assessment", {}).get("assessed_lanes", [])
    promoted = [lane for lane in lanes if lane.get("promoted_to_live_radar") is True]
    return promoted[:8]


def omitted_lanes(state: dict[str, Any]) -> list[dict[str, Any]]:
    lanes = state.get("lane_assessment", {}).get("assessed_lanes", [])
    return [lane for lane in lanes if lane.get("promoted_to_live_radar") is not True][:6]


def report_suffix(report_date: str) -> str:
    return report_date.replace("-", "")[2:]


def replacement_duel_table(state: dict[str, Any]) -> str:
    prices = price_by_symbol(state)
    current = {str(p.get("ticker", "")).upper(): p for p in position_rows(state)}
    duel_map = {
        "PPA": ["ITA"],
        "PAVE": ["GRID"],
        "GLD": ["GSG", "BIL"],
        "SPY": ["QUAL", "IEFA"],
    }
    lines = [
        "| Current holding | Challenger | Current close | Challenger close | Close-date basis | Duel status | Decision implication |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for holding, challengers in duel_map.items():
        current_close = f2(current.get(holding, {}).get("previous_price_local"))
        challenger_close_parts = []
        close_basis_parts = []
        any_priced = False
        for challenger in challengers:
            p = prices.get(challenger)
            if p:
                any_priced = True
                challenger_close_parts.append(f"{challenger} {f2(p.get('price'))}")
                close_basis_parts.append(str(p.get("returned_close_date") or "latest verified"))
            else:
                challenger_close_parts.append(f"{challenger} n/a")
                close_basis_parts.append("missing")
        status = "priced but duel incomplete" if any_priced else "not fundable — pricing missing"
        lines.append(
            f"| {holding} | {' / '.join(challengers)} | {current_close} | {'; '.join(challenger_close_parts)} | "
            f"{' / '.join(close_basis_parts)} | {status} | Do not fund replacement until same-basis relative-strength duel is complete |"
        )
    return "\n".join(lines)


def radar_table(state: dict[str, Any]) -> str:
    lines = [
        "| Theme | Primary ETF | Alternative ETF | Why it matters | Structural fit | Macro timing | Status | What needs to happen | Time horizon |",
        "|---|---|---|---|---:|---:|---|---|---|",
    ]
    for lane in promoted_lanes(state):
        status = "Actionable now" if float(lane.get("total_score") or 0) >= 4.5 else "Watchlist / under review"
        lines.append(
            f"| {lane.get('lane_name')} | {lane.get('primary_etf')} | {lane.get('alternative_etf')} | "
            f"{lane.get('what_would_change', '')} | {lane.get('structural_strength', '')} | {lane.get('macro_alignment', '')} | "
            f"{status} | {lane.get('what_would_change', '')} | 3-12 months |"
        )
    return "\n".join(lines)


def omitted_table(state: dict[str, Any]) -> str:
    lines = [
        "| Theme | Primary ETF | Why not promoted | What would change that |",
        "|---|---|---|---|",
    ]
    for lane in omitted_lanes(state):
        lines.append(
            f"| {lane.get('lane_name')} | {lane.get('primary_etf')} | "
            f"{lane.get('rejection_reason') or 'Not superior to funded exposures this run.'} | {lane.get('what_would_change', '')} |"
        )
    return "\n".join(lines)


def section15_table(state: dict[str, Any]) -> str:
    w = weights(state)
    lines = [
        "| Ticker | Shares | Price (local) | Currency | Market value (local) | Market value (EUR) | Weight % |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for p in position_rows(state):
        ticker = str(p.get("ticker", "")).upper()
        lines.append(
            f"| {ticker} | {f2(p.get('shares'))} | {f2(p.get('previous_price_local'))} | {p.get('currency', 'USD')} | "
            f"{f2(p.get('previous_market_value_local'))} | {f2(p.get('previous_market_value_eur'))} | {f2(w.get(ticker))} |"
        )
    cash_pct = cash_eur(state) / (total_nav(state) or 1.0) * 100.0
    lines.append(f"| CASH | - | 1.00 | EUR | {f2(cash_eur(state))} | {f2(cash_eur(state))} | {f2(cash_pct)} |")
    return "\n".join(lines)


def section7_table(state: dict[str, Any]) -> str:
    report_date = state.get("report_date") or ""
    nav = total_nav(state)
    return "\n".join(
        [
            "| Date | Portfolio value (EUR) | Comment |",
            "|---|---:|---|",
            "| 2026-03-28 | 100000.00 | Inaugural model portfolio established |",
            f"| {report_date} | {nav:.2f} | Runtime-derived valuation from pricing audit and explicit portfolio state |",
        ]
    )


def current_position_table(state: dict[str, Any]) -> str:
    lines = [
        "| Ticker | Score | Action | Conviction | Key point |",
        "|---|---:|---|---|---|",
    ]
    for p in position_rows(state):
        lines.append(
            f"| {p.get('ticker')} | {f2(p.get('total_score'))} | {p.get('suggested_action', 'Hold')} | "
            f"{p.get('conviction_tier', '')} | {p.get('short_reason', '')} |"
        )
    return "\n".join(lines)


def final_action_table(state: dict[str, Any]) -> str:
    w = weights(state)
    lines = [
        "| Ticker | ETF | Existing/New | Weight Inherited | Target Weight | Suggested Action | Conviction Tier | Total Score | Portfolio Role | Better Alternative Exists? | Short Reason |",
        "|---|---|---|---:|---:|---|---|---:|---|---|---|",
    ]
    for p in position_rows(state):
        ticker = str(p.get("ticker", "")).upper()
        lines.append(
            f"| {ticker} | {ETF_NAMES.get(ticker, ticker)} | {p.get('existing_new', 'Existing')} | {f2(p.get('previous_weight_pct'))} | {f2(w.get(ticker))} | "
            f"{p.get('suggested_action', 'Hold')} | {p.get('conviction_tier', '')} | {f2(p.get('total_score'))} | {p.get('portfolio_role', '')} | "
            f"{p.get('better_alternative_exists', 'No')} | {p.get('short_reason', '')} |"
        )
    return "\n".join(lines)


def position_changes_table(state: dict[str, Any]) -> str:
    w = weights(state)
    lines = [
        "| Ticker | Previous weight % | New weight % | Weight change % | Shares delta | Action executed | Funding source / note |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for p in position_rows(state):
        ticker = str(p.get("ticker", "")).upper()
        prev = float(p.get("previous_weight_pct") or p.get("current_weight_pct") or 0.0)
        new = w.get(ticker, prev)
        lines.append(
            f"| {ticker} | {prev:.2f} | {new:.2f} | {new - prev:.2f} | {f2(p.get('shares_delta_this_run'))} | "
            f"{p.get('action_executed_this_run', 'None')} | {p.get('funding_source_note', '')} |"
        )
    cash_pct = cash_eur(state) / (total_nav(state) or 1.0) * 100.0
    lines.append(f"| CASH | - | {cash_pct:.2f} | - | 0.00 | None | Residual cash |")
    return "\n".join(lines)


def continuity_table(state: dict[str, Any]) -> str:
    w = weights(state)
    lines = [
        "| Ticker | ETF Name | Direction | Weight % | Avg Entry | Current Price | P/L % | Original Thesis | Role |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for p in position_rows(state):
        ticker = str(p.get("ticker", "")).upper()
        lines.append(
            f"| {ticker} | {ETF_NAMES.get(ticker, ticker)} | {p.get('direction', 'Long')} | {f2(w.get(ticker))} | {f2(p.get('avg_entry_local'))} | "
            f"{f2(p.get('previous_price_local'))} | {f2(p.get('pnl_pct'))} | {p.get('original_thesis', '')} | {p.get('portfolio_role', '')} |"
        )
    return "\n".join(lines)


def render_en(state: dict[str, Any]) -> str:
    report_date = state.get("report_date") or "unknown"
    nav = total_nav(state)
    inv = invested_eur(state)
    cash = cash_eur(state)
    holdings = ", ".join(str(p.get("ticker")) for p in position_rows(state))
    eurusd = eurusd_used(state)
    return f"""# Weekly ETF Pro Review {report_date}

> *This report is for informational and educational purposes only; please see the disclaimer at the end.*

## 1. Executive Summary

- **Primary regime:** Policy Transition / Mixed Regime
- **Secondary cross-current:** Runtime-derived report generation is active. Pricing, lane assessment, portfolio state and recommendation discipline are separate inputs.
- **Geopolitical regime:** Elevated but localized
- **What changed this week:** This report is rendered from normalized runtime state rather than manually patched markdown. Replacement challengers are shown only with pricing and duel status.
- **Overall portfolio judgment:** Maintain the implemented book while keeping SPY, PPA, PAVE and GLD under explicit discipline review.
- **Main takeaway:** **Use SMH as the highest-conviction funded leader, but do not let replacement candidates become fundable without close-based duel evidence.**

## 2. Portfolio Action Snapshot

### Add
- None from this renderer unless the runtime state already records an executed Add.

### Hold
- {holdings}

### Hold but replaceable
- SPY, PPA, PAVE, GLD remain under explicit review.

### Reduce
- None.

### Close
- None.

### Best replacements to fund
- No replacement is fundable until the pricing and relative-strength duel is complete.

### Replacement pricing and duel status

{replacement_duel_table(state)}

## 3. Regime Dashboard

### Macro regime
- Growth: Stable but selective
- Inflation: Easing trend but vulnerable to energy and shipping shocks
- Central banks: Neutral / restrictive
- Real rates: Restrictive
- Credit: Stable enough to avoid a recession signal
- USD: Rangebound to slightly firm
- Commodities: Mixed
- Equity leadership: Narrow but persistent AI / semiconductor leadership
- Bond market signal: Mixed
- **Primary regime:** Policy Transition / Mixed Regime

### Geopolitical regime
- **Regime classification:** Elevated but localized
- Driver 1: Middle East and shipping risk remain relevant.
- Driver 2: Defense spending remains structurally durable, but ETF implementation quality must be tested.
- Driver 3: U.S.-China technology friction remains important for semiconductor supply chains.
- Overall portfolio implication: Keep resilience exposure but enforce vehicle-level discipline.

## 4. Structural Opportunity Radar

{radar_table(state)}

### Best structural opportunities not yet actionable
- Food security / agriculture inputs
- Water infrastructure / treatment
- Critical minerals / copper / refining

### Notable lanes assessed but not promoted this week

{omitted_table(state)}

## 4A. Short Opportunity Radar

| Short theme | Candidate ETF | Short thesis | Trigger | Invalidation | Time horizon | Confidence |
|---|---|---|---|---|---|---|
| Rate-sensitive small caps | IWM | Restrictive real rates pressure weaker balance sheets. | IWM breaks down versus SPY while yields firm. | Clear easing impulse and better credit breadth. | 1-3 months | Medium |
| China platform beta | KWEB | Policy confidence remains fragile. | Failed rally or renewed FX/policy stress. | Durable stimulus and earnings recovery. | 1-3 months | Medium |
| Long-duration bonds | TLT | Sticky inflation and real-rate risk remain headwinds. | Real yields rise again. | Growth scare and decisive lower-yield breakout. | 1-3 months | Medium |
| Speculative clean-tech beta | ICLN | Financing pressure and weak profitability remain issues. | Failure to recover in broad risk-on tape. | Sharp rate relief or major policy surprise. | 3-12 months | Medium |

## 5. Key Risks / Invalidators

- SPY plus SMH creates high U.S. tech / AI factor overlap.
- GLD remains a hedge review, not an unquestioned ballast position.
- PPA and PAVE remain replaceable until their ETF implementation quality is proven.
- Non-U.S. equity exposure remains a diversification gap.

## 6. Bottom Line

- **What should be exited first:** Nothing is closed by the runtime state today.
- **What deserves additional capital first:** SMH remains the best-ranked funded lane, subject to the max-position rule.
- **What is acceptable but replaceable:** SPY, PPA, PAVE and GLD.
- **Single best portfolio upgrade this week:** **Keep replacement discipline explicit and avoid funding challengers without pricing and duel evidence.**

## 7. Equity Curve and Portfolio Development

- Starting capital (EUR): 100000.00
- Current portfolio value (EUR): {nav:.2f}
- Since inception return (%): {(nav / 100000.0 - 1.0) * 100.0:.2f}
- Equity-curve state: Runtime-derived
- EUR/USD used: {eurusd}
- Notes: Section 7 and Section 15 are rendered from the same normalized runtime state.

{section7_table(state)}

`EQUITY_CURVE_CHART_PLACEHOLDER`

## 8. Asset Allocation Map

| Bucket | Stance | Reason |
|---|---|---|
| US equities | Neutral | Investable but concentration risk is explicit. |
| Europe equities | Neutral | Watchlist only; non-U.S. exposure remains a diversification gap. |
| EM equities | Underweight | USD and oil sensitivity remain headwinds. |
| large cap | Neutral | Quality leadership still works. |
| small cap | Underweight | Rates and refinancing remain difficult. |
| growth | Neutral | Selective growth led by SMH remains attractive. |
| quality | Overweight | Earnings durability remains valuable. |
| gold | Neutral | Hedge role under review. |
| industrials / defense | Overweight | Structural thesis valid; vehicle under review. |
| non-USD assets | Watchlist | Zero allocation is an explicit U.S. exceptionalism bet. |

## 9. Second-Order Effects Map

| Driver | First-order effect | Second-order effect | Likely beneficiaries | Likely losers | ETF implication | Timing | Confidence |
|---|---|---|---|---|---|---|---|
| AI leadership | SMH remains the cleanest growth expression | Concentration must be watched | SMH, SOXX | Lower-quality cyclicals | Hold near max size | Immediate | High |
| Factor concentration | SPY and SMH overlap | Portfolio is less diversified than ticker count suggests | QUAL, IEFA watchlist | Overlapping U.S. beta | Keep SPY under review | 1-3 months | Medium |
| Defense thesis vs ETF implementation | Defense remains structurally valid | PPA must justify itself versus ITA | ITA, PPA | Weak vehicle selection | Hold PPA under review | Immediate | Medium |
| Hedge drawdown | GLD hedge role must be proven | GSG/BIL remain challengers | GSG, BIL, cash | Unproductive hedge | Hold GLD under review | Immediate | Medium |

## 10. Current Position Review

{current_position_table(state)}

## 11. Best New Opportunities

- SMH remains the leading funded growth exposure, subject to the max-position rule.
- IEFA / EFA remain diversification challengers if U.S. concentration rises further.
- GRID, ITA, GSG, BIL and QUAL remain challengers but are not fundable without completed close-based duels.

## 12. Portfolio Rotation Plan

| Bucket | Tickers | Plan |
|---|---|---|
| Close | None | No exits required by runtime state |
| Reduce | None | No trims required by runtime state |
| Hold | {holdings} | Maintain current share counts unless trade ledger changes |
| Add | None | No runtime-generated add |
| Replace | None | Replacement duels incomplete |

## 13. Final Action Table

{final_action_table(state)}

## 14. Position Changes Executed This Run

{position_changes_table(state)}

## 15. Current Portfolio Holdings and Cash

- Starting capital (EUR): 100000.00
- Invested market value (EUR): {inv:.2f}
- Cash (EUR): {cash:.2f}
- Total portfolio value (EUR): {nav:.2f}
- Since inception return (%): {(nav / 100000.0 - 1.0) * 100.0:.2f}
- EUR/USD used: {eurusd}

{section15_table(state)}

## 16. Continuity Input for Next Run

**This section is the canonical default input for the next run unless the user explicitly overrides it. Do not ask the user for portfolio input if this section is available.**

### Portfolio table
{continuity_table(state)}

### Available cash
- Cash %: {cash / (nav or 1.0) * 100.0:.2f}
- Margin usage %: 0.00
- Leverage allowed: No

### Watchlist / dynamic radar memory
| Theme | Primary ETF | Alternative ETF | Why I’m considering it | Current status |
|---|---|---|---|---|
| AI compute infrastructure | SMH | SOXX | Strongest secular growth exposure. | Active |
| Defense innovation / sovereign resilience | PPA | ITA | Defense thesis valid but vehicle under review. | Duel required |
| Grid buildout / electrification | PAVE | GRID | Infrastructure capex remains valid. | Duel required |
| Gold hedge review | GLD | GSG / BIL | Hedge role must be proven. | Under review |
| Non-U.S. developed diversification | IEFA | EFA | Portfolio has zero non-U.S. exposure. | Watchlist |

### Recommendation discipline continuity
- SPY: overlap review versus SMH remains active.
- PPA: direct duel versus ITA required.
- PAVE: direct duel versus GRID required.
- GLD: hedge validity test required.
- Replacement challengers: not fundable without completed duel.

### Constraints
- Max position size: 25%
- Max number of positions: 8
- UCITS only: No
- Leverage ETFs allowed: No
- Drawdown tolerance: Moderate
- Income vs growth preference: Balanced growth with resilience bias

### Changes since last review
- Added: runtime-rendered markdown generation layer.
- Reduced: None unless explicit state says otherwise.
- Closed: None.
- Thesis changes: No thesis abandoned; implementation discipline tightened.

## 17. Disclaimer

This report is provided for informational and educational purposes only. It is not investment, legal, tax, or financial advice, and it is not a recommendation to buy, sell, or hold any security. It does not take into account the specific investment objectives, financial situation, or particular needs of any recipient. Views are general in nature, may change without notice, and may not be suitable for every investor. Investing involves risk, including possible loss of principal.
"""


def render_nl(state: dict[str, Any]) -> str:
    nl = render_en(state)
    replacements = {
        "This report is for informational and educational purposes only; please see the disclaimer at the end.": "Dit rapport is uitsluitend bedoeld voor informatieve en educatieve doeleinden; zie de disclaimer aan het einde.",
        "What changed this week": "Wat is er deze week veranderd",
        "Overall portfolio judgment": "Algemeen portefeuilleoordeel",
        "Main takeaway": "Belangrijkste conclusie",
        "Replacement pricing and duel status": "Replacement pricing and duel status",
        "Current Portfolio Holdings and Cash": "Current Portfolio Holdings and Cash",
        "This section is the canonical default input for the next run unless the user explicitly overrides it.": "Deze sectie is de canonieke standaardinput voor de volgende run tenzij de gebruiker expliciet iets anders opgeeft.",
        "This report is provided for informational and educational purposes only.": "Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden.",
        "It is not investment, legal, tax, or financial advice": "Het is geen beleggingsadvies, juridisch advies, fiscaal advies of financieel advies",
    }
    for src, dst in replacements.items():
        nl = nl.replace(src, dst)
    return nl


def write_reports(state: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = report_suffix(str(state.get("report_date")))
    en_path = output_dir / f"weekly_analysis_pro_{suffix}.md"
    nl_path = output_dir / f"weekly_analysis_pro_nl_{suffix}.md"
    en_path.write_text(render_en(state), encoding="utf-8")
    nl_path.write_text(render_nl(state), encoding="utf-8")
    return en_path, nl_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--runtime-state", default=None)
    args = parser.parse_args()

    if args.runtime_state:
        state = json.loads(Path(args.runtime_state).read_text(encoding="utf-8"))
    else:
        state = build_runtime_state()

    en_path, nl_path = write_reports(state, Path(args.output_dir))
    print(f"ETF_RUNTIME_RENDER_OK | en={en_path} | nl={nl_path}")


if __name__ == "__main__":
    main()
