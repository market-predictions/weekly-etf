# Handover — Weekly ETF fix-verification delivery

Date: 2026-07-19
Repository: `market-predictions/weekly-etf`
Work package: `WP_WEEKLY_ETF_FIX_VERIFICATION_DELIVERY`
Status: closed / delivered / inbox confirmed

## Outcome

The persisted bilingual report for run `20260719_002755` was rendered, sent and received after the cockpit trade-weight lineage correction.

Received cockpit text:

```text
English: PAVE 0.0% → 4.9%; XLU 5.5% → 0.5%.
Dutch:   PAVE 0,0% → 4,9%; XLU 5,5% → 0,5%.
```

This confirms that the fix is present in the actual receiving-mail-client body, not only in a test fixture or local renderer.

## Delivery package

```text
English PDF: output/weekly_analysis_pro_260717_04.pdf
English HTML: output/weekly_analysis_pro_260717_04_delivery.html
Dutch PDF: output/weekly_analysis_pro_nl_260717_04.pdf
Dutch HTML: output/weekly_analysis_pro_nl_260717_04_delivery.html
delivery manifest: output/delivery/weekly_etf_delivery_manifest_2026-07-17_20260719_002755.json
run manifest: output/run_manifests/weekly_etf_run_manifest_2026-07-17_20260719_002755.json
```

Both messages include four attachments: PDF, clean Markdown, delivery HTML and equity-curve PNG.

## Validation

```text
implementation_pull_request: 111
implementation_merge: d3d4960b3611fe54f5db6d5ef2d3608fc2f6ac34
no_send_recovery_validation_run: 29667585209 success
full_render_boundary_run: 29667585181 success
delivery_authorization_commit: 58f16df50309e30b5d5f3c3b5e2f4b37200c50ce
delivery_evidence_commit: 8ae50d7ccfe931dd9be5a9008b41570d32f4fdff
SMTP result: no exception
English inbox receipt: confirmed
Dutch inbox receipt: confirmed
```

## Authority boundary

The recovery was report-only. It produced a guarded `not_authorized` execution artifact and did not repeat portfolio execution, authorize broker execution, or mutate the official portfolio state, trade ledger or valuation history.

## Stable rule

The source run is closed against automatic resend. Future reports use the upstream trade-lineage contract. Any resend of this package requires a new explicit authorization and duplicate-delivery review.
