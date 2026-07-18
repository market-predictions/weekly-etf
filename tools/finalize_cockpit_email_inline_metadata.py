import json
from pathlib import Path

CLOSEOUT_MERGE = "720c2e47e51ec59329fdb1eac4d5d69edd22e176"
METADATA_PR = 100


def update_text(path: Path, replacements: list[tuple[str, str]], append: str = "") -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
    if append and append.splitlines()[0] not in text:
        text = text.rstrip() + "\n\n" + append.rstrip() + "\n"
    path.write_text(text, encoding="utf-8")


update_text(
    Path("control/work_package_claims/WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_20260718.md"),
    [("metadata_pull_request: pending", "metadata_pull_request: 100")],
)

update_text(
    Path("control/work_packages/WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_20260718.md"),
    [
        ("Status: closed_on_closeout_merge / merged / validated_no_send", "Status: closed / merged / validated_no_send"),
        ("closeout_pull_request: #99", "closeout_pull_request: #99\ncloseout_merge: 720c2e47e51ec59329fdb1eac4d5d69edd22e176\nmetadata_pull_request: #100"),
        ("- governance-closeout PR #99 and claim release: effective on merge;", "- governance-closeout PR #99 merged and claim released: complete;"),
    ],
)

handover_append = """## Final closeout receipt

```text
implementation_pull_request: #98
implementation_merge: 467726f2449b3a409008075812c761c4dc48c3f3
closeout_pull_request: #99
closeout_merge: 720c2e47e51ec59329fdb1eac4d5d69edd22e176
metadata_pull_request: #100
claim_status: closed / released
portfolio_state_changed: false
historical_report_changed: false
production_report_generated: false
email_sent: false
```
"""
update_text(
    Path("control/handovers/HANDOVER_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_20260718.md"),
    [
        ("Status: closed on governance-closeout merge / claim release effective on merge", "Status: closed / merged / claim released"),
        ("Governance-closeout pull request: #99", "Governance-closeout pull request: #99\nGovernance-closeout merge: `720c2e47e51ec59329fdb1eac4d5d69edd22e176`\nMetadata pull request: #100"),
    ],
    handover_append,
)

path = Path("control/evidence/COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_EVIDENCE_20260718.json")
payload = json.loads(path.read_text(encoding="utf-8"))
payload["status"] = "closed_merged_validated_no_send"
payload["implementation"]["closeout_merge"] = CLOSEOUT_MERGE
payload["implementation"]["metadata_pull_request"] = METADATA_PR
payload["authority"]["claim_released"] = True
path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

for name in ("control/CURRENT_STATE.md", "control/NEXT_ACTIONS.md"):
    path = Path(name)
    text = path.read_text(encoding="utf-8")
    text = text.replace("status: closed_on_governance_closeout_merge", "status: closed_merged_validated_no_send", 1)
    marker = "cockpit_email_fix_closeout_pull_request: #99\n"
    replacement = (
        "cockpit_email_fix_closeout_pull_request: #99\n"
        "cockpit_email_fix_closeout_merge: 720c2e47e51ec59329fdb1eac4d5d69edd22e176\n"
        "cockpit_email_fix_metadata_pull_request: #100\n"
    )
    if marker in text and "cockpit_email_fix_closeout_merge:" not in text:
        text = text.replace(marker, replacement, 1)
    path.write_text(text, encoding="utf-8")
