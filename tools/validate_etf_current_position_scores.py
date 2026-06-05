from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_report_state import build_runtime_state

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")
SCORE_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def _latest_report(output_dir: Path, pattern: re.Pattern[str], env_name: str) -> Path:
    explicit = os.environ.get(env_name, "").strip()
    if explicit:
        path = Path(explicit)
        if path.exists() and pattern.match(path.name):
            return path
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    if not reports:
        raise RuntimeError(f"No matching report found for {pattern.pattern} in {output_dir}")
    return reports[-1]


def _runtime_state(runtime_state_path: str | None) -> dict[str, Any]:
    if runtime_state_path:
        return json.loads(Path(runtime_state_path).read_text(encoding="utf-8"))
    env_path = os.environ.get("MRKT_RPRTS_RUNTIME_STATE_PATH") or os.environ.get("ETF_RUNTIME_STATE_PATH")
    if env_path and Path(env_path).exists():
        return json.loads(Path(env_path).read_text(encoding="utf-8"))
    return build_runtime_state()


def _active_tickers(state: dict[str, Any]) -> list[str]:
    return [str(p.get("ticker") or "").strip().upper() for p in state.get("positions", []) if str(p.get("ticker") or "").strip()]


def _position_scores(state: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in state.get("positions", []) or []:
        ticker = str(p.get("ticker") or "").strip().upper()
        value = str(p.get("total_score") or "").strip()
        if ticker:
            out[ticker] = value
    return out


def _plain_ticker_text(md_text: str) -> str:
    return re.sub(r"\[([A-Z][A-Z0-9.-]*)\]\([^\)]*\)", r"\1", md_text)


def _section(md_text: str, start_heading: str, end_heading: str) -> str:
    start = md_text.find(start_heading)
    if start == -1:
        raise RuntimeError(f"Missing section heading: {start_heading}")
    end = md_text.find(end_heading, start + len(start_heading))
    if end == -1:
        raise RuntimeError(f"Missing end heading after {start_heading}: {end_heading}")
    return md_text[start:end]


def _row_score(section: str, ticker: str) -> str | None:
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0] == ticker:
            return cells[2] if "Actie" in section or "Vers kapitaal" in section else cells[1]
    return None


def validate_runtime_scores(state: dict[str, Any]) -> None:
    missing = []
    invalid = []
    for ticker, score in _position_scores(state).items():
        if not score:
            missing.append(ticker)
        elif SCORE_RE.fullmatch(score) is None:
            invalid.append(f"{ticker}={score!r}")
    if missing or invalid:
        raise RuntimeError(
            "ETF current-position score validation failed in runtime state: "
            f"missing={missing or 'none'} invalid={invalid or 'none'}"
        )


def validate_report_scores(path: Path, state: dict[str, Any], language: str) -> None:
    text = _plain_ticker_text(path.read_text(encoding="utf-8"))
    if language == "nl":
        section = _section(text, "## 10. Review huidige posities", "## 11. Beste nieuwe kansen")
    else:
        section = _section(text, "## 10. Current Position Review", "## 11. Best New Opportunities")
    failures = []
    for ticker in _active_tickers(state):
        score = _row_score(section, ticker)
        if score is None:
            failures.append(f"{ticker}=row_missing")
        elif score.lower() in {"", "n/a", "n.v.t.", "none", "-"}:
            failures.append(f"{ticker}={score!r}")
        elif SCORE_RE.search(score) is None:
            failures.append(f"{ticker}={score!r}")
    if failures:
        raise RuntimeError(f"ETF current-position score validation failed for {path.name}: " + ", ".join(failures))
    print(f"ETF_CURRENT_POSITION_SCORES_OK | report={path.name} | language={language} | positions={len(_active_tickers(state))}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--runtime-state", default=None)
    args = parser.parse_args()

    state = _runtime_state(args.runtime_state)
    validate_runtime_scores(state)
    output_dir = Path(args.output_dir)
    validate_report_scores(_latest_report(output_dir, EN_RE, "MRKT_RPRTS_EXPLICIT_REPORT_PATH"), state, "en")
    validate_report_scores(_latest_report(output_dir, NL_RE, "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL"), state, "nl")


if __name__ == "__main__":
    main()
