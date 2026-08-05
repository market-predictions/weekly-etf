# Weekly ETF — Project Governance Bootstrap

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
canonical_standard_location=https://github.com/market-predictions/weekly-etf-eu/blob/main/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
canonical_location_status=INTERIM_PENDING_CONTROL_PLANE_REPOSITORY
project_repository=market-predictions/weekly-etf
project_risk_class=financial_report_delivery_and_portfolio_state
adoption_status=documented
enforcement_maturity=LEVEL_1_CHECKLIST
target_enforcement_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
project_specific_assurance_contract=control/ETF_RELEASE_ASSURANCE_CONTRACT_V1.md
project_specific_assurance_contract_status=PLANNED
production_action=bilingual_report_generation_and_email_delivery
post_action_confirmation=delivery_manifest_and_independent_bilingual_inbox_receipt
```

## User interface

The user gives one Weekly ETF instruction and receives one consolidated project status. The user does not separately coordinate the implementation and assurance roles.

## Current adoption boundary

This file adopts the shared role separation and status semantics. It does not yet claim that Weekly ETF has a machine-generated independent assurance record or a hard governance gate before delivery.

The existing pricing-lineage, rendering, language, manifest, and receipt controls remain active. They are implementation and closeout evidence, but they must not be described as independent release assurance until the planned project-specific contract and CI gate exist.

## Required project-specific extension

The planned `control/ETF_RELEASE_ASSURANCE_CONTRACT_V1.md` should independently verify at least:

- source SHA and immutable run identity;
- requested close date and pricing audit identity;
- portfolio-state, trade-ledger, valuation-history, and report consistency;
- English and Dutch numeric and section parity;
- exact Markdown, HTML, PDF, and equity-chart artifact hashes;
- delivery authorization scope;
- delivery manifest;
- independent bilingual inbox receipt before confirmed completion.

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
