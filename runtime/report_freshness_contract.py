from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

RUNTIME_POINTER = Path("output/runtime/latest_etf_report_state_path.txt")


class ReportFreshnessError(RuntimeError):
    pass


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _date(value: Any) -> date | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None


def load_runtime_state(explicit: str | Path | None = None) -> dict[str, Any]:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    for env_name in ("MRKT_RPRTS_RUNTIME_STATE_PATH", "ETF_RUNTIME_STATE_PATH"):
        raw = os.environ.get(env_name, "").strip()
        if raw:
            candidates.append(Path(raw))
    if RUNTIME_POINTER.exists():
        raw = RUNTIME_POINTER.read_text(encoding="utf-8").strip()
        if raw:
            candidates.append(Path(raw))

    for candidate in candidates:
        if not candidate.is_absolute() and not candidate.exists():
            alternative = RUNTIME_POINTER.parent / candidate.name
            if alternative.exists():
                candidate = alternative
        if not candidate.exists():
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict):
            payload.setdefault("_runtime_state_source", str(candidate))
            return payload
    return {}


def _positions(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in state.get("positions", []) or []:
        if not isinstance(row, dict):
            continue
        ticker = str(row.get("ticker") or "").strip().upper()
        if ticker:
            out[ticker] = row
    return out


def _weight(state: dict[str, Any], ticker: str) -> float:
    row = _positions(state).get(ticker.upper(), {})
    return _float(row.get("current_weight_pct"), _float(row.get("weight_pct"), 0.0))


def _macro_pack(state: dict[str, Any]) -> dict[str, Any]:
    pack = state.get("macro_policy_pack") or {}
    return pack if isinstance(pack, dict) else {}


def _regime_memory(state: dict[str, Any]) -> dict[str, Any]:
    memory = _macro_pack(state).get("regime_memory") or {}
    return memory if isinstance(memory, dict) else {}


def _regime(state: dict[str, Any]) -> dict[str, Any]:
    regime = _macro_pack(state).get("regime") or {}
    return regime if isinstance(regime, dict) else {}


def _current_ai_leadership(state: dict[str, Any]) -> bool:
    signals = _macro_pack(state).get("macro_signals") or {}
    equity = signals.get("equity_leadership") if isinstance(signals, dict) else {}
    signal = str((equity or {}).get("signal") or "").lower()
    evidence = (equity or {}).get("evidence") or {}
    smh = _float(evidence.get("SMH_return_3m_pct"))
    spy = _float(evidence.get("SPY_return_3m_pct"))
    return signal == "narrow_ai_leadership" or smh > spy + 4.0


def delta_summary(state: dict[str, Any], language: str) -> str:
    memory = _regime_memory(state)
    regime = _regime(state)
    current = str(memory.get("current_regime") or regime.get("current") or "Unknown").strip()
    prior = str(memory.get("prior_regime") or regime.get("previous") or "Unknown").strip()
    changed = bool(memory.get("regime_changed_this_run")) and prior not in {"", "Unknown"}
    breadth = str(memory.get("breadth_trend") or "mixed").replace("_", " ")
    cross = str(memory.get("cross_asset_confirmation") or "mixed").replace("_", " ")
    ai = _current_ai_leadership(state)

    if language == "nl":
        if changed:
            return (
                f"Het regime veranderde ten opzichte van de vorige review van {prior} naar {current}. "
                f"De marktbreedte is {breadth} en de cross-assetbevestiging is {cross}."
            )
        if ai:
            return (
                "Er is geen materiële regimeverandering vastgesteld ten opzichte van de vorige review. "
                "AI- en semiconductorleiderschap bleef dominant, terwijl marktbreedte en cross-assetbevestiging gemengd bleven."
            )
        return (
            "Er is geen materiële regimeverandering vastgesteld ten opzichte van de vorige review. "
            f"Het bestaande regime bleef intact; de marktbreedte is {breadth} en de cross-assetbevestiging is {cross}."
        )

    if changed:
        return (
            f"The regime changed versus the prior review from {prior} to {current}. "
            f"Market breadth is {breadth} and cross-asset confirmation is {cross}."
        )
    if ai:
        return (
            "No material regime change was recorded versus the prior review. "
            "AI / semiconductor leadership remained dominant, while market breadth and cross-asset confirmation stayed mixed."
        )
    return (
        "No material regime change was recorded versus the prior review. "
        f"The existing regime remained intact; market breadth is {breadth} and cross-asset confirmation is {cross}."
    )


def _replace_executive_change_line(text: str, summary: str, language: str) -> str:
    if language == "nl":
        pattern = re.compile(r"^- \*\*Wat is er deze week veranderd:\*\*.*$", re.MULTILINE)
        replacement = f"- **Wat veranderde ten opzichte van de vorige review:** {summary}"
    else:
        pattern = re.compile(r"^- \*\*What changed this week:\*\*.*$", re.MULTILINE)
        replacement = f"- **What changed versus the prior review:** {summary}"
    return pattern.sub(replacement, text, count=1)


def _replace_what_changed_block(text: str, summary: str, language: str) -> str:
    heading = "### Wat veranderde" if language == "nl" else "### What changed"
    start = text.find(heading)
    if start == -1:
        return text
    body_start = start + len(heading)
    next_heading = text.find("\n### ", body_start)
    if next_heading == -1:
        next_heading = text.find("\n## ", body_start)
    if next_heading == -1:
        next_heading = len(text)
    return text[:body_start] + f"\n- {summary}\n" + text[next_heading:]


def _event_is_current(report_date: date | None, event_date: date | None, lookback_days: int = 6) -> bool:
    if report_date is None or event_date is None:
        return False
    return report_date - timedelta(days=lookback_days) <= event_date <= report_date


def _stale_policy_areas(state: dict[str, Any]) -> set[str]:
    pack = _macro_pack(state)
    report_date = _date(pack.get("report_date") or state.get("report_date"))
    stale: set[str] = set()
    for item in pack.get("policy_catalysts", []) or []:
        if not isinstance(item, dict) or item.get("transfer_to_report") is not True:
            continue
        event_date = _date(item.get("event_date"))
        if event_date and not _event_is_current(report_date, event_date):
            stale.add(str(item.get("policy_area") or "").strip())
    return stale


def _filter_stale_policy_catalysts(text: str, state: dict[str, Any], language: str) -> str:
    stale = _stale_policy_areas(state)
    lines = text.splitlines()
    out: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped in {"### Policy catalysts included in this report", "### Beleidscatalysatoren in dit rapport"}:
            in_section = True
            out.append(line)
            continue
        if in_section and (stripped.startswith("### ") or stripped.startswith("## ")):
            in_section = False
        if in_section and stripped.startswith("- "):
            lowered = stripped.lower()
            if any(area and area.lower() in lowered for area in stale):
                continue
            if "raised rates this week" in lowered or "verhoogde deze week de rente" in lowered:
                continue
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def _replace_many(text: str, replacements: dict[str, str]) -> str:
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _replace_in_section(text: str, section_number: int, replacements: dict[str, str]) -> str:
    marker = f"## {section_number}."
    start = text.find(marker)
    if start == -1:
        return text
    next_section = text.find(f"\n## {section_number + 1}.", start + len(marker))
    if next_section == -1:
        next_section = len(text)
    section = _replace_many(text[start:next_section], replacements)
    return text[:start] + section + text[next_section:]


def _apply_state_consistency(text: str, state: dict[str, Any], language: str) -> str:
    positions = _positions(state)
    iefa_weight = _weight(state, "IEFA")
    has_iefa = iefa_weight >= 1.0
    has_dfen = "DFEN" in positions
    has_ppa = "PPA" in positions

    if language == "nl":
        replacements: dict[str, str] = {
            "Financial infrastructure and market plumbing": "Financiële infrastructuur en marktinfrastructuur",
            "Power infrastructure and utilities capex": "Energie-infrastructuur en investeringen in nutsbedrijven",
            "Diagnostisch-only": "Alleen diagnostisch",
            "fundability-bevoegdheid": "financieringsbevoegdheid",
        }
        if has_iefa:
            replacements.update(
                {
                    "Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof.": f"IEFA levert inmiddels een materiële allocatie naar ontwikkelde markten buiten de VS ({iefa_weight:.2f}%); verdere uitbreiding vraagt nog relatieve-sterkte- en concentratiebevestiging.",
                    "Alleen volglijst; blootstelling buiten de VS blijft een diversificatiekloof.": f"IEFA vertegenwoordigt al {iefa_weight:.2f}% van de portefeuille; verdere uitbreiding is niet automatisch en blijft afhankelijk van relatieve sterkte en concentratie.",
                    "Nulallocatie is een expliciete inzet op Amerikaanse uitzonderingskracht.": f"De portefeuille heeft via IEFA al {iefa_weight:.2f}% niet-Amerikaanse ontwikkelde-marktenblootstelling; valuta- en regioconcentratie moeten daarom actief worden bewaakt.",
                    "De portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de VS.": f"IEFA biedt al een materiële allocatie naar ontwikkelde markten buiten de VS ({iefa_weight:.2f}%); verdere wijzigingen vereisen relatieve-sterkte- en concentratiebewijs.",
                    "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL), [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) op de volglijst": "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL) als kwaliteitsalternatief en [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) als reeds gefinancierde diversificatie",
                    "QUAL, IEFA op de volglijst": "QUAL als kwaliteitsalternatief en IEFA als reeds gefinancierde diversificatie",
                    "| Ontwikkelde markten buiten de VS | [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) | Relatieve sterkte tegenover de relevante huidige positie is nog onvoldoende overtuigend. | Sterkere relatieve sterkte en duidelijke aansluiting op de beleggingscase. |": "| Ontwikkelde markten buiten de VS | [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) | Bestaande gefinancierde positie; deze run is geen aanvullende lane-promotie toegekend. | Heroverweeg alleen bij een duidelijke wijziging in relatieve sterkte, factorconcentratie of financieringsbron. |",
                    "| Ontwikkelde markten buiten de VS | IEFA | Relatieve sterkte tegenover de relevante huidige positie is nog onvoldoende overtuigend. | Sterkere relatieve sterkte en duidelijke aansluiting op de beleggingscase. |": "| Ontwikkelde markten buiten de VS | IEFA | Bestaande gefinancierde positie; deze run is geen aanvullende lane-promotie toegekend. | Heroverweeg alleen bij een duidelijke wijziging in relatieve sterkte, factorconcentratie of financieringsbron. |",
                }
            )
        text = _replace_many(text, replacements)
        if has_iefa:
            text = _replace_in_section(
                text,
                9,
                {
                    "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL), [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) op de volglijst": "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL) als kwaliteitsalternatief en [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) als reeds gefinancierde diversificatie",
                },
            )
        if has_dfen and not has_ppa:
            text = _replace_in_section(
                text,
                5,
                {
                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) blijven vervangbaar totdat de kwaliteit van de ETF-implementatie is bewezen.": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) blijven onder implementatie- en vervangingsreview; bij DFEN moet ook het hefboomprofiel expliciet worden meegewogen.",
                    "PPA en PAVE blijven vervangbaar totdat de kwaliteit van de ETF-implementatie is bewezen.": "DFEN en PAVE blijven onder implementatie- en vervangingsreview; bij DFEN moet ook het hefboomprofiel expliciet worden meegewogen.",
                },
            )
            text = _replace_in_section(
                text,
                6,
                {
                    "Voordat nieuw kapitaal naar alternatieven gaat, moeten [SPY](https://www.tradingview.com/chart/?symbol=SPY), [PPA](https://www.tradingview.com/chart/?symbol=PPA) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) expliciet worden getoetst": "Voordat nieuw kapitaal naar alternatieven gaat, moeten [SPY](https://www.tradingview.com/chart/?symbol=SPY), [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) expliciet worden getoetst",
                    "Voordat nieuw kapitaal naar alternatieven gaat, moeten SPY, PPA en PAVE expliciet worden getoetst": "Voordat nieuw kapitaal naar alternatieven gaat, moeten SPY, DFEN en PAVE expliciet worden getoetst",
                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) moet zich bewijzen tegenover [ITA](https://www.tradingview.com/chart/?symbol=ITA), [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) tegenover [GRID](https://www.tradingview.com/chart/?symbol=GRID)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) moet worden getoetst aan niet-gehevelde defensiealternatieven, en [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) aan [GRID](https://www.tradingview.com/chart/?symbol=GRID)",
                    "PPA moet zich bewijzen tegenover ITA, PAVE tegenover GRID": "DFEN moet worden getoetst aan niet-gehevelde defensiealternatieven, en PAVE aan GRID",
                },
            )
            text = _replace_in_section(
                text,
                9,
                {
                    "[PPA](https://www.tradingview.com/chart/?symbol=PPA) moet zich bewijzen tegenover [ITA](https://www.tradingview.com/chart/?symbol=ITA)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) moet worden vergeleken met niet-gehevelde defensiealternatieven zoals [ITA](https://www.tradingview.com/chart/?symbol=ITA) en [PPA](https://www.tradingview.com/chart/?symbol=PPA)",
                    "PPA moet zich bewijzen tegenover ITA": "DFEN moet worden vergeleken met niet-gehevelde defensiealternatieven zoals ITA en PPA",
                    "Houd [PPA](https://www.tradingview.com/chart/?symbol=PPA) onder herbeoordeling": "Houd de implementatiekwaliteit en het hefboomprofiel van [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) onder herbeoordeling",
                    "Houd PPA onder herbeoordeling": "Houd de implementatiekwaliteit en het hefboomprofiel van DFEN onder herbeoordeling",
                },
            )
        return text

    replacements = {}
    if has_iefa:
        replacements.update(
            {
                "Non-U.S. equity exposure remains a diversification gap.": f"IEFA now provides a material non-U.S. developed-market allocation ({iefa_weight:.2f}%); further expansion still requires relative-strength and concentration confirmation.",
                "Watchlist only; non-U.S. exposure remains a diversification gap.": f"IEFA already represents {iefa_weight:.2f}% of the portfolio; further expansion is not automatic and remains relative-strength and concentration gated.",
                "Zero allocation is an explicit bet on U.S. exceptionalism.": f"The portfolio already carries {iefa_weight:.2f}% non-U.S. developed-market exposure through IEFA; currency and regional concentration therefore require active monitoring.",
                "Zero allocation is an explicit U.S. exceptionalism bet.": f"The portfolio already carries {iefa_weight:.2f}% non-U.S. developed-market exposure through IEFA; currency and regional concentration therefore require active monitoring.",
                "Portfolio has limited non-U.S. exposure.": f"IEFA already provides a material non-U.S. developed-market allocation ({iefa_weight:.2f}%); further changes require relative-strength and concentration evidence.",
                "QUAL, IEFA on the watchlist": "QUAL as a quality alternative and IEFA as an already funded diversifier",
                "| Non-U.S. developed market diversification | [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) | Scored below the live radar cutoff versus stronger funded and challenger lanes. | Becomes fundable if U.S. factor concentration rises or non-U.S. breadth improves. |": "| Non-U.S. developed market diversification | [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) | Existing funded position; no additional lane promotion was granted this run. | Reassess only if relative strength, factor concentration or the funding case changes materially. |",
                "| Non-U.S. developed market diversification | IEFA | Scored below the live radar cutoff versus stronger funded and challenger lanes. | Becomes fundable if U.S. factor concentration rises or non-U.S. breadth improves. |": "| Non-U.S. developed market diversification | IEFA | Existing funded position; no additional lane promotion was granted this run. | Reassess only if relative strength, factor concentration or the funding case changes materially. |",
            }
        )
    text = _replace_many(text, replacements)
    if has_iefa:
        text = _replace_in_section(
            text,
            9,
            {
                "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL), [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) watchlist": "[QUAL](https://www.tradingview.com/chart/?symbol=QUAL) as a quality alternative and [IEFA](https://www.tradingview.com/chart/?symbol=IEFA) as an already funded diversifier",
                "QUAL, IEFA watchlist": "QUAL as a quality alternative and IEFA as an already funded diversifier",
            },
        )
    if has_dfen and not has_ppa:
        text = _replace_in_section(
            text,
            5,
            {
                "[PPA](https://www.tradingview.com/chart/?symbol=PPA) and [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) remain replaceable until their ETF implementation quality is proven.": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) and [PAVE](https://www.tradingview.com/chart/?symbol=PAVE) remain under implementation and replacement review; DFEN's leverage profile must also be assessed explicitly.",
                "PPA and PAVE remain replaceable until their ETF implementation quality is proven.": "DFEN and PAVE remain under implementation and replacement review; DFEN's leverage profile must also be assessed explicitly.",
            },
        )
        text = _replace_in_section(
            text,
            9,
            {
                "[PPA](https://www.tradingview.com/chart/?symbol=PPA) must justify itself versus [ITA](https://www.tradingview.com/chart/?symbol=ITA)": "[DFEN](https://www.tradingview.com/chart/?symbol=DFEN) must be compared with unlevered defense alternatives such as [ITA](https://www.tradingview.com/chart/?symbol=ITA) and [PPA](https://www.tradingview.com/chart/?symbol=PPA)",
                "PPA must justify itself versus ITA": "DFEN must be compared with unlevered defense alternatives such as ITA and PPA",
                "Hold [PPA](https://www.tradingview.com/chart/?symbol=PPA) under review": "Keep [DFEN](https://www.tradingview.com/chart/?symbol=DFEN) implementation quality and leverage under review",
                "Hold PPA under review": "Keep DFEN implementation quality and leverage under review",
            },
        )
    return text


