from runtime.scrub_nl_client_language import FORBIDDEN_AFTER_SCRUB, scrub_text


def test_native_dutch_replay_normalizes_passive_holds_without_weakening_guard() -> None:
    source = (
        "# Wekelijkse ETF-review\n\n"
        "## Kernsamenvatting\n"
        "De beslislaag onderscheidt passive holds van actieve herbeoordelingen.\n"
    )
    scrubbed = scrub_text(source, native_dutch=True)

    assert "passive holds" not in scrubbed.lower()
    assert "passief aangehouden posities" in scrubbed.lower()
    assert "passive holds" in FORBIDDEN_AFTER_SCRUB
