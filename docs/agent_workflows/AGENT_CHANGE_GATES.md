# Agent Change Gates

## Role

This document owns staged objective checks and warning-first structure evidence.
It does not make result records mandatory for ordinary changes.

## Applicability

The cached checker inspects staged source, test, tool, region-config, and
result-record changes. Docs-only wording and status checks normally need no
gate beyond diff inspection.

## Objective Hard Checks

The staged checker fails on:

- staged whitespace errors;
- Python syntax errors in checked source;
- new production source over 350 LOC;
- Phase 1 UI presentation literals that bypass token owners without an approved
  exemption;
- malformed or mutated result records;
- a new record without its index row or required memory update;
- staged paths outside an explicitly supplied local manifest.

These checks are mechanical and do not depend on report presence.

## Warning-First Structure Checks

The checker warns, but does not fail solely, when:

- a new production source is 251-350 LOC;
- a new source has many top-level classes;
- an existing hotspot grows by 40 net LOC or more;
- a structural change has no reuse/commonization decision;
- a Phase 2 UI presentation literal may deserve a token.

Warnings require review, not automatic extraction or a mandatory record. A
durable record is needed only when the task independently matches a Result
Record trigger.

## Optional Change Gate Evidence

A compact record may include:

```yaml
change_gate:
  new_source: none | small | split | justified
  hotspot_delta: none | wiring-only | accepted-for-slice | split-audit-required | split-required
  ui_literal_exemption: none | approved-for-slice
  reuse_commonization: not_required | checked | reused-existing-owner | local-with-reason | design-deferred
```

Use this block for an approved UI literal exemption or a structure decision
worth preserving.

## Local Task Manifest

The optional local manifest is resolved through:

```bash
git rev-parse --git-path agent_task_manifest.yml
```

It may restrict staged files with literal `allowed_paths` and select one
`report_path` when multiple new records contain change-gate evidence. It is
local staging control, not durable project history and not a reason to require a
report.

## Result Record Checks

New records must:

- be added under
  `result_reports/records/YYYY-MM/YYYY-MM-DD-<slug>.md`;
- contain the five-field `record` metadata block;
- have a staged row in `result_reports/REPORT_INDEX.md`;
- stage the memory seed when `memory_review: updated`;
- remain append-only after commit.

The checker reads index blobs rather than unstaged worktree content.

## UI Literal Policy

Phase 1 rejects new staged production UI literals for known table/window/color
policy surfaces. Token-owner modules and existing grandfathered lines remain
outside the check.

Phase 2 warns on likely repeated `width`, `height`, `padx`, `pady`, or
named-color literals. Prefer an existing token/helper; create a durable
exemption record only when the local value is deliberate and reusable policy is
not appropriate.

Domain/regulation values are not UI presentation literals.

## Hook Policy

`.githooks/pre-commit` runs:

```bash
git diff --cached --check
python3 -B tools/check_agent_change_gate.py --cached
```

Hooks are implemented in the repository but enabled per clone only when
`core.hooksPath` is configured. Do not describe them as active in a checkout
without verifying that configuration.

## Validation

When this policy or checker changes, run:

- focused agent-change-gate tests;
- focused UI literal tests when that surface changes;
- Git hook tests when hook behavior changes;
- `tools/check_code_structure.py` for structure-impacting source changes.

Do not run full pytest solely because the harness policy changed.