def apply_report_freshness_contract(text: str, state: dict[str, Any], language: str) -> str:
    language = language.lower().strip()
    if language not in {"en", "nl"}:
        raise ValueError(f"Unsupported report language: {language}")
    summary = delta_summary(state, language)
    text = _replace_executive_change_line(text, summary, language)
    text = _replace_what_changed_block(text, summary, language)
    text = _filter_stale_policy_catalysts(text, state, language)
    text = _apply_state_consistency(text, state, language)
    validate_report_freshness(text, state, language)
    return text


def _what_changed_lines(text: str, language: str) -> list[str]:
    heading = "### Wat veranderde" if language == "nl" else "### What changed"
    start = text.find(heading)
    if start == -1:
        return []
    body_start = start + len(heading)
    end = text.find("\n### ", body_start)
    if end == -1:
        end = text.find("\n## ", body_start)
    if end == -1:
        end = len(text)
    return [line.strip()[2:].strip() for line in text[body_start:end].splitlines() if line.strip().startswith("- ")]


def validate_report_freshness(text: str, state: dict[str, Any], language: str) -> None:
    errors: list[str] = []
    positions = _positions(state)
    iefa_weight = _weight(state, "IEFA")
    lowered = text.lower()

    if "raised rates this week" in lowered or "verhoogde deze week de rente" in lowered:
        errors.append("stale_policy_event_relative_date")

    if iefa_weight >= 1.0:
        for phrase in (
            "non-u.s. equity exposure remains a diversification gap",
            "only watchlist; non-u.s. exposure remains a diversification gap",
            "watchlist only; non-u.s. exposure remains a diversification gap",
            "zero allocation is an explicit bet",
            "zero allocation is an explicit u.s. exceptionalism bet",
            "portfolio has limited non-u.s. exposure",
            "de portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de vs",
            "niet-amerikaanse aandelenblootstelling blijft een diversificatiekloof",
            "alleen volglijst; blootstelling buiten de vs blijft een diversificatiekloof",
            "nulallocatie is een expliciete inzet",
        ):
            if phrase in lowered:
                errors.append("iefa_position_contradicted_by_stale_zero_or_gap_wording")
                break

    if "DFEN" in positions and "PPA" not in positions:
        for phrase in (
            "ppa and pave remain replaceable",
            "keep ppa under review",
            "ppa en pave blijven vervangbaar",
            "houd [ppa]",
        ):
            if phrase in lowered:
                errors.append("non_held_ppa_described_as_current_position")
                break

    continuity_tokens = (" remains ", " still ", " continues ") if language == "en" else (" blijft ", " nog steeds ")
    exception_tokens = ("no material regime change",) if language == "en" else ("geen materiële regimeverandering",)
    for line in _what_changed_lines(text, language):
        padded = f" {line.lower()} "
        if any(token in padded for token in continuity_tokens) and not any(token in padded for token in exception_tokens):
            errors.append("what_changed_contains_continuity_without_explicit_no_change")

    if language == "nl":
        for phrase in ("financial infrastructure and market plumbing", "power infrastructure and utilities capex", "diagnostisch-only", "fundability-bevoegdheid"):
            if phrase in lowered:
                errors.append(f"unlocalized_dutch_surface:{phrase}")

    if errors:
        raise ReportFreshnessError("ETF report freshness validation failed: " + "; ".join(sorted(set(errors))))
