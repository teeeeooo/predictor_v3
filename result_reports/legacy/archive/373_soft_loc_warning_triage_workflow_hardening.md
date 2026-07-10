# 373 Soft LOC Warning Triage Workflow Hardening

## Goal

Prevent soft structure warnings, especially soft LOC warnings on changed/new
source files, from being hidden behind validation OK.

## Scope / Non-goals

- Scope: documentation workflow hardening for UI surface warning triage,
  architecture acceptance wording, result report warning fields, router hook,
  and compact work plan sequencing.
- Non-goals: no source code changes, tests, checker changes, hard error guard,
  path-specific rule, SCOP section split, SCOP Slice 3, Report 372 hygiene
  correction, memory seed update, project log update, or lifecycle movement.

## Existing Rule Audit

- `UI_SURFACE_WORKFLOW.md` already treats soft LOC limits, including 400 LOC
  warnings, as preflight triggers and forbids mechanical line-count splits.
- `PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` already defines View boundaries,
  stop conditions, repeated mapping/formatting/routing smells, and source file
  owner boundary policy.
- `RESULT_REPORT_WORKFLOW.md` already defines compact/full report modes,
  terminal output shape, commit/push policy, and active report count wording.
- `AGENT_TASK_ROUTER.md` already routes structure-impacting work to
  `check_code_structure.py`, warning-first preflight evidence, UI surface
  workflow, clean architecture boundary, and result report workflow.

## Added Workflow Rules

- Added post-implementation soft warning triage for changed/new UI surface,
  adapter, helper, controller, or view files before moving to the next code
  slice.
- Clarified that a structure warning is not architectural acceptance; reports
  should explain accepted responsibility co-location or set split audit as the
  next action.
- Added `Structure Warnings` and `Warning Triage` result report coverage with
  compact triage actions.
- Added a short router hook that sends changed/new source soft warnings to the
  result report warning triage rule.

## MVC/SoC Judgment

The change keeps ownership in documentation workflow layers. It does not alter
runtime code, tests, schemas, public APIs, or checker behavior. The new rule is
general to UI surface/adapter/helper/controller/view responsibilities and does
not create path-specific hard gating.

## Changed Files

- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`
- `AGENT_TASK_ROUTER.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/373_soft_loc_warning_triage_workflow_hardening.md`

## Validation

- `git diff --check` OK.
- `git status --short` showed only the allowed docs/report changes for this
  task.
- `python3 -B tools/check_code_structure.py` OK with one existing soft LOC
  warning in the SCOP section UI path; no changed/new source file was modified
  by this docs-only task.
- `find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l` OK;
  exact count is reported only in terminal output.

## Structure Warnings / Warning Triage

- Structure Warnings: none for changed/new source files in this docs-only task.
- Warning Triage: existing SCOP section UI soft LOC warning remains a next-slice
  responsibility audit candidate, not a hard checker failure.

## Known Risks / Gaps

- This is a workflow/documentation hardening only. The checker still emits soft
  LOC warnings without failing the command.
- Existing legacy warnings can still be accepted with reason; future discipline
  depends on reports recording the warning path, reason, and next action.

## Next Suggested Action

Before adding more responsibility to the SCOP section UI path, choose either
Report 372 hygiene correction or a SCOP section responsibility split audit
based on current repo status.

## Project Memory Delta

- none

## Commit / Push

- Final commit hash and push status are reported in terminal output to avoid a
  self-referential report update loop.
