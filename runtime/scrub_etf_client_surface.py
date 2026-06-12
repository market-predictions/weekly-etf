from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_report_state import build_runtime_state
from runtime.max_position_action_contract import over_cap_tickers

SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b")
EN_NEGATIVE_RE = re.compile(r"(\breduce\s+(?:\[[^\]]+\]\([^\)]+\)|[A-Z][A-Z0-9.-]*)\s+(?:by)\s+)-(\d+(?:\.\d+)?%)", re.IGNORECASE)
NL_NEGATIVE_RE = re.compile(r"(\bverlaag\s+(?:\[[^\]]+\]\([^\)]+\)|[A-Z][A-Z0-9.-]*)\s+met\s+)-(\d+(?:\.\d+)?%)", re.IGNORECASE)
EMPTY_COMMENT_ARTIFACT_RE = re.compile(r"(?im)^\s*(?:&lt;!|<!)\s*--\s*--\s*(?:&gt;|>)\s*\n?")
PORTFOLIO_STATE_PATH = Path("output/etf_portfolio_state.json")

EXACT_REPLACEMENTS = {
    "rotation_decisions, target_weights and trade_intents": "the portfolio rotation plan, target allocations and proposed trade intents",
    "trade_intents": "proposed trade intents",
    "target_weights": "target allocations",
    "rotation_decisions": "rotation decisions",
    "churn_budget_used": "rotation budget already used",
    "etf_valuation_history": "ETF valuation history",
    "Reason codes": "Decision rationale",
    "Redencodes": "Toelichting",
    "fresh_cash_smaller_or_review": "fresh capital only after review or at smaller size",
    "failed_fresh_cash_test": "position does not pass the fresh-capital test",
    "replaceable_status": "position is under replacement review",
    "review_age_ge_2": "review has persisted for multiple report cycles",
    "review_age_ge_3": "review has persisted for several report cycles",
}

PHRASE_REPLACEMENTS = {
    "Notes: Section 7 uses `output/ETF valuation history.csv` plus the current runtime NAV; Section 15 is rendered from the same normalized runtime state.":
        "Notes: Section 7 uses the validated valuation history plus the current portfolio NAV; Section 15 is rendered from the same reconciled portfolio state.",
    "Notes: Section 7 uses `output/etf valuation history.csv` plus the current runtime NAV; Section 15 is rendered from the same normalized runtime state.":
        "Notes: Section 7 uses the validated valuation history plus the current portfolio NAV; Section 15 is rendered from the same reconciled portfolio state.",
    "Notes: Section 7 uses `output/etf_valuation_history.csv` plus the current runtime NAV; Section 15 is rendered from the same normalized runtime state.":
        "Notes: Section 7 uses the validated valuation history plus the current portfolio NAV; Section 15 is rendered from the same reconciled portfolio state.",
    "Rotation plan artifact is active; Sections 12-14 are rendered from the portfolio rotation plan, target allocations and proposed trade intents.":
        "Rotation plan artifact is active; Sections 12-14 are rendered from the portfolio rotation plan, target allocations and proposed trade intents.",
    "override rotation budget already used": "override: rotation budget already used",
}

