from __future__ import annotations

import os
import subprocess
from pathlib import Path

FILES = (
    Path("control/CURRENT_STATE.md"),
    Path("control/NEXT_ACTIONS.md"),
    Path("control/work_packages/WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md"),
    Path("control/work_package_claims/WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md"),
    Path("control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json"),
    Path("control/handovers/HANDOVER_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md"),
)
TEMPORARY_FILES = (
    Path(".github/workflows/fix-position-count-closeout-metadata.yml"),
    Path("tools/fix_position_count_closeout_metadata_20260717.py"),
)

REPLACEMENTS = (
    ("closeout_pull_request: #92", "closeout_pull_request: #93"),
    ("closeout_pull_request: 92", "closeout_pull_request: 93"),
    ("Closeout pull request: #92", "Closeout pull request: #93"),
    ("closeout PR #92", "closeout PR #93"),
    ("complete in PR #92", "complete in PR #93"),
)


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def main() -> None:
    changed: list[str] = []
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)

        if path.name == "PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json":
            text = text.replace(
                '"closeout_pull_request": 93,',
                '"closeout_pull_request": 93,\n    "closeout_merge": "9cfca787620c73e65a4302d2e4dc403a921f5ffb",',
            )
            text = text.replace(
                '"append_workflow_result": "success",',
                '"append_workflow_result": "success",\n    "final_closeout_copy_run": 29619454009,\n    "final_closeout_copy_job": 88011401148,\n    "final_closeout_copy_result": "success",',
            )
        elif path.name == "HANDOVER_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md":
            text = text.replace(
                "Closeout pull request: #93\n",
                "Closeout pull request: #93\nCloseout merge: `9cfca787620c73e65a4302d2e4dc403a921f5ffb`\n",
            )
            text = text.replace(
                "temporary_files_removed: true\n```",
                "temporary_files_removed: true\nfinal_clean_copy_run: 29619454009 success\nfinal_clean_copy_job: 88011401148\n```",
            )
        elif path.name == "CURRENT_STATE.md":
            text = text.replace(
                "closeout_pull_request: #93\n",
                "closeout_pull_request: #93\ncloseout_merge: 9cfca787620c73e65a4302d2e4dc403a921f5ffb\n",
            )
        elif path.name == "NEXT_ACTIONS.md":
            text = text.replace(
                "closeout_pull_request: #93\n",
                "closeout_pull_request: #93\ncloseout_merge: 9cfca787620c73e65a4302d2e4dc403a921f5ffb\n",
            )

        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path))

    stale = []
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        if any(old in text for old, _new in REPLACEMENTS):
            stale.append(str(path))
    if stale:
        raise RuntimeError("Stale closeout metadata remains: " + ", ".join(stale))
    if not changed:
        raise RuntimeError("No closeout metadata changed")

    for path in TEMPORARY_FILES:
        path.unlink(missing_ok=True)

    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run("git", "add", *(str(path) for path in FILES))
    run("git", "add", "-u")
    run("git", "commit", "-m", "Correct ETF position-count closeout metadata [skip ci]")
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise RuntimeError("Could not resolve target branch")
    run("git", "push", "origin", f"HEAD:{branch}")
    print(
        "ETF_POSITION_COUNT_CLOSEOUT_METADATA_OK | "
        f"files={len(changed)} | closeout_pr=93 | temporary_files_removed=true | "
        "portfolio_mutation=false | email_sent=false"
    )


if __name__ == "__main__":
    main()
