# ETF Review OS — Next Actions

## Current authoritative baseline

```text
latest_report_close: 2026-07-16
latest_report_run_id: 20260717_154351
latest_delivered_report: output/weekly_analysis_pro_260716_02.md
latest_delivered_report_nl: output/weekly_analysis_pro_nl_260716_02.md
official_portfolio_state: output/etf_portfolio_state.json
whole_share_status: compliant
nav_eur: 107117.94
cash_eur: 2534.36
position_count: 9
cockpit_production_feature: enabled
client_language_contract: active
inbox_receipt: confirmed_both_languages
```

The current delivered package is now the first real production proof combining:

1. whole-share official state and integer trade deltas;
2. one cockpit front page per language;
3. preserved classic report bodies;
4. the shared internal-language clean gate;
5. passed pricing lineage and successful run manifest;
6. a real delivery manifest;
7. confirmed English and Dutch Gmail Inbox receipts.

## Completed delivery recovery

```text
package: WP_FRESH_WEEKLY_ETF_SEND_RECOVERY
source_run: 20260717_154351
persisted_rotation: XLU -> PAVE
repeat_portfolio_execution: false
language_fix_PR: #89
language_fix_merge: 68e8587ff6032c8cf3fe1c30019fb513cf57058f
recovery_workflow_PR: #90
recovery_workflow_merge: de2464fc81cc1579437ffaad4a62f4add279d6f5
validation_run: 29596023922
validation_job: 87936494610
delivery_evidence_commit: ddc745fddf0e80a31c4309658743f6435a4d486b
status: closed_delivered
```

Persistent evidence:

```text
control/evidence/WEEKLY_ETF_DELIVERY_RECOVERY_EVIDENCE_20260717.json
output/delivery/weekly_etf_delivery_manifest_2026-07-16_20260717_154351.json
output/run_manifests/weekly_etf_run_manifest_2026-07-16_20260717_154351.json
```

## Immediate next package

Create and claim:

```text
WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
```

### Current issue

The official portfolio contains nine whole-share positions:

```text
CIBR
GSG
IEFA
PAVE
SMH
URNM
XBI
XLU
XLV
```

The current report constraint says:

```text
Max number of positions: 8
```

The mismatch arose because `XLU` was reduced from 148 to 14 shares while `PAVE` was added at 107 shares. Whole-share compliance is intact, but maximum-position-count compliance is ambiguous.

### Required decision framework

The package must choose and document one rule:

```text
A. every non-zero position counts, so a rotation adding a ninth position must close a source position completely;
B. sub-threshold residual positions may temporarily exceed the maximum under an explicit residual exception;
C. another deterministic rule supported by portfolio and execution evidence.
```

### Required input/state contract

- official position count must be computed from `output/etf_portfolio_state.json`;
- zero-share positions must never count;
- residual thresholds, if allowed, must be explicit and machine-readable;
- no holding may be changed during a planning or validation-only package.

### Required output contract

- the report constraint and actual official position count may not contradict each other;
- any residual exception must be visible in client-safe language;
- no raw override or workflow terminology may leak into the report.

### Required operational runbook

- fail closed before future guarded execution when the intended post-trade count breaches the selected rule;
- prove integer shares and no NAV drift beyond the existing tolerance;
- add focused tests for reduce-to-residual, full close, new add and already-over-limit state;
- do not send a new report as part of this reconciliation package.

## Later governance cleanup

A separate governance-only package may still reconcile stale `planned` labels in `control/SYSTEM_INDEX.md`. Do not combine that documentation cleanup with position-count logic or portfolio execution.
