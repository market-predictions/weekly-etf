from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

import send_report as report_module
from runtime.build_etf_report_state import build_runtime_state
from runtime.delivery_html_overrides import build_report_html_with_state
from runtime.nl_dates import localize_english_report_dates
from runtime.render_etf_report_from_state import cash_eur, invested_eur, total_nav

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
STANDARD_REPORT_RE = re.compile(r"^weekly_analysis_(\d{6})(?:_(\d{2}))?\.md$")

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


def _looks_dutch(md_text: str) -> bool:
    """Detect Dutch from the markdown itself, never from global env."""
    lower = (md_text or "").lower()
    dutch_score = sum(marker in lower for marker in DUTCH_MD_MARKERS)
    english_score = sum(marker in lower for marker in ENGLISH_MD_MARKERS)
    return dutch_score >= 2 and dutch_score > english_score


def _localize_dutch_delivery_html(html: str) -> str:
    for src, dst in DUTCH_HTML_TOKEN_REPLACEMENTS.items():
        html = html.replace(src, dst)
    return localize_english_report_dates(html)


def _sanitize_client_facing_html(html: str, md_text: str | None = None) -> str:
    for forbidden, replacement in CLIENT_FACING_TOKEN_REPLACEMENTS.items():
        html = html.replace(forbidden, replacement)
    if md_text and _looks_dutch(md_text):
        html = _localize_dutch_delivery_html(html)
    return html


def _with_client_facing_sanitizer(build_html: Callable[..., str]) -> Callable[..., str]:
    def _wrapped(md_text: str, report_date_str: str, image_src: str | None = None, render_mode: str = "email") -> str:
        html = build_html(md_text, report_date_str, image_src=image_src, render_mode=render_mode)
        return _sanitize_client_facing_html(html, md_text=md_text)

    return _wrapped


def validate_nl_email_body_runtime(html_body: str, md_text: str) -> None:
    """Dutch delivery validator aligned with Dutch masthead localization."""
    html_lower = html_body.lower()
    masthead_options = [
        "weekly etf review",
        "weekly report review",
        "weekly etf intelligence",
        "weekly etf pro review",
        "wekelijkse etf-review",
        "wekelijkse etf review",
        "wekelijks etf-review",
        "wekelijks etf review",
        "beleggersrapport",
    ]
    if not any(token in html_lower for token in masthead_options):
        raise RuntimeError("Dutch HTML body is missing required masthead block.")

    required_groups = [
        ["executive summary", "samenvatting", "kernsamenvatting"],
        ["portfolio action snapshot", "portefeuille", "actie", "portefeuille-acties"],
        ["structural opportunity radar", "structurele kansenradar"],
        ["current portfolio holdings and cash", "huidige portefeuille", "holdings en cash", "huidige posities en cash"],
    ]
    for group in required_groups:
        if not any(token in html_lower for token in group):
            raise RuntimeError(f"Dutch HTML body is missing a required content block from: {group}")

    plain_html = report_module._base.html_to_plain_text(html_body)
    plain_md = report_module._base.html_to_plain_text(report_module._base.MARKDOWN(md_text))
    if len(plain_html) < 0.72 * len(plain_md):
        raise RuntimeError("Dutch HTML body appears too short relative to the full report.")

    for bad_token in ["\\n", "#### ", "|---|", "\\t"]:
        if bad_token in html_body:
            raise RuntimeError(f"Dutch HTML body still contains raw markdown / escaped formatting token: {bad_token}")


def _canonical_report_key(path: Path, mode: str) -> tuple[str, int] | None:
    match = PRO_REPORT_RE.match(path.name) if mode == "pro" else STANDARD_REPORT_RE.match(path.name)
    if not match:
        return None
    return match.group(1), int(match.group(2) or "1")


def _explicit_report_path(mode: str) -> Path | None:
    raw = report_module.os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH", "").strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.exists():
        raise RuntimeError(f"Explicit report path does not exist: {path}")
    if _canonical_report_key(path, report_module.normalize_report_mode(mode)) is None:
        raise RuntimeError(f"Explicit report path is not a canonical {mode} report: {path}")
    return path


