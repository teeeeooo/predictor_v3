# 410 EN14825 SEER batch dialog wiring

## Goal

Wire the tested SEER batch handler into the existing Tk batch dialog shell while
keeping the single-case section thin and behaviorally unchanged.

## Scope

- Added an EN14825 SEER batch profile using `BatchDialogShell` and
  `BatchMatrixTable`.
- Added dialog-owned common inputs, auto-calculation, compact row summary,
  Add/Remove Case, Copy All, and CSV export.
- Added combined common-input and logical-case snapshot preservation.
- Added a section-level batch action with open/focus/close lifecycle ownership.
- Added focused dialog/profile/lifecycle tests and updated WORK_PLAN/code map.

## Non-goals

- No SCOP dialog wiring or dynamic rebuild policy.
- No single-case calculation, adapter, core, config, schema, or golden changes.
- No generic shell/table refactor and no existing headless test-file split.

## Task Results

- Common values are independent from the single-case SEER variables and common
  auxiliary callback.
- Closing and reopening restores both common inputs and matrix cases.
- Partial rows remain pending; genuine row errors alone contribute to the
  compact invalid count.
- The section owns only the button, dialog reference, and session snapshot.
- Copy/export continue through existing table and CSV helpers.

## Reference Parity

- Reused the Hong Kong CSPF batch profile composition, generic dialog shell,
  matrix table/controller, debounce scheduler, clipboard, and CSV paths.
- SEER adds a profile-local common-input surface and combined snapshot because
  those values are dialog-owned rather than section-owned.
- The profile module is 248 LOC; no new generic state framework was introduced.

## Verification

- `py_compile` for changed source/test files: OK.
- EN14825 SEER batch dialog + headless focused tests: OK, 17 passed.
- Existing EN14825 UI + generic shell/matrix focused tests: OK, 39 passed.
- `tools/check_code_structure.py`: OK with existing EN14825 section LOC soft
  warnings only after map regeneration.
- `tools/code_checker/build_reference_map.py`: OK; map changed for the new
  profile module and import/symbol inventory.
- `git diff --check`: OK.

## Changed Files

- `apps/calculator/ui/batch_dialogs/profiles/en14825_seer.py`
- `apps/calculator/ui/sections/en14825_seer_section.py`
- `tests/test_ui_tk_en14825_seer_batch_dialog.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/410_en14825_seer_batch_dialog_wiring.md`

## Known Failures / Risks

- `En14825SeerSection` remains above the existing 400 LOC soft limit; this
  slice adds only thin dialog lifecycle wiring and does not add calculation
  responsibility there.
- Platform-specific visual/manual smoke remains a follow-up after automated
  validation.
- SCOP dialog work remains blocked on its dynamic rebuild/snapshot policy.

## Scope Compliance

- No core, data, config, SCOP, ML, batch shell, shared table behavior, or golden
  file was changed.
- Existing single-case SEER tests remain green.

## Code Map

- `code_map_check`: regenerated.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` is included in the diff.

## Commit / Push

- Final validation passed; implementation and report are committed and pushed
  together.

## Project Memory Delta

- none.

## Next Suggested Action

EN14825 SCOP batch rebuild/snapshot policy design.
