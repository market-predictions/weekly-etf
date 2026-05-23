from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EN_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
START = "<!-- ETF_PRICE_BASIS_DISCLOSURE_START -->"
END = "<!-- ETF_PRICE_BASIS_DISCLOSURE_END -->"
SECTION_RE = re.compile(r"(^##\s+(\d+)\.\s+.*?$)", re.M)


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


def latest_runtime_state(output_dir: Path) -> dict[str, Any]:
    runtime_dir = output_dir / "runtime"
    files = sorted(runtime_dir.glob("etf_report_state_*.json"))
    if not files:
        raise RuntimeError(f"No runtime ETF state files found in {runtime_dir}")
    return json.loads(files[-1].read_text(encoding="utf-8"))


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


def remove_existing_block(text_value: str) -> str:
    return re.sub(rf"\n?{re.escape(START)}.*?{re.escape(END)}\n?", "\n", text_value, flags=re.S)


def price_status_label(value: Any, language: str) -> str:
    raw = text(value, "unknown")
    labels = {
        "fresh_close": {"en": "Fresh close", "nl": "Verse slotkoers"},
        "fresh_fallback_source": {"en": "Fresh fallback source", "nl": "Verse fallbackbron"},
        "carried_forward": {"en": "Carried forward", "nl": "Doorgeschoven"},
        "unresolved": {"en": "Unresolved", "nl": "Niet opgelost"},
    }
    return labels.get(raw, {"en": raw, "nl": raw}).get(language, raw)


def price_source(value: Any) -> str:
    return text(value, "not recorded")


def close_date_used(position: dict[str, Any], requested_close: str) -> str:
    return text(
        position.get("previous_price_date")
        or position.get("returned_close_date")
        or position.get("close_date")
        or position.get("pricing_date"),
        requested_close,
    )


def en_block(state: dict[str, Any]) -> str:
    requested_close = text(state.get("requested_close_date") or state.get("report_date"), "unknown")
    fx = state.get("fx_basis") or {}
    lines = [
        START,
        "### Closing prices used in this report",
        "",
        f"The portfolio valuation above is based on the per-position closes shown here. Requested close date: **{requested_close}**. If a holding used a fallback or carried-forward close, it is shown explicitly in this table.",
        "",
        "| Holding | Close date used | Close used | Currency | Pricing source | Status |",
        "|---|---|---:|---|---|---|",
    ]
    for position in state.get("positions", []) or []:
        ticker = text(position.get("ticker"), "UNKNOWN").upper()
        lines.append(
            f"| {ticker} | {close_date_used(position, requested_close)} | {f2(position.get('previous_price_local') or position.get('current_price_local'))} | "
            f"{text(position.get('currency'), 'USD')} | {price_source(position.get('pricing_source'))} | {price_status_label(position.get('pricing_status'), 'en')} |"
        )
    fx_date = text(fx.get("returned_date") or fx.get("requested_date"), requested_close)
    lines.extend(
        [
            "",
            "| FX basis | Date used | Rate | Source | Status |",
            "|---|---|---:|---|---|",
            f"| {text(fx.get('pair'), 'EUR/USD')} | {fx_date} | {f4(fx.get('rate'))} | {price_source(fx.get('source'))} | {price_status_label(fx.get('status'), 'en')} |",
            END,
        ]
    )
    return "\n".join(lines)


def nl_block(state: dict[str, Any]) -> str:
    requested_close = text(state.get("requested_close_date") or state.get("report_date"), "onbekend")
    fx = state.get("fx_basis") or {}
    lines = [
        START,
        "### Gebruikte slotkoersen in dit rapport",
        "",
        f"De bovenstaande portefeuillewaardering is gebaseerd op de slotkoersen per positie in deze tabel. Gevraagde slotdatum: **{requested_close}**. Als een positie een fallbackbron of doorgeschoven slotkoers gebruikt, staat dat expliciet in deze tabel.",
        "",
        "| Positie | Gebruikte slotdatum | Gebruikte slotkoers | Valuta | Prijsbron | Status |",
        "|---|---|---:|---|---|---|",
    ]
    for position in state.get("positions", []) or []:
        ticker = text(position.get("ticker"), "ONBEKEND").upper()
        lines.append(
            f"| {ticker} | {close_date_used(position, requested_close)} | {f2(position.get('previous_price_local') or position.get('current_price_local'))} | "
            f"{text(position.get('currency'), 'USD')} | {price_source(position.get('pricing_source'))} | {price_status_label(position.get('pricing_status'), 'nl')} |"
        )
    fx_date = text(fx.get("returned_date") or fx.get("requested_date"), requested_close)
    lines.extend(
        [
            "",
            "| FX-basis | Gebruikte datum | Koers | Bron | Status |",
            "|---|---|---:|---|---|",
            f"| {text(fx.get('pair'), 'EUR/USD')} | {fx_date} | {f4(fx.get('rate'))} | {price_source(fx.get('source'))} | {price_status_label(fx.get('status'), 'nl')} |",
            END,
        ]
    )
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

    # Keep the valuation-history table as the first table in Section 7.
    # send_report.py and the equity-curve validator intentionally parse the
    # first Section 7 table as the NAV history source. The pricing-basis table
    # is therefore inserted immediately after that first table, before the
    # chart placeholder where possible.
    first_table_end = end_of_first_table(section)
    if first_table_end is not None:
        insert_at = start + first_table_end
        return clean[:insert_at].rstrip() + "\n\n" + block + "\n\n" + clean[insert_at:].lstrip()

    placeholder = section.find("`EQUITY_CURVE_CHART_PLACEHOLDER`")
    if placeholder >= 0:
        insert_at = start + placeholder
        return clean[:insert_at].rstrip() + "\n\n" + block + "\n\n" + clean[insert_at:].lstrip()
    return clean[:end].rstrip() + "\n\n" + block + "\n\n" + clean[end:].lstrip()


def update_report(path: Path, state: dict[str, Any], language: str) -> None:
    block = nl_block(state) if language == "nl" else en_block(state)
    path.write_text(insert_into_section7(path.read_text(encoding="utf-8"), block), encoding="utf-8")
    print(f"ETF_PRICE_BASIS_DISCLOSURE_ADDED | language={language} | report={path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--runtime-state", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    state = json.loads(Path(args.runtime_state).read_text(encoding="utf-8")) if args.runtime_state else latest_runtime_state(output_dir)
    en_path, nl_path = latest_report_pair(output_dir)
    update_report(en_path, state, "en")
    update_report(nl_path, state, "nl")


if __name__ == "__main__":
    main()
