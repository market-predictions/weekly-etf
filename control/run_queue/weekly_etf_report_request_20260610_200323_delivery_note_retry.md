# Weekly ETF report request — delivery note retry

## Purpose

Retry the weekly ETF report after replacing stale hardcoded GLD -> GSG post-execution delivery wording with state-derived executed-pair wording.

## Previous client-surface issue

The delivered report showed this stale line even though GLD is no longer an active position:

```text
The GLD → GSG guarded model rotation is already reflected in the official portfolio state and trade ledger; no new state or ledger mutation was performed this run.
```

## Fix included before this retry

```text
408439d340f26f05feeaae36513405d0a1264925 — Render post-execution replacement note from executed pair
af9eb285de9ae87dd78117c322ed46c6f605a41b — Test post-execution replacement note uses executed pair
```

## Expected delivery wording

For the current executed state, the post-execution delivery note should refer to:

```text
SPY → IEFA
```

It must not refer to:

```text
GLD → GSG
```

## Scope

This is a client-surface delivery wording fix only.

No scoring, fundability, target-weight, execution, policy, trade-ledger, or portfolio-state logic was changed.

## Operational note

Avoid additional direct commits to `main` while this workflow is running, otherwise the final artifact push can fail with a non-fast-forward rejection.
