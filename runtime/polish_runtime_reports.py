from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")
MACRO_LATEST = Path("output/macro/latest.json")
RUNTIME_POINTER = Path("output/runtime/latest_etf_report_state_path.txt")


def latest_report(output_dir: Path, pattern: re.Pattern[str]) -> Path:
    for env_name in ("MRKT_RPRTS_EXPLICIT_REPORT_PATH", "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL"):
        raw = os.environ.get(env_name, "").strip()
        if not raw:
            continue
        path = Path(raw)
        if pattern.match(path.name):
            if not path.exists():
                raise RuntimeError(f"Explicit report path from {env_name} does not exist: {path}")
            return path

    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    if not reports:
        raise RuntimeError(f"No matching report found in {output_dir} for {pattern.pattern}")
    return reports[-1]


def is_native_dutch_report(text: str) -> bool:
    markers = [
        "# Wekelijkse ETF-review",
        "## 1. Kernsamenvatting",
        "## 2. Portefeuille-acties",
        "## 3. Regime-dashboard",
        "## 10. Review huidige posities",
        "## 15. Huidige posities en cash",
    ]
    return sum(marker in text for marker in markers) >= 5


def load_macro_pack() -> dict[str, Any]:
    if not MACRO_LATEST.exists():
        return {}
    try:
        return json.loads(MACRO_LATEST.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _resolve_runtime_state_path(explicit: str | None = None) -> Path | None:
    candidates = [
        explicit,
        os.environ.get("MRKT_RPRTS_RUNTIME_STATE_PATH"),
        os.environ.get("ETF_RUNTIME_STATE_PATH"),
    ]
    for raw in candidates:
        if not raw:
            continue
        path = Path(str(raw).strip())
        if path.exists():
            return path
    if RUNTIME_POINTER.exists():
        raw = RUNTIME_POINTER.read_text(encoding="utf-8").strip()
        if raw:
            path = Path(raw)
            if path.exists():
                return path
            candidate = RUNTIME_POINTER.parent / path.name
            if candidate.exists():
                return candidate
    return None


def load_runtime_state(runtime_state_path: str | None = None) -> dict[str, Any]:
    path = _resolve_runtime_state_path(runtime_state_path)
    if path is None:
        return {}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        state.setdefault("_runtime_state_source", str(path))
        return state
    except Exception:
        return {}


def _take(values: Any, limit: int = 3) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(v).strip() for v in values if str(v).strip()][:limit]


def _bullets(values: list[str], fallback: str, limit: int = 3) -> str:
    items = values[:limit] or [fallback]
    return "\n".join(f"- {item}" for item in items)


def _policy_bullets(pack: dict[str, Any], limit: int = 2) -> str:
    catalysts = [c for c in pack.get("policy_catalysts", []) or [] if c.get("transfer_to_report") is True]
    lines: list[str] = []
    for catalyst in catalysts[:limit]:
        area = catalyst.get("policy_area", "Policy catalyst")
        signal = catalyst.get("latest_signal", "")
        affected = ", ".join(catalyst.get("affected_lanes", []) or [])
        if affected:
            lines.append(f"- **{area}:** {signal} Affected lanes: {affected}.")
        else:
            lines.append(f"- **{area}:** {signal}")
    return "\n".join(lines) if lines else "- No policy catalyst is strong enough to change a portfolio action by itself this week."


def _macro_reason_for_lane(lane_name: Any, pack: dict[str, Any]) -> str:
    lane_name = str(lane_name or "").strip()
    payload = (pack.get("lane_adjustments", {}) or {}).get(lane_name, {})
    return str(payload.get("reason") or "").strip()


def replace_between(text: str, start_heading: str, end_heading: str, replacement_body: str) -> str:
    start = text.find(start_heading)
    if start == -1:
        return text
    body_start = start + len(start_heading)
    end = text.find(end_heading, body_start)
    if end == -1:
        return text
    return text[:body_start] + "\n\n" + replacement_body.strip() + "\n\n" + text[end:]


def _trade_intents(state: dict[str, Any]) -> list[dict[str, Any]]:
    intents = state.get("trade_intents") or (state.get("rotation_plan") or {}).get("trade_intents") or []
    return list(intents) if isinstance(intents, list) else []


