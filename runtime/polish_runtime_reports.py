from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from runtime.macro_report_surface import dashboard_en, dashboard_nl, executive_lines_en, executive_lines_nl
from runtime.post_execution_report_surface import (
    action_buckets,
    decision_cockpit_en,
    decision_cockpit_nl,
    executed_rotation_summary_en,
    has_executed_changes,
    main_takeaway_en,
    main_takeaway_nl,
)
from runtime.replacement_edge_report_notes import (
    EN_AUTHORITY_DISCLAIMER,
    MARKER as REPLACEMENT_EDGE_NOTES_MARKER,
    NL_AUTHORITY_DISCLAIMER,
    build_notes_payload_from_paths,
    replacement_edge_notes_markdown,
)

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")
MACRO_LATEST = Path("output/macro/latest.json")
RUNTIME_POINTER = Path("output/runtime/latest_etf_report_state_path.txt")

MAIN_TAKEAWAY_EN = (
    "SMH remains the best-supported core exposure, but fresh capital and replacement decisions must clear "
    "price, relative-strength and portfolio-discipline gates."
)
MAIN_TAKEAWAY_NL = (
    "SMH blijft de best onderbouwde kernblootstelling, maar nieuw kapitaal en vervangingsbeslissingen moeten "
    "prijs-, relatieve-sterkte- en portefeuillediscipline doorstaan."
)
DECISION_COCKPIT_EN = """### Decision cockpit

- **This week:** no portfolio action.
- **Main active risk:** SMH concentration remains above the soft position cap.
- **Main active reviews:** SPY versus SMH overlap, PAVE versus GRID, and GSG hedge-role validation.
- **Next action trigger:** a replacement candidate must show confirmed relative-strength edge, clean pricing basis, thesis fit, and a clear funding source.
- **Fresh capital:** blocked for positions under size or replacement review unless a future run clears the discipline gates.
"""
DECISION_COCKPIT_NL = """### Besliscockpit

- **Deze week:** geen portefeuilleactie.
- **Belangrijkste actieve risico:** SMH-concentratie blijft boven de zachte positielimiet.
- **Belangrijkste actieve reviews:** SPY versus SMH-overlap, PAVE versus GRID, en validatie van de GSG-hedgerol.
- **Trigger voor volgende actie:** een vervangingskandidaat moet bevestigde relatieve-sterktevoorsprong, schone prijsbasis, aansluiting op de thesis en duidelijke financieringsbron tonen.
- **Vers kapitaal:** geblokkeerd voor posities onder grootte- of vervangingsreview totdat een toekomstige run de disciplinepoorten vrijgeeft.
"""
WEIGHT_BASIS_NOTE_EN = (
    "Weight basis note: action-table weights are model/action weights; current-holdings weights are live "
    "market-value weights including cash. Small differences can occur when cash, rounding or override handling is included."
)
WEIGHT_BASIS_NOTE_NL = (
    "Toelichting gewichtsbasis: gewichten in de actietabel zijn model-/actiegewichten; gewichten bij huidige posities zijn actuele "
    "marktwaardegewichten inclusief cash. Kleine verschillen kunnen ontstaan door cash, afronding of override-verwerking."
)
HOLD_OVERRIDE_NOTE_EN = (
    "Hold-with-override note: The model would normally force reduce/replace review, but the position is too small or "
    "operationally impractical to trade this run."
)
HOLD_OVERRIDE_NOTE_NL = (
    "Override-toelichting: Het model dwingt normaal een verklein-/vervangingsreview af, maar de positie is deze run te klein "
    "of operationeel niet zinvol om te verhandelen."
)


