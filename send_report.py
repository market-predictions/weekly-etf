from __future__ import annotations

import re
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


# Re-export core API expected by workflows
normalize_report_mode = _base.normalize_report_mode
report_regex = _base.report_regex
report_sort_key = _base.report_sort_key
list_report_files = _base.list_report_files
latest_report_file = _base.latest_report_file
latest_reports_by_day = _base.latest_reports_by_day
require_env = _base.require_env
normalize_markdown_text = _base.normalize_markdown_text
strip_citations = _base.strip_citations
clean_md_inline = _base.clean_md_inline
html_to_plain_text = _base.html_to_plain_text
plain_text_from_markdown = _base.plain_text_from_markdown
esc = _base.esc
is_markdown_table_line = _base.is_markdown_table_line
is_markdown_separator_line = _base.is_markdown_separator_line
parse_markdown_table = _base.parse_markdown_table
pretty_section_title = _base.pretty_section_title
heading_text_from_md_heading = _base.heading_text_from_md_heading
tradingview_url = _base.tradingview_url
is_probable_ticker = _base.is_probable_ticker
ticker_anchor_html = _base.ticker_anchor_html
maybe_link_ticker_text_html = _base.maybe_link_ticker_text_html
maybe_link_ticker_csv_html = _base.maybe_link_ticker_csv_html
linkify_ticker_headings = _base.linkify_ticker_headings
linkify_ticker_tables = _base.linkify_ticker_tables
add_tradingview_targets = _base.add_tradingview_targets
linkify_position_card_title = _base.linkify_position_card_title
parse_report_date = _base.parse_report_date
format_full_date = _base.format_full_date
extract_section = _base.extract_section
extract_label_pairs = _base.extract_label_pairs
parse_numeric_value = _base.parse_numeric_value
parse_section15_totals = _base.parse_section15_totals
extract_sections = _base.extract_sections
validate_required_report = _base.validate_required_report
validate_email_body = _base.validate_email_body
write_delivery_manifest = _base.write_delivery_manifest
normalize_subheader = _base.normalize_subheader
preprocess_markdown_block = _base.preprocess_markdown_block
render_markdown_block = _base.render_markdown_block
section_header_html = _base.section_header_html
section_number = _base.section_number
with_display_number = _base.with_display_number
parse_subsections = _base.parse_subsections
split_h3_blocks = _base.split_h3_blocks
render_executive_summary = _base.render_executive_summary
render_action_snapshot = _base.render_action_snapshot
render_standard_panel = _base.render_standard_panel
render_position_review = _base.render_position_review
render_carry_panel = _base.render_carry_panel
render_best_opportunities = _base.render_best_opportunities
render_rotation_plan = _base.render_rotation_plan
build_report_html = _base.build_report_html
create_pdf_from_html = _base.create_pdf_from_html
send_email_with_attachments = _base.send_email_with_attachments

MARKDOWN = _base.MARKDOWN
BRAND = _base.BRAND
DISCLAIMER_LINE = _base.DISCLAIMER_LINE
REQUIRED_MAIL_TO = _base.REQUIRED_MAIL_TO


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
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _norm_header(value: str) -> str:
    return re.sub(r"\s+", " ", clean_md_inline(value).strip().lower())


def parse_section15_holdings_rows(md_text: str) -> list[dict[str, str]]:
    lines = extract_section(md_text, "Current portfolio holdings and cash")
    if not lines:
        return []
    block = _first_markdown_table(lines)
    if not block:
        return []
    rows = parse_markdown_table(block)
    if len(rows) < 2:
        return []
    headers = [_norm_header(h) for h in rows[0]]
    result = []
    for row in rows[1:]:
        padded = row + [""] * (len(headers) - len(row))
        result.append({headers[idx]: padded[idx] for idx in range(len(headers))})
    return result


def parse_section7_equity_points(md_text: str) -> list[tuple[str, float]]:
    lines = extract_section(md_text, "Equity curve and portfolio development")
    if not lines:
        return []
    block = _first_markdown_table(lines)
    if not block:
        return []
    rows = parse_markdown_table(block)
    if len(rows) < 2:
        return []
    headers = [_norm_header(h) for h in rows[0]]
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


