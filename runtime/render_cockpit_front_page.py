from __future__ import annotations

import argparse
import csv
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

STARTING_CAPITAL_EUR = 100000.0
SOFT_MAX_POSITION_PCT = 25.0
MACRO_POLICY_PACK_PATH = Path("output/macro/latest.json")
PRICING_AUDIT_POINTER = Path("output/pricing/latest_price_audit_path.txt")
RUN_MANIFEST_POINTER = Path("output/run_manifests/latest_weekly_etf_run_manifest_path.txt")
PREVIEW_DIR_NAME = "cockpit_preview"

INTERNAL_SURFACE_TOKENS = (
    "release score",
    "runtime valuation",
    "immutable pricing audit",
    "system override",
    "fundability authority",
    "lane scoring",
    "shadow engine",
    "shadow-engine",
)


@dataclass(frozen=True)
class RenderedCockpit:
    language: str
    html_path: Path
    pdf_path: Path | None


def _read_text_pointer(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"Missing required pointer file: {path}")
    target = path.read_text(encoding="utf-8").strip()
    if not target:
        raise RuntimeError(f"Pointer file is empty: {path}")
    return target


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing JSON artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _output_relative(path: Path, output_dir: Path) -> Path:
    if path.is_absolute():
        return path
    return output_dir.parent / path if str(path).startswith("output/") else output_dir / path


def _resolve_runtime_state_path(output_dir: Path, explicit_runtime_state: str | None = None) -> Path:
    if explicit_runtime_state:
        return _output_relative(Path(explicit_runtime_state), output_dir)
    return _output_relative(Path(_read_text_pointer(output_dir / "runtime" / "latest_etf_report_state_path.txt")), output_dir)


def _macro_pack_path(output_dir: Path, state: dict[str, Any]) -> Path:
    source_files = state.get("source_files") or {}
    return _output_relative(Path(source_files.get("macro_policy_pack") or str(MACRO_POLICY_PACK_PATH)), output_dir)


def _load_macro_pack(output_dir: Path, state: dict[str, Any]) -> dict[str, Any]:
    path = _macro_pack_path(output_dir, state)
    if not path.exists():
        return {}
    try:
        return _load_json(path)
    except Exception:
        return {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _first_present_number(mapping: dict[str, Any], *keys: str, default: float = 0.0) -> float:
    """Use the first present numeric field without treating an authoritative zero as missing."""
    for key in keys:
        if key not in mapping or mapping[key] is None or mapping[key] == "":
            continue
        try:
            value = float(mapping[key])
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            return value
    return default


def _fmt_eur(value: float, language: str) -> str:
    text = f"{value:,.0f}"
    return "€" + (text.replace(",", ".") if language == "nl" else text)


def _fmt_pct(value: float, language: str, signed: bool = False) -> str:
    sign = "+" if signed and value > 0 else ""
    text = f"{sign}{value:.1f}%"
    return text.replace(".", ",") if language == "nl" else text


def _fmt_date(value: str, language: str) -> str:
    try:
        date = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return value
    if language == "nl":
        months = "januari februari maart april mei juni juli augustus september oktober november december".split()
        return f"{date.day} {months[date.month - 1]} {date.year}"
    return date.strftime("%d %b %Y")


def _positions(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in (state.get("positions") or []) if str(row.get("ticker") or "").strip()]


def _market_value_eur(position: dict[str, Any]) -> float:
    return _first_present_number(position, "market_value_eur", "previous_market_value_eur")


def _position_weight(position: dict[str, Any]) -> float:
    return _first_present_number(position, "current_weight_pct", "target_weight_pct", "previous_weight_pct", "weight_inherited_pct")


def _previous_weight(position: dict[str, Any]) -> float:
    return _first_present_number(position, "previous_weight_pct", "weight_inherited_pct", "current_weight_pct")


def _total_nav(state: dict[str, Any]) -> float:
    portfolio = state.get("portfolio") or {}
    explicit = _float(portfolio.get("total_portfolio_value_eur"), 0.0)
    if explicit > 0:
        return explicit
    return round(_float(portfolio.get("cash_eur"), 0.0) + sum(_market_value_eur(position) for position in _positions(state)), 2)


def _cash_eur(state: dict[str, Any]) -> float:
    return _float((state.get("portfolio") or {}).get("cash_eur"))


def _read_valuation_history(output_dir: Path, state: dict[str, Any]) -> list[tuple[str, float]]:
    path = output_dir / "etf_valuation_history.csv"
    points: dict[str, float] = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                date = str(row.get("date") or "").strip()
                nav = _float(row.get("nav_eur"), 0.0)
                if date and nav > 0:
                    points[date] = round(nav, 2)
    report_date = str(state.get("report_date") or state.get("requested_close_date") or "").strip()
    if report_date:
        points[report_date] = _total_nav(state)
    if not points:
        points["2026-03-28"] = STARTING_CAPITAL_EUR
    return sorted(points.items())


def _max_drawdown_pct(points: list[tuple[str, float]]) -> float:
    peak = 0.0
    worst = 0.0
    for _, value in points:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, (value / peak - 1.0) * 100.0)
    return worst


