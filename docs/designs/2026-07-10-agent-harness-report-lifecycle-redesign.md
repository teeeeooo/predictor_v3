# Design Gate — Agent Harness Report And Memory Redesign

## Goal

Reduce report and lifecycle overhead while preserving durable change reasons,
long-running project recall, targeted report discovery, and objective staged
guards.

## Confirmed Decisions

- Ordinary source, test, tool, UI, docs, and bugfix work does not require a
  result report.
- Compact records are required for architecture/owner changes, schema or public
  contracts, calculator formula/golden/config behavior, harness enforcement,
  migrations/releases, decisive external/manual evidence, and user requests.
- UI and bugfix records are required only for non-obvious, repeated,
  cross-owner, manual-only, platform-specific, or unguarded regressions.
- Required records are committed with their source changes. Commit hashes live
  in terminal output and Git history, not inside the record.
- New records use date-based final paths and a one-line discovery index.
- Memory review is required for new records, milestone/branch closeout, explicit
  handoff, and return to a long-paused workstream.
- Existing archive/summary content is read-only under
  `result_reports/legacy/`. Historical bodies remain unchanged.

## Core vs Handler Boundary

- Agent entrypoint/router: trigger and routing policy.
- Result workflow: record shape, storage, index, terminal, and same-commit rule.
- Memory workflow: recall and Memory Review Gate.
- Staged checker: objective errors plus record/index/memory consistency.
- Legacy migration: Sol owns semantic classification; Luna owns approved
  mechanical moves and substitutions.

## Data Shape / API Boundary

- Record path:
  `result_reports/records/YYYY-MM/YYYY-MM-DD-<slug>.md`
- Required record metadata: `date`, `topic`, `tags`, `memory_review`,
  `memory_reason`.
- Terminal fields: `modified`, `validation`, `commit`, `push`,
  `report`.
- Existing calculator, ML, UI runtime, schema, config, and public APIs are
  unaffected.

## Required Tests

- Ordinary staged source/test/tool changes pass without a report.
- Objective structure and UI literal errors remain enforced.
- Warning-first structure findings do not require a report.
- New records require a valid path, index entry, and memory decision.
- `memory_review: updated` requires the staged memory seed.
- Checker reads staged blobs rather than unstaged worktree content.

## Migration / Refactor Path

1. Implement the report, terminal, memory, and staged-gate bootstrap.
2. Review Slice A before legacy movement.
3. Sol classifies external legacy references.
4. Luna performs approved moves and exact substitutions without commit/push.
5. Sol or the primary agent reviews rename purity, links, and stale references.

## Risks

- Warning-first structure checks may be ignored; objective checks remain hard.
- Memory review can become mechanical; a short reason is required.
- Legacy movement can break source traces; it is isolated in Slice B.

## Non-goals

- No legacy report or summary movement in Slice A.
- No bulk rewrite of historical report bodies.
- No calculator, ML, UI runtime, schema, or golden behavior change.
- No commit or push without explicit user authorization.

## Implementation Status

- Slice A completed in commit `c3cd9e4`.
- Slice B moved 720 archived reports and 53 summaries under the physical legacy
  boundary with byte-preserved bodies and targeted active-reference remapping.
- Branch push is complete. Main merge remains pending completion and verification
  of the pre-merge documentation corrections.

## Next Codex Implementation Prompt

```text
Review Slice B rename purity, active and historical path boundaries, compact
record/index/memory consistency, and staged gate output before committing or
pushing.
```
