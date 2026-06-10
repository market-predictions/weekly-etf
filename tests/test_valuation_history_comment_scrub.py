from runtime.fix_report_output_contract import sanitize_valuation_history_comments


def test_sanitize_valuation_history_comments_removes_stale_ticker_carry_forward_text() -> None:
    text = "\n".join(
        [
            "Fresh five-of-six repricing; PPA carried forward",
            "Fresh five-of-six pricing recovery; GLD carried forward",
            "Verse herprijzing voor vijf van zes posities; PPA doorgeschoven",
            "Prijsherstel voor vijf van zes posities; goudpositie doorgeschoven",
        ]
    )

    cleaned = sanitize_valuation_history_comments(text)

    assert "Partial fresh repricing using latest verified marks" in cleaned
    assert "Partial pricing recovery using latest verified marks" in cleaned
    assert "Gedeeltelijke herprijzing op basis van laatst geverifieerde koersen" in cleaned
    assert "Gedeeltelijk prijsherstel op basis van laatst geverifieerde koersen" in cleaned
    assert "PPA carried forward" not in cleaned
    assert "GLD carried forward" not in cleaned
    assert "PPA doorgeschoven" not in cleaned
    assert "goudpositie doorgeschoven" not in cleaned
