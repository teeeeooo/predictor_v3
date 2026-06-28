# Arc 9.5 Full Audit Report and Correction Plan
Predictor v3 — Unified Case Table / Train-Predict Visual Architecture Review

Generated: 2026-06-28  
Repo: `teeeeooo/predictor_v3`  
Audited ref: `main` at `bdeb6fd990f36a0b8434f4e66e7a13f5af40475c`  
Primary change range checked: `0fff2aa..bdeb6fd990f36a0b8434f4e66e7a13f5af40475c`  
User manual smoke status: **Arc 9.5 closeout rejected**

## 0. Executive Summary

Arc 9.5 should be reopened again. The final closeout report claims acceptance, but the current code still contains several structural and UX violations that match the user's manual smoke findings.

The problems are not isolated to one bad widget. They indicate a wider pattern across the Arc 9.5 changes:

1. Some UI elements look visually close but are not connected to the actual table mechanics.
2. Some tests assert construction or presence of widgets rather than validating the real user interaction contract.
3. Some UI widgets still own state mutation, mapping lookup, or visual data structures that should belong to controller/adapter/model boundaries.
4. The Trainer visual panels introduced table-shaped `QTableWidget` surfaces despite the project architecture banning `QTableWidget`.
5. The final report advanced the project to Arc 10 even though manual smoke found baseline Arc 9.5 issues.

Recommended decision:

- Do **not** proceed to Arc 10 yet.
- Create an Arc 9.5 correction branch or direct main follow-up, depending on repo policy.
- First commit an audit report in `result_reports/active/`.
- Then correct in focused slices, starting with the fake table group header and dropdown editor because those are user-visible baseline failures.
- Update docs from "Arc 10 current" back to "Arc 9.5 correction after manual smoke" until the manual smoke is actually passed.

---

## 1. Audit Scope

### 1.1 Changed/new files from Arc 9.5 closeout range

The GitHub compare for `0fff2aa..bdeb6fd` reports 38 changed files after Slice 1. The final closeout report also states Slice 1 through Slice 11 commits and categories, including newly added active reports and tests.

### 1.2 Source files audited

#### Predict unified table

- `apps/predict/schema/case_table_schema_adapter.py`
- `apps/predict/ui/tables/case_table_model.py`
- `apps/predict/ui/tables/case_table_view.py`
- `apps/predict/ui/tables/delegates.py`
- `apps/predict/ui/tables/undo.py`
- `apps/predict/ui/workspace.py`
- `apps/predict/controllers/input_edit_controller.py`
- `apps/predict/state/predict_session.py`

#### Train visual surfaces

- `apps/train/ui/shell.py`
- `apps/train/ui/train_model_panel.py`
- `apps/train/ui/data_mapping_panel.py`

#### Shared UI style

- `apps/common/ui/style.py`
- `ui_common/visual_tokens.py`

#### Tests

- `tests/test_apps_predict_workspace_unified_table.py`
- `tests/test_apps_predict_spreadsheet_ux.py`
- `tests/test_apps_predict_mapping_backed_dropdown.py`
- `tests/test_apps_train_shell.py`
- related existing table/schema/style tests by reference

#### Docs/reports

