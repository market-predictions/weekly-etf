# Weekly ETF Cockpit Surface Roadmap — Current Status

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`

## Historical completion

```text
WP01: merged in PR #52
WP02: merged in PR #52
WP03: merged in PR #53
WP04: merged in PR #54
WP05: merged in PR #55
WP06: merged in PR #56
WP07: merged in PR #57
current-runtime revalidation: merged in PR #74
WP08 evidence review: merged in PR #76
WP09 refinement: merged in PR #79
WP09 closeout: merged in PR #80
promotion decision: merged in PR #81
promotion decision closeout: merged in PR #82
```

## Stable boundary

```text
classic_report_evidence_layer: preserved
one email body per language: preserved
one PDF per language: preserved
attachment_contract: unchanged
manifest_contract: unchanged
portfolio/pricing/execution authority: unchanged
promotion_status: not_promoted
```

## Evidence-based review status

```text
schema_version: cockpit_side_by_side_review_v2
review_conclusion: ready_for_promotion_decision
blocking_findings: []
all_eleven_dimensions: pass
```

## Selected production relationship

```text
selected_option: additive_delivery_front_page
integration_layer: delivery HTML/PDF render pipeline
complete classic report body: preserved
small decision cockpit: suppressed only when full front page succeeds
feature gate: required
feature default: disabled
failure behavior: classic output
rollback: disable feature flag
```

## WP10 additive delivery front page

```text
package: WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE
status: validated_ready_for_enablement_decision
PR: #83
validated_code_head: b2ca4b032793f23f13b0d4557a919623366dc501
final_validation_run: 29541727393
visual_artifact_run: 29542004498
feature_flag: MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled|enabled
feature_default: disabled
production_enablement: false
email_sent: false
promotion_status: not_promoted
```

WP10 passes disabled, enabled and fail-closed validation:

```text
disabled EN/NL HTML byte-identical: true
enabled EN/NL front-page count: one each
enabled EN/NL PDF page addition: one each
classic report body preserved: true
small decision cockpit duplicate: false
standalone equity embed: passed
email equity CID: passed
attachment/manifest changes: false
protected authority mutation: false
WP08 blockers: none
```

Persistent evidence:

```text
control/evidence/COCKPIT_WP10_ADDITIVE_DELIVERY_FRONT_PAGE_EVIDENCE_20260717.json
```

## Next package

```text
WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
status: next_after_WP10_merge
promotion_status: not_promoted
```

WP11 must decide whether to enable the explicit feature flag in `.github/workflows/send-weekly-report.yml`. No send is authorized by WP10, and rollback must remain a single switch to `disabled`.
