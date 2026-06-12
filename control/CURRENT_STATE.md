# ETF Review OS — Current State

## Snapshot date
2026-06-12

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 macro event recency and report-surface QA repair is implemented, and a WP16 follow-up repair has now been committed for the two remaining client-surface defects found in `260611_02`: visible empty-comment residue in the Dutch replacement-analysis surface and duplicated soft-cap / zachte-bovengrens constraint wording. A new follow-up rerun request has been created. Clean final delivery is still not proven until the new workflow run produces valid GitHub Actions, run-manifest, delivery-manifest, pricing-lineage, and persisted EN/NL artifact evidence. Deterministic macro remains not promoted. Historical generated outputs remain immutable by default.**

## Latest verified clean baseline before WP16 repair cycle

```text
requested_close_date: 2026-06-10
run_id: 20260610_211606
report_token: 260610
english_report_path: output/weekly_analysis_pro_260610_02.md
dutch_report_path: output/weekly_analysis_pro_nl_260610_02.md
pricing_lineage_status: passed
delivery_status: smtp_sendmail_returned_no_exception
```

Delivery evidence remains delivery-layer evidence only. It is not an end-recipient inbox receipt.

## WP16 rerun review status

Uploaded `260611_02` PDFs show the main WP16 macro fixes landed:

```text
ECB stance now surfaces as Tightening / inflation-sensitive / Verkrappend / inflatiegevoelig.
ECB rate-policy tightening is included as a report policy catalyst.
Non-U.S. developed exposure is mostly reconciled with active IEFA exposure.
English performance tables now use n/a instead of n.v.t.
English equity-curve chart renders visibly.
```

Remaining defects confirmed in `260611_02`:

```text
Dutch replacement-analysis surface still exposes visible empty-comment residue.
English and Dutch continuity constraints duplicate the soft-cap / soft-target wording.
```

## WP16 follow-up repair status

```text
WP16-FOLLOWUP — Empty-comment and constraint-copy repair: implemented / rerun requested / delivery not yet verified
```

Files changed by follow-up:

```text
runtime/scrub_etf_client_surface.py
runtime/client_facing_sanitizer.py
tests/test_wp16_report_surface_qa_contract.py
tools/validate_etf_dutch_client_surface_clean.py
control/run_queue/weekly_etf_report_request_20260612_wp16_followup_rerun.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

Follow-up source changes:

```text
Markdown scrub now removes raw and escaped empty-comment artifacts.
Constraint-copy scrub is idempotent and rewrites entire constraint lines to one canonical sentence.
Delivery HTML sanitizer removes escaped empty-comment artifacts before PDF/email rendering.
WP16 regression tests now cover escaped empty comments and idempotent constraint copy.
Dutch client-surface validator now fails on empty-comment residue and duplicated Dutch constraint wording.
```

Rerun request:

```text
control/run_queue/weekly_etf_report_request_20260612_wp16_followup_rerun.md
```

## Deterministic macro boundary

Current deterministic macro state remains:

```text
macro report surface: integrated as client-safe only
deterministic macro read as raw/shadow object: not client-facing
deterministic macro read as official decision/regime source: not promoted
```

Do not infer deterministic macro promotion from WP16 or WP16-FOLLOWUP.

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

WP16-FOLLOWUP did not manually rewrite historical report artifacts. A clean report must be produced by workflow rerun.

## Four-layer operating status

### 1. Decision framework

- WP16-FOLLOWUP repairs client-surface QA only.
- It does not alter scoring, fundability, execution, delivery authority, or portfolio authority.
- It does not promote deterministic macro.

### 2. Input/state contract

- Current production truth remains tied to manifest-linked runtime/pricing/delivery artifacts.
- Uploaded PDFs are QA evidence, not source-of-truth state.

### 3. Output contract

Future reports should not expose empty comment residue and should not duplicate soft-cap / soft-target constraint wording.

### 4. Operational runbook

Do not claim successful report delivery until the follow-up rerun is verified through GitHub Actions, run manifest, delivery manifest, pricing lineage, and persisted EN/NL artifacts.

## Immediate next action

Verify the WP16 follow-up rerun:

```text
control/run_queue/weekly_etf_report_request_20260612_wp16_followup_rerun.md
```

Required verification:

```text
GitHub Actions run success
run manifest exists
delivery manifest exists
English/Dutch reports exist
pricing lineage passes
Dutch empty-comment residue absent
English/Dutch constraint duplication absent
ECB policy catalyst still appears
ECB stance remains Tightening / inflation-sensitive
non-U.S. exposure wording remains reconciled with IEFA
English n.v.t. residue remains absent
Dutch equity-curve render checked
```