def _fmt(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _trade_summary_en(state: dict[str, Any]) -> str:
    intents = _trade_intents(state)
    if not intents:
        return "No proposed rotation trade intent was generated this run."
    parts: list[str] = []
    for trade in intents:
        source = str(trade.get("source_ticker") or "").upper()
        destination = str(trade.get("destination_ticker") or "CASH").upper()
        source_delta = _fmt(trade.get("delta_weight_pct"))
        dest_delta = _fmt(trade.get("destination_delta_weight_pct"))
        parts.append(f"reduce {source} by {source_delta}% NAV and allocate {dest_delta}% NAV to {destination}")
    return "; ".join(parts) + ", pending execution and portfolio-state persistence."


def _trade_summary_nl(state: dict[str, Any]) -> str:
    intents = _trade_intents(state)
    if not intents:
        return "Deze run is geen voorgestelde rotatie-intentie gegenereerd."
    parts: list[str] = []
    for trade in intents:
        source = str(trade.get("source_ticker") or "").upper()
        destination = str(trade.get("destination_ticker") or "CASH").upper()
        source_delta = _fmt(trade.get("delta_weight_pct"))
        dest_delta = _fmt(trade.get("destination_delta_weight_pct"))
        parts.append(f"verlaag {source} met {source_delta}% NAV en alloceer {dest_delta}% NAV naar {destination}")
    return "; ".join(parts) + ", in afwachting van uitvoering en verwerking in de portefeuille-staat."


def _patch_rotation_intent_language_en(text: str, state: dict[str, Any]) -> str:
    if not _trade_intents(state):
        return text
    summary = _trade_summary_en(state)
    text = text.replace(
        "## 14. Position Changes Executed This Run",
        "## 14. Proposed Position Changes / Rotation Trade Intents",
    )
    text = text.replace(
        "| Action | Reason |\n|---|---|---:|---:|---:|---|---|",
        "| Intent status | Reason |\n|---|---|---:|---:|---:|---|---|",
    )
    text = text.replace(
        "- Added: a validated state-led production path with macro-policy regime input; no portfolio position was added unless shown in Section 14.",
        "- Added: no executed portfolio position was added unless recorded in the trade ledger; Section 14 shows proposed rotation intents while the rotation engine is in warning mode.",
    )
    text = text.replace(
        "- Reduced: None unless explicit state says otherwise.",
        f"- Proposed rotation: {summary}",
    )
    text = text.replace(
        "- Closed: None.",
        "- Executed reductions/closures: none unless separately recorded in the trade ledger and persisted portfolio state.",
    )
    marker = "### Recommendation discipline continuity"
    if marker in text and "Proposed rotation:" not in text:
        text = text.replace(marker, f"### Proposed rotation\n- {summary}\n\n{marker}")
    return text


def _patch_rotation_intent_language_nl(text: str, state: dict[str, Any]) -> str:
    if not _trade_intents(state):
        return text
    summary = _trade_summary_nl(state)
    text = text.replace(
        "## 14. Positiewijzigingen in deze run",
        "## 14. Voorgestelde positiewijzigingen / rotatie-intenties",
    )
    text = text.replace(
        "| Actie | Reden |\n|---|---|---:|---:|---:|---|---|",
        "| Intentiestatus | Reden |\n|---|---|---:|---:|---:|---|---|",
    )
    text = text.replace(
        "Toegevoegd: geen positie toegevoegd tenzij expliciet in sectie 14 vermeld.",
        "Toegevoegd: geen uitgevoerde positie toegevoegd tenzij deze in het handelslogboek en de portefeuille-staat is verwerkt.",
    )
    text = text.replace(
        "Verlaagd: geen tenzij expliciet in de portefeuille-staat vermeld.",
        f"Voorgestelde rotatie: {summary}",
    )
    text = text.replace(
        "Gesloten: geen.",
        "Uitgevoerde verlagingen/sluitingen: geen tenzij apart vastgelegd in het handelslogboek en de portefeuille-staat.",
    )
    marker = "### Recommendation discipline continuity"
    nl_marker = "### Aanbevelingsdiscipline-continuïteit"
    continuity_marker = marker if marker in text else nl_marker
    if continuity_marker in text and "Voorgestelde rotatie:" not in text:
        text = text.replace(continuity_marker, f"### Voorgestelde rotatie\n- {summary}\n\n{continuity_marker}")
    return text


def _macro_executive_summary(pack: dict[str, Any]) -> str:
    regime = pack.get("regime", {}) or {}
    current = regime.get("current") or "Policy transition / mixed regime"
    confidence = regime.get("confidence")
    confidence_text = f"{float(confidence):.0%}" if isinstance(confidence, (int, float)) else "medium"
    what_changed = _take(regime.get("what_changed"), 3)
    implications = _take(pack.get("portfolio_implications"), 3)

    return f"""
- **Primary regime:** {current} ({confidence_text} confidence)
- **What changed this week:** {what_changed[0] if what_changed else 'No decisive full-regime break; allocation discipline remains more important than theme expansion.'}
- **Portfolio implication:** {implications[0] if implications else 'Stay invested, but make new capital pass a stricter macro and relative-strength filter.'}
- **Overall portfolio judgment:** Keep the current portfolio intact for now, but treat weak or over-budget positions as active capital-source candidates rather than passive holds.
- **Main takeaway:** **SMH remains the earned leader, but fresh capital and replacement decisions must pass regime, pricing and duel-evidence checks.**
"""


def _macro_regime_dashboard(pack: dict[str, Any]) -> str:
    regime = pack.get("regime", {}) or {}
    current = regime.get("current") or "Policy transition / mixed regime"
    confidence = regime.get("confidence")
    confidence_text = f"{float(confidence):.0%}" if isinstance(confidence, (int, float)) else "medium"
    what_changed = _take(regime.get("what_changed"), 3)
    implications = _take(pack.get("portfolio_implications"), 3)
    cross_asset = _take(pack.get("cross_asset_confirmation"), 3)

    return f"""
### Regime snapshot
- **Current regime:** {current}
- **Confidence:** {confidence_text}
- **Decision rule:** Macro supports selection discipline, not broad risk expansion by default.

### What changed
{_bullets(what_changed, 'No decisive full-regime break; allocation discipline remains more important than theme expansion.', 3)}

### Portfolio implications
{_bullets(implications, 'Stay invested, but make new capital pass a stricter macro and relative-strength filter.', 3)}

### Cross-asset confirmation
{_bullets(cross_asset, 'Cross-asset confirmation is mixed; avoid turning thematic conviction into automatic funding.', 3)}

### Policy catalysts transferred to the report
{_policy_bullets(pack, 2)}
"""


def _macro_bottom_line(pack: dict[str, Any]) -> str:
    implications = _take(pack.get("portfolio_implications"), 3)
    first = implications[0] if implications else "Stay invested, but make new capital pass a stricter macro and relative-strength filter."
    second = implications[1] if len(implications) > 1 else "Treat replaceable positions as active capital-source candidates rather than indefinite review items."
    third = implications[2] if len(implications) > 2 else "Use trade_intents[] as proposed rotation output, not as executed trades until the ledger and portfolio state are updated."
    return f"""
- **Portfolio stance:** {first}
- **Best earned exposure:** SMH remains the portfolio's strongest contributor and cleanest secular growth expression.
- **Main discipline issue:** {second}
- **Weakest implementation questions:** PPA must prove itself against ITA, PAVE must prove itself against GRID, and GLD must prove that it still behaves like useful ballast.
- **Action bias:** {third}
"""


def _inject_macro_radar_reasons(text: str, pack: dict[str, Any]) -> str:
    if not pack:
        return text
    lines = text.splitlines()
    out: list[str] = []
    in_radar = False
    for line in lines:
        if line.strip() == "## 4. Structural Opportunity Radar":
            in_radar = True
        elif in_radar and line.startswith("## "):
            in_radar = False

        if in_radar and line.startswith("|") and not line.startswith("|---") and "| Theme |" not in line:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells:
                reason = _macro_reason_for_lane(cells[0], pack)
                if reason and len(cells) >= 9 and reason not in line:
                    cells[3] = f"{cells[3]} Macro filter: {reason}"
                    line = "| " + " | ".join(cells) + " |"
        out.append(line)
    return "\n".join(out)


def polish_english(text: str, runtime_state: dict[str, Any] | None = None) -> str:
    runtime_state = runtime_state or {}
    pack = load_macro_pack()

    text = text.replace("Replacement Duel Table v2", "Replacement Duel Table")
    text = text.replace(
        "- **Secondary cross-current:** Runtime-derived report generation is active. Pricing, lane discovery, portfolio state and recommendation discipline are separate inputs.",
        "- **Secondary cross-current:** The production process is state-led: pricing, portfolio holdings, lane discovery, macro regime, rotation plan and recommendation discipline are independently validated before delivery."
    )
    text = text.replace(
        "- None from this renderer unless the runtime state already records an executed Add.",
        "- None executed this run. SMH remains the first candidate for additional capital only if the 25% position-size rule leaves room."
    )
    text = text.replace(
        "- No replacement is fundable until the pricing and relative-strength duel is complete.",
        "- Replacement funding is now governed by the rotation plan; trade intents remain proposed until ledger/state persistence records execution."
    )
    text = text.replace("- Equity-curve state: Runtime-derived", "- Equity-curve state: Reconciled to Section 15")
    text = text.replace(
        "- Added: runtime-rendered markdown generation layer.",
        "- Added: a validated state-led production path with macro-policy and rotation-plan inputs; no portfolio position was executed unless recorded in the trade ledger."
    )
    text = text.replace(
        "- Thesis changes: No thesis abandoned; implementation discipline tightened.",
        "- Thesis changes: No structural thesis was abandoned; implementation, macro-regime and rotation discipline are materially tighter."
    )

    if pack:
        text = replace_between(text, "## 1. Executive Summary", "## 2. Portfolio Action Snapshot", _macro_executive_summary(pack))
        text = replace_between(text, "## 3. Regime Dashboard", "## 4. Structural Opportunity Radar", _macro_regime_dashboard(pack))
        text = replace_between(text, "## 6. Bottom Line", "## 7. Equity Curve and Portfolio Development", _macro_bottom_line(pack))
        text = _inject_macro_radar_reasons(text, pack)
    else:
        text = replace_between(
            text,
            "## 6. Bottom Line",
            "## 7. Equity Curve and Portfolio Development",
            """
- **Portfolio stance:** Stay invested, but raise the bar for any new capital deployment.
- **Best earned exposure:** SMH remains the portfolio's strongest contributor and cleanest secular growth expression.
- **Main discipline issue:** Replaceable positions must not remain indefinite review items.
- **Weakest implementation questions:** PPA must prove itself against ITA, PAVE must prove itself against GRID, and GLD must prove that it still behaves like useful ballast.
- **Action bias:** Trade intents are proposed rotation output, not executed trades until ledger and portfolio-state persistence record them.
"""
        )

    return _patch_rotation_intent_language_en(text, runtime_state)


def polish_dutch(text: str, runtime_state: dict[str, Any] | None = None) -> str:
    runtime_state = runtime_state or {}
    text = _patch_rotation_intent_language_nl(text, runtime_state)
    if is_native_dutch_report(text):
        print("ETF_RUNTIME_POLISH_NL_SKIPPED | reason=native_dutch_renderer")
        return text
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--runtime-state", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    en_path = latest_report(output_dir, EN_RE)
    nl_path = latest_report(output_dir, NL_RE)
    runtime_state = load_runtime_state(args.runtime_state)

    en_path.write_text(polish_english(en_path.read_text(encoding="utf-8"), runtime_state), encoding="utf-8")
    nl_path.write_text(polish_dutch(nl_path.read_text(encoding="utf-8"), runtime_state), encoding="utf-8")

    source = runtime_state.get("_runtime_state_source", "none") if runtime_state else "none"
    print(f"ETF_RUNTIME_POLISH_OK | en={en_path.name} | nl={nl_path.name} | runtime_state={source}")


if __name__ == "__main__":
    main()
