# Weekly ETF report request — production validation run

## Purpose

Trigger the production Weekly ETF report workflow from the repo-native run queue to validate the full report flow after adding:

- macro/thesis client-surface leakage guard
- Dutch terminology contract consolidation
- Dutch terminology repo-visible validation evidence

## Requested by

ChatGPT project workflow session

## Validation focus

This run should exercise the production path:

```text
pricing audit
→ relative strength
→ macro policy pack
→ lane discovery
→ challenger pricing
→ portfolio rotation plan
→ runtime EN/NL reports
→ Dutch localization / terminology guards
→ macro/thesis leakage guards
→ delivery HTML validation
→ pricing-lineage pre-send gate
→ PDF/email delivery step
→ final run manifest
```

## Authority boundary

This request does not promote Stage-1, Stage-2, deterministic regime, or macro/thesis artifacts into client-facing authority.

The expected purpose is validation of guardrails and the existing production report pipeline.

## Follow-up verification targets

After the workflow completes, verify from repo artifacts where possible:

```text
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/weekly_analysis_pro_<token>*.md
output/weekly_analysis_pro_nl_<token>*.md
output/weekly_analysis_pro_*_delivery.html
```

And confirm the relevant validators did not block:

```text
validate_etf_macro_thesis_surface_leakage.py
validate_nl_terminology_contract.py / Dutch localization quality path
validate_etf_delivery_html_contract.py
validate_etf_client_surface_clean.py
validate_etf_pricing_lineage_contract.py
```

Do not claim email delivery success unless a delivery receipt/manifest exists or the user confirms receipt.
