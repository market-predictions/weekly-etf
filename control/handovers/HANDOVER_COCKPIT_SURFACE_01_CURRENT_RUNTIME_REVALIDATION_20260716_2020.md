# Handover — WP_COCKPIT_SURFACE_01_CURRENT_RUNTIME_REVALIDATION

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp01-current-runtime-revalidation`
PR: #74
Status: implementation validated / governance reconciliation ready for final check

## Package title

```text
WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_CURRENT_RUNTIME_REVALIDATION
```

## Historical implementation status

The original cockpit implementation was not recreated.

```text
WP01 renderer and WP02 workflow: PR #52
WP03 visual/state contracts: PR #53
WP04 side-by-side review: PR #54
WP05 promotion review: PR #55
WP06 iteration path: PR #56
WP07 source/provenance iteration: PR #57
```

```text
promotion_status: not_promoted
selected_path: iteration
```

## Claim status

No open cockpit PR or active cockpit branch existed at claim time. The historical June WP01 handover was implementation evidence, not an active claim.

The package was claimed on:

```text
feature/cockpit-wp01-current-runtime-revalidation
```

## Current issue

The existing renderer predated the July post-execution authority work.

It selected:

```text
previous_weight_pct before current_weight_pct
previous_market_value_eur before market_value_eur
```

It also rendered an executed mutation only as:

```text
Portfolio action — Action present in runtime state.
Portefeuilleactie — Actie aanwezig volgens runtime state.
```

## Root cause

The June preview renderer used continuity fields as presentation defaults. That was acceptable for the original fixtures but became incorrect after the runtime state gained authoritative post-execution values and action deltas.

The use of Python `or` also treated a legitimate numeric zero as missing, allowing stale non-zero historical values to leak into the preview.

## Authority inspected

```text
output/runtime/latest_etf_report_state_path.txt
output/runtime/etf_report_state_20260714_20260715_175910_executed.json
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
output/etf_valuation_history.csv
output/pricing/latest_price_audit_path.txt
output/pricing/price_audit_2026-07-14_20260715_175910.json
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/run_manifests/weekly_etf_run_manifest_2026-07-14_20260715_175910.json
output/macro/latest.json
```

## Files changed

```text
runtime/render_cockpit_front_page.py
tests/test_cockpit_current_runtime_authority.py
tests/test_report_decision_clarity.py
.github/workflows/validate-cockpit-current-runtime.yml
control/work_packages/WP_COCKPIT_SURFACE_01_PREVIEW_RENDERER_20260618.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
control/decisions/COCKPIT_CURRENT_RUNTIME_AUTHORITY_DECISION_20260716.md
control/handovers/HANDOVER_COCKPIT_SURFACE_01_CURRENT_RUNTIME_REVALIDATION_20260716_2020.md
```

## What was implemented

### Current-value precedence

```text
current_weight_pct
then target_weight_pct
then previous_weight_pct
then weight_inherited_pct
```

```text
market_value_eur
then previous_market_value_eur
```

The resolver checks field presence rather than truthiness, so zero remains authoritative.

### Executed-action surface

The cockpit now derives action wording and weight transitions from the current runtime positions.

For the July 14 state:

```text
EN title: URNM reduced · XBI added
EN note: URNM 7.0% → 2.0%; XBI 0.0% → 5.0%.

