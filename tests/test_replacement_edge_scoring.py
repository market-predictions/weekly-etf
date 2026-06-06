import json
from pathlib import Path

import pytest

from runtime.map_challenger_to_current_holding import map_challenger_to_current_holding
from runtime.score_replacement_edge import build_replacement_edge_artifact, write_replacement_edge_artifact
from tools.validate_replacement_edge_scoring import validate_replacement_edge_scoring


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _portfolio_state() -> dict:
    return {
        "positions": [
            {"ticker": "SPY", "bucket": "us_equity", "taxonomy_tag": "us_large_cap", "name": "US large-cap equity"},
            {"ticker": "TLT", "bucket": "duration", "taxonomy_tag": "long_duration", "name": "long duration bonds"},
            {"ticker": "CASH", "name": "residual cash"},
        ]
    }


def _lane_assessment() -> dict:
    return {
        "report_date": "2026-06-06",
        "assessed_lanes": [
            {
                "lane_name": "US quality challenger",
                "bucket": "us_equity",
                "taxonomy_tag": "us_large_cap",
                "primary_etf": "QUAL",
                "challenger": True,
            },
            {
                "lane_name": "Explicit duration challenger",
                "bucket": "duration",
                "taxonomy_tag": "long_duration",
                "primary_etf": "IEF",
                "replacement_target": "TLT",
                "challenger": True,
            },
            {
                "lane_name": "Held lane should not map to itself",
                "bucket": "us_equity",
                "taxonomy_tag": "us_large_cap",
                "primary_etf": "SPY",
                "challenger": True,
            },
        ],
    }


def _relative_strength() -> dict:
    return {
        "metrics": {
            "SPY": {"return_1m_pct": 2.0, "return_3m_pct": 6.0, "max_drawdown_3m_pct": -8.0, "volatility_3m_pct": 14.0},
            "QUAL": {"return_1m_pct": 5.0, "return_3m_pct": 11.0, "max_drawdown_3m_pct": -6.0, "volatility_3m_pct": 12.0},
            "TLT": {"return_1m_pct": -1.0, "return_3m_pct": 1.0, "max_drawdown_3m_pct": -12.0, "volatility_3m_pct": 19.0},
            "IEF": {"return_1m_pct": 0.5, "return_3m_pct": 3.0, "max_drawdown_3m_pct": -5.0, "volatility_3m_pct": 8.0},
        }
    }


def test_maps_challenger_by_metadata_without_trade_authority():
    lane = _lane_assessment()["assessed_lanes"][0]
    mapping = map_challenger_to_current_holding(lane, _portfolio_state())

    assert mapping is not None
    assert mapping.current_holding == "SPY"
    assert mapping.challenger == "QUAL"
    assert "metadata" in mapping.mapping_confidence


def test_builds_diagnostic_replacement_edge_artifact(tmp_path: Path):
    lane_path = _write(tmp_path / "output/lane_reviews/etf_lane_assessment_260606.json", _lane_assessment())
    rs_path = _write(tmp_path / "output/market_history/etf_relative_strength.json", _relative_strength())
    portfolio_path = _write(tmp_path / "output/etf_portfolio_state.json", _portfolio_state())

    payload = build_replacement_edge_artifact(lane_path, rs_path, portfolio_path, run_id="20260606_000000")

    assert payload["diagnostic_only"] is True
    assert payload["portfolio_action_authority"] is False
    assert payload["fundability_authority"] is False
    assert payload["lane_scoring_authority"] is False
    assert len(payload["edges"]) == 2

    qual_edge = next(edge for edge in payload["edges"] if edge["challenger"] == "QUAL")
    assert qual_edge["current_holding"] == "SPY"
    assert qual_edge["1m_relative_strength_edge"] == 3.0
    assert qual_edge["3m_relative_strength_edge"] == 5.0
    assert qual_edge["drawdown_edge"] == 2.0
    assert qual_edge["volatility_edge"] == 2.0
    assert qual_edge["replacement_edge_score"] > 0


def test_validator_accepts_generated_artifact(tmp_path: Path):
    lane_path = _write(tmp_path / "output/lane_reviews/etf_lane_assessment_260606.json", _lane_assessment())
    rs_path = _write(tmp_path / "output/market_history/etf_relative_strength.json", _relative_strength())
    portfolio_path = _write(tmp_path / "output/etf_portfolio_state.json", _portfolio_state())
    payload = build_replacement_edge_artifact(lane_path, rs_path, portfolio_path, run_id="20260606_000000")
    artifact = write_replacement_edge_artifact(payload, tmp_path / "output/replacement_edges")

    validate_replacement_edge_scoring(artifact)


def test_validator_rejects_authority_escalation(tmp_path: Path):
    lane_path = _write(tmp_path / "output/lane_reviews/etf_lane_assessment_260606.json", _lane_assessment())
    rs_path = _write(tmp_path / "output/market_history/etf_relative_strength.json", _relative_strength())
    portfolio_path = _write(tmp_path / "output/etf_portfolio_state.json", _portfolio_state())
    payload = build_replacement_edge_artifact(lane_path, rs_path, portfolio_path, run_id="20260606_000000")
    payload["portfolio_action_authority"] = True
    artifact = _write(tmp_path / "bad.json", payload)

    with pytest.raises(RuntimeError, match="portfolio_action_authority must remain false"):
        validate_replacement_edge_scoring(artifact)
