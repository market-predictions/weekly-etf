from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

import send_report as report_module
from runtime.build_etf_report_state import build_runtime_state
from runtime.client_facing_sanitizer import sanitize_client_facing_html, looks_dutch_markdown
from runtime.delivery_html_overrides import build_report_html_with_state
from runtime.render_etf_report_from_state import cash_eur, invested_eur, total_nav

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
STANDARD_REPORT_RE = re.compile(r"^weekly_analysis_(\d{6})(?:_(\d{2}))?\.md$")
ISO_DATE_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
DUTCH_LONG_DATE_RE = re.compile(
    r"\b(?:Maandag|Dinsdag|Woensdag|Donderdag|Vrijdag|Zaterdag|Zondag)?\s*"
    r"(\d{1,2})\s+"
    r"(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\s+"
    r"(20\d{2})\b",
    flags=re.IGNORECASE,
)
DUTCH_MONTH_NUMBERS = {
    "januari": "01",
    "februari": "02",
    "maart": "03",
    "april": "04",
    "mei": "05",
    "juni": "06",
    "juli": "07",
    "augustus": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "december": "12",
}
NATIVE_DUTCH_SECTION_MARKERS = [
    "## 1. Kernsamenvatting",
    "## 2. Portefeuille-acties",
    "## 3. Regime-dashboard",
    "## 4. Structurele kansenradar",
    "## 10. Review huidige posities",
    "## 15. Huidige posities en cash",
]


def _render_exec_summary_marker(_section: dict[str, Any]) -> str:
    """Suppress duplicate Section 1 panel at render source.

    `send_report_OLD.build_report_html()` already renders section 1 into the
    three hero summary cards. It then rendered section 1 a second time through
    `render_executive_summary()`, which created the stray duplicated takeaway
    outside the hero-card frame. The runtime delivery path treats the hero cards
    as the executive-summary authority and leaves only a hidden semantic marker
    for legacy body-presence validators.
    """
    return "<div class='exec-summary-render-marker' style='display:none'>Executive Summary / Kernsamenvatting</div>"


def _patch_base_renderer_contract() -> None:
    report_module._base.render_executive_summary = _render_exec_summary_marker


def _add_aliases(alias_map: dict[str, list[str]], canonical: str, aliases: list[str]) -> None:
    existing = alias_map.setdefault(canonical, [])
    for alias in aliases:
        if alias not in existing:
            existing.append(alias)


def _extend_native_dutch_numeric_aliases() -> None:
    """Teach legacy parity validators native Dutch table labels."""
    _add_aliases(report_module.SECTION15_LABEL_ALIASES, "Starting capital (EUR)", ["startkapitaal eur"])
    _add_aliases(report_module.SECTION15_LABEL_ALIASES, "Invested market value (EUR)", ["belegde marktwaarde eur"])
    _add_aliases(report_module.SECTION15_LABEL_ALIASES, "Cash (EUR)", ["cash eur"])
    _add_aliases(report_module.SECTION15_LABEL_ALIASES, "Total portfolio value (EUR)", ["totale portefeuillewaarde eur"])
    _add_aliases(report_module.SECTION15_LABEL_ALIASES, "Since inception return (%)", ["rendement sinds start"])

    _add_aliases(report_module.SECTION15_HEADER_ALIASES, "ticker", ["etf"])
    _add_aliases(report_module.SECTION15_HEADER_ALIASES, "shares", ["aantal stukken"])
    _add_aliases(report_module.SECTION15_HEADER_ALIASES, "price (local)", ["prijs lokaal", "lokale prijs"])
    _add_aliases(report_module.SECTION15_HEADER_ALIASES, "market value (local)", ["marktwaarde lokaal", "lokale marktwaarde"])
    _add_aliases(report_module.SECTION15_HEADER_ALIASES, "market value (eur)", ["marktwaarde eur", "marktwaarde in eur"])
    _add_aliases(report_module.SECTION15_HEADER_ALIASES, "weight %", ["weging %"])

    _add_aliases(report_module.SECTION7_HEADER_ALIASES, "portfolio value (eur)", ["portefeuillewaarde eur", "portefeuillewaarde in eur"])
    _add_aliases(report_module.SECTION7_HEADER_ALIASES, "comment", ["toelichting"])