NL title: URNM afgebouwd · XBI toegevoegd
NL note: URNM 7,0% → 2,0%; XBI 0,0% → 5,0%.
```

No ticker or weight is hardcoded in renderer logic. The exact July values appear only in the regression fixture and current CI evidence.

### Existing design preserved

The original cockpit HTML structure, CSS, masthead, cards, equity sparkline, metrics, discipline point and source/provenance strip remain intact.

No new card or visual redesign was introduced.

## What was not implemented

```text
no production promotion
no classic report replacement
no email send
no delivery-path change
no portfolio model execution
no pricing change
no target-weight change
no state or ledger write
no valuation-history mutation
no run-manifest mutation
no delivery-manifest creation
no ETF EU / UCITS work
```

## English/Dutch parity findings

The action title and weight-transition note are generated from the same action list and authority fields. The language-specific difference is limited to the reader-facing verbs and decimal punctuation.

The existing Dutch cockpit labels and provenance wording remain unchanged.

## Workflow safety findings

The existing manual preview workflow remains:

```text
workflow_dispatch only
contents: read
no SMTP secrets
no email step
no production send script
no portfolio model execution
no state persistence
artifact upload only
```

The new PR validator is also read-only. It renders preview/review artifacts only inside the CI workspace and uploads them as workflow artifacts.

## Tests and validators

Implementation validation head:

```text
e605eb8de532eed44ec9c44a7be7c6705f128893
```

Validation run:

```text
29525632206 — success
```

Results:

```text
33 focused tests passed
ETF delivery HTML contract passed
macro/thesis surface leakage validator passed
bilingual current-runtime cockpit rendered
side-by-side review rendered
promotion_status: not_promoted
protected-file SHA-256 comparison: identical
```

A stale pair of case-sensitive assertions in `tests/test_report_decision_clarity.py` was corrected to preserve the same semantic assertion while accepting the currently valid sentence capitalization. No product wording changed for that correction.

## Protected hashes before and after

The following SHA-256 values were identical before and after validation:

```text
f18fbd032f7ef7bddce4aa52abe825d10b76857b94c09aae20ef634a16624172  output/etf_portfolio_state.json
1c2d357d5e0e94320bfe253c0b15fb7677d36abbbd907b313755691eb27ff77d  output/etf_trade_ledger.csv
174ecd7b2df2f321fecf23fb846fd78b3a8d08bc36c8d52836203402777644b5  output/etf_valuation_history.csv
ded83fe32eebd1b70109ee538928f57f8cb821f06fa2ee92f3559286a1284065  output/pricing/latest_price_audit_path.txt
94c439aa5a4125a49142a7ddaca27182bd853c852585c85762b6c7a95f1aa970  output/pricing/price_audit_2026-07-14_20260715_175910.json
6278e7e2f9a1302da6ac515a6e9e1ab6436da89bb03b71f6f641500a06136708  output/run_manifests/latest_weekly_etf_run_manifest_path.txt
513769c84dad3d571b7b480b55299d0af4e61e5dc93608dbc9697668859da883  output/run_manifests/weekly_etf_run_manifest_2026-07-14_20260715_175910.json
8cbb41880ed564df07ea4e5e8a06b7729e494f5e81e7296f1c3e2b287e0dc639  output/runtime/etf_report_state_20260714_20260715_175910_executed.json
fb0ce58ad7bb4f2c9e0cccad407a31078e7d5ece7d57a00dd64633682a973fac  output/runtime/latest_etf_report_state_path.txt
```

The before and after lists are included in workflow artifact:

```text
cockpit-current-runtime-29525632206
```

## Generated preview/review paths

Generated in CI and uploaded as preview-only evidence:

```text
output/cockpit_preview/weekly_analysis_pro_cockpit_260714_01.html
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260714_01.html
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260714.json
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260714.md
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_260714.html
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_nl_260714.md
output/cockpit_review/weekly_etf_cockpit_side_by_side_review_nl_260714.html
```

These generated artifacts are not committed production files and are not delivery evidence.

## Promotion status

```text
promotion_status: not_promoted
production_report_change: none
delivery_change: none
state_change: none
```

## Remaining risk

The corrected cockpit now requires a fresh coordinator-facing side-by-side assessment against the current July classic report. Technical correctness does not itself establish that the cockpit is ready for attachment or production promotion.

## Next recommended package

```text
WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION
```

WP08 must remain review-only and use the corrected current-runtime surface. It may not make a production change.

## Final closeout fields

```text
PR: #74
final_governance_head: pending exact-head validation
final_validation_run: pending
merge_commit: pending
```
