from __future__ import annotations

import os
import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Callable

from runtime import render_cockpit_front_page as cockpit

FEATURE_FLAG = "MRKT_RPRTS_COCKPIT_FRONT_PAGE"
VALID_FEATURE_VALUES = frozenset({"disabled", "enabled"})
STYLE_ID = "etf-cockpit-delivery-front-page-style"
FRONT_PAGE_MARKER = 'data-cockpit-front-page="delivery"'


@dataclass(frozen=True)
class CockpitFrontPageFragment:
    css: str
    html: str
    language: str


@dataclass(frozen=True)
class CockpitFrontPageInjectionResult:
    html: str
    status: str
    diagnostic: str
    feature_value: str
    front_page_count: int


def parse_feature_value(raw_value: str | None = None) -> str:
    raw = os.environ.get(FEATURE_FLAG, "disabled") if raw_value is None else raw_value
    value = str(raw).strip().lower()
    if value not in VALID_FEATURE_VALUES:
        raise ValueError(
            f"{FEATURE_FLAG} must be exactly 'disabled' or 'enabled'; received {raw!r}"
        )
    return value


def _delivery_evidence_html(
    *,
    output_dir: Path,
    state_path: Path,
    macro_path: Path,
    language: str,
) -> str:
    pricing_path = cockpit._optional_pointer_target(output_dir, cockpit.PRICING_AUDIT_POINTER)
    run_manifest_path = cockpit._optional_pointer_target(output_dir, cockpit.RUN_MANIFEST_POINTER)
    valuation_path = output_dir / "etf_valuation_history.csv"

    if language == "nl":
        title = "Bronnen en controle"
        intro = "De voorpagina is opgebouwd uit de actuele portefeuillestatus. De volledige analyse en onderliggende tabellen volgen hierna."
        rows = [
            ("Portefeuillestatus", "actuele uitvoerautoriteit" if state_path.exists() else "niet beschikbaar"),
            ("Waarderingshistorie", "gereconcilieerd" if valuation_path.exists() else "niet beschikbaar"),
            ("Prijscontrole", "gekoppeld" if pricing_path and pricing_path.exists() else "niet beschikbaar"),
            ("Macrobeeld", "gekoppeld" if macro_path.exists() else "niet beschikbaar"),
            ("Uitvoerregistratie", "gekoppeld" if run_manifest_path and run_manifest_path.exists() else "niet beschikbaar"),
            ("Volledig rapport", "volgt direct na deze voorpagina"),
        ]
    else:
        title = "Sources & controls"
        intro = "This front page is built from the current portfolio state. The complete analysis and underlying tables follow below."
        rows = [
            ("Portfolio state", "current runtime authority" if state_path.exists() else "not available"),
            ("Valuation history", "reconciled" if valuation_path.exists() else "not available"),
            ("Pricing control", "linked" if pricing_path and pricing_path.exists() else "not available"),
            ("Macro view", "linked" if macro_path.exists() else "not available"),
            ("Run record", "linked" if run_manifest_path and run_manifest_path.exists() else "not available"),
            ("Complete report", "follows immediately after this front page"),
        ]

    row_html = "".join(
        "<div class='etf-cockpit-evidence-item'>"
        f"<div class='etf-cockpit-evidence-label'>{escape(label)}</div>"
        f"<div class='etf-cockpit-evidence-value'>{escape(value)}</div>"
        "</div>"
        for label, value in rows
    )
    return (
        f"<div class='etf-cockpit-section-title'>{escape(title)}</div>"
        "<div class='etf-cockpit-evidence' data-source-evidence='true'>"
        f"<p class='etf-cockpit-evidence-intro'>{escape(intro)}</p>"
        f"<div class='etf-cockpit-evidence-grid'>{row_html}</div>"
        "</div>"
    )


