from __future__ import annotations

from pathlib import Path

import pytest

from tools.validate_macro_narrative_client_surface import validate

FIXTURE_DIR = Path("fixtures/macro_narrative")


def test_macro_narrative_client_surface_accepts_safe_bilingual_candidate() -> None:
    validate(FIXTURE_DIR / "safe_shadow_candidate_en_nl.json")


@pytest.mark.parametrize(
    ("fixture_name", "expected_error"),
    [
        ("bad_predictive_language.json", "predictive_wording_detected"),
        ("bad_shadow_label_leakage.json", "blocked_internal_keys_present"),
        ("bad_dutch_parity.json", "meaning_drift_between_en_nl"),
    ],
)
def test_macro_narrative_client_surface_rejects_bad_fixtures(
    fixture_name: str,
    expected_error: str,
) -> None:
    with pytest.raises(RuntimeError, match=expected_error):
        validate(FIXTURE_DIR / fixture_name)