- `docs/architecture/pyside6_train_predict_architecture.md`
- `docs/architecture/project_architecture.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- `result_reports/active/573_arc95-final-acceptance-closeout.md`

### 1.3 Audit limitations

- I did not execute the application locally.
- I did not run GUI/manual smoke.
- I audited GitHub source and docs directly and cross-checked the user's manual smoke findings against code.
- The user's manual smoke findings are source-confirmed.

---

## 2. Governing Contract Summary

### 2.1 Spreadsheet table UX contract

The active table contract defines a table-shaped surface as more than a visual grid. It must implement selection, copy/paste, clear, undo, navigation, edit/replace behavior, and read-only roles.

Key requirements:

- Multi-cell rectangular selection.
- Copy as TSV.
- Paste from TSV.
- Grouped undo.
- Tab/Enter navigation and shifted variants.
- Click/type replace-on-type.
- Read-only result cell copy and mutation prevention.
- Single click selects a cell; printable key from selection mode starts whole-cell replacement.
- Same active-cell click, double-click, and F2 enter edit mode.
- Read-only cells are included in copy but excluded from paste/clear.
- Undo stack is local to the table and cleared when the data context changes.

### 2.2 Input matrix / result surface rules

Repeated case data should be one coherent matrix table with visible row/column headers. Splitting one logical matrix into multiple mini-grids is a failed shape unless distinct ownership genuinely requires it.

### 2.3 Architecture boundary

The architecture requires:

- Thin app entrypoints.
- Predict UI under `apps/predict`.
- Train UI under `apps/train`.
- Predict workspace reused by Train without duplicating Predict code.
- Table model exposes data and editability but does not call mapping repository, prediction service, training execution, or calculators.
- Table view owns spreadsheet mechanics but does not call mapping repository, prediction service, training execution, or calculators.
- Mapping/cascade access should be hidden behind app-side mapping/cascade adapters and controller boundaries.
- `QTableWidget` is forbidden by project architecture; use `QTableView + QAbstractTableModel`.

---

## 3. Critical Findings

## F1. Fake unified group header is not a real table header

Severity: Critical  
Files:

- `apps/predict/ui/workspace.py`

Evidence:

- `PredictWorkspace._build_table_panel()` adds `self._build_group_band()` above the table before adding the table widget.
- `_build_group_band()` creates a separate `QFrame` with `QHBoxLayout` and `QLabel`s for `Input`, `Auto-fill / Calculated`, `Prediction Results`, and `Status / Warning`.
- The width computation uses static sums of initial column widths.
- There is no connection to `QHeaderView.sectionResized`, `QHeaderView.sectionMoved`, `horizontalScrollBar().valueChanged`, or the table viewport offset.

Impact:

- The group header is visually detached from the actual table.
- Horizontal scroll moves cells but not the group labels.
- Column resize/scroll causes group labels to drift.
- This exactly matches the user's manual smoke finding.
- It violates the "visible-as-selected" unified table intention because the visible hierarchy is not part of the real table surface.

Contract violation:

- `03_SPREADSHEET_TABLE_UX_CONTRACT.md`: table implementations must prove the table inside the existing workflow, not only as a standalone grid visual.
- `02_DESIGN_TOKENS_AND_LAYOUT.md`: horizontal scrolling must stay inside the table widget with headers visible.
- `pyside6_train_predict_architecture.md`: the view may provide or coordinate grouped column header visual affordance, but the final table must remain one coherent table surface.

Correction direction:

Preferred:

- Implement a table-linked group header using a `QHeaderView` subclass or a dedicated `GroupHeaderView` component that is geometrically tied to the table.
- It must recompute group rectangles from `sectionViewportPosition()`, `sectionSize()`, and current horizontal scroll.
- It must update on section resize, horizontal scroll, model reset, column hidden/shown changes.

Acceptable simpler option:

- Remove the fake group band entirely.
- Use normal column headers plus subtle group separators/background roles until a real table-linked group header is implemented.

Not acceptable:

- More manual spacing.
- Fixed pixel offsets.
- A top `QFrame` not linked to the table's header/scroll state.
- Calling it "non-pixel-perfect" while geometry is objectively detached.

Required tests:

- Offscreen header geometry helper test:
  - scroll table horizontally
  - assert group header rect changes consistently with first/last group columns
- section resize test:
  - resize one input column
  - assert group rect width changes
- workspace test:
  - no `ColumnGroupBand` detached from table unless it is a table-linked component

---

## F2. Dropdown editor is not editable and has no autocomplete

Severity: Critical  
Files:

- `apps/predict/ui/tables/delegates.py`
- `apps/predict/ui/workspace.py`
- `apps/predict/controllers/input_edit_controller.py`

Evidence:

- `DropdownDelegate.createEditor()` creates `QComboBox(parent)` and calls `combo.addItems(items)`.
- It never calls `combo.setEditable(True)`.
- It never configures a `QCompleter`.
- It immediately opens the popup via `QTimer.singleShot(0, combo.showPopup)`.
- `setModelData()` commits only `editor.currentText()`.

Impact:

- The cell behaves as a closed dropdown selector.
- Direct user typing is blocked or unreliable, matching the manual smoke finding.
- The intended workflow was "type a value + autocomplete + commit + autofill".
- Mapping-backed options exist, but the editor UX does not support the required interaction.

Contract violation:

- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` requires numeric, text, and drop-down cells to use appropriate editors.
- It also requires selection mode printable key to start whole-cell replacement, and edit mode to preserve/insert text at caret.
- Current dropdown behavior is one-click popup-first, not spreadsheet-style selection/edit lifecycle.