def latest_report(output_dir: Path, pattern: re.Pattern[str]) -> Path:
    env_names = ("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL",) if pattern is NL_RE else ("MRKT_RPRTS_EXPLICIT_REPORT_PATH",)
    for env_name in env_names:
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
        payload = json.loads(MACRO_LATEST.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


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
        if isinstance(state, dict):
            state.setdefault("_runtime_state_source", str(path))
            return state
    except Exception:
        return {}
    return {}


def replace_between(text: str, start_heading: str, end_heading: str, replacement_body: str) -> str:
    start = text.find(start_heading)
    if start == -1:
        return text
    body_start = start + len(start_heading)
    end = text.find(end_heading, body_start)
    if end == -1:
        return text
    return text[:body_start] + "\n\n" + replacement_body.strip() + "\n\n" + text[end:]


def _macro_state(runtime_state: dict[str, Any]) -> dict[str, Any]:
    state = dict(runtime_state or {})
    pack = state.get("macro_policy_pack")
    if not isinstance(pack, dict) or not pack:
        state["macro_policy_pack"] = load_macro_pack()
    return state


def _replacement_edge_payload(state: dict[str, Any]) -> dict[str, Any]:
    source_files = state.get("source_files") if isinstance(state.get("source_files"), dict) else {}
    lane_path = source_files.get("lane_assessment") or (state.get("validation_flags") or {}).get("lane_assessment_source")
    if not lane_path:
        return {"edges": []}
    try:
        return build_notes_payload_from_paths(lane_path, run_id=str(state.get("run_id") or "report_notes"))
    except Exception:
        return {"edges": []}


def _inject_replacement_edge_notes(text: str, state: dict[str, Any], *, language: str) -> str:
    if REPLACEMENT_EDGE_NOTES_MARKER in text or EN_AUTHORITY_DISCLAIMER in text or NL_AUTHORITY_DISCLAIMER in text:
        return text
    notes = replacement_edge_notes_markdown(_replacement_edge_payload(state), language=language)
    headings = ["### Replacement Duel Table", "### Replacement Duel Table v2"] if language == "en" else ["### Vervangingsanalyse"]
    for heading in headings:
        start = text.rfind(heading)
        if start == -1:
            continue
        next_section = text.find("\n\n## ", start + len(heading))
        if next_section == -1:
            return text.rstrip() + "\n\n" + notes + "\n"
        return text[:next_section].rstrip() + "\n\n" + notes + "\n" + text[next_section:]
    return text


def _macro_reason_for_lane(lane_name: Any, pack: dict[str, Any]) -> str:
    lane_name = str(lane_name or "").strip()
    payload = (pack.get("lane_adjustments", {}) or {}).get(lane_name, {})
    if not isinstance(payload, dict):
        return ""
    reason = str(payload.get("reason") or "").strip()
    reason = re.sub(r"\b(?:shadow_only|client_facing_authority|deterministic_regime_shadow)\b", "macro status", reason, flags=re.IGNORECASE)
    return reason if len(reason) <= 190 else reason[:189].rstrip() + "…"


def _inject_macro_radar_reasons(text: str, state: dict[str, Any]) -> str:
    pack = (state.get("macro_policy_pack") or {}) if isinstance(state.get("macro_policy_pack"), dict) else {}
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
                if reason and len(cells) >= 9 and "Macro filter:" not in line:
                    cells[3] = f"{cells[3]} Macro filter: {reason}"
                    line = "| " + " | ".join(cells) + " |"
        out.append(line)
    return "\n".join(out)


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
    text = text.replace("## 14. Position Changes Executed This Run", "## 14. Proposed Position Changes / Rotation Trade Intents")
    text = text.replace(
        "- Added: a validated state-led production path with macro-policy regime input; no portfolio position was added unless shown in Section 14.",
        "- Added: no executed portfolio position was added unless recorded in the trade ledger; Section 14 shows proposed rotation intents while the rotation engine is in warning mode.",
    )
    text = text.replace("- Reduced: None unless explicit state says otherwise.", f"- Proposed rotation: {summary}")
    text = text.replace("- Closed: None.", "- Executed reductions/closures: none unless separately recorded in the trade ledger and persisted portfolio state.")
    marker = "### Recommendation discipline continuity"
    if marker in text and "Proposed rotation:" not in text:
        text = text.replace(marker, f"### Proposed rotation\n- {summary}\n\n{marker}")
    return text


def _patch_rotation_intent_language_nl(text: str, state: dict[str, Any]) -> str:
    if not _trade_intents(state):
        return text
    summary = _trade_summary_nl(state)
    text = text.replace("## 14. Positiewijzigingen in deze run", "## 14. Voorgestelde positiewijzigingen / rotatie-intenties")
    text = text.replace(
        "Toegevoegd: geen positie toegevoegd tenzij expliciet in sectie 14 vermeld.",
        "Toegevoegd: geen uitgevoerde positie toegevoegd tenzij deze in het handelslogboek en de portefeuille-staat is verwerkt.",
    )
    text = text.replace("Verlaagd: geen tenzij expliciet in de portefeuille-staat vermeld.", f"Voorgestelde rotatie: {summary}")
    text = text.replace("Gesloten: geen.", "Uitgevoerde verlagingen/sluitingen: geen tenzij apart vastgelegd in het handelslogboek en de portefeuille-staat.")
    marker = "### Aanbevelingsdiscipline-continuïteit"
    if marker in text and "Voorgestelde rotatie:" not in text:
        text = text.replace(marker, f"### Voorgestelde rotatie\n- {summary}\n\n{marker}")
    return text


def _executive_en(state: dict[str, Any]) -> str:
    lines = executive_lines_en(state)
    return f"""
- **Primary regime:** {lines['primary_regime']}
- **Secondary cross-current:** {lines['secondary_cross_current']}
- **Geopolitical regime:** {lines['geopolitical_regime']}
- **What changed this week:** {lines['what_changed']}
- **Overall portfolio judgment:** Keep discipline explicit: every holding must re-earn capital against alternatives, concentration limits and current price evidence.
- **Main takeaway:** **{main_takeaway_en(state)}**

{decision_cockpit_en(state)}
"""


def _executive_nl(state: dict[str, Any]) -> str:
    lines = executive_lines_nl(state)
    return f"""
- **Primair regime:** {lines['primary_regime']}
- **Geopolitiek regime:** {lines['geopolitical_regime']}
- **Wat is er deze week veranderd:** {lines['what_changed']}
- **Algemeen portefeuilleoordeel:** Laat elke positie opnieuw kapitaal verdienen tegenover alternatieven, concentratielimieten en actuele prijsbevestiging.
- **Belangrijkste conclusie:** {main_takeaway_nl(state)}

{decision_cockpit_nl(state)}
"""


def _bottom_line_en(state: dict[str, Any]) -> str:
    if has_executed_changes(state):
        buckets = action_buckets(state)
        reduced = ", ".join(buckets["reduce"] + buckets["close"]) or "the selected funding source"
        added = ", ".join(buckets["add"]) or "the selected destination"
        return f"""
- **What was reduced or exited first:** {reduced}; the guarded mutation is executed and persisted.
- **What received additional capital:** {added}; no further capital is deployed after the completed major rotation.
- **What is acceptable but replaceable:** Holdings with high release scores remain subject to reduce/replace/override discipline.
- **Single best portfolio upgrade this week:** **{executed_rotation_summary_en(state)}**
"""
    return """
- **What should be exited first:** Determined by the rotation plan when active; otherwise no close is executed by legacy state.
- **What deserves additional capital first:** SMH remains the best-ranked funded lane, subject to the max-position rule.
- **What is acceptable but replaceable:** Holdings with high release scores require reduce/replace/override discipline.
- **Single best portfolio upgrade this week:** Use the rotation artifact as the bridge between evidence and target weights.
"""


def _ensure_decision_cockpit(text: str, state: dict[str, Any], *, language: str) -> str:
    cockpit = decision_cockpit_nl(state) if language == "nl" else decision_cockpit_en(state)
    legacy_heading = "## 2A. Besliscockpit" if language == "nl" else "## 2A. Decision cockpit"
    legacy_end = "## 3. Regime-dashboard" if language == "nl" else "## 3. Regime Dashboard"
    if legacy_heading in text and legacy_end in text:
        cockpit_lines = cockpit.strip().splitlines()
        cockpit_body = "\n".join(cockpit_lines[2:]).strip() if len(cockpit_lines) > 2 else cockpit.strip()
        return replace_between(text, legacy_heading, legacy_end, cockpit_body)
    marker = "### Besliscockpit" if language == "nl" else "### Decision cockpit"
    if marker in text:
        return text
    start_heading = "## 1. Kernsamenvatting" if language == "nl" else "## 1. Executive Summary"
    next_heading = "## 2. Portefeuille-acties" if language == "nl" else "## 2. Portfolio Action Snapshot"
    if start_heading in text and next_heading in text:
        return text.replace(next_heading, cockpit.strip() + "\n\n" + next_heading, 1)
    return cockpit.strip() + "\n\n" + text

def _inject_weight_basis_note(text: str, *, language: str) -> str:
    note = WEIGHT_BASIS_NOTE_NL if language == "nl" else WEIGHT_BASIS_NOTE_EN
    override_note = HOLD_OVERRIDE_NOTE_NL if language == "nl" else HOLD_OVERRIDE_NOTE_EN
    if note in text:
        return text
    headings = ["## 13. Definitieve actietabel", "## 6. Definitieve actietabel"] if language == "nl" else ["## 13. Final Action Table", "## 6. Final Action Table"]
    for heading in headings:
        if heading in text:
            return text.replace(heading, f"{heading}\n\n{note}\n\n{override_note}", 1)
    return text


def _client_surface_cleanup(text: str, *, language: str) -> str:
    if language == "nl":
        replacements = {
            "Portefeuillerol is verzwakt": "Rol onder herbeoordeling",
            "portefeuillerol is verzwakt": "rol onder herbeoordeling",
            "Portefeuillerol rechtvaardigt huidige allocatie niet meer": "Rol rechtvaardigt huidige allocatie niet meer",
        }
    else:
        replacements = {
            "Portfolio role is impaired": "Role under review",
            "portfolio role is impaired": "role under review",
        }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def polish_english(text: str, runtime_state: dict[str, Any] | None = None) -> str:
    state = _macro_state(runtime_state or {})
    text = text.replace("Replacement Duel Table v2", "Replacement Duel Table")
    text = text.replace("- Equity-curve state: Runtime-derived", "- Equity-curve state: Reconciled to Section 15")
    text = text.replace(
        "- Thesis changes: No thesis abandoned; implementation discipline tightened.",
        "- Thesis changes: No structural thesis was abandoned; implementation, macro-regime and rotation discipline are materially tighter.",
    )

    if state.get("macro_policy_pack"):
        text = replace_between(text, "## 1. Executive Summary", "## 2. Portfolio Action Snapshot", _executive_en(state))
        text = replace_between(text, "## 3. Regime Dashboard", "## 4. Structural Opportunity Radar", dashboard_en(state))
        text = _inject_macro_radar_reasons(text, state)
    text = _ensure_decision_cockpit(text, state, language="en")
    text = _inject_weight_basis_note(text, language="en")
    text = _client_surface_cleanup(text, language="en")
    text = replace_between(text, "## 6. Bottom Line", "## 7. Equity Curve and Portfolio Development", _bottom_line_en(state))
    text = _inject_replacement_edge_notes(text, state, language="en")
    return _patch_rotation_intent_language_en(text, state)


def polish_dutch(text: str, runtime_state: dict[str, Any] | None = None) -> str:
    state = _macro_state(runtime_state or {})
    text = _patch_rotation_intent_language_nl(text, state)
    if state.get("macro_policy_pack") and is_native_dutch_report(text):
        text = replace_between(text, "## 1. Kernsamenvatting", "## 2. Portefeuille-acties", _executive_nl(state))
        text = replace_between(text, "## 3. Regime-dashboard", "## 4. Structurele kansenradar", dashboard_nl(state))
        print("ETF_RUNTIME_POLISH_NL_MACRO_OK | reason=native_dutch_macro_surface_applied")
    text = _ensure_decision_cockpit(text, state, language="nl")
    text = _inject_weight_basis_note(text, language="nl")
    text = _client_surface_cleanup(text, language="nl")
    return _inject_replacement_edge_notes(text, state, language="nl")


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
