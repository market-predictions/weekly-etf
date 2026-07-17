# Decision — WP10 additive delivery front-page feature gate

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Status: validated implementation / production enablement not granted

## Decision

The cockpit may enter the production delivery architecture only as an additive first page inside the existing English and Dutch HTML/PDF report.

```text
classic report evidence body: preserved
email body count: unchanged
PDF count: unchanged
attachment contract: unchanged
manifest contract: unchanged
```

The implementation is controlled by exactly:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled|enabled
```

## Default and rollback

```text
missing value: disabled
implementation default: disabled
invalid value: fail closed to classic output
render/injection failure: fail closed to classic output
rollback: set disabled
production enablement: separate WP11 decision
```

No implicit truthy or falsey aliases are accepted.

## Duplicate-surface rule

When the full front page is successfully enabled, the smaller injected `Decision cockpit / Besliscockpit` is suppressed. In disabled or fallback mode, the smaller cockpit remains available.

## Evidence

```text
final validation run: 29541727393
visual artifact run: 29542004498
front page count EN/NL: one each
added PDF pages EN/NL: one each
classic report body: preserved
disabled HTML byte-identical: true
WP08 blockers: none
protected authority mutation: false
email_sent: false
promotion_status: not_promoted
```

Persistent evidence:

```text
control/evidence/COCKPIT_WP10_ADDITIVE_DELIVERY_FRONT_PAGE_EVIDENCE_20260717.json
```

## Consequence

WP10 validates the feature but does not enable it in `.github/workflows/send-weekly-report.yml`.

Actual production enablement requires:

```text
WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
```

WP11 must perform a validate-only enabled replay before any send and preserve immediate rollback to `disabled`.