def _delivery_css() -> str:
    return f"""<style id=\"{STYLE_ID}\">
.etf-cockpit-page{{max-width:780px;margin:0 auto 28px;background:#F6F1E7;color:#211C16;border:1px solid #D8CDB8;font-family:Arial,Helvetica,sans-serif;box-sizing:border-box}}
.etf-cockpit-page *{{box-sizing:border-box}}
.etf-cockpit-inner{{padding:34px 42px 28px}}
.etf-cockpit-header{{display:flex;justify-content:space-between;gap:20px;border-bottom:2px solid #211C16;padding-bottom:14px}}
.etf-cockpit-kicker,.etf-cockpit-issue,.etf-cockpit-strap,.etf-cockpit-section-title,.etf-cockpit-label,.etf-cockpit-metric-label,.etf-cockpit-metric-sub,.etf-cockpit-footer,.etf-cockpit-evidence-label,.etf-cockpit-evidence-value{{font-family:'Courier New',monospace}}
.etf-cockpit-kicker{{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#B07D2B}}
.etf-cockpit-mast{{font-family:Georgia,'Times New Roman',serif;font-size:40px;font-weight:700;line-height:1;margin-top:8px;letter-spacing:-.02em}}
.etf-cockpit-mast em{{color:#0F4438;font-style:italic;font-weight:400}}
.etf-cockpit-issue{{text-align:right;font-size:10.5px;line-height:1.65;color:#5A5043}}
.etf-cockpit-strap{{margin-top:12px;display:flex;gap:12px;align-items:center;font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:#5A5043}}
.etf-cockpit-dot{{width:5px;height:5px;border-radius:50%;background:#B07D2B;display:inline-block}}
.etf-cockpit-section-title{{margin:28px 0 12px;color:#0F4438;font-size:11px;letter-spacing:.19em;text-transform:uppercase;display:flex;align-items:center;gap:12px}}
.etf-cockpit-section-title:after{{content:'';height:1px;background:#D8CDB8;flex:1}}
.etf-cockpit-lede{{font-family:Georgia,'Times New Roman',serif;font-size:20px;line-height:1.48;margin:0}}
.etf-cockpit-row{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:24px}}
.etf-cockpit-card{{border:1px solid #D8CDB8;background:#EFE8D9;padding:16px 18px}}
.etf-cockpit-label{{font-size:9.5px;letter-spacing:.17em;text-transform:uppercase;color:#5A5043;margin-bottom:9px}}
.etf-cockpit-value{{font-family:Georgia,'Times New Roman',serif;font-size:20px;font-weight:600;line-height:1.25}}
.etf-cockpit-note{{font-size:12px;color:#5A5043;line-height:1.45;margin-top:9px}}
.etf-cockpit-confidence{{display:flex;align-items:center;gap:9px;margin-top:12px}}
.etf-cockpit-bar{{flex:1;height:6px;background:#E2D9C6;border-radius:4px;overflow:hidden}}
.etf-cockpit-bar i{{display:block;height:100%;background:#0F4438}}
.etf-cockpit-performance{{border:1px solid #D8CDB8;background:#fff}}
.etf-cockpit-chart{{padding:18px 18px 6px}}
.etf-cockpit-chart-caption{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-bottom:6px}}
.etf-cockpit-chart-title{{font-family:'Courier New',monospace;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5A5043}}
.etf-cockpit-page svg.spark{{width:100%;height:120px;display:block}}
.etf-cockpit-metrics{{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid #D8CDB8}}
.etf-cockpit-metric{{padding:15px 16px;border-right:1px solid #D8CDB8;border-top:1px solid #D8CDB8}}
.etf-cockpit-metric:nth-child(3n){{border-right:none}}
.etf-cockpit-metric:nth-child(-n+3){{border-top:none}}
.etf-cockpit-metric-label{{font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#5A5043}}
.etf-cockpit-metric-value{{font-family:Georgia,'Times New Roman',serif;font-size:24px;font-weight:600;margin-top:7px;line-height:1}}
.etf-cockpit-positive{{color:#2F7A57}}
.etf-cockpit-negative{{color:#A8452C}}
.etf-cockpit-metric-sub{{font-size:10.5px;color:#5A5043;margin-top:5px}}
.etf-cockpit-discipline{{border-left:4px solid #B07D2B;background:rgba(176,125,43,.10);padding:14px 16px;font-size:13px;line-height:1.5}}
.etf-cockpit-trigger{{margin-top:10px;border:1px solid #D8CDB8;background:#fff;padding:13px 15px;font-size:12.5px;line-height:1.5;color:#5A5043}}
.etf-cockpit-evidence{{border:1px solid #D8CDB8;background:#fff;padding:14px 16px}}
.etf-cockpit-evidence-intro{{margin:0 0 12px;color:#5A5043;font-size:12px;line-height:1.45}}
.etf-cockpit-evidence-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px 14px}}
.etf-cockpit-evidence-item{{border-top:1px solid #D8CDB8;padding-top:8px}}
.etf-cockpit-evidence-label{{font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#5A5043}}
.etf-cockpit-evidence-value{{margin-top:4px;font-size:10px;color:#211C16;overflow-wrap:anywhere}}
.etf-cockpit-footer{{margin-top:22px;padding-top:13px;border-top:1px solid #D8CDB8;display:flex;justify-content:space-between;gap:12px;color:#5A5043;font-size:10px}}
@media print{{
.etf-cockpit-page{{page-break-after:always;break-after:page;border:none;margin:0;max-width:none;font-size:9px;break-inside:avoid;page-break-inside:avoid}}
.etf-cockpit-inner{{padding:14px 22px 12px}}
.etf-cockpit-header{{gap:12px;padding-bottom:7px}}
.etf-cockpit-kicker{{font-size:8px}}
.etf-cockpit-mast{{font-size:28px;margin-top:4px}}
.etf-cockpit-issue{{font-size:8.5px;line-height:1.35}}
.etf-cockpit-strap{{margin-top:5px;gap:7px;font-size:8px}}
.etf-cockpit-section-title{{margin:10px 0 5px;font-size:8.5px;gap:8px}}
.etf-cockpit-lede{{font-size:14px;line-height:1.28}}
.etf-cockpit-row{{gap:8px;margin-top:8px}}
.etf-cockpit-card{{padding:8px 10px}}
.etf-cockpit-label{{font-size:7.5px;margin-bottom:4px}}
.etf-cockpit-value{{font-size:14.5px;line-height:1.1}}
.etf-cockpit-note{{font-size:9px;line-height:1.25;margin-top:4px}}
.etf-cockpit-confidence{{gap:5px;margin-top:5px;font-size:8px}}
.etf-cockpit-bar{{height:4px}}
.etf-cockpit-chart{{padding:8px 10px 2px}}
.etf-cockpit-chart-caption{{gap:8px;margin-bottom:3px;font-size:9px}}
.etf-cockpit-chart-title{{font-size:7.5px}}
.etf-cockpit-page svg.spark{{height:58px}}
.etf-cockpit-metric{{padding:6px 8px}}
.etf-cockpit-metric-label{{font-size:7px}}
.etf-cockpit-metric-value{{font-size:16px;margin-top:3px}}
.etf-cockpit-metric-sub{{font-size:8px;margin-top:2px}}
.etf-cockpit-discipline{{padding:7px 9px;font-size:9px;line-height:1.25}}
.etf-cockpit-trigger{{margin-top:4px;padding:6px 8px;font-size:8.5px;line-height:1.25}}
.etf-cockpit-evidence{{padding:6px 8px}}
.etf-cockpit-evidence-intro{{margin:0 0 4px;font-size:8px;line-height:1.2}}
.etf-cockpit-evidence-grid{{grid-template-columns:repeat(3,1fr);gap:3px 8px}}
.etf-cockpit-evidence-item{{padding-top:3px}}
.etf-cockpit-evidence-label{{font-size:6.5px}}
.etf-cockpit-evidence-value{{margin-top:1px;font-size:7.5px}}
.etf-cockpit-footer{{margin-top:6px;padding-top:4px;font-size:7.5px}}
}}
@media (max-width:640px){{.etf-cockpit-inner{{padding:24px 20px}}.etf-cockpit-header{{display:block}}.etf-cockpit-issue{{text-align:left;margin-top:14px}}.etf-cockpit-row,.etf-cockpit-evidence-grid{{grid-template-columns:1fr}}.etf-cockpit-metrics{{grid-template-columns:1fr 1fr}}.etf-cockpit-metric:nth-child(3n){{border-right:1px solid #D8CDB8}}.etf-cockpit-metric:nth-child(2n){{border-right:none}}}}
</style>"""