def _latest_canonical_report_file(output_dir: Path, mode: str = "standard") -> Path:
    normalized_mode = report_module.normalize_report_mode(mode)
    explicit = _explicit_report_path(normalized_mode)
    if explicit is not None:
        return explicit

    candidates: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_analysis*.md"):
        key = _canonical_report_key(path, normalized_mode)
        if key is not None:
            candidates.append((key[0], key[1], path))
    if not candidates:
        raise RuntimeError(f"No canonical {normalized_mode} report files found in {output_dir}.")
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[-1][2]


def _latest_canonical_reports_by_day(output_dir: Path, mode: str = "standard") -> list[Path]:
    normalized_mode = report_module.normalize_report_mode(mode)
    explicit = _explicit_report_path(normalized_mode)
    if explicit is not None:
        return [explicit]

    by_day: dict[str, tuple[int, Path]] = {}
    for path in output_dir.glob("weekly_analysis*.md"):
        key = _canonical_report_key(path, normalized_mode)
        if key is None:
            continue
        day, version = key
        if day not in by_day or version > by_day[day][0]:
            by_day[day] = (version, path)
    return [item[1] for item in sorted(by_day.values(), key=lambda row: row[1].name)]


def _as_float(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Runtime state validation failed: non-numeric {label}: {value!r}") from exc


def validate_section15_from_runtime_state(_md_text: str | None = None, tolerance: float = 0.05) -> None:
    state = build_runtime_state()
    positions = state.get("positions", []) or []
    if not isinstance(positions, list) or not positions:
        raise RuntimeError("Runtime state validation failed: no positions found.")

    invested = invested_eur(state)
    cash = cash_eur(state)
    nav = total_nav(state)
    if invested <= 0 or nav <= 0:
        raise RuntimeError("Runtime state validation failed: invested value or NAV is not positive.")
    if cash < -tolerance:
        raise RuntimeError("Runtime state validation failed: cash is negative.")
    if abs((invested + cash) - nav) > tolerance:
        raise RuntimeError(f"Runtime state validation failed: invested + cash does not reconcile to NAV ({invested:.2f} + {cash:.2f} vs {nav:.2f}).")

    for position in positions:
        ticker = str(position.get("ticker") or "").strip().upper()
        if not ticker:
            raise RuntimeError("Runtime state validation failed: position missing ticker.")
        shares = _as_float(position.get("shares"), f"shares for {ticker}")
        price = _as_float(position.get("previous_price_local"), f"price for {ticker}")
        value_eur = _as_float(position.get("previous_market_value_eur"), f"EUR value for {ticker}")
        if shares <= 0 or price <= 0 or value_eur <= 0:
            raise RuntimeError(f"Runtime state validation failed: invalid numeric position data for {ticker}.")

    print(f"RUNTIME_SECTION15_OK | positions={len(positions)} | invested_eur={invested:.2f} | cash_eur={cash:.2f} | total_nav={nav:.2f}")


def validate_equity_curve_from_runtime_state(_md_text: str | None = None, tolerance: float = 0.05) -> None:
    state = build_runtime_state()
    nav = total_nav(state)
    if nav <= 0:
        raise RuntimeError("Runtime equity validation failed: NAV is not positive.")
    print(f"RUNTIME_EQUITY_CURVE_OK | latest_nav={nav:.2f}")


report_module.latest_report_file = _latest_canonical_report_file
report_module.latest_reports_by_day = _latest_canonical_reports_by_day
report_module.validate_section15_arithmetic = validate_section15_from_runtime_state
report_module.validate_equity_curve_alignment = validate_equity_curve_from_runtime_state
report_module.validate_nl_email_body = validate_nl_email_body_runtime
report_module.build_report_html = _with_client_facing_sanitizer(
    build_report_html_with_state(report_module.build_report_html, report_module._base)
)

if __name__ == "__main__":
    report_module.main()
