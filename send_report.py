from __future__ import annotations

import base64
import os
import re
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    import send_report_OLD as _base
except ImportError as exc:
    raise RuntimeError(
        "send_report_OLD.py not found. Before renaming this file into send_report.py, "
        "rename the current production send_report.py to send_report_OLD.py and keep it in the repo as backup."
    ) from exc

from validate_lane_breadth import validate_report_breadth_proof

normalize_report_mode = _base.normalize_report_mode
latest_report_file = _base.latest_report_file
latest_reports_by_day = _base.latest_reports_by_day
normalize_markdown_text = _base.normalize_markdown_text
strip_citations = _base.strip_citations
clean_md_inline = _base.clean_md_inline
is_markdown_table_line = _base.is_markdown_table_line
is_markdown_separator_line = _base.is_markdown_separator_line
parse_markdown_table = _base.parse_markdown_table
parse_report_date = _base.parse_report_date
extract_section = _base.extract_section
validate_required_report = _base.validate_required_report
validate_email_body = _base.validate_email_body
build_report_html = _base.build_report_html
create_pdf_from_html = _base.create_pdf_from_html
send_email_with_attachments = _base.send_email_with_attachments

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
PRO_NL_REPORT_RE = re.compile(r"^weekly_analysis_pro_nl_(\d{6})(?:_(\d{2}))?\.md$")
SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+(.*)$")

SECTION15_LABEL_ALIASES = {
    "Starting capital (EUR)": ["starting capital (eur)", "startkapitaal (eur)"],
    "Invested market value (EUR)": ["invested market value (eur)", "belegde marktwaarde (eur)"],
    "Cash (EUR)": ["cash (eur)"],
    "Total portfolio value (EUR)": ["total portfolio value (eur)", "totale portefeuillewaarde (eur)"],
    "Since inception return (%)": ["since inception return (%)", "rendement sinds start (%)"],
    "EUR/USD used": ["eur/usd used", "eur/usd gebruikt"],
}

SECTION15_HEADER_ALIASES = {
    "ticker": ["ticker"],
    "shares": ["shares", "aantal aandelen"],
    "price (local)": ["price (local)", "prijs (lokaal)"],
    "currency": ["currency", "valuta"],
    "market value (local)": ["market value (local)", "marktwaarde (lokaal)"],
    "market value (eur)": ["market value (eur)", "marktwaarde (eur)"],
    "weight %": ["weight %", "gewicht %"],
}

SECTION7_HEADER_ALIASES = {
    "date": ["date", "datum"],
    "portfolio value (eur)": ["portfolio value (eur)", "portefeuillewaarde (eur)"],
    "comment": ["comment", "opmerking"],
}

DUTCH_MARKERS = [
    "wat is er deze week veranderd",
    "belangrijkste conclusie",
    "beschikbare cash",
    "doorgeschoven waardering",
    "huidige portefeuille",
    "opmerking",
]

NL_SUBJECT_PREFIX_FALLBACK = "Weekly ETF Pro Review | Nederlands"


def _first_markdown_table(lines: list[str]) -> list[str]:
    i = 0
    while i + 1 < len(lines):
        if is_markdown_table_line(lines[i]) and is_markdown_separator_line(lines[i + 1]):
            j = i + 2
            block = [lines[i], lines[i + 1]]
            while j < len(lines) and is_markdown_table_line(lines[j]):
                block.append(lines[j])
                j += 1
            return block
        i += 1
    return []


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    raw = clean_md_inline(value).replace(",", "").replace("%", "").strip()
    if not raw or raw == "-":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _norm_header(value: str) -> str:
    return re.sub(r"\s+", " ", clean_md_inline(value).strip().lower())


def _match_header_alias(header: str, alias_map: dict[str, list[str]]) -> str:
    normalized = _norm_header(header)
    for canonical, aliases in alias_map.items():
        if normalized in aliases:
            return canonical
    return normalized


def _extract_label_pairs(lines: list[str]) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in lines:
        stripped = clean_md_inline(line.strip())
        if not stripped or stripped.startswith("## "):
            continue
        if stripped.startswith("- "):
            stripped = stripped[2:]
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        pairs[_norm_header(key)] = value.strip()
    return pairs


def extract_section_by_number(md_text: str, section_number: int) -> list[str]:
    lines = md_text.splitlines()
    result: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        match = SECTION_RE.match(stripped)
        if match:
            current_number = int(match.group(1))
            if current_number == section_number:
                in_section = True
                result.append(stripped)
                continue
            if in_section:
                break
        elif in_section:
            result.append(line)
    return result