def render_delivery_cockpit_front_page_fragment(
    *,
    output_dir: Path,
    language: str,
    render_mode: str = "email",
    runtime_state: str | None = None,
) -> CockpitFrontPageFragment:
    if language not in {"en", "nl"}:
        raise ValueError(f"Unsupported cockpit language: {language}")

    state_path = cockpit._resolve_runtime_state_path(output_dir, runtime_state)
    state = cockpit._load_json(state_path)
    macro_path = cockpit._macro_pack_path(output_dir, state)
    macro = cockpit._load_macro_pack(output_dir, state)
    points = cockpit._read_valuation_history(output_dir, state)

    is_nl = language == "nl"
    nav = cockpit._total_nav(state)
    cash = cockpit._cash_eur(state)
    cash_pct = (cash / nav * 100.0) if nav else 0.0
    since = cockpit._since_start_pct(points, nav)
    drawdown = cockpit._max_drawdown_pct(points)
    largest_ticker, largest_weight = cockpit._largest_position(state)
    regime, confidence = cockpit._macro_surface(macro)
    action_title, action_note = cockpit._action_surface(state, language)
    report_date = str(state.get("report_date") or state.get("requested_close_date") or "")
    summary = cockpit._plain_summary(state, macro, points, language)
    discipline = cockpit._discipline_surface(state, language)
    next_trigger = cockpit._next_action_trigger(state, language)
    evidence = _delivery_evidence_html(
        output_dir=output_dir,
        state_path=state_path,
        macro_path=macro_path,
        language=language,
    )

    text = {
        "title": "De ETF-Review" if is_nl else "The ETF Review",
        "kicker": "Beleggersrapport · US ETF-strategie" if is_nl else "Investor report · US ETF strategy",
        "frequency": "Wekelijks" if is_nl else "Weekly",
        "model": "Modelportefeuille · EUR" if is_nl else "Model portfolio · EUR",
        "issue": "Rapportvoorpagina" if is_nl else "Report front page",
        "strap": "Clientcockpit · geen beleggingsadvies" if is_nl else "Client cockpit · not investment advice",
        "short": "In het kort" if is_nl else "In brief",
        "climate": "Marktklimaat" if is_nl else "Market climate",
        "confidence": "vertrouwen" if is_nl else "confidence",
        "action": "Actie deze week" if is_nl else "This week's action",
        "performance": "Prestatie & risico" if is_nl else "Performance & risk",
        "nav": "Portefeuillewaarde" if is_nl else "Portfolio value",
        "return": "Rendement sinds start" if is_nl else "Return since inception",
        "drawdown": "Grootste terugval" if is_nl else "Max drawdown",
        "cash": "Cash",
        "positions": "Posities" if is_nl else "Positions",
        "largest": "Grootste positie" if is_nl else "Largest position",
        "discipline": "Disciplinepunt" if is_nl else "Discipline point",
        "since": "sinds start" if is_nl else "since inception",
        "holdings": "actieve posities" if is_nl else "active holdings",
        "pricing": "prijsbasis" if is_nl else "pricing basis",
        "footer": "Volledige analyse en bewijslaag volgen hierna." if is_nl else "Complete analysis and evidence layer follow below.",
    }

    return_class = "etf-cockpit-positive" if since >= 0 else "etf-cockpit-negative"
    drawdown_class = "etf-cockpit-negative" if drawdown < 0 else ""
    html = f"""<section class="etf-cockpit-page" {FRONT_PAGE_MARKER} data-cockpit-language="{language}" data-render-mode="{escape(render_mode)}">
<div class="etf-cockpit-inner">
<header class="etf-cockpit-header"><div><div class="etf-cockpit-kicker">{escape(text['kicker'])}</div><div class="etf-cockpit-mast">{escape(text['title']).replace('ETF', '<em>ETF</em>')}</div></div><div class="etf-cockpit-issue">{escape(text['model'])}<br>{escape(cockpit._fmt_date(report_date, language))}<br><b>{escape(text['issue'])}</b></div></header>
<div class="etf-cockpit-strap"><span>{escape(text['frequency'])}</span><span class="etf-cockpit-dot"></span><span>US ETF</span><span class="etf-cockpit-dot"></span><span>{escape(text['strap'])}</span></div>
<div class="etf-cockpit-section-title">{escape(text['short'])}</div><p class="etf-cockpit-lede">{summary}</p>
<div class="etf-cockpit-row"><div class="etf-cockpit-card"><div class="etf-cockpit-label">{escape(text['climate'])}</div><div class="etf-cockpit-value">{escape(regime)}</div><div class="etf-cockpit-confidence"><div class="etf-cockpit-bar"><i style="width:{max(0, min(confidence, 100))}%"></i></div><span>{confidence}% {escape(text['confidence'])}</span></div></div><div class="etf-cockpit-card"><div class="etf-cockpit-label">{escape(text['action'])}</div><div class="etf-cockpit-value">{escape(action_title)}</div><div class="etf-cockpit-note">{escape(action_note)}</div></div></div>
<div class="etf-cockpit-section-title">{escape(text['performance'])}</div><div class="etf-cockpit-performance"><div class="etf-cockpit-chart"><div class="etf-cockpit-chart-caption"><span class="etf-cockpit-chart-title">{escape(text['nav'])} · EUR</span><span>{escape(cockpit._fmt_eur(nav, language))} · <b>{escape(cockpit._fmt_pct(since, language, signed=True))}</b></span></div>{cockpit._sparkline_svg(points)}</div><div class="etf-cockpit-metrics"><div class="etf-cockpit-metric"><div class="etf-cockpit-metric-label">{escape(text['return'])}</div><div class="etf-cockpit-metric-value {return_class}">{escape(cockpit._fmt_pct(since, language, signed=True))}</div><div class="etf-cockpit-metric-sub">{escape(cockpit._fmt_eur(points[0][1], language))} → {escape(cockpit._fmt_eur(nav, language))}</div></div><div class="etf-cockpit-metric"><div class="etf-cockpit-metric-label">{escape(text['drawdown'])}</div><div class="etf-cockpit-metric-value {drawdown_class}">{escape(cockpit._fmt_pct(drawdown, language))}</div><div class="etf-cockpit-metric-sub">{escape(text['since'])}</div></div><div class="etf-cockpit-metric"><div class="etf-cockpit-metric-label">{escape(text['cash'])}</div><div class="etf-cockpit-metric-value">{escape(cockpit._fmt_pct(cash_pct, language))}</div><div class="etf-cockpit-metric-sub">{escape(cockpit._fmt_eur(cash, language))}</div></div><div class="etf-cockpit-metric"><div class="etf-cockpit-metric-label">{escape(text['positions'])}</div><div class="etf-cockpit-metric-value">{len(cockpit._positions(state))}</div><div class="etf-cockpit-metric-sub">{escape(text['holdings'])}</div></div><div class="etf-cockpit-metric"><div class="etf-cockpit-metric-label">{escape(text['largest'])}</div><div class="etf-cockpit-metric-value">{escape(largest_ticker)}</div><div class="etf-cockpit-metric-sub">{escape(cockpit._fmt_pct(largest_weight, language))}</div></div><div class="etf-cockpit-metric"><div class="etf-cockpit-metric-label">EUR/USD</div><div class="etf-cockpit-metric-value">{cockpit._float((state.get('fx_basis') or {}).get('rate')):.4f}</div><div class="etf-cockpit-metric-sub">{escape(text['pricing'])}</div></div></div></div>
<div class="etf-cockpit-section-title">{escape(text['discipline'])}</div><div class="etf-cockpit-discipline">{escape(discipline)}</div><div class="etf-cockpit-trigger" data-next-action-trigger="true">{escape(next_trigger)}</div>
{evidence}<div class="etf-cockpit-footer"><span>{escape(text['footer'])}</span><span>01</span></div>
</div></section>"""

    lowered = html.lower()
    leaked = [token for token in cockpit.INTERNAL_SURFACE_TOKENS if token in lowered]
    preview_tokens = [
        "preview lane",
        "preview-only cockpit",
        "no delivery claim",
        "not promoted to production",
        "voorbeeldcockpit",
        "geen leveringsclaim",
        "niet naar productie gepromoveerd",
    ]
    leaked.extend(token for token in preview_tokens if token in lowered)
    if leaked:
        raise RuntimeError(f"Delivery cockpit leaked forbidden wording: {', '.join(sorted(set(leaked)))}")

    return CockpitFrontPageFragment(css=_delivery_css(), html=html, language=language)


