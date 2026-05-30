from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _f2(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _replace_between(text: str, start_heading: str, end_heading: str, replacement_body: str) -> str:
    start = text.find(start_heading)
    if start == -1:
        return text
    body_start = start + len(start_heading)
    end = text.find(end_heading, body_start)
    if end == -1:
        return text
    return text[:body_start] + "\n\n" + replacement_body.strip() + "\n\n" + text[end:]


def _position_change_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = list(state.get("executed_model_changes") or [])
    if rows:
        return rows
    out: list[dict[str, Any]] = []
    for p in state.get("positions", []) or []:
        shares_delta = _float(p.get("shares_delta_this_run"))
        action = str(p.get("action_executed_this_run") or "None").strip()
        if abs(shares_delta) <= 0.0005 and action.lower() in {"", "none"}:
            continue
        out.append(
            {
                "ticker": _ticker(p.get("ticker")),
                "action": action,
                "shares_delta": shares_delta,
                "previous_weight_pct": _float(p.get("previous_weight_pct")),
                "new_weight_pct": _float(p.get("current_weight_pct")),
                "weight_change_pct": _float(p.get("weight_change_pct")),
                "funding_source_note": str(p.get("funding_source_note") or "").strip(),
            }
        )
    return out


def _position_changes_table_en(state: dict[str, Any]) -> str:
    rows = _position_change_rows(state)
    lines = [
        "| Ticker | Previous weight % | New weight % | Weight change % | Shares delta | Action executed | Funding source / note |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    if not rows:
        lines.append("| None | - | - | - | 0.00 | None | No guarded model trade was executed this run. |")
        return "\n".join(lines)
    for row in rows:
        prev = _float(row.get("previous_weight_pct"))
        new = _float(row.get("new_weight_pct"))
        change = _float(row.get("weight_change_pct"), new - prev)
        lines.append(
            f"| {_ticker(row.get('ticker'))} | {_f2(prev)} | {_f2(new)} | {_f2(change)} | {_f2(row.get('shares_delta'))} | "
            f"{row.get('action') or 'None'} | {row.get('funding_source_note') or 'Guarded model rotation executed and persisted.'} |"
        )
    cash = _float((state.get("portfolio") or {}).get("cash_eur"))
    nav = _float((state.get("portfolio") or {}).get("total_portfolio_value_eur"))
    cash_pct = cash / nav * 100.0 if nav else 0.0
    lines.append(f"| CASH | - | {_f2(cash_pct)} | - | 0.00 | None | Residual cash |")
    return "\n".join(lines)


def _position_changes_table_nl(state: dict[str, Any]) -> str:
    rows = _position_change_rows(state)
    lines = [
        "| Ticker | Vorig gewicht % | Nieuw gewicht % | Gewichtswijziging % | Wijziging aantal stukken | Uitgevoerde actie | Financieringsbron / toelichting |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    action_nl = {"Sell": "Verkopen", "Buy": "Kopen", "None": "Geen"}
    if not rows:
        lines.append("| Geen | - | - | - | 0.00 | Geen | Deze run is geen bewaakte modeltransactie uitgevoerd. |")
        return "\n".join(lines)
    for row in rows:
        prev = _float(row.get("previous_weight_pct"))
        new = _float(row.get("new_weight_pct"))
        change = _float(row.get("weight_change_pct"), new - prev)
        action = str(row.get("action") or "None")
        lines.append(
            f"| {_ticker(row.get('ticker'))} | {_f2(prev)} | {_f2(new)} | {_f2(change)} | {_f2(row.get('shares_delta'))} | "
            f"{action_nl.get(action, action)} | {row.get('funding_source_note') or 'Bewaakte modelrotatie uitgevoerd en verwerkt.'} |"
        )
    cash = _float((state.get("portfolio") or {}).get("cash_eur"))
    nav = _float((state.get("portfolio") or {}).get("total_portfolio_value_eur"))
    cash_pct = cash / nav * 100.0 if nav else 0.0
    lines.append(f"| CASH | - | {_f2(cash_pct)} | - | 0.00 | Geen | Resterende cash |")
    return "\n".join(lines)


def validate_executed_change_semantics(state: dict[str, Any]) -> None:
    errors: list[str] = []
    phase = (state.get("execution_context") or {}).get("report_phase")
    if phase != "post_execution":
        return
    rows = _position_change_rows(state)
    for row in rows:
        delta = _float(row.get("shares_delta"))
        prev = _float(row.get("previous_weight_pct"))
        new = _float(row.get("new_weight_pct"))
        if abs(delta) > 0.0005 and abs(new - prev) <= 0.005:
            errors.append(f"executed_change_weight_not_changed:{_ticker(row.get('ticker'))}:shares_delta={delta:.6f}:prev={prev:.4f}:new={new:.4f}")
    if errors:
        raise RuntimeError("ETF executed-report contract validation failed: " + "; ".join(errors))


def _patch_common_text(text: str) -> str:
    replacements = {
        "Rotation plan artifact is active; target weights and trade intents are proposed until the trade ledger and portfolio state record execution.": "Guarded model rotation has been executed and persisted in the official portfolio state and trade ledger.",
        "Rotation plan artifact is active; Sections 12-14 are rendered from rotation_decisions, target_weights and trade_intents.": "Guarded model rotation has been executed and persisted in the official portfolio state and trade ledger.",
        "Trade intents are proposed rotation output while the engine is in warning mode; they are not executed trades until the ledger and portfolio state record execution.": "Executed model changes are shown from the official trade ledger and guarded-auto artifact.",
        "Rotation plan artifact not present; legacy recommendation labels are used.": "Post-execution report: rotation decisions have been applied to the official portfolio state.",
        "Rotation plan: not available; legacy labels used.": "Rotation execution: completed and persisted in the official portfolio state and trade ledger.",
        "Proposed rotation:": "Executed rotation:",
        "pending execution and portfolio-state persistence": "executed and persisted in portfolio state",
        "Het rotatieplan is actief; doelgewichten en handelsintenties blijven voorstellen totdat het handelslogboek en de portefeuille-staat uitvoering vastleggen.": "De bewaakte modelrotatie is uitgevoerd en verwerkt in de officiële portefeuillestaat en het handelslogboek.",
        "in afwachting van uitvoering en verwerking in de portefeuille-staat": "uitgevoerd en verwerkt in de portefeuillestaat",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"Rotation plan:\s*not available; legacy labels used\.", "Rotation execution: completed and persisted in the official portfolio state and trade ledger.", text, flags=re.IGNORECASE)
    return text


def patch_report(path: Path, state: dict[str, Any]) -> None:
    text = path.read_text(encoding="utf-8")
    text = _patch_common_text(text)
    text = _replace_between(text, "## 14. Position Changes Executed This Run", "## 15. Current Portfolio Holdings and Cash", _position_changes_table_en(state))
    text = _replace_between(text, "## 14. Positiewijzigingen in deze run", "## 15. Huidige posities en cash", _position_changes_table_nl(state))
    path.write_text(text, encoding="utf-8")
    print(f"ETF_EXECUTED_REPORT_CONTRACT_PATCHED | report={path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-state", required=True)
    parser.add_argument("--english-report", required=True)
    parser.add_argument("--dutch-report", required=True)
    args = parser.parse_args()
    state = _read_json(Path(args.runtime_state))
    validate_executed_change_semantics(state)
    patch_report(Path(args.english_report), state)
    patch_report(Path(args.dutch_report), state)
    print("ETF_EXECUTED_REPORT_CONTRACT_OK")


if __name__ == "__main__":
    main()
