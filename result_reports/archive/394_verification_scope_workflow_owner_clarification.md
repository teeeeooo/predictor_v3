# 394 Verification scope workflow owner clarification

## Goal

Audit whether a new verification profile document is needed and clarify where
verification command scope should be chosen so prompts do not need repeated long
command lists.

## Scope

- Reviewed validation-related ranges in UI, calculator, diff/read, result report,
  and router workflow documents.
- Updated existing workflow owners with compact verification-scope rules.
- Kept router as route/hook only.
- Did not create `docs/agent_workflows/VERIFICATION_PROFILES.md`.

## Decision

- No new `VERIFICATION_PROFILES.md` is needed. Existing workflow owners already
  own validation scope by task type:
  - `UI_SURFACE_WORKFLOW.md` for UI surface validation.
  - `CALCULATOR_WORKFLOW.md` for calculator/golden/smoke/validation tests.
  - `DIFF_READ_BUDGET.md` for command-output discipline, structure guard, and
    code_map reference evidence gate.
  - `RESULT_REPORT_WORKFLOW.md` for reporting validation evidence and skipped
    stronger checks.
- A new profile document would duplicate those owners and create another routing
  surface to keep in sync.

## Workflow Hardening

- `DIFF_READ_BUDGET.md` now states that `check_code_structure.py` is a final
  guard for structure-impacting source work, not default validation for
  docs/report/manual-smoke/audit-only work.
- `DIFF_READ_BUDGET.md` also limits code_map check/regenerate to structural
  source inventory work unless the task specifically audits code_map state.
- `UI_SURFACE_WORKFLOW.md` now points UI source structure changes to the
  structure guard/code_map judgment rules and avoids repeated focused UI tests
  for visual-only or manual-smoke reflection.
- `CALCULATOR_WORKFLOW.md` now clarifies that calculator validation applies to
  core/calculator logic, schema/API, golden, fixture, or route changes, not
  docs-only/audit-only work.
- `RESULT_REPORT_WORKFLOW.md` now records validation scope as owner-driven and
  limits `code_map_check` reporting to structure-impacting source changes or
  explicit source-inventory/code_map audits.
- `AGENT_TASK_ROUTER.md` received only a short hook; no command matrix was added.

## Verification

- `git diff --check` OK.
- `git status --short` reviewed before commit.
- Confirmed `docs/agent_workflows/VERIFICATION_PROFILES.md` was not created.

## Scope Compliance

- No apps, core, data, tests, tools, code_map, memory, summary, archive, or
  project log files were modified.
- No EN14825 batch or AHRI tab implementation was performed.

## Commit / Push

- Final commit hash and push status are reported in terminal output.
