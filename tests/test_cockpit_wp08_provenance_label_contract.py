from runtime.build_cockpit_side_by_side_review import _dutch_provenance_status


def test_wp08_accepts_legacy_dutch_provenance_status_labels() -> None:
    text = "Geen deliveryclaim; Niet gepromoveerd naar productie"
    assert _dutch_provenance_status(text) == (True, True)


def test_wp08_accepts_natural_dutch_provenance_status_labels() -> None:
    text = "Geen leveringsclaim; Niet naar productie gepromoveerd"
    assert _dutch_provenance_status(text) == (True, True)


def test_wp08_requires_both_dutch_provenance_statuses() -> None:
    assert _dutch_provenance_status("Geen leveringsclaim") == (True, False)
    assert _dutch_provenance_status("Niet naar productie gepromoveerd") == (False, True)
