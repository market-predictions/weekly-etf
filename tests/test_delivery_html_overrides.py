from runtime.delivery_html_overrides import _post_execution_pairs, _trade_summary_html


class _Base:
    def ticker_anchor_html(self, ticker: str) -> str:
        return ticker


def test_post_execution_best_replacements_note_uses_executed_pair_not_stale_gld():
    state = {
        "execution_context": {"report_phase": "post_execution"},
        "positions": [
            {
                "ticker": "SPY",
                "action_executed_this_run": "Sell",
                "funding_source_note": "Guarded auto-execution: reduce SPY to fund IEFA.",
            },
            {
                "ticker": "IEFA",
                "action_executed_this_run": "Buy",
                "funding_source_note": "Guarded auto-execution: buy IEFA funded by SPY.",
            },
            {
                "ticker": "GSG",
                "action_executed_this_run": "None",
                "funding_source_note": "No model trade executed this run.",
            },
        ],
    }

    assert _post_execution_pairs(state) == ["SPY→IEFA"]
    note = _trade_summary_html(_Base(), state, "en")

    assert "SPY" in note
    assert "IEFA" in note
    assert "GLD" not in note
    assert "GSG" not in note
