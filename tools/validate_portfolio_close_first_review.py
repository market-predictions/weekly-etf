from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_CONCLUSIONS = {
    "close_to_cash_supported",
    "close_and_reallocate_existing_supported",
    "no_trade_insufficient_evidence",
}
BLOCKED_SURFACE_TERMS = ("shadow", "engine", "workflow", "override", "guarded", "release score")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"Expected JSON object: {path}")
    return payload


def validate(evidence: dict[str, Any], en: str, nl: str, expected_close_date: str) -> None:
    assert evidence["schema_version"] == "portfolio_close_first_execution_review_v1"
    assert evidence["status"] == "validated_no_mutation_review"

    current = evidence["current_state"]
    assert current["active_count"] == 9
    assert current["maximum"] == 8
    current_tickers = set(current["tickers"])
    assert len(current_tickers) == 9

    snapshot = evidence["market_snapshot"]
    assert snapshot["source"] == "yfinance"
    assert snapshot["requested_close_date"] == expected_close_date
    assert snapshot["freshness_status"] == "complete"
    assert snapshot["missing_or_stale_tickers"] == []
    for ticker in snapshot["required_tickers"]:
        row = snapshot["rows"][ticker]
        assert row["status"] == "complete", (ticker, row)
        assert row["observed_price_date"] == expected_close_date, (ticker, row)
        assert row["close"] is not None

    ranking = evidence["ranking"]
    assert len(ranking) == 9
    ranked_tickers = [row["ticker"] for row in ranking]
    assert len(set(ranked_tickers)) == 9
    assert set(ranked_tickers) == current_tickers
    assert ranking == sorted(ranking, key=lambda row: (-row["close_priority_score"], row["ticker"]))
    for row in ranking:
        assert 0 <= row["close_priority_score"] <= 100
        assert 0 <= row["non_size_priority_score"] <= 100
        assert isinstance(row["independent_issue_families"], list)
        assert row["issue_family_count"] == len(row["independent_issue_families"])
        assert row["market"]["status"] == "complete"

    decision = evidence["decision"]
    conclusion = decision["conclusion"]
    assert conclusion in ALLOWED_CONCLUSIONS
    transition = decision["transition"]
    assert transition["passed"] is True
    assert transition["current_count"] == 9
    assert transition["opened_tickers"] == []

    proof = evidence["selection_proof"]
    assert proof["smallest_position_not_automatic"] is True

    if conclusion == "no_trade_insufficient_evidence":
        assert decision["selected_source"] == ""
        assert transition["projected_count"] == 9
    else:
        assert decision["selected_source"] == ranking[0]["ticker"]
        assert decision["selected_source"] in transition["closed_tickers"]
        assert transition["projected_count"] <= 8
        assert proof["selected_source_remains_top_without_size_points"] is True
        assert len(proof["selected_source_issue_families"]) >= 2
        if conclusion == "close_to_cash_supported":
            assert decision["selected_destination"] == ""
            assert decision["destination_shares_added"] == 0
        else:
            assert decision["selected_destination"] in current_tickers
            assert decision["selected_destination"] != decision["selected_source"]
            assert decision["destination_shares_added"] > 0

    boundary = evidence["authority_boundary"]
    assert boundary
    assert all(value is False for value in boundary.values())

    for language, surface in (("en", en), ("nl", nl)):
        assert surface.strip()
        leaked = [term for term in BLOCKED_SURFACE_TERMS if term in surface.lower()]
        assert not leaked, (language, leaked)
    assert "Official portfolio state was not changed" in en
    assert "De officiële portefeuille is niet gewijzigd" in nl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--english", required=True)
    parser.add_argument("--dutch", required=True)
    parser.add_argument("--expected-close-date", required=True)
    args = parser.parse_args()

    evidence = read_json(Path(args.evidence))
    en = Path(args.english).read_text(encoding="utf-8")
    nl = Path(args.dutch).read_text(encoding="utf-8")
    validate(evidence, en, nl, args.expected_close_date)
    print(
        "ETF_CLOSE_FIRST_REVIEW_VALIDATION_OK | "
        f"close_date={args.expected_close_date} | conclusion={evidence['decision']['conclusion']} | "
        f"source={evidence['decision']['selected_source'] or 'none'} | "
        f"projected_count={evidence['decision']['transition']['projected_count']} | "
        "portfolio_mutation=false | email_sent=false"
    )


if __name__ == "__main__":
    main()
