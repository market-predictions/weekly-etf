from __future__ import annotations

import re
from html import escape

from runtime import nl_terminology_contract as contract
from runtime.nl_dates import localize_english_report_dates
from runtime.wp16_followup3_cleanup import clean_text

CLIENT_FACING_TOKEN_REPLACEMENTS = contract.CLIENT_FACING_TOKEN_REPLACEMENTS
DUTCH_HTML_TOKEN_REPLACEMENTS = contract.CLIENT_SURFACE_EXACT_REPLACEMENTS | {
    "Risk-on narrow US mega-cap leadership": "Risk-on met smal Amerikaans mega-capleiderschap",
    "Risk-on narrow U.S. mega-cap leadership": "Risk-on met smal Amerikaans mega-capleiderschap",
    "Risk-on narrow leadership": "Risk-on met smal marktleiderschap",
    "Risk-on smal marktleiderschap": "Risk-on met smal marktleiderschap",
    "Fresh capital only after review or at smaller size": "Nieuw kapitaal alleen kleiner of na herbeoordeling inzetten",
    "Position does not pass the fresh-capital test": "Positie voldoet niet aan de vers-kapitaaltoets",
    "Position is under replacement review": "Positie staat onder vervangingsreview",
    "Review has persisted for multiple report cycles": "Review loopt al meerdere rapportcycli",
    "Review has persisted for several report cycles": "Review loopt al meerdere rapportcycli",
    "Portfolio role is impaired": "Portefeuillerol is verzwakt",
    "Proposed destination from the rotation plan": "Voorgestelde bestemming uit het rotatieplan",
    "System override: rotation budget already used": "Systeemoverride: rotatiebudget is al gebruikt",
    "rotation budget already used": "rotatiebudget is al gebruikt",
    "Decision rationale": "Toelichting",
}
DUTCH_MD_MARKERS = contract.DUTCH_MD_MARKERS
ENGLISH_MD_MARKERS = contract.ENGLISH_MD_MARKERS
DUTCH_DELIVERY_FORBIDDEN_TOKENS = contract.DUTCH_DELIVERY_FORBIDDEN_TOKENS

