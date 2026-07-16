# Post-execution correction runbook decision

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Status: accepted

## Decision

Post-execution report correction is a manual, guarded operational runbook with three explicitly separated modes:

```text
validate_only
recover_no_send
send
```

The canonical workflow is:

```text
.github/workflows/resend-corrected-post-execution-report.yml
```

## Authority rules

1. **Send authority**
   - A correction request must contain `send_confirmation: confirm_correction_resend`.
   - The manual workflow dispatch must independently select `confirm_correction_resend`.
   - The correction suffix must be unused; a send may not overwrite an existing correction package.

2. **Mail configuration authority**
   - Only the established `MRKT_RPRTS_*` production mail contract is valid.
   - Legacy `MAIL_*` and `SMTP_*` aliases are not correction-runbook authority.

3. **Delivery evidence authority**
   - Delivery success is established by the persisted `DELIVERY_OK | mode=pro_bilingual` text receipt.
   - The receipt must identify both English and Dutch `*_delivery_manifest.txt` files and confirm both PDFs.
   - JSON file discovery is not the production delivery-receipt contract.

4. **Recovery authority**
   - `recover_no_send` removes all mail configuration, sets the explicit dry-run flag and calls render-only asset generation.
   - Recovery may use a prior positive delivery receipt to reconstruct missing evidence.
   - Recovery may not invoke the mail delivery entrypoint.
   - Recovery is transactional: if existing historical report artifacts would change, their original bytes are restored and the operation fails.
   - Recovery may not overwrite a different historical receipt.

5. **State authority**
   - Every correction operation snapshots the current official portfolio-state and trade-ledger hashes and proves they are unchanged afterward.
   - Historical correction-manifest hashes prove immutability during that historical correction. They are not a requirement that future legitimate production state forever retain the same hash.

## Retired behavior

The one-shot bridge is retired:

```text
.github/workflows/dispatch-corrected-etf-report-bridge.yml
```

Automatic push-triggered correction sends are not permitted.

## Boundary

This decision changes only the correction operational runbook and delivery-evidence contract. It does not change portfolio logic, pricing authority, report recommendations, model execution or ordinary weekly delivery behavior.
