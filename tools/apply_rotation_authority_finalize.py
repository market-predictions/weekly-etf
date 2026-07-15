from pathlib import Path

root = Path('.')
auth = root / 'runtime/rotation_state_authority.py'
v2 = root / 'runtime/portfolio_rotation_engine_v2.py'
tests = root / 'tests/test_etf_rotation_state_authority.py'

text = auth.read_text(encoding='utf-8')
text = text.replace('import csv\nfrom pathlib import Path', 'import csv\nimport json\nfrom pathlib import Path')
text = text.replace(
    'PRICED_VALUATION_STATUSES = {\n',
    'DEFAULT_TRADE_LEDGER = Path("output/etf_trade_ledger.csv")\n'
    'DEFAULT_RUNTIME_DIR = Path("output/runtime")\n\n'
    'PRICED_VALUATION_STATUSES = {\n',
    1,
)
marker = '''def build_current_run_valuation_state(\n    portfolio_state: dict[str, Any], pricing_audit: dict[str, Any]\n) -> dict[str, Any]:\n'''
insert = '''def _execution_artifact_path(source_report: str, runtime_dir: Path) -> Path | None:\n    raw = str(source_report or "").strip()\n    if not raw.startswith("runtime:"):\n        return None\n    source_name = Path(raw.removeprefix("runtime:")).name\n    if not source_name.startswith("etf_report_state_"):\n        return None\n    return runtime_dir / source_name.replace(\n        "etf_report_state_", "etf_model_execution_", 1\n    )\n\n\ndef _execution_positions(payload: dict[str, Any]) -> list[dict[str, Any]]:\n    rows: list[dict[str, Any]] = []\n    for key in ("executed_positions", "shadow_positions", "positions"):\n        value = payload.get(key)\n        if isinstance(value, list):\n            rows.extend(row for row in value if isinstance(row, dict))\n    for key in ("post_trade_portfolio", "post_trade_shadow_portfolio", "result"):\n        nested = payload.get(key)\n        if not isinstance(nested, dict):\n            continue\n        value = nested.get("positions")\n        if isinstance(value, list):\n            rows.extend(row for row in value if isinstance(row, dict))\n    return rows\n\n\ndef reconstruct_average_entry_local(\n    symbol: str,\n    trade_ledger_path: Path = DEFAULT_TRADE_LEDGER,\n    runtime_dir: Path = DEFAULT_RUNTIME_DIR,\n) -> float | None:\n    if not trade_ledger_path.exists():\n        return None\n    lots: list[tuple[float, float]] = []\n    with trade_ledger_path.open("r", encoding="utf-8", newline="") as handle:\n        for ledger_row in csv.DictReader(handle):\n            if ticker(ledger_row.get("ticker")) != ticker(symbol):\n                continue\n            shares_delta = number(ledger_row.get("shares_delta"))\n            if shares_delta is None or shares_delta <= 0:\n                continue\n            artifact_path = _execution_artifact_path(\n                str(ledger_row.get("source_report") or ""), runtime_dir\n            )\n            if artifact_path is None or not artifact_path.exists():\n                continue\n            try:\n                payload = json.loads(artifact_path.read_text(encoding="utf-8"))\n            except (OSError, json.JSONDecodeError):\n                continue\n            matching = [\n                row\n                for row in _execution_positions(payload)\n                if ticker(row.get("ticker")) == ticker(symbol)\n            ]\n            if not matching:\n                continue\n            positive = [\n                row\n                for row in matching\n                if (number(row.get("shares_delta_this_run"), 0.0) or 0.0) > 0\n            ]\n            selected = positive[0] if positive else matching[0]\n            execution_price = number(\n                selected.get("selected_close"),\n                number(selected.get("current_price_local")),\n            )\n            if execution_price is None or execution_price <= 0:\n                continue\n            lots.append((shares_delta, execution_price))\n    total_shares = sum(shares for shares, _ in lots)\n    if total_shares <= 0:\n        return None\n    return round(\n        sum(shares * price for shares, price in lots) / total_shares, 6\n    )\n\n\n'''
if marker not in text:
    raise SystemExit('build marker not found')
