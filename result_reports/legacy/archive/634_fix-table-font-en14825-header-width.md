# Goal

- Set calculator table typography to 10pt across the shared Tk table owner, including batch table consumers.
- Prevent EN14825 main input table row headers from clipping long labels such as `Declared capacity [W]` and `Tested power [W]`.

# Scope

- Changed shared calculator Tk table font size in `apps/calculator/ui/layout_constants.py`.
- Added an EN14825-specific row-header width constant in the same visual/layout owner.
- Applied that row-header width to EN14825 SEER and SCOP main input tables only.
- Added focused tests for the global table font constant and EN14825 row-header width binding.

# Non-goals

- No calculator logic, schema, public keys, or label text changes.
- No table interaction behavior changes.
- No broad table component refactor.

# Verification

- `xvfb-run -a python3 -m pytest tests/test_apps_calculator_ui_en14825.py::test_en14825_gui_integration tests/test_apps_calculator_ui_en14825.py::test_en14825_tab_composes_seer_scop_and_refits_on_scop_toggle tests/test_apps_calculator_ui_en14825_scop.py::test_scop_gui_integration_basics tests/test_ui_tk_iso_table_autocalc.py::test_metric_inputs_render_bordered_matrix_cell_roles -q` - passed, 4 tests.
- `python3 -B tools/check_code_structure.py` - passed with existing soft warnings.
- `git diff --check` - passed.

# Task Results

- `TABLE_FONT_SIZE` is now `10`; `TABLE_BODY_FONT` and `TABLE_HEADER_FONT` inherit it.
- EN14825 SEER and SCOP main input tables now use `METRIC_TABLE_EN14825_ROW_HEADER_CHARS = 22`.
- The wider EN14825 row header is scoped to the EN14825 main tables; auxiliary/common compact tables keep their existing widths.

# Test Results

- Added SEER GUI assertions that the shared table font size is 10 and that the declared-capacity row header uses the EN14825 width.
- Added SCOP GUI assertion that the average-climate main input table uses the EN14825 row-header width.

# Changed Files

- `apps/calculator/ui/layout_constants.py`
- `apps/calculator/ui/sections/en14825_seer_section.py`
- `apps/calculator/ui/sections/en14825_scop_section.py`
- `tests/test_apps_calculator_ui_en14825.py`
- `tests/test_apps_calculator_ui_en14825_scop.py`

# Known Failures / Risks

- Manual visual inspection was not performed; validation used Xvfb-backed Tk widget construction and assertions.
- Global table font size affects all calculator Tk table consumers that import `TABLE_BODY_FONT` / `TABLE_HEADER_FONT`, including batch tables as intended.

# Reference / Structure Notes

- Reuse/commonization decision: reused the existing shared visual/layout owner and `MetricInputTable` constructor knobs; no new helper or table component was introduced.
- Structure Warnings: existing soft LOC warnings remain for `apps/calculator/ui/sections/en14825_seer_section.py` and `apps/calculator/ui/sections/en14825_scop_section.py`; accepted for this narrow visual/layout slice because no new responsibility was added.
- `code_map_check`: skipped; this is a small visual/layout constant and existing surface binding change, with no new owner/helper/module or source structure change.

# Next Suggested Action

- Run the app manually on the target desktop display and confirm EN14825 SEER/SCOP row labels are visually unclipped at the default window size.

# Scope Compliance

- Stayed within app-calculator Tk UI table presentation.
- Did not modify calculator formulas, region config, model schema, or public result keys.

# Commit / Push

- Code commit: `ffd58d3fde54a73bde162cb56dd5085421a24c97`
- Report commit: separate follow-up commit.
- Push: report commit to be pushed separately.

# Project Memory Delta

- none
