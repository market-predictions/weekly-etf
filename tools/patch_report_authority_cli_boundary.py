from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one marker in {path}, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


runtime = ROOT / "runtime/model_execution_guarded_auto.py"
replace_once(
    runtime,
    '''def build_guarded_artifact(
    runtime_state_path: Path, portfolio_state_path: Path, trade_ledger_path: Path, output_dir: Path
) -> dict[str, Any]:
''',
    '''def build_guarded_artifact(
    runtime_state_path: Path,
    portfolio_state_path: Path,
    trade_ledger_path: Path,
    output_dir: Path,
    *,
    enforce_request_authority: bool = False,
) -> dict[str, Any]:
''',
)
replace_once(
    runtime,
    '''    if not _portfolio_execution_authorized():
''',
    '''    if enforce_request_authority and not _portfolio_execution_authorized():
''',
)
replace_once(
    runtime,
    '''    artifact = build_guarded_artifact(
        Path(args.runtime_state), Path(args.portfolio_state), Path(args.trade_ledger), Path(args.output_dir)
    )
''',
    '''    artifact = build_guarded_artifact(
        Path(args.runtime_state),
        Path(args.portfolio_state),
        Path(args.trade_ledger),
        Path(args.output_dir),
        enforce_request_authority=True,
    )
''',
)

test_path = ROOT / "tests/test_model_execution_request_authority.py"
replace_once(
    test_path,
    '''    artifact = build_guarded_artifact(runtime, portfolio, ledger, output)
''',
    '''    artifact = build_guarded_artifact(
        runtime, portfolio, ledger, output, enforce_request_authority=True
    )
''',
)

print("REPORT_AUTHORITY_CLI_BOUNDARY_PATCH_OK")
