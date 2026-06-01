# Dutch Terminology Contract Status

## Date
2026-06-01

## Status
Phase 7 Dutch terminology / alias consolidation is implemented, workflow-proven, and repo-visible evidence-proven.

This is a Dutch quality and terminology guard only. It does not promote macro/thesis artifacts, alter portfolio scoring, change fundability, or change production recommendations.

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
workflow.run_number: 6
workflow.run_id: 26749079689
workflow.commit_sha: 0dfec471c377e52e92c6ffe7fa1bb5ce817c0405
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
tools/validate_nl_terminology_contract.py
.github/workflows/validate-nl-terminology-contract.yml
tools/write_nl_terminology_contract_validation_evidence.py
output/macro/validation/latest_nl_terminology_contract_validation.json
```

## What changed

- `runtime/apply_nl_localization.py` now uses `runtime/nl_terminology.py` as the central terminology overlay.
- Exact decision/trigger translations now run before generic cleanup so broad regex cleanup cannot partially mutate source phrases before exact phrase maps apply.
- The terminology contract validates the central map, runtime localization overlay, native Dutch safety overlay, bad-token repair/block behavior, and disclaimer replacement behavior.
- The isolated Dutch terminology workflow now writes repo-visible validation evidence after the contract passes.

## Workflow proof

Workflow-proven by repo-visible evidence and by GitHub Actions screenshot supplied by the user.

Evidence from screenshot:

```text
workflow: Validate ETF Dutch terminology contract
run title: commit Dutch terminology validation evidence after pass #6
trigger: push
commit: 0dfec47
branch: main
status: Success
job: validate-nl-terminology-contract
total duration: 13s
```

Expected markers:

```text
ETF_NL_TERMINOLOGY_CONTRACT_OK
ETF_NL_TERMINOLOGY_EVIDENCE_OK
```

## Failure/fix history

The isolated workflow initially exposed useful contract issues:

1. `Neetable` existed intentionally as a forbidden-after-scrub guard token, but the validator incorrectly treated all guard tokens as client-facing values.
2. `Toevoegened` was repairable by the scrub layer, so the contract was adjusted to require known-bad tokens to be repaired or blocked, not always present in the forbidden list.
3. The self-test placed decision phrases after `## 17. Disclaimer`, so `_replace_disclaimer()` correctly removed them before phrase translation. The fixture was moved before the disclaimer section.
4. The native Dutch localization order was corrected so exact decision/trigger phrase translations run before generic cleanup.

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

The next safe roadmap step is to run a production ETF report validation to make sure the new leakage and Dutch terminology guards pass in the full report flow.
