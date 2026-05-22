# 089 — AHRI HSPF2 v3 Horizontal Table Input (Second UI Slice)

## Goal

Switch the AHRI HSPF2 v3 heating test-point input portion of the
calculator UI from the long vertical `QFormLayout` to a horizontal
spreadsheet-style table (`QTableView` + `QAbstractTableModel`),
following Slice B of
`docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md` and
the global `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`.

AHRI SEER2 table from slice 088 is kept; EN14825 and ISO16358 UI are
not touched. HSPF2 calculator engine is not modified; expected values
are not changed.

## Scope

- `ui/spreadsheet_table.py`: add `AHRI_HSPF2_COLUMNS`,
  `AHRI_HSPF2_ROW_LABELS`, and `make_ahri_hspf2_table_model()`
  factory. No change to `SpreadsheetTableModel` itself.
- `tests/test_spreadsheet_table_model.py`: add factory shape tests
  (column/row labels) and `as_point_dict` round-trip test for the new
  HSPF2 factory; also add a SEER2 factory shape test for symmetry.
- `ui/calc_window.py`: replace the H01..H32 per-point `QFormLayout`
  rows with a `QTableView` bound to the new HSPF2 model; keep the
  four auxiliary fields (`t_off`, `t_on`,
  `defrost_t_test_minutes`, `defrost_t_max_minutes`) in a compact
  `QFormLayout` inside the same group; add
  `_read_ahri_hspf2_table_points()` helper; route
  `_build_hspf2_v3_input()` through the model.
- `tests/test_app_calculator_ui_smoke.py`: add a
  `_fill_ahri_hspf2_table` helper; replace the HSPF2 input-fill in
  the HP smoke; add two new tests (HSPF2 table layout +
  `as_point_dict` shape); replace
  `test_hspf2_input_widgets_have_no_duplicate_rows` with
  `test_ahri_hspf2_input_uses_horizontal_table_layout` reflecting the
  new dict shape (only 4 auxiliary keys remain).
- `docs/WORK_PLAN.md`: mark the AHRI HSPF2 slice as done; queued next
  action is now EN14825 horizontal table-input slice.
- `result_reports/active/089_ahri-hspf2-horizontal-table-input-slice.md`:
  this report.

## Non-goals

- No EN14825 / ISO16358 UI change.
- No AHRI SEER2 table restructure (088 implementation is preserved).
- No `app_calculator.py` redesign.
- No `calculate_hspf2_v3` calculator engine edit; no expected /
  golden change.
- No `CalculatorInputEnvelope`, `core/calculator_unit_adapter.py`,
  adapter chain, region config, or ML caller edit.
- No `QTableWidget`; no `setCellWidget`.
- No ISO16358-2 HSPF mismatch audit; no xfail change.
- No clipboard / view-keybinding controller implementation.

## Verification

- `python3 -B -m py_compile ui/spreadsheet_table.py ui/calc_window.py
  tests/test_app_calculator_ui_smoke.py` → OK.
