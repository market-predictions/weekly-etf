from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

RS_PATH = Path("output/market_history/etf_relative_strength.json")
MACRO_PATH = Path("config/etf_macro_fundamental_context.yml")
PORTFOLIO_STATE_PATH = Path("output/etf_portfolio_state.json")

# These are the current high-priority duels that must be usable for the report.
# Secondary or illiquid challengers may still be displayed as incomplete rather
# than blocking the whole production run.
REQUIRED_CHALLENGERS_BY_HOLDING: dict[str, set[str]] = {
    "SPY": {"QUAL", "IEFA"},
    "PPA": {"ITA"},
    "PAVE": {"GRID"},
    "GLD": {"GSG", "DBC", "BIL"},
}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required file: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _current_holdings() -> set[str]:
    state = _load_json(PORTFOLIO_STATE_PATH)
    return {_ticker(position.get("ticker")) for position in state.get("positions", []) if _ticker(position.get("ticker"))}


def _target_map() -> dict[str, list[str]]:
    macro = _load_yaml(MACRO_PATH)
    target_map = ((macro.get("replacement_duel_policy") or {}).get("target_map") or {})
    out: dict[str, list[str]] = {}
    for holding, payload in target_map.items():
        holding_ticker = _ticker(holding)
        challengers = payload.get("challengers", []) if isinstance(payload, dict) else payload or []
        out[holding_ticker] = [_ticker(challenger) for challenger in challengers if _ticker(challenger)]
    return out


def _required_tickers() -> set[str]:
    holdings = _current_holdings()
    configured = _target_map()
    required: set[str] = set()
    for holding, challengers in REQUIRED_CHALLENGERS_BY_HOLDING.items():
        if holding not in holdings:
            continue
        required.add(holding)
        configured_challengers = set(configured.get(holding, []))
        required.update(challenger for challenger in challengers if challenger in configured_challengers)
    return required


def _optional_tickers() -> set[str]:
    holdings = _current_holdings()
    configured = _target_map()
    optional: set[str] = set()
    for holding, challengers in configured.items():
        if holding not in holdings:
            continue
        optional.add(holding)
        optional.update(challengers)
    return optional - _required_tickers()


def _has_1m_3m(metrics: dict[str, Any], ticker: str) -> bool:
    row = metrics.get(ticker) or {}
    return row.get("return_1m_pct") is not None and row.get("return_3m_pct") is not None


def main() -> None:
    rs = _load_json(RS_PATH)
    metrics = rs.get("metrics", {}) or {}
    required = _required_tickers()
    optional = _optional_tickers()

    missing_required = sorted(ticker for ticker in required if ticker not in metrics)
    if missing_required:
        raise RuntimeError(
            "Replacement duel RS coverage failed: required strategic tickers missing from historical metrics: "
            + ", ".join(missing_required)
        )

    incomplete_required = sorted(ticker for ticker in required if not _has_1m_3m(metrics, ticker))
    if incomplete_required:
        raise RuntimeError(
            "Replacement duel RS coverage failed: required strategic tickers lack 1m/3m returns: "
            + ", ".join(incomplete_required)
        )

    missing_optional = sorted(ticker for ticker in optional if ticker not in metrics)
    incomplete_optional = sorted(ticker for ticker in optional if ticker in metrics and not _has_1m_3m(metrics, ticker))

    print(
        "ETF_REPLACEMENT_DUEL_RS_COVERAGE_OK | "
        f"required={len(required)} | optional={len(optional)} | "
        f"missing_optional={','.join(missing_optional) if missing_optional else 'none'} | "
        f"incomplete_optional={','.join(incomplete_optional) if incomplete_optional else 'none'}"
    )


if __name__ == "__main__":
    main()
