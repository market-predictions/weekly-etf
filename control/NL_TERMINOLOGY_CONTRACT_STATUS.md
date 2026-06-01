# Dutch Terminology Contract Status

## Date
2026-06-01

## Status
Phase 7 Dutch terminology / alias consolidation is implemented, workflow-proven, repo-visible evidence-proven, and updated to protect the native Dutch report architecture.

This is a Dutch quality and terminology guard only. It does not promote macro/thesis artifacts, alter portfolio scoring, change fundability, or change production recommendations.

## Architecture rule

The agreed output architecture is:

```text
runtime state / key figures
→ English native render
→ Dutch native render from the same runtime state
→ guard-only Dutch validation for native reports
```

It is not:

```text
English report
→ broad translation / scrub pass
→ Dutch report
```

The Dutch report is independently constructed from the same runtime state and key figures as the English report. It is not a second research pass and not a translation of the English markdown.

## Repo-visible proof

Evidence file:

```text
output/macro/validation/latest_nl_terminology_contract_validation.json
```

Current evidence reports:

```text
artifact_type: nl_terminology_contract_validation_evidence
status: passed
workflow.name: Validate ETF Dutch terminology contract
workflow.run_number: 10
workflow.run_id: 26770580704
workflow.commit_sha: d32dbf6813084892efa565277c479a11951c698c
validated_markers:
  - ETF_NL_TERMINOLOGY_CONTRACT_OK
```

The evidence confirms these guarded scopes:

```text
central_terminology_contract: true
localization_overlay_guard: true
native_dutch_safety_overlay_guard: true
bad_token_repair_or_block_guard: true
disclaimer_replacement_guard: true
```

## Files updated

```text
runtime/apply_nl_localization.py
runtime/scrub_nl_client_language.py
tools/validate_nl_terminology_contract.py
.github/workflows/validate-nl-terminology-contract.yml
tools/write_nl_terminology_contract_validation_evidence.py
output/macro/validation/latest_nl_terminology_contract_validation.json
```

## What changed

- `runtime/render_etf_report_from_state.py` already writes the Dutch report from `render_nl_native(state)`.
- `runtime/apply_nl_localization.py` now treats native Dutch reports as guard-only: official disclaimer replacement and deterministic artifact cleanup only.
- `runtime/scrub_nl_client_language.py` now treats native Dutch reports as guard-only and does not run broad English-to-Dutch replacement maps over native Dutch prose.
- Broad localization/scrub behavior remains available only for legacy/non-native text.
- The terminology contract now proves:
  - legacy/non-native text may still be localized;
  - native Dutch text remains guard-only;
  - native Dutch text keeps valid wording such as `Nog geen alternatief...`;
  - English leakage in native Dutch is not silently translated;
  - English leakage fails Dutch quality validation.

## Workflow proof

Workflow-proven by repo-visible evidence and by GitHub Actions screenshot supplied by the user.

Evidence from screenshot:

```text
workflow: Validate ETF Dutch terminology contract
run title: validate native Dutch guard-only architecture #10
trigger: push
commit: d32dbf6
branch: main
status: Success
job: validate-nl-terminology-contract
total duration: 16s
```

Expected markers:

```text
ETF_NL_TERMINOLOGY_CONTRACT_OK
ETF_NL_TERMINOLOGY_EVIDENCE_OK
```

## Failure/fix history

The isolated workflow exposed useful contract issues:

1. `Neetable` existed intentionally as a forbidden-after-scrub guard token, but the validator incorrectly treated all guard tokens as client-facing values.
2. `Toevoegened` was repairable by the scrub layer, so the contract was adjusted to require known-bad tokens to be repaired or blocked, not always present in the forbidden list.
3. The self-test placed decision phrases after `## 17. Disclaimer`, so `_replace_disclaimer()` correctly removed them before phrase translation. The fixture was moved before the disclaimer section.
4. The native Dutch localization order was corrected so exact decision/trigger phrase translations ran before generic cleanup.
5. After the user correctly pointed out that Dutch should not be a translation of English, native Dutch reports were moved to guard-only localization/scrub mode.

## Authority boundary

This Phase 7 work is not a macro/thesis production promotion.

It does not change:

```text
client-facing investment logic
lane scoring
fundability
portfolio actions
final recommendations
macro/thesis authority
```

The evidence explicitly records:

```text
quality_guard_only: true
client_facing_investment_logic_changed: false
macro_thesis_promotion: false
lane_scoring_authority: false
fundability_authority: false
portfolio_action_authority: false
production_recommendation_authority: false
```

## Next action

Run a production ETF report validation to prove the full report flow now passes with native Dutch guard-only handling and without translation/scrub mutation of the Dutch report.
