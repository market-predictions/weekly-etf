from runtime.etf_instrument_constraints import (
    apply_rotation_policy_constraints,
    normalize_lane_instruments,
)


CONSTRAINTS = {
    "schema_version": "1.1",
    "portfolio_policy": {
        "max_active_positions": 8,
        "leveraged_etfs_allowed": False,
    },
    "instruments": {
        "DFEN": {
            "portfolio_eligible": False,
            "reason": "daily_leveraged_3x",
            "eligible_research_replacement": "EUAD",
        }
    },
}


def test_ineligible_primary_is_replaced_by_eligible_vehicles() -> None:
    lane = {
        "lane_name": "Europe defense",
        "primary_etf": "DFEN",
        "alternative_etf": "NATO",
    }

    normalized = normalize_lane_instruments(lane, CONSTRAINTS)

    assert normalized["primary_etf"] == "NATO"
    assert normalized["alternative_etf"] == "EUAD"
    assert normalized["primary_portfolio_eligible"] is True
    assert normalized["alternative_portfolio_eligible"] is True
    assert normalized["excluded_research_vehicle"] == "DFEN"
    assert normalized["excluded_research_vehicle_reason"] == "daily_leveraged_3x"
    assert normalized["eligible_research_replacement_applied"] is True


def test_close_first_state_blocks_partial_new_ticker_rotation() -> None:
    incumbents = [
        {"ticker": ticker, "current_weight_pct": 10.0}
        for ticker in ("A", "B", "C", "D", "E", "F", "G", "H", "I")
    ]
    plan = {
        "policy": {},
        "incumbent_reviews": incumbents,
        "candidate_reviews": [
            {
                "candidate": "NATO",
                "is_fundable_candidate": True,
                "funding_scope": "general",
                "destination_reasons": [],
            }
        ],
        "rotation_decisions": [
            {
                "ticker": "A",
                "action_code": "replace_partial",
                "current_weight_pct": 10.0,
                "target_weight_pct": 8.0,
                "delta_weight_pct": -2.0,
                "destination_ticker": "NATO",
                "override_status": "none",
                "override_reason_code": "",
                "reason_codes": [],
            }
        ],
        "target_weights": [
            *[
                {
                    "ticker": row["ticker"],
                    "target_weight_pct": (
                        8.0 if row["ticker"] == "A" else 10.0
                    ),
                }
                for row in incumbents
            ],
            {"ticker": "NATO", "target_weight_pct": 2.0},
        ],
        "trade_intents": [
            {
                "source_ticker": "A",
                "destination_ticker": "NATO",
                "delta_weight_pct": -2.0,
                "destination_delta_weight_pct": 2.0,
            }
        ],
        "validation_flags": {},
    }

    constrained = apply_rotation_policy_constraints(plan, CONSTRAINTS)

    assert constrained["trade_intents"] == []
    assert all(
        row["ticker"] != "NATO" for row in constrained["target_weights"]
    )
    decision = constrained["rotation_decisions"][0]
    assert decision["action_code"] == "hold_with_override"
    assert decision["target_weight_pct"] == 10.0
    assert decision["override_reason_code"] == "portfolio_constraint_blocked"
    assert (
        constrained["portfolio_constraint_validation"]["block_reason"]
        == "position_count_close_first"
    )
    assert (
        constrained["validation_flags"][
            "portfolio_constraint_validation_passed"
        ]
        is True
    )


def test_ineligible_destination_is_blocked_even_when_position_count_is_compliant() -> None:
    plan = {
        "policy": {},
        "incumbent_reviews": [
            {"ticker": ticker, "current_weight_pct": 20.0}
            for ticker in ("A", "B", "C", "D")
        ],
        "candidate_reviews": [
            {
                "candidate": "DFEN",
                "is_fundable_candidate": True,
                "funding_scope": "general",
                "destination_reasons": [],
            }
        ],
        "rotation_decisions": [
            {
                "ticker": "A",
                "action_code": "replace_partial",
                "current_weight_pct": 20.0,
                "target_weight_pct": 18.0,
                "delta_weight_pct": -2.0,
                "destination_ticker": "DFEN",
                "override_status": "none",
                "override_reason_code": "",
                "reason_codes": [],
            }
        ],
        "target_weights": [
            {"ticker": "A", "target_weight_pct": 18.0},
            {"ticker": "B", "target_weight_pct": 20.0},
            {"ticker": "C", "target_weight_pct": 20.0},
            {"ticker": "D", "target_weight_pct": 20.0},
            {"ticker": "DFEN", "target_weight_pct": 2.0},
        ],
        "trade_intents": [
            {
                "source_ticker": "A",
                "destination_ticker": "DFEN",
                "delta_weight_pct": -2.0,
                "destination_delta_weight_pct": 2.0,
            }
        ],
        "validation_flags": {},
    }

    constrained = apply_rotation_policy_constraints(plan, CONSTRAINTS)

    assert constrained["trade_intents"] == []
    assert (
        constrained["candidate_reviews"][0]["is_fundable_candidate"]
        is False
    )
    assert (
        constrained["portfolio_constraint_validation"]["block_reason"]
        == "portfolio_ineligible_destination"
    )