Correction direction:

- Make dropdown editors editable:
  - `combo.setEditable(True)`
  - attach case-insensitive `QCompleter`
  - use inline completion or popup completion
  - ensure typed custom values commit through `model.setData(index, combo.currentText(), Qt.EditRole)`
- Separate editor creation from selection:
  - single click should select the cell.
  - same active-cell click, double click, F2, printable key should enter edit mode.
  - clicking arrow affordance may open popup.
- Preserve one-click popup only if it does not violate selection mode. A dropdown arrow click affordance is acceptable; whole-cell click-to-popup is not.
- Keep mapping option source outside the delegate's repository access. Delegate should receive an option provider callable, not a mapping repository.

Required tests:

- editable combobox editor test:
  - create editor for dropdown cell
  - assert `isEditable()`
  - assert completer exists
- typed value commit test:
  - set editor text to a value not selected from popup
  - commit
  - assert `CaseTableModel.setData()` path updates `CaseRow.input_values`
- typed value triggers autofill:
  - type ODU or mapped key
  - commit
  - assert `InputEditController.handle_cell_edited()` side effects occur
- one-click selection test:
  - first click selects, not auto-popup unless arrow area is clicked

---

## F3. `PredictWorkspace` directly loads mapping data for dropdown options

Severity: High  
Files:

- `apps/predict/ui/workspace.py`
- `apps/predict/controllers/input_edit_controller.py`

Evidence:

- `PredictWorkspace._base_dropdown_options()` calls `self.mapping_repository.load()`.
- It reads raw `mapping_data.get(section_name, {})` and returns section keys.

Impact:

- A QWidget owns mapping access and raw mapping JSON shape.
- This weakens MVC/SoC and hexagonal boundary.
- Tests explicitly check that table model/view/delegate do not import mapping repository, but they do not check `PredictWorkspace`.
- The mapping boundary is therefore only partially enforced.

Contract violation:

- `pyside6_train_predict_architecture.md` defines `mapping_adapter.py` as the owner that hides raw mapping JSON structure from table model/view classes and mapping/cascade adapters for ODU cascade.
- The same architecture assigns mapping/autofill updates to controller/state boundaries, not QWidget-level mapping reads.
- `project_architecture.md` says cascading autofill should separate data lookup, signal-blocked value write, and UI rendering updates.

Correction direction:

- Add an app-side option provider boundary:
  - `apps/predict/adapters/mapping_adapter.py` or `apps/predict/adapters/dropdown_option_adapter.py`
  - or `apps/predict/controllers/dropdown_option_controller.py`
- `PredictWorkspace` should not parse raw mapping dicts.
- `PredictWorkspace` may wire a controller/provider into the delegate.
- `InputEditController` may remain owner of row-specific dropdown states.
- Base dropdown options should come from controller/adapter, not QWidget raw mapping reads.

Required tests:

- source guard:
  - `apps/predict/ui/workspace.py` must not contain `.mapping_repository.load()`
  - `apps/predict/ui/workspace.py` must not parse mapping section keys directly
- provider tests:
  - base options for IDU/ODU/compressor
  - row-specific ODU cascade options
  - missing mapping returns controlled empty/fallback option state

---

## F4. Train shell duplicates Predict header/status by embedding full `PredictWorkspace`

Severity: High  
Files:

- `apps/train/ui/shell.py`
- `apps/predict/ui/workspace.py`

Evidence:

- `TrainShell` builds a top status strip.
- `TrainShell` embeds `PredictWorkspace(tabs)` as the first tab.
- `PredictWorkspace` itself builds a title, status strip, command bar, table, and bottom status.
- In `app_train`, the Predict tab therefore shows both Train shell status and Predict workspace status/title.

Impact:

- User sees duplicate `모델 상태`, `progress`/status-like areas.
- Status ownership is ambiguous.
- Trainer shell and embedded Predict workspace both behave as screen shells.
- This is not just visual polish; it is an ownership problem.

Contract tension:

- Architecture says Trainer has header/status line and tabs.
- It also says Predict tab embeds the same `PredictWorkspace`.
- That can be correct only if `PredictWorkspace` has an embedded mode or if the screen-level shell/header is separated from the reusable workspace body.

