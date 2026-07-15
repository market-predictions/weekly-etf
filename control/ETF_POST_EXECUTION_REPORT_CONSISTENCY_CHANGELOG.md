# ETF Post-Execution Report Consistency — Changelog

Repository: `market-predictions/weekly-etf`
Work package: `WP_POST_EXECUTION_REPORT_CONSISTENCY`

## 2026-07-15 — Production surface contradiction identified

Production run `20260715_175910` executed and persisted one guarded model rotation:

```text
URNM: Sell -122.008961 shares; model weight 7.01% -> 2.01%
XBI: Buy +40.491749 shares; model weight 0.00% -> 5.00%
```

The first delivered English and Dutch reports mixed correct execution evidence with stale no-action wording. Earlier intermediate share quantities were superseded by the official execution artifact and ledger values above.

## 2026-07-15 — Output-authority decision

Stable rule introduced:

```text
executed_model_changes is authoritative for all post-execution action wording and classification.
```

Official portfolio state remains authoritative for holdings and values. Official trade ledger remains authoritative for executed share deltas. `suggested_action` is research memory only after execution.

## 2026-07-15 — Implementation completed

Added:

- deterministic post-execution action classification;
- bilingual executed-state action buckets and labels;
- dynamic Markdown and HTML decision cockpits;
- aligned Sections 1, 2, 12, 13, 14 and 15;
- blocking cross-section consistency validation;
- exact-artifact correction rendering without model re-execution;
- state/ledger immutability checks;
- retained correction diagnostics and evidence-recovery support.

## 2026-07-15 — Validation completed

```text
workflow: Validate ETF post-execution report consistency
run_id: 29442287444
conclusion: success
```

Verified compilation, focused tests, exact-artifact replay, EN/NL semantic consistency, delivery-cockpit consistency and state/ledger immutability.

## 2026-07-15 — Implementation merged

```text
PR: #59
merge_commit: 907598eff2a08a5d27b8bd2238610ecc83a31d76
```

## 2026-07-15 — Corrected delivery completed

The corrected report transaction generated and sent:

```text
output/weekly_analysis_pro_260714_03.md
output/weekly_analysis_pro_nl_260714_03.md
```

Delivery evidence:

```text
workflow_run: 29455717158
receipt: DELIVERY_OK | mode=pro_bilingual
pdf_en: yes
pdf_nl: yes
delivery_layer_status: smtp_sendmail_returned_no_exception
```

The runner failed only after successful delivery because it expected JSON manifests while the sender emitted text manifests. No duplicate resend was performed.

## 2026-07-15 — Evidence recovered and persisted without resending

```text
workflow_run: 29455966433
conclusion: success
persistence_commit: d829e89329656b29be4c1d9b3b4aca75ba46f3b4
```

The recovery path:

- downloaded the successful delivery transcript;
- regenerated EN/NL Markdown, clean Markdown, HTML, PDF and equity-curve assets without SMTP;
- proved official state and ledger hashes unchanged;
- persisted the delivery transcript and correction manifest.

## 2026-07-15 — Inbox receipts verified and package closed

Connected Gmail confirmed both corrected messages in the inbox with their PDF attachments:

```text
Corrected Weekly ETF Pro Review 2026-07-14
Gecorrigeerde Weekly ETF Pro Review | Nederlands 2026-07-14
```

Final evidence:

```text
output/delivery/weekly_etf_correction_delivery_receipt_2026-07-14_29455717158.txt
output/delivery/weekly_etf_correction_manifest_2026-07-14_20260715_223718.json
```

`WP_POST_EXECUTION_REPORT_CONSISTENCY` is closed. No further correction resend is required.
