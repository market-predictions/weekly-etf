from runtime.wp16_followup3_cleanup import clean_text, failures


def test_rotation_budget_constraint_is_client_safe_in_english() -> None:
    source = (
        "PAVE — Hold with override; override: rotation budget already used\n"
        "System override: Rotation budget for this run is already used"
    )

    cleaned = clean_text(source, language="en")

    assert "weekly rotation limit reached" in cleaned
    assert "Execution constraint: weekly rotation limit reached" in cleaned
    assert "rotatielimiet" not in cleaned.lower()
    assert "override" not in cleaned.lower()
    assert failures(cleaned, language="en") == []


def test_rotation_budget_constraint_is_client_safe_in_dutch() -> None:
    source = (
        "PAVE — Aanhouden met override; override: rotation budget already used\n"
        "System override: Rotation budget for this run is already used"
    )

    cleaned = clean_text(source, language="nl")

    assert "rotatielimiet bereikt voor deze review" in cleaned.lower()
    assert "Uitvoeringsbeperking: rotatielimiet bereikt voor deze review" in cleaned
    assert "weekly rotation limit" not in cleaned.lower()
    assert "override" not in cleaned.lower()
    assert failures(cleaned, language="nl") == []
