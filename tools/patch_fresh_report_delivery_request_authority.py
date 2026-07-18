from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one patch marker in {path}, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


model_path = ROOT / "runtime/model_execution_guarded_auto.py"

helpers_marker = """def _positions_from_portfolio_state(path: Path) -> list[dict[str, Any]]:\n"""
helpers = '''REPORT_REQUEST_GLOB = "weekly_etf_report_request_*.md"
TRUTHY = {"1", "true", "yes", "y", "on"}
FALSEY = {"0", "false", "no", "n", "off"}


def _request_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower().replace("-", "_")] = value.strip().strip('"').strip("'")
    return values


def _latest_report_request(run_queue_dir: Path = Path("control/run_queue")) -> Path | None:
    files = sorted(run_queue_dir.glob(REPORT_REQUEST_GLOB))
    return files[-1] if files else None


def _portfolio_execution_authorized(run_queue_dir: Path = Path("control/run_queue")) -> bool:
    request = _latest_report_request(run_queue_dir)
    if request is None:
        return False
    raw = _request_values(request).get("portfolio_execution_authorized", "").strip().lower()
    if raw in TRUTHY:
        return True
    if raw in FALSEY:
        return False
    return False


def _positions_from_portfolio_state(path: Path) -> list[dict[str, Any]]:
'''
replace_once(model_path, helpers_marker, helpers)

build_marker = """def build_guarded_artifact(\n    runtime_state_path: Path, portfolio_state_path: Path, trade_ledger_path: Path, output_dir: Path\n) -> dict[str, Any]:\n"""
not_authorized_builder = '''def _build_execution_not_authorized_artifact(
    runtime_state_path: Path,
    portfolio_state_path: Path,
    trade_ledger_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    _assert_official_state_is_whole_share(portfolio_state_path)
    state = _read_json(runtime_state_path)
    prepared = engine._prepare_runtime_state(state, portfolio_state_path)
    positions = [engine._clear_run_fields(dict(row)) for row in prepared.get("positions", []) or []]
    portfolio = dict(prepared.get("portfolio") or {})
    cash = round(float(portfolio.get("cash_eur") or 0.0), 2)
    nav = round(float(portfolio.get("total_portfolio_value_eur") or 0.0), 2)
    invested = round(sum(engine._market_value_eur(row) for row in positions), 2)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_token = str(state.get("report_date") or state.get("requested_close_date") or "unknown").replace("-", "")
    run_id = str(state.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    out_path = output_dir / f"etf_model_execution_{report_token}_{run_id}_not_authorized.json"
    source_files = dict(state.get("source_files") or {})
    artifact = {
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "guarded_auto",
        "execution_status": "no_trade_intents",
        "run_id": state.get("run_id"),
        "report_date": state.get("report_date"),
        "requested_close_date": state.get("requested_close_date"),
        "source_files": {
            "runtime_state": str(runtime_state_path),
            "portfolio_state": str(portfolio_state_path),
            "trade_ledger": str(trade_ledger_path),
            "pricing_audit": source_files.get("pricing_audit"),
            "rotation_plan": source_files.get("rotation_plan"),
            "lane_assessment": source_files.get("lane_assessment"),
        },
        "policy_checks": {
            "passed": True,
            "errors": [],
            "warnings": ["portfolio_execution_not_authorized_by_latest_report_request"],
            "mode_note": "Fresh report generation and delivery were authorized; portfolio mutation was not authorized.",
        },
        "pre_trade_portfolio": {
            "cash_eur": cash,
            "total_portfolio_value_eur": nav,
            "base_currency": "EUR",
        },
        "post_trade_shadow_portfolio": {
            "cash_eur": cash,
            "invested_market_value_eur": invested,
            "nav_eur": nav,
            "nav_drift_eur": 0.0,
        },
        "proposed_ledger_rows": [],
        "shadow_positions": positions,
        "guarded_auto_result": {
            "official_ledger_rows": [],
            "portfolio_state_written": False,
            "trade_ledger_written": False,
            "idempotency_status": "execution_not_authorized",
            "authorization_status": "not_authorized",
            "matched_pairs": [],
            "post_trade_nav_eur": nav,
            "post_trade_invested_market_value_eur": invested,
            "post_trade_cash_eur": cash,
            "whole_share_contract_status": "compliant",
        },
        "artifact_path": str(out_path),
    }
    _write_json(out_path, artifact)
    (output_dir / "latest_etf_model_execution_path.txt").write_text(str(out_path) + "\\n", encoding="utf-8")
    return artifact


def build_guarded_artifact(
    runtime_state_path: Path, portfolio_state_path: Path, trade_ledger_path: Path, output_dir: Path
) -> dict[str, Any]:
'''
replace_once(model_path, build_marker, not_authorized_builder)

