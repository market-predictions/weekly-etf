from runtime.executed_report_contradiction_cleanup import (
    authoritative_execution_present,
    remove_no_action_contradictions,
)


def executed_state() -> dict:
    return {
        "executed_model_changes": [
            {"ticker": "URNM", "shares_delta": -48, "action": "reduce"},
            {"ticker": "XBI", "shares_delta": 78, "action": "add"},
        ]
    }


def test_execution_evidence_is_recognized() -> None:
    assert authoritative_execution_present(executed_state()) is True


def test_english_no_action_phrase_is_repaired_only_for_executed_state() -> None:
    source = "The decision cockpit states: no portfolio action this week."
    repaired = remove_no_action_contradictions(source, executed_state(), "en")

    assert "no portfolio action" not in repaired.lower()
    assert "portfolio action executed and reflected" in repaired.lower()
    assert remove_no_action_contradictions(source, {"executed_model_changes": []}, "en") == source


def test_dutch_no_action_phrase_is_repaired_only_for_executed_state() -> None:
    source = "De besliscockpit vermeldt: geen portefeuilleactie deze week."
    repaired = remove_no_action_contradictions(source, executed_state(), "nl")

    assert "geen portefeuilleactie" not in repaired.lower()
    assert "portefeuilleactie uitgevoerd en verwerkt" in repaired.lower()
    assert remove_no_action_contradictions(source, {"executed_model_changes": []}, "nl") == source