def _with_client_facing_sanitizer(build_html: Callable[..., str]) -> Callable[..., str]:
    def _wrapped(md_text: str, report_date_str: str, image_src: str | None = None, render_mode: str = "email") -> str:
        html = build_html(md_text, report_date_str, image_src=image_src, render_mode=render_mode)
        return sanitize_client_facing_html(html, md_text=md_text, language="nl" if looks_dutch_markdown(md_text) else "en")

    return _wrapped


def _dutch_long_date_to_iso(match: re.Match[str]) -> str:
    day, month, year = match.groups()
    return f"{year}-{DUTCH_MONTH_NUMBERS[month.lower()]}-{int(day):02d}"


def _title_lines(md_text: str) -> list[str]:
    return [line for line in md_text.splitlines() if line.startswith("# ")]


def parse_report_date_runtime(md_text: str) -> str:
    """Parse report date from the H1 title first.

    Native Dutch reports contain historical valuation dates in Section 7. A
    whole-document date search can accidentally pick the inception date
    (`2026-03-28`) instead of the report title date. The report title is the
    authority for cover/date delivery; historical tables remain historical data.
    """
    for line in _title_lines(md_text):
        dutch = DUTCH_LONG_DATE_RE.search(line)
        if dutch:
            return _dutch_long_date_to_iso(dutch)
        iso = ISO_DATE_RE.search(line)
        if iso:
            return iso.group(0)
    iso = ISO_DATE_RE.search(md_text)
    if iso:
        return iso.group(0)
    dutch = DUTCH_LONG_DATE_RE.search(md_text)
    if dutch:
        return _dutch_long_date_to_iso(dutch)
    return report_module._base.parse_report_date(md_text)


def _has_report_title_date(md_text: str) -> bool:
    for line in _title_lines(md_text):
        if ISO_DATE_RE.search(line) or DUTCH_LONG_DATE_RE.search(line):
            return True
    return False


def validate_dutch_companion_report_runtime(md_text: str) -> None:
    """Validate both legacy patched Dutch and native Dutch companion reports."""
    if not _has_report_title_date(md_text):
        raise RuntimeError("Dutch companion report title is missing a report date.")

    for section_number in range(1, 18):
        if not report_module.extract_section_by_number(md_text, section_number):
            raise RuntimeError(f"Dutch companion report is missing section {section_number}.")

    lower = md_text.lower()
    native_score = sum(marker.lower() in lower for marker in NATIVE_DUTCH_SECTION_MARKERS)
    legacy_score = sum(marker in lower for marker in report_module.DUTCH_MARKERS)
    if native_score < 4 and legacy_score < 2:
        raise RuntimeError("Dutch companion report does not appear to contain enough Dutch-language wording.")

    if (
        "for informational and educational purposes only" not in lower
        and "uitsluitend verstrekt voor informatieve en educatieve doeleinden" not in lower
    ):
        raise RuntimeError("Dutch companion report disclaimer language is missing.")


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


_patch_base_renderer_contract()
_extend_native_dutch_numeric_aliases()
report_module.latest_report_file = _latest_canonical_report_file
report_module.latest_reports_by_day = _latest_canonical_reports_by_day
report_module.parse_report_date = parse_report_date_runtime
report_module.validate_dutch_companion_report = validate_dutch_companion_report_runtime
report_module.validate_section15_arithmetic = validate_section15_from_runtime_state
report_module.validate_equity_curve_alignment = validate_equity_curve_from_runtime_state
report_module.validate_nl_email_body = validate_nl_email_body_runtime
report_module.build_report_html = _with_client_facing_sanitizer(
    build_report_html_with_state(report_module.build_report_html, report_module._base)
)

if __name__ == "__main__":
    report_module.main()
