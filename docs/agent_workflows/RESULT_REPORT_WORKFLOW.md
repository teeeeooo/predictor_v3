# Result Record Workflow

## Role

This document owns the repository-specific conditional Result Record lifecycle: trigger classification, record shape/path, discovery index, append-only history, Memory Review coupling, and required same-change atomicity.

A compact Result Record is durable repository evidence. It does not replace source, tests, Git history, or the final task report. Ordinary tracked-file changes do not require a Result Record.

## Required Record Triggers

Create one compact record when the task changes or establishes:

- architecture or owner boundaries;
- schema, public API, JSON keys, or diagnostics contracts;
- calculator formulas, golden/fixture expectations, or region-config behavior;
- agent harness, gate, or workflow enforcement;
- migration, release, or deployment decisions;
- external/manual evidence that is necessary for final acceptance;
- a non-obvious, repeated, cross-owner, platform/manual-only, or unguarded
  UI/bug regression;
- an explicitly user-requested report.

Do not create a record for ordinary implementation, focused internal refactor,
tests, UI polish, simple bugfix, docs wording, formatting, or status checks
unless one of the triggers above is actually present.

## UI And Bug Recurrence History

Regression tests are the primary recurrence guard. For an ordinary UI/bugfix
without a result record, use a meaningful commit body when commit is requested:

```text
Symptom:
Cause:
Fix:
Guard:
```

When recurrence is suspected, search Git history by the affected path and a
stable symptom/symbol before opening broad historical reports. Escalate to a
compact record only for the non-obvious/repeated/manual/cross-owner cases listed
above.

## Location And Naming

New records use their final history path immediately:

```text
result_reports/records/YYYY-MM/YYYY-MM-DD-<slug>.md
```

- Use a short kebab-case slug.
- Add `-02`, `-03`, and so on only for a same-day path collision.
- Do not scan legacy directories for a global number.
- Records are append-only. Correct a material error with a new correction
  record rather than rewriting history.
- Existing records preserve the metadata and optional change-gate schema valid
  when created. Current parser and staged-checker schemas apply only to newly
  staged records; do not bulk-convert existing records.

Existing `active/` is a legacy input retained at its historical path. Existing
archive and summary evidence is read-only under `result_reports/legacy/`.

## Record Contract

Every new record contains exactly one metadata block:

```yaml
record:
  date: YYYY-MM-DD
  topic: short-stable-topic
  tags: comma-separated, search-friendly, tags
  memory_review: updated | no-change
  memory_reason: one short reason
```

Minimum content:

- Change Reason
- Contract / Behavior Changed
- Evidence And Verification
- Changed Files
- Known Risks

Preserve why and the durable evidence. Do not reproduce the full terminal
output, diff, test log, implementation diary, or owner-document text.

An optional `change_gate` block may record an approved UI literal exemption or
nontrivial structure decision. It is not required merely because source or test
files changed.

## Discovery Index

Add one row per new record to `result_reports/REPORT_INDEX.md`:

```text
| Date | Topic | Tags | Decision / Reason | Record |
```

The staged checker verifies the path, index row, and memory-review consistency.
Search the index or memory seed before opening record bodies.

## Memory Review

Every new record declares one of:

- `updated`: update `result_reports/memory/project_memory_seed.md` in the
  same staged change;
- `no-change`: give a short reason why existing memory is sufficient or the
  decision is not useful for long-term recall.

The broader Memory Review Gate also applies at milestone/branch closeout,
explicit handoff, and return to a long-paused workstream. Its owner is
`PROJECT_LOG_AND_MEMORY.md`.

## Verification Evidence

A Result Record preserves the decision-bearing validation evidence produced by the matching Skill/domain owner. Creating a record does not require rerunning evidence or broadening validation. Note meaningful weaker, skipped, unavailable, or manual-only verification when it changes confidence in the recorded decision.

## Commit Atomicity

- A required compact record is included in the same commit as its source/docs changes.
- The record requirement does not grant commit/push authority; follow the user's requested or explicitly approved Git scope.
- Do not put a commit hash in the record. Git history already associates the record and diff.
- Use a separate report-only commit only when explicitly required by the task.
- Do not create self-referential hash update loops.

## Final Reporting

The final task report follows `AGENTS.md`. State whether a Result Record was created when that matters to the change. Do not impose a separate fixed terminal template from this document.
