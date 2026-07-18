from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

CLOSEOUT_MERGE = "b2d32e327023ea515c1c78ccbc66f69b69afab45"
METADATA_PR = 97
PACKAGE = Path("control/work_packages/WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_20260718.md")
CLAIM = Path("control/work_package_claims/WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_20260718.md")
HANDOVER = Path("control/handovers/HANDOVER_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_20260718.md")
EVIDENCE = Path("control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json")
CURRENT = Path("control/CURRENT_STATE.md")
NEXT = Path("control/NEXT_ACTIONS.md")
SELF = Path("tools/finalize_close_first_review_metadata.py")
WORKFLOW = Path(".github/workflows/finalize-close-first-review-metadata.yml")


def replace_required(path: Path, old: str, new: str, label: str) -> None:
    content = path.read_text(encoding="utf-8")
    if old not in content:
        raise RuntimeError(f"Missing metadata anchor in {path}: {label}")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def patch_package() -> None:
    replace_required(
        PACKAGE,
        "Status: closed_on_closeout_merge / implementation_merged / validated_no_change",
        "Status: closed / merged / validated_no_change",
        "package status",
    )
    replace_required(PACKAGE, "closeout_merge: pending", f"closeout_merge: {CLOSEOUT_MERGE}", "package closeout merge")
    content = PACKAGE.read_text(encoding="utf-8")
    content = content.replace("- governance-closeout PR: ready for merge;", "- governance-closeout PR merged: complete;")
    content = content.replace("- claim release: effective on closeout merge;", "- claim release: complete;")
    if "metadata_pull_request: #97" not in content:
        content = content.replace(
            f"closeout_merge: {CLOSEOUT_MERGE}\n",
            f"closeout_merge: {CLOSEOUT_MERGE}\nmetadata_pull_request: #97\n",
            1,
        )
    PACKAGE.write_text(content, encoding="utf-8")


def patch_claim() -> None:
    replace_required(CLAIM, "metadata_pull_request: pending", "metadata_pull_request: 97", "claim metadata PR")


def patch_handover() -> None:
    replace_required(
        HANDOVER,
        "Status: closed on governance-closeout merge / claim release effective on merge",
        "Status: closed / merged / claim released",
        "handover status",
    )
    replace_required(HANDOVER, "Governance-closeout merge: pending", f"Governance-closeout merge: `{CLOSEOUT_MERGE}`", "handover closeout merge")
    content = HANDOVER.read_text(encoding="utf-8")
    if "Metadata finalization pull request: #97" not in content:
        content = content.replace(
            f"Governance-closeout merge: `{CLOSEOUT_MERGE}`\n",
            f"Governance-closeout merge: `{CLOSEOUT_MERGE}`\nMetadata finalization pull request: #97\n",
            1,
        )
    HANDOVER.write_text(content, encoding="utf-8")


def patch_evidence() -> None:
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    closeout = payload.setdefault("governance_closeout", {})
    closeout.update(
        {
            "pull_request": 96,
            "merge_commit": CLOSEOUT_MERGE,
            "metadata_pull_request": METADATA_PR,
            "claim_release": "closed_released",
        }
    )
    payload["status"] = "closed_merged_validated_no_change"
    EVIDENCE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def patch_control(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    content = content.replace("status: closed_on_closeout_merge", "status: closed_merged_validated_no_change")
    content = content.replace("closeout_merge: pending", f"closeout_merge: {CLOSEOUT_MERGE}")
    if "metadata_pull_request: #97" not in content:
        anchor = f"closeout_merge: {CLOSEOUT_MERGE}\n"
        if anchor in content:
            content = content.replace(anchor, anchor + "metadata_pull_request: #97\n", 1)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    patch_package()
    patch_claim()
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
    subprocess.run(["git", "commit", "-m", "Finalize close-first review metadata"], check=True)
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise RuntimeError("Could not resolve metadata branch")
    subprocess.run(["git", "push", "origin", f"HEAD:{branch}"], check=True)
    print("ETF_CLOSE_FIRST_REVIEW_METADATA_OK | closeout_merge_recorded=true | claim_released=true | temporary_files_removed=true")


if __name__ == "__main__":
    main()
