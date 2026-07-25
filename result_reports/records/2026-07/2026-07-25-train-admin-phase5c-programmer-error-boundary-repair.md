# Train/Admin Phase 5C Programmer-Error Boundary Repair

```yaml
record:
  date: 2026-07-25
  topic: train-admin-phase5c-programmer-error-boundary-repair
  tags: train-admin, phase-5c, audit-repair, programmer-error, candidate-corruption, exception-boundary
  memory_review: updated
  memory_reason: The third Phase 5C audit FAIL and its programmer-error versus persisted-corruption distinction are durable final re-audit context.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The third independent L4 re-audit of PR #30 returned `FAIL` for one remaining
blocker: lifecycle read and publication validation inferred persisted Candidate
corruption from unexpected validator/parser/helper `TypeError` or
`AttributeError`. The first two audit repairs remain historical and unchanged.

## Contract / Behavior Changed

- Malformed manifest, Candidate result, structured training result, and artifact
  reference payloads now fail through an explicit analysis artifact-contract
  error owned by the persisted contract parser.
- Candidate read and publication validation no longer list `TypeError` or
  `AttributeError` among expected persisted-artifact failures.
- Promotion re-raises those two programmer exceptions instead of returning a
  blocked Candidate result.
- Existing controlled rejection for canonical path, category, strict boolean
  `required`, SHA-256, manifest/result parity, and unsupported/malformed result
  versions is preserved.
- The application terminal path still preserves original target evidence and
  cleans staging when a publication-time programmer exception escapes the
  lifecycle validation boundary.

## Evidence And Verification

- Focused repository, promotion, and Phase 5C lifecycle suite: 124 passed.
- Canonical full suite: 2616 passed, 2 xfailed.
- Direct injected `TypeError` and `AttributeError` regressions cover manifest
  parsing, Candidate file validation, publication validation, promotion,
  Active identity/revision/history stability, terminal Core target evidence,
  and staging cleanup.
- Prior malformed artifact, canonical alias, strict type, required nine-artifact,
  and failure-evidence regressions run in the same focused suite.
- Compile and whitespace checks passed. Structure validation reported only the
  unchanged repository soft-warning inventory; staged change-gate and official
  exact-head GitHub validation are recorded in the Draft PR after push.

## Changed Files

- Candidate and training-result persisted contract parsers
- lifecycle repository and promotion exception boundaries
- focused lifecycle and terminal-evidence regressions
- current work-plan/design-set status, project log, report index, and memory seed

## Known Risks

- This repair deliberately does not redesign the broader lifecycle exception
  taxonomy or change how non-TypeError/AttributeError compatibility failures are
  returned by promotion.
- This Worker does not declare audit `PASS`, merge PR #30, or start Phase 5D,
  CLI, Campaign, leaderboard, or the agent loop.
