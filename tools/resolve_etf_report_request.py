from __future__ import annotations

import argparse
import re
from pathlib import Path

DATE_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}$")
TRUTHY = {"1", "true", "yes", "y", "on"}
FALSEY = {"0", "false", "no", "n", "off"}


def _parse_request(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace("-", "_")
        values[key] = value.strip().strip('"').strip("'")
    return values


def _latest_request(run_queue_dir: Path) -> Path | None:
    files = sorted(run_queue_dir.glob("weekly_etf_report_request_*.md"))
    return files[-1] if files else None


def _bool_value(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in TRUTHY:
        return True
    if normalized in FALSEY:
        return False
    return default


def _env_line(key: str, value: str) -> str:
    safe_value = value.replace("\n", " ").replace("\r", " ")
    return f"{key}={safe_value}\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-queue-dir", default="control/run_queue")
    parser.add_argument("--github-env", default="")
    args = parser.parse_args()

    run_queue_dir = Path(args.run_queue_dir)
    latest = _latest_request(run_queue_dir)

    requested_close_date = ""
    strict_required = False
    source = "none"
    if latest is not None:
        source = str(latest)
        values = _parse_request(latest)
        candidate = values.get("requested_close_date", "")
        if DATE_RE.match(candidate):
            requested_close_date = candidate
        strict_required = _bool_value(values.get("strict_fresh_pricing_required"), default=False)

    # Balanced default policy:
    # - explicit requested_close_date is honored when provided
    # - one small stale/prior-valid holding is tolerated
    # - most of the portfolio must still be exact-close priced
    # - strict_fresh_pricing_required can still force all holdings exact
    env_values = {
        "ETF_REPORT_REQUEST_SOURCE": source,
        "ETF_REQUESTED_CLOSE_DATE": requested_close_date,
        "ETF_STRICT_FRESH_PRICING_REQUIRED": "true" if strict_required else "false",
        "ETF_FRESH_PRICE_MIN_COUNT_PCT": "83.34",
        "ETF_FRESH_PRICE_MIN_WEIGHT_PCT": "85.00",
        "ETF_MAX_STALE_HOLDINGS": "1",
        "ETF_MAX_STALE_WEIGHT_PCT": "20.00",
        "ETF_MAX_ACCEPTABLE_CLOSE_LAG_DAYS": "1",
    }

    github_env = Path(args.github_env) if args.github_env else None
    if github_env:
        with github_env.open("a", encoding="utf-8") as handle:
            for key, value in env_values.items():
                handle.write(_env_line(key, value))

    print(
        "ETF_REPORT_REQUEST_RESOLVED | "
        f"source={source} | requested_close_date={requested_close_date or 'auto'} | "
        f"strict_fresh_pricing_required={env_values['ETF_STRICT_FRESH_PRICING_REQUIRED']} | "
        f"min_count_pct={env_values['ETF_FRESH_PRICE_MIN_COUNT_PCT']} | "
        f"min_weight_pct={env_values['ETF_FRESH_PRICE_MIN_WEIGHT_PCT']} | "
        f"max_stale_holdings={env_values['ETF_MAX_STALE_HOLDINGS']} | "
        f"max_stale_weight_pct={env_values['ETF_MAX_STALE_WEIGHT_PCT']}"
    )


if __name__ == "__main__":
    main()