def _inject_fragment(classic_html: str, fragment: CockpitFrontPageFragment) -> str:
    if FRONT_PAGE_MARKER in classic_html:
        if classic_html.count(FRONT_PAGE_MARKER) != 1:
            raise RuntimeError("Classic HTML already contains multiple cockpit front pages")
        return classic_html

    head_close = re.search(r"</head\s*>", classic_html, flags=re.IGNORECASE)
    body_open = re.search(r"<body\b[^>]*>", classic_html, flags=re.IGNORECASE)
    if body_open is None:
        raise RuntimeError("Classic HTML is missing an opening body element")

    updated = classic_html
    if f'id="{STYLE_ID}"' not in updated:
        if head_close is not None:
            updated = updated[: head_close.start()] + fragment.css + updated[head_close.start() :]
        else:
            updated = fragment.css + updated

    body_open = re.search(r"<body\b[^>]*>", updated, flags=re.IGNORECASE)
    if body_open is None:
        raise RuntimeError("HTML body disappeared during cockpit style injection")
    updated = updated[: body_open.end()] + fragment.html + updated[body_open.end() :]
    if updated.count(FRONT_PAGE_MARKER) != 1:
        raise RuntimeError("Cockpit delivery front page count is not exactly one after injection")
    return updated


def inject_additive_cockpit_front_page(
    classic_html: str,
    *,
    language: str,
    output_dir: Path = Path("output"),
    render_mode: str = "email",
    feature_value: str | None = None,
    renderer: Callable[..., CockpitFrontPageFragment] = render_delivery_cockpit_front_page_fragment,
) -> CockpitFrontPageInjectionResult:
    try:
        mode = parse_feature_value(feature_value)
    except Exception as exc:
        return CockpitFrontPageInjectionResult(
            html=classic_html,
            status="fallback",
            diagnostic=f"invalid_feature_value:{type(exc).__name__}:{exc}",
            feature_value=str(feature_value if feature_value is not None else os.environ.get(FEATURE_FLAG, "disabled")),
            front_page_count=classic_html.count(FRONT_PAGE_MARKER),
        )

    if mode == "disabled":
        return CockpitFrontPageInjectionResult(
            html=classic_html,
            status="disabled",
            diagnostic="feature_disabled",
            feature_value=mode,
            front_page_count=classic_html.count(FRONT_PAGE_MARKER),
        )

    try:
        fragment = renderer(
            output_dir=Path(output_dir),
            language=language,
            render_mode=render_mode,
        )
        updated = _inject_fragment(classic_html, fragment)
        return CockpitFrontPageInjectionResult(
            html=updated,
            status="enabled",
            diagnostic="front_page_injected",
            feature_value=mode,
            front_page_count=updated.count(FRONT_PAGE_MARKER),
        )
    except Exception as exc:
        return CockpitFrontPageInjectionResult(
            html=classic_html,
            status="fallback",
            diagnostic=f"render_or_injection_failure:{type(exc).__name__}:{exc}",
            feature_value=mode,
            front_page_count=classic_html.count(FRONT_PAGE_MARKER),
        )
