# 189-e Profile Switch Default Exact-fit Hotfix

Date: 2026-05-29

## Goal

Replace the 189-d grow-only profile switch behavior with default exact-fit sizing. Manual smoke showed that grow-only left awkward blank space when switching Hong Kong -> ISO/ISEER 2-point.

## Changed Files

- `ui_tk/window_geometry.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/189e_profile-switch-default-exact-fit-hotfix.md`

## Implementation

- Restored profile-switch exact-fit via `fit_window_to_preferred_content()`.
- Removed the current-window-size floor from profile switch sizing.
- Kept the measured overflow delta one-shot grow after exact-fit.
- Kept scroll top reset after profile switch.
- Kept the no-overflow wheel guard from 189-c.

## Verification

- py_compile for changed source/tests -> OK
- `python3 -B tools/check_code_structure.py` -> OK
- quick smoke -> 2 passed
- focused suite -> 45 passed
- `git diff --check` -> OK
- leftover pytest process check -> none after verification

Full pytest was intentionally not run.

## Manual Check Result

- User confirmed the profile switch exact-fit behavior works as intended.
- Window geometry polish for this slice is closed; move on to the next work item.
- Further geometry tuning should be treated as a known limitation unless a new blocking issue appears.

## Known Risks

- This exact-fit policy can extend to future tabs/profiles, but it depends on each tab/profile reporting an accurate preferred size.
- Hidden tabs, graph/detail, and dynamic result surfaces need their preferred size owner checked in their own future design slices.
- If profile-switch geometry polish is still unsatisfactory after this hotfix, record it as a known limitation and move to the next feature slice.

## Excluded Scope

- No 2-point section/result table, ResultPanel, resolver, core/config/golden/fixture, PyQt, SASO, multi/batch, detail/trace, graph, EN/AHRI, project log, memory seed, or lifecycle changes.

## Commit / Push

- Source/test commit: `bcdb12a fix: exact fit iso profile switch window`
- Docs/report commit: `e516e30 report: profile switch exact fit hotfix`
- Push: completed to `origin/work/ui-ux-ssot-adoption`

## Project Memory Delta

- none
