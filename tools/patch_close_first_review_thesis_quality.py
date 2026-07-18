from __future__ import annotations

from pathlib import Path

BUILDER = Path("runtime/build_portfolio_close_first_review.py")
TESTS = Path("tests/test_portfolio_close_first_review.py")

old = '''        total_score = num(row.get("total_score"), num(card.get("total_score"), num(lane.get("total_score"), 3.0)))
        result[ticker] = {
            "ticker": ticker,
            "shares": int(round(num(row.get("shares")))),
            "current_weight_pct": num(row.get("current_weight_pct")),
            "portfolio_role": text(row.get("portfolio_role") or card.get("portfolio_role")),
            "conviction_tier": text(row.get("conviction_tier") or card.get("conviction_tier")),
            "total_score": round(total_score, 2),
'''
new = '''        holding_score = num(row.get("total_score"), num(card.get("total_score"), 3.0))
        lane_score = num(lane.get("total_score"), holding_score)
        decision_quality_score = min(holding_score, lane_score)
        result[ticker] = {
            "ticker": ticker,
            "shares": int(round(num(row.get("shares")))),
            "current_weight_pct": num(row.get("current_weight_pct")),
            "portfolio_role": text(row.get("portfolio_role") or card.get("portfolio_role")),
            "conviction_tier": text(row.get("conviction_tier") or card.get("conviction_tier")),
            "holding_score": round(holding_score, 2),
            "lane_score": round(lane_score, 2),
            "total_score": round(decision_quality_score, 2),
            "lane_evidence_summary": text(lane.get("evidence_summary")),
            "lane_why_now": text(lane.get("why_now")),
            "macro_freshness_note": text(lane.get("macro_freshness_note")),
'''
text = BUILDER.read_text(encoding="utf-8")
if old not in text:
    raise RuntimeError("Expected continuity-score block not found")
text = text.replace(old, new, 1)
text = text.replace("Continuity score", "Decision quality")
text = text.replace("Continuiteitsscore", "Besliskwaliteit")
BUILDER.write_text(text, encoding="utf-8")

addition = '''\n\ndef test_current_lane_score_sets_decision_quality_floor() -> None:\n    from runtime.build_portfolio_close_first_review import continuity_rows\n\n    state = {\n        "positions": [\n            {\n                "ticker": "URNM",\n                "shares": 48,\n                "current_weight_pct": 1.9,\n                "total_score": 3.7,\n            }\n        ]\n    }\n    lanes = {\n        "URNM": {\n            "total_score": 2.96,\n            "evidence_summary": "Nuclear fuel security remains structural.",\n            "why_now": "Timing is less urgent.",\n            "macro_freshness_note": "Strategic but weakly confirmed.",\n        }\n    }\n    row = continuity_rows(state, {}, lanes)["URNM"]\n    assert row["holding_score"] == 3.7\n    assert row["lane_score"] == 2.96\n    assert row["total_score"] == 2.96\n    assert row["lane_why_now"] == "Timing is less urgent."\n'''
tests = TESTS.read_text(encoding="utf-8")
marker = "def test_current_lane_score_sets_decision_quality_floor()"
if marker not in tests:
    TESTS.write_text(tests.rstrip() + addition + "\n", encoding="utf-8")