Correction direction:

Preferred:

- Split Predict into:
  - `PredictWorkspaceBody` or `PredictCaseTableSurface`: table + command + bottom status
  - `PredictWorkspace`: standalone screen wrapper with title/status
- `app_predict` uses full standalone workspace/shell.
- `app_train` embeds body or workspace with `embedded=True`.

Simpler acceptable correction:

- Add explicit constructor options:
  - `show_title: bool = True`
  - `show_status_strip: bool = True`
  - maybe `show_bottom_status: bool = True` if needed
- `PredictShell` uses default full display.
- `TrainShell` uses `PredictWorkspace(show_title=False, show_status_strip=False)` or equivalent.
- Do not hide by objectName stylesheet hacks.

Required tests:

- `app_predict`/PredictShell still contains title/status.
- `app_train` Predict tab contains no duplicate top model/mapping/preprocess status.
- TrainShell still has its top shell status.
- PredictWorkspace reuse still exists; no duplicated Predict implementation under `apps/train`.

---

## F5. Trainer visual panels use `QTableWidget`, violating project architecture

Severity: Critical  
Files:

- `apps/train/ui/train_model_panel.py`
- `apps/train/ui/data_mapping_panel.py`
- `tests/test_apps_train_shell.py`

Evidence:

- `train_model_panel.py` imports `QTableWidget` and `QTableWidgetItem`.
- `_summary_table()` creates `QTableWidget`.
- `data_mapping_panel.py` imports `QTableWidget` and `QTableWidgetItem`.
- `_mapping_table()` creates `QTableWidget`.
- `tests/test_apps_train_shell.py` imports `QTableWidget` and asserts that it exists in TrainModelPanel and DataMappingPanel.

Impact:

- The test suite now codifies a forbidden architecture pattern.
- These are table-shaped surfaces with widget-owned data, not `QTableView + QAbstractTableModel`.
- This contradicts the project's own View Pattern guardrail.

Contract violation:

- `project_architecture.md` explicitly says `QTableWidget` is forbidden and `QTableView + QAbstractTableModel` must be used.
- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` says a grid that only looks like a table remains non-compliant until behaviors are present or the gap is reported.

Correction direction:

Preferred:

- Replace table-shaped Trainer placeholder tables with `QTableView + QAbstractTableModel`.
- Add:
  - `apps/train/ui/models/training_summary_model.py`
  - `apps/train/ui/models/mapping_status_model.py`
  - or local small models if the architecture accepts UI-local models
- Tests must assert `QTableView` and `QAbstractTableModel`, not `QTableWidget`.

Alternative if tables are not needed:

- Replace with cards/labels and do not present it as a table-shaped surface.
- Report why no table behavior baseline is required.

Required tests:

- no `QTableWidget` in `apps/train/ui`
- Train panels use `QTableView` for table-shaped surfaces
- train/mapping model returns expected row/column data
- no execution foundation imported

---

## F6. `PredictWorkspace` still owns too much state mutation and command handling

Severity: Medium-High  
Files:

- `apps/predict/ui/workspace.py`

Evidence:

- `_append_row()` directly calls `self.session.case_store.append_empty_rows()`.
- `_reset_rows()` directly removes rows/results and appends rows.
- `_remove_row_indexes()` directly calls `self.session.case_store.remove_rows()` and `self.session.remove_results_for_cases()`.
- `_handle_input_cell_edited()` calls `InputEditController`, updates model, and sets status.
- `_run_prediction()` calls `PredictionController` directly.

Impact:

- The QWidget is still a workflow orchestrator and state mutator.
- This keeps the app functional but weakens MVC/SoC.
- It makes later worker/progress and selected/dirty scope execution harder.
- It encourages more UI-layer fixes when behavior changes.

Contract tension:

- Architecture says command bar buttons should emit signals or call controller methods and should not mutate `PredictSession` directly.
- Predict controller should coordinate session, adapters, services, worker, and model refresh requests.
- Table edit controller should handle paste/clear/row insert/delete behavior.

Correction direction:

- Create or expand a table/session command controller:
  - row append/delete/reset
  - selected row resolution
  - affected result clearing
  - optional undo-stack reset after model reset
- Keep `PredictWorkspace` as view composition and signal wiring.
- `PredictWorkspace` may call controller methods and update UI labels from returned summaries/events.
- Do not move all UI behavior into controller; keep selection mechanics in view.

Required tests:

- source guard for direct case_store mutation in `workspace.py`
- controller row lifecycle tests
- workspace signal/action smoke

---

## F7. Table selection/edit state machine is incomplete or conflicts with dropdown behavior

Severity: High  
Files:

- `apps/predict/ui/tables/case_table_view.py`
- `apps/predict/ui/tables/delegates.py`

Evidence:

- `CaseTableView` sets edit triggers including `SelectedClicked`.
- `DropdownDelegate.editorEvent()` calls `self.parent().edit(index)` on `MouseButtonRelease` for dropdown columns.
- This means first-click or selected-click behavior may open edit/popup instead of preserving selection mode.
- `replace_current_cell()` calls `self.edit(index)` after `model.setData()` only if the view is visible. Tests may not catch visible runtime editor behavior.

Impact:

- Baseline spreadsheet behavior is likely inconsistent.
- Single click should select; same active-cell click / double click / F2 should enter partial edit.
- Dropdown behavior currently forces editing/popup too early.

Contract violation:

- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` gives explicit selection/edit state transitions. Single click selects; same active-cell click, double click, and F2 enter edit mode.
- The current `SelectedClicked` + delegate `MouseButtonRelease` path risks violating that lifecycle.

