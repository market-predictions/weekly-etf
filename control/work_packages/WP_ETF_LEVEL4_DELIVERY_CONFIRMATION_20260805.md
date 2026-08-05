# Work Package — ETF LEVEL 4 Delivery Confirmation

```text
work_package_id=WP_ETF_LEVEL4_DELIVERY_CONFIRMATION_20260805
owner_role=implementation_operations
review_role=governance_release_assurance
status=IN_PROGRESS
repository=market-predictions/weekly-etf
current_maturity=LEVEL_3_HARD_CI_GATE
target_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
portfolio_mutation=false
report_generation=false
email_delivery=false
```

## Objective

Bind the post-send delivery manifest and independent receiving-system evidence for both languages to the exact pre-send release-assurance identity and artifact hashes.

## Required implementation

- machine-readable inbox-receipt evidence schema;
- deterministic closeout builder and validator;
- positive and planted-failure tests;
- CI workflow that validates the post-action contract;
- explicit separation between SMTP acceptance and confirmed inbox receipt;
- control-file and adoption-register updates only after independent validation passes.

## Acceptance criteria

A `DELIVERY_CONFIRMED` closeout requires:

1. pre-send release assurance decision `PASS`;
2. exact run ID, close date, report token, and source SHA agreement;
3. delivery manifest for the same run;
4. English and Dutch receiving-system receipts;
5. recipient hashes match the delivery manifest without exposing addresses;
6. received subjects and attachment names identify the expected language package;
7. exact report/PDF/HTML/equity-curve hashes match the pre-send assurance record;
8. receipt timestamps are after transport timestamps;
9. implementation and assurance roles remain distinct;
10. a failed or incomplete candidate returns `FAIL`, never an inferred confirmation.

## Boundary

This work package installs and validates the mechanism. It does not itself authorize a fresh report, portfolio mutation, workflow dispatch, or email send.
