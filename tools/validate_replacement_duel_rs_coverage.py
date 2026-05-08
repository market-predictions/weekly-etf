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


def _required_target_map_tickers() -> set[str]:
    macro = _load_yaml(MACRO_PATH)
    target_map = ((macro.get("replacement_duel_policy") or {}).get("target_map") or {})
    holdings = _current_holdings()
    tickers: set[str] = set()
    for holding, payload in target_map.items():
        holding_ticker = _ticker(holding)
        if holding_ticker not in holdings:
            continue
        tickers.add(holding_ticker)
        challengers = payload.get("challengers", []) if isinstance(payload, dict) else payload or []
        for challenger in challengers:
            challenger_ticker = _ticker(challenger)
            if challenger_ticker:
                tickers.add(challenger_ticker)
    return tickers


def main() -> None:
    rs = _load_json(RS_PATH)
    metrics = rs.get("metrics", {}) or {}
    required = _required_target_map_tickers()
    missing = sorted(ticker for ticker in required if ticker not in metrics)
    if missing:
        raise RuntimeError(
            "Replacement duel RS coverage failed: target-map tickers missing from historical metrics: "
            + ", ".join(missing)
        )

    incomplete = sorted(
        ticker
        for ticker in required
        if (metrics.get(ticker) or {}).get("return_1m_pct") is None
        or (metrics.get(ticker) or {}).get("return_3m_pct") is None
    )
    if incomplete:
        raise RuntimeError(
            "Replacement duel RS coverage failed: target-map tickers lack 1m/3m returns: "
            + ", ".join(incomplete)
        )

    print(
        "ETF_REPLACEMENT_DUEL_RS_COVERAGE_OK | "
        f"required={len(required)} | tickers={','.join(sorted(required))}"
    )


if __name__ == "__main__":
    main()
