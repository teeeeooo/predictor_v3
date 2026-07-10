# 088 — AHRI SEER2 Horizontal Table Input (First UI Slice)

## Goal

Switch only the AHRI SEER2 cooling input portion of the calculator UI
from the long vertical `QFormLayout` to a horizontal
spreadsheet-style table (`QTableView` + `QAbstractTableModel`). The
table follows the global
`docs/ui/SPREADSHEET_TABLE_CONTRACT.md` contract via the existing
`ui/spreadsheet_table.py` component; AHRI HSPF2, EN14825, and
ISO16358 UI surfaces remain unchanged in this slice.

This is Slice A of the calculator horizontal table design
(`docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`).

## Scope

- `ui/spreadsheet_table.py`: add an AHRI SEER2 factory
  (`make_ahri_seer2_table_model`) plus the column / row label
  constants. No new behavior on `SpreadsheetTableModel` itself.
- `ui/calc_window.py`: replace the AHRI SEER2 five-point `QFormLayout`
  with a `QTableView` bound to the new model; rewire
  `calculate_ahri()` and `_build_hspf2_v3_input()` to read points from
  the model via `_read_ahri_seer2_table_points` /
  `_read_ahri_seer2_point` helpers; keep `Cd_low` / `Cd_full` and the
  AHRI HSPF2 vertical form unchanged.
- `tests/test_app_calculator_ui_smoke.py`: refactor the AC / HP /
  HSPF2-validation tests so they fill the new table model; add two
  new tests for the SEER2 table layout and `as_point_dict()` shape.
- `docs/WORK_PLAN.md`: mark the AHRI SEER2 slice as done; queued next
  action is now AHRI HSPF2 slice → EN14825 slice.
- `result_reports/active/088_ahri-seer2-horizontal-table-input-slice.md`:
  this report.

## Non-goals

- No AHRI HSPF2 UI conversion.
- No EN14825 / ISO16358 UI change.
- No `app_calculator.py` redesign.
- No calculator engine, region config, ML feature schema, calculator
  result schema, adapter, or unit conversion change.
- No ISO16358-2 HSPF mismatch audit; no xfail change.
- No `QTableWidget` introduced; no `setCellWidget` introduced.
- `input_widgets_ahri` dict is preserved: only the five-point
  per-cell `*_cap` / `*_pow` `QLineEdit` keys are removed because they
  no longer exist as widgets. `Cd_low` and `Cd_full` stay there as
  before.

## Verification

- `python3 -B -m py_compile ui/spreadsheet_table.py ui/calc_window.py
  tests/test_app_calculator_ui_smoke.py` → OK.