Correction direction:

- Implement explicit table edit-state controller inside `CaseTableView` or helper:
  - first click selects
  - second click on active cell enters edit mode
  - double click enters edit mode
  - F2 enters edit mode
  - printable key replaces whole cell and enters edit mode
- For dropdown:
  - arrow click opens popup
  - typing enters editable combo/line editor
  - same active-cell click may enter edit mode but should not necessarily force popup
- Tests should simulate mouse events, not only direct method calls.

Required tests:

- first click selects and does not open editor
- same active-cell second click opens editor
- double click opens editor
- F2 opens editor
- printable key replace opens editor and preserves typed text
- dropdown arrow popup path

---

## F8. Undo stack is not reset on context/model reset

Severity: Medium  
Files:

- `apps/predict/ui/tables/undo.py`
- `apps/predict/ui/tables/case_table_view.py`
- `apps/predict/ui/workspace.py`

Evidence:

- `TableUndoStack` has `clear()`.
- `PredictWorkspace._reset_rows()` resets the model/session but does not clear the table undo stack.
- `CaseTableView` does not appear to hook model reset/data context changes to `undo_stack.clear()`.

Impact:

- User can reset rows and then undo an edit from a previous data context.
- That can write stale values to new rows if row/col still exist.
- The table contract explicitly requires undo stack clearing when data context changes.

Correction direction:

- Expose `CaseTableView.clear_undo_history()`.
- Call it after reset/load/new data context.
- Optionally connect to model reset signals.
- Add test:
  - edit cell
  - reset rows
  - undo returns 0 and does not mutate new rows

---

## F9. Tests miss the manual smoke failures and in one case encode a violation

Severity: Critical  
Files:

- `tests/test_apps_predict_workspace_unified_table.py`
- `tests/test_apps_predict_mapping_backed_dropdown.py`
- `tests/test_apps_predict_spreadsheet_ux.py`
- `tests/test_apps_train_shell.py`

Findings:

1. Group header scroll/resize behavior is not tested.
   - Tests only assert one `CaseTableView` exists and split views do not.
   - They do not verify the visible group header tracks table columns.

2. Dropdown editable/autocomplete is not tested.
   - Mapping tests check option provider return values.
   - They do not create the delegate editor and assert editable combobox/completer behavior.
   - They do not simulate typed dropdown input and commit/autofill.

3. Train duplicate header/status is not tested.
   - Train tests only assert PredictWorkspace reuse.

4. `QTableWidget` is asserted as expected.
   - This test directly contradicts project architecture.

5. Mapping boundary source guard is too narrow.
   - It checks table model/view/delegate do not import mapping repository.
   - It does not check `workspace.py`, which currently loads mapping data directly.

6. Spreadsheet UX tests are method-centric.
   - Many tests call `replace_current_cell()`, `paste_tsv_at_selection()`, or direct key events.
   - They do not adequately exercise visible editor lifecycle, mouse click state transitions, or combo editor autocomplete.

Correction direction:

