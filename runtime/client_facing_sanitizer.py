from __future__ import annotations

import re
from html import escape

from runtime.nl_dates import localize_english_report_dates

CLIENT_FACING_TOKEN_REPLACEMENTS = {
    "Pending classification": "Mixed / not yet decisive",
    "Placeholder for runtime replacement": "Latest available classified input",
    "runtime rebuild required": "Latest available classified input",
}

DUTCH_HTML_TOKEN_REPLACEMENTS = {
    "WEEKLY ETF PRO REVIEW": "WEKELIJKSE ETF-REVIEW",
    "Weekly ETF Pro Review": "Wekelijkse ETF-review",
    "WEEKLY ETF REVIEW": "WEKELIJKSE ETF-REVIEW",
    "Weekly ETF Review": "Wekelijkse ETF-review",
    "Investor Report": "Beleggersrapport",
    "Investment Report": "Beleggersrapport",
    "Analyst Report": "Analistenrapport",
    "PRIMARY REGIME": "PRIMAIR REGIME",
    "Primary Regime": "Primair regime",
    "GEOPOLITICAL REGIME": "GEOPOLITIEK REGIME",
    "Geopolitical Regime": "Geopolitiek regime",
    "MAIN TAKEAWAY": "KERNCONCLUSIE",
    "Main Takeaway": "Kernconclusie",
    "Risk-on narrow US mega-cap leadership": "Risk-on met smal Amerikaans mega-capleiderschap",
    "Risk-on narrow U.S. mega-cap leadership": "Risk-on met smal Amerikaans mega-capleiderschap",
    "Risk-on narrow leadership": "Risk-on met smal marktleiderschap",
    "Risk-on smal marktleiderschap": "Risk-on met smal marktleiderschap",
    "confidence": "vertrouwen",
    "Mixed / not yet decisive": "Gemengd / nog niet doorslaggevend",
    "Keep the current allocation disciplined.": "Houd de huidige allocatie gedisciplineerd.",
    "Keep the current allocation": "Houd de huidige allocatie",
    "This report is for informational and educational purposes only; please see the disclaimer at the end.": "Dit rapport wordt uitsluitend verstrekt voor informatieve en educatieve doeleinden; zie de disclaimer aan het einde.",
    "Equity Curve (EUR)": "Portefeuillecurve (EUR)",
    "Portfolio value (EUR)": "Portefeuillewaarde (EUR)",
    "Date": "Datum",
}

DUTCH_MD_MARKERS = [
    "kernsamenvatting",
    "portefeuille-acties",
    "huidige posities",
    "beleggersrapport",
    "wekelijks",
    "wekelijkse etf-review",
    "primair regime",
    "geopolitiek regime",
    "kernconclusie",
    "dit rapport wordt uitsluitend verstrekt",
]

ENGLISH_MD_MARKERS = [
    "executive summary",
    "portfolio action snapshot",
    "current portfolio holdings and cash",
    "weekly etf review",
    "weekly etf pro review",
    "investor report",
    "primary regime",
    "main takeaway",
    "this report is for informational",
]

DUTCH_DELIVERY_FORBIDDEN_TOKENS = [
    "Wednesday,",
    "Thursday,",
    "Friday,",
    "Saturday,",
    "Sunday,",
    "Monday,",
    "Tuesday,",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
    "PRIMARY REGIME",
    "GEOPOLITICAL REGIME",
    "MAIN TAKEAWAY",
    "Investor Report",
    "Investment Report",
    "Analyst Report",
    "Mixed / not yet decisive",
    "Keep the current allocation",
    "confidence",
    "Equity Curve (EUR)",
    "Portfolio value (EUR)",
]

RAW_MARKDOWN_LINK_RE = re.compile(r"\[([A-Z][A-Z0-9.-]{0,14})\]\((https?://[^\s\)]+)\)")
MINI_CARD_TRIPLE_RE = re.compile(
    r"(?:<div class=['\"]mini-card['\"]>\s*"
    r"<div class=['\"]mini-label['\"]>.*?</div>\s*"
    r"<div class=['\"]mini-value['\"]>.*?</div>\s*"
    r"</div>\s*){3}",
    re.DOTALL,
)


def looks_dutch_markdown(md_text: str | None) -> bool:
    lower = (md_text or "").lower()
    dutch_score = sum(marker in lower for marker in DUTCH_MD_MARKERS)
    english_score = sum(marker in lower for marker in ENGLISH_MD_MARKERS)
    return dutch_score >= 2 and dutch_score > english_score


def _strip_md(value: str) -> str:
    value = RAW_MARKDOWN_LINK_RE.sub(lambda m: m.group(1), value)
    value = value.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", value).strip()


