# Dutch Terminology Contract Status

## Date
2026-06-01

## Status
Phase 7 Dutch terminology / alias consolidation is implemented and workflow-proven.

This is a Dutch quality and terminology guard only. It does not promote macro/thesis artifacts, alter portfolio scoring, change fundability, or change production recommendations.

## Files updated

```text
runtime/apply_nl_localization.py
tools/validate_nl_terminology_contract.py
.github/workflows/validate-nl-terminology-contract.yml
```

## What changed

- `runtime/apply_nl_localization.py` now uses `runtime/nl_terminology.py` as the central terminology overlay.
- Exact decision/trigger translations now run before generic cleanup so broad regex cleanup cannot partially mutate source phrases before exact phrase maps apply.
- The terminology contract validates the central map, runtime localization overlay, native Dutch safety overlay, bad-token repair/block behavior, and disclaimer replacement behavior.

## Workflow proof

Workflow-proven by GitHub Actions screenshot supplied by the user.

Evidence from screenshot:

```text
workflow: Validate ETF Dutch terminology
run title: fix Dutch terminology fixture disclaimer placement #7
trigger: push
commit: de2af14
branch: main
status: Success
job: validate-nl-terminology
total duration: 10s
```

Expected marker:

```text
ETF_NL_TERMINOLOGY_CONTRACT_OK
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

## Next action

The next safe roadmap step is either:

1. run a production ETF report validation to make sure the new leakage and Dutch terminology guards pass in the full report flow; or
2. add a repo-visible evidence mechanism for the Dutch terminology contract, similar to the macro-regime and Stage-2 evidence files, if future chats should verify it without relying on Actions screenshots.
