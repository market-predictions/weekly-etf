# ETF Review OS — Current State

## Snapshot date

2026-06-13

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 is closed and WP17 PDF visual QA / delivery-runbook hardening is implemented and verified on the latest manifest-linked report set `260612_08`. The latest production run succeeded with pricing lineage passed, EN/NL artifacts generated, PDF visual contract passed, manifest evidence validator passed, and delivery-manifest evidence written. Deterministic macro remains not promoted. Historical generated outputs remain immutable by default.**

## Latest verified production baseline

```text
requested_close_date: 2026-06-12
run_id: 20260613_113054
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_08.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_08.md
pricing_lineage_status: passed
workflow_status: workflow_success
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260613_113054.json
delivery_status: smtp_sendmail_returned_no_exception
total_portfolio_value_eur: 108243.33
cash_eur: 1936.52
fresh_holdings_count: 9
carried_forward_holdings_count: 0
```

Delivery evidence remains delivery-layer evidence only. It is not an end-recipient inbox receipt.

## WP16 repair closeout status

WP16 and its follow-ups are closed for the latest verified client-surface baseline.

Resolved WP16 issues:

```text
ECB macro recency miss repaired.
ECB stance now surfaces as Tightening / inflation-sensitive / Verkrappend / inflatiegevoelig.
ECB rate-policy tightening appears as a policy catalyst.
Non-U.S. developed exposure wording is reconciled with active IEFA exposure.
English performance tables no longer use Dutch n.v.t. residue.
Dutch empty-comment residue is removed.
Soft-cap / soft-target duplicate wording is normalized.
Dutch equity curve renders visibly in PDF.
No-trade model execution artifacts are accepted in shadow and guarded-auto modes when no trade intents exist.
Dutch ETF/product names are protected from localization corruption.
GSG continuity product name renders as iShares S&P GSCI Commodity-Indexed Trust.
```

## WP17 closeout status

WP17 is closed on `260612_08`.

Implemented and verified:

```text
PDF visual contract validator added.
Poppler rendering tools installed in the production workflow.
EN/NL PDF equity-curve visual gate runs before send.
Dutch PDF product-name corruption gate runs before send.
Manifest evidence validator added.
Manifest evidence gate runs after final run-manifest write.
Latest run #247 succeeded after these gates were wired.
```

The PDF visual validator renders committed PDFs to images and requires a visible equity curve in English and Dutch. The manifest evidence validator checks latest run/delivery manifests, attached PDFs, EN/NL language coverage, pricing lineage, and the delivery caveat.

## Deterministic macro boundary

Current deterministic macro state remains:

```text
macro report surface: integrated as client-safe only
deterministic macro read as raw/shadow object: not client-facing
deterministic macro read as official decision/regime source: not promoted
```

Do not infer deterministic macro promotion from WP16, WP17, or their follow-ups.

Standing authority boundary:

```text
client_facing_narrative_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
delivery_authority=false
execution_authority=false
production_report_mutation=false
```

## Historical artifact policy

WP15 remains active:

```text
historical_output_artifacts_are_immutable_by_default=true
current_baseline_scope=manifest_linked_latest_report_set
historical_output_mutation=false
```

WP16/WP17 did not manually rewrite historical report artifacts. Current production truth is tied to the latest manifest-linked report/runtime/pricing/delivery artifacts.

## Four-layer operating status

### 1. Decision framework

- WP16 repaired report-surface QA and macro-event recency handling.
- WP17 hardened visual PDF QA and delivery-runbook evidence.
- Neither WP16 nor WP17 altered scoring, fundability, execution authority, or portfolio authority.
- Neither WP16 nor WP17 promoted deterministic macro.
- ETF/product names are protected product terms and must not be translated by Dutch localization.

### 2. Input/state contract

- Current production truth remains tied to manifest-linked runtime/pricing/delivery artifacts.
- Uploaded PDFs are QA evidence, not source-of-truth state.
- Latest pricing lineage is passed for all 9 holdings.

### 3. Output contract

- Future reports must not expose empty-comment residue, duplicated soft-cap wording, English/Dutch language leakage, Dutch equity-curve clipping, invisible charts, or product-name localization corruption such as `iAantal aandelen`.
- PDF visual validation is now part of the pre-send gate.

### 4. Operational runbook

- Do not claim inbox delivery; the latest delivery evidence is `smtp_sendmail_returned_no_exception` plus delivery manifest.
- Manual GitHub Actions starts may still be required when run-queue pushes do not automatically trigger the workflow.
- Latest successful report baseline after WP17 is `260612_08`.

## Immediate next action

Return to the roadmap proper.

Recommended next package:

```text
WP18 — Macro/thesis roadmap Phase 2: macro audit foundation
```

Scope should remain shadow/audit-only unless a separate promotion contract explicitly grants authority.
