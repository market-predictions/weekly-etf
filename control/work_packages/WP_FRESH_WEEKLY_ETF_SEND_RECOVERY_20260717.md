# WP_FRESH_WEEKLY_ETF_SEND_RECOVERY

Date: 2026-07-17
Status: closed_delivered

## Current issue resolved

Production run `20260717_154351` completed pricing, report generation and whole-share guarded execution, but its first attempt failed after rendering and before email delivery.

The official `XLU -> PAVE` state change had already been persisted and was not repeated.

## Root causes

1. Generic client-facing remnants `discipline gates` / `disciplinepoorten` were not covered by the phrase-specific internal-language cleanup.
2. The Dutch delivery validator inspected raw HTML and treated the CSS/class identifier `confidence` as visible English, while the rendered client label was correctly `vertrouwen`.

## Implemented recovery

```text
PR #89: residual internal-language normalization
merge: 68e8587ff6032c8cf3fe1c30019fb513cf57058f

PR #90: fail-closed persisted-package recovery workflow
merge: de2464fc81cc1579437ffaad4a62f4add279d6f5
validation run: 29596023922
validation job: 87936494610
```

The recovery reused the exact persisted runtime, pricing and execution artifacts for run `20260717_154351`. It did not run pricing, discovery or guarded execution again.

## Acceptance result

- exact failing post-render gates identified;
- smallest client-language and visible-text validation repairs implemented;
- existing report package rebuilt and fully validated;
- one cockpit front page rendered per language;
- official whole-share state and ledger remained unchanged during recovery;
- SMTP delivery returned without exception;
- delivery and successful run manifests were written;
- both English and Dutch `_02` messages were confirmed in Gmail Inbox;
- each message contains exactly four attachments.

## Evidence

```text
output/delivery/weekly_etf_delivery_manifest_2026-07-16_20260717_154351.json
output/run_manifests/weekly_etf_run_manifest_2026-07-16_20260717_154351.json
control/evidence/WEEKLY_ETF_DELIVERY_RECOVERY_EVIDENCE_20260717.json
delivery evidence commit: ddc745fddf0e80a31c4309658743f6435a4d486b
```
