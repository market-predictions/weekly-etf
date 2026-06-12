from __future__ import annotations

from runtime.wp16_followup3_cleanup import clean_text, failures


def test_wp16_followup3_keeps_english_regime_memory_english() -> None:
    text = "Risk-on growth has persisted for 24 run(s); transition state is stable, breadth is improving, and cross-asset confirmation is mixed."
    cleaned = clean_text(text, language="en")

    assert "Risk-on growth has persisted for 24 run(s)" in cleaned
    assert "Risk-on groei houdt" not in cleaned
    assert failures(cleaned, language="en") == []


def test_wp16_followup3_translates_dutch_regime_memory_only_for_dutch() -> None:
    text = "Risk-on growth has persisted for 24 run(s); transition state is stable, breadth is improving, and cross-asset confirmation is mixed."
    cleaned = clean_text(text, language="nl")

    assert "Risk-on growth has persisted" not in cleaned
    assert "Risk-on groei houdt al 24 runs aan" in cleaned
    assert failures(cleaned, language="nl") == []


def test_wp16_followup3_flags_removed_markdown_guard_marker() -> None:
    marker = "wp16-nl-equity-curve-guard"
    assert marker in failures(marker, language="en")
    assert marker in failures(marker, language="nl")
