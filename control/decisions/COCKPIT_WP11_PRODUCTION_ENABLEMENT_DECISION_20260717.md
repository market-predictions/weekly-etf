# Cockpit WP11 Production Enablement Decision

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT`
Status: accepted / validated / no send

## Decision

Enable the additive cockpit front page in the real Weekly ETF production workflow.

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: enabled
```

The rollback value remains:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: disabled
```

## Rationale

WP10 proved the additive front-page implementation against the classic delivery contract. WP11 then replayed the production bundle against an exact-current temporary overlay built from the latest persisted runtime context and the current whole-share-compliant official portfolio state.

The evidence proves:

```text
English enabled front pages: 1
Dutch enabled front pages: 1
English PDF page delta: +1
Dutch PDF page delta: +1
classic report body: preserved
small decision cockpit duplicate: false
whole-share official state: compliant
protected authority hashes: identical
email sent: false
```

The front page reconciled to:

```text
NAV EUR: 107117.94
cash EUR: 2519.05
position count: 8
largest position: SMH
```

## Authority boundaries

This decision grants production output-contract authority only to the additive cockpit front page.

It does not grant or change:

```text
pricing authority
macro or thesis narrative authority
lane-scoring authority
fundability authority
portfolio-action authority
portfolio-model execution authority
state mutation authority
trade-ledger mutation authority
email-delivery authority
historical report mutation authority
```

A future report send still requires a separate explicit production request. Delivery may be claimed only from a real run manifest and delivery receipt/evidence.

## Failure and rollback behavior

- Invalid feature values fail closed to the unchanged classic output.
- Front-page render failure preserves the classic report and smaller decision cockpit.
- Operational rollback requires setting `MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled`.
- The full classic EN/NL report remains present after the additive page.

## Evidence

```text
control/evidence/COCKPIT_WP11_PRODUCTION_ENABLEMENT_EVIDENCE_20260717.json
validation run: 29582753816
current-runtime regression run: 29582753774
WP08 evidence regression run: 29582753837
```
