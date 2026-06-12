# Deterministic Macro Read Promotion Review

## Work package

```text
WP13 — Deterministic macro read promotion review, not implementation
```

## Repository

```text
market-predictions/weekly-etf
```

## Snapshot date

```text
2026-06-12
```

## Layer

```text
decision framework + output contract
```

## Purpose

This review defines what would be required before the deterministic macro read may become a production report narrative source.

This is a review artifact only. It does not promote the deterministic macro read, does not mutate production report behavior, and does not change portfolio, scoring, fundability, funding, execution, delivery, or portfolio-state authority.

## Current baseline preserved

```text
run_id: 20260610_211606
GitHub Actions run: 27306857013
artifact_commit: e2891ca
latest report set: 260610_02
pricing_lineage_status: passed
delivery_status: smtp_sendmail_returned_no_exception
```

Current macro state:

```text
client-safe macro report surface: integrated
raw deterministic macro read: not client-facing
deterministic macro read as official production regime source: not promoted
```

Do not infer promotion from:

```text
green validators
old-vs-new review readiness
macro policy pack existence
client-safe macro surface presence
prior pilot output
prior review artifact
```

## Current authority state

The current promotion decision remains:

```text
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

Required authority boundaries remain:

```text
client_facing_narrative_authority=false until explicitly promoted
production_report_narrative_authority=false until explicitly promoted
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
delivery_authority=false
execution_authority=false
production_report_mutation=false
```

---

## Four-layer distinction

### 1. Decision framework

The decision is whether deterministic macro may replace or supplement the current legacy macro policy pack as the production report narrative source only.

This review does not authorize:

```text
portfolio actions
lane scoring
fundability
funding
portfolio mutation
execution
delivery authority
```

Even after future narrative promotion, those authorities would require separate explicit contracts.

### 2. Input/state contract

The current production macro input remains:

```text
output/macro/latest.json
```

The current deterministic macro evidence remains review-only:

```text
output/macro/pilot/macro_regime_client_surface_pilot_20260605_000000.json
output/macro/review/macro_old_vs_new_review_20260605_000000.json
output/macro/promotion/macro_regime_promotion_decision_20260606_000000.json
```

A future promoted deterministic macro narrative source must be represented by an explicit promotion artifact that satisfies:

```text
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
```

### 3. Output contract

Only a client-safe rendered surface may enter English/Dutch reports.

Raw deterministic fields must never be copied directly into client report Markdown, HTML, PDF, or delivery surfaces.

### 4. Operational runbook

Promotion, if ever approved, must happen in two separate steps:

```text
1. explicit control-layer promotion decision
2. separate production report integration work package
```

WP13 performs neither step. It records the review criteria only.

---

## Six-question promotion review checklist

### 1. What exact deterministic fields would become production narrative source?

No raw deterministic fields become production narrative source directly.

Allowed future source fields are limited to a client-safe deterministic macro report surface derived from the deterministic read and validated before report use.

The current pilot artifact shows the shape of the only acceptable source layer:

```text
client_surface.en.title
client_surface.en.body
client_surface.en.citations
client_surface.en.meaning_claims
client_surface.nl.title
client_surface.nl.body
client_surface.nl.citations
client_surface.nl.meaning_claims
deterministic_macro_candidate_en
deterministic_macro_candidate_nl
```

Use rule:

```text
copy raw deterministic model fields directly: no
copy pilot candidate text directly: no, unless it is regenerated for the active run and passes validators
transform through safe renderer: yes
summarize through safe renderer: yes
map meaning_claims into constrained report language: yes
```

The source must be run-specific. A future production integration must not hardcode the 2026-06-05 pilot wording into a later report.

The allowed semantic concepts are:

```text
macro regime label as descriptive classification
risk tone as descriptive context
leadership breadth as descriptive context
confidence language as evidence-based observation, not forecast probability
explicit no-action authority disclaimer
citation/provenance marker or source reference where required
```

Current `output/macro/latest.json` remains the live macro pack input until a later promotion decision and report-integration package change the input contract.

### 2. What bilingual surface would be allowed?

Allowed English surface:

```text
short deterministic macro title
short deterministic macro body
one concise regime/risk-tone explanation
one explicit authority disclaimer
optional citation/provenance marker
```

Allowed Dutch surface:

```text
korte deterministische macrotitel
korte deterministische macrotekst
één compacte uitleg van regime/risicotoon
een expliciete autoriteitsdisclaimer
optionele bron-/provenanceverwijzing
```

The surface must distinguish:

```text
internal deterministic read: raw model/evidence object, not client-facing
allowed English narrative surface: validated client-safe prose only
allowed Dutch narrative surface: validated native Dutch prose only
renderer/output layer: a dedicated safe renderer or runtime.macro_report_surface-compatible layer
```

The current production client-safe macro surface is:

```text
runtime.build_macro_policy_pack
  -> output/macro/latest.json
  -> runtime.macro_report_surface
  -> runtime.polish_runtime_reports / native report rendering
  -> English/Dutch report sections
