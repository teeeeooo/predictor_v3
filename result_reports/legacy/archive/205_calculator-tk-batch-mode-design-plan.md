# 205 Calculator Tk Batch Mode Design Plan

## Goal

Plan `calculator_tk` simple batch mode before implementation. The batch mode should repeat existing calculator calls for multiple user-entered cases and show one result row per case without changing calculator formulas, fixtures, golden data, region config, or existing single-case behavior.

## Current State

- Branch/status: `main`, up to date with `origin/main`, clean before this report.
- Recent direction:
  - 204 closed the C# WPF spike without merging WPF code to `main`.
  - `docs/WORK_PLAN.md` now sets `calculator_tk simple batch mode` as the next action.
  - Batch result is explicitly not internal formula trace.
- Current Tkinter shell:
  - `app_calculator_tk.py` is a thin entrypoint.
  - `ui_tk/calculator_app.py` builds `CalculatorTkApp`, creates one `ttk.Notebook`, and adds `Iso16358Tab`.
  - `ui_tk/tabs/iso16358_tab.py` owns ISO mode/profile selection and creates section classes.
- Current Hong Kong CSPF single-case flow:
  - `HongKongCspfSection` owns immediate calculation.
  - `MetricInputTable` renders rated and test input matrices.
  - `ExcelLikeTableController` owns copy/paste/clear/undo/navigation for those input tables.
  - `DebouncedAutoCalc` schedules `recalculate_now()`.
  - `resolve_profile_id("Hong Kong", "CSPF")` maps UI labels to `hong_kong_cspf`.
  - `create_calculator_for_profile(profile_id="hong_kong_cspf")` creates the core calculator.
  - `build_cspf_input()` maps UI values to core inputs.
  - `summarize_cspf_result()` formats core outputs.
- Existing PyQt batch mode:
  - No active reusable PyQt batch calculator flow was found in the searched main files.
  - `app_calculator.py` is only a PyQt entrypoint to `ui.calc_window.CalculatorWindow`.
- Existing table foundations:
  - `MetricInputTable` is good for fixed single-case matrix inputs, not arbitrary row-per-case batch output.
  - `TableGrid` / `TableGridModel` are pure/simple editable grid foundations but do not yet cover mixed editable/result/status columns or Excel-like controller parity.
  - Treeview result tables already exist for read-only comparison/detail surfaces and table copy/export.

## Batch Mode Requirements

Confirmed requirements:

- Batch mode is not internal formula trace.
- Batch mode is not detail/bin trace.
- Batch mode is a simple repeated-calculation result table.
- Initial UI shape is one row per case.
- Users enter multiple case rows and see result columns on the same row.
- Initial Hong Kong CSPF columns:
  - `Case`
  - `Declared`
  - `35 Full Cap`
  - `35 Full Power`
  - `35 Half Cap`
  - `35 Half Power`
  - `CSPF`
  - `CSEC`
  - `Status`
- Calculation reuses the existing single calculator/core path.
- Output formatting should reuse existing result formatter behavior where possible.

Excluded:

- No formula trace, bin/detail trace, graph/export, or detail/bin schema implementation.
- No calculator core formula changes.
- No fixture/golden/region config changes.
- No C# WPF work.
- No implementation in this task.

Implementation questions to resolve in the next coding slice:

- Initial row count and row add/remove UI: recommended first slice is a small fixed starter count plus Add Row / Clear Results controls, not dynamic import/export.
- Whether batch lives as a separate Hong Kong metric tab label (`CSPF Batch`) or a separate section below the CSPF single-case surface. Recommendation: separate tab/section so the default single-case immediate-calc flow stays unchanged.
- Whether batch recalculates on paste or only on explicit Run. Recommendation: explicit Run for batch because multiple rows can be partially valid and calculation may be more expensive.

## Structure Judgment

### Recommended Structure

Use a common batch surface with profile-specific specs/handlers.

First implementation profile:

- Hong Kong CSPF only.
- Use the existing `hong_kong_cspf` core profile.
- Reuse `build_cspf_input()`, `resolve_profile_id()`, `create_calculator_for_profile()`, and CSPF result formatting helpers.

Common surface responsibilities:

- Render a row-per-case editable table.
- Distinguish input columns, result columns, and status columns.
- Support Excel-like copy/paste for input columns.
- Keep result/status cells read-only.
- Provide explicit Run Batch and Clear Results actions.
- Keep row-level validation state visible.

Profile spec/handler responsibilities:

- Define user-facing input/result/status columns.
- Define default row template.
- Map one UI row to calculator input.
- Select calculator profile id without exposing raw profile ids in labels.
- Run the existing calculator method.
- Map result dict to display columns.
- Map exceptions to row `Status`.

### Why Not Single-Profile Hardcode

A Hong Kong-only hardcoded table would be fastest, but it would put profile-specific column keys and result mapping directly into the UI surface. That creates several risks:

- HSPF, EN14825, AHRI, and KS will need different input and output columns.
- UI table schema could leak into calculator core or dispatcher calls.
- Future profile additions would copy/paste table code.
- Error/status/result formatting would diverge by section.

### Why Not a Full Generic Framework Now

A large shared framework is also not justified yet. The first slice should avoid a generic result-surface rewrite and avoid changing `ResultPanel` or existing detail tables.

Recommended compromise:

- Build one small reusable `BatchCaseTable` / model surface that knows column roles.
- Build one `HongKongCspfBatchSpec` / handler.
- Keep registration explicit and local.
- Add more profile specs only after the Hong Kong CSPF slice passes manual smoke.

## Candidate Files

Likely new files:

- `ui_tk/batch_models.py`
  - `BatchColumnSpec`
  - `BatchColumnRole`
  - `BatchRowState`
  - `BatchProfileSpec`