start_marker = '''    _assert_official_state_is_whole_share(portfolio_state_path)
    state = _read_json(runtime_state_path)
    trade_date = _trade_date(state)
'''
start_replacement = '''    _assert_official_state_is_whole_share(portfolio_state_path)
    state = _read_json(runtime_state_path)
    if not _portfolio_execution_authorized():
        return _build_execution_not_authorized_artifact(
            runtime_state_path, portfolio_state_path, trade_ledger_path, output_dir
        )
    trade_date = _trade_date(state)
'''
replace_once(model_path, start_marker, start_replacement)

readme_path = ROOT / "control/run_queue/README.md"
readme_old = '''requested_by: ChatGPT
mode: fresh-runtime-production
repository: market-predictions/weekly-etf
note: User requested a fresh Weekly ETF Pro Review from ChatGPT.
'''
readme_new = '''requested_by: ChatGPT
mode: fresh-runtime-production
repository: market-predictions/weekly-etf
requested_close_date: YYYY-MM-DD
portfolio_execution_authorized: false
delivery_authorized: true
note: User requested a fresh Weekly ETF Pro Review from ChatGPT.
'''
replace_once(readme_path, readme_old, readme_new)

readme_append = '''

## Execution authorization boundary

Every new report request must state `portfolio_execution_authorized` explicitly.

- `false` generates, validates and delivers the fresh report without writing model trades to the official portfolio state or trade ledger.
- `true` permits the existing guarded model-portfolio execution path, subject to every normal policy, pricing, whole-share and position-count gate.
- missing or malformed authorization fails closed to `false`.

`delivery_authorized` records the user's delivery instruction. The production send workflow must only be triggered by a request that explicitly authorizes delivery.
'''
readme_path.write_text(readme_path.read_text(encoding="utf-8").rstrip() + readme_append + "\n", encoding="utf-8")

