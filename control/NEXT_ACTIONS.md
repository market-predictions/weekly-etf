# ETF Review OS — Next Actions

## Current production baseline

```text
baseline: 260612_08
run_id: 20260613_113054
workflow_status: workflow_success
delivery_status: smtp_sendmail_returned_no_exception
```

Delivery evidence remains delivery-layer evidence only and is not an inbox receipt.

---

## Closed packages

```text
WP16: closed
WP17: closed
WP18: closed
WP19: closed
WP20: closed as not_promoted
WP21: closed as design-only
WP22: closed as manually validated
WP23: closed as manually validated
WP24: closed as review-only
WP25: closed as proposal-only
WP26: closed as manually validated
```

WP26 evidence:

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_IMPLEMENTATION_STATUS.md
output/macro/validation/deterministic_regime_report_integration_validation_20260613_codespace.json
```

---

## Active package

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```

Current status:

```text
started / pending fresh report artifact / not closed
```

Status file:

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_VISUAL_QA_STATUS.md
```

Required next step:

```text
generate or provide a fresh EN/NL report artifact after the WP26 commits
```

Minimum local checks after fresh report generation:

```bash
rg "Deterministic regime read|Deterministische regime-inschatting" output/weekly_analysis_pro*.md
rg "macro_axes|macro_axis_scores|macro_evidence|confidence_decomposition|workflow_run_id|commit_sha|output/macro/validation|\.json" output/weekly_analysis_pro*.md
```

Close WP27 only after fresh EN/NL report output is inspected and evidence is recorded.