EXITED_GLD_REPLACEMENTS = {
    "GLD → GSG": "prior commodity-breadth rotation into GSG",
    "GLD -> GSG": "prior commodity-breadth rotation into GSG",
    "Added as commodity-breadth replacement for part of GLD.": "Added as current commodity-breadth hedge exposure after the prior gold-sleeve exit.",
    "Added as commodity-breadth replacement for part of GLD": "Added as current commodity-breadth hedge exposure after the prior gold-sleeve exit",
    "Gold hedge review": "Commodity-breadth hedge review",
    "gold hedge review": "commodity-breadth hedge review",
    "Gold hedge behavior remains under review rather than automatic ballast.": "Commodity-breadth hedge behavior remains under review rather than automatic ballast.",
    "Het gedrag van goud als hedge blijft onder herbeoordeling en is geen automatische stabilisator.": "De grondstoffenbrede hedgefunctie blijft onder herbeoordeling en is geen automatische stabilisator.",
    "Laat de huidige portefeuille voorlopig intact, maar behandel SPY, PPA, PAVE en GLD als posities onder actieve herbeoordeling.": "Laat de huidige portefeuille voorlopig intact, maar behandel SPY, PPA, PAVE en de hedgefunctie als posities onder actieve herbeoordeling.",
    "GLD blijft een hedgepositie onder herbeoordeling en is geen vanzelfsprekende stabilisator.": "De hedgefunctie blijft onder herbeoordeling en is geen vanzelfsprekende stabilisator.",
    "PPA moet zich bewijzen tegenover ITA, PAVE tegenover GRID, en GLD moet bewijzen dat het nog steeds een stabiliserende hedgefunctie heeft.": "PPA moet zich bewijzen tegenover ITA, PAVE tegenover GRID, en de hedgefunctie moet bewijzen dat zij nog steeds stabiliseert.",
    "| Herbeoordeling goudhedge | GLD | GSG / BIL | Hedgefunctie moet worden bewezen. | Onder herbeoordeling |": "| Herbeoordeling grondstoffenhedge | GSG | DBC / BIL | De huidige grondstoffenbrede hedgefunctie moet worden bewezen tegenover cash en alternatieven. | Onder herbeoordeling |",
    "| Goud | Neutraal | Hedgerol onder herbeoordeling. |": "| Defensieve ballast | Neutraal | Hedge- en cashachtige rollen blijven onder opportunity-cost-review. |",
    "| Hedgedrawdown | GLD moet zijn hedgefunctie bewijzen | GSG en BIL blijven alternatieven | GSG, BIL, cash | Onproductieve hedgepositie | Houd GLD onder herbeoordeling | Direct | Gemiddeld |": "| Hedgedrawdown | De hedgefunctie moet zichzelf bewijzen | GSG, BIL en cash blijven alternatieven | GSG, BIL, cash | Onproductieve hedgepositie | Houd de huidige hedgefunctie onder herbeoordeling | Direct | Gemiddeld |",
    "- GLD: hedge-validiteitstest vereist.\n": "",
}

CANONICAL_CONSTRAINT_LINES = {
    "en_position_size": "Max position size: 25% soft cap; current inherited overweights require no-fresh-cash and review/trim discipline",
    "en_position_count": "Max number of positions: 8 soft target; current inherited count may exceed this until guarded rotation reduces it",
    "nl_position_size": "Maximale positiegrootte: 25% zachte bovengrens; bestaande overwegingen krijgen geen nieuw kapitaal en blijven onder verklein-/reviewdiscipline",
    "nl_position_count": "Maximaal aantal posities: 8 zachte doelstelling; het huidige geërfde aantal kan tijdelijk hoger zijn totdat bewaakte rotatie dit verlaagt",
}


def _clean_snake_token(match: re.Match[str]) -> str:
    token = match.group(0)
    replacement = EXACT_REPLACEMENTS.get(token)
    if replacement:
        return replacement
    return token.replace("_", " ")


def _portfolio_positions() -> list[dict[str, Any]]:
    try:
        payload = json.loads(PORTFOLIO_STATE_PATH.read_text(encoding="utf-8"))
        rows = payload.get("positions", [])
        return list(rows) if isinstance(rows, list) else []
    except Exception:
        return []


def _active_tickers_from_portfolio_state() -> set[str]:
    return {str(position.get("ticker") or "").upper() for position in _portfolio_positions() if str(position.get("ticker") or "").strip()}


def _has_material_non_us_developed_exposure(threshold_pct: float = 2.0) -> bool:
    for position in _portfolio_positions():
        ticker = str(position.get("ticker") or "").upper()
        if ticker not in {"IEFA", "EFA", "VEA"}:
            continue
        for key in ("current_weight_pct", "weight_pct", "previous_weight_pct"):
            try:
                if float(position.get(key) or 0.0) >= threshold_pct:
                    return True
            except (TypeError, ValueError):
                continue
    return "IEFA" in _active_tickers_from_portfolio_state()


def _over_cap_from_state() -> list[str]:
    try:
        return over_cap_tickers(build_runtime_state())
    except Exception:
        return []


def _ticker_md_pattern(ticker: str) -> str:
    escaped = re.escape(ticker)
    return rf"(?:\[{escaped}\]\([^\)]+\)|{escaped})"


