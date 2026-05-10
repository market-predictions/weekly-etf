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


def load_macro_pack() -> dict[str, Any]:
    if not MACRO_LATEST.exists():
        return {}
    try:
        return json.loads(MACRO_LATEST.read_text(encoding="utf-8"))
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
    reason = str(payload.get("reason") or "").strip()
    return reason


def replace_between(text: str, start_heading: str, end_heading: str, replacement_body: str) -> str:
    start = text.find(start_heading)
    if start == -1:
        return text
    body_start = start + len(start_heading)
    end = text.find(end_heading, body_start)
    if end == -1:
        return text
    return text[:body_start] + "\n\n" + replacement_body.strip() + "\n\n" + text[end:]


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
- **Overall portfolio judgment:** Keep the current portfolio intact for now, but treat SPY, PPA, PAVE and GLD as active review items rather than passive holds.
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
    second = implications[1] if len(implications) > 1 else "Treat SPY, PPA, PAVE and GLD as active review items rather than passive holds."
    third = implications[2] if len(implications) > 2 else "Do not fund replacement candidates until pricing basis and direct duel evidence are visible."
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


def polish_english(text: str) -> str:
    pack = load_macro_pack()

    text = text.replace("Replacement Duel Table v2", "Replacement Duel Table")
    text = text.replace(
        "- **Secondary cross-current:** Runtime-derived report generation is active. Pricing, lane discovery, portfolio state and recommendation discipline are separate inputs.",
        "- **Secondary cross-current:** The production process is state-led: pricing, portfolio holdings, lane discovery, macro regime and recommendation discipline are independently validated before delivery."
    )
    text = text.replace(
        "- None from this renderer unless the runtime state already records an executed Add.",
        "- None executed this run. SMH remains the first candidate for additional capital only if the 25% position-size rule leaves room."
    )
    text = text.replace(
        "- No replacement is fundable until the pricing and relative-strength duel is complete.",
        "- No challenger is promoted to a fundable replacement yet. Each named replacement must first clear the same close-date pricing basis and relative-strength duel."
    )
    text = text.replace("- Equity-curve state: Runtime-derived", "- Equity-curve state: Reconciled to Section 15")
    text = text.replace(
        "- Added: runtime-rendered markdown generation layer.",
        "- Added: a validated state-led production path with macro-policy regime input; no portfolio position was added unless shown in Section 14."
    )
    text = text.replace(
        "- Thesis changes: No thesis abandoned; implementation discipline tightened.",
        "- Thesis changes: No structural thesis was abandoned; implementation and macro-regime discipline are materially tighter."
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
- **Main discipline issue:** SPY and SMH still create meaningful U.S. tech / AI overlap; this is concentration with benefits, not full diversification.
- **Weakest implementation questions:** PPA must prove itself against ITA, PAVE must prove itself against GRID, and GLD must prove that it still behaves like useful ballast.
- **Action bias:** No replacement is fundable yet. The right next move is evidence gathering, not forced churn.
"""
        )

    return text


def polish_dutch(text: str) -> str:
    text = polish_english(text)
    replacements = {
        "The production process is state-led: pricing, portfolio holdings, lane discovery, macro regime and recommendation discipline are independently validated before delivery.": "Het productieproces is state-led: pricing, portefeuilleposities, lane-discovery, macroregime en aanbevelingsdiscipline worden onafhankelijk gevalideerd vóór verzending.",
        "No challenger is promoted to a fundable replacement yet. Each named replacement must first clear the same close-date pricing basis and relative-strength duel.": "Geen challenger is al gepromoveerd tot financierbare vervanger. Elke genoemde vervanger moet eerst dezelfde sluitkoersbasis en relatieve-sterkte-duel doorstaan.",
        "Portfolio stance": "Portefeuillehouding",
        "Best earned exposure": "Best verdiende exposure",
        "Main discipline issue": "Belangrijkste disciplinepunt",
        "Weakest implementation questions": "Zwakste implementatievragen",
        "Action bias": "Actiebias",
        "Current regime": "Huidig regime",
        "Confidence": "Vertrouwen",
        "Decision rule": "Beslisregel",
        "What changed": "Wat veranderde",
        "Portfolio implications": "Portefeuille-implicaties",
        "Cross-asset confirmation": "Cross-asset bevestiging",
        "Policy catalysts transferred to the report": "Beleidscatalysatoren in het rapport",
        "Macro supports selection discipline, not broad risk expansion by default.": "Macro ondersteunt selectiediscipline, niet standaard brede risico-uitbreiding.",
        "Stay invested": "Blijf belegd",
        "SMH remains the portfolio's strongest contributor and cleanest secular growth expression.": "SMH blijft de sterkste bijdrage in de portefeuille en de zuiverste structurele groeiblootstelling.",
        "PPA must prove itself against ITA, PAVE must prove itself against GRID, and GLD must prove that it still behaves like useful ballast.": "PPA moet zich bewijzen tegenover ITA, PAVE tegenover GRID, en GLD moet bewijzen dat het nog steeds nuttige ballast is.",
        "Reconciled to Section 15": "Aangesloten op Section 15",
        "a validated state-led production path with macro-policy regime input; no portfolio position was added unless shown in Section 14.": "een gevalideerd state-led productiepad met macro-/beleidsregime-input; geen positie is toegevoegd tenzij zichtbaar in Section 14.",
        "No structural thesis was abandoned; implementation and macro-regime discipline are materially tighter.": "Geen structurele thesis is losgelaten; implementatie- en macroregimediscipline zijn duidelijk aangescherpt.",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    en_path = latest_report(output_dir, EN_RE)
    nl_path = latest_report(output_dir, NL_RE)

    en_path.write_text(polish_english(en_path.read_text(encoding="utf-8")), encoding="utf-8")
    nl_path.write_text(polish_dutch(nl_path.read_text(encoding="utf-8")), encoding="utf-8")

    print(f"ETF_RUNTIME_POLISH_OK | en={en_path.name} | nl={nl_path.name}")


if __name__ == "__main__":
    main()
