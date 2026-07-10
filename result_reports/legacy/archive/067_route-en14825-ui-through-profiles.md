# 067 Route EN14825 UI Through Profiles

## Goal

Reduce the remaining direct JSON scan path in `ui/calc_window.py` by routing EN14825 through calculator profiles and the dispatcher.

## Scope

- `core/calculator_profiles.py`
- `core/calculator_dispatcher.py`
- `ui/calc_window.py`
- `tests/test_calculator_profiles.py`
- `tests/test_calculator_dispatcher.py`
- `tests/test_app_calculator_ui_smoke.py`
- Managed docs that describe current UI/profile routing state

## Non-goals

- No EN14825 formula changes.
- No EN golden value changes.
- No UI redesign.
- No ML adapter expansion.
- `calculate_en()` remains a dummy result path for a separate EN UI calculation task.

## Changed Files

- `core/calculator_profiles.py`
- `core/calculator_dispatcher.py`
- `ui/calc_window.py`
- `tests/test_calculator_profiles.py`
- `tests/test_calculator_dispatcher.py`
- `tests/test_app_calculator_ui_smoke.py`
- `docs/WORK_PLAN.md`
- `docs/REFACTOR_PLAN.md`
- `docs/architecture/project_architecture.md`
- `project_brief.md`
- `result_reports/active/067_route-en14825-ui-through-profiles.md`

## Verification

- `python3 -B -m py_compile core/calculator_profiles.py core/calculator_dispatcher.py ui/calc_window.py`
  - passed
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py tests/test_app_calculator_ui_smoke.py tests/test_en14825_golden.py tests/test_calculator_schema_boundaries.py -q`
  - `43 passed`
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest tests/test_app_calculator_ui_smoke.py tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py tests/test_en14825_golden.py -q`
  - `40 passed`
- `rg -n "en14825_scop|EN_14825|EN14825 SCOP|_populate_en_profiles|combo_region_en|calculator_id=\\\"en14825\\\"|calculator_id == \\\"en14825\\\"" core ui tests docs/WORK_PLAN.md docs/REFACTOR_PLAN.md docs/architecture/project_architecture.md project_brief.md`
  - confirmed profile, dispatcher, UI, tests, and docs references.
- `git diff --check`
  - passed before source commit.

## Task Results

- Added enabled profile `en14825_scop`.
- Added dispatcher support for `calculator_id="en14825"`.
- Changed EN combo population from region-config JSON scanning to profile registry item data.
- `on_region_changed_en()` now builds the selected calculator through `create_calculator_for_profile()`.
- Added resolver, dispatcher, and offscreen UI smoke coverage for the EN profile selector.
- Updated work/refactor plan, architecture docs, and project brief to match the current routing state.

## Known Risks

- EN tab calculation output remains a placeholder string. This task only routes EN calculator construction through profiles.
- Other UI paths outside `ui/calc_window.py` may still have direct config scanning and should be audited separately if they become active work.

## Commit / Push

- Source commit: `bc184e7` (`feat: route EN14825 UI through calculator profiles`).
- Report commit: this commit (`report: record EN14825 UI profile routing`).
- Push: deferred until final objective push.