(ROOT / "tests/test_model_execution_request_authority.py").write_text('''from __future__ import annotations

import json
from pathlib import Path

from runtime.model_execution_guarded_auto import (
    _portfolio_execution_authorized,
    build_guarded_artifact,
)


def _request(directory: Path, value: str | None) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    lines = ["# Weekly ETF report request", "delivery_authorized: true"]
    if value is not None:
        lines.append(f"portfolio_execution_authorized: {value}")
    (directory / "weekly_etf_report_request_20260718_125324.md").write_text("\\n".join(lines) + "\\n", encoding="utf-8")


def test_request_authorization_is_explicit_and_fail_closed(tmp_path: Path) -> None:
    queue = tmp_path / "queue"
    assert _portfolio_execution_authorized(queue) is False
    _request(queue, None)
    assert _portfolio_execution_authorized(queue) is False
    _request(queue, "not-a-boolean")
    assert _portfolio_execution_authorized(queue) is False
    _request(queue, "false")
    assert _portfolio_execution_authorized(queue) is False
    _request(queue, "true")
    assert _portfolio_execution_authorized(queue) is True


def test_unauthorized_report_request_writes_no_portfolio_or_ledger(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    queue = tmp_path / "control/run_queue"
    _request(queue, "false")
    output = tmp_path / "output/runtime"
    output.mkdir(parents=True)
    portfolio = tmp_path / "output/etf_portfolio_state.json"
    portfolio.parent.mkdir(parents=True, exist_ok=True)
    portfolio.write_text(json.dumps({
        "cash_eur": 1000.0,
        "invested_market_value_eur": 1000.0,
        "nav_eur": 2000.0,
        "positions": [{
            "ticker": "AAA", "shares": 10, "currency": "EUR",
            "current_price_local": 100.0, "previous_price_local": 100.0,
            "market_value_local": 1000.0, "previous_market_value_local": 1000.0,
            "market_value_eur": 1000.0, "previous_market_value_eur": 1000.0,
            "current_weight_pct": 50.0, "previous_weight_pct": 50.0,
            "weight_inherited_pct": 50.0, "target_weight_pct": 50.0,
        }],
        "whole_share_contract": {"status": "compliant"},
    }), encoding="utf-8")
    ledger = tmp_path / "output/etf_trade_ledger.csv"
    ledger.write_text("trade_id,trade_date,source_report,ticker,action,shares_delta\\n", encoding="utf-8")
    runtime = tmp_path / "output/runtime/state.json"
    runtime.write_text(json.dumps({
        "run_id": "20260718_125324",
        "report_date": "2026-07-17",
        "requested_close_date": "2026-07-17",
        "portfolio": {"cash_eur": 1000.0, "total_portfolio_value_eur": 2000.0, "base_currency": "EUR"},
        "fx_basis": {"rate": 1.0},
        "pricing": [{"symbol": "AAA", "selected_close": 100.0, "currency": "EUR", "status": "fresh_exact_close", "pricing_tier": "valuation_grade"}],
        "positions": [{"ticker": "AAA", "shares": 10}],
        "trade_intents": [{"source_ticker": "AAA", "destination_ticker": "BBB"}],
        "source_files": {"pricing_audit": "fixture.json", "rotation_plan": "plan.json"},
    }), encoding="utf-8")

    portfolio_before = portfolio.read_bytes()
    ledger_before = ledger.read_bytes()
    artifact = build_guarded_artifact(runtime, portfolio, ledger, output)

    assert artifact["execution_mode"] == "guarded_auto"
    assert artifact["execution_status"] == "no_trade_intents"
    assert artifact["guarded_auto_result"]["authorization_status"] == "not_authorized"
    assert artifact["guarded_auto_result"]["portfolio_state_written"] is False
    assert artifact["guarded_auto_result"]["trade_ledger_written"] is False
    assert artifact["proposed_ledger_rows"] == []
    assert portfolio.read_bytes() == portfolio_before
    assert ledger.read_bytes() == ledger_before
''', encoding="utf-8")

(ROOT / ".github/workflows/validate-report-request-execution-authority.yml").write_text('''name: Validate report-request execution authority

on:
  pull_request:
    branches: [main]
    paths:
      - "runtime/model_execution_guarded_auto.py"
      - "tests/test_model_execution_request_authority.py"
      - "control/run_queue/README.md"
      - "control/run_queue/weekly_etf_report_request_*.md"
      - ".github/workflows/validate-report-request-execution-authority.yml"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    env:
      PYTHONPATH: .
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install pytest
      - name: Compile authority gate
        run: python -m py_compile runtime/model_execution_guarded_auto.py tests/test_model_execution_request_authority.py
      - name: Run focused authority tests
        run: pytest -q tests/test_model_execution_request_authority.py tests/test_model_no_trade_gate.py
      - name: Verify fresh request boundary
        run: |
          python - <<'PY'
          from pathlib import Path
          path = Path("control/run_queue/weekly_etf_report_request_20260718_125324.md")
          text = path.read_text(encoding="utf-8")
          assert "requested_close_date: 2026-07-17" in text
          assert "portfolio_execution_authorized: false" in text
          assert "delivery_authorized: true" in text
          print("REPORT_REQUEST_AUTHORITY_OK")
          PY
''', encoding="utf-8")

