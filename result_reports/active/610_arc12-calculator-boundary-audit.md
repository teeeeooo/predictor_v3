# Arc 12 Calculator Boundary Audit

## Goal
- Formalize the Arc 12 Calculator UI/Application Boundary Audit in repo docs.
- Make the first extraction sequence discoverable before source implementation.

## Scope
- Added the Arc 12 design record.
- Updated current project state docs and design index.
- No production source, tests, calculator formulas, configs, fixtures, golden
  expected values, profile IDs, or public result contracts changed.

## Changed Files
- `docs/designs/2026-06-28-arc12-calculator-usecase-boundary-audit.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `docs/REFACTOR_PLAN.md`
- `project_log.md`
- `result_reports/active/610_arc12-calculator-boundary-audit.md`

## Verification
- OK: `git diff --check`
- OK: `git status --short`
- OK with pre-existing soft warnings: `python3 -B tools/check_code_structure.py`

## Known Risks
- Source extraction is intentionally deferred to Slice 1 and later.
- Remaining calculator UI orchestration in SASO, Hong Kong, EN14825, and AHRI is
  known debt and not hidden by this audit.
- Structure guard reported existing soft warnings in calculator core/UI hotspot
  files; Slice 0 did not modify source files.

## Commit / Push
- commit: completed in slice commit; final hash reported in terminal output
- push: deferred until all Arc 12 slices are complete per user request

## Project Memory Delta
- type: decision
- topic: Arc 12 calculator usecase boundary
- content: Arc 12 starts with ISO/ISEER 2-point application-usecase extraction and batch reuse while protecting calculator formulas/config/golden/public result contracts.
- keywords: arc12, calculator, usecase, iso_iseer, boundary