```

A future deterministic surface must remain equivalent in discipline: renderer-owned, bilingual, concise, sanitized, and validator-protected.

### 3. What would remain forbidden?

Forbidden fields and concepts include:

```text
deterministic_regime_shadow
macro_axes
macro_axis_scores
macro_evidence
confidence_decomposition components
raw score tables
raw evidence tables
raw model axis calculations
shadow/internal labels
Stage-1/Stage-2 labels
internal driver IDs
authority field names in client output
predictive macro wording
central-bank certainty wording
uncited overlay claims
orphan macro figures without provenance
portfolio-action wording
fundability wording
funding wording
trade/execution wording
target-weight wording
portfolio-mutation wording
```

Forbidden authority escalation:

```text
macro_direct_lane_scoring_authority
macro_direct_fundability_authority
macro_direct_portfolio_trade_authority
```

Forbidden implementation pattern:

```text
raw deterministic object -> Markdown report
```

Required implementation pattern if later promoted:

```text
raw deterministic object -> validated safe surface -> report renderer -> compliance/leakage/output validators -> delivery guard
```

### 4. What validators must pass?

Required existing validators:

```text
python tools/validate_macro_report_surface.py --macro-pack output/macro/latest.json
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
python tools/validate_macro_compliance.py --macro-pack output/macro/latest.json
python tools/validate_etf_report_content_contract.py --output-dir output
python tools/validate_etf_client_surface_clean.py --output-dir output
python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_macro_regime_promotion_contract.py <promotion_decision_artifact.json>
```

Required future validator:

```text
tools/validate_deterministic_macro_read_promotion_review.py
```

or equivalent coverage added to existing validators.

The future validator should prove:

```text
only allowed deterministic surface fields are used
raw deterministic fields are blocked from report output
English/Dutch candidate surfaces are both present
bilingual meaning parity is preserved
authority flags remain false except narrative flags after explicit promotion
forbidden predictive/portfolio/fundability/execution wording is absent
promotion artifact contains the exact required phrase and boolean
rollback metadata is present
```

A green validator does not by itself promote deterministic macro. It only proves the artifact/output is internally consistent with the contract.

### 5. What explicit control-layer phrase/flag authorizes promotion?

Promotion requires both the exact status phrase and authority boolean:

```text
status=promoted_to_report_narrative_authority
production_report_narrative_authority=true
```

The promotion artifact must also contain:

```text
client_facing_narrative_authority=true
control_layer_decision=promote_to_report_narrative_authority
explicit_control_layer_promotion_decision=true
methodology_approved=true
bilingual_parity_approved=true
compliance_validator_passed=true
old_vs_new_comparison_reviewed=true
blockers=[]
```

Without both:

```text
status=promoted_to_report_narrative_authority
production_report_narrative_authority=true
```

the deterministic macro read remains:

```text
not_promoted
```

Promotion to narrative authority still does not grant:

```text
portfolio_action_authority
lane_scoring_authority
fundability_authority
funding_authority
portfolio_mutation
execution_authority
delivery_authority
```

### 6. What rollback path exists if client output regresses?

Safe rollback path:

```text
1. Revert the future production report integration commit or disable the deterministic macro renderer switch.
2. Restore legacy macro policy pack surface as the report macro source.
3. Keep output/macro/latest.json as the macro report input unless a separate safe fallback pack is explicitly selected.
4. Re-run macro report surface, macro/thesis leakage, macro compliance, client surface clean, report content, and delivery HTML validators.
5. Re-render English/Dutch reports from runtime state.
6. Verify raw deterministic fields remain absent from Markdown, HTML, PDF, and delivery surfaces.
7. Record rollback in CURRENT_STATE.md and NEXT_ACTIONS.md.
```

Rollback must not require:

```text
portfolio-state mutation
trade-ledger mutation
fundability change
scoring change
execution change
cash/holdings change
```

Rollback target:

```text
legacy macro policy pack surface
previous report renderer behavior
previous validator set
previous client-safe output boundary
```

---

## Review conclusion

```text
review_status: completed
promotion_status: not_promoted
production_report_behavior_changed: false
production_report_narrative_authority: false
client_facing_narrative_authority: false
portfolio_action_authority: false
lane_scoring_authority: false
fundability_authority: false
funding_authority: false
portfolio_mutation: false
delivery_authority: false
execution_authority: false
production_report_mutation: false
```

WP13 is complete as a promotion-review checklist only.

The recommended next package is:

```text
WP14 — Deterministic macro read shadow replay evidence
```