RAW_MARKDOWN_LINK_RE = re.compile(r"\[([A-Z][A-Z0-9.-]{0,14})\]\((https?://[^\s\)]+)\)")
TICKER_REF_RE = r"(?:\[[^\]]+\]\([^\)]+\)|<a\b[^>]*>\s*[A-Z][A-Z0-9.-]*\s*</a>|[A-Z][A-Z0-9.-]*)"
EN_DOUBLE_NEGATIVE_RE = re.compile(rf"(\breduce\s+{TICKER_REF_RE}\s+by\s+)-(?=\d+(?:\.\d+)?%)", re.IGNORECASE)
NL_DOUBLE_NEGATIVE_RE = re.compile(rf"(\bverlaag\s+{TICKER_REF_RE}\s+met\s+)-(?=\d+(?:\.\d+)?%)", re.IGNORECASE)
MINI_CARD_TRIPLE_RE = re.compile(
    r"(?:<div class=['\"]mini-card['\"]>\s*"
    r"<div class=['\"]mini-label['\"]>.*?</div>\s*"
    r"<div class=['\"]mini-value['\"]>.*?</div>\s*"
    r"</div>\s*){3}",
    re.DOTALL,
)
PANEL_EXEC_OPEN_RE = re.compile(
    r"<div\b(?=[^>]*\bclass\s*=\s*['\"][^'\"]*\bpanel-exec\b)[^>]*>",
    re.IGNORECASE,
)
PANEL_REPLACEMENT_DUEL_OPEN_RE = re.compile(
    r"<div\b(?=[^>]*\bclass\s*=\s*['\"][^'\"]*\bpanel-replacement-duel\b)[^>]*>",
    re.IGNORECASE,
)
DIV_TAG_RE = re.compile(r"</?div\b[^>]*>", re.IGNORECASE)
PANEL_EXEC_TO_NEXT_PANEL_RE = re.compile(
    r"<div\b(?=[^>]*\bclass\s*=\s*['\"][^'\"]*\bpanel-exec\b)[^>]*>.*?(?=<div\b(?=[^>]*\bclass\s*=\s*['\"][^'\"]*\bpanel\b)[^>]*>)",
    re.DOTALL | re.IGNORECASE,
)
SECTION_BADGE_REPLACEMENT_DUEL_RE = re.compile(
    r"(<span\s+class=['\"]section-badge['\"]>)\s*11\s*(</span>\s*</td>\s*<td\s+class=['\"]section-label-cell['\"]>\s*<span\s+class=['\"]section-label['\"]>\s*Replacement Duel Table\s*</span>)",
    re.IGNORECASE,
)
EMPTY_COMMENT_ARTIFACT_RE = re.compile(
    r"(?:<p[^>]*>\s*)?(?:&lt;!|<!)\s*--\s*--\s*(?:&gt;|>)(?:\s*</p>)?",
    re.IGNORECASE,
)
HERO_LAYOUT_GUARD_CSS = """
<style id="etf-hero-layout-guard">
  .summary-strip .mini-card {
    overflow: hidden;
  }
  .summary-strip .mini-value {
    overflow-wrap: break-word;
    word-break: normal;
    hyphens: auto;
  }
  .summary-strip .mini-card:nth-child(3) .mini-value {
    font-size: 19px;
    line-height: 1.22;
  }
  .panel-equity,
  .equity-curve-panel,
  .equity-curve {
    break-inside: avoid;
    page-break-inside: avoid;
    overflow: visible;
  }
  .panel-equity img,
  .equity-curve-panel img,
  .equity-curve img,
  img[src*="equity"],
  img[alt*="Equity"],
  img[alt*="Portefeuillecurve"] {
    display: block;
    width: 100%;
    max-width: 100%;
    height: auto;
    max-height: none;
    object-fit: contain;
    object-position: center center;
  }
  @media screen and (max-width: 1100px) {
    .summary-strip .mini-card:nth-child(3) .mini-value {
      font-size: 18px;
      line-height: 1.24;
    }
  }
</style>
"""


