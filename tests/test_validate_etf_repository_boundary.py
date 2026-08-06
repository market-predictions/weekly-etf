from pathlib import Path

from tools.validate_etf_repository_boundary import validate


def test_clean_repository_passes(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "weekly-etf.yml").write_text("name: Weekly ETF\non: workflow_dispatch\njobs: {}\n", encoding="utf-8")
    assert validate(tmp_path)["verdict"] == "PASS"


def test_fx_runner_is_blocked(tmp_path: Path) -> None:
    (tmp_path / "prediction.py").write_text("print('fx')\n", encoding="utf-8")
    result = validate(tmp_path)
    assert result["verdict"] == "FAIL"
    assert any(item["path"] == "prediction.py" for item in result["blockers"])


def test_fx_workflow_token_is_blocked(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "fx.yml").write_text("steps:\n  - run: python prediction.py\n", encoding="utf-8")
    result = validate(tmp_path)
    assert result["verdict"] == "FAIL"
    assert any(item["type"] == "fx_token_in_active_workflow" for item in result["blockers"])
