from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from runtime.build_etf_report_state import build_runtime_state
from runtime.render_etf_report_from_state import f2, position_rows

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")


def latest_report(output_dir: Path, pattern: re.Pattern[str]) -> Path:
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    if not reports:
        raise RuntimeError(f"No matching report found in {output_dir} for {pattern.pattern}")
    return reports[-1]


def replace_between(text: str, start_heading: str, end_heading: str, replacement_body: str) -> str:
    start = text.find(start_heading)
    if start == -1:
        raise RuntimeError(f"Missing start heading: {start_heading}")
    body_start = start + len(start_heading)
    end = text.find(end_heading, body_start)
    if end == -1:
        raise RuntimeError(f"Missing end heading: {end_heading}")
    return text[:body_start] + "\n\n" + replacement_body.strip() + "\n\n" + text[end:]


def clean_action(value: Any) -> str:
    return str(value or "").strip() or "None"


def compact(value: Any, max_len: int = 105) -> str:
    raw = clean_action(value)
    if len(raw) <= max_len:
        return raw
    return raw[: max_len - 1].rstrip() + "…"


def is_add(p: dict[str, Any]) -> bool:
    action = clean_action(p.get("suggested_action")).lower()
    executed = clean_action(p.get("action_executed_this_run")).lower()
    shares_delta = float(p.get("shares_delta_this_run") or 0.0)
    return "add" in action or "buy" in executed or shares_delta > 0


def is_hold(p: dict[str, Any]) -> bool:
    action = clean_action(p.get("suggested_action")).lower()
    return "hold" in action and not is_add(p)


def is_replace(p: dict[str, Any]) -> bool:
    action = clean_action(p.get("suggested_action")).lower()
    better = clean_action(p.get("better_alternative_exists")).lower()
    return better == "yes" or "review" in action or "replace" in action


def tickers(items: list[dict[str, Any]]) -> str:
    values = [str(p.get("ticker", "")).upper() for p in items if p.get("ticker")]
    return ", ".join(values) if values else "None"


def current_position_cards(state: dict[str, Any]) -> str:
    """Renderer-safe current-position block.

    The PDF renderer's current-position template gives strong visual treatment to
    `###` titles. In the previous output, only the ticker heading survived into
    the PDF. Therefore the essential decision data is now embedded directly in
    each heading, with the paragraph kept as a secondary fallback.
    """
    parts = [
        "The position review separates thesis quality, ETF implementation quality and the fresh-cash test. Existing holdings are not treated as automatic default holds."
    ]
    for p in position_rows(state):
        ticker = str(p.get("ticker", "")).upper()
        score = f2(p.get("total_score")) or "n/a"
        action = clean_action(p.get("suggested_action"))
        fresh_cash = clean_action(p.get("fresh_cash_test"))
        role = clean_action(p.get("portfolio_role"))
        key_point = compact(p.get("short_reason"), 96)
        next_action = compact(p.get("required_next_action"), 96)
        parts.extend([
            f"### {ticker} — {action} — Score {score} — Fresh cash: {fresh_cash}",
            f"Role: {role}. Key point: {key_point}. Next action: {next_action}.",
            "",
        ])
    return "\n".join(parts).strip()


def rotation_plan_sections(state: dict[str, Any]) -> str:
    positions = position_rows(state)
    add = [p for p in positions if is_add(p)]
    hold = [p for p in positions if is_hold(p)]
    replace = [p for p in positions if is_replace(p)]
    reduce = [p for p in positions if "reduce" in clean_action(p.get("suggested_action")).lower()]
    close = [p for p in positions if "close" in clean_action(p.get("suggested_action")).lower() or "sell" in clean_action(p.get("suggested_action")).lower()]
    return "\n".join([
        "| Close | Reduce | Hold | Add | Replace |",
        "|---|---|---|---|---|",
        f"| {tickers(close)} | {tickers(reduce)} | {tickers(hold)} | {tickers(add)} | {tickers(replace)} |",
    ])


def trim_omitted_lanes_table(text: str, max_rows: int = 5) -> str:
    marker = "### Notable lanes assessed but not promoted this week"
    start = text.find(marker)
    if start == -1:
        return text
    table_start = text.find("| Theme | Primary ETF |", start)
    if table_start == -1:
        return text
    next_heading = text.find("\n## 4A.", table_start)
    if next_heading == -1:
        return text
    block = text[table_start:next_heading].strip("\n")
    lines = block.splitlines()
    if len(lines) <= 2:
        return text
    header = lines[:2]
    rows = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        theme, primary = cells[0], cells[1]
        if not theme or not primary:
            continue
        rows.append(line)
        if len(rows) >= max_rows:
            break
    new_block = "\n".join(header + rows)
    return text[:table_start] + new_block + "\n" + text[next_heading:]


def patch_report(path: Path, state: dict[str, Any]) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_between(
        text,
        "## 10. Current Position Review",
        "## 11. Best New Opportunities",
        current_position_cards(state),
    )
    text = replace_between(
        text,
        "## 12. Portfolio Rotation Plan",
        "## 13. Final Action Table",
        rotation_plan_sections(state),
    )
    text = trim_omitted_lanes_table(text)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--runtime-state", default=None)
    args = parser.parse_args()

    if args.runtime_state:
        state = json.loads(Path(args.runtime_state).read_text(encoding="utf-8"))
    else:
        state = build_runtime_state()
    output_dir = Path(args.output_dir)
    for pattern in (EN_RE, NL_RE):
        patch_report(latest_report(output_dir, pattern), state)
    print("ETF_OUTPUT_CONTRACT_FIX_OK")


if __name__ == "__main__":
    main()