- `ui_tk/batch_case_table.py`
  - `BatchCaseTable`
  - row add/remove, copy/paste, read-only result/status rendering
- `ui_tk/batch_controller.py`
  - `BatchCalculationController`
  - Run Batch, Clear Results, row validation orchestration
- `ui_tk/sections/hong_kong_cspf_batch_section.py`
  - `HongKongCspfBatchSection`
  - profile-specific UI composition
- `ui_tk/sections/hong_kong_cspf_batch_spec.py`
  - `HongKongCspfBatchSpec`
  - row-to-core mapping and result formatting

Likely modified files:

- `ui_tk/tabs/iso16358_tab.py`
  - add the batch section without changing the existing `CSPF` single-case section behavior
- `ui_tk/sections/iso16358_helpers.py`
  - only if a pure helper is needed to share CSPF row mapping; do not move widget logic here
- `tests/test_ui_tk_batch_models.py`
- `tests/test_ui_tk_hong_kong_cspf_batch_spec.py`

Files/areas not to touch in the first implementation:

- `core/calculator_iso16358.py`
- `core/calculator_dispatcher.py` public behavior
- `core/calculator_profiles.py` profile ids/config paths
- `data/region_configs/*.json`
- golden expected files
- existing single-case `HongKongCspfSection` behavior except optional import/wiring for the new batch section
- detail/bin graph/export code

## Implementation Steps

1. Add pure batch model/spec dataclasses.
   - Keep them toolkit-neutral.
   - Include column roles: `input`, `result`, `status`.
   - Include row validation state without calculator calls.
2. Add Hong Kong CSPF batch spec.
   - Input columns map to `declared_capacity`, `full_capacity`, `full_power`, `half_capacity`, `half_power`.
   - Build core input with `build_cspf_input()`.
   - Resolve and call existing `hong_kong_cspf`.
   - Format `CSPF`, `CSEC`, and row `Status`.
3. Add batch table surface.
   - Use a Tkinter table/grid with editable input cells and read-only result/status cells.
   - Reuse existing numeric parsing rules where possible.
   - Support paste into input columns.
   - Do not expose demo rows; starter rows are real case rows.
4. Add controller.
   - Run rows on explicit Run Batch.
   - Validate each row independently.
   - Keep invalid rows in table and mark status rather than aborting all rows.
   - Update result/status cells in the same row.
5. Wire UI.
   - Add a separate batch section/tab for Hong Kong CSPF.
   - Preserve the existing single-case immediate-calculation CSPF flow.
6. Add focused tests.
   - Pure model/spec tests first.
   - No broad GUI tests unless needed for smoke.

## Validation Plan For Implementation Slice

Code-side checks:

- `python -m pytest -q tests/test_ui_tk_batch_models.py`
- `python -m pytest -q tests/test_ui_tk_hong_kong_cspf_batch_spec.py`
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py`
- `python3 -B tools/check_code_structure.py`
- `git diff --check`

Manual GUI smoke:

- Launch `python app_calculator_tk.py`.
- Confirm existing single-case Hong Kong CSPF tab still auto-calculates without pressing Run.
- Open the batch section/tab.
- Enter/paste two valid cases.
- Run batch.
- Confirm each row shows `CSPF`, `CSEC`, and `Status`.
- Compare one batch row result with the existing single-case CSPF result using the same inputs.
- Paste TSV data into input columns.
- Copy selected batch rows to TSV if implemented in the first slice.
- Confirm result/status cells are read-only.
- Confirm invalid row shows row-local error/status and does not prevent valid rows from calculating.

Packaging impact:

- No new heavy dependencies should be added.
- Tkinter-only code should keep current packaged-size assumptions.
- Avoid creating `.bat` or `.exe` helper artifacts in the repo.

Failure boundary checks:

- If numeric parsing fails, inspect batch model/spec validation.
- If profile resolution fails, inspect `profile_resolver` usage and spec profile mapping.
- If CSPF differs from single-case output, inspect row-to-core mapping before suspecting core formulas.
- If paste/copy behavior is weak, inspect table surface/controller boundaries rather than calculator logic.

## Next Action

Implement the first slice as Hong Kong CSPF batch only, using common batch surface + profile spec/handler boundaries. Keep the existing single-case calculator untouched and validate one batch row against the current single-case CSPF path.

## Scope Compliance

- No code implementation was performed.
- No UI behavior was changed.
- No calculator core, fixture, golden, or region config file was modified.
- No detail/bin schema, graph/export, internal formula trace, or C# WPF work was performed.

## Verification

Executed for this report task:

- `git diff --check`
  - passed
- `python3 -B tools/check_code_structure.py`
  - exited `0` with existing warning:
    - `[W] ui_tk/sections/bin_detail_panel.py: file exceeds 400 LOC soft limit (437). Consider splitting before adding more responsibilities.`
- `git status --short`
  - confirmed only this new report file before commit

Not planned:

- pytest, because this task only writes a design/report and does not change code.
- GUI smoke, because no UI code changed.

## Commit / Push

- Final commit hash and push status are recorded in the terminal summary for this task.

## Project Memory Delta

```yaml
- type: decision
  topic: calculator_tk_batch_mode_design
  content: predictor_v3 calculator_tk batch mode should start with Hong Kong CSPF only but use a common batch surface plus profile-specific spec/handler boundaries so future HSPF, EN14825, AHRI, and KS batch profiles can vary input/output columns without leaking UI table schema into calculator core.
  keywords:
    - predictor_v3
    - calculator_tk
    - batch mode
    - profile spec
    - UI boundary
  assertionStatus: observed
  source: result_reports/active/205_calculator-tk-batch-mode-design-plan.md
```
