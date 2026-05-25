from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EN_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
OLD_START = "<!-- ETF_PRICE_BASIS_DISCLOSURE_START -->"
OLD_END = "<!-- ETF_PRICE_BASIS_DISCLOSURE_END -->"
SECTION_RE = re.compile(r"(^##\s+(\d+)\.\s+.*?$)", re.M)
EN_HEADING = "### Closing prices used in this report"
NL_HEADING = "### Gebruikte slotkoersen in dit rapport"


def f2(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""


def f4(value: Any) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return ""


def text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw if raw else fallback


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_runtime_state(output_dir: Path) -> dict[str, Any]:
    runtime_dir = output_dir / "runtime"
    files = sorted(runtime_dir.glob("etf_report_state_*.json"))
    if not files:
        raise RuntimeError(f"No runtime ETF state files found in {runtime_dir}")
    return read_json(files[-1])


def latest_price_audit(output_dir: Path) -> dict[str, Any]:
    pricing_dir = output_dir / "pricing"
    files = sorted(pricing_dir.glob("price_audit_*.json"))
    if not files:
        raise RuntimeError(f"No pricing audit files found in {pricing_dir}")
    return read_json(files[-1])


def latest_report_pair(output_dir: Path) -> tuple[Path, Path]:
    candidates: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_analysis_pro_*.md"):
        if "_nl_" in path.name or path.name.endswith("_clean.md"):
            continue
        match = EN_REPORT_RE.match(path.name)
        if not match:
            continue
        token = match.group(1)
        version = int(match.group(2) or "1")
        candidates.append((token, version, path))
    if not candidates:
        raise RuntimeError(f"No English ETF Pro reports found in {output_dir}")
    candidates.sort(key=lambda item: (item[0], item[1]))
    token, version, en_path = candidates[-1]
    suffix = "" if version == 1 else f"_{version:02d}"
    nl_path = output_dir / f"weekly_analysis_pro_nl_{token}{suffix}.md"
    if not nl_path.exists():
        raise RuntimeError(f"Matching Dutch report missing for {en_path.name}: {nl_path.name}")
    return en_path, nl_path


def section_bounds(markdown: str, section_number: int) -> tuple[int, int] | None:
    matches = list(SECTION_RE.finditer(markdown))
    for idx, match in enumerate(matches):
        if int(match.group(2)) == section_number:
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(markdown)
            return start, end
    return None


def remove_existing_block(markdown: str) -> str:
    out = re.sub(rf"\n?{re.escape(OLD_START)}.*?{re.escape(OLD_END)}\n?", "\n", markdown, flags=re.S)
    out = re.sub(r"\n?&lt;!-- ETF_PRICE_BASIS_DISCLOSURE_START --&gt;.*?&lt;!-- ETF_PRICE_BASIS_DISCLOSURE_END --&gt;\n?", "\n", out, flags=re.S)
    for heading in (EN_HEADING, NL_HEADING):
        pattern = rf"\n?{re.escape(heading)}\n.*?(?=\n`EQUITY_CURVE_CHART_PLACEHOLDER`|\n### |\n## |\Z)"
        out = re.sub(pattern, "\n", out, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", out)


def price_status_label(value: Any, language: str) -> str:
    raw = text(value, "unknown")
    labels = {
        "fresh_close": {"en": "Fresh exact close", "nl": "Exacte slotkoers"},
        "fresh_fallback_source": {"en": "Prior valid close", "nl": "Eerdere geldige slotkoers"},
        "fresh_exact_close": {"en": "Fresh exact close, verified", "nl": "Exacte slotkoers, geverifieerd"},
        "fresh_exact_unverified": {"en": "Fresh exact close, unverified", "nl": "Exacte slotkoers, niet onafhankelijk geverifieerd"},
        "prior_valid_close": {"en": "Prior valid market close", "nl": "Eerdere geldige markt-slotkoers"},
        "carried_forward": {"en": "Carried forward", "nl": "Doorgeschoven"},
        "unresolved": {"en": "Unresolved", "nl": "Niet opgelost"},
        "blocked": {"en": "Blocked", "nl": "Geblokkeerd"},
    }
    return labels.get(raw, {"en": raw, "nl": raw}).get(language, raw)


def source_label(result: dict[str, Any], language: str) -> str:
    source = text(result.get("source"))
    delegated = text((result.get("metadata") or {}).get("delegated_source"))
    source_detail = text(result.get("source_detail"))
    source_to_label = {
        "twelve_data": {"en": "Twelve Data", "nl": "Twelve Data"},
        "yahoo_history": {"en": "Yahoo Finance history", "nl": "Yahoo Finance historie"},
        "yfinance": {"en": "Yahoo Finance history", "nl": "Yahoo Finance historie"},
        "fmp": {"en": "Financial Modeling Prep", "nl": "Financial Modeling Prep"},
        "alpha_vantage": {"en": "Alpha Vantage", "nl": "Alpha Vantage"},
        "ecb_reference": {"en": "ECB reference rate", "nl": "ECB-referentiekoers"},
        "issuer_pages": {"en": "Issuer page", "nl": "Uitgeverpagina"},
        "price_cache": {"en": "Persisted price cache", "nl": "Opgeslagen prijscache"},
        "manual_override": {"en": "Manual override", "nl": "Handmatige override"},
    }
    if delegated in {"yahoo_history", "yfinance"}:
        return "Yahoo Finance history via issuer resolver" if language == "en" else "Yahoo Finance historie via uitgeversresolver"
    if source == "issuer_override":
        return "Issuer resolver" if not source_detail else "Issuer resolver with delegated market data"
    return source_to_label.get(source, {"en": source or "Not recorded", "nl": source or "Niet vastgelegd"}).get(language, source)


def audit_price_map(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = audit.get("price_results") or audit.get("prices") or []
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = text(row.get("symbol")).upper()
        if symbol:
            out[symbol] = row
    return out


def close_value(row: dict[str, Any]) -> Any:
    return row.get("selected_close") if row.get("selected_close") is not None else row.get("price")


def holding_order(state: dict[str, Any], audit: dict[str, Any]) -> list[str]:
    tickers = [text(p.get("ticker")).upper() for p in state.get("positions", []) if text(p.get("ticker"))]
    if tickers:
        return tickers
    return [text(h.get("ticker")).upper() for h in audit.get("holdings", []) if text(h.get("ticker"))]


def en_block(state: dict[str, Any], audit: dict[str, Any]) -> str:
    requested_close = text(audit.get("requested_close_date") or state.get("requested_close_date") or state.get("report_date"), "unknown")
    price_map = audit_price_map(audit)
    fx = audit.get("fx_basis") or state.get("fx_basis") or {}
    lines = [
        EN_HEADING,
        "",
        f"The portfolio valuation above is based on the per-position closes shown here. Requested close date: **{requested_close}**. The source column shows the market-data layer that supplied the close, not internal resolver names.",
        "",
        "| Holding | Requested close | Close date used | Close used | Currency | Market-data source | Status |",
        "|---|---|---|---:|---|---|---|",
    ]
    for ticker in holding_order(state, audit):
        row = price_map.get(ticker, {})
        lines.append(
            f"| {ticker} | {text(row.get('requested_close_date'), requested_close)} | {text(row.get('returned_close_date'), requested_close)} | "
            f"{f2(close_value(row))} | {text(row.get('currency'), 'USD')} | {source_label(row, 'en')} | {price_status_label(row.get('status'), 'en')} |"
        )
    fx_date = text(fx.get("returned_date") or fx.get("requested_date"), requested_close)
    lines.extend([
        "",
        "| FX basis | Requested date | Date used | Rate | Source | Status |",
        "|---|---|---|---:|---|---|",
        f"| {text(fx.get('pair'), 'EUR/USD')} | {text(fx.get('requested_date'), requested_close)} | {fx_date} | {f4(fx.get('rate'))} | {source_label(fx, 'en')} | {price_status_label(fx.get('status'), 'en')} |",
    ])
    return "\n".join(lines)


def nl_block(state: dict[str, Any], audit: dict[str, Any]) -> str:
    requested_close = text(audit.get("requested_close_date") or state.get("requested_close_date") or state.get("report_date"), "onbekend")
    price_map = audit_price_map(audit)
    fx = audit.get("fx_basis") or state.get("fx_basis") or {}
    lines = [
        NL_HEADING,
        "",
        f"De bovenstaande portefeuillewaardering is gebaseerd op de slotkoersen per positie in deze tabel. Gevraagde slotdatum: **{requested_close}**. De bronkolom toont de marktdata-laag die de slotkoers leverde, niet interne resolvernamen.",
        "",
        "| Positie | Gevraagde slotdatum | Gebruikte slotdatum | Gebruikte slotkoers | Valuta | Marktdata-bron | Status |",
        "|---|---|---|---:|---|---|---|",
    ]
    for ticker in holding_order(state, audit):
        row = price_map.get(ticker, {})
        lines.append(
            f"| {ticker} | {text(row.get('requested_close_date'), requested_close)} | {text(row.get('returned_close_date'), requested_close)} | "
            f"{f2(close_value(row))} | {text(row.get('currency'), 'USD')} | {source_label(row, 'nl')} | {price_status_label(row.get('status'), 'nl')} |"
        )
    fx_date = text(fx.get("returned_date") or fx.get("requested_date"), requested_close)
    lines.extend([
        "",
        "| FX-basis | Gevraagde datum | Gebruikte datum | Koers | Bron | Status |",
        "|---|---|---|---:|---|---|",
        f"| {text(fx.get('pair'), 'EUR/USD')} | {text(fx.get('requested_date'), requested_close)} | {fx_date} | {f4(fx.get('rate'))} | {source_label(fx, 'nl')} | {price_status_label(fx.get('status'), 'nl')} |",
    ])
    return "\n".join(lines)


def end_of_first_table(section: str) -> int | None:
    lines = section.splitlines(keepends=True)
    offset = 0
    for i in range(len(lines) - 1):
        if lines[i].lstrip().startswith("|") and lines[i + 1].lstrip().startswith("|") and "---" in lines[i + 1]:
            j = i + 2
            end_offset = offset + len(lines[i]) + len(lines[i + 1])
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                end_offset += len(lines[j])
                j += 1
            return end_offset
        offset += len(lines[i])
    return None


def insert_into_section7(markdown: str, block: str) -> str:
    clean = remove_existing_block(markdown)
    bounds = section_bounds(clean, 7)
    if not bounds:
        raise RuntimeError("Section 7 not found for pricing basis disclosure insertion")
    start, end = bounds
    section = clean[start:end]
    first_table_end = end_of_first_table(section)
    if first_table_end is not None:
        insert_at = start + first_table_end
        return clean[:insert_at].rstrip() + "\n\n" + block + "\n\n" + clean[insert_at:].lstrip()
    placeholder = section.find("`EQUITY_CURVE_CHART_PLACEHOLDER`")
    if placeholder >= 0:
        insert_at = start + placeholder
        return clean[:insert_at].rstrip() + "\n\n" + block + "\n\n" + clean[insert_at:].lstrip()
    return clean[:end].rstrip() + "\n\n" + block + "\n\n" + clean[end:].lstrip()


def update_report(path: Path, state: dict[str, Any], audit: dict[str, Any], language: str) -> None:
    block = nl_block(state, audit) if language == "nl" else en_block(state, audit)
    path.write_text(insert_into_section7(path.read_text(encoding="utf-8"), block), encoding="utf-8")
    print(f"ETF_PRICE_BASIS_DISCLOSURE_ADDED | language={language} | report={path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--runtime-state", default=None)
    parser.add_argument("--pricing-audit", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    state = read_json(Path(args.runtime_state)) if args.runtime_state else latest_runtime_state(output_dir)
    audit = read_json(Path(args.pricing_audit)) if args.pricing_audit else latest_price_audit(output_dir)
    en_path, nl_path = latest_report_pair(output_dir)
    update_report(en_path, state, audit, "en")
    update_report(nl_path, state, audit, "nl")


if __name__ == "__main__":
    main()