- Add regression tests before implementation fixes where possible.
- Make tests guard actual failure modes:
  - detached group header fails on scroll
  - dropdown editor not editable fails
  - Train embedded duplicate status fails
  - QTableWidget source guard fails
  - workspace direct mapping load fails
  - undo stack not cleared fails

---

## F10. Closeout docs are now inaccurate

Severity: High  
Files:

- `result_reports/active/573_arc95-final-acceptance-closeout.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`

Evidence:

- Report 573 marks unified case table, spreadsheet UX, mapping, visual, and Trainer checklist items as OK.
- The user's manual smoke disproves at least:
  - visual group header parity
  - dropdown editable/autocomplete
  - Trainer visual duplication
- Docs moved the project to Arc 10.

Impact:

- Project state is misleading.
- A subsequent agent will try to start Arc 10 on top of incomplete Arc 9.5.
- The reports overstate validation because automated tests did not cover manual failure modes.

Correction direction:

- Add new active report:
  - `574_arc95-full-audit-after-manual-smoke.md`
- Do not delete 573, but mark in Work Plan / project_brief that 573 is superseded by manual smoke reject.
- Move current next action back from Arc 10 to Arc 9.5 manual-smoke correction.
- Keep Arc 10 on hold.

---

## 4. Secondary Findings

## S1. Row-level error background may be too broad

Severity: Medium  
File:

- `apps/predict/ui/tables/case_table_model.py`

Evidence:

- `_background_for_cell()` checks result status before most column group coloring.
- Error/invalid/partial status can color the whole row, including input and auto columns.

Impact:

- This may be visually useful for row status, but it can obscure group semantics.
- User already reported strong status/card color issues earlier; this can repeat the same problem at cell level.

Correction direction:

- Render status severity primarily in status/message columns and row header or left indicator.
- Keep subtle row tint if needed, but preserve clear input/auto/result group backgrounds.
- Add visual token distinction for "row warning indicator" vs full cell background.

## S2. Style/token changes need a targeted visual token audit

Severity: Medium  
Files:

- `apps/common/ui/style.py`
- `ui_common/visual_tokens.py`

Impact:

- Arc 9.5 changed several token values and style helpers.
- No manual acceptance criteria appears to check contrast, intensity, or group readability beyond smoke tests.
- This is lower priority than structural fixes, but should be included in final visual correction.

Correction direction:

- After structural table fixes, perform a short token pass against the updated B-option reference.
- Do not tune colors before fixing structural header/dropdown defects.

---

## 5. Correction Plan

## Slice A — Reopen after Manual Smoke / Audit State Reset

Goal:

- Record that Arc 9.5 closeout 573 is not accepted.
- Move `docs/WORK_PLAN.md` and `project_brief.md` back to Arc 9.5 correction state.
- Add audit report.

Allowed files:

- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md` optional compact note
- `result_reports/active/574_arc95-full-audit-after-manual-smoke.md`

Forbidden:

- Source code changes
- Tests changes
- Arc 10 worker/progress

Validation:

- `git diff --check`
- `git status --short`

Commit:

- `docs(predict): audit arc95 manual smoke regressions`

---

## Slice B — Table Header Architecture Correction

Goal:

- Remove fake group band or replace it with table-linked group header architecture.

Preferred implementation:

- Add `apps/predict/ui/tables/group_header.py`.
- Implement table-linked header/overlay whose geometry is calculated from the table's actual `QHeaderView`.
- Connect:
  - horizontal scroll value change
  - header section resize
  - model reset
  - column width changes
- Alternatively remove the group band and implement safe non-fake group separators.

Allowed files:

- `apps/predict/ui/workspace.py`
- `apps/predict/ui/tables/group_header.py`
- `apps/predict/ui/tables/case_table_view.py`
- `apps/common/ui/style.py`
- focused tests

Tests:

- group header moves with horizontal scroll
- group header resizes with section resize
- no detached `ColumnGroupBand` unless connected to table header state

Commit:

- `fix(predict): align unified table group header with table scroll`

---

## Slice C — Dropdown Editable Autocomplete / State Machine Correction

Goal:

- Dropdown cells support direct typing, autocomplete, commit, and autofill.
- Dropdown click/edit behavior follows spreadsheet selection/edit contract.

Implementation:

- Make `DropdownDelegate` editor editable.
- Add completer.
- Fix editor lifecycle:
  - first click selects
  - same-cell click/double-click/F2 enters edit
  - printable key starts whole-cell replace and edit
  - arrow/popup affordance can open options
- Ensure typed text commits through model and `InputEditController`.

Allowed files:

- `apps/predict/ui/tables/delegates.py`
- `apps/predict/ui/tables/case_table_view.py`
- `apps/predict/ui/tables/case_table_model.py` only if needed
- focused tests

Tests:

- dropdown editor is editable
- completer exists and uses mapping options
- typed value commits
- typed value triggers autofill path
- one-click selection does not force popup

Commit:

- `fix(predict): support editable dropdown autocomplete`

---

## Slice D — Mapping Option Boundary Correction

Goal:

- Move mapping option lookup out of `PredictWorkspace`.

Implementation:

- Add app-side option provider/adapter:
  - `apps/predict/adapters/dropdown_option_adapter.py`
  - or `apps/predict/controllers/dropdown_option_controller.py`
- It owns:
  - base options from mapping data
  - fallback options for `ref_type` and `exp_type`
  - row-specific cascade options from `InputEditController`
  - missing mapping controlled behavior
- `PredictWorkspace` only wires provider into delegate.

Allowed files:

- `apps/predict/adapters/dropdown_option_adapter.py`
- `apps/predict/controllers/input_edit_controller.py`
- `apps/predict/ui/workspace.py`
- focused tests

Tests:

- no `.mapping_repository.load()` in `workspace.py`
- base options still work
- row-specific cascade still works
- missing mapping controlled state still works

Commit:

- `refactor(predict): move dropdown option lookup behind adapter boundary`

---

## Slice E — Train/Predict Header Ownership Correction

Goal:

- Remove duplicated status/header in `app_train` while preserving standalone `app_predict`.

Implementation options:

Option 1, preferred:

- Split `PredictWorkspace` into:
  - reusable body/surface
  - standalone wrapper with title/status
- `PredictShell` uses full wrapper.
- `TrainShell` embeds body/surface.

Option 2, acceptable:

- Add explicit constructor options:
  - `show_title`
  - `show_status_strip`
  - maybe `show_bottom_status`
- `PredictShell` uses defaults.
- `TrainShell` embeds with title/status disabled.

Allowed files:

- `apps/predict/ui/workspace.py`
- `apps/predict/ui/shell.py`
- `apps/train/ui/shell.py`
- focused tests

Tests:

- `PredictShell` retains standalone title/status
- `TrainShell` Predict tab has no duplicate top model/mapping/preprocess status
- Predict tab still reuses PredictWorkspace or its approved reusable surface

Commit:

- `fix(train): remove duplicate embedded predict status header`

---

## Slice F — Trainer Table Surface MVC Correction

Goal:

- Remove `QTableWidget` from Trainer visual panels.

Implementation:

- Replace `QTableWidget` with `QTableView + QAbstractTableModel`.
- Or replace tables with non-table cards if they are not intended to be interactive tables.
- Update tests to assert no `QTableWidget`.

Allowed files:

- `apps/train/ui/train_model_panel.py`
- `apps/train/ui/data_mapping_panel.py`
- optional new `apps/train/ui/models/*.py`
- `tests/test_apps_train_shell.py`

Tests:

- no `QTableWidget` import/use in `apps/train/ui`
- model row/column data tests
- disabled execution controls remain disabled
- no training/mapping execution imports

Commit:

- `refactor(train): replace widget-owned tables with model views`

---

## Slice G — Workspace Command / State Boundary Cleanup

Goal:

- Reduce QWidget state mutation in `PredictWorkspace`.

Implementation:

- Add `apps/predict/controllers/table_edit_controller.py` or expand `InputEditController`.
- Move:
  - append rows
  - delete rows
  - reset rows
  - affected result clearing
  - undo stack reset coordination
- `PredictWorkspace` remains signal wiring + view refresh.

Allowed files:

- `apps/predict/controllers/table_edit_controller.py`
- `apps/predict/ui/workspace.py`
- `apps/predict/ui/tables/case_table_view.py`
- focused tests

Tests:

- controller row lifecycle
- workspace no direct `case_store.append_empty_rows/remove_rows` except through controller
- reset clears undo stack

Commit:

- `refactor(predict): move case row commands behind controller`

---

## Slice H — Test Adequacy / Final Closeout

Goal:

- Ensure tests fail for the manual smoke regressions if they reappear.
- Update docs/report and move to Arc 10 only after manual smoke passes.

Tests required:

- group header scroll/resize
- editable dropdown autocomplete
- dropdown typed commit + autofill
- app_train duplicate status absent
- no `QTableWidget`
- no direct mapping repository load in workspace
- undo stack cleared on reset
- final smoke construction

Docs:

- New closeout report after actual correction.
- `project_brief.md` and `docs/WORK_PLAN.md` move to Arc 10 only after user manual smoke confirmation.

Commit:

- `docs(predict): close arc95 manual smoke correction`

Push:

- Push only after all correction slices pass and user agrees if following current main hotfix policy.

---

## 6. Recommended Execution Order

1. Slice A — Audit state reset.
2. Slice B — Table header correction.
3. Slice C — Dropdown editable/autocomplete correction.
4. Slice D — Mapping option boundary correction.
5. Slice E — Train/Predict header ownership correction.
6. Slice F — Trainer table surface MVC correction.
7. Slice G — Workspace command/state boundary cleanup.
8. Slice H — Tests/final closeout.

Reasoning:

- Slice B and C address the most obvious manual smoke failures.
- Slice D prevents the dropdown fix from deepening UI/data coupling.
- Slice E addresses `app_train` user-visible duplication.
- Slice F removes an explicit architecture violation.
- Slice G improves maintainability before Arc 10 worker/progress.
- Slice H prevents another false closeout.

---

## 7. Files Requiring Correction

### Must modify

- `apps/predict/ui/workspace.py`
- `apps/predict/ui/tables/delegates.py`
- `apps/predict/ui/tables/case_table_view.py`
- `apps/train/ui/shell.py`
- `apps/train/ui/train_model_panel.py`
- `apps/train/ui/data_mapping_panel.py`
- `tests/test_apps_predict_workspace_unified_table.py`
- `tests/test_apps_predict_mapping_backed_dropdown.py`
- `tests/test_apps_predict_spreadsheet_ux.py`
- `tests/test_apps_train_shell.py`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- new active correction/audit report

### Likely new files

- `apps/predict/ui/tables/group_header.py`
- `apps/predict/adapters/dropdown_option_adapter.py`
- `apps/predict/controllers/table_edit_controller.py`
- `apps/train/ui/models/training_summary_model.py`
- `apps/train/ui/models/mapping_status_model.py`
- new focused test files if existing files become too large

### Should not modify unless separately scoped

- `core/ml/*`
- `core/mapping/*` schema/contract
- `core/predictor_schema/columns.py`
- calculators
- model artifacts
- mapping JSON schema

---

## 8. Acceptance Criteria for Corrected Arc 9.5

Arc 9.5 can be closed only when all of the following are true:

1. `app_predict`
   - unified table group headers track actual columns during horizontal scroll and resize, or fake group header is removed.
   - dropdown cells accept typed values and provide autocomplete.
   - typed dropdown values commit and trigger existing autofill flow.
   - spreadsheet selection/edit state machine behaves per contract.

2. `app_train`
   - Predict tab does not duplicate top header/status.
   - Trainer visual panels do not use `QTableWidget`.
   - Trainer execution remains deferred.

3. Architecture
   - UI widgets do not parse raw mapping JSON.
   - Table model does not call mapping/prediction/training/calculator logic.
   - Table view/delegate do not call mapping repository/prediction/training/calculator logic.
   - Workspace direct state mutation is reduced or explicitly reported if deferred.

4. Tests
   - automated tests catch the exact manual smoke regressions.
   - tests do not assert forbidden widgets.
   - final report no longer overstates manual acceptance.

5. Docs
   - `573` is superseded by manual-smoke correction report.
   - Arc 10 is not current until corrected Arc 9.5 is manually accepted.

---

## 9. Suggested One-line Status for User / Project Brief

Arc 9.5 final closeout was rejected by manual smoke. Source audit confirms the failures are structural: detached group header overlay, non-editable dropdown editor, duplicated Train/Predict status ownership, UI-level mapping lookup, and forbidden QTableWidget usage in Trainer visual panels. Arc 10 should remain on hold until the Arc 9.5 manual-smoke correction slices pass.
