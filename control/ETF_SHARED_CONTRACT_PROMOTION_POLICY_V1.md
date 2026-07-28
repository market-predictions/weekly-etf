# ETF Shared Contract Promotion Policy V1

**Repository:** `market-predictions/weekly-etf`  
**Contract owner:** Weekly ETF donor strategy layer  
**Initial release:** `weekly_etf_shared_contract_v1_0_0`  
**Status:** becomes stable only when the release manifest and its validators are merged to `main`

## 1. Purpose

This policy governs promotion, compatibility, consumer pinning, deprecation and rollback for the read-only artifacts exported by Weekly ETF to downstream implementation repositories.

The initial contract contains:

- `etf_shared_strategy_state_v1`;
- `etf_shared_portfolio_target_v1`.

The contract communicates strategy research and reference portfolio state. It never grants portfolio mutation, funding, execution or broker authority.

## 2. Release identity

Every promoted contract must have one immutable release manifest under `control/releases/` containing:

- a semantic version;
- a stable contract release ID;
- the exact schemas, builders and validators included;
- authority boundaries;
- compatibility policy;
- consumer pinning requirements;
- the pull request through which the release is promoted.

A release marked `stable_on_merge` is not stable while it exists only on a feature branch. It becomes stable when the owning pull request is merged into `main` and the merge commit has passed all required checks.

## 3. Consumer pinning

Production and cutover candidates must not consume a mutable feature branch.

Allowed consumer references:

1. an immutable donor merge commit SHA;
2. a repository tag that resolves to that accepted commit;
3. a later immutable release commit explicitly declared compatible by a newer release manifest.

Disallowed consumer references:

- `sync/shared-strategy-state` or any other feature branch;
- an unversioned latest artifact;
- a schema version inferred only from file names;
- a donor report or Markdown document used as machine authority.

## 4. Semantic compatibility

### Patch release

A patch release may fix validators, comments, error handling or deterministic serialization without changing required fields or field meaning.

### Minor release

A minor release may add optional fields or new enumerated capabilities that existing consumers can ignore safely. Existing required fields and authority boundaries must remain valid.

### Major release

A major release is required for any of the following:

- removing or renaming a required field;
- changing field meaning or units;
- changing an authority boundary;
- changing exposure identifiers incompatibly;
- changing ranking or target semantics in a way that alters consumer interpretation;
- making a previously optional field required.

Consumers must reject unsupported major releases rather than silently adapting.

## 5. Promotion gates

A release may be promoted only when all gates pass:

1. both artifacts build deterministically apart from `generated_at_utc`;
2. both artifact validators pass;
3. the release-manifest validator passes;
4. source lineage is present;
5. all mutation, funding and execution flags remain false;
6. at least one downstream consumer has validated the release in shadow mode;
7. the pull request is mergeable and required CI is green;
8. the promotion does not alter the donor production portfolio, report or delivery path.

For release `1.0.0`, the validated downstream consumer is `market-predictions/weekly-etf-eu` draft PR `#66`.

## 6. Deprecation

A stable major contract remains supported until:

- a replacement release is merged;
- all registered consumers have a validated migration path;
- a deprecation date and rollback reference are recorded;
- no production consumer still pins the deprecated release.

Deprecation must not be inferred from branch deletion.

## 7. Rollback

Rollback means repinning consumers to the last accepted immutable donor commit and rebuilding their shadow or production package from that reference.

Rollback must not:

- mutate portfolio state automatically;
- replay or reverse trades automatically;
- infer ledger changes from report text;
- bypass local implementation or pricing controls.

## 8. Release 1.0.0 authority boundary

Release `weekly_etf_shared_contract_v1_0_0` is read-only and exposure-first.

It grants:

- strategy research authority to the donor state;
- reference portfolio-target authority to the donor target.

It explicitly denies:

- portfolio mutation authority;
- funding authority;
- execution authority;
- broker execution authority;
- permission for a consumer to reuse US instruments without local remapping.

## 9. Operational handover

After merge, downstream consumers must replace any feature-branch checkout with the immutable donor merge commit or a tag resolving to it. The consumer must record the pinned release ID and commit SHA in its own cutover manifest.