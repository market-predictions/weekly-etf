from __future__ import annotations

from runtime.wp16_followup3_cleanup import clean_text, failures


def test_wp16_followup9_repairs_ishares_product_name_corruption() -> None:
    text = "GSG — iAantal aandelen S&P GSCI Commodity-Indexed Trust"

    cleaned = clean_text(text, language="nl")

    assert "iShares S&P GSCI Commodity-Indexed Trust" in cleaned
    assert "iAantal aandelen" not in cleaned
    assert failures(cleaned, language="nl") == []


def test_wp16_followup9_flags_unrepaired_ishares_corruption() -> None:
    text = "GSG — iAantal aandelen S&P GSCI Commodity-Indexed Trust"

    assert "iaantal aandelen" in failures(text, language="nl")
