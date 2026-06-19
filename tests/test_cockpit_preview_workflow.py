from __future__ import annotations

from pathlib import Path


WORKFLOW = Path(".github/workflows/render-cockpit-preview.yml")


def _workflow_text() -> str:
    assert WORKFLOW.exists(), "Cockpit preview workflow is missing"
    return WORKFLOW.read_text(encoding="utf-8")


def test_cockpit_preview_workflow_is_manual_only() -> None:
    text = _workflow_text()

    assert "workflow_dispatch:" in text
    assert "push:" not in text
    assert "pull_request:" not in text
    assert "schedule:" not in text


def test_cockpit_preview_workflow_does_not_use_delivery_or_mail_path() -> None:
    text = _workflow_text()
    lowered = text.lower()

    assert "send_report.py" not in text
    assert "send_report_runtime_html.py" not in text
    assert "smtp" not in lowered
    assert "email" not in lowered


def test_cockpit_preview_workflow_renders_and_uploads_preview_only() -> None:
    text = _workflow_text()

    assert "runtime.render_cockpit_front_page" in text
    assert "output/cockpit_preview" in text
    assert "actions/upload-artifact" in text
    assert "git commit" not in text
    assert "git push" not in text
