# Handover — Weekly ETF post-execution authority and native Dutch guard-only closure

## Date
2026-06-01

## Repository

```text
market-predictions/weekly-etf
```

## Latest green production evidence

```text
workflow: Send weekly ETF Pro report
run_number: 195
trigger_commit: e0a6f075127f1a079ca880accd26923928349f9c
run_id: 20260601_213417
requested_close_date: 2026-06-01
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
report_authority_source: portfolio_state_post_execution
english_report_path: output/weekly_analysis_pro_260601_04.md
dutch_report_path: output/weekly_analysis_pro_nl_260601_04.md
runtime_state_path: output/runtime/etf_report_state_20260601_20260601_213417.json
pricing_audit_path: output/pricing/price_audit_2026-06-01_20260601_213417.json
portfolio_state_path: output/etf_portfolio_state.json
total_portfolio_value_eur: 110290.91
```

Manifest:

```text
output/run_manifests/weekly_etf_run_manifest_2026-06-01_20260601_213417.json
```

## Delivery boundary

The latest manifest still records:

```text
delivery_manifest_path: null
```

Therefore the repo proves workflow and validation success, but not independent email delivery success. Do not claim delivery unless a delivery receipt/manifest exists or the user confirms receipt.

## Current issue closed

A long production-hardening chain is now closed around:

1. Dutch native-render architecture;
2. Dutch terminology and runtime-state label residue;
3. Dutch PDF chart labels;
4. HTML/PDF render validation;
5. fully exited zero-share position handling;
6. dynamic pricing-basis disclosure;
7. post-execution pricing-lineage authority.

## Root causes found and fixed

### 1. Dutch should not be broad-translated English markdown

The user correctly challenged the architecture: the Dutch report should be independently constructed from the same key figures/runtime state, not produced by broad English-to-Dutch translation/scrub mutation.

Implemented rule:

```text
runtime state / key figures
→ English native render
→ Dutch native render from same runtime state
→ guard-only native Dutch validation
→ delivery HTML/PDF validation
```

Not allowed:

```text
English markdown
→ broad translation / scrub
→ Dutch report
```

### 2. Native Dutch guard-only path exposed real residue

Once broad translation was disabled, validators exposed true native-state residue such as:

```text
Neeg geen alternatief
Non-U.S. developed market diversification
Latest 4 mei close basis; +8 SMH from cash
Runtime valuation from immutable pricing audit and explicit portfolio state
Rotation destination
Long
```

Fix approach: narrow structured runtime-state display-label normalization only. Do not reintroduce broad English-to-Dutch scrub behavior.

### 3. Dutch chart labels were generated inside the PNG/PDF asset path

English chart labels in the Dutch PDF came from the equity-curve image generator, not markdown. Runtime delivery now uses Dutch labels when rendering Dutch markdown:

```text
Portefeuillecurve (EUR)
Portefeuillewaarde (EUR)
Datum
```

### 4. Dutch HTML validator rejected normal HTML newlines

The validator treated a normal newline as raw markdown residue. It now blocks real raw markdown/formatting artifacts while allowing normal HTML line breaks.

### 5. Guarded execution sold GLD to zero

The official active portfolio state omits fully exited positions. The execution artifact can retain a zero-share row for auditability. The execution-state validator now allows absent official-state tickers only if artifact shares/value/weight are effectively zero.

### 6. Pricing-basis disclosure used stale hardcoded tickers

The validator still required GLD after GLD was fully exited. It now derives required pricing rows dynamically from current active Section 15 holdings.

### 7. Pricing-lineage validator compared post-execution report to pre-execution runtime

The client report Section 7/15 reflected post-execution official state, while the validator compared it against pre-execution runtime positions. The validator now separates authority layers:

```text
runtime state = pre-execution pricing/report-state provenance
official portfolio state = post-execution active holdings after guarded execution
client report Section 7 / Section 15 = post-execution official portfolio state when execution occurred in the same run
```

Latest manifest confirms:

```text
report_authority_source: portfolio_state_post_execution
```

## Files changed during closure cycle

Key files changed include:

```text
runtime/apply_nl_localization.py
runtime/scrub_nl_client_language.py
tools/validate_nl_terminology_contract.py
send_report_runtime_html.py
tools/validate_etf_execution_state_authority.py
tools/validate_etf_pricing_basis_disclosure.py
tools/validate_etf_pricing_lineage_contract.py
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

## Four-layer summary

### 1. Decision framework

- Preserve runtime-driven production baseline.
- Preserve guarded model execution.
- Preserve post-execution official portfolio state as the active-holdings authority after execution.
- Preserve macro/thesis roadmap as shadow-first and non-authoritative until promoted.

### 2. Input/state contract

- Runtime state remains pricing/provenance input.
- Official portfolio state is the post-execution active-holdings authority.
- Fully exited zero-share artifact rows may be absent from active official state.
- Pricing-basis required rows come from current active holdings, not a stale hardcoded set.

### 3. Output contract

- English is canonical.
- Dutch is native companion render from the same runtime/key figures.
- Native Dutch is guard-only; no broad English-to-Dutch scrub passes.
- Section 7/15 reconcile to post-execution official state when execution happened in the same run.
- Delivery/PDF success is separate from email delivery receipt.

### 4. Operational runbook

- Continue using `control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md` for ChatGPT-triggered runs.
- Verify workflow results and repo artifacts directly when possible.
- Do not claim delivery without a receipt/manifest or user confirmation.

## Visual PDF inspection boundary

Repo evidence confirms PDFs and the Dutch chart asset exist and validations passed. However, through the current connector the binary PDFs are exposed as base64 text resources rather than mounted sandbox files. Direct visual PDF inspection still requires either:

1. the latest PDFs uploaded into the chat, or
2. an Actions artifact ZIP/download path that can be rendered with the PDF skill.

## Recommended next actions

1. Add a durable delivery receipt/manifest so successful email/PDF delivery can be proven from repo evidence.
2. Upload or expose the latest PDFs for visual inspection.
3. Consolidate Dutch terminology/alias handling into a single source of truth.
4. Continue macro/thesis roadmap through fixture/shadow mode only.
5. Add direct challenger-vs-current-holding scoring as a future model enhancement.

## Suggested next prompt for fresh chat

```text
We are continuing in market-predictions/weekly-etf. Start by reading:
1. control/SYSTEM_INDEX.md
2. control/CURRENT_STATE.md
3. control/NEXT_ACTIONS.md
4. control/handovers/HANDOVER_WEEKLY_ETF_POST_EXECUTION_AUTHORITY_20260601.md

Latest green production run:
- workflow run #195
- run_id: 20260601_213417
- requested_close_date: 2026-06-01
- manifest: output/run_manifests/weekly_etf_run_manifest_2026-06-01_20260601_213417.json
- pricing_lineage_status: passed
- workflow_conclusion: success
- report_authority_source: portfolio_state_post_execution

Do not claim email delivery success unless a delivery receipt/manifest exists or I confirm receipt.

Next task: add durable delivery receipt/manifest evidence and/or visually inspect the latest generated PDFs if I upload them.
```