- `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q`
  → `27 passed`.
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q`
  → `12 passed` (was `10 passed`; two new tests for the SEER2 table
  layout and `as_point_dict()` shape).
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → `3 passed`. The new `ui/spreadsheet_table.py` factory does not
  add any `core/calculator_*.py` modifications.
- `python3 -B -m pytest -q` → `436 passed, 34 xfailed`. Baseline was
  `434 passed, 34 xfailed`; the +2 delta is exactly the two new UI
  smoke tests. xfail count is unchanged.

## Task Results

### Task 1 — AHRI SEER2 table model factory

Files modified: `ui/spreadsheet_table.py`.

New additions (no change to existing API):

- Constants
  - `AHRI_SEER2_COLUMNS = ("A_Full", "B_Full", "B_Low", "E_Int",
    "F_Low")`
  - `AHRI_SEER2_ROW_LABELS = ("능력 [Btu/h]", "전력 [W]")`
- Factory `make_ahri_seer2_table_model(parent=None)`:
  - Returns a `SpreadsheetTableModel` shaped for AHRI SEER2 input.
  - Raises `ImportError` if PyQt5 is unavailable (the helper itself
    requires Qt).

Output of `model.as_point_dict(capacity_row=0, power_row=1)` is

```python
{
    "A_Full": (capacity, power),
    "B_Full": (capacity, power),
    "B_Low":  (capacity, power),
    "E_Int":  (capacity, power),
    "F_Low":  (capacity, power),
}
```

which is exactly the `test_points` shape
`AHRICalculator.calculate_seer2()` accepts. No new behavior on
`SpreadsheetTableModel` was added; the factory is a thin construction
helper.

### Task 2 — Wire AHRI SEER2 table into `ui/calc_window.py`

Files modified: `ui/calc_window.py`.

Range converted to a table:

- The five SEER2 points
  (`A_Full / B_Full / B_Low / E_Int / F_Low`) × two fields
  (capacity / power) are now a single `QTableView` driven by
  `self.ahri_seer2_model` (built via the factory above).
- Columns are stretched to fill width;
  `QAbstractItemView.ExtendedSelection` and the standard edit
  triggers (double-click, edit-key, any-key) are enabled. No
  `setCellWidget` is used.
- `self.ahri_seer2_view` is the `QTableView`; `self.ahri_seer2_model`
  is the model.
- The previous two `QGroupBox`es (`1. Full Load 조건` and
  `2. Part Load / Low Speed 조건`) are merged into a single
  `1. SEER2 냉방 시험 포인트 (A_Full ~ F_Low)` group containing the
  table. Existing `2. 추가 파라미터 (Optional)` (Cd_low / Cd_full) and
  `3. HSPF2 v3 난방 테스트 포인트` are renumbered accordingly.

Range kept exactly as before:

- `Cd_low` / `Cd_full` stay as `QLineEdit`s in `input_widgets_ahri`
  (compact form).
- AHRI HSPF2 v3 input (`H01..H32`, `t_off`, `t_on`,
  `defrost_t_test_minutes`, `defrost_t_max_minutes`) stays in the
  existing `QFormLayout` under `input_widgets_hspf2`.
- `bind_error_reset` binding for `input_widgets_ahri.values()` still
  iterates only over `Cd_low / Cd_full` (which are `QLineEdit`s);
  table cells are intentionally not bound to the LineEdit-style
  error-style reset, per task instructions.
- ISO / EN tabs are not touched.

Validation / error handling:

- `_read_ahri_seer2_table_points()` reads all five columns and
  returns the `{point: (capacity, power)}` dict; per-cell empty,
  non-numeric, or non-positive values raise `InputValidationError`
  with a Korean message naming the offending column and field
  (`AHRI SEER2 A_Full 능력 (Btu/h) 값을 입력해주세요.`, etc.).
- `_read_ahri_seer2_point(point_id, col_index=None)` reads a single
  column with the same validation messages; used by
  `_build_hspf2_v3_input()` so HSPF2 v3 derives `A2` from the SEER2
  table without re-implementing checks.
- `calculate_ahri()` no longer reads SEER2 LineEdits through
  `_get_float_val`; it routes through
  `_read_ahri_seer2_table_points()` instead. The on_calculate path
  catches `InputValidationError` exactly as before (popup +
  cell-style highlight where `e.widget` is set; for table cells the
  message-only popup path is used).
- `coerce_numeric` is imported from `ui.spreadsheet_table` for cell
  parsing; it tolerates whitespace / empty / non-numeric.

### Task 3 — Smoke test refactor

Files modified: `tests/test_app_calculator_ui_smoke.py`.

New / updated tests:

- `_fill_ahri_seer2_table(window, points)` — helper that writes a
  `{point: (capacity, power)}` dict directly into the SEER2 model.
  Avoids any OS-clipboard dependency.
- `test_ahri_seer2_input_uses_horizontal_table_layout` (new) — asserts
  the table model exposes the expected `column_labels` and
  `row_labels`, and that the per-point `*_cap` / `*_pow` keys are
  gone from `input_widgets_ahri` while `Cd_low` / `Cd_full` remain.
- `test_ahri_seer2_table_as_point_dict_matches_calculator_input_shape`
  (new) — fills the table and asserts
  `as_point_dict(capacity_row=0, power_row=1)` returns the expected
  five-point tuple dict.
- `test_ahri_hp_calculate_button_displays_seer2_and_hspf2_results`
  (updated) — uses `_fill_ahri_seer2_table` for SEER2 input; HSPF2
  v3 input still goes through the existing `input_widgets_hspf2`
  form; HP smoke result label must contain both
  `"AHRI SEER2 (HP) 결과:"` and `"HSPF2 v3 결과:"`. Pass.
- `test_ahri_calculate_button_displays_result_text` (updated) —
  uses `_fill_ahri_seer2_table` for AC smoke; result label must
  contain `"AHRI SEER2 (AC) 결과:"`. Pass.
- `test_hspf2_required_input_raises_validation_error_when_missing`
  (updated) — writes only the AHRI SEER2 `A_Full` column via
  `model.set_cell` (the rest of the HSPF2 vertical form is empty);
  `calculate_hspf2_v3` raises `InputValidationError`. Pass.

PyQt optional skip: the existing module-level
`pytest.importorskip("PyQt5")` is preserved, so in a PyQt5-less
environment all tests in this file (including the new ones) skip at
collection time. No OS clipboard dependency, no real GUI launch —
the offscreen Qt platform plugin is set via
`QT_QPA_PLATFORM=offscreen`. No expected numeric value was added as a
golden; tests assert on result label substrings only.

### Task 4 — Docs sync

Files modified: `docs/WORK_PLAN.md`.

Changes:

- Current milestone focus bullet for the spreadsheet table component
  was updated to call out that the AHRI SEER2 surface is now driven
  by `make_ahri_seer2_table_model()` (and that AHRI HSPF2 and EN are
  still on the previous forms).
- Near-term execution order: the AHRI SEER2 horizontal table-input
  first slice is removed from the queued list because it is done;
  the queue is now (1) AHRI HSPF2 horizontal table-input slice,
  (2) EN14825 table-input slice. ISO16358-2 HSPF mismatch is still
  parked as a user-side external audit.
- The trailing completed-prerequisites paragraph now lists
  `ui/spreadsheet_table.py`, `core/calculator_unit_adapter.py`,
  `tests/test_calculator_envelope_chain.py`, **and** the AHRI SEER2
  horizontal table-input UI slice as done.

## Test Results

- `python3 -B -m py_compile ui/spreadsheet_table.py ui/calc_window.py
  tests/test_app_calculator_ui_smoke.py` → exit 0.
- `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q`
  → `27 passed`.
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q`
  → `12 passed`.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → `3 passed`.