text = text.replace(marker, insert + '''def build_current_run_valuation_state(\n    portfolio_state: dict[str, Any],\n    pricing_audit: dict[str, Any],\n    *,\n    trade_ledger_path: Path = DEFAULT_TRADE_LEDGER,\n    runtime_dir: Path = DEFAULT_RUNTIME_DIR,\n) -> dict[str, Any]:\n''', 1)
old = '''        pnl = recompute_pnl_pct(price, row.get("avg_entry_local"))\n        row.update(\n'''
new = '''        avg_entry = number(row.get("avg_entry_local"))\n        avg_entry_source = "portfolio_state"\n        if avg_entry is None or avg_entry <= 0:\n            avg_entry = reconstruct_average_entry_local(\n                symbol,\n                trade_ledger_path=trade_ledger_path,\n                runtime_dir=runtime_dir,\n            )\n            avg_entry_source = "model_execution_history"\n        if avg_entry is None or avg_entry <= 0:\n            errors.append(f"{symbol}:missing_average_entry_authority")\n            continue\n        pnl = recompute_pnl_pct(price, avg_entry)\n        row.update(\n'''
if old not in text:
    raise SystemExit('pnl marker not found')
text = text.replace(old, new, 1)
text = text.replace(
    '                "selected_close": price,\n                "pnl_pct": pnl,\n                "pnl_basis": "current_close_vs_avg_entry" if pnl is not None else "unresolved_missing_avg_entry",\n',
    '                "selected_close": price,\n'
    '                "avg_entry_local": avg_entry,\n'
    '                "avg_entry_source": avg_entry_source,\n'
    '                "pnl_pct": pnl,\n'
    '                "pnl_basis": "current_close_vs_avg_entry",\n',
    1,
)
text = text.replace(
    '            "pnl_recomputed_from_avg_entry": True,\n            "prior_persisted_market_values_not_authoritative": True,\n',
    '            "pnl_recomputed_from_avg_entry": True,\n'
    '            "average_entry_authority_complete": True,\n'
    '            "prior_persisted_market_values_not_authoritative": True,\n',
    1,
)
text = text.replace(
    '''        if expected_pnl is not None and (\n            actual_pnl is None\n            or abs(actual_pnl - expected_pnl) > pnl_tolerance_pct\n        ):\n            errors.append(\n                f"{symbol}:pnl_mismatch expected={expected_pnl:.2f} actual={actual_pnl}"\n            )\n''',
    '''        if expected_pnl is None:\n            errors.append(f"{symbol}:missing_average_entry_authority")\n        elif actual_pnl is None or abs(actual_pnl - expected_pnl) > pnl_tolerance_pct:\n            errors.append(\n                f"{symbol}:pnl_mismatch expected={expected_pnl:.2f} actual={actual_pnl}"\n            )\n''',
    1,
)
text = text.replace(
    '        "pnl_consistent_with_current_close_and_avg_entry": True,\n        "current_price_consistent": True,\n',
    '        "pnl_consistent_with_current_close_and_avg_entry": True,\n'
    '        "average_entry_authority_complete": True,\n'
    '        "current_price_consistent": True,\n',
    1,
)
auth.write_text(text, encoding='utf-8')

text = v2.read_text(encoding='utf-8')
old_choose = '''    return sorted(\n        eligible,\n        key=lambda item: (\n            item[0],\n            -item[1]["destination_score"],\n            item[1]["candidate"],\n        ),\n    )[0][1]\n'''
new_choose = '''    return sorted(\n        eligible,\n        key=lambda item: (\n            item[0],\n            0 if item[1].get("promoted_to_live_radar") else 1,\n            0 if item[1].get("candidate_role") == "primary" else 1,\n            -_num(item[1].get("total_score"), 0.0),\n            -_num(item[1].get("relative_strength_score"), 0.0),\n            -_num(item[1].get("avg_dollar_volume_3m"), 0.0),\n            item[1]["candidate"],\n        ),\n    )[0][1]\n'''
if old_choose not in text:
    raise SystemExit('choose block not found')
