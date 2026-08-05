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
