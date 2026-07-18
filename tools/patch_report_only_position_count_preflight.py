from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one marker in {path}, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


validator = ROOT / "tools/validate_etf_persisted_valuation_state.py"
replace_once(
    validator,
    "from runtime.model_execution_guarded_auto import _whole_share_engine_patch\n",
    "from runtime.model_execution_guarded_auto import (\n    _portfolio_execution_authorized,\n    _whole_share_engine_patch,\n)\n",
)
replace_once(
    validator,
    '''def _position_count_preflight(
    runtime_state: dict[str, Any],
    portfolio_state: dict[str, Any],
    portfolio_state_path: Path,
) -> PositionCountAssessment:
''',
    '''def _position_count_preflight(
    runtime_state: dict[str, Any],
    portfolio_state: dict[str, Any],
    portfolio_state_path: Path,
    *,
    enforce_request_authority: bool = False,
) -> PositionCountAssessment:
''',
)
replace_once(
    validator,
    '''    intents = _trade_intents(runtime_state)
''',
    '''    if enforce_request_authority and not _portfolio_execution_authorized():
        return current

    intents = _trade_intents(runtime_state)
''',
)
replace_once(
    validator,
    '''    position_count = _position_count_preflight(
        runtime_state,
        portfolio_state,
        portfolio_state_path,
    )
''',
    '''    position_count = _position_count_preflight(
        runtime_state,
        portfolio_state,
        portfolio_state_path,
        enforce_request_authority=True,
    )
''',
)

test_path = ROOT / "tests/test_model_execution_request_authority.py"
text = test_path.read_text(encoding="utf-8")
append = '''


def test_report_only_position_count_preflight_does_not_project_rotation(tmp_path: Path, monkeypatch) -> None:
    from tools.validate_etf_persisted_valuation_state import _position_count_preflight

    monkeypatch.chdir(tmp_path)
    _request(tmp_path / "control/run_queue", "false")
    positions = [{"ticker": ticker, "shares": 1} for ticker in "ABCDEFGHI"]
    portfolio = {"positions": positions}
    portfolio_path = tmp_path / "output/etf_portfolio_state.json"
    portfolio_path.parent.mkdir(parents=True, exist_ok=True)
    portfolio_path.write_text(json.dumps(portfolio), encoding="utf-8")
    runtime = {
        "positions": positions,
        "rotation_plan": {
            "policy": {"max_active_positions": 8},
            "trade_intents": [{
                "source_ticker": "A",
                "destination_ticker": "NEW",
                "action_code": "replace_partial",
            }],
        },
    }

    assessment = _position_count_preflight(
        runtime,
        portfolio,
        portfolio_path,
        enforce_request_authority=True,
    )

    assert assessment.status == "close_first"
    assert assessment.current_count == 9
    assert assessment.projected_count == 9
    assert assessment.opened_tickers == ()
'''
if "test_report_only_position_count_preflight_does_not_project_rotation" not in text:
    test_path.write_text(text.rstrip() + append + "\n", encoding="utf-8")

print("REPORT_ONLY_POSITION_COUNT_PREFLIGHT_PATCH_OK")
