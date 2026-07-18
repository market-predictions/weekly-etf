from __future__ import annotations

from pathlib import Path

builder_path = Path("runtime/build_portfolio_close_first_review.py")
tests_path = Path("tests/test_portfolio_close_first_review.py")
validator_path = Path("tools/validate_portfolio_close_first_review.py")

builder = builder_path.read_text(encoding="utf-8")
old = '''    decision = evidence["decision"]
    source = decision.get("selected_source") or "None"
    destination = decision.get("selected_destination") or "cash"
    rows = "\\n".join'''
new = '''    decision = evidence["decision"]
    source = decision.get("selected_source") or "None"
    destination = decision.get("selected_destination") or "cash"
    conclusion_en = {
        "close_to_cash_supported": "Closing the selected source and retaining the proceeds as cash is supported by this review.",
        "close_and_reallocate_existing_supported": "Closing the selected source and reallocating to an existing holding is supported by this review.",
        "no_trade_insufficient_evidence": "Current evidence is insufficient to support a count-reducing action.",
    }[decision["conclusion"]]
    conclusion_nl = {
        "close_to_cash_supported": "Deze beoordeling ondersteunt sluiting van de geselecteerde bron en behoud van de opbrengst als cash.",
        "close_and_reallocate_existing_supported": "Deze beoordeling ondersteunt sluiting van de geselecteerde bron en herallocatie naar een bestaande positie.",
        "no_trade_insufficient_evidence": "Het huidige bewijs is onvoldoende voor een positie-aantal verlagende actie.",
    }[decision["conclusion"]]
    rows = "\\n".join'''
if old not in builder:
    raise RuntimeError("Render preamble not found")
builder = builder.replace(old, new, 1)
builder = builder.replace("**Conclusion:** {decision['conclusion']}", "**Review conclusion:** {conclusion_en}")
builder = builder.replace("**Conclusie:** {decision['conclusion']}", "**Conclusie van de beoordeling:** {conclusion_nl}")
builder_path.write_text(builder, encoding="utf-8")

tests = tests_path.read_text(encoding="utf-8")
old_test = '''    assert "separate authorization" in en
    assert "afzonderlijke toestemming" in nl
'''
new_test = '''    assert "Current evidence is insufficient" in en
    assert "Het huidige bewijs is onvoldoende" in nl
    assert "no_trade_insufficient_evidence" not in en
    assert "no_trade_insufficient_evidence" not in nl
    assert "separate authorization" in en
    assert "afzonderlijke toestemming" in nl
'''
if old_test not in tests:
    raise RuntimeError("Render test assertion block not found")
tests_path.write_text(tests.replace(old_test, new_test, 1), encoding="utf-8")

validator = validator_path.read_text(encoding="utf-8")
old_validator = '''    for language, surface in (("en", en), ("nl", nl)):
        assert surface.strip()
        leaked = [term for term in BLOCKED_SURFACE_TERMS if term in surface.lower()]
        assert not leaked, (language, leaked)
'''
new_validator = '''    for language, surface in (("en", en), ("nl", nl)):
        assert surface.strip()
        leaked = [term for term in BLOCKED_SURFACE_TERMS if term in surface.lower()]
        assert not leaked, (language, leaked)
        assert conclusion not in surface, (language, conclusion)
'''
if old_validator not in validator:
    raise RuntimeError("Validator surface block not found")
validator_path.write_text(validator.replace(old_validator, new_validator, 1), encoding="utf-8")
