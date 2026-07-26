from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Patch anchor not found in {path}: {old[:120]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def apply() -> None:
    replace_once(
        "runtime/report_portfolio_integrity_contract.py",
        'def _conclusion_section(state: dict[str, Any], language: str) -> str:\n    if language == "nl":',
        '''def _conclusion_section(state: dict[str, Any], language: str) -> str:\n    if not _no_action(state):\n        if language == "nl":\n            return "\\n".join(\n                [\n                    "- **Portefeuillehouding:** voorgestelde of uitgevoerde wijzigingen worden uitsluitend door de autoritatieve actietabellen bepaald.",\n                    "- **Best onderbouwde blootstelling:** SMH blijft structureel sterk, maar concentratie- en positielimieten blijven bindend.",\n                    "- **Belangrijkste disciplinepunt:** iedere mutatie moet de positiecapaciteit verbeteren en de prijs-, relatieve-sterkte- en thesistoets doorstaan.",\n                    "- **Volglijstscheiding:** PPA en ITA blijven niet-aangehouden defensie-instrumenten totdat een afzonderlijke, geldige allocatiebeslissing bestaat.",\n                ]\n            )\n        return "\\n".join(\n            [\n                "- **Portfolio stance:** proposed or executed changes are determined only by the authoritative action tables.",\n                "- **Best-supported exposure:** SMH remains structurally strong, but concentration and position limits remain binding.",\n                "- **Main discipline point:** every transition must improve portfolio capacity and pass pricing, relative-strength and thesis review.",\n                "- **Watchlist separation:** PPA and ITA remain non-held defense instruments until a separate valid allocation decision exists.",\n            ]\n        )\n    if language == "nl":''',
    )
    replace_once(
        "runtime/report_portfolio_integrity_contract.py",
        '''    for old, new in replacements.items():\n        text = text.replace(old, new)\n\n    duplicate_patterns = [''',
        '''    for old, new in replacements.items():\n        text = text.replace(old, new)\n    if language == "nl":\n        text = text.replace(\n            "SPY-relative performance",\n            "prestaties tegenover de SPY-marktbenchmark",\n        )\n        text = text.replace(\n            "SPY-relatieve performance",\n            "prestaties tegenover de SPY-marktbenchmark",\n        )\n    else:\n        text = text.replace(\n            "SPY-relative performance",\n            "performance versus the SPY market benchmark",\n        )\n\n    duplicate_patterns = [''',
    )

    replace_once(
        "runtime/regime_memory.py",
        "from datetime import datetime",
        "from datetime import date, datetime",
    )
    replace_once(
        "runtime/regime_memory.py",
        '''def _cross_asset_status(pack: dict[str, Any]) -> str:\n    signals = pack.get("macro_signals") or {}''',
        '''def _calendar_observations(last_major_shift: Any, report_date: str) -> int:\n    try:\n        start = date.fromisoformat(str(last_major_shift)[:10])\n        end = date.fromisoformat(report_date[:10])\n    except (TypeError, ValueError):\n        return 1\n    if end < start:\n        return 1\n    return max((end - start).days // 7 + 1, 1)\n\n\ndef _cross_asset_status(pack: dict[str, Any]) -> str:\n    signals = pack.get("macro_signals") or {}''',
    )
    replace_once(
        "runtime/regime_memory.py",
        '''    regime_changed = previous_regime not in {"", "Unknown"} and previous_regime != current_regime\n    if regime_changed:\n        new_weeks = 1\n        last_major_shift = report_date\n        failed_rotation_count = int(previous.get("failed_rotation_count") or 0)\n    else:\n        new_weeks = weeks_in_regime + 1 if weeks_in_regime else 1\n        last_major_shift = previous.get("last_major_shift") or report_date\n        failed_rotation_count = int(previous.get("failed_rotation_count") or 0)''',
        '''    regime_changed = previous_regime not in {"", "Unknown"} and previous_regime != current_regime\n    previous_report_date = str(previous.get("report_date") or "")\n    if regime_changed:\n        new_weeks = 1\n        last_major_shift = report_date\n        failed_rotation_count = int(previous.get("failed_rotation_count") or 0)\n    else:\n        last_major_shift = previous.get("last_major_shift") or report_date\n        calendar_count = _calendar_observations(last_major_shift, report_date)\n        if previous_report_date == report_date:\n            new_weeks = min(weeks_in_regime or 1, calendar_count)\n        else:\n            new_weeks = calendar_count\n        failed_rotation_count = int(previous.get("failed_rotation_count") or 0)''',
    )
    replace_once(
        "runtime/regime_memory.py",
        '"Do not rotate aggressively unless a regime shift persists for at least two runs or cross-asset confirmation becomes broad."',
        '"Do not rotate aggressively unless a regime shift persists across at least two distinct report dates or cross-asset confirmation becomes broad."',
    )
    replace_once(
        "runtime/regime_memory.py",
        'f"{regime} has persisted for {weeks} run(s); transition state is {transition}, "',
        'f"{regime} has persisted across {weeks} weekly observation(s); transition state is {transition}, "',
    )

    replace_once(
        "runtime/build_macro_policy_pack.py",
        'ECB_JUNE_2026_HIKE_DATE = "2026-06-11"',
        'ECB_JUNE_2026_HIKE_DATE = "2026-06-11"\nECB_JULY_2026_HOLD_DATE = "2026-07-23"',
    )
    replace_once(
        "runtime/build_macro_policy_pack.py",
        '''def _ecb_june_2026_hike_applies(report_date: str | None) -> bool:\n    report = _date_or_none(report_date)\n    hike = _date_or_none(ECB_JUNE_2026_HIKE_DATE)\n    return bool(report and hike and report >= hike)''',
        '''def _ecb_june_2026_hike_applies(report_date: str | None) -> bool:\n    report = _date_or_none(report_date)\n    hike = _date_or_none(ECB_JUNE_2026_HIKE_DATE)\n    return bool(report and hike and report >= hike)\n\n\ndef _ecb_july_2026_hold_applies(report_date: str | None) -> bool:\n    report = _date_or_none(report_date)\n    hold = _date_or_none(ECB_JULY_2026_HOLD_DATE)\n    return bool(report and hold and report >= hold)''',
    )
    replace_once(
        "runtime/build_macro_policy_pack.py",
        '''    if _ecb_june_2026_hike_applies(report_date):\n        ecb = {\n            "stance": "Tightening / inflation-sensitive",\n            "likely_direction": "Following the 11 June 2026 rate increase, the next step remains data- and inflation-dependent.",\n            "main_risk": "Renewed energy-led inflation pressure can raise the hurdle for rate-sensitive and non-U.S. developed-market exposure.",\n            "etf_implication": "IEFA exposure is now present, but further non-U.S. developed allocations still require relative-strength, pricing and portfolio-discipline confirmation.",\n            "confidence": 0.70,\n            "event_date": ECB_JUNE_2026_HIKE_DATE,\n            "event_status": "verified_report_week_policy_event",\n        }''',
        '''    if _ecb_july_2026_hold_applies(report_date):\n        ecb = {\n            "stance": "On hold after June tightening / data-dependent",\n            "likely_direction": "The ECB kept its key interest rates unchanged on 23 July 2026 and retained a meeting-by-meeting, data-dependent approach.",\n            "main_risk": "Renewed inflation pressure or weaker growth can change the relative-strength hurdle for developed-market exposure outside the United States.",\n            "etf_implication": "IEFA exposure is already material; further allocation still requires relative-strength, pricing and portfolio-concentration confirmation.",\n            "confidence": 0.75,\n            "event_date": ECB_JULY_2026_HOLD_DATE,\n            "event_status": "verified_latest_policy_decision",\n        }\n    elif _ecb_june_2026_hike_applies(report_date):\n        ecb = {\n            "stance": "Tightening / inflation-sensitive",\n            "likely_direction": "Following the 11 June 2026 rate increase, the next step remains data- and inflation-dependent.",\n            "main_risk": "Renewed energy-led inflation pressure can raise the hurdle for rate-sensitive and non-U.S. developed-market exposure.",\n            "etf_implication": "IEFA exposure is now present, but further non-U.S. developed allocations still require relative-strength, pricing and portfolio-discipline confirmation.",\n            "confidence": 0.70,\n            "event_date": ECB_JUNE_2026_HIKE_DATE,\n            "event_status": "verified_historical_policy_event",\n        }''',
    )
    replace_once(
        "runtime/build_macro_policy_pack.py",
        '''    if _event_is_in_report_week(report_date, ECB_JUNE_2026_HIKE_DATE):\n        catalysts.insert(''',
        '''    if _event_is_in_report_week(report_date, ECB_JULY_2026_HOLD_DATE):\n        catalysts.insert(\n            0,\n            {\n                "policy_area": "ECB rate-policy hold",\n                "latest_signal": "The ECB kept its key interest rates unchanged on 23 July 2026 and retained a data-dependent, meeting-by-meeting approach; this is descriptive policy context and does not override portfolio gates.",\n                "affected_lanes": ["Non-U.S. developed diversification", "Rate-sensitive small caps", "Long-duration bonds"],\n                "direction": "on hold / data-dependent",\n                "time_horizon": "1-6 months",\n                "confidence": 0.75,\n                "event_date": ECB_JULY_2026_HOLD_DATE,\n                "event_status": "verified_report_week_policy_event",\n                "transfer_to_report": True,\n            },\n        )\n    elif _event_is_in_report_week(report_date, ECB_JUNE_2026_HIKE_DATE):\n        catalysts.insert(''',
    )

    replace_once(
        "runtime/persist_etf_valuation_state.py",
        '''    fx = _fx_rate_full(runtime_state)\n    cash = round(_float(existing_state.get("cash_eur"), _float((runtime_state.get("portfolio") or {}).get("cash_eur"))), 2)''',
        '''    fx = _fx_rate_full(runtime_state)\n    current_run_id = _text(runtime_state.get("run_id"))\n    last_execution_run_id = _text((existing_state.get("last_model_execution") or {}).get("run_id"))\n    reset_historical_execution_fields = bool(\n        current_run_id and last_execution_run_id and current_run_id != last_execution_run_id\n    )\n    cash = round(_float(existing_state.get("cash_eur"), _float((runtime_state.get("portfolio") or {}).get("cash_eur"))), 2)''',
    )
    replace_once(
        "runtime/persist_etf_valuation_state.py",
        '''        item.update(\n            {\n                "ticker": ticker,''',
        '''        if reset_historical_execution_fields:\n            item["shares_delta_this_run"] = 0.0\n            item["weight_change_pct"] = 0.0\n            item["action_executed_this_run"] = "None"\n            item["funding_source_note"] = "No model trade executed this run."\n\n        item.update(\n            {\n                "ticker": ticker,''',
    )
    replace_once(
        "runtime/persist_etf_valuation_state.py",
        '''    return {\n        "date": report_date,''',
        '''    pricing_statuses = {\n        str(row.get("pricing_status") or "")\n        for row in (runtime_state.get("positions") or [])\n        if str(row.get("ticker") or "").upper() != "CASH"\n    }\n    all_fresh = bool(pricing_statuses) and pricing_statuses.issubset({\n        "fresh_close",\n        "fresh_fallback_source",\n        "fresh_exact_close",\n        "fresh_exact_unverified",\n    })\n    valuation_comment = (\n        "Portfolio valuation based on confirmed closing prices and official holdings"\n        if all_fresh\n        else "Portfolio valuation based on official holdings with unresolved prices carried under the pricing contract"\n    )\n\n    return {\n        "date": report_date,''',
    )
    replace_once(
        "runtime/persist_etf_valuation_state.py",
        '"comment": "Runtime valuation repriced from official portfolio-state shares",',
        '"comment": valuation_comment,',
    )


if __name__ == "__main__":
    apply()
    print("ETF_REPORT_INTEGRITY_SOURCE_PATCH_OK")