def _strip_ticker_from_list(value: str, ticker: str, none_label: str = "None") -> str:
    ticker_pat = _ticker_md_pattern(ticker)
    value = re.sub(rf"\s*,?\s*{ticker_pat}\s*,?\s*", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\s*,\s*,\s*", ", ", value)
    value = re.sub(r"^\s*,\s*|\s*,\s*$", "", value.strip())
    return value if value else none_label


def _scrub_empty_html_comments(text: str) -> str:
    text = EMPTY_COMMENT_ARTIFACT_RE.sub("", text)
    text = text.replace("<!-- -->", "")
    text = text.replace("&lt;!-- --&gt;", "")
    return text


def _scrub_non_us_exposure_references(text: str) -> str:
    if not _has_material_non_us_developed_exposure():
        return text
    replacements = {
        "Zero non-U.S. equity exposure is an implicit U.S.-exceptionalism bet.": "Non-U.S. developed exposure has been increased through IEFA, but still requires relative-strength confirmation before becoming a broader allocation theme.",
        "Zero allocation is an explicit U.S. exceptionalism bet.": "IEFA now provides non-U.S. developed-market exposure, but broader allocation still requires relative-strength confirmation.",
        "Non-U.S. equity exposure remains a diversification gap.": "Non-U.S. developed exposure has been increased through IEFA, but breadth and relative-strength confirmation remain required.",
        "Portfolio has limited non-U.S. exposure.": "IEFA now provides non-U.S. developed-market exposure, with broader allocation still under confirmation.",
        "De portefeuille heeft geen blootstelling aan ontwikkelde markten buiten de VS.": "De portefeuille heeft via IEFA blootstelling aan ontwikkelde markten buiten de VS, maar verdere allocatie vraagt bevestiging in relatieve sterkte.",
        "Nulallocatie is een expliciete inzet op Amerikaanse uitzonderingskracht.": "IEFA biedt nu blootstelling aan ontwikkelde markten buiten de VS; verdere allocatie vraagt nog bevestiging.",
        "Niet-Amerikaanse aandelenblootstelling blijft een diversificatiekloof.": "Blootstelling aan ontwikkelde markten buiten de VS is via IEFA verhoogd, maar blijft onder bevestiging in relatieve sterkte.",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _replace_constraint_line(pattern: str, replacement: str, text: str) -> str:
    return re.sub(pattern, lambda m: f"{m.group('prefix')}{replacement}", text, flags=re.IGNORECASE | re.MULTILINE)


def _scrub_constraint_copy(text: str) -> str:
    text = _replace_constraint_line(
        r"^(?P<prefix>\s*(?:[-*]\s*)?)Max position size:\s*25%.*$",
        CANONICAL_CONSTRAINT_LINES["en_position_size"],
        text,
    )
    text = _replace_constraint_line(
        r"^(?P<prefix>\s*(?:[-*]\s*)?)Max number of positions:\s*8.*$",
        CANONICAL_CONSTRAINT_LINES["en_position_count"],
        text,
    )
    text = _replace_constraint_line(
        r"^(?P<prefix>\s*(?:[-*]\s*)?)Maximale positiegrootte:\s*25%.*$",
        CANONICAL_CONSTRAINT_LINES["nl_position_size"],
        text,
    )
    text = _replace_constraint_line(
        r"^(?P<prefix>\s*(?:[-*]\s*)?)Maximaal aantal posities:\s*8.*$",
        CANONICAL_CONSTRAINT_LINES["nl_position_count"],
        text,
    )
    return text


def _scrub_exited_holding_references(text: str) -> str:
    active = _active_tickers_from_portfolio_state()
    if "GLD" in active:
        return text
    gld = _ticker_md_pattern("GLD")
    gsg = _ticker_md_pattern("GSG")
    bil = _ticker_md_pattern("BIL")
    for source, target in EXITED_GLD_REPLACEMENTS.items():
        text = text.replace(source, target)
    text = re.sub(rf"{gld}\s*[→-]>?\s*{gsg}", "prior commodity-breadth rotation into GSG", text, flags=re.IGNORECASE)
    text = re.sub(rf"Added as commodity-breadth replacement for part of {gld}\.?", "Added as current commodity-breadth hedge exposure after the prior gold-sleeve exit.", text, flags=re.IGNORECASE)
    text = re.sub(rf"Laat de huidige portefeuille voorlopig intact, maar behandel SPY, PPA, PAVE en {gld} als posities onder actieve herbeoordeling\.", "Laat de huidige portefeuille voorlopig intact, maar behandel SPY, PPA, PAVE en de hedgefunctie als posities onder actieve herbeoordeling.", text, flags=re.IGNORECASE)
    text = re.sub(rf"{gld} blijft een hedgepositie onder herbeoordeling en is geen vanzelfsprekende stabilisator\.", "De hedgefunctie blijft onder herbeoordeling en is geen vanzelfsprekende stabilisator.", text, flags=re.IGNORECASE)
    text = re.sub(rf"PPA moet zich bewijzen tegenover ITA, PAVE tegenover GRID, en {gld} moet bewijzen dat het nog steeds een stabiliserende hedgefunctie heeft\.", "PPA moet zich bewijzen tegenover ITA, PAVE tegenover GRID, en de hedgefunctie moet bewijzen dat zij nog steeds stabiliseert.", text, flags=re.IGNORECASE)
    text = re.sub(rf"\|\s*Herbeoordeling goudhedge\s*\|\s*{gld}\s*\|\s*{gsg}\s*/\s*{bil}\s*\|\s*Hedgefunctie moet worden bewezen\.\s*\|\s*Onder herbeoordeling\s*\|", "| Herbeoordeling grondstoffenhedge | GSG | DBC / BIL | De huidige grondstoffenbrede hedgefunctie moet worden bewezen tegenover cash en alternatieven. | Onder herbeoordeling |", text, flags=re.IGNORECASE)
    text = re.sub(rf"\|\s*Hedgedrawdown\s*\|\s*{gld} moet zijn hedgefunctie bewijzen\s*\|\s*{gsg} en {bil} blijven alternatieven\s*\|\s*{gsg}, {bil}, cash\s*\|\s*Onproductieve hedgepositie\s*\|\s*Houd {gld} onder herbeoordeling\s*\|\s*Direct\s*\|\s*Gemiddeld\s*\|", "| Hedgedrawdown | De hedgefunctie moet zichzelf bewijzen | GSG, BIL en cash blijven alternatieven | GSG, BIL, cash | Onproductieve hedgepositie | Houd de huidige hedgefunctie onder herbeoordeling | Direct | Gemiddeld |", text, flags=re.IGNORECASE)
    text = re.sub(rf"-\s*{gld}: hedge-validiteitstest vereist\.\n", "", text, flags=re.IGNORECASE)
    return text


def _scrub_over_cap_adds(text: str, tickers: list[str]) -> str:
    for ticker in tickers:
        ticker_pat = _ticker_md_pattern(ticker)
        hold_msg_plain = f"{ticker} remains the best earned exposure, but no fresh capital is added while it is above the 25% max-position cap."
        hold_msg_linked = rf"\1 remains the best earned exposure, but no fresh capital is added while it is above the 25% max-position cap."
        short_reason = "Best earned exposure, but no fresh cash while above the 25% cap"
        capped_status = "Structurally actionable, but no fresh capital while above cap"
        text = text.replace(f"- {ticker} remains the leading funded growth exposure, subject to the max-position rule.", f"- {hold_msg_plain}")
        text = text.replace(f"- {ticker} remains the first candidate for additional capital only if the 25% position-size rule leaves room.", f"- {hold_msg_plain}")
        text = text.replace("Best earned use of cash, capped below max position size", short_reason)
        text = text.replace("Best earned use of cash", short_reason)
        text = text.replace("capped below max position size", "above the 25% max-position cap")
        text = re.sub(rf"-\s*({ticker_pat})\s+remains the leading funded growth exposure, subject to the max-position rule\.", "- " + hold_msg_linked, text, flags=re.IGNORECASE)
        text = re.sub(rf"-\s*({ticker_pat})\s+remains the first candidate for additional capital[^\.]*\.", "- " + hold_msg_linked, text, flags=re.IGNORECASE)
        text = re.sub(rf"\|\s*{ticker_pat}\s*\|\s*Add\s*\|", f"| {ticker} | Hold / no fresh cash while above 25% cap |", text, flags=re.IGNORECASE)
        text = re.sub(rf"\|\s*{ticker_pat}\s*\|\s*([^\|\n]*)\|\s*([^\|\n]*)\|\s*Add\s*\|", rf"| {ticker} | \1| \2| Hold / no fresh cash while above 25% cap |", text, flags=re.IGNORECASE)
        text = re.sub(rf"(### Add\s*\n-\s*)([^\n]*)", lambda m: m.group(1) + _strip_ticker_from_list(m.group(2), ticker), text, flags=re.IGNORECASE)
        text = re.sub(rf"(\|\s*Close\s*\|\s*Reduce\s*\|\s*Hold\s*\|\s*Add(?: / destination)?\s*\|[^\n]*\n\|[^\n]*\n\|\s*[^\|]*\|\s*[^\|]*\|\s*[^\|]*\|\s*)([^\|\n]*(?:{ticker_pat})[^\|\n]*)(\s*\|)", lambda m: m.group(1) + _strip_ticker_from_list(m.group(2), ticker) + m.group(3), text, flags=re.IGNORECASE)
        text = re.sub(rf"(\|[^\n]*\|\s*{ticker_pat}\s*\|[^\n]*\|[^\n]*\|[^\n]*\|[^\n]*\|\s*)Actionable now(\s*\|)", rf"\1{capped_status}\2", text, flags=re.IGNORECASE)
        text = re.sub(rf"(\|[^\n]*\|\s*{ticker_pat}\s*\|[^\n]*\|[^\n]*\|[^\n]*\|[^\n]*\|\s*)Actionable now(\s*\|\s*[^\|\n]*(?:position-size discipline matters|position size discipline matters)[^\|\n]*\|)", rf"\1{capped_status}\2", text, flags=re.IGNORECASE)
        text = re.sub(rf"(\|\s*AI compute infrastructure\s*\|\s*{ticker_pat}\s*\|\s*(?:\[SOXX\]\([^\)]*\)|SOXX)\s*\|\s*Strongest secular growth exposure\.\s*\|\s*)Active(\s*\|)", rf"\1Active / capped\2", text, flags=re.IGNORECASE)
        text = re.sub(rf"(\|\s*AI-rekenkrachtinfrastructuur\s*\|\s*{ticker_pat}\s*\|\s*(?:\[SOXX\]\([^\)]*\)|SOXX)\s*\|\s*Sterkste structurele groeiblootstelling\.\s*\|\s*)Actief(\s*\|)", rf"\1Actief / begrensd\2", text, flags=re.IGNORECASE)
    return text


def scrub_text(text: str, over_cap: list[str] | None = None) -> str:
    text = _scrub_empty_html_comments(text)
    text = EN_NEGATIVE_RE.sub(r"\1\2", text)
    text = NL_NEGATIVE_RE.sub(r"\1\2", text)
    for source, target in EXACT_REPLACEMENTS.items():
        text = text.replace(source, target)
    for source, target in PHRASE_REPLACEMENTS.items():
        text = text.replace(source, target)
    text = SNAKE_CASE_RE.sub(_clean_snake_token, text)
    text = _scrub_exited_holding_references(text)
    text = _scrub_non_us_exposure_references(text)
    text = _scrub_constraint_copy(text)
    text = _scrub_over_cap_adds(text, over_cap or [])
    for source, target in PHRASE_REPLACEMENTS.items():
        text = text.replace(source, target)
    text = _scrub_exited_holding_references(text)
    text = _scrub_empty_html_comments(text)
    return text


def scrub(output_dir: Path) -> None:
    count = 0
    over_cap = _over_cap_from_state()
    for path in sorted(output_dir.glob("weekly_analysis_pro*.md")):
        if path.is_dir():
            continue
        original = path.read_text(encoding="utf-8")
        cleaned = scrub_text(original, over_cap=over_cap)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            count += 1
            print(f"ETF_CLIENT_SURFACE_SCRUBBED | report={path.name}")
    print(f"ETF_CLIENT_SURFACE_SCRUB_OK | changed={count} | over_cap={','.join(over_cap) if over_cap else 'none'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    scrub(Path(args.output_dir))


if __name__ == "__main__":
    main()
