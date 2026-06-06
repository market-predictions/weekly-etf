from __future__ import annotations

from pathlib import Path

from runtime.nl_localization import localize_text
from runtime.scrub_nl_client_language import scrub_text
from runtime import nl_terminology as term


def test_central_terminology_covers_dutch_enum_leak_regression() -> None:
    assert localize_text("No / under review", language="nl") == "Nee / onder herbeoordeling"
    assert localize_text("Smaller / under review", language="nl") == "Kleiner / onder herbeoordeling"
    assert localize_text("Hold but replaceable", language="nl") == "Aanhouden, maar vervangbaar"


def test_native_guard_only_scrub_uses_narrow_centralized_runtime_aliases() -> None:
    text = "| Better Alternative Exists? | Fresh cash |\n| No / under review | Smaller / under review |"
    scrubbed = scrub_text(text, native_dutch=True)
    assert "No / under review" not in scrubbed
    assert "Nee / onder herbeoordeling" in scrubbed
    assert "Kleiner / onder herbeoordeling" in scrubbed


def test_validators_import_shared_terminology_contract() -> None:
    assert "Review huidige posities" in term.REQUIRED_DUTCH_MARKERS
    assert "Executive Summary" in term.FORBIDDEN_CLIENT_LABELS
    assert "No" in term.ACTION_REPLACEMENTS
    assert term.ACTION_REPLACEMENTS["Under review"] == "Onder herbeoordeling"


def test_sitecustomize_does_not_own_client_surface_aliases() -> None:
    sitecustomize = Path("sitecustomize.py").read_text(encoding="utf-8")
    assert "Dutch client-facing enum/status terminology belongs" in sitecustomize
    assert "No / under review" not in sitecustomize
    assert "Nee / onder herbeoordeling" not in sitecustomize