def png_to_data_uri(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def parse_section15_totals_generic(md_text: str) -> dict[str, float]:
    lines = extract_section_by_number(md_text, 15)
    pairs = _extract_label_pairs(lines)
    totals: dict[str, float] = {}
    for canonical, aliases in SECTION15_LABEL_ALIASES.items():
        for alias in aliases:
            if alias in pairs:
                value = _to_float(pairs[alias])
                if value is not None:
                    totals[canonical] = value
                    break
    return totals


def parse_section15_holdings_rows_generic(md_text: str) -> list[dict[str, str]]:
    lines = extract_section_by_number(md_text, 15)
    if not lines:
        return []
    block = _first_markdown_table(lines)
    if not block:
        return []
    rows = parse_markdown_table(block)
    if len(rows) < 2:
        return []
    headers = [_match_header_alias(h, SECTION15_HEADER_ALIASES) for h in rows[0]]
    result = []
    for row in rows[1:]:
        padded = row + [""] * (len(headers) - len(row))
        result.append({headers[idx]: padded[idx] for idx in range(len(headers))})
    return result


def parse_section7_equity_points_generic(md_text: str) -> list[tuple[str, float]]:
    lines = extract_section_by_number(md_text, 7)
    if not lines:
        return []
    block = _first_markdown_table(lines)
    if not block:
        return []
    rows = parse_markdown_table(block)
    if len(rows) < 2:
        return []
    headers = [_match_header_alias(h, SECTION7_HEADER_ALIASES) for h in rows[0]]
    try:
        date_idx = headers.index("date")
        value_idx = headers.index("portfolio value (eur)")
    except ValueError:
        return []

    points: list[tuple[str, float]] = []
    for row in rows[1:]:
        if len(row) <= max(date_idx, value_idx):
            continue
        report_date = clean_md_inline(row[date_idx])
        nav = _to_float(row[value_idx])
        if report_date and nav is not None:
            points.append((report_date, nav))
    return points


def validate_section15_arithmetic(md_text: str, tolerance: float = 0.05) -> None:
    totals = parse_section15_totals_generic(md_text)
    rows = parse_section15_holdings_rows_generic(md_text)
    if not rows:
        raise RuntimeError("Section 15 holdings table is missing or unreadable.")

    invested_sum = 0.0
    cash_sum = 0.0
    total_sum = 0.0

    for row in rows:
        ticker = clean_md_inline(row.get("ticker", ""))
        market_value_eur = _to_float(row.get("market value (eur)"))
        if market_value_eur is None:
            raise RuntimeError(f"Section 15 contains a non-numeric Market value (EUR) cell for ticker: {ticker or 'UNKNOWN'}")
        total_sum += market_value_eur
        if ticker.upper() == "CASH":
            cash_sum += market_value_eur
        else:
            invested_sum += market_value_eur

    if abs(invested_sum - totals.get("Invested market value (EUR)", 0.0)) > tolerance:
        raise RuntimeError("Section 15 arithmetic mismatch: invested market value does not reconcile.")
    if abs(cash_sum - totals.get("Cash (EUR)", 0.0)) > tolerance:
        raise RuntimeError("Section 15 arithmetic mismatch: cash does not reconcile.")
    if abs(total_sum - totals.get("Total portfolio value (EUR)", 0.0)) > tolerance:
        raise RuntimeError("Section 15 arithmetic mismatch: total portfolio value does not reconcile.")


def validate_equity_curve_alignment(md_text: str, tolerance: float = 0.05) -> None:
    points = parse_section7_equity_points_generic(md_text)
    total_label = parse_section15_totals_generic(md_text).get("Total portfolio value (EUR)")
    if not points or total_label is None:
        return
    latest_nav = points[-1][1]
    if abs(latest_nav - total_label) > tolerance:
        raise RuntimeError(
            f"Equity curve mismatch: latest section 7 table value={latest_nav:.2f} but section 15 total portfolio value={total_label:.2f}."
        )


def validate_dutch_companion_report(md_text: str) -> None:
    if not re.search(r"^#\s+.*\d{4}-\d{2}-\d{2}\s*$", md_text, flags=re.MULTILINE):
        raise RuntimeError("Dutch companion report title is missing a report date.")

    for section_number in range(1, 18):
        if not extract_section_by_number(md_text, section_number):
            raise RuntimeError(f"Dutch companion report is missing section {section_number}.")

    lower = md_text.lower()
    if sum(marker in lower for marker in DUTCH_MARKERS) < 2:
        raise RuntimeError("Dutch companion report does not appear to contain enough Dutch-language wording.")

    if (
        "for informational and educational purposes only" not in lower
        and "uitsluitend verstrekt voor informatieve en educatieve doeleinden" not in lower
    ):
        raise RuntimeError("Dutch companion report disclaimer language is missing.")


def validate_nl_email_body(html_body: str, md_text: str) -> None:
    html_lower = html_body.lower()
    masthead_options = [
        "weekly etf review",
        "weekly report review",
        "weekly etf intelligence",
        "weekly etf pro review",
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

    plain_html = _base.html_to_plain_text(html_body)
    plain_md = _base.html_to_plain_text(_base.MARKDOWN(md_text))
    if len(plain_html) < 0.72 * len(plain_md):
        raise RuntimeError("Dutch HTML body appears too short relative to the full report.")

    for bad_token in ["\\n", "#### ", "|---|", "\\t"]:
        if bad_token in html_body:
            raise RuntimeError(f"Dutch HTML body still contains raw markdown / escaped formatting token: {bad_token}")


def _report_identity(path: Path) -> tuple[str, int, str]:
    english = PRO_REPORT_RE.match(path.name)
    if english:
        return english.group(1), int(english.group(2) or "1"), "en"
    dutch = PRO_NL_REPORT_RE.match(path.name)
    if dutch:
        return dutch.group(1), int(dutch.group(2) or "1"), "nl"
    raise RuntimeError(f"Unsupported pro report filename: {path.name}")


def matching_dutch_report_path(report_path_en: Path) -> Path:
    if not PRO_REPORT_RE.match(report_path_en.name):
        raise RuntimeError(f"Not a canonical English pro report filename: {report_path_en.name}")
    return report_path_en.with_name(report_path_en.name.replace("weekly_analysis_pro_", "weekly_analysis_pro_nl_", 1))


def has_matching_dutch_report(report_path_en: Path) -> bool:
    return matching_dutch_report_path(report_path_en).exists()


def validate_bilingual_numeric_parity(md_text_en: str, md_text_nl: str, tolerance: float = 0.05) -> None:
    totals_en = parse_section15_totals_generic(md_text_en)
    totals_nl = parse_section15_totals_generic(md_text_nl)
    for key in SECTION15_LABEL_ALIASES:
        value_en = totals_en.get(key)
        value_nl = totals_nl.get(key)
        if value_en is None or value_nl is None:
            raise RuntimeError(f"Bilingual parity check failed: missing Section 15 total for {key}.")
        if abs(value_en - value_nl) > tolerance:
            raise RuntimeError(f"Bilingual parity mismatch in Section 15 total for {key}: EN={value_en:.2f}, NL={value_nl:.2f}")

    rows_en = parse_section15_holdings_rows_generic(md_text_en)
    rows_nl = parse_section15_holdings_rows_generic(md_text_nl)
    if len(rows_en) != len(rows_nl):
        raise RuntimeError("Bilingual parity mismatch: Section 15 holdings row count differs between EN and NL.")

    numeric_fields = ["price (local)", "market value (local)", "market value (eur)", "weight %"]
    for row_en, row_nl in zip(rows_en, rows_nl):
        ticker_en = clean_md_inline(row_en.get("ticker", "")).upper()
        ticker_nl = clean_md_inline(row_nl.get("ticker", "")).upper()
        if ticker_en != ticker_nl:
            raise RuntimeError(f"Bilingual parity mismatch: holdings ticker order differs ({ticker_en} vs {ticker_nl}).")
        if clean_md_inline(row_en.get("shares", "")) != clean_md_inline(row_nl.get("shares", "")):
            raise RuntimeError(f"Bilingual parity mismatch: share count differs for {ticker_en}.")
        if clean_md_inline(row_en.get("currency", "")) != clean_md_inline(row_nl.get("currency", "")):
            raise RuntimeError(f"Bilingual parity mismatch: currency differs for {ticker_en}.")
        for field in numeric_fields:
            value_en = _to_float(row_en.get(field))
            value_nl = _to_float(row_nl.get(field))
            if value_en is None or value_nl is None:
                raise RuntimeError(f"Bilingual parity mismatch: missing numeric field {field} for {ticker_en}.")
            if abs(value_en - value_nl) > tolerance:
                raise RuntimeError(
                    f"Bilingual parity mismatch for {ticker_en} field {field}: EN={value_en:.2f}, NL={value_nl:.2f}"
                )

    points_en = parse_section7_equity_points_generic(md_text_en)
    points_nl = parse_section7_equity_points_generic(md_text_nl)
    if len(points_en) != len(points_nl):
        raise RuntimeError("Bilingual parity mismatch: Section 7 equity point count differs between EN and NL.")
    for (date_en, nav_en), (date_nl, nav_nl) in zip(points_en, points_nl):
        if date_en != date_nl:
            raise RuntimeError(f"Bilingual parity mismatch: Section 7 date differs ({date_en} vs {date_nl}).")
        if abs(nav_en - nav_nl) > tolerance:
            raise RuntimeError(f"Bilingual parity mismatch: Section 7 NAV differs on {date_en}: EN={nav_en:.2f}, NL={nav_nl:.2f}")


def validate_bilingual_pair(report_path_en: Path) -> None:
    report_path_nl = matching_dutch_report_path(report_path_en)
    if not report_path_nl.exists():
        raise RuntimeError(f"Missing Dutch companion report for {report_path_en.name}: expected {report_path_nl.name}")

    date_en, version_en, _ = _report_identity(report_path_en)
    date_nl, version_nl, _ = _report_identity(report_path_nl)
    if date_en != date_nl or version_en != version_nl:
        raise RuntimeError(
            f"Bilingual pair mismatch: EN report {report_path_en.name} and NL report {report_path_nl.name} do not share date/version."
        )

    md_text_en = strip_citations(normalize_markdown_text(report_path_en.read_text(encoding="utf-8")))
    md_text_nl = strip_citations(normalize_markdown_text(report_path_nl.read_text(encoding="utf-8")))

    validate_required_report(md_text_en, mode="pro")
    validate_report_breadth_proof(md_text_en, report_path_en)
    validate_section15_arithmetic(md_text_en)
    validate_equity_curve_alignment(md_text_en)

    validate_dutch_companion_report(md_text_nl)
    validate_section15_arithmetic(md_text_nl)
    validate_equity_curve_alignment(md_text_nl)

    validate_bilingual_numeric_parity(md_text_en, md_text_nl)


def create_equity_curve_png(output_dir: Path, chart_path: Path, mode: str = "standard", md_text: str | None = None):
    points: list[tuple[str, float]] = []
    if md_text:
        points = parse_section7_equity_points_generic(md_text)
    if not points:
        for report_path in latest_reports_by_day(output_dir, mode=mode):
            hist_md = report_path.read_text(encoding="utf-8")
            report_date = parse_report_date(hist_md)
            nav = parse_section15_totals_generic(hist_md).get("Total portfolio value (EUR)")
            if nav is not None:
                points.append((report_date, nav))
    if not points:
        return None

    dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in points]
    values = [v for _, v in points]
    plt.figure(figsize=(8.8, 3.7))
    plt.plot(dates, values, marker="o", linewidth=2.2)
    plt.title("Equity Curve (EUR)")
    plt.xlabel("Date")
    plt.ylabel("Portfolio value (EUR)")
    plt.grid(True, alpha=0.28)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=180)
    plt.close()
    return chart_path