text = text.replace(old_choose, new_choose, 1)
text = text.replace('"schema_version": "1.1",', '"schema_version": "1.2",', 1)
text = text.replace(
    '            "stale_scorecard_or_pnl_mismatch_is_blocking": True,\n',
    '            "stale_scorecard_or_pnl_mismatch_is_blocking": True,\n'
    '            "average_entry_history_reconstruction_is_blocking": True,\n'
    '            "destination_tie_break_uses_quality_evidence": True,\n',
    1,
)
v2.write_text(text, encoding='utf-8')

text = tests.read_text(encoding='utf-8')
text = text.replace('import pytest\n', 'import csv\nimport json\n\nimport pytest\n', 1)
text = text.replace(
    '    build_current_run_valuation_state,\n',
    '    build_current_run_valuation_state,\n    reconstruct_average_entry_local,\n',
    1,
)
text += r'''\n\n\ndef test_average_entry_reconstructed_from_execution_history(tmp_path) -> None:\n    runtime_dir = tmp_path / "runtime"\n    runtime_dir.mkdir()\n    ledger = tmp_path / "etf_trade_ledger.csv"\n    with ledger.open("w", encoding="utf-8", newline="") as handle:\n        writer = csv.DictWriter(handle, fieldnames=["ticker", "shares_delta", "source_report"])\n        writer.writeheader()\n        writer.writerow({"ticker": "TEST", "shares_delta": "10", "source_report": "runtime:output/runtime/etf_report_state_20260701_run1.json"})\n        writer.writerow({"ticker": "TEST", "shares_delta": "5", "source_report": "runtime:output/runtime/etf_report_state_20260702_run2.json"})\n    for name, shares_delta, price in (("etf_model_execution_20260701_run1.json", 10, 100.0), ("etf_model_execution_20260702_run2.json", 5, 110.0)):\n        (runtime_dir / name).write_text(json.dumps({"execution_status": "executed", "shadow_positions": [{"ticker": "TEST", "shares_delta_this_run": shares_delta, "selected_close": price}]}), encoding="utf-8")\n    avg_entry = reconstruct_average_entry_local("TEST", trade_ledger_path=ledger, runtime_dir=runtime_dir)\n    assert avg_entry == 103.333333\n    portfolio = {"cash_eur": 0.0, "positions": [{"ticker": "TEST", "shares": 15, "total_score": 4.0, "fresh_cash_test": "Hold"}]}\n    pricing = {"requested_close_date": "2026-07-14", "fx_basis": {"rate": 1.0}, "price_results": [{"symbol": "TEST", "selected_close": 120.0, "status": "fresh_exact_unverified", "pricing_tier": "valuation_grade", "currency": "USD"}]}\n    state = build_current_run_valuation_state(portfolio, pricing, trade_ledger_path=ledger, runtime_dir=runtime_dir)\n    position = state["positions"][0]\n    assert position["avg_entry_source"] == "model_execution_history"\n    assert position["pnl_pct"] == 16.13\n\n\ndef test_destination_ranking_prefers_live_primary_over_alphabetical_tie() -> None:\n    incumbents = [{"ticker": "URNM", "current_weight_pct": 7.0, "release_score": 90, "release_reasons": ["loss_and_sub4_forced_reunderwrite"], "role_validity": "fail", "weeks_replaceable": 0}]\n    shared = {"destination_score": 100, "is_fundable_candidate": True, "funding_scope": "general", "price_status": "fresh_exact_unverified", "pricing_tier": "valuation_grade", "direct_rs_vs_holding": "", "direct_rs_vs_holding_1m_pct": 0.0, "direct_rs_vs_holding_3m_pct": 0.0, "relative_strength_score": 1.25}\n    candidates = [{**shared, "candidate": "IAI", "candidate_role": "alternative", "promoted_to_live_radar": False, "total_score": 3.8, "avg_dollar_volume_3m": 20_000_000}, {**shared, "candidate": "XBI", "candidate_role": "primary", "promoted_to_live_radar": True, "total_score": 4.36, "avg_dollar_volume_3m": 1_300_000_000}]\n    _, _, intents = build_decisions(incumbents, candidates, 110000.0, {"URNM"})\n    assert intents[0]["destination_ticker"] == "XBI"\n'''
tests.write_text(text, encoding='utf-8')
print('ROTATION_AUTHORITY_FINALIZE_PATCH_OK')
