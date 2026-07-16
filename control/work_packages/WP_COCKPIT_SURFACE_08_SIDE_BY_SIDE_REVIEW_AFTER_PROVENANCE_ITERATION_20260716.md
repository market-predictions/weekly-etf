# Work Package — WP_COCKPIT_SURFACE_08_SIDE_BY_SIDE_REVIEW_AFTER_PROVENANCE_ITERATION

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp08-evidence-side-by-side-review`

## Layer

```text
decision framework
output contract
operational runbook
```

## Status

```text
claimed
promotion_status: not_promoted
```

## Purpose

Perform an evidence-based side-by-side review of the current July 14 classic report and the corrected current-runtime cockpit after the source/provenance iteration.

The existing WP04 review builder is a historical foundation. WP08 must not repeat its static June conclusions. It must inspect the selected current artifacts, record pass/fail findings for the required dimensions, produce a clear review conclusion and identify the narrow next package.

## Authority inputs

```text
output/runtime/latest_etf_report_state_path.txt
output/weekly_analysis_pro_260714_04.md
output/weekly_analysis_pro_260714_04_delivery.html
output/weekly_analysis_pro_nl_260714_04.md
output/weekly_analysis_pro_nl_260714_04_delivery.html
output/cockpit_preview/weekly_analysis_pro_cockpit_260714_<seq>.html
output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260714_<seq>.html
output/etf_valuation_history.csv
output/pricing/latest_price_audit_path.txt
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
```

The runtime state and pointers remain authoritative. The report sources are review surfaces, not independent state authority.

## Required review dimensions

```text
readability
density
visual_hierarchy
decision_clarity
executed_action_clarity
current_weight_accuracy
performance_risk_accuracy
trust_provenance_clarity
bilingual_semantic_parity
premium_look_and_feel
audit_evidence_preservation
```

## Required findings contract

The review metadata must record for each dimension:

```text
status: pass | partial | fail
classic_observation
cockpit_observation
evidence
required_fix
```

It must also record:

```text
selected current classic source per language
selected current cockpit source per language
runtime-state source
report token and date
review conclusion
blocking findings
next recommended package
promotion_status: not_promoted
```

## Current defects already evidenced

The WP08 baseline review has identified these issues that the new review contract must capture rather than hide:

1. The historical builder selects every report variant for the token instead of one current canonical baseline per language.
2. The historical builder emits static prose and does not inspect report or cockpit contents.
3. The historical builder still says source linkage must become explicit even though WP07 added a visible source/evidence strip.
4. The current cockpit summary says discipline is ahead of activity even though URNM was reduced and XBI was added.
5. The Dutch discipline sentence ends with a comma because punctuation is changed by whole-sentence replacement.
6. The cockpit lacks a dedicated explicit next-action trigger even though the classic decision cockpit contains one.

WP08 reviews and records these issues. Product-surface corrections belong to the next narrow preview-only package.

## Output contract

Write only under:

```text
output/cockpit_review/
```

Expected files:

```text
weekly_etf_cockpit_side_by_side_review_<token>.json
weekly_etf_cockpit_side_by_side_review_<token>.md
weekly_etf_cockpit_side_by_side_review_<token>.html
weekly_etf_cockpit_side_by_side_review_nl_<token>.md
weekly_etf_cockpit_side_by_side_review_nl_<token>.html
```

The HTML must be a readable client-grade review surface, not escaped Markdown inside a `<pre>` block.

## Safety boundary

```text
production_promotion: false
production_report_replacement: false
email_send: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
valuation_history_mutation: false
delivery_manifest_creation: false
preview_output_only: output/cockpit_preview/
review_output_only: output/cockpit_review/
```

## Minimum validation

```text
python -m py_compile runtime/build_cockpit_side_by_side_review.py
pytest -q tests/test_cockpit_side_by_side_review.py tests/test_cockpit_wp08_evidence_review.py
python tools/validate_etf_delivery_html_contract.py --output-dir output
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
render current bilingual cockpit preview
build WP08 review
prove protected authority hashes unchanged
```

## Acceptance

- one current classic baseline per language is selected deterministically;
- one latest current cockpit baseline per language is selected deterministically;
- findings are derived from artifact content and runtime state;
- the review exposes current gaps rather than repeating historical template language;
- English and Dutch review surfaces are semantically parallel;
- HTML is visually structured and readable;
- review conclusion remains non-promotional;
- the next package is explicit;
- no authority or delivery file is mutated.

## Expected conclusion boundary

WP08 may conclude:

```text
iteration_required
ready_for_promotion_decision
```

It may not itself promote the cockpit. Based on the evidenced baseline defects, the expected initial conclusion is `iteration_required` and the likely next package is a narrow current-runtime cockpit refinement package.
