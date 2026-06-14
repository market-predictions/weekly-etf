# Deterministic Regime Report Integration Proposal

## Work package

```text
WP25 — Deterministic regime report integration proposal
```

## Status

```text
closed / proposal-only / implementation-not-started / integration-not-authorized
```

## Scope

WP25 proposes how the deterministic regime safe-surface helper could be integrated in a later implementation package.

WP25 does not implement production report integration, does not promote deterministic macro, and does not change report Markdown, HTML/PDF delivery, portfolio state, lane scoring, fundability, or historical outputs.

## Reviewed chain

```text
WP21 — safe output contract
WP22 — safe-surface validator
WP23 — helper-only DTO/rendering layer
WP24 — review-only integration review
```

## Proposal decision

A later implementation package may be considered with this shape:

```text
future_implementation_package_allowed=true
next_package=WP26 — Deterministic regime report integration implementation, only if explicitly approved
```

This proposal does not grant:

```text
production_report_integration=false
production_report_narrative_authority=false
client_facing_authority=false
automatic_promotion=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```

## Proposed future integration shape

A future implementation package should integrate only the safe surface text, not raw shadow evidence.

Recommended minimal architecture:

```text
latest shadow validation evidence
+ latest shadow comparison evidence
→ build_deterministic_regime_client_surface(...)
→ render_deterministic_regime_surface_en/nl(dto)
→ WP22 validator on rendered text
→ optional insertion into macro dashboard section
```

## Proposed files for a later implementation package

A later WP26 implementation may consider these files only:

```text
runtime/macro_report_surface.py
tools/validate_macro_report_surface.py
tests/test_deterministic_regime_client_surface_helper.py
tests/test_deterministic_regime_client_surface_validator.py
```

Optional support file if needed:

```text
runtime/deterministic_regime_client_surface.py
```

## Proposed report placement

The safest future placement is a short review-only line inside the existing macro dashboard area, after the legacy regime confidence line and before portfolio implications.

English heading should remain visibly review-only:

```text
Deterministic regime read — review-only
```

Dutch heading should remain visibly review-only:

```text
Deterministische regime-inschatting — alleen ter review
```

## Proposed validation requirements for any later implementation

Before a future integration can be accepted, it must add tests proving:

```text
1. The production report renderer still uses the legacy macro policy pack as the governing production macro source.
2. The deterministic regime safe surface is generated only from the narrow DTO.
3. Raw fields do not appear in EN/NL report text.
4. The WP22 validator passes on the exact rendered EN/NL text.
5. Review-only wording remains visible in both languages.
6. Confidence remains banded and never numeric in the deterministic safe surface.
7. No portfolio/scoring/fundability/execution files change.
8. Historical generated outputs are not rewritten.
```

## Explicit blocked implementation choices

A future implementation must not:

```text
wire full shadow validation JSON directly into report text
wire macro_axes or macro_axis_scores into report text
show source paths, workflow ids, fixture names, or raw confidence decomposition
replace the legacy macro pack as production regime authority
change portfolio decisions, lane scores, fundability, funding, or execution logic
rewrite historical reports
```

## Required future approval boundary

WP26 may implement only if the user explicitly starts that package.

WP25 itself closes as proposal-only and does not authorize implementation.

## Closeout

WP25 is closed as proposal-only.

Next package, only if explicitly approved:

```text
WP26 — Deterministic regime report integration implementation
```
