from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Patch anchor not found in {path}: {old[:160]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def apply() -> None:
    replace_once(
        "runtime/etf_instrument_constraints.py",
        '''            decision["reason_codes"] = reasons\n\n    plan["target_weights"] = [''',
        '''            decision["reason_codes"] = reasons\n\n    # A blocked transition can invalidate the only proposed rotation. Any later\n    # decision marked as having consumed that rotation budget is then stale: no\n    # valid trade intent survived the portfolio constraints. Normalize it to the\n    # same blocking authority so the client surface cannot claim that a rotation\n    # was used when the final plan contains zero trades.\n    for decision in plan.get("rotation_decisions", []) or []:\n        if str(decision.get("override_reason_code") or "") != "churn_budget_used":\n            continue\n        decision["action_code"] = "hold_with_override"\n        decision["override_status"] = "engine"\n        decision["override_reason_code"] = "portfolio_constraint_blocked"\n        reasons = list(decision.get("reason_codes") or [])\n        if reason_code not in reasons:\n            reasons.append(reason_code)\n        decision["reason_codes"] = reasons\n\n    plan["target_weights"] = [''',
    )

    replace_once(
        "tools/validate_etf_rotation_output_contract.py",
        '''    trades = plan.get("trade_intents") or []\n    for idx, trade in enumerate(trades):''',
        '''    trades = plan.get("trade_intents") or []\n    constraint_validation = plan.get("portfolio_constraint_validation") or {}\n    if not trades and constraint_validation.get("block_reason"):\n        stale_churn = [\n            str(row.get("ticker") or "")\n            for row in decisions\n            if str(row.get("override_reason_code") or "") == "churn_budget_used"\n        ]\n        if stale_churn:\n            failures.append(\n                "zero-trade constrained plan retains stale churn_budget_used for: "\n                + ", ".join(sorted(stale_churn))\n            )\n    for idx, trade in enumerate(trades):''',
    )

    replace_once(
        "runtime/render_etf_report_nl_from_state.py",
        '''        "Latest 4 May close basis; +8 SMH executed from cash": "Laatste slotkoersbasis van 4 mei; +8 SMH uitgevoerd vanuit cash",\n    }''',
        '''        "Latest 4 May close basis; +8 SMH executed from cash": "Laatste slotkoersbasis van 4 mei; +8 SMH uitgevoerd vanuit cash",\n        "Portfolio valuation based on confirmed prices and official holdings": "Waardering op basis van bevestigde slotkoersen en officiële posities",\n        "Portfolio valuation based on confirmed closing prices and official holdings": "Waardering op basis van bevestigde slotkoersen en officiële posities",\n        "Runtime valuation repriced from official portfolio-state shares": "Waardering op basis van bevestigde slotkoersen en officiële posities",\n    }''',
    )
    replace_once(
        "runtime/render_etf_report_nl_from_state.py",
        '''    if report_date:\n        points[report_date] = {"date": report_date, "nav_eur": total_nav(state), "comment": "Doorgeschoven waardering uit prijsaudit en expliciete portefeuillestaat"}''',
        '''    if report_date:\n        fresh_statuses = {\n            str(row.get("pricing_status") or "")\n            for row in position_rows(state)\n        }\n        all_fresh = bool(fresh_statuses) and fresh_statuses.issubset({\n            "fresh_close",\n            "fresh_fallback_source",\n            "fresh_exact_close",\n            "fresh_exact_unverified",\n        })\n        comment = (\n            "Waardering op basis van bevestigde slotkoersen en officiële posities"\n            if all_fresh\n            else "Waardering op basis van officiële posities met onopgeloste koersen volgens het prijscontract"\n        )\n        points[report_date] = {"date": report_date, "nav_eur": total_nav(state), "comment": comment}''',
    )

    replace_once(
        ".github/workflows/send-weekly-report.yml",
        '''          python -m runtime.link_runtime_report_tickers --output-dir output\n          python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output''',
        '''          python -m runtime.link_runtime_report_tickers --output-dir output\n          python tools/validate_etf_report_portfolio_integrity.py --output-dir output\n          python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output''',
    )


if __name__ == "__main__":
    apply()
    print("ETF_ZERO_TRADE_AND_NL_HISTORY_FIX_OK")
