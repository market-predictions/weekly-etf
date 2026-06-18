from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.rotation_render_tables import final_action_table_from_rotation, final_action_table_from_rotation_nl


def _state() -> dict:
    return {
        "positions": [{"ticker": "PAVE", "previous_weight_pct": 0.03, "current_weight_pct": 0.04}],
        "rotation_decisions": [
            {
                "ticker": "PAVE",
                "action_code": "hold_with_override",
                "target_weight_pct": 0.03,
                "release_score": 85,
                "reason_codes": ["role_impaired", "replaceable_status"],
                "override_status": "engine",
                "override_reason_code": "min_trade_size_not_met",
            }
        ],
        "target_weights": [{"ticker": "PAVE", "target_weight_pct": 0.03}],
    }


def test_english_action_table_contains_weight_basis_and_override_note() -> None:
    table = final_action_table_from_rotation(_state(), {"PAVE": "Global X U.S. Infrastructure Development ETF"})
    assert "Weight basis note: action-table weights are model/action weights" in table
    assert "Hold-with-override note:" in table
    assert "operationally impractical" in table


def test_dutch_action_table_contains_weight_basis_and_override_note() -> None:
    table = final_action_table_from_rotation_nl(_state(), {"PAVE": "Global X U.S. Infrastructure Development ETF"})
    assert "Toelichting gewichtsbasis: gewichten in de actietabel" in table
    assert "Override-toelichting:" in table
    assert "operationeel niet zinvol" in table


def test_harsh_role_language_is_not_rendered() -> None:
    en = final_action_table_from_rotation(_state(), {"PAVE": "Global X U.S. Infrastructure Development ETF"})
    nl = final_action_table_from_rotation_nl(_state(), {"PAVE": "Global X U.S. Infrastructure Development ETF"})
    assert "Portfolio role is impaired" not in en
    assert "Role under review" in en
    assert "Portefeuillerol is verzwakt" not in nl
    assert "Rol onder herbeoordeling" in nl