- `python3 -B -m pytest -q` → `436 passed, 34 xfailed`.

## Changed Files

- `ui/spreadsheet_table.py` — new `AHRI_SEER2_COLUMNS`,
  `AHRI_SEER2_ROW_LABELS`, and `make_ahri_seer2_table_model()`
  factory. `SpreadsheetTableModel` itself unchanged.
- `ui/calc_window.py` — AHRI SEER2 two QFormLayouts replaced with a
  single `QTableView` + table model; new helpers
  `_read_ahri_seer2_table_points` /
  `_read_ahri_seer2_point`; `calculate_ahri()` and
  `_build_hspf2_v3_input()` route SEER2 reads through the model;
  imports of `QTableView` / `QHeaderView` /
  `QAbstractItemView` added; `coerce_numeric` and the factory
  imported from `ui/spreadsheet_table.py`.
- `tests/test_app_calculator_ui_smoke.py` — `_fill_ahri_seer2_table`
  helper; two new tests for the table layout + point-dict shape;
  AC / HP / HSPF2-validation tests refactored to use the table.
- `docs/WORK_PLAN.md` — AHRI SEER2 slice completion + queued next
  actions.
- `result_reports/active/088_ahri-seer2-horizontal-table-input-slice.md`
  — this report.

## Known Failures / Risks

- The SEER2 table does not yet expose a visual error indicator for
  invalid cells; `is_cell_invalid` is available on the model but no
  delegate paints the marker yet. Calculator-side validation
  (`_read_ahri_seer2_table_points`) still fails fast with a clear
  Korean message, so users cannot silently pass bad input through.
  Adding a delegate is left to a follow-up slice and may piggyback on
  the AHRI HSPF2 table slice.
- The `bind_error_reset` LineEdit-style error highlight cannot apply
  to table cells. When a SEER2 cell fails validation, the user sees
  the popup but the offending cell does not get an inline border /
  background tint. Inline cell-error rendering is also a delegate
  concern and is deferred.
- Manual `QTableView` interactions (Tab / Enter navigation, Ctrl+C /
  Ctrl+V / Ctrl+Z keybindings) are not wired to the model's helper
  methods yet; the model exposes everything the controller needs
  (`paste_tsv`, `selected_to_tsv`, `clear_cells`, `undo`) but the
  view-side keybinding hookup is deferred to a follow-up slice.
- `Cd_low` / `Cd_full` remain in `input_widgets_ahri`. Future slices
  may move them into the table-aware compact form area; for now the
  task instruction to keep them as-is is honored.

## Next Suggested Action

1. **AHRI HSPF2 horizontal table-input slice** (Slice B of
   `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`):
   - New factory `make_ahri_hspf2_table_model()` in
     `ui/spreadsheet_table.py` (columns
     `H01, H11, H12, H1N, H22, H2Int, H32`; rows
     `능력 [Btu/h]`, `전력 [W]`).
   - Replace `input_widgets_hspf2` per-point QLineEdits with the
     table; keep `t_off`, `t_on`, `defrost_t_test_minutes`,
     `defrost_t_max_minutes` in a compact form.
   - Update HP-mode smoke tests to fill the new HSPF2 table.
2. Then **EN14825 table-input slice** (Slice C → SCOP, Slice D →
   SEER).
3. Wire view-side keybindings (Ctrl+C / Ctrl+V / Ctrl+Z, Tab / Enter
   navigation) to the model helpers in a separate slice once at least
   two profiles share the table component.

## Scope Compliance

- AHRI HSPF2 input form is unchanged.
- EN14825 tab unchanged.
- ISO16358 tab unchanged.
- `app_calculator.py` unchanged.
- `core/calculator_*.py` engines unchanged; no calculator logic edit.
- No region config, ML feature schema, or calculator result schema
  edited.
- `CalculatorInputEnvelope`, `core/calculator_unit_adapter.py`, and
  the adapter chain unchanged.
- No `QTableWidget` or `setCellWidget` introduced.
- ISO16358-2 HSPF mismatch list and xfail set unchanged.
- `input_widgets_ahri` dict is preserved; only the five-point
  per-cell `*_cap` / `*_pow` keys are removed because their backing
  `QLineEdit` widgets no longer exist. `Cd_low` and `Cd_full` are
  kept exactly as before, matching the task instruction not to remove
  the dict entirely.

## Commit / Push

- Source + tests + docs commit: a single commit covering
  `ui/spreadsheet_table.py`, `ui/calc_window.py`,
  `tests/test_app_calculator_ui_smoke.py`, `docs/WORK_PLAN.md`.
- Report commit: this report as a separate commit (`report: ...`
  style).
- Both commits pushed to `origin/work/iso-separation-plan`.
