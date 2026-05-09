from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from runtime.build_etf_report_state import build_runtime_state
from runtime.render_etf_report_from_state import f2, position_rows, replacement_duel_table

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")


def latest_report(output_dir: Path, pattern: re.Pattern[str]) -> Path:
    """Return the report this run just rendered, not merely the latest file by name.

    The workflow exports MRKT_RPRTS_EXPLICIT_REPORT_PATH and
    MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL immediately after runtime rendering.
    Without this, same-day reruns can patch an older/newer filename while the
    content validator correctly checks the explicit runtime output.
    """
    for env_name in ("MRKT_RPRTS_EXPLICIT_REPORT_PATH", "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL"):
        raw = os.environ.get(env_name, "").strip()
        if not raw:
            continue
        path = Path(raw)
        if pattern.match(path.name):
            if not path.exists():
                raise RuntimeError(f"Explicit report path from {env_name} does not exist: {path}")
            return path

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


def clean_optional(value: Any) -> str:
    raw = str(value or "").strip()
    if raw.lower() in {"none", "nan", "null", "n/a", "-"}:
        return ""
    return raw


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


def is_reduce(p: dict[str, Any]) -> bool:
    return "reduce" in clean_action(p.get("suggested_action")).lower()


def is_close(p: dict[str, Any]) -> bool:
    action = clean_action(p.get("suggested_action")).lower()
    return "close" in action or "sell" in action


def tickers(items: list[dict[str, Any]]) -> str:
    values = [str(p.get("ticker", "")).upper() for p in items if p.get("ticker")]
    return ", ".join(values) if values else "None"


def ticker_bullets(items: list[dict[str, Any]]) -> str:
    values = [str(p.get("ticker", "")).upper() for p in items if p.get("ticker")]
    if not values:
        return "- None"
    return "\n".join(f"- {ticker}" for ticker in values)


def action_snapshot_section(state: dict[str, Any]) -> str:
    positions = position_rows(state)
    add = [p for p in positions if is_add(p)]
    hold = [p for p in positions if is_hold(p) or is_add(p)]
    replace = [p for p in positions if is_replace(p)]
    reduce = [p for p in positions if is_reduce(p)]
    close = [p for p in positions if is_close(p)]
    return "\n".join([
        "### Add",
        ticker_bullets(add),
        "",
        "### Hold",
        ticker_bullets(hold),
        "",
        "### Hold but replaceable",
        f"- {tickers(replace)} remain under explicit review." if replace else "- None.",
        "",
        "### Reduce",
        ticker_bullets(reduce),
        "",
        "### Close",
        ticker_bullets(close),
        "",
        "### Best replacements to fund",
        "- No challenger is promoted to a fundable replacement yet. Each named replacement must first clear the same close-date pricing basis and relative-strength duel.",
        "",
        "### Replacement pricing and duel status",
        "",
        replacement_duel_table(state),
    ])


def current_position_cards(state: dict[str, Any]) -> str:
    # This section is rendered by a custom card renderer, not by the generic
    # markdown-table renderer. Keep the essential fields in the H3 title so the
    # PDF cannot drop the details.
    parts = [
        "The position review separates thesis quality, ETF implementation quality and the fresh-cash test. Existing holdings are not treated as automatic default holds."
    ]
    for p in position_rows(state):
        ticker = str(p.get("ticker", "")).upper()
        action = clean_action(p.get("suggested_action"))
        score = f2(p.get("total_score")) or "n/a"
        fresh_cash = clean_action(p.get("fresh_cash_test"))
        role = compact(p.get("portfolio_role"), 70)
        next_action = compact(p.get("required_next_action"), 95)
        parts.extend([
            f"### {ticker} — {action} — Score {score} — Fresh cash: {fresh_cash}",
            f"Role: {role}. Required next action: {next_action}.",
            "",
        ])
    return "\n".join(parts).strip()


def rotation_plan_sections(state: dict[str, Any]) -> str:
    positions = position_rows(state)
    add = [p for p in positions if is_add(p)]
    hold = [p for p in positions if is_hold(p)]
    replace = [p for p in positions if is_replace(p)]
    reduce = [p for p in positions if is_reduce(p)]
    close = [p for p in positions if is_close(p)]
    return "\n".join([
        "| Close | Reduce | Hold | Add | Replace |",
        "|---|---|---|---|---|",
        f"| {tickers(close)} | {tickers(reduce)} | {tickers(hold)} | {tickers(add)} | {tickers(replace)} |",
    ])


def lane_label(lane: dict[str, Any]) -> str:
    primary = clean_optional(lane.get("primary_etf"))
    alternative = clean_optional(lane.get("alternative_etf"))
    if primary and alternative:
        return f"{primary} / {alternative}"
    if primary:
        return primary
    if alternative:
        return alternative
    return clean_optional(lane.get("lane_name")) or "Unnamed challenger lane"


def best_new_opportunities(state: dict[str, Any]) -> str:
    lines = ["- SMH remains the leading funded growth exposure, subject to the max-position rule."]
    promoted = state.get("lane_assessment", {}).get("assessed_lanes", [])
    count = 0
    for lane in promoted:
        if lane.get("promoted_to_live_radar") is True and lane.get("challenger") is True and count < 3:
            label = lane_label(lane)
            summary = compact(lane.get("evidence_summary") or lane.get("why_now"), 150)
            lines.append(f"- {label}: {summary}")
            count += 1
    if count == 0:
        lines.append("- No challenger is fundable without completed pricing and relative-strength duel evidence.")
    lines.append("- Replacement candidates remain evidence-gated: pricing basis and duel status must be visible before funding.")
    return "\n".join(lines)


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
        "## 2. Portfolio Action Snapshot",
        "## 3. Regime Dashboard",
        action_snapshot_section(state),
    )
    text = replace_between(
        text,
        "## 10. Current Position Review",
        "## 11. Best New Opportunities",
        current_position_cards(state),
    )
    text = replace_between(
        text,
        "## 11. Best New Opportunities",
        "## 12. Portfolio Rotation Plan",
        best_new_opportunities(state),
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
