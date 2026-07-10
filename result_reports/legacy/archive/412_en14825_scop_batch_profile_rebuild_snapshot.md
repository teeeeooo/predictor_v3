# 412 EN14825 SCOP batch profile rebuild and snapshot

## Goal

Implement the SCOP batch profile-local dynamic matrix and snapshot policy
before adding any parent-section wiring.

## Scope

- Added a Tk-free SCOP batch session state for active conditions and hidden
  point input preservation.
- Added a SCOP batch profile with draft conditions, explicit Apply Conditions,
  matrix rebuild, auto-calculation, compact status, case actions, copy, and CSV.
- Added a separate shell adapter/dialog wrapper using the existing
  `BatchDialogShell` protocol.
- Added focused state, rebuild, failure, round-trip, and reopen tests.
- Updated WORK_PLAN and regenerated the code reference map.

## Non-goals

- No SCOP parent section button or lifecycle wiring.
- No generic shell snapshot protocol or matrix spec-replacement API change.
- No core, config, adapter availability, calculation, golden, or single-case
  SCOP UI change.

## Task Results

- Snapshot state separates draft `common_values`, valid `active_conditions`,
  and hidden-point `cases`.
- Invalid or unapplied drafts survive close/reopen while matrix/spec restoration
  remains based on the last valid active conditions.
- Apply failure preserves the active table, conditions, and case store.
- Condition round-trips preserve hidden point values and restore only current
  spec input keys to the visible table.
- `scop` and `qh_kwh` are excluded from the source snapshot/store.
- `Pdesignh` remains case-local and not applicable on the Power row.

## Reference Parity

- Reused the established SEER profile shell, debounce, matrix, controller,
  copy, CSV, and `last_snapshot` wrapper pattern.
- Applied the supplied SCOP rebuild/snapshot design with the added
  `active_conditions` snapshot field needed for invalid-draft reopen safety.
- Kept dynamic state SCOP-specific rather than introducing a generic framework.

## Verification

- `py_compile` for all new source/test files: OK.
- Final focused superset covering SCOP dialog, EN14825 batch headless contracts,
  generic shell, and matrix table: OK, 43 passed.
- `tools/check_code_structure.py`: OK with the two existing EN14825 section LOC
  soft warnings only.
- `tools/code_checker/build_reference_map.py`: OK; map changed for three new
  source modules and their import/symbol inventory.
- `git diff --check`: OK before report creation; final check performed before
  commit.

## Changed Files

- `apps/calculator/ui/en14825/scop_batch_session.py`
- `apps/calculator/ui/batch_dialogs/profiles/en14825_scop.py`
- `apps/calculator/ui/batch_dialogs/profiles/en14825_scop_dialog.py`
- `tests/test_ui_tk_en14825_scop_batch_dialog.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/412_en14825_scop_batch_profile_rebuild_snapshot.md`

## Known Failures / Risks

- Parent SCOP section wiring and end-to-end dialog launch remain for the next
  thin slice.
- No platform-specific manual visual smoke was run.
- The generic shell combined-snapshot protocol remains intentionally unchanged;
  the SCOP wrapper keeps the profile-local `last_snapshot` bridge.

## Scope Compliance

- Parent section, generic shell/table, core, data, config, and golden files were
  not modified.
- Profile composition is split into 242 LOC orchestration, 105 LOC headless
  state, and an 80 LOC shell wrapper.

## Code Map

- `code_map_check`: regenerated.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` is included in the diff.

## Commit / Push

- Final validation passed; implementation and report are committed and pushed
  together.

## Project Memory Delta

- none.

## Next Suggested Action

EN14825 SCOP batch parent section wiring.
