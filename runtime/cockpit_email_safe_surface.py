from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Iterable

from runtime import render_cockpit_front_page as cockpit

FRONT_PAGE_MARKER = 'data-cockpit-front-page="delivery"'


def _attr(value: str) -> str:
    return escape(value, quote=True)


def _style(**items: str) -> str:
    return ";".join(f"{key.replace('_', '-')}:{value}" for key, value in items.items() if value)


def _sparkline_text(points: Iterable[tuple[str, float]]) -> str:
    point_list = list(points)
    values = [float(value) for _, value in point_list]
    if not values:
        return "—"
    if len(values) > 44:
        step = max(1, len(values) // 44)
        values = values[::step]
        final_value = float(point_list[-1][1])
        if values[-1] != final_value:
            values.append(final_value)
    low = min(values)
    high = max(values)
    bars = "▁▂▃▄▅▆▇█"
    if high <= low:
        return bars[3] * len(values)
    return "".join(bars[min(len(bars) - 1, max(0, round((value - low) / (high - low) * (len(bars) - 1))))] for value in values)


def _evidence_rows(
    *,
    output_dir: Path,
    state_path: Path,
    macro_path: Path,
    language: str,
) -> tuple[str, str, list[tuple[str, str]]]:
    pricing_path = cockpit._optional_pointer_target(output_dir, cockpit.PRICING_AUDIT_POINTER)
    run_manifest_path = cockpit._optional_pointer_target(output_dir, cockpit.RUN_MANIFEST_POINTER)
    valuation_path = output_dir / "etf_valuation_history.csv"
    if language == "nl":
        return (
            "Bronnen en controle",
            "De voorpagina is opgebouwd uit de actuele portefeuillestatus. De volledige analyse en onderliggende tabellen volgen hierna.",
            [
                ("Portefeuillestatus", "actuele uitvoerautoriteit" if state_path.exists() else "niet beschikbaar"),
                ("Waarderingshistorie", "gereconcilieerd" if valuation_path.exists() else "niet beschikbaar"),
                ("Prijscontrole", "gekoppeld" if pricing_path and pricing_path.exists() else "niet beschikbaar"),
                ("Macrobeeld", "gekoppeld" if macro_path.exists() else "niet beschikbaar"),
                ("Uitvoerregistratie", "gekoppeld" if run_manifest_path and run_manifest_path.exists() else "niet beschikbaar"),
                ("Volledig rapport", "volgt direct na deze voorpagina"),
            ],
        )
    return (
        "Sources & controls",
        "This front page is built from the current portfolio state. The complete analysis and underlying tables follow below.",
        [
            ("Portfolio state", "current runtime authority" if state_path.exists() else "not available"),
            ("Valuation history", "reconciled" if valuation_path.exists() else "not available"),
            ("Pricing control", "linked" if pricing_path and pricing_path.exists() else "not available"),
            ("Macro view", "linked" if macro_path.exists() else "not available"),
            ("Run record", "linked" if run_manifest_path and run_manifest_path.exists() else "not available"),
            ("Complete report", "follows immediately after this front page"),
        ],
    )


def _section_title(title: str) -> str:
    return (
        f'<div class="etf-cockpit-section-title" style="{_attr(_style(margin="24px 0 10px 0", color="#0F4438", font_family="Courier New,monospace", font_size="11px", font_weight="700", letter_spacing="2px", text_transform="uppercase", border_bottom="1px solid #D8CDB8", padding_bottom="7px"))}">'
        f"{escape(title)}</div>"
    )


def _metric_cell(label: str, value: str, sub: str, *, value_color: str = "#211C16") -> str:
    cell_style = _style(width="33.333%", vertical_align="top", padding="13px 14px", border="1px solid #D8CDB8", background_color="#FFFFFF")
    label_style = _style(font_family="Courier New,monospace", font_size="9px", font_weight="700", letter_spacing="1px", text_transform="uppercase", color="#5A5043")
    value_style = _style(font_family="Georgia,Times New Roman,serif", font_size="23px", font_weight="700", line_height="1.1", color=value_color, padding_top="7px")
    sub_style = _style(font_family="Courier New,monospace", font_size="10px", line_height="1.35", color="#5A5043", padding_top="5px")
    return (
        f'<td class="etf-cockpit-metric" style="{_attr(cell_style)}">'
        f'<div class="etf-cockpit-metric-label" style="{_attr(label_style)}">{escape(label)}</div>'
        f'<div class="etf-cockpit-metric-value" style="{_attr(value_style)}">{escape(value)}</div>'
        f'<div class="etf-cockpit-metric-sub" style="{_attr(sub_style)}">{escape(sub)}</div>'
        "</td>"
    )


def render_email_safe_cockpit_front_page(
    *,
    output_dir: Path,
    state_path: Path,
    macro_path: Path,
    language: str,
    report_date: str,
    text: dict[str, str],
    summary: str,
    regime: str,
    confidence: int,
    action_title: str,
    action_note: str,
    points: list[tuple[str, float]],
    nav: float,
    since: float,
    drawdown: float,
    cash: float,
    cash_pct: float,
    position_count: int,
    largest_ticker: str,
    largest_weight: float,
    fx_rate: float,
    discipline: str,
    next_trigger: str,
) -> str:
    evidence_title, evidence_intro, evidence_rows = _evidence_rows(
        output_dir=output_dir,
        state_path=state_path,
        macro_path=macro_path,
        language=language,
    )

    outer_style = _style(max_width="780px", margin="0 auto 28px auto", background_color="#F6F1E7", color="#211C16", border="1px solid #D8CDB8", font_family="Arial,Helvetica,sans-serif")
    shell_style = _style(width="100%", border_collapse="collapse", border_spacing="0")
    inner_style = _style(padding="30px 36px 28px 36px")
    kicker_style = _style(font_family="Courier New,monospace", font_size="10px", font_weight="700", letter_spacing="2px", text_transform="uppercase", color="#B07D2B", padding_bottom="7px")
    mast_style = _style(font_family="Georgia,Times New Roman,serif", font_size="38px", font_weight="700", line_height="1.05", color="#211C16")
    issue_style = _style(text_align="right", vertical_align="top", font_family="Courier New,monospace", font_size="10px", line_height="1.65", color="#5A5043", padding_left="20px")
    strap_style = _style(font_family="Courier New,monospace", font_size="10px", font_weight="700", letter_spacing="1px", text_transform="uppercase", color="#5A5043", border_top="2px solid #211C16", padding_top="10px")
    lede_style = _style(font_family="Georgia,Times New Roman,serif", font_size="19px", line_height="1.5", color="#211C16", margin="0")
    card_style = _style(width="50%", vertical_align="top", border="1px solid #D8CDB8", background_color="#EFE8D9", padding="15px 17px")
    label_style = _style(font_family="Courier New,monospace", font_size="9px", font_weight="700", letter_spacing="1px", text_transform="uppercase", color="#5A5043", padding_bottom="8px")
    card_value_style = _style(font_family="Georgia,Times New Roman,serif", font_size="19px", font_weight="700", line_height="1.25", color="#211C16")
    note_style = _style(font_size="12px", line_height="1.45", color="#5A5043", padding_top="8px")
    performance_style = _style(border="1px solid #D8CDB8", background_color="#FFFFFF", padding="16px")
    caption_style = _style(font_family="Courier New,monospace", font_size="10px", font_weight="700", letter_spacing="1px", text_transform="uppercase", color="#5A5043")
    spark_style = _style(font_family="Courier New,monospace", font_size="20px", letter_spacing="1px", line_height="1.2", color="#0F4438", white_space="nowrap", overflow="hidden", padding="12px 0 5px 0")
    discipline_style = _style(border_left="4px solid #B07D2B", background_color="#F0E5D0", padding="13px 15px", font_size="13px", line_height="1.5", color="#211C16")
    trigger_style = _style(margin_top="9px", border="1px solid #D8CDB8", background_color="#FFFFFF", padding="12px 14px", font_size="12px", line_height="1.5", color="#5A5043")
    evidence_style = _style(border="1px solid #D8CDB8", background_color="#FFFFFF", padding="13px 15px")
    evidence_intro_style = _style(margin="0 0 10px 0", color="#5A5043", font_size="12px", line_height="1.45")
    footer_style = _style(border_top="1px solid #D8CDB8", padding_top="12px", font_family="Courier New,monospace", font_size="10px", color="#5A5043")

    confidence_width = max(0, min(int(confidence), 100))
    confidence_bar = (
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;border-collapse:collapse;margin-top:10px">'
        '<tr><td style="background:#E2D9C6;height:6px;line-height:6px;font-size:1px">'
        f'<div style="width:{confidence_width}%;height:6px;line-height:6px;background:#0F4438;font-size:1px">&nbsp;</div>'
        '</td><td style="width:92px;padding-left:9px;font-size:11px;color:#5A5043;white-space:nowrap">'
        f'{confidence_width}% {escape(text["confidence"])}</td></tr></table>'
    )

    evidence_cells: list[str] = []
    for label, value in evidence_rows:
        evidence_cells.append(
            '<td class="etf-cockpit-evidence-item" style="width:50%;vertical-align:top;border-top:1px solid #D8CDB8;padding:8px 10px 7px 0">'
            f'<div class="etf-cockpit-evidence-label" style="font-family:Courier New,monospace;font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#5A5043">{escape(label)}</div>'
            f'<div class="etf-cockpit-evidence-value" style="font-family:Courier New,monospace;font-size:10px;line-height:1.35;color:#211C16;padding-top:4px">{escape(value)}</div>'
            '</td>'
        )
    empty_evidence_cell = '<td style="width:50%"></td>'
    evidence_rows_html = "".join(
        "<tr>"
        + evidence_cells[index]
        + (evidence_cells[index + 1] if index + 1 < len(evidence_cells) else empty_evidence_cell)
        + "</tr>"
        for index in range(0, len(evidence_cells), 2)
    )

    return_color = "#2F7A57" if since >= 0 else "#A8452C"
    drawdown_color = "#A8452C" if drawdown < 0 else "#211C16"
    sparkline = _sparkline_text(points)

    return f'''<section class="etf-cockpit-page" {FRONT_PAGE_MARKER} data-cockpit-language="{_attr(language)}" data-render-mode="email" style="{_attr(outer_style)}">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="{_attr(shell_style)}"><tr><td class="etf-cockpit-inner" style="{_attr(inner_style)}">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" class="etf-cockpit-header" style="width:100%;border-collapse:collapse"><tr><td style="vertical-align:top"><div class="etf-cockpit-kicker" style="{_attr(kicker_style)}">{escape(text['kicker'])}</div><div class="etf-cockpit-mast" style="{_attr(mast_style)}">{escape(text['title'])}</div></td><td class="etf-cockpit-issue" style="{_attr(issue_style)}">{escape(text['model'])}<br>{escape(cockpit._fmt_date(report_date, language))}<br><strong>{escape(text['issue'])}</strong></td></tr></table>
<div class="etf-cockpit-strap" style="{_attr(strap_style)}">{escape(text['frequency'])} &nbsp;·&nbsp; US ETF &nbsp;·&nbsp; {escape(text['strap'])}</div>
{_section_title(text['short'])}<p class="etf-cockpit-lede" style="{_attr(lede_style)}">{summary}</p>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" class="etf-cockpit-row" style="width:100%;border-collapse:separate;border-spacing:10px 0;margin-top:20px"><tr><td class="etf-cockpit-card" style="{_attr(card_style)}"><div class="etf-cockpit-label" style="{_attr(label_style)}">{escape(text['climate'])}</div><div class="etf-cockpit-value" style="{_attr(card_value_style)}">{escape(regime)}</div>{confidence_bar}</td><td class="etf-cockpit-card" style="{_attr(card_style)}"><div class="etf-cockpit-label" style="{_attr(label_style)}">{escape(text['action'])}</div><div class="etf-cockpit-value" style="{_attr(card_value_style)}">{escape(action_title)}</div><div class="etf-cockpit-note" style="{_attr(note_style)}">{escape(action_note)}</div></td></tr></table>
{_section_title(text['performance'])}<div class="etf-cockpit-performance" style="{_attr(performance_style)}"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;border-collapse:collapse"><tr><td class="etf-cockpit-chart-title" style="{_attr(caption_style)}">{escape(text['nav'])} · EUR</td><td style="text-align:right;font-size:13px;color:#211C16">{escape(cockpit._fmt_eur(nav, language))} · <strong>{escape(cockpit._fmt_pct(since, language, signed=True))}</strong></td></tr></table><div class="etf-cockpit-email-sparkline" aria-label="portfolio trend" style="{_attr(spark_style)}">{sparkline}</div><table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" class="etf-cockpit-metrics" style="width:100%;border-collapse:collapse"><tr>{_metric_cell(text['return'], cockpit._fmt_pct(since, language, signed=True), f"{cockpit._fmt_eur(points[0][1], language)} → {cockpit._fmt_eur(nav, language)}", value_color=return_color)}{_metric_cell(text['drawdown'], cockpit._fmt_pct(drawdown, language), text['since'], value_color=drawdown_color)}{_metric_cell(text['cash'], cockpit._fmt_pct(cash_pct, language), cockpit._fmt_eur(cash, language))}</tr><tr>{_metric_cell(text['positions'], str(position_count), text['holdings'])}{_metric_cell(text['largest'], largest_ticker, cockpit._fmt_pct(largest_weight, language))}{_metric_cell('EUR/USD', f'{fx_rate:.4f}', text['pricing'])}</tr></table></div>
{_section_title(text['discipline'])}<div class="etf-cockpit-discipline" style="{_attr(discipline_style)}">{escape(discipline)}</div><div class="etf-cockpit-trigger" data-next-action-trigger="true" style="{_attr(trigger_style)}">{escape(next_trigger)}</div>
{_section_title(evidence_title)}<div class="etf-cockpit-evidence" data-source-evidence="true" style="{_attr(evidence_style)}"><p class="etf-cockpit-evidence-intro" style="{_attr(evidence_intro_style)}">{escape(evidence_intro)}</p><table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" class="etf-cockpit-evidence-grid" style="width:100%;border-collapse:collapse">{evidence_rows_html}</table></div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" class="etf-cockpit-footer" style="width:100%;border-collapse:collapse;margin-top:18px"><tr><td style="{_attr(footer_style)}">{escape(text['footer'])}</td><td style="{_attr(footer_style)};text-align:right">01</td></tr></table>
</td></tr></table></section>'''