- `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q`
  → `32 passed` (was `27`; added 5 new tests).
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q`
  → `13 passed` (was `12`; the HSPF2 layout test replaced the
  duplicate-row test, and an HSPF2 `as_point_dict` test was added —
  net +1).
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → `3 passed`.
- `python3 -B -m pytest -q` → `442 passed, 34 xfailed`. Baseline
  before this task was `436 passed, 34 xfailed`; the +6 delta is
  exactly the new spreadsheet model + UI smoke tests. xfail count
  unchanged.

## Task Results

### Task 1 — `make_ahri_hspf2_table_model()` factory

Files modified:

- `ui/spreadsheet_table.py` — added `AHRI_HSPF2_COLUMNS` constant
  `("H01", "H11", "H12", "H1N", "H22", "H2Int", "H32")`,
  `AHRI_HSPF2_ROW_LABELS` constant
  `("능력 [Btu/h]", "전력 [W]")`, and
  `make_ahri_hspf2_table_model(parent=None)` factory that builds a
  `SpreadsheetTableModel` with that shape. The factory is a thin
  wrapper; `SpreadsheetTableModel` itself is unchanged.
- `tests/test_spreadsheet_table_model.py` — added five new tests:
  - `test_ahri_seer2_factory_uses_locked_column_and_row_labels`
  - `test_ahri_hspf2_columns_and_rows_match_design_doc`
  - `test_ahri_hspf2_factory_uses_locked_column_and_row_labels`
  - `test_ahri_hspf2_as_point_dict_returns_calculator_test_point_shape`
  - `test_ahri_hspf2_as_point_dict_rejects_missing_value`

Table shape (after factory):

- Columns: `H01, H11, H12, H1N, H22, H2Int, H32` (7).
- Rows: `능력 [Btu/h]` (capacity, index 0) and `전력 [W]` (power,
  index 1).

Output of `model.as_point_dict(capacity_row=0, power_row=1)`:

```python
{
    "H01":   (capacity, power),
    "H11":   (capacity, power),
    "H12":   (capacity, power),
    "H1N":   (capacity, power),
    "H22":   (capacity, power),
    "H2Int": (capacity, power),
    "H32":   (capacity, power),
}
```

This is exactly the per-point portion of
`HSPF2Calculator.calculate_hspf2_v3`'s `test_points` dict; the `A2`
point used by HSPF2 v3 is sourced separately from the AHRI SEER2
table's `A_Full` column (slice 088).

### Task 2 — Wire HSPF2 table into `ui/calc_window.py`

Files modified: `ui/calc_window.py`.

Range converted to a table:

- The seven HSPF2 v3 heating points
  (`H01 / H11 / H12 / H1N / H22 / H2Int / H32`) × two fields
  (capacity / power) are now a single `QTableView` driven by
  `self.ahri_hspf2_model` (built via `make_ahri_hspf2_table_model`).
- Columns stretch to fill width;
  `QAbstractItemView.ExtendedSelection` and the standard edit
  triggers are enabled. No `setCellWidget`.
- `self.ahri_hspf2_view` is the `QTableView`; `self.ahri_hspf2_model`
  is the model.
- The previous 14 `QFormLayout.addRow` calls for HSPF2 heating
  points are removed; the parent `QGroupBox`
  (`3. HSPF2 v3 난방 테스트 포인트`) now holds a `QVBoxLayout`
  that stacks the table on top of the auxiliary compact form.

Auxiliary inputs kept as compact form (`input_widgets_hspf2`):

- `t_off` (°F)
- `t_on` (°F)
- `defrost_t_test_minutes`
- `defrost_t_max_minutes`

All four remain `QLineEdit`s under `input_widgets_hspf2`. The
existing `bind_error_reset` loop still binds them; it now iterates
over `input_widgets_ahri` (Cd_low / Cd_full) + `input_widgets_hspf2`
(four aux keys) only.

Per-point keys removed from `input_widgets_hspf2`: every
`{point}_cap` and `{point}_pow` for the seven heating points.
`input_widgets_hspf2` is **not** deleted as the user instructed;
auxiliary keys still live there. The dict size goes from 18 keys (7×2
points + 4 aux) to 4 keys (4 aux only).

Read path:

- New helper `_read_ahri_hspf2_table_points()` reads all seven
  columns and returns the `{point: (capacity, power)}` dict; per-cell
  empty / non-numeric / non-positive values raise
  `InputValidationError` with a Korean message naming the offending
  point and field (e.g. `AHRI HSPF2 H22 능력 (Btu/h) 값을
  입력해주세요.` or `AHRI HSPF2 H22 능력 (Btu/h)은 0보다 큰 값이어야
  합니다.`).
- `_build_hspf2_v3_input()` now derives `test_points` from
  - `A2 = self._read_ahri_seer2_point("A_Full")` (SEER2 table; from
    slice 088) and
  - `self._read_ahri_hspf2_table_points()` (HSPF2 table; this slice).
  `kwargs` (`t_off`, `t_on`, `defrost_*`) still reads through
  `_get_float_val` on the auxiliary `QLineEdit`s.

Validation / error display:

- Per-cell validation messages are routed through
  `InputValidationError`. Because the offending element is a table
  cell (not a `QLineEdit`), the exception is created without
  `e.widget`; `on_calculate` shows the popup with the message text
  but does not apply the inline-LineEdit border tint to the table
  cell. Inline cell-error rendering is left to a future
  delegate-paint slice (same deferral as 088).

### Task 3 — Smoke test refactor

Files modified: `tests/test_app_calculator_ui_smoke.py`.

- New helper `_fill_ahri_hspf2_table(window, points)` mirrors the
  existing `_fill_ahri_seer2_table` helper. Writes `(capacity,
  power)` into the HSPF2 model by column index.
- `test_ahri_hp_calculate_button_displays_seer2_and_hspf2_results`
  (updated) — uses `_fill_ahri_hspf2_table` for HSPF2 heating
  points; t_off / t_on / defrost minutes still go through
  `input_widgets_hspf2`. HP smoke result label still must contain
  both `"AHRI SEER2 (HP) 결과:"` and `"HSPF2 v3 결과:"`. Pass.
- `test_hspf2_input_widgets_have_no_duplicate_rows` is replaced by
  two new tests:
  - `test_ahri_hspf2_input_uses_horizontal_table_layout` — asserts
    the model exposes the expected `column_labels` and `row_labels`;
    the per-point `*_cap` / `*_pow` keys are absent from
    `input_widgets_hspf2`; and the dict's surviving key set is
    exactly the four auxiliary inputs. Pass.
  - `test_ahri_hspf2_table_as_point_dict_matches_calculator_input_shape`
    — fills the HSPF2 table and asserts
    `as_point_dict(capacity_row=0, power_row=1)` returns the
    expected seven-point tuple dict. Pass.
- `test_hspf2_required_input_raises_validation_error_when_missing`
  (unchanged from 088) — still writes only the SEER2 `A_Full`
  column; the HSPF2 table is empty; `calculate_hspf2_v3` raises
  `InputValidationError`. The error now originates in the new
  `_read_ahri_hspf2_table_points()` helper instead of the old
  `_get_float_val` path; the test still asserts only that
  `InputValidationError` is raised, so it remains green without
  modification.

PyQt optional skip: the module-level
`pytest.importorskip("PyQt5")` is preserved, so in a PyQt5-less
environment all tests in this file (including the new HSPF2 tests)
skip at collection time. `QT_QPA_PLATFORM=offscreen` is still set.
No OS clipboard / GUI manual interaction; no new expected /
golden numbers introduced.

### Task 4 — Docs sync

Files modified: `docs/WORK_PLAN.md`.

- `Current milestone focus`: added a bullet for the AHRI HSPF2
  horizontal table conversion and `make_ahri_hspf2_table_model()`;
  the SEER2 bullet was tightened to drop the "AHRI HSPF2 vertical
  form은 그대로 유지" tail because it is no longer true.
- `Near-term execution order`: AHRI HSPF2 slice is removed from the
  queued list because it is done. The queue is now just EN14825
  horizontal table-input slice (Slice C → Slice D). Unit adapter
  expansion to ISO / KS / EN profile and ML / inverse-search
  resumption remain below the EN14825 slice. ISO16358-2 HSPF
  mismatch stays parked as a user-side external audit.
- Trailing completed-prerequisites paragraph now lists
  `ui/spreadsheet_table.py`, `core/calculator_unit_adapter.py`,
  `tests/test_calculator_envelope_chain.py`, AHRI SEER2 slice, **and**
  AHRI HSPF2 slice as done.

## Test Results

- `python3 -B -m py_compile ui/spreadsheet_table.py ui/calc_window.py
  tests/test_app_calculator_ui_smoke.py` → exit 0.
- `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q`
  → `32 passed`.
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q`
  → `13 passed`.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → `3 passed`.