def _since_start_pct(points: list[tuple[str, float]], nav: float) -> float:
    first = points[0][1] if points else STARTING_CAPITAL_EUR
    return (nav / first - 1.0) * 100.0 if first else 0.0


def _largest_position(state: dict[str, Any]) -> tuple[str, float]:
    rows = _positions(state)
    if not rows:
        return "-", 0.0
    largest = max(rows, key=_position_weight)
    return str(largest.get("ticker") or "-").upper(), _position_weight(largest)


def _report_token(state: dict[str, Any]) -> str:
    date = str(state.get("report_date") or state.get("requested_close_date") or "").strip()
    return date.replace("-", "")[2:] if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", date) else datetime.utcnow().strftime("%y%m%d")


def _next_sequence(preview_dir: Path, token: str, language: str) -> int:
    prefix = "weekly_analysis_pro_nl_cockpit" if language == "nl" else "weekly_analysis_pro_cockpit"
    pattern = re.compile(rf"^{re.escape(prefix)}_{re.escape(token)}_(\d{{2}})\.html$")
    existing = [int(match.group(1)) for path in preview_dir.glob(f"{prefix}_{token}_*.html") if (match := pattern.match(path.name))]
    return max(existing, default=0) + 1


def _macro_surface(macro: dict[str, Any]) -> tuple[str, int]:
    regime = macro.get("regime") or {}
    current = str(regime.get("current") or (macro.get("regime_memory") or {}).get("current_regime") or "Risk-on growth")
    confidence = int(round(_float(regime.get("confidence") or (macro.get("regime_memory") or {}).get("current_confidence"), 0.66) * 100))
    return current, confidence


