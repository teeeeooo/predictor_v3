# 208 — calculator_tk batch UI parity correction

## Goal

Correct the Hong Kong CSPF batch UI entry and presentation while preserving the 206 batch model/spec/handler structure.

## Scope

- Remove the separate `CSPF Batch` metric tab.
- Open Hong Kong CSPF batch mode from the existing CSPF page with a `Multi 입력` button.
- Keep the existing single-case Hong Kong CSPF immediate calculation flow.
- Keep 207 Hong Kong HSPF load-line/UI behavior unchanged.

## Preflight

- 206 added a separate `CSPF Batch` tab through `Iso16358Tab._render_region()`.
- That tab was included in hidden metric-tab measurement and could inflate the initial Hong Kong calculator size.
- `BatchProfileSpec`, `BatchTableModel`, `HongKongCspfBatchHandler`, and `BatchCalculationController` were reusable.
- PyQt reference uses a `Multi 입력` button that opens a dialog, not a primary calculator tab.

## Changed Files

- `ui_tk/batch_models.py`
- `ui_tk/batch_case_table.py`
- `ui_tk/sections/hong_kong_cspf_batch_section.py`
- `ui_tk/sections/hong_kong_cspf_section.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_ui_tk_batch_models.py`
- `tests/test_ui_tk_iso_table_autocalc.py`

## UI Correction

- Removed `HongKongCspfBatchSection` construction from `Iso16358Tab`.
- Added `HongKongCspfBatchDialog`, a `Toplevel` owner for the existing batch section.
- Added `HongKongCspfSection.batch_button` with text `Multi 입력`.
- Reused an existing open batch dialog on repeated button clicks instead of creating duplicate windows.
- Closed any open batch dialog when the owning CSPF section is destroyed.

## Batch Table UX

- Kept `BatchCaseTable` and `BatchTableModel`.
- Changed the batch table shell from spaced independent entry/label cells to a bordered grid using existing `layout_constants` table tokens.
- Input columns remain editable entries.
- Result/status columns remain labels and are not user-editable.
- TSV paste remains scoped to input columns.
- Added `Remove Row`; model keeps at least one row.

## Window Sizing

Batch mode is no longer a hidden metric notebook tab, so `preferred_initial_size()` measures only the single-case CSPF/HSPF sections before the batch dialog is opened. The batch dialog owns its own geometry.

## Preserved Behavior

- Hong Kong CSPF declared capacity input remains in the single-case page.
- Hong Kong CSPF immediate auto-calc remains unchanged.
- Hong Kong HSPF 207 behavior remains unchanged.
- Core calculator formulas, region config, golden expected values, and batch calculation handler logic were not changed.

## 207 Manual Verification Closeout

User Windows/manual verification for 207 is considered complete:

- Hong Kong HSPF rated heating capacity input removal confirmed.
- 7 Full / 7 Half inputs calculate without rated heating capacity.
- Values were checked as normal against the official calculator.

## Verification

- `python -m pytest -q tests/test_ui_tk_batch_models.py`: 5 passed
- `python -m pytest -q tests/test_ui_tk_hong_kong_cspf_batch_spec.py`: 3 passed
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py`: 25 passed
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py`: 11 passed, 11 skipped
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py`: 8 passed, 37 skipped
- Combined focused run: 52 passed, 48 skipped
- `python -m py_compile ...`: passed for modified UI/test modules
- `python3 -B tools/check_code_structure.py`: passed with existing `ui_tk/sections/bin_detail_panel.py` soft LOC warning
- `git diff --check`: passed

## Manual Smoke Needed

Codex environment has no `DISPLAY`, so GUI runtime smoke was not run.

Windows checks:

- Open `app_calculator_tk.py`.
- Select Hong Kong.
- Confirm metric tabs are only `CSPF` and `HSPF`; no `CSPF Batch` tab is shown.
- Confirm CSPF page has `Multi 입력`.
- Click `Multi 입력` and confirm a separate CSPF Batch window opens.
- Confirm repeated clicks focus/reuse the existing batch window.
- Paste TSV into input columns and run batch.
- Confirm result/status columns are not directly editable.
- Confirm closing the batch window does not resize the main calculator window.

## Excluded

- Core calculator changes.
- Hong Kong HSPF load-line changes.
- CSPF/HSPF golden expected changes.
- Region config changes.
- HSPF/EN/AHRI/KS batch implementation.
- Detail/bin schema, graph/export, internal formula trace, or C# WPF work.

## Next Action

Run the Windows manual smoke above. If accepted, continue with common detail/bin result schema design rather than expanding batch scope in this correction.
