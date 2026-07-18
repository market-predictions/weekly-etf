from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

MERGE = "2895bbb5940ead8526ab4c10d0ce3687f8aca423"
PR = 96
HANDOVER = Path("control/handovers/HANDOVER_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_20260718.md")
EVIDENCE = Path("control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json")
CURRENT = Path("control/CURRENT_STATE.md")
NEXT = Path("control/NEXT_ACTIONS.md")
SELF = Path("tools/patch_close_first_review_closeout.py")
WORKFLOW = Path(".github/workflows/patch-close-first-review-closeout.yml")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise RuntimeError(f"Missing closeout anchor: {label}")
    return content.replace(old, new, 1)


def patch_handover() -> None:
    content = HANDOVER.read_text(encoding="utf-8")
    content = replace_once(
        content,
        "Status: implementation complete / validation green / merge pending\nPull request: #95",
        "Status: closed on governance-closeout merge / claim release effective on merge\n"
        "Implementation pull request: #95\n"
        f"Implementation merge: `{MERGE}`\n"
        f"Governance-closeout pull request: #{PR}\n"
        "Governance-closeout merge: pending",
        "handover header",
    )
    marker = "## Final same-head validation"
    if marker not in content:
        block = '''
## Final same-head validation

```text
validated_head: bbf03f8966c93d714ff750c9d177917bcc0eef9d
review_run: 29622792895 success
position_count_run: 29622792864 success
report_language_run: 29622792867 success
current_runtime_cockpit_run: 29622792888 success
wp08_run: 29622792861 success
wp11_run: 29622792862 success
artifact_id: 8422761924
artifact_digest: sha256:1526642d997b2c9055554a3bab969ba84d1bafdf103285af00056fb7f96eae29
protected_authority_hashes: identical
historical_report_hashes: identical
```

'''
        content = replace_once(content, "## Authority boundary\n", block + "## Authority boundary\n", "handover authority heading")
    HANDOVER.write_text(content, encoding="utf-8")


def patch_evidence() -> None:
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    validation = payload.setdefault("validation", {})
    validation.update(
        {
            "implementation_pull_request": 95,
            "implementation_merge": MERGE,
            "final_validated_head": "bbf03f8966c93d714ff750c9d177917bcc0eef9d",
            "final_review_run": 29622792895,
            "final_position_count_run": 29622792864,
            "final_report_language_run": 29622792867,
            "final_current_runtime_cockpit_run": 29622792888,
            "final_wp08_run": 29622792861,
            "final_wp11_run": 29622792862,
            "final_artifact_id": 8422761924,
            "final_artifact_digest": "sha256:1526642d997b2c9055554a3bab969ba84d1bafdf103285af00056fb7f96eae29",
        }
    )
    payload["governance_closeout"] = {
        "pull_request": PR,
        "merge_commit": "pending",
        "claim_release": "effective_on_merge",
    }
    EVIDENCE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def patch_control(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    content = content.replace(
        "status: implementation_complete_validation_green_merge_pending",
        "status: closed_on_closeout_merge",
    )
    anchor = "pull_request: #95\n"
    if anchor in content and "implementation_merge: 2895bbb" not in content:
        content = content.replace(
            anchor,
            anchor
            + f"implementation_merge: {MERGE}\n"
            + f"closeout_pull_request: #{PR}\n"
            + "closeout_merge: pending\n",
            1,
        )
    path.write_text(content, encoding="utf-8")


def main() -> None:
    patch_handover()
    patch_evidence()
    patch_control(CURRENT)
    patch_control(NEXT)
    SELF.unlink(missing_ok=True)
    WORKFLOW.unlink(missing_ok=True)

    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", "control"], check=True)
    subprocess.run(["git", "add", "-u", str(SELF), str(WORKFLOW)], check=True)
    subprocess.run(["git", "commit", "-m", "Finalize close-first review closeout records [skip ci]"], check=True)
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise RuntimeError("Could not resolve closeout branch")
    subprocess.run(["git", "push", "origin", f"HEAD:{branch}"], check=True)
    print("ETF_CLOSE_FIRST_REVIEW_CLOSEOUT_OK | pr=96 | implementation_merge_recorded=true | temporary_files_removed=true")


if __name__ == "__main__":
    main()