def _executed_actions(state: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for position in _positions(state):
        shares_delta = _float(position.get("shares_delta_this_run"))
        action = str(position.get("action_executed_this_run") or "").strip()
        if abs(shares_delta) <= 1e-9 and action.lower() in {"", "none", "no", "n/a"}:
            continue
        actions.append(
            {
                "ticker": str(position.get("ticker") or "-").upper(),
                "shares_delta": shares_delta,
                "action": action,
                "previous_weight_pct": _previous_weight(position),
                "current_weight_pct": _position_weight(position),
            }
        )
    return actions


def _action_surface(state: dict[str, Any], language: str) -> tuple[str, str]:
    actions = _executed_actions(state)
    if not actions:
        if language == "nl":
            return "Geen portefeuilleactie", "Geen posities geopend, gesloten, vergroot of verkleind in deze preview-run."
        return "No portfolio action", "No positions opened, closed, increased, or reduced in this preview run."

    labels: list[str] = []
    details: list[str] = []
    for item in actions:
        normalized_action = str(item["action"]).lower()
        shares_delta = float(item["shares_delta"])
        if shares_delta < 0 or normalized_action in {"sell", "reduce", "reduced", "close", "closed"}:
            verb = "afgebouwd" if language == "nl" else "reduced"
        elif shares_delta > 0 or normalized_action in {"buy", "add", "added", "open", "opened"}:
            verb = "toegevoegd" if language == "nl" else "added"
        else:
            verb = "aangepast" if language == "nl" else "adjusted"
        labels.append(f"{item['ticker']} {verb}")
        details.append(
            f"{item['ticker']} {_fmt_pct(float(item['previous_weight_pct']), language)} → "
            f"{_fmt_pct(float(item['current_weight_pct']), language)}"
        )
    return " · ".join(labels), "; ".join(details) + "."


def _review_tickers(state: dict[str, Any]) -> list[str]:
    tickers: list[str] = []
    for position in _positions(state):
        ticker = str(position.get("ticker") or "").upper()
        fresh_cash = str(position.get("fresh_cash_test") or "").lower()
        role = str(position.get("portfolio_role") or "").lower()
        if ticker and ("review" in fresh_cash or "under" in fresh_cash or "review" in role or str(position.get("better_alternative_exists") or "").lower() == "yes" or _position_weight(position) > SOFT_MAX_POSITION_PCT):
            tickers.append(ticker)
    return tickers


def _discipline_surface(state: dict[str, Any], language: str) -> str:
    ticker, weight = _largest_position(state)
    reviews = _review_tickers(state)
    if language == "nl":
        if weight > SOFT_MAX_POSITION_PCT:
            return f"Belangrijkste disciplinepunt: {ticker} is {_fmt_pct(weight, 'nl')} en blijft boven de zachte positielimiet; nieuw kapitaal blijft dus geblokkeerd totdat de disciplinepoorten vrijgeven."
        if reviews:
            return f"Belangrijkste disciplinepunt: {', '.join(reviews[:4])} blijven onder herbeoordeling; vervanging vereist bevestigde relatieve sterkte, prijsbasis en financieringsbron."
        return "Belangrijkste disciplinepunt: geen nieuwe allocatie zonder bevestigde prijsbasis, relatieve sterkte en duidelijke financieringsbron."
    if weight > SOFT_MAX_POSITION_PCT:
        return f"Main discipline point: {ticker} is {weight:.1f}% and remains above the soft position cap; fresh capital stays blocked until discipline gates clear."
    if reviews:
        return f"Main discipline point: {', '.join(reviews[:4])} remain under review; replacement requires confirmed relative strength, pricing basis, and funding source."
    return "Main discipline point: no new allocation without confirmed pricing basis, relative strength, and clear funding source."


def _next_action_trigger(state: dict[str, Any], language: str) -> str:
    ticker, weight = _largest_position(state)
    reviews = _review_tickers(state)
    review_focus = ", ".join(reviews[:3]) or ticker
    if language == "nl":
        if weight > SOFT_MAX_POSITION_PCT:
            return (
                f"Trigger voor volgende actie: een volgende mutatie vereist dat {ticker} terugkeert binnen de zachte positielimiet, "
                f"of dat een alternatief voor {review_focus} bevestigde relatieve sterkte, een geldige prijsbasis, "
                "aansluiting op de beleggingsthese en een duidelijke financieringsbron toont."
            )
        if reviews:
            return (
                f"Trigger voor volgende actie: een mutatie in {review_focus} vereist bevestigde relatieve sterkte, "
                "een geldige prijsbasis, aansluiting op de beleggingsthese en een duidelijke financieringsbron."
            )
        return (
            "Trigger voor volgende actie: een nieuwe allocatie vereist bevestigde relatieve sterkte, "
            "een geldige prijsbasis, aansluiting op de beleggingsthese en een duidelijke financieringsbron."
        )
    if weight > SOFT_MAX_POSITION_PCT:
        return (
            f"Next action trigger: another mutation requires {ticker} to return within the soft position cap, "
            f"or an alternative to {review_focus} to show confirmed relative strength, a valid pricing basis, "
            "thesis fit, and a clear funding source."
        )
    if reviews:
        return (
            f"Next action trigger: a mutation in {review_focus} requires confirmed relative strength, "
            "a valid pricing basis, thesis fit, and a clear funding source."
        )
    return (
        "Next action trigger: a new allocation requires confirmed relative strength, "
        "a valid pricing basis, thesis fit, and a clear funding source."
    )


def _plain_summary(state: dict[str, Any], macro: dict[str, Any], points: list[tuple[str, float]], language: str) -> str:
    regime, _ = _macro_surface(macro)
    nav = _total_nav(state)
    since = _since_start_pct(points, nav)
    ticker, weight = _largest_position(state)
    action_title, _ = _action_surface(state, language)
    if _executed_actions(state):
        if language == "nl":
            return f"Deze week is een gecontroleerde rotatie uitgevoerd: {action_title}. De portefeuille staat sinds de start op {_fmt_pct(since, 'nl', signed=True)}, het marktklimaat blijft {escape(regime)}, en de grootste concentratie zit in {ticker} met {_fmt_pct(weight, 'nl')}."
        return f"A controlled rotation was executed this week: {action_title}. The portfolio is {_fmt_pct(since, 'en', signed=True)} since inception, the market climate remains {escape(regime)}, and the largest concentration is {ticker} at {_fmt_pct(weight, 'en')}."
    if language == "nl":
        return f"We houden deze week discipline boven activiteit. De portefeuille staat sinds de start op {_fmt_pct(since, 'nl', signed=True)}, het marktklimaat blijft {escape(regime)}, en de grootste concentratie zit in {ticker} met {_fmt_pct(weight, 'nl')}. Actie deze week: {action_title}."
    return f"We keep discipline ahead of activity this week. The portfolio is {_fmt_pct(since, 'en', signed=True)} since inception, the market climate remains {escape(regime)}, and the largest concentration is {ticker} at {_fmt_pct(weight, 'en')}. This week's action: {action_title}."


def _sparkline_svg(points: list[tuple[str, float]]) -> str:
    if len(points) < 2:
        return ""
    width, height = 620, 130
    left, right, top, bottom = 18, 18, 12, 20
    vals = [value for _, value in points]
    min_v, max_v = min(vals), max(vals)
    span = max(max_v - min_v, 1.0)
    plot_w = width - left - right
    plot_h = height - top - bottom
    coords = [(left + (idx / max(len(points) - 1, 1)) * plot_w, top + (1 - ((value - min_v) / span)) * plot_h) for idx, (_, value) in enumerate(points)]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    baseline_y = top + (1 - ((STARTING_CAPITAL_EUR - min_v) / span)) * plot_h
    return f'<svg class="spark" viewBox="0 0 {width} {height}" role="img" aria-label="Equity curve preview"><line x1="{left}" y1="{baseline_y:.1f}" x2="{width-right}" y2="{baseline_y:.1f}" stroke="#D8CDB8" stroke-width="1" stroke-dasharray="2 4"/><polyline points="{poly}" fill="none" stroke="#0F4438" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><circle cx="{coords[-1][0]:.1f}" cy="{coords[-1][1]:.1f}" r="4.2" fill="#0F4438"/></svg>'


def _relative_label(path: Path, output_dir: Path) -> str:
    try:
        return str(path.relative_to(output_dir.parent)).replace("\\", "/")
    except ValueError:
        return path.name


def _optional_pointer_target(output_dir: Path, pointer_path: Path) -> Path | None:
    pointer = _output_relative(pointer_path, output_dir)
    if not pointer.exists():
        return None
    target = pointer.read_text(encoding="utf-8").strip()
    return _output_relative(Path(target), output_dir) if target else None


def _source_evidence_html(output_dir: Path, state_path: Path, macro_path: Path, language: str) -> str:
    is_nl = language == "nl"
    pricing_path = _optional_pointer_target(output_dir, PRICING_AUDIT_POINTER)
    run_manifest_path = _optional_pointer_target(output_dir, RUN_MANIFEST_POINTER)
    valuation_path = output_dir / "etf_valuation_history.csv"
    if is_nl:
        labels = [
            ("Gebouwd vanuit actuele portefeuillestatus", _relative_label(state_path, output_dir)),
            ("Waarderingshistorie gecontroleerd", _relative_label(valuation_path, output_dir) if valuation_path.exists() else "niet beschikbaar"),
            ("Bron prijscontrole", _relative_label(pricing_path, output_dir) if pricing_path and pricing_path.exists() else "niet beschikbaar"),
            ("Bron macrobeeld", _relative_label(macro_path, output_dir) if macro_path.exists() else "niet beschikbaar"),
            ("Bron uitvoerregistratie", _relative_label(run_manifest_path, output_dir) if run_manifest_path and run_manifest_path.exists() else "niet beschikbaar"),
            ("Voorbeeldcockpit", "beschikbaar"),
            ("Geen leveringsclaim", "leveringslaag niet aangeroepen"),
            ("Niet naar productie gepromoveerd", "productierapport ongewijzigd"),
        ]
        title = "Bronnen en bewijs"
        intro = "Deze cockpit is een voorbeeldlaag bovenop bestaande status- en controlebestanden. Hij vervangt het productierapport niet."
    else:
        labels = [
            ("Built from runtime state", _relative_label(state_path, output_dir)),
            ("Valuation history checked", _relative_label(valuation_path, output_dir) if valuation_path.exists() else "not available"),
            ("Pricing audit reference", _relative_label(pricing_path, output_dir) if pricing_path and pricing_path.exists() else "not available"),
            ("Macro pack reference", _relative_label(macro_path, output_dir) if macro_path.exists() else "not available"),
            ("Run-manifest reference", _relative_label(run_manifest_path, output_dir) if run_manifest_path and run_manifest_path.exists() else "not available"),
            ("Preview-only cockpit", "available"),
            ("No delivery claim", "delivery layer not invoked"),
            ("Not promoted to production", "production report unchanged"),
        ]
        title = "Source & evidence"
        intro = "This cockpit is a preview layer over existing runtime and audit files. It does not replace the production report."
    rows = "".join(f'<div class="evidence-item"><div class="ei-label">{escape(label)}</div><div class="ei-value">{escape(value)}</div></div>' for label, value in labels)
    return f'<div class="section-title">{escape(title)}</div><section class="evidence-strip" data-source-evidence="true" data-promotion-status="not_promoted"><p class="evidence-intro">{escape(intro)}</p><div class="evidence-grid">{rows}</div></section>'


def _html_document(state: dict[str, Any], macro: dict[str, Any], points: list[tuple[str, float]], language: str, output_dir: Path, state_path: Path, macro_path: Path) -> str:
    is_nl = language == "nl"
    nav = _total_nav(state)
    cash = _cash_eur(state)
    cash_pct = (cash / nav * 100.0) if nav else 0.0
    since = _since_start_pct(points, nav)
    drawdown = _max_drawdown_pct(points)
    largest_ticker, largest_weight = _largest_position(state)
    regime, confidence = _macro_surface(macro)
    action_title, action_note = _action_surface(state, language)
    report_date = str(state.get("report_date") or state.get("requested_close_date") or "")
    evidence_html = _source_evidence_html(output_dir, state_path, macro_path, language)
    text = {
        "title": "De ETF-Review" if is_nl else "The ETF Review",
        "kicker": "Beleggersrapport · US ETF-strategie" if is_nl else "Investor report · US ETF strategy",
        "frequency": "Wekelijks" if is_nl else "Weekly",
        "model": "Modelportefeuille · EUR" if is_nl else "Model portfolio · EUR",
        "short": "In het kort" if is_nl else "In brief",
        "climate": "Marktklimaat" if is_nl else "Market climate",
        "confidence": "vertrouwen" if is_nl else "confidence",
        "action": "Actie deze week" if is_nl else "This week's action",
        "perf": "Prestatie & risico" if is_nl else "Performance & risk",
        "nav": "Portefeuillewaarde" if is_nl else "Portfolio value",
        "ret": "Rendement sinds start" if is_nl else "Return since inception",
        "dd": "Grootste terugval" if is_nl else "Max drawdown",
        "cash": "Cash" if is_nl else "Cash",
        "positions": "Posities" if is_nl else "Positions",
        "largest": "Grootste positie" if is_nl else "Largest position",
        "disc": "Disciplinepunt" if is_nl else "Discipline point",
        "preview": "Preview-only cockpit surface; geen beleggingsadvies." if is_nl else "Preview-only cockpit surface; not investment advice.",
        "since": "sinds start" if is_nl else "since inception",
        "holdings": "actieve posities" if is_nl else "active holdings",
        "pricing": "prijsbasis" if is_nl else "pricing basis",
        "foot": "Preview-only artefact gebouwd vanuit huidige runtime-state." if is_nl else "Preview-only artifact generated from current runtime state.",
    }
    summary = _plain_summary(state, macro, points, language)
    discipline = _discipline_surface(state, language)
    next_trigger = _next_action_trigger(state, language)
    html = f"""<!DOCTYPE html><html lang="{'nl' if is_nl else 'en'}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{escape(text['title'])} — Cockpit preview</title><style>
    :root{{--paper:#F6F1E7;--paper-2:#EFE8D9;--ink:#211C16;--ink-soft:#5A5043;--line:#D8CDB8;--petrol:#0F4438;--brass:#B07D2B;--pos:#2F7A57;--neg:#A8452C}}*{{box-sizing:border-box}}body{{margin:0;padding:28px 16px;background:var(--paper);color:var(--ink);font-family:Arial,Helvetica,sans-serif}}.sheet{{max-width:780px;margin:0 auto;border:1px solid var(--line);background:var(--paper);box-shadow:0 18px 48px -28px rgba(33,28,22,.45)}}.pad{{padding:34px 42px 28px}}.top{{display:flex;justify-content:space-between;gap:20px;border-bottom:2px solid var(--ink);padding-bottom:14px}}.kicker,.issue,.strap,.section-title,.lab,.ms,.foot,.ei-label,.ei-value{{font-family:'Courier New',monospace}}.kicker{{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--brass)}}.mast{{font-family:Georgia,'Times New Roman',serif;font-size:40px;font-weight:700;line-height:1;margin-top:8px;letter-spacing:-.02em}}.mast em{{color:var(--petrol);font-style:italic;font-weight:400}}.issue{{text-align:right;font-size:10.5px;line-height:1.65;color:var(--ink-soft)}}.strap{{margin-top:12px;display:flex;gap:12px;align-items:center;font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-soft)}}.dot{{width:5px;height:5px;border-radius:50%;background:var(--brass);display:inline-block}}.section-title{{margin:28px 0 12px;color:var(--petrol);font-size:11px;letter-spacing:.19em;text-transform:uppercase;display:flex;align-items:center;gap:12px}}.section-title:after{{content:"";height:1px;background:var(--line);flex:1}}.lede{{font-family:Georgia,'Times New Roman',serif;font-size:20px;line-height:1.48}}.row{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:24px}}.card{{border:1px solid var(--line);background:var(--paper-2);padding:16px 18px}}.lab{{font-size:9.5px;letter-spacing:.17em;text-transform:uppercase;color:var(--ink-soft);margin-bottom:9px}}.value{{font-family:Georgia,'Times New Roman',serif;font-size:20px;font-weight:600;line-height:1.25}}.note{{font-size:12px;color:var(--ink-soft);line-height:1.45;margin-top:9px}}.conf{{display:flex;align-items:center;gap:9px;margin-top:12px}}.bar{{flex:1;height:6px;background:#E2D9C6;border-radius:4px;overflow:hidden}}.bar i{{display:block;height:100%;width:{max(0, min(confidence, 100))}%;background:linear-gradient(90deg,var(--petrol),#1c6b56)}}.perf-wrap{{border:1px solid var(--line);background:#fff}}.chartbox{{padding:18px 18px 6px}}.chart-cap{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-bottom:6px}}.chart-cap .t{{font-family:'Courier New',monospace;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft)}}svg.spark{{width:100%;height:120px;display:block}}.metrics{{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line)}}.metric{{padding:15px 16px;border-right:1px solid var(--line);border-top:1px solid var(--line)}}.metric:nth-child(3n){{border-right:none}}.metric:nth-child(-n+3){{border-top:none}}.ml{{font-family:'Courier New',monospace;font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft)}}.mv{{font-family:Georgia,'Times New Roman',serif;font-size:24px;font-weight:600;margin-top:7px;line-height:1}}.mv.pos{{color:var(--pos)}}.mv.neg{{color:var(--neg)}}.ms{{font-size:10.5px;color:var(--ink-soft);margin-top:5px}}.discipline{{border-left:4px solid var(--brass);background:rgba(176,125,43,.10);padding:14px 16px;font-size:13px;line-height:1.5}}.trigger{{margin-top:10px;border:1px solid var(--line);background:#fff;padding:13px 15px;font-size:12.5px;line-height:1.5;color:var(--ink-soft)}}.evidence-strip{{border:1px solid var(--line);background:#fff;padding:14px 16px}}.evidence-intro{{margin:0 0 12px;color:var(--ink-soft);font-size:12px;line-height:1.45}}.evidence-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px 14px}}.evidence-item{{border-top:1px solid var(--line);padding-top:8px}}.ei-label{{font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft)}}.ei-value{{margin-top:4px;font-size:10px;color:var(--ink);overflow-wrap:anywhere}}.foot{{margin-top:22px;padding-top:13px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:12px;color:var(--ink-soft);font-size:10px}}@media print{{body{{padding:0}}.sheet{{box-shadow:none;border:none}}}}
    </style></head><body><div class="sheet" data-cockpit-front-page="true" data-preview-only="true"><div class="pad"><header class="top"><div><div class="kicker">{escape(text['kicker'])}</div><div class="mast">{escape(text['title']).replace('ETF', '<em>ETF</em>')}</div></div><div class="issue">{escape(text['model'])}<br>{escape(_fmt_date(report_date, language))}<br><b>Preview lane</b></div></header><div class="strap"><span>{escape(text['frequency'])}</span><span class="dot"></span><span>US ETF</span><span class="dot"></span><span>{escape(text['preview'])}</span></div><div class="section-title">{escape(text['short'])}</div><p class="lede">{summary}</p><div class="row"><div class="card"><div class="lab">{escape(text['climate'])}</div><div class="value">{escape(regime)}</div><div class="conf"><div class="bar"><i></i></div><span>{confidence}% {escape(text['confidence'])}</span></div></div><div class="card"><div class="lab">{escape(text['action'])}</div><div class="value">{escape(action_title)}</div><div class="note">{escape(action_note)}</div></div></div><div class="section-title">{escape(text['perf'])}</div><div class="perf-wrap"><div class="chartbox"><div class="chart-cap"><span class="t">{escape(text['nav'])} · EUR</span><span class="v">{escape(_fmt_eur(nav, language))} · <b>{escape(_fmt_pct(since, language, signed=True))}</b></span></div>{_sparkline_svg(points)}</div><div class="metrics"><div class="metric"><div class="ml">{escape(text['ret'])}</div><div class="mv {'pos' if since >= 0 else 'neg'}">{escape(_fmt_pct(since, language, signed=True))}</div><div class="ms">{escape(_fmt_eur(points[0][1], language))} → {escape(_fmt_eur(nav, language))}</div></div><div class="metric"><div class="ml">{escape(text['dd'])}</div><div class="mv {'neg' if drawdown < 0 else ''}">{escape(_fmt_pct(drawdown, language))}</div><div class="ms">{escape(text['since'])}</div></div><div class="metric"><div class="ml">{escape(text['cash'])}</div><div class="mv">{escape(_fmt_pct(cash_pct, language))}</div><div class="ms">{escape(_fmt_eur(cash, language))}</div></div><div class="metric"><div class="ml">{escape(text['positions'])}</div><div class="mv">{len(_positions(state))}</div><div class="ms">{escape(text['holdings'])}</div></div><div class="metric"><div class="ml">{escape(text['largest'])}</div><div class="mv">{escape(largest_ticker)}</div><div class="ms">{escape(_fmt_pct(largest_weight, language))}</div></div><div class="metric"><div class="ml">EUR/USD</div><div class="mv">{_float((state.get('fx_basis') or {}).get('rate')):.4f}</div><div class="ms">{escape(text['pricing'])}</div></div></div></div><div class="section-title">{escape(text['disc'])}</div><div class="discipline">{escape(discipline)}</div><div class="trigger" data-next-action-trigger="true">{escape(next_trigger)}</div>{evidence_html}<div class="foot"><span>{escape(text['foot'])}</span><span>01 — cockpit preview</span></div></div></div></body></html>"""
    lower = html.lower()
    leaked = [token for token in INTERNAL_SURFACE_TOKENS if token in lower]
    if leaked:
        raise RuntimeError(f"Cockpit preview leaked internal engine language: {', '.join(leaked)}")
    return html


def _write_pdf(html_path: Path, pdf_path: Path) -> Path | None:
    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        return None
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    return pdf_path if pdf_path.exists() and pdf_path.stat().st_size > 0 else None


def render_cockpit_front_page(*, output_dir: Path, language: str = "both", html_only: bool = False, runtime_state: str | None = None) -> list[RenderedCockpit]:
    state_path = _resolve_runtime_state_path(output_dir, runtime_state)
    state = _load_json(state_path)
    macro_path = _macro_pack_path(output_dir, state)
    macro = _load_macro_pack(output_dir, state)
    points = _read_valuation_history(output_dir, state)
    token = _report_token(state)
    preview_dir = output_dir / PREVIEW_DIR_NAME
    preview_dir.mkdir(parents=True, exist_ok=True)
    languages = ["en", "nl"] if language == "both" else [language]
    rendered: list[RenderedCockpit] = []
    for lang in languages:
        if lang not in {"en", "nl"}:
            raise RuntimeError(f"Unsupported cockpit language: {lang}")
        seq = _next_sequence(preview_dir, token, lang)
        prefix = "weekly_analysis_pro_nl_cockpit" if lang == "nl" else "weekly_analysis_pro_cockpit"
        html_path = preview_dir / f"{prefix}_{token}_{seq:02d}.html"
        pdf_path = preview_dir / f"{prefix}_{token}_{seq:02d}.pdf"
        html_path.write_text(_html_document(state, macro, points, lang, output_dir, state_path, macro_path), encoding="utf-8")
        final_pdf_path = None if html_only else _write_pdf(html_path, pdf_path)
        rendered.append(RenderedCockpit(language=lang, html_path=html_path, pdf_path=final_pdf_path))
    return rendered


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render preview-only cockpit front-page artifacts for the Weekly ETF report.")
    parser.add_argument("--output-dir", default="output", help="Repository output directory. Defaults to output.")
    parser.add_argument("--language", choices=["en", "nl", "both"], default="both", help="Language surface to render.")
    parser.add_argument("--html-only", action="store_true", help="Render HTML only and skip optional PDF rendering.")
    parser.add_argument("--runtime-state", default=None, help="Optional explicit runtime-state JSON path.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    rendered = render_cockpit_front_page(output_dir=Path(args.output_dir), language=args.language, html_only=args.html_only, runtime_state=args.runtime_state)
    for item in rendered:
        pdf_display = str(item.pdf_path) if item.pdf_path else "not_rendered"
        print(f"COCKPIT_PREVIEW_OK | language={item.language} | html={item.html_path} | pdf={pdf_display}")


if __name__ == "__main__":
    main()
