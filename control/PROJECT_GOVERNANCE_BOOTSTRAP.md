# Weekly ETF — Project Governance Bootstrap

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
canonical_standard_location=https://github.com/market-predictions/control-plane/blob/main/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
canonical_location_status=CANONICAL_ACTIVE
project_repository=market-predictions/weekly-etf
project_risk_class=financial_report_delivery_and_portfolio_state
adoption_status=enforced
enforcement_maturity=LEVEL_3_HARD_CI_GATE
target_enforcement_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
project_specific_assurance_contract=control/ETF_RELEASE_ASSURANCE_CONTRACT_V1.md
project_specific_assurance_contract_status=ENFORCED
production_action=bilingual_report_generation_and_email_delivery
post_action_confirmation=delivery_manifest_and_independent_bilingual_inbox_receipt
```

## User interface

The user gives one Weekly ETF instruction and receives one consolidated project status. The user does not separately coordinate the implementation and assurance roles.

## Enforced pre-send assurance

The production delivery entrypoint reconstructs and validates a release-assurance record before transport. It binds the source SHA, run/date/token identity, pricing audit, runtime state, run manifest, official portfolio state, trade ledger, English and Dutch report/render artifacts, bilingual table-number parity, and exact SHA-256 identities.

A failed or incomplete record prevents the delivery entrypoint from calling the SMTP transport layer.

The hard gate is implemented by:

- `control/ETF_RELEASE_ASSURANCE_CONTRACT_V1.md`
- `tools/etf_release_assurance.py`
- `send_report_runtime_html.py`
- `tests/test_etf_release_assurance.py`
- `.github/workflows/validate-etf-release-assurance.yml`

## Remaining LEVEL 4 boundary

The project is not recorded at LEVEL 4 until the delivery manifest and independent receiving-system confirmation for both languages are machine-bound to the same release identity and artifact hashes. SMTP return without exception remains `TRANSPORT_SENT_UNVERIFIED`.

## Session read rule

For production, release, delivery, portfolio mutation, or completion claims, read this file after:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`

Then read the minimum relevant execution and assurance files.

## Prompt invocation

Operational prompts should include only this short clause:

```text
Apply the project's implementation-versus-release-assurance separation. Treat all generated output as a release candidate until independent assurance passes. Do not let implementation certify its own completion. Report action execution separately from independently confirmed outcome.
```
