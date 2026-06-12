from __future__ import annotations

from runtime.add_etf_position_performance_section import _fmt_eur, _fmt_pct
from runtime.build_macro_policy_pack import central_banks_for_regime, policy_catalysts
from runtime.client_facing_sanitizer import sanitize_client_facing_html
from runtime.macro_report_surface import dashboard_en, dashboard_nl
from runtime.scrub_etf_client_surface import CANONICAL_CONSTRAINT_LINES, scrub_text


def test_wp16_ecb_hike_is_surfaced_after_20260611() -> None:
    banks = central_banks_for_regime("Risk-on growth", "2026-06-11")
    assert banks["ecb"]["stance"] == "Tightening / inflation-sensitive"
    assert banks["ecb"]["event_status"] == "verified_report_week_policy_event"

    catalysts = policy_catalysts({}, "2026-06-11")
    assert catalysts[0]["policy_area"] == "ECB rate-policy tightening"
    assert catalysts[0]["transfer_to_report"] is True


def test_wp16_macro_surface_renders_ecb_policy_event_bilingually() -> None:
    pack = {
        "regime": {"current": "Risk-on growth", "confidence": 0.66, "what_changed": ["AI / semiconductor leadership remains the dominant equity impulse."]},
        "regime_memory": {"report_transfer": {"summary": "Risk-on growth has persisted for 22 run(s); transition state is stable, breadth is improving, and cross-asset confirmation is mixed."}, "decision_rule": "Do not rotate aggressively unless a regime shift persists for at least two runs or cross-asset confirmation becomes broad."},
        "central_banks": central_banks_for_regime("Risk-on growth", "2026-06-11"),
        "policy_catalysts": policy_catalysts({}, "2026-06-11"),
        "portfolio_implications": ["Risk appetite is supportive, but fresh adds still need position-size room and pricing confirmation."],
        "report_transfer": {"max_policy_catalysts": 3},
    }
    state = {"macro_policy_pack": pack}

    en = dashboard_en(state)
    nl = dashboard_nl(state)

    assert "ECB stance: Tightening / inflation-sensitive" in en
    assert "ECB rate-policy tightening" in en
    assert "ECB-houding: Verkrappend / inflatiegevoelig" in nl
    assert "ECB-renteverkrapping" in nl


def test_wp16_scrub_removes_empty_comment_and_stale_non_us_wording() -> None:
    marker = "<!" + "-- --" + ">"
    escaped_marker = "&lt;!" + "-- --" + "&gt;"
    text = marker + "\n" + escaped_marker + "\nZero non-U.S. equity exposure is an implicit U.S.-exceptionalism bet.\n"
    cleaned = scrub_text(text)
    assert marker not in cleaned
    assert escaped_marker not in cleaned
    assert "Zero non-U.S. equity exposure" not in cleaned


def test_wp16_delivery_html_sanitizer_removes_escaped_empty_comment() -> None:
    escaped_marker = "&lt;!" + "-- --" + "&gt;"
    html = f"<div><h3>Vervangingsanalyse</h3><p>{escaped_marker}</p></div>"
    cleaned = sanitize_client_facing_html(html, md_text="## 4. Beste nieuwe kansen\nVervangingsanalyse", language="nl")
    assert escaped_marker not in cleaned
    assert "<p></p>" not in cleaned


def test_wp16_constraint_copy_scrub_is_idempotent() -> None:
    english = "- " + CANONICAL_CONSTRAINT_LINES["en_position_size"] + " soft cap; current inherited overweights require no-fresh-cash and review/trim discipline"
    dutch = "- " + CANONICAL_CONSTRAINT_LINES["nl_position_size"] + " zachte bovengrens; bestaande overwegingen krijgen geen nieuw kapitaal en blijven onder verklein-/reviewdiscipline"

    cleaned = scrub_text("\n".join([english, dutch]))

    assert cleaned.count("soft cap") == 1
    assert cleaned.count("zachte bovengrens") == 1
    assert CANONICAL_CONSTRAINT_LINES["en_position_size"] in cleaned
    assert CANONICAL_CONSTRAINT_LINES["nl_position_size"] in cleaned


def test_wp16_english_performance_uses_english_na_label() -> None:
    assert _fmt_pct(None, language="en") == "n/a"
    assert _fmt_eur(None, language="en") == "n/a"
    assert _fmt_pct(None, language="nl") == "n.v.t."
    assert _fmt_eur(None, language="nl") == "n.v.t."
