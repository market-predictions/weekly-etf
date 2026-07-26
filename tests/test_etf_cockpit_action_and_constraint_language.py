from __future__ import annotations

from runtime import render_cockpit_front_page as cockpit
from runtime.report_surface_language_contract import (
    client_language_findings,
    normalize_client_language,
)


def _base_state() -> dict:
    return {
        "positions": [
            {
                "ticker": "SMH",
                "shares_delta_this_run": 0.0,
                "action_executed_this_run": "None",
                "previous_weight_pct": 27.16,
                "current_weight_pct": 27.16,
            }
        ],
        "executed_model_changes": [],
    }


def test_additive_cockpit_names_proposed_source_and_destination() -> None:
    state = _base_state()
    state["trade_intents"] = [
        {
            "source_ticker": "SMH",
            "destination_ticker": "DFEN",
            "delta_weight_pct": -2.0,
            "destination_delta_weight_pct": 2.0,
        }
    ]

    title_en, note_en = cockpit._action_surface(state, "en")
    title_nl, note_nl = cockpit._action_surface(state, "nl")

    assert title_en == "Proposed — not executed"
    assert "SMH -2.00% NAV" in note_en
    assert "DFEN +2.00% NAV" in note_en
    assert "No trade was executed" in note_en
    assert title_nl == "Voorgesteld — niet uitgevoerd"
    assert "SMH -2.00% NAV" in note_nl
    assert "DFEN +2.00% NAV" in note_nl
    assert "Geen transactie is uitgevoerd" in note_nl


def test_additive_cockpit_no_change_wording_is_explicit() -> None:
    state = _base_state()
    state["trade_intents"] = []

    title_en, note_en = cockpit._action_surface(state, "en")
    title_nl, note_nl = cockpit._action_surface(state, "nl")

    assert title_en == "No change proposed or executed"
    assert "current weights remain unchanged" in note_en
    assert title_nl == "Geen wijziging voorgesteld of uitgevoerd"
    assert "huidige gewichten blijven ongewijzigd" in note_nl


def test_constraint_language_cleanup_removes_internal_override_terms() -> None:
    english = (
        "SMH; override portfolio constraint blocked\n"
        "System override: Portfolio constraint blocks action\n"
        "Override status"
    )
    dutch = (
        "Aanhouden met onderbouwde override\n"
        "Override-toelichting: uitleg\n"
        "Systeemoverride: Portefeuillerandvoorwaarde blokkeert actie\n"
        "Override-status"
    )

    cleaned_en = normalize_client_language(english, language="en")
    cleaned_nl = normalize_client_language(dutch, language="nl")

    assert "override" not in cleaned_en.lower()
    assert "Execution constraint: portfolio capacity blocks action" in cleaned_en
    assert client_language_findings(cleaned_en, language="en") == []

    assert "override" not in cleaned_nl.lower()
    assert "Uitvoeringsbeperking: portefeuillecapaciteit blokkeert actie" in cleaned_nl
    assert "Status uitvoeringsbeperking" in cleaned_nl
    assert client_language_findings(cleaned_nl, language="nl") == []
