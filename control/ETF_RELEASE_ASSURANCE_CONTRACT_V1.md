# Weekly ETF Release Assurance Contract V1

## Status

```text
contract_id=ETF_RELEASE_ASSURANCE_CONTRACT_V1
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
project=market-predictions/weekly-etf
current_maturity=LEVEL_3_HARD_CI_GATE
target_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
```

## Purpose

Prevent the Weekly ETF implementation and rendering path from certifying its own delivery readiness.

The production report is a release candidate until a separate, fail-closed assurance reconstruction returns `PASS`. The user continues to issue one project instruction and receives one consolidated status.

## Pre-send release identity

The assurance record must bind:

- source commit SHA;
- GitHub workflow run ID when available;
- ETF pricing run ID;
- requested close date;
- report token;
- immutable pricing-audit path;
- runtime-state path;
- run-manifest path;
- official portfolio-state path;
- official trade-ledger path;
- English and Dutch report paths;
- English and Dutch delivery HTML paths;
- English and Dutch PDF paths;
- English and Dutch equity-curve PNG paths;
- SHA-256 for every required evidence and client artifact.

## Mandatory checks

A pre-send `PASS` requires:

1. valid and complete source/run/date/token identity;
2. every required file exists and has the expected format;
3. control JSON is parseable;
4. run manifest binds run ID, requested close date, report token, pricing audit, runtime state and both reports;
5. pricing audit binds the requested close and pricing run;
6. runtime state binds the requested close and pricing audit;
7. official portfolio state and trade ledger are present and hashed;
8. English and Dutch report tables have equivalent normalized financial numeric content;
9. all client artifacts have complete SHA-256 identities;
10. implementation and assurance roles are distinct;
11. the resulting assurance record validates against the expected current identity.

Missing or contradictory evidence returns `FAIL`; it is never inferred as acceptable.

## Hard-gate location

`send_report_runtime_html.py` invokes the assurance builder and validator immediately before `send_report.main()` performs transport.

SMTP transport is therefore unreachable when assurance fails. The gate output is persisted under `output/run_manifests/`, which is already part of the production artifact commit-back scope.

## Allowed statuses

```text
RELEASE_CANDIDATE_READY
GOVERNANCE_FAIL
GOVERNANCE_PASS_PRE_SEND
TRANSPORT_SENT_UNVERIFIED
DELIVERY_CONFIRMED
```

`GOVERNANCE_PASS_PRE_SEND` is not proof of delivery.

## Post-action confirmation

LEVEL 4 remains dependent on independent receiving-system evidence for both languages plus a delivery manifest bound to the same artifact hashes. SMTP return without exception is only `TRANSPORT_SENT_UNVERIFIED`.

## Prohibited behavior

- implementation may not write its own `PASS` without the independent validator accepting the record;
- the assurance path may not mutate portfolio state, ledger, reports or pricing evidence;
- a failed candidate must return to implementation and receive a new assurance pass;
- English success may not bypass Dutch failure;
- rendering success may not be reported as delivery confirmation.
