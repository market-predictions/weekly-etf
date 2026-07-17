from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.position_count_contract import (
    DEFAULT_MAX_ACTIVE_POSITIONS,
    assess_current_positions,
    client_breach_sentence,
)
from runtime.wp16_followup3_cleanup import _active_report_tickers, clean_text


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(
    *,
    portfolio_state_path: Path,
    english_report_path: Path,
    dutch_report_path: Path,
    trade_ledger_path: Path,
    valuation_history_path: Path,
    evidence_path: Path,
    max_active_positions: int = DEFAULT_MAX_ACTIVE_POSITIONS,
) -> Path:
    required = [
        portfolio_state_path,
        english_report_path,
        dutch_report_path,
        trade_ledger_path,
        valuation_history_path,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError("Missing required position-count validation inputs: " + ", ".join(missing))

    protected = [portfolio_state_path, trade_ledger_path, valuation_history_path]
    before_hashes = {str(path): _sha256(path) for path in protected}
    report_before_hashes = {
        str(english_report_path): _sha256(english_report_path),
        str(dutch_report_path): _sha256(dutch_report_path),
    }

    portfolio_state = _read_json(portfolio_state_path)
    assessment = assess_current_positions(
        portfolio_state.get("positions", []) or [],
        max_active_positions=max_active_positions,
    )
    if not assessment.passed:
        raise RuntimeError("Official portfolio state is invalid: " + "; ".join(assessment.errors))
    if assessment.status != "close_first":
        raise RuntimeError(
            "Expected the current official state to require close-first reconciliation; "
            f"received status={assessment.status}, count={assessment.current_count}"
        )

    languages: dict[str, dict[str, Any]] = {}
    for language, path in (("en", english_report_path), ("nl", dutch_report_path)):
        original = path.read_text(encoding="utf-8")
        report_tickers = _active_report_tickers(original, language)
        if report_tickers != assessment.current_tickers:
            raise RuntimeError(
                f"{language} report active tickers {report_tickers} do not match official state {assessment.current_tickers}"
            )
        cleaned = clean_text(original, language=language)
        expected = client_breach_sentence(
            current_count=assessment.current_count,
            max_active_positions=max_active_positions,
            language=language,
        )
        if not expected or expected not in cleaned:
            raise RuntimeError(f"{language} report cleanup did not expose the position-count breach")
        if clean_text(cleaned, language=language) != cleaned:
            raise RuntimeError(f"{language} position-count client surface is not idempotent")
        languages[language] = {
            "source_path": str(path),
            "source_sha256": report_before_hashes[str(path)],
            "active_tickers": list(report_tickers),
            "active_position_count": len(report_tickers),
            "expected_client_sentence": expected,
            "client_sentence_present_after_in_memory_cleanup": True,
            "source_file_mutated": False,
            "cleanup_idempotent": True,
        }

    after_hashes = {str(path): _sha256(path) for path in protected}
    report_after_hashes = {
        str(english_report_path): _sha256(english_report_path),
        str(dutch_report_path): _sha256(dutch_report_path),
    }
    if before_hashes != after_hashes:
        raise RuntimeError("Protected authority files changed during read-only position-count validation")
    if report_before_hashes != report_after_hashes:
        raise RuntimeError("Historical report inputs changed during read-only position-count validation")

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "weekly_etf_position_count_constraint_reconciliation_evidence",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "package": "WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION",
        "status": "validated_no_send",
        "decision": {
            "every_non_zero_position_counts": True,
            "generic_residual_exception": False,
            "max_active_positions": max_active_positions,
            "current_active_positions": assessment.current_count,
            "current_status": assessment.status,
            "new_ticker_while_over_limit": "blocked",
            "new_ticker_at_limit": "requires_full_source_close_same_execution",
        },
        "official_state": {
            "path": str(portfolio_state_path),
            "active_tickers": list(assessment.current_tickers),
            "warnings": list(assessment.warnings),
            "portfolio_state_mutation": False,
            "trade_ledger_mutation": False,
            "valuation_history_mutation": False,
        },
        "client_surfaces": languages,
        "protected_authority_hashes_before": before_hashes,
        "protected_authority_hashes_after": after_hashes,
        "protected_authority_hashes_identical": True,
        "historical_report_hashes_before": report_before_hashes,
        "historical_report_hashes_after": report_after_hashes,
        "historical_reports_byte_unchanged": True,
        "portfolio_execution": False,
        "email_sent": False,
    }

    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ETF_POSITION_COUNT_CONTRACT_OK | "
        f"status={assessment.status} | active={assessment.current_count}/{max_active_positions} | "
        f"tickers={','.join(assessment.current_tickers)} | evidence={evidence_path} | "
        "authority_mutation=false | email_sent=false"
    )
    return evidence_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the ETF position-count contract without mutating authority files.")
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_portfolio_state.json"))
    parser.add_argument("--english-report", type=Path, default=Path("output/weekly_analysis_pro_260716_02.md"))
    parser.add_argument("--dutch-report", type=Path, default=Path("output/weekly_analysis_pro_nl_260716_02.md"))
    parser.add_argument("--trade-ledger", type=Path, default=Path("output/etf_trade_ledger.csv"))
    parser.add_argument("--valuation-history", type=Path, default=Path("output/etf_valuation_history.csv"))
    parser.add_argument("--evidence", type=Path, default=Path("/tmp/etf_position_count_contract_evidence.json"))
    parser.add_argument("--max-active-positions", type=int, default=DEFAULT_MAX_ACTIVE_POSITIONS)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    validate(
        portfolio_state_path=args.portfolio_state,
        english_report_path=args.english_report,
        dutch_report_path=args.dutch_report,
        trade_ledger_path=args.trade_ledger,
        valuation_history_path=args.valuation_history,
        evidence_path=args.evidence,
        max_active_positions=args.max_active_positions,
    )


if __name__ == "__main__":
    main()
