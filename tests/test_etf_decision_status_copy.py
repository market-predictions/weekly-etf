from runtime.wp16_followup3_cleanup import clean_text, failures


def test_english_reflected_rotation_boilerplate_is_state_neutral() -> None:
    source = (
        "Rotation execution status\n"
        "portfolio rotation is already reflected in the official portfolio state and trade ledger; "
        "this run performed no duplicate state or ledger mutation."
    )

    cleaned = clean_text(source, language="en")

    assert "Portfolio decision status" in cleaned
    assert "The official portfolio state and trade ledger are authoritative for this report" in cleaned
    assert "rotation is already reflected" not in cleaned.lower()
    assert failures(cleaned, language="en") == []


def test_dutch_reflected_rotation_boilerplate_is_state_neutral() -> None:
    source = (
        "Status rotatie-uitvoering\n"
        "De bewaakte modelrotatie is al verwerkt in de officiële portefeuillestaat en het handelslogboek; "
        "deze run heeft geen dubbele staat- of handelslogboekmutatie uitgevoerd."
    )

    cleaned = clean_text(source, language="nl")

    assert "Status portefeuillebesluit" in cleaned
    assert "De officiële portefeuillestaat en het handelslogboek zijn leidend voor dit rapport" in cleaned
    assert "rotatie is al verwerkt" not in cleaned.lower()
    assert failures(cleaned, language="nl") == []
