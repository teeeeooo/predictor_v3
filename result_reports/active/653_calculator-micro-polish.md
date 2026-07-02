# Calculator Micro Polish

## Goal

- Add a minimal visual distinction for the calculator top-level notebook tabs.
- Make the ISO 16358 profile selector boundary easier to recognize.
- Keep this branch as a main-based micro polish after discarding the prior UI polish branch.

## Scope

- Branch source: `main`, new branch `feature/calculator-micro-polish`.
- Changed only the allowed UI/test files plus this report.
- No cherry-pick or implementation reuse from `feature/calculator-ui-polish`.

## Non-goals

- No calculator logic, table/result/button color, scroll/window geometry, lifecycle, nested notebook sizing, broad theme, or dashboard-style restyle changes.
- No new `theme.py`.
- No unrelated refactor.

## Task Results

- task 1: OK - applied a small `CalculatorTop.TNotebook` style only to the app shell notebook with modest tab padding and selected-tab font/foreground emphasis.
- task 2: OK - changed the ISO profile selector container from a plain frame to a `ttk.LabelFrame(text="프로파일 선택")` with small internal padding.
- task 3: OK - extended the Tk foundation smoke to confirm the app notebook, ISO tab, and profile selector widgets exist without pixel/color assertions.

## Follow-up Task Results

- AHRI SEER2 action buttons: OK - `일괄 입력` and `상세 보기` now share one gridded action row with packed horizontal children.
- AHRI HSPF2 action buttons: OK - batch access remains the dialog lifecycle owner, but its button is now created inside the section action row alongside the detail toggle.
- HSPF2 main UI labels/order: OK - visible heating columns are `H01, H11, H2v, H32, H42, H1N(STD), H12, H22`; internal `H2Int` and `H1N` field keys are unchanged.
- HSPF2 batch labels/order: OK - batch matrix uses the same heating display order and labels as the main UI, with `A2` retained as the separate anchor point.
- H1N/H2Int policy: OK - H1N required policy, H2Int internal adapter/schema naming, optional point policy, and core calculator behavior were not changed.

## Verification

- `python3 -m py_compile apps/calculator/ui/calculator_app.py apps/calculator/ui/tabs/iso16358_tab.py` - OK
- `PYTHONPATH=. pytest -q tests/test_ui_tk_calculator_foundation.py` - OK, 13 passed / 11 skipped
- `python3 -m py_compile apps/calculator/ui/sections/ahri_seer2_section.py apps/calculator/ui/sections/ahri_hspf2_section.py apps/calculator/ui/ahri/hspf2_batch_access.py apps/calculator/ui/ahri/hspf2_batch.py` - OK
- `PYTHONPATH=. pytest -q tests/test_apps_calculator_ui_ahri_seer2.py` - OK, 9 passed / 2 skipped
- `PYTHONPATH=. pytest -q tests/test_apps_calculator_ui_ahri_hspf2.py` - OK, 7 passed / 3 skipped
- `PYTHONPATH=. pytest -q tests/test_ui_tk_ahri_hspf2_batch.py` - OK, 4 passed / 3 skipped
- `PYTHONPATH=. pytest -q tests/test_ui_tk_calculator_foundation.py` - OK, 13 passed / 11 skipped
- `git diff --check` - OK
- `git status --short` - checked before commit; only scoped follow-up files were modified

## Structure / Reuse

- change_gate: visual-only micro polish; no reusable helper or theme owner added.
- Sibling surface check: existing Tk sections already use `ttk.LabelFrame`; reused that toolkit-native boundary instead of introducing a custom style or helper.
- Follow-up reuse check: HSPF2 main and batch display order/labels now share a small UI-only constant/helper in the existing `hspf2_batch.py` owner instead of duplicating the map or changing the application adapter.
- code_map_check: skipped; the new helper is a local UI display-label helper only, with no new surface, adapter, public route, or structural inventory change.
- Structure Warnings: none observed for changed scope; structure guard not run because this slice does not add a new responsibility boundary.

## Changed Files

- `apps/calculator/ui/calculator_app.py`
- `apps/calculator/ui/tabs/iso16358_tab.py`
- `apps/calculator/ui/sections/ahri_seer2_section.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`
- `apps/calculator/ui/ahri/hspf2_batch_access.py`
- `apps/calculator/ui/ahri/hspf2_batch.py`
- `tests/test_apps_calculator_ui_ahri_seer2.py`
- `tests/test_apps_calculator_ui_ahri_hspf2.py`
- `tests/test_ui_tk_ahri_hspf2_batch.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `result_reports/active/653_calculator-micro-polish.md`

## Known Risks

- Manual GUI smoke remains pending to visually close out the subtle tab/profile selector distinction on a real display.

## Next Suggested Action

- Next: manual GUI smoke closeout

## Commit / Push

- Commit and push results are reported in the final terminal response to avoid a self-referential report hash update loop.

## Project Memory Delta

- none
