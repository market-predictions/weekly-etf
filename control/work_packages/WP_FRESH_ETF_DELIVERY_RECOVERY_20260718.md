# Work Package — WP_FRESH_ETF_DELIVERY_RECOVERY

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: active / delivery recovery authorized

## Current issue

Production runs `20260718_134258` and `20260718_140601` generated and persisted fresh 2026-07-17 report evidence but stopped before email transport. Neither run wrote a delivery manifest and Gmail contains no matching English or Dutch message.

## Root cause boundary

The deterministic report, valuation, whole-share, position-count, bilingual, HTML, PDF and client-language gates have passed in exact-current replay. Recovery must therefore remain isolated to the output contract and delivery runbook. It must not rerun or authorize portfolio execution.

## Decision framework

A delivery recovery is permitted only when:

- the source reports and runtime state are immutable and identified;
- the prior run manifest has no delivery manifest;
- no receiving-inbox message exists;
- portfolio and trade-ledger hashes remain unchanged;
- both language editions are sent exactly once;
- success is claimed only after a delivery manifest and independent inbox receipts exist.

## Input/state contract

Source run: `20260718_140601`
Close date: `2026-07-17`
English report: `output/weekly_analysis_pro_260717_02.md`
Dutch report: `output/weekly_analysis_pro_nl_260717_02.md`
Runtime state: `output/runtime/etf_report_state_20260717_20260718_140601.json`
Run manifest: `output/run_manifests/weekly_etf_run_manifest_2026-07-17_20260718_140601.json`

## Output contract

- validated EN/NL HTML and PDF delivery assets;
- successful bilingual SMTP transport;
- delivery manifest linked to the existing run manifest;
- unchanged official portfolio shares and trade ledger;
- inbox receipts before delivery success is reported.

## Operational runbook

1. validate the source run and absence of a prior delivery manifest;
2. snapshot official portfolio and ledger hashes;
3. rerun downstream client-surface, bilingual, render and explicit-state gates only;
4. send English and Dutch editions;
5. write delivery and completed run manifests;
6. persist delivery assets and receipts;
7. independently verify both inbox messages.
