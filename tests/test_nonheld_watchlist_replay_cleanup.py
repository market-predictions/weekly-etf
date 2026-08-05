from runtime.nonheld_watchlist_replay_cleanup import normalize_nonheld_watchlist_text


def test_english_ppa_replay_becomes_explicitly_non_held() -> None:
    source = "- PPA must justify itself before promotion."
    normalized = normalize_nonheld_watchlist_text(source, "en")

    assert "ppa must justify itself" not in normalized.lower()
    assert "non-held watchlist" in normalized.lower()


def test_dutch_ppa_replay_becomes_explicitly_non_held() -> None:
    source = "- PPA moet zich bewijzen voordat promotie mogelijk is."
    normalized = normalize_nonheld_watchlist_text(source, "nl")

    assert "ppa moet zich bewijzen" not in normalized.lower()
    assert "niet-aangehouden volglijst" in normalized.lower()


def test_reconstructed_english_radar_gets_explicit_nonheld_note() -> None:
    source = (
        "## 4. Structural Opportunity Radar\n\n"
        "| Theme | Primary ETF | Alternative |\n"
        "|---|---|---|\n"
        "| Defense | PPA | ITA |\n\n"
        "## 5. Key Risks / Invalidators\n"
    )
    normalized = normalize_nonheld_watchlist_text(source, "en")

    radar = normalized.split("## 5.", 1)[0].lower()
    assert "ppa" in radar
    assert "non-held" in radar
    assert "neither is a current portfolio position" in radar


def test_reconstructed_dutch_radar_gets_explicit_nonheld_note() -> None:
    source = (
        "## 4. Structurele kansenradar\n\n"
        "| Thema | Primaire ETF | Alternatief |\n"
        "|---|---|---|\n"
        "| Defensie | PPA | ITA |\n\n"
        "## 5. Belangrijkste risico’s / invalidaties\n"
    )
    normalized = normalize_nonheld_watchlist_text(source, "nl")

    radar = normalized.split("## 5.", 1)[0].lower()
    assert "ppa" in radar
    assert "niet-aangehouden" in radar
    assert "geen van beide is een huidige portefeuillepositie" in radar