def _visible_exec_summary_marker(language: str) -> str:
    label = "Kernsamenvatting" if language == "nl" else "Executive Summary"
    return (
        "<div class='panel panel-exec-visible'>"
        "<table class='section-kicker' role='presentation' cellpadding='0' cellspacing='0'><tr>"
        "<td class='section-badge-cell'><span class='section-badge'>1</span></td>"
        f"<td class='section-label-cell'><span class='section-label'>{escape(label)}</span></td>"
        "</tr></table>"
        "</div>"
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
    def repl(match: re.Match[str]) -> str:
        label = escape(match.group(1))
        url = escape(match.group(2), quote=True)
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'

    return RAW_MARKDOWN_LINK_RE.sub(repl, html)


def _apply_global_client_token_replacements(html: str, *, language: str) -> str:
    for forbidden, replacement in CLIENT_FACING_TOKEN_REPLACEMENTS.items():
        html = html.replace(forbidden, replacement)
    html = clean_text(html, language=language)
    html = EN_DOUBLE_NEGATIVE_RE.sub(r"\1", html)
    html = NL_DOUBLE_NEGATIVE_RE.sub(r"\1", html)
    return html


def remove_empty_comment_artifacts(html: str) -> str:
    return EMPTY_COMMENT_ARTIFACT_RE.sub("", html).replace("&lt;!-- --&gt;", "").replace("<!-- -->", "")


def inject_hero_layout_guard(html: str) -> str:
    if "etf-hero-layout-guard" in html:
        return html
    if "</head>" in html:
        return html.replace("</head>", HERO_LAYOUT_GUARD_CSS + "\n</head>", 1)
    return HERO_LAYOUT_GUARD_CSS + html


def _find_matching_div_end(html: str, start: int) -> int | None:
    depth = 0
    seen_start = False
    for tag in DIV_TAG_RE.finditer(html, start):
        is_close = tag.group(0).startswith("</")
        if not is_close:
            depth += 1
            seen_start = True
        elif seen_start:
            depth -= 1
            if depth == 0:
                return tag.end()
    return None


def _remove_panel_blocks_by_depth(html: str, pattern: re.Pattern[str], replacement: str = "") -> tuple[str, int]:
    count = 0
    cursor = 0
    out: list[str] = []
    for match in pattern.finditer(html):
        start = match.start()
        if start < cursor:
            continue
        end = _find_matching_div_end(html, start)
        if end is None:
            continue
        out.append(html[cursor:start])
        out.append(replacement if count == 0 else "")
        cursor = end
        count += 1
    if count == 0:
        return html, 0
    out.append(html[cursor:])
    return "".join(out), count


def suppress_duplicate_executive_panel(html: str, *, language: str = "en") -> str:
    marker = _visible_exec_summary_marker(language)
    updated, count = _remove_panel_blocks_by_depth(html, PANEL_EXEC_OPEN_RE, marker)
    if count:
        return updated
    updated, fallback_count = PANEL_EXEC_TO_NEXT_PANEL_RE.subn(marker, html, count=1)
    return updated if fallback_count else html


def _has_embedded_replacement_duel(html: str) -> bool:
    if "ETF_REPLACEMENT_DUEL_V2_EMBEDDED" in html:
        return True
    panel_pos = html.find("panel-replacement-duel")
    prefix = html if panel_pos == -1 else html[:panel_pos]
    dutch_header = "Huidige positie" in prefix and "Alternatief" in prefix and "Benodigde bevestiging" in prefix
    english_header = "Current holding" in prefix and "Challenger" in prefix and "Required trigger" in prefix
    return dutch_header or english_header


def _de_stale_replacement_duel_badge(html: str) -> str:
    return SECTION_BADGE_REPLACEMENT_DUEL_RE.sub(r"\g<1>4B\g<2>", html)


def remove_duplicate_replacement_duel_panel(html: str) -> str:
    has_embedded = _has_embedded_replacement_duel(html)
    if has_embedded:
        html, _ = _remove_panel_blocks_by_depth(html, PANEL_REPLACEMENT_DUEL_OPEN_RE, "")
        html = html.replace("<!-- ETF_REPLACEMENT_DUEL_V2_EMBEDDED -->", "")
        html = html.replace("ETF_REPLACEMENT_DUEL_V2_EMBEDDED", "")
    else:
        html = _de_stale_replacement_duel_badge(html)
    html = html.replace("Replacement Duel Table v2", "Replacement Duel Table")
    return html


def sanitize_client_facing_html(html: str, *, md_text: str | None = None, language: str | None = None) -> str:
    resolved_language = language or ("nl" if looks_dutch_markdown(md_text) else "en")
    html = clean_text(remove_empty_comment_artifacts(html), language=resolved_language)
    html = remove_duplicate_replacement_duel_panel(html)
    html = suppress_duplicate_executive_panel(html, language=resolved_language)
    html = replace_hero_cards_from_markdown(html, md_text, resolved_language)
    html = _apply_global_client_token_replacements(html, language=resolved_language)
    html = convert_residual_markdown_links(html)
    if resolved_language == "nl":
        html = localize_dutch_delivery_html(html)
    html = clean_text(remove_empty_comment_artifacts(html), language=resolved_language)
    html = remove_duplicate_replacement_duel_panel(html)
    html = suppress_duplicate_executive_panel(html, language=resolved_language)
    html = replace_hero_cards_from_markdown(html, md_text, resolved_language)
    html = suppress_duplicate_executive_panel(html, language=resolved_language)
    html = inject_hero_layout_guard(html)
    html = _apply_global_client_token_replacements(html, language=resolved_language)
    html = convert_residual_markdown_links(html)
    html = remove_duplicate_replacement_duel_panel(html)
    return clean_text(remove_empty_comment_artifacts(html), language=resolved_language)


def validate_dutch_delivery_language(html: str, report_name: str) -> None:
    remaining = [token for token in DUTCH_DELIVERY_FORBIDDEN_TOKENS if token in html]
    if remaining:
        raise RuntimeError(
            f"Delivery HTML contract validation failed for {report_name}: Dutch delivery HTML still contains English/client-facing tokens: "
            + ", ".join(sorted(set(remaining)))
        )
