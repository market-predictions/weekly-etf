from runtime.executed_replay_state_contract import executed_model_change_present


def test_executed_model_changes_are_recognized_without_position_annotations() -> None:
    state = {
        "positions": [{"ticker": "XBI", "shares": 100}],
        "executed_model_changes": [
            {"ticker": "URNM", "shares_delta": -48, "action": "reduce"},
            {"ticker": "XBI", "shares_delta": 78, "action": "add"},
        ],
    }

    assert executed_model_change_present(state) is True


def test_empty_or_hold_only_replay_is_not_execution() -> None:
    assert executed_model_change_present({"executed_model_changes": []}) is False
    assert (
        executed_model_change_present(
            {"executed_model_changes": [{"ticker": "SMH", "shares_delta": 0, "action": "hold"}]}
        )
        is False
    )


def test_explicit_executed_action_without_delta_is_recognized() -> None:
    state = {
        "executed_model_changes": [
            {"ticker": "XLU", "shares_delta": 0, "action_executed": "close executed"}
        ]
    }

    assert executed_model_change_present(state) is True
