import json
from pathlib import Path

IMPLEMENTATION_MERGE = "467726f2449b3a409008075812c761c4dc48c3f3"
CLOSEOUT_PR = 99
FINAL_HEAD = "7e9706b6019f4e4eb6debc5a2ff95fe0ed70399c"
FINAL_ARTIFACT = 8428574798
FINAL_DIGEST = "sha256:87a73c4c03d491105d7fcb8b2df1775410113b3e4547f159684027a714fb0319"


def replace_required(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"required text missing in {path}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# Work package
wp = Path("control/work_packages/WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_20260718.md")
replace_required(
    wp,
    "Status: implementation_complete / validation_green / merge_pending",
    "Status: closed_on_closeout_merge / merged / validated_no_send",
)
text = wp.read_text(encoding="utf-8")
text = text.replace("- PR merge: pending;", "- implementation PR #98 merged: complete;")
text = text.replace(
    "- claim release and final handover closeout: pending merge;",
    "- governance-closeout PR #99 and claim release: effective on merge;",
)
if "implementation_merge: 467726f2449b3a409008075812c761c4dc48c3f3" not in text:
    text = text.replace(
        "validated_head: 72841c3bbedfea19122269f2f7c78168676955cb",
        "implementation_pull_request: #98\nimplementation_merge: 467726f2449b3a409008075812c761c4dc48c3f3\ncloseout_pull_request: #99\nvalidated_head: 7e9706b6019f4e4eb6debc5a2ff95fe0ed70399c",
        1,
    )
    text = text.replace("email_inline_run: 29640677887 success", "email_inline_run: 29640892996 success", 1)
    text = text.replace("wp10_run: 29640677890 success", "wp10_run: 29640893034 success", 1)
    text = text.replace("current_runtime_run: 29640677892 success", "current_runtime_run: 29640892988 success", 1)
    text = text.replace("wp08_run: 29640677898 success", "wp08_run: 29640893022 success", 1)
    text = text.replace("wp11_run: 29640677882 success", "wp11_run: 29640892992 success", 1)
    text = text.replace("artifact_id: 8428508030", "report_language_run: 29640893008 success\nposition_count_run: 29640893026 success\nartifact_id: 8428574798", 1)
    text = text.replace("sha256:df5c3daae4e82b386bdc868aaeb53d8be00cdeb4da1a6f87decd9b62037e8a34", FINAL_DIGEST, 1)
wp.write_text(text, encoding="utf-8")

# Claim
claim = Path("control/work_package_claims/WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_20260718.md")
text = claim.read_text(encoding="utf-8")
text = text.replace("closeout_pull_request: pending", "closeout_pull_request: 99")
text = text.replace("status: implementation_merged / closeout_active", "status: closeout_ready / release_effective_on_merge")
text = text.replace(
    "The claim remains held until the governance-closeout PR merges and the exact closeout merge is recorded.",
    "The claim is released when PR #99 merges. The exact closeout merge is then recorded in the final receipt.",
)
claim.write_text(text, encoding="utf-8")

# Handover
handover = Path("control/handovers/HANDOVER_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_20260718.md")
text = handover.read_text(encoding="utf-8")
text = text.replace("Status: implementation complete / validation green / merge pending", "Status: closed on governance-closeout merge / claim release effective on merge")
text = text.replace("Pull request: #98", "Implementation pull request: #98\nImplementation merge: `467726f2449b3a409008075812c761c4dc48c3f3`\nGovernance-closeout pull request: #99")
if "## Final same-head receipt" not in text:
    text = text.rstrip() + """

## Final same-head receipt

```text
validated_head: 7e9706b6019f4e4eb6debc5a2ff95fe0ed70399c
email_inline_run: 29640892996 success
wp10_run: 29640893034 success
wp11_run: 29640892992 success
current_runtime_run: 29640892988 success
wp08_run: 29640893022 success
report_language_run: 29640893008 success
position_count_run: 29640893026 success
artifact_id: 8428574798
artifact_digest: sha256:87a73c4c03d491105d7fcb8b2df1775410113b3e4547f159684027a714fb0319
protected_authority_hashes: identical
historical_reports: unchanged
production_report_generated: false
email_sent: false
```
"""
handover.write_text(text, encoding="utf-8")

# Persistent evidence
path = Path("control/evidence/COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_EVIDENCE_20260718.json")
payload = json.loads(path.read_text(encoding="utf-8"))
payload["status"] = "closed_on_closeout_merge_validated_no_send"
payload["implementation"]["pull_request"] = 98
payload["implementation"]["merge_commit"] = IMPLEMENTATION_MERGE
payload["implementation"]["closeout_pull_request"] = CLOSEOUT_PR
payload["validation"].update(
    {
        "validated_head": FINAL_HEAD,
        "email_inline_run": 29640892996,
        "wp10_run": 29640893034,
        "wp11_run": 29640892992,
        "current_runtime_run": 29640892988,
        "wp08_run": 29640893022,
        "report_language_run": 29640893008,
        "position_count_run": 29640893026,
        "artifact_id": FINAL_ARTIFACT,
        "artifact_digest": FINAL_DIGEST,
        "all_final_gates": "success",
    }
)
path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

# Control files
for name in ("control/CURRENT_STATE.md", "control/NEXT_ACTIONS.md"):
    path = Path(name)
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "status: implementation_complete_validation_green_merge_pending",
        "status: closed_on_governance_closeout_merge",
        1,
    )
    if "cockpit_email_fix_implementation_merge: 467726f2449b3a409008075812c761c4dc48c3f3" not in text:
        marker = "pull_request: #98\n"
        replacement = (
            "pull_request: #98\n"
            "cockpit_email_fix_implementation_merge: 467726f2449b3a409008075812c761c4dc48c3f3\n"
            "cockpit_email_fix_closeout_pull_request: #99\n"
        )
        text = text.replace(marker, replacement, 1)
    path.write_text(text, encoding="utf-8")