def generate_delivery_assets(output_dir: Path, report_path: Path, mode: str = "standard", language: str = "en"):
    original_md_text = normalize_markdown_text(report_path.read_text(encoding="utf-8"))
    md_text_clean = strip_citations(original_md_text)

    if language == "en":
        validate_required_report(md_text_clean, mode=mode)
        if mode == "pro":
            validate_report_breadth_proof(md_text_clean, report_path)
    elif language == "nl":
        validate_dutch_companion_report(md_text_clean)
    else:
        raise RuntimeError(f"Unsupported delivery language: {language}")

    validate_section15_arithmetic(md_text_clean)
    validate_equity_curve_alignment(md_text_clean)

    report_date_str = parse_report_date(md_text_clean)
    safe_stem = report_path.stem

    clean_md_path = report_path.with_name(f"{safe_stem}_clean.md")
    clean_md_path.write_text(md_text_clean, encoding="utf-8")

    equity_curve_png = report_path.with_name(f"{safe_stem}_equity_curve.png")
    create_equity_curve_png(output_dir, equity_curve_png, mode=mode, md_text=md_text_clean)

    image_src_pdf = png_to_data_uri(equity_curve_png) if equity_curve_png.exists() else None
    image_src_email = "cid:equitycurve" if equity_curve_png.exists() else None
    html_email = build_report_html(md_text_clean, report_date_str, image_src=image_src_email, render_mode="email")
    html_pdf = build_report_html(md_text_clean, report_date_str, image_src=image_src_pdf, render_mode="pdf")
    html_pdf_fallback = build_report_html(md_text_clean, report_date_str, image_src=image_src_pdf, render_mode="pdf_fallback")

    if "EQUITY_CURVE_CHART_PLACEHOLDER" in md_text_clean and equity_curve_png.exists():
        if 'data:image/png;base64,' not in html_pdf and '<img src="' not in html_pdf:
            raise RuntimeError("Equity curve image was not embedded into PDF HTML.")

    if language == "en":
        validate_email_body(html_email, md_text_clean, mode=mode)
    else:
        validate_nl_email_body(html_email, md_text_clean)

    html_path = report_path.with_name(f"{safe_stem}_delivery.html")
    html_path.write_text(html_email, encoding="utf-8")

    pdf_path = report_path.with_name(f"{safe_stem}.pdf")
    create_pdf_from_html(html_pdf, pdf_path, fallback_html=html_pdf_fallback)
    if not pdf_path.exists() or pdf_path.stat().st_size <= 0:
        raise RuntimeError(f"PDF attachment was not created correctly: {pdf_path}")

    return {
        "report_date_str": report_date_str,
        "clean_md_path": clean_md_path,
        "equity_curve_png": equity_curve_png,
        "html_path": html_path,
        "pdf_path": pdf_path,
        "html_email": html_email,
        "safe_stem": safe_stem,
        "md_text_clean": md_text_clean,
        "language": language,
        "report_path": report_path,
    }


