# 582 Summary - Arc 9.5 Unified Table Manual Smoke Closeout

## Goal

Compress the completed Arc 9.5 visual parity, unified table, manual-smoke
reopen, and second-correction reports into one lifecycle summary so Arc 10 can
start from current owner docs rather than completed active reports.

## Covered Reports

- `result_reports/archive/555_active-report-lifecycle-cleanup-arc9-arc92.md`
- `result_reports/archive/556_arc95-visual-parity-audit-plan.md`
- `result_reports/archive/557_arc95-pyside6-style-adapter.md`
- `result_reports/archive/558_arc95-predict-command-status-surface.md`
- `result_reports/archive/559_arc95-predict-table-parity-slice.md`
- `result_reports/archive/560_arc95-predict-status-integration.md`
- `result_reports/archive/561_arc95-train-shell-visual-parity.md`
- `result_reports/archive/562_arc95-visual-parity-closeout.md`
- `result_reports/archive/563_arc95-reopen-completion-criteria-reset.md`
- `result_reports/archive/564_arc95-unified-case-table-design-contract.md`
- `result_reports/archive/565_arc95-unified-case-column-adapter.md`
- `result_reports/archive/566_arc95-unified-case-table-model.md`
- `result_reports/archive/567_arc95-unified-case-table-workspace-integration.md`
- `result_reports/archive/568_arc95-spreadsheet-ux-completion.md`
- `result_reports/archive/569_arc95-mapping-backed-dropdown-options.md`
- `result_reports/archive/570_arc95-unified-result-status-integration.md`
- `result_reports/archive/571_arc95-predict-visual-parity-correction.md`
- `result_reports/archive/572_arc95-trainer-visual-parity-correction.md`
- `result_reports/archive/573_arc95-final-acceptance-closeout.md`
- `result_reports/archive/574_arc95-full-audit-after-manual-smoke.md`
- `result_reports/archive/575_arc95-table-linked-group-header.md`
- `result_reports/archive/576_arc95-editable-dropdown-autocomplete.md`
- `result_reports/archive/577_arc95-dropdown-option-adapter-boundary.md`
- `result_reports/archive/578_arc95-train-embedded-predict-header.md`
- `result_reports/archive/579_arc95-train-table-model-views.md`
- `result_reports/archive/580_arc95-predict-table-row-controller.md`
- `result_reports/archive/581_arc95-second-correction-closeout.md`

## Consolidated Result

Arc 9.5 is accepted/complete for the current automated and user-confirmed
manual-smoke scope. The first visual-parity closeout delivered useful PySide6
Predict/Train surface foundation, but it was not the final table UX because it
deferred spreadsheet baseline behavior and kept a split input/result surface.

The accepted target is the unified case table:

- one visible row is one prediction case;
- input, auto-fill/calculated, prediction result, and status/warning columns
  are grouped in the same spreadsheet-like table;
- result and status columns are read-only but selectable and copyable;
- internal `case_id` remains hidden;
- split input/result panes are historical foundation, not final Arc 9.5 UX.

Manual smoke later rejected the prior closeout because the surface still had
structural issues: detached group header geometry, non-editable dropdowns,
duplicated Train/Predict header/status ownership, UI-level mapping option
lookup, forbidden Trainer `QTableWidget` usage, and row lifecycle/undo reset
gaps. The second correction resolved those findings with focused automated
coverage, and the user has now supplied manual-smoke acceptance for the
corrected Arc 9.5 surface.

## Durable Decisions

- The B-option local visual reference at
  `docs/designs/assets/predict_ref_img.png` is the Arc 9.5 unified case-table
  reference.
- The table-linked group header belongs to the Predict table View boundary and
  derives geometry from the real `QTableView` header.
- Dropdown editors are editable and autocomplete-capable; typed values commit
  through the existing table model/controller path.
- Base dropdown option lookup belongs behind
  `apps/predict/adapters/dropdown_option_adapter.py`; row-specific cascade
  options remain with the input edit controller.
- `TrainShell` embeds `PredictWorkspace` with duplicate top title/status hidden;
  standalone `app_predict.py` keeps the full Predict title/status surface.
- Trainer visual/status tables use model/view surfaces, not `QTableWidget`.
- Predict row lifecycle mutations are behind `TableEditController`; reset
  clears table-local undo history.

## Verification Evidence

The correction closeout recorded focused coverage for the manual-smoke failure
classes:

- unified table and group-header behavior;
- mapping-backed dropdown options and editable autocomplete;
- spreadsheet UX behavior and read-only mutation prevention;
- unified result/status rendering;
- Train shell embedded Predict construction;
- Trainer model/view table surfaces.

Slice 0 also refreshed `docs/code_map/CODEBASE_REFERENCE_MAP.md` because the
map was stale against current HEAD before Arc 10 start.

## Known Risks / Open Items

- Real-model prediction success smoke remains blocked in this checkout because
  `model/model.pkl` is absent.
- Arc 10 worker/progress/cancel is now the active implementation arc; it must
  preserve ML algorithm, mapping schema, calculator behavior, and unified table
  UX contracts.
- Arc 11 Trainer execution remains deferred and must not be started as part of
  Arc 10.

## Project Memory Seed Sync Judgment

The memory seed is updated with this summary as a new source summary and one
compact durable decision covering Arc 9.5 acceptance and Arc 10 readiness. No
individual active-report inventory is copied into memory.