(ROOT / "control/work_packages/WP_FRESH_REPORT_DELIVERY_REQUEST_AUTHORITY_20260718.md").write_text('''# Work Package — WP_FRESH_REPORT_DELIVERY_REQUEST_AUTHORITY

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: active / claimed

## Current issue

The user authorized a fresh report generation and delivery, but did not authorize the separate close-first portfolio execution package. The production workflow invokes guarded model execution unconditionally, so the run request must be able to fail closed against unauthorized portfolio mutation.

## Decision framework

Report delivery authorization and portfolio execution authorization are separate decisions. A fresh report request must state both explicitly.

## Input/state contract

The latest `control/run_queue/weekly_etf_report_request_*.md` file is the run authorization record. Missing, malformed or false `portfolio_execution_authorized` means no official portfolio or trade-ledger write.

## Output contract

The fresh EN/NL report may describe current evidence and recommendations, but may not claim a model trade was implemented when portfolio execution was not authorized.

## Operational runbook

1. add a fail-closed request parser to the guarded execution wrapper;
2. emit a validated `guarded_auto/no_trade_intents` artifact when execution is unauthorized;
3. preserve official shares and ledger;
4. trigger the normal production workflow with a request for close 2026-07-17;
5. validate run and delivery manifests;
6. confirm both inbox receipts before claiming success.

## Authority boundary

```text
portfolio_execution_authorized: false
delivery_authorized: true
broker_execution: false
```
''', encoding="utf-8")

(ROOT / "control/work_package_claims/WP_FRESH_REPORT_DELIVERY_REQUEST_AUTHORITY_20260718.md").write_text('''# Work Package Claim

```text
package: WP_FRESH_REPORT_DELIVERY_REQUEST_AUTHORITY
repository: market-predictions/weekly-etf
claimed_by: ChatGPT
claimed_at_utc: 2026-07-18T12:53:24Z
branch: agent/fresh-report-delivery-request-authority
status: active
scope: fail-closed report-request execution authority, fresh 2026-07-17 production report and delivery proof
```

Boundaries:

- fresh report generation and bilingual delivery are authorized;
- portfolio execution is not authorized;
- official share quantities and trade ledger may not change;
- valuation refresh and immutable run/delivery evidence are allowed;
- delivery success requires a manifest and independent inbox receipt.
''', encoding="utf-8")

(ROOT / "control/run_queue/weekly_etf_report_request_20260718_125324.md").write_text('''# Weekly ETF report request

requested_at_utc: 2026-07-18T12:53:24Z
requested_by: ChatGPT
mode: fresh-runtime-production-report-only
repository: market-predictions/weekly-etf
report_scope: standard U.S. Weekly ETF Pro report
requested_close_date: 2026-07-17
portfolio_execution_authorized: false
delivery_authorized: true
broker_execution_authorized: false
note: User explicitly requested a fresh Weekly ETF report generation and bilingual email delivery after the cockpit email inline-style correction.

## Required production proof

1. refresh holding and challenger pricing for the latest completed U.S. session;
2. refresh relative strength, macro evidence and lane scoring;
3. generate current English and Dutch reports from official portfolio authority;
4. do not write model trades to official portfolio shares or the trade ledger;
5. render one inline-styled email cockpit per language and preserve the classic report body;
6. validate pricing lineage, whole shares, position count, client language, HTML and PDF;
7. send both language editions;
8. persist run and delivery manifests;
9. confirm both messages in the receiving inbox before delivery is called successful.
''', encoding="utf-8")

for temporary in (
    ROOT / "tools/patch_fresh_report_delivery_request_authority.py",
    ROOT / ".github/workflows/patch-fresh-report-delivery-request-authority.yml",
):
    temporary.unlink()

print("FRESH_REPORT_DELIVERY_REQUEST_AUTHORITY_PATCH_OK")
