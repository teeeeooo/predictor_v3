# 393 Code map freshness correction reference gate hardening

## Goal

Correct the stale code_map state after recent EN14825 UI/result/table structure
changes and harden the warning-first Reference Evidence Gate so future
structure-impacting work records code_map check/regenerate judgment.

## Scope

- Checked `docs/agent_workflows/DIFF_READ_BUDGET.md` Reference Evidence Gate
  trigger and regenerate policy range.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md` with the existing
  generator.
- Hardened Reference Evidence Gate/report/router docs without changing owner
  boundaries.
- Added a warning-first code_map freshness reminder to
  `tools/check_code_structure.py`.
- Added focused tests for the new structure guard reminder.

## Code Map Check

- `code_map_check`: checked.
- Initial `python3 -B tools/code_checker/build_reference_map.py --check`
  reported stale map metadata: map commit `8541934` vs current HEAD `729fc12`.
- Targeted map search before regeneration did not find the requested EN14825
  symbols, confirming the map missed recent structure/surface additions.

## Code Map Regenerate

- `code_map_regenerate`: regenerated.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` is included in this diff.
- Regenerated map now includes EN14825 package adapters/table models, SCOP
  mapper/formatter/result surface imports, `MetricInputTable`, `ResultPanel`,
  and current hotspot/import-edge changes.

## Workflow Hardening

- `DIFF_READ_BUDGET.md` now explicitly treats structural source changes,
  new/moved/split helpers/adapters/controllers/table surfaces/result surfaces,
  window/commonization paths, and new profile UI as Reference Evidence Gate
  triggers.
- `RESULT_REPORT_WORKFLOW.md` now requires compact `code_map_check` judgment for
  structure-impacting source changes.
- `AGENT_TASK_ROUTER.md` now routes structure/UI surface work to Reference
  Evidence Gate for both preflight and report/regenerate judgment.

## Tool Hardening

- `tools/check_code_structure.py` now reuses
  `code_checker.metadata.evaluate_freshness()` and emits code_map freshness
  reminders as warnings only.
- Stale/missing/metadata-error map states do not fail the guard; they only
  surface the Reference Evidence Gate reminder.
- The tool remains a structure guard, not a semantic linter.

## Tests

- Focused tests found and run:
  - `tests/test_code_checker_reference_map.py`
  - `tests/test_code_structure_guard.py`
- Apps/core/UI behavior tests were not run because this task only changes
  code_map/docs/tool harness.

## Verification

- `python3 -B -m py_compile tools/code_checker/build_reference_map.py` OK.
- `python3 -B -m py_compile tools/check_code_structure.py` OK.
- `python3 -B tools/code_checker/build_reference_map.py --check` OK; status
  FRESH with dirty-working-tree warning expected during this uncommitted task.
- `python3 -B tools/code_checker/build_reference_map.py` OK; map regenerated.
- `python3 -B tools/check_code_structure.py` OK with existing SEER/SCOP soft
  LOC warnings.
- `python3 -B -m pytest tests/test_code_checker_reference_map.py
  tests/test_code_structure_guard.py -q` OK, 41 passed.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Scope Compliance

- Apps, core, data, calculator logic, UI behavior/source surfaces, fixtures,
  summaries, archive, memory seed, and `project_log.md` were not modified.
- No EN14825 batch or AHRI tab implementation was performed.

## Commit / Push

- Final commit hash and push status are reported in terminal output.
