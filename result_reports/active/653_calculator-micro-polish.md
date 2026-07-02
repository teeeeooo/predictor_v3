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

## Verification

- `python3 -m py_compile apps/calculator/ui/calculator_app.py apps/calculator/ui/tabs/iso16358_tab.py` - OK
- `PYTHONPATH=. pytest -q tests/test_ui_tk_calculator_foundation.py` - OK, 13 passed / 11 skipped
- `git diff --check` - OK
- `git status --short` - checked before report creation; only scoped files were modified

## Structure / Reuse

- change_gate: visual-only micro polish; no reusable helper or theme owner added.
- Sibling surface check: existing Tk sections already use `ttk.LabelFrame`; reused that toolkit-native boundary instead of introducing a custom style or helper.
- code_map_check: skipped; no new surface, helper, adapter, public route, or structural inventory change.
- Structure Warnings: none observed for changed scope; structure guard not run because this slice does not add a new responsibility boundary.

## Changed Files

- `apps/calculator/ui/calculator_app.py`
- `apps/calculator/ui/tabs/iso16358_tab.py`
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
