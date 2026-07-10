# 577 Arc 9.5 Dropdown Option Adapter Boundary

## Goal

- Move base dropdown option lookup and raw mapping section parsing out of
  `PredictWorkspace`.

## Scope

- Added `apps/predict/adapters/dropdown_option_adapter.py`.
- Wired `PredictWorkspace` to use `DropdownOptionAdapter` for fallback/base
  options while keeping row-specific cascade options from
  `InputEditController`.
- Added focused adapter behavior tests and a workspace source guard.

## Non-goals

- No mapping JSON schema, autofill core logic, ML, calculator, or UI visual
  layout changes.
- Workspace row command/state mutation cleanup remains a later slice.

## Verification

- `PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest -q tests/test_apps_predict_mapping_backed_dropdown.py` - OK, 9 passed.
- `python3 -B tools/check_code_structure.py` - OK with pre-existing unrelated soft warnings and code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE; not regenerated in this focused adapter slice.
- `git diff --check` - OK.

## Task Results

- `PredictWorkspace` no longer calls `.mapping_repository.load()` for dropdown
  options and no longer parses raw mapping sections.
- `DropdownOptionAdapter` owns fallback refrigerant/expansion options and
  mapping-backed base option extraction.
- Row-specific cascade options remain owned by `InputEditController`; the
  adapter prefers those options when provided.

## Reference Parity / Change Gate

- Existing `apps/predict/adapters/` package was reused instead of adding a
  helper in the UI package.
- Reuse/commonization decision: dropdown option lookup is Predict-specific
  mapping adapter behavior, not a generic table delegate concern. No broader
  common owner exists yet.
- `code_map_check`: checked; stale before this slice, not regenerated because
  the map was already stale and the change is a small app-side adapter.

## Structure Warnings

- No changed/new source file emitted a LOC/class warning.
- Existing unrelated calculator and code-map freshness warnings remain.

## Changed Files

- `apps/predict/adapters/dropdown_option_adapter.py`
- `apps/predict/ui/workspace.py`
- `tests/test_apps_predict_mapping_backed_dropdown.py`

## Known Risks

- Missing/corrupt mapping file behavior continues to depend on
  `PredictMappingRepository.load()` behavior.

## Commit / Push

- Commit: pending for this slice.
- Push: deferred per user request until all slices complete.

## Project Memory Delta

- none
