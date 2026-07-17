from __future__ import annotations

import os
import subprocess
from pathlib import Path

SOURCE_REF = "origin/agent/position-count-constraint-closeout"
FILES = (
    "control/CURRENT_STATE.md",
    "control/NEXT_ACTIONS.md",
    "control/DECISION_LOG.md",
    "control/ETF_SESSION_CHANGELOG.md",
    "control/work_packages/WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md",
    "control/work_package_claims/WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md",
    "control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json",
    "control/decisions/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_DECISION_20260717.md",
    "control/handovers/HANDOVER_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md",
)
TEMPORARY_FILES = (
    Path(".github/workflows/append-position-count-governance-20260717.yml"),
    Path(".github/workflows/finalize-position-count-closeout.yml"),
    Path("control/run_queue/append_position_count_governance_20260717.md"),
    Path("tools/append_position_count_governance_20260717.py"),
)


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def output(*args: str) -> bytes:
    return subprocess.check_output(args)


def main() -> None:
    run("git", "fetch", "origin", "agent/position-count-constraint-closeout")
    for raw_path in FILES:
        path = Path(raw_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(output("git", "show", f"{SOURCE_REF}:{raw_path}"))

    for path in TEMPORARY_FILES:
        path.unlink(missing_ok=True)

    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run("git", "add", *FILES)
    run("git", "add", "-u", *(str(path) for path in TEMPORARY_FILES))
    run("git", "commit", "-m", "Finalize ETF position-count governance records [skip ci]")
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise RuntimeError("Could not resolve target branch")
    run("git", "push", "origin", f"HEAD:{branch}")
    print(
        "ETF_POSITION_COUNT_CLOSEOUT_COPY_OK | "
        f"source={SOURCE_REF} | files={len(FILES)} | temporary_files_removed=true | "
        "portfolio_mutation=false | email_sent=false"
    )


if __name__ == "__main__":
    main()