- `python3 -B -m pytest -q` → `442 passed, 34 xfailed`.

## Changed Files

- `ui/spreadsheet_table.py` — new `AHRI_HSPF2_COLUMNS`,
  `AHRI_HSPF2_ROW_LABELS`, and `make_ahri_hspf2_table_model()`
  factory. `SpreadsheetTableModel` and the SEER2 factory are
  unchanged.
- `ui/calc_window.py` — AHRI HSPF2 v3 vertical `QFormLayout` rows
  replaced with a `QTableView` + table model and a compact
  auxiliary form; new helper `_read_ahri_hspf2_table_points`;
  `_build_hspf2_v3_input` now reads HSPF2 points from the model;
  imports of `make_ahri_hspf2_table_model` added; new instance
  attributes `self.ahri_hspf2_model` and `self.ahri_hspf2_view`.
- `tests/test_spreadsheet_table_model.py` — five new tests for the
  SEER2 / HSPF2 factories and HSPF2 `as_point_dict` round-trip.
- `tests/test_app_calculator_ui_smoke.py` — new
  `_fill_ahri_hspf2_table` helper; HP smoke fills the HSPF2 table
  via the helper; new `test_ahri_hspf2_input_uses_horizontal_table_layout`
  and `test_ahri_hspf2_table_as_point_dict_matches_calculator_input_shape`;
  obsolete `test_hspf2_input_widgets_have_no_duplicate_rows` removed.