def generate_delivery_assets_for_run(output_dir: Path, report_path_en: Path, mode: str = "standard") -> dict:
    assets_en = generate_delivery_assets(output_dir, report_path_en, mode=mode, language="en")
    bundle = {"bilingual": False, "en": assets_en}
    if mode == "pro" and has_matching_dutch_report(report_path_en):
        validate_bilingual_pair(report_path_en)
        report_path_nl = matching_dutch_report_path(report_path_en)
        assets_nl = generate_delivery_assets(output_dir, report_path_nl, mode=mode, language="nl")
        bundle["bilingual"] = True
        bundle["nl"] = assets_nl
    return bundle


@contextmanager
def _temporary_env(overrides: dict[str, str | None]):
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _send_language_email(assets: dict, mode: str, subject_prefix: str, mail_to: str | None = None):
    overrides = {"MRKT_RPRTS_SUBJECT_PREFIX": subject_prefix}
    if mail_to:
        overrides["MRKT_RPRTS_MAIL_TO"] = mail_to
    with _temporary_env(overrides):
        return send_email_with_attachments(assets, mode=mode)


def main():
    output_dir = Path("output")
    mode = normalize_report_mode(os.environ.get("MRKT_RPRTS_REPORT_MODE", "standard"))
    latest_report = latest_report_file(output_dir, mode=mode)
    bundle = generate_delivery_assets_for_run(output_dir, latest_report, mode=mode)

    if bundle.get("bilingual"):
        subject_prefix_en = os.environ.get("MRKT_RPRTS_SUBJECT_PREFIX", "Weekly ETF Pro Review")
        subject_prefix_nl = os.environ.get("MRKT_RPRTS_SUBJECT_PREFIX_NL", NL_SUBJECT_PREFIX_FALLBACK)
        mail_to_default = os.environ.get("MRKT_RPRTS_MAIL_TO")
        mail_to_nl = os.environ.get("MRKT_RPRTS_MAIL_TO_NL") or mail_to_default

        attachments_en, manifest_path_en, mail_to_en = _send_language_email(bundle["en"], mode=mode, subject_prefix=subject_prefix_en, mail_to=mail_to_default)
        attachments_nl, manifest_path_nl, mail_to_nl_effective = _send_language_email(bundle["nl"], mode=mode, subject_prefix=subject_prefix_nl, mail_to=mail_to_nl)

        print(
            "DELIVERY_OK | mode=pro_bilingual | "
            f"report_en={bundle['en']['report_path'].name} | report_nl={bundle['nl']['report_path'].name} | "
            f"recipient_en={mail_to_en} | recipient_nl={mail_to_nl_effective} | "
            f"html_body_en=full_report | html_body_nl=full_report | "
            f"pdf_en=yes | pdf_nl=yes | manifest_en={manifest_path_en.name} | manifest_nl={manifest_path_nl.name} | "
            f"attachments_en={', '.join(attachments_en)} | attachments_nl={', '.join(attachments_nl)}"
        )
        return

    attachments, manifest_path, mail_to = send_email_with_attachments(bundle["en"], mode=mode)
    print(
        f"DELIVERY_OK | mode={mode} | report={latest_report.name} | recipient={mail_to} | "
        f"html_body=full_report | pdf_attached=yes | manifest={manifest_path.name} | "
        f"attachments={', '.join(attachments)}"
    )


if __name__ == "__main__":
    main()
