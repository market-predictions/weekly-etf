from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.report_portfolio_integrity_contract import validate_report_portfolio_integrity

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")


def _runtime_state(path_value: str | None) -> tuple[Path, dict]:
    candidates: list[Path] = []
    if path_value:
        candidates.append(Path(path_value))
    for env_name in ("MRKT_RPRTS_RUNTIME_STATE_PATH", "ETF_RUNTIME_STATE_PATH"):
        raw = os.environ.get(env_name, "").strip()
        if raw:
            candidates.append(Path(raw))
    pointer = Path("output/runtime/latest_etf_report_state_path.txt")
    if pointer.exists():
        raw = pointer.read_text(encoding="utf-8").strip()
        if raw:
            candidates.append(Path(raw))
    for candidate in candidates:
        if not candidate.exists() and not candidate.is_absolute():
            alternate = Path("output/runtime") / candidate.name
            if alternate.exists():
                candidate = alternate
        if candidate.exists():
            return candidate, json.loads(candidate.read_text(encoding="utf-8"))
    raise RuntimeError("No runtime ETF state is available for report-integrity validation.")


def _report(output_dir: Path, pattern: re.Pattern[str], explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.exists():
            raise RuntimeError(f"Explicit report does not exist: {path}")
        return path
    candidates = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    if not candidates:
        raise RuntimeError(f"No report matches {pattern.pattern} in {output_dir}")
    return candidates[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Weekly ETF portfolio/watchlist and stale-surface integrity.")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--runtime-state", default=None)
    parser.add_argument("--english-report", default=None)
    parser.add_argument("--dutch-report", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    state_path, state = _runtime_state(args.runtime_state)
    en_path = _report(output_dir, EN_RE, args.english_report or os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH"))
    nl_path = _report(output_dir, NL_RE, args.dutch_report or os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL"))

    validate_report_portfolio_integrity(en_path.read_text(encoding="utf-8"), state, "en")
    validate_report_portfolio_integrity(nl_path.read_text(encoding="utf-8"), state, "nl")
    print(
        "ETF_REPORT_PORTFOLIO_INTEGRITY_OK | "
        f"runtime_state={state_path} | en={en_path} | nl={nl_path}"
    )


if __name__ == "__main__":
    main()
