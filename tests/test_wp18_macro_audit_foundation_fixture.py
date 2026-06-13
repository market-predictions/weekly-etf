from __future__ import annotations

from pathlib import Path

from tools.replay_macro_audit_foundation_fixture import replay


class Args:
    fixture = Path("tests/fixtures/macro_data_audit_fixture.json")
    config = Path("config/macro_data_sources.yml")
    cb_calendar = Path("config/cb_calendar.yml")
    reference_date = "2026-05-31"
    run_id = "test_wp18_fixture"
    workflow_name = "pytest"
    workflow_run_id = "local"
    workflow_run_number = "local"
    workflow_attempt = "1"
    commit_sha = "test"
    source_ref = "test"


def test_wp18_macro_audit_foundation_fixture_replay_writes_shadow_evidence(tmp_path) -> None:
    args = Args()
    args.output_dir = tmp_path

    result = replay(args)

    audit = Path(result["audit"])
    evidence = Path(result["evidence"])
    latest = Path(result["latest"])
    assert audit.exists()
    assert evidence.exists()
    assert latest.exists()
    assert result["summary"]["mode"] == "fixture"
    assert result["summary"]["groups"] == ["ecb", "fred", "treasury_fiscaldata", "volatility"]
