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

---

## Active package

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```

Current status:

```text
started / validator green / pending fresh report artifact / not closed
```

Status files:

```text
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_VISUAL_QA_STATUS.md
output/macro/validation/deterministic_regime_report_visual_qa_partial_20260613_codespace.json
```

Generate fresh reports:

```bash
PYTHONPATH=. python runtime/render_etf_report_from_state.py --output-dir output
```

Then use the exact paths printed by the renderer:

```bash
grep -nE "Deterministic regime read|Deterministische regime-inschatting" <fresh_en_path> <fresh_nl_path>
grep -nE "macro_axes|macro_axis_scores|macro_evidence|confidence_decomposition|workflow_run_id|commit_sha|output/macro/validation" <fresh_en_path> <fresh_nl_path>
```

Close WP27 only after the fresh EN/NL report artifacts are inspected and evidence is recorded.