def validate_section15_arithmetic(md_text: str, tolerance: float = 0.05) -> dict[str, float]:
    totals = parse_section15_totals(md_text)
    rows = parse_section15_holdings_rows(md_text)
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

    invested_label = totals.get("Invested market value (EUR)")
    cash_label = totals.get("Cash (EUR)")
    total_label = totals.get("Total portfolio value (EUR)")

    if invested_label is None or cash_label is None or total_label is None:
        raise RuntimeError("Section 15 summary labels are incomplete; cannot validate valuation arithmetic.")

    if abs(invested_sum - invested_label) > tolerance:
        raise RuntimeError(
            f"Section 15 arithmetic mismatch: invested market value label={invested_label:.2f} but table sums to {invested_sum:.2f}."
        )
    if abs(cash_sum - cash_label) > tolerance:
        raise RuntimeError(
            f"Section 15 arithmetic mismatch: cash label={cash_label:.2f} but CASH row sums to {cash_sum:.2f}."
        )
    if abs(total_sum - total_label) > tolerance:
        raise RuntimeError(
            f"Section 15 arithmetic mismatch: total portfolio value label={total_label:.2f} but table sums to {total_sum:.2f}."
        )

    return {
        "invested_market_value_eur": invested_sum,
        "cash_eur": cash_sum,
        "total_portfolio_value_eur": total_sum,
    }


def validate_equity_curve_alignment(md_text: str, tolerance: float = 0.05) -> None:
    points = parse_section7_equity_points(md_text)
    totals = parse_section15_totals(md_text)
    total_label = totals.get("Total portfolio value (EUR)")
    if not points or total_label is None:
        return
    latest_nav = points[-1][1]
    if abs(latest_nav - total_label) > tolerance:
        raise RuntimeError(
            f"Equity curve mismatch: latest section 7 table value={latest_nav:.2f} but section 15 total portfolio value={total_label:.2f}."
        )


def create_equity_curve_png(output_dir: Path, chart_path: Path, mode: str = "standard", md_text: str | None = None):
    points: list[tuple[str, float]] = []

    if md_text:
        points = parse_section7_equity_points(md_text)

    if not points:
        for report_path in latest_reports_by_day(output_dir, mode=mode):
            hist_md = report_path.read_text(encoding="utf-8")
            report_date = parse_report_date(hist_md)
            totals = parse_section15_totals(hist_md)
            nav = totals.get("Total portfolio value (EUR)")
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


def generate_delivery_assets(output_dir: Path, report_path: Path, mode: str = "standard"):
    original_md_text = normalize_markdown_text(report_path.read_text(encoding="utf-8"))
    md_text_clean = strip_citations(original_md_text)
    validate_required_report(md_text_clean, mode=mode)
    validate_section15_arithmetic(md_text_clean)
    validate_equity_curve_alignment(md_text_clean)

    report_date_str = parse_report_date(md_text_clean)
    safe_stem = report_path.stem

    clean_md_path = report_path.with_name(f"{safe_stem}_clean.md")
    clean_md_path.write_text(md_text_clean, encoding="utf-8")

    equity_curve_png = report_path.with_name(f"{safe_stem}_equity_curve.png")
    create_equity_curve_png(output_dir, equity_curve_png, mode=mode, md_text=md_text_clean)

    image_src_pdf = equity_curve_png.resolve().as_uri() if equity_curve_png.exists() else None
    image_src_email = "cid:equitycurve" if equity_curve_png.exists() else None

    html_email = build_report_html(md_text_clean, report_date_str, image_src=image_src_email, render_mode="email")
    html_pdf = build_report_html(md_text_clean, report_date_str, image_src=image_src_pdf, render_mode="pdf")
    html_pdf_fallback = build_report_html(md_text_clean, report_date_str, image_src=image_src_pdf, render_mode="pdf_fallback")

    validate_email_body(html_email, md_text_clean, mode=mode)

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
    }


def main():
    output_dir = Path("output")
    mode = normalize_report_mode(__import__("os").environ.get("MRKT_RPRTS_REPORT_MODE", "standard"))
    latest_report = latest_report_file(output_dir, mode=mode)
    assets = generate_delivery_assets(output_dir, latest_report, mode=mode)
    attachments, manifest_path, mail_to = send_email_with_attachments(assets, mode=mode)

    receipt = (
        f"DELIVERY_OK | mode={mode} | report={latest_report.name} | recipient={mail_to} | "
        f"html_body=full_report | pdf_attached=yes | manifest={manifest_path.name} | "
        f"attachments={', '.join(attachments)}"
    )
    print(receipt)


if __name__ == "__main__":
    main()
