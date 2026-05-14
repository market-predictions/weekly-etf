from __future__ import annotations

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


def looks_dutch_markdown(md_text: str | None) -> bool:
    lower = (md_text or "").lower()
    dutch_score = sum(marker in lower for marker in DUTCH_MD_MARKERS)
    english_score = sum(marker in lower for marker in ENGLISH_MD_MARKERS)
    return dutch_score >= 2 and dutch_score > english_score


def localize_dutch_delivery_html(html: str) -> str:
    for source, target in DUTCH_HTML_TOKEN_REPLACEMENTS.items():
        html = html.replace(source, target)
    return localize_english_report_dates(html)


def sanitize_client_facing_html(html: str, *, md_text: str | None = None, language: str | None = None) -> str:
    """Remove internal/runtime placeholder language from final client-facing HTML.

    For Dutch delivery output this also applies the delivery-layer Dutch cover,
    date and chart-label localization. This keeps markdown localization and
    delivery HTML localization aligned and avoids validator drift.
    """
    for forbidden, replacement in CLIENT_FACING_TOKEN_REPLACEMENTS.items():
        html = html.replace(forbidden, replacement)
    if language == "nl" or (language is None and looks_dutch_markdown(md_text)):
        html = localize_dutch_delivery_html(html)
    return html


def validate_dutch_delivery_language(html: str, report_name: str) -> None:
    remaining = [token for token in DUTCH_DELIVERY_FORBIDDEN_TOKENS if token in html]
    if remaining:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Dutch delivery HTML still contains English/client-facing tokens: "
            + ", ".join(sorted(set(remaining)))
        )