- `docs/WORK_PLAN.md` — AHRI HSPF2 slice completion + queued next
  actions.
- `result_reports/active/089_ahri-hspf2-horizontal-table-input-slice.md`
  — this report.

## Known Failures / Risks

- The HSPF2 table, like the SEER2 table from 088, does not yet have
  a delegate that paints an invalid-cell marker.
  `is_cell_invalid` is available on the model, and
  `_read_ahri_hspf2_table_points` fails fast with a clear Korean
  message, so the user cannot silently pass bad input through. A
  follow-up slice should add a single delegate that covers both AHRI
  tables.
- `InputValidationError` for table cells does not currently apply
  the inline-LineEdit border tint (`e.widget` is `None`). Same
  limitation as 088; deferred to the delegate slice.
- Table view keybindings (Ctrl+C / Ctrl+V / Ctrl+Z, Tab / Enter
  navigation) still pass through the default `QTableView` behavior;
  the model exposes the helpers
  (`selected_to_tsv`, `paste_tsv`, `clear_cells`, `undo`) but the
  controller wiring slice is intentionally deferred.
- `input_widgets_hspf2` now contains only the four auxiliary fields.
  No external production code references the per-point keys; only
  the smoke test `test_hspf2_input_widgets_have_no_duplicate_rows`
  did, and it has been replaced.

## Next Suggested Action

1. **EN14825 horizontal table-input slice — Slice C (SCOP)** first:
   - New factory `make_en14825_scop_table_model()` in
     `ui/spreadsheet_table.py` (columns
     `A, B, C, D, TOL, Tbiv`; rows `능력 [kW]`, `전력 [kW]`).
   - Replace the per-point `_capacity` / `_power` QLineEdits in the
     EN tab with a `QTableView` while keeping `p_design_h`,
     `climate`, `TOL_temp_c`, `Tbiv_temp_c`, and standby powers in a
     compact form.
   - Update EN SCOP smoke (`test_en_calculate_button_displays_scop_result_text`)
     to fill the new table.
2. **Slice D (SEER)** afterward (columns `A, B, C, D`; same row
   labels), reusing the SCOP factory pattern.
3. After all three calculator profiles share the table component,
   start the delegate slice that paints invalid-cell markers and
   wires view-side keybindings.

## Scope Compliance

- AHRI SEER2 table (slice 088) is unchanged.
- EN14825 tab unchanged.
- ISO16358 tab unchanged.
- `app_calculator.py` unchanged.
- `core/calculator_*.py` engines unchanged; no calculator logic
  edit; no HSPF2 expected / golden change.
- No region config, ML feature schema, or calculator result schema
  edit.
- `CalculatorInputEnvelope`, `core/calculator_unit_adapter.py`, and
  the adapter chain unchanged.
- No `QTableWidget` or `setCellWidget` introduced.
- ISO16358-2 HSPF mismatch list and xfail set unchanged.
- `input_widgets_hspf2` dict is preserved for auxiliary fields; only
  the seven per-point `*_cap` / `*_pow` keys are removed because
  their backing widgets no longer exist.

## Commit / Push

- Source + tests + docs commit: a single commit covering
  `ui/spreadsheet_table.py`, `ui/calc_window.py`,
  `tests/test_spreadsheet_table_model.py`,
  `tests/test_app_calculator_ui_smoke.py`, `docs/WORK_PLAN.md`.
- Report commit: this report as a separate commit (`report: ...`
  style).
- Both commits pushed to `origin/work/iso-separation-plan`.