def _section_one_pairs(md_text: str | None) -> dict[str, str]:
    pairs: dict[str, str] = {}
    in_section = False
    for raw in (md_text or "").splitlines():
        stripped = raw.strip()
        if stripped.startswith("## 1."):
            in_section = True
            continue
        if in_section and stripped.startswith("## 2."):
            break
        if not in_section or not stripped.startswith("-") or ":" not in stripped:
            continue
        key, value = stripped.lstrip("- ").split(":", 1)
        pairs[_strip_md(key).lower()] = _strip_md(value)
    return pairs


def _summary_values(md_text: str | None, language: str) -> dict[str, str]:
    pairs = _section_one_pairs(md_text)
    if language == "nl":
        return {
            "primary": pairs.get("primair regime") or pairs.get("primary regime") or "",
            "geo": pairs.get("geopolitiek regime") or pairs.get("geopolitical regime") or "",
            "takeaway": pairs.get("belangrijkste conclusie") or pairs.get("kernconclusie") or pairs.get("main takeaway") or "",
        }
    return {
        "primary": pairs.get("primary regime") or pairs.get("primair regime") or "",
        "geo": pairs.get("geopolitical regime") or pairs.get("geopolitiek regime") or "",
        "takeaway": pairs.get("main takeaway") or pairs.get("belangrijkste conclusie") or pairs.get("kernconclusie") or "",
    }


def _hero_cards_html(md_text: str | None, language: str) -> str:
    values = _summary_values(md_text, language)
    if language == "nl":
        labels = ("Primair regime", "Geopolitiek regime", "Kernconclusie")
        fallbacks = ("Gemengd / nog niet doorslaggevend", "Gemengd / nog niet doorslaggevend", "Houd de huidige allocatie gedisciplineerd.")
    else:
        labels = ("Primary regime", "Geopolitical regime", "Main takeaway")
        fallbacks = ("Mixed / not yet decisive", "Mixed / not yet decisive", "Keep the current allocation disciplined.")
    primary = values.get("primary") or fallbacks[0]
    geo = values.get("geo") or fallbacks[1]
    takeaway = values.get("takeaway") or fallbacks[2]
    return (
        f"<div class='mini-card'><div class='mini-label'>{escape(labels[0])}</div><div class='mini-value'>{escape(primary)}</div></div>"
        f"<div class='mini-card'><div class='mini-label'>{escape(labels[1])}</div><div class='mini-value'>{escape(geo)}</div></div>"
        f"<div class='mini-card'><div class='mini-label'>{escape(labels[2])}</div><div class='mini-value'>{escape(takeaway)}</div></div>"
    )


def replace_hero_cards_from_markdown(html: str, md_text: str | None, language: str) -> str:
    replacement = _hero_cards_html(md_text, language)
    return MINI_CARD_TRIPLE_RE.sub(replacement, html, count=1)


def localize_dutch_delivery_html(html: str) -> str:
    for source, target in DUTCH_HTML_TOKEN_REPLACEMENTS.items():
        html = html.replace(source, target)
    return localize_english_report_dates(html)


def convert_residual_markdown_links(html: str) -> str:
    """Convert markdown links that survived custom HTML rendering into anchors."""
    def repl(match: re.Match[str]) -> str:
        label = escape(match.group(1))
        url = escape(match.group(2), quote=True)
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'

    return RAW_MARKDOWN_LINK_RE.sub(repl, html)


def _apply_global_client_token_replacements(html: str) -> str:
    for forbidden, replacement in CLIENT_FACING_TOKEN_REPLACEMENTS.items():
        html = html.replace(forbidden, replacement)
    return html


def sanitize_client_facing_html(html: str, *, md_text: str | None = None, language: str | None = None) -> str:
    """Remove internal/runtime placeholder language from final client-facing HTML."""
    resolved_language = language or ("nl" if looks_dutch_markdown(md_text) else "en")
    html = replace_hero_cards_from_markdown(html, md_text, resolved_language)
    html = _apply_global_client_token_replacements(html)
    html = convert_residual_markdown_links(html)
    if resolved_language == "nl":
        html = localize_dutch_delivery_html(html)
    # Re-apply hero cards after generic localization to preserve exact section-1
    # values and keep the executive summary link-free. Then re-apply global
    # forbidden-token cleanup so a missing section-1 value cannot reintroduce
    # delivery-blocking placeholders such as `Pending classification`.
    html = replace_hero_cards_from_markdown(html, md_text, resolved_language)
    html = _apply_global_client_token_replacements(html)
    html = convert_residual_markdown_links(html)
    return html


def validate_dutch_delivery_language(html: str, report_name: str) -> None:
    remaining = [token for token in DUTCH_DELIVERY_FORBIDDEN_TOKENS if token in html]
    if remaining:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Dutch delivery HTML still contains English/client-facing tokens: "
            + ", ".join(sorted(set(remaining)))
        )
