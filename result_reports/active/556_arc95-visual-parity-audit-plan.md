# 556 - Arc 9.5 Visual Parity Audit and Slice Plan

## Goal

Audit the current PySide6 Predict / Train UI against the stored design assets,
Arc 9.2 harvest checklist, active architecture contract, and UI/UX contracts;
then fix the Arc 9.5 implementation slice plan.

## References Checked

- `ACTIVE_DOCUMENTS.md`
- `project_brief.md`
- `docs/WORK_PLAN.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `docs/designs/README.md`
- `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`
- `docs/designs/assets/predict_ref_img.png`
- `docs/designs/assets/train_ref_img.png`
- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `result_reports/summaries/554_summary-arc9-pyside6-schema-legacy-ui-harvest-closeout.md`

## Design Asset Check

Both assets exist and were visually inspected:

- `docs/designs/assets/predict_ref_img.png`: 1672 x 941 PNG; visually shows an
  HVAC V3 Trainer / Train Model style screen.
- `docs/designs/assets/train_ref_img.png`: 1672 x 941 PNG; visually shows an
  HVAC V3 Predictor screen.

The filenames appear swapped relative to the window titles. This arc will keep
the repository paths unchanged and use the visual content as the acceptance
reference by screen type. The target is layout density, hierarchy, grouping,
and interaction parity, not pixel-perfect replication.

## Current Implementation Audit

Checked:

- `app_predict.py`
- `app_train.py`
- `apps/predict/ui/shell.py`
- `apps/predict/ui/workspace.py`
- `apps/predict/ui/tables/`
- `apps/train/ui/shell.py`
- `apps/train/ui/train_model_panel.py`
- `apps/train/ui/data_mapping_panel.py`
- `apps/train/app.py`
- `ui_common/visual_tokens.py`

Current state:

- Predict is a working foundation with split input/result tables, row add /
  delete / reset, synchronous prediction run wiring, case_id-hidden result
  lookup, and row headers as user-facing identity.
- Train shell is a tabbed shell and reuses `PredictWorkspace`, but Train Model
  and Data Mapping tabs are placeholders.
- `ui_common.visual_tokens` already has a useful neutral token base but no
  PySide6 style adapter applies it consistently.
- Current offscreen screenshots confirm the UI is not final visual parity:
  sparse default Qt styling, no top status strip, weak command grouping, no
  badge/card hierarchy, limited table visual distinction, and placeholder Train
  admin panels.

## Gap Classification

### Predict

- Top status / model / mapping / preprocess area: missing.
- Command bar: present as plain buttons, not grouped; paste/copy/export
  placeholders are absent.
- Input/result split workspace: present but visually plain.
- Input / auto / result visual distinction: minimal schema background only;
  no tokenized table styling.
- Table header / row height / column width: basic resize-to-contents only.
- Dropdown affordance / one-click popup: missing.
- Validation / error / warning rendering: mostly missing.
- Bottom status summary: present as one text label, not structured.
- Large-batch usability: split surface exists, but density/status/scroll affordance
  need improvement.

### Train

- Tabbed admin shell: present.
- Predict tab reuse: present.
- Train Model tab visual structure: placeholder only.
- Data Mapping tab visual structure: placeholder only.
- Model/data/mapping status cards: missing.
- Log/status areas: missing.
- Design asset hierarchy: not yet reflected.

## Arc 9.5 Slice Targets

1. Create a PySide6 style adapter around `ui_common.visual_tokens` and add only
   minimal missing semantic roles.
2. Apply Predict top status, command grouping, panel hierarchy, and bottom
   status summary without adding worker/progress/cancel.
3. Improve Predict input/result table visual parity and implement or explicitly
   defer spreadsheet interactions by priority: copy/paste/clear first, then
   dropdown affordance, validation rendering, undo/navigation.
4. Surface mapping, validation, and result statuses through controller/state/UI
   boundaries without moving business logic into table models.
5. Replace Train placeholder panels with visual Train Model and Data Mapping
   admin surfaces while keeping execution actions disabled/placeholder-only.
6. Close the arc with docs updated toward Arc 10.

## Explicit Non-goals

- No legacy `ui/` restoration.
- No PyQt production dependency.
- No root compatibility wrapper recreation.
- No ML algorithm, feature list, target list, preprocessing formula, mapping
  schema, model artifact, calculator formula/config/fixture/golden, or public
  result contract changes.
- No prediction worker/progress/cancel implementation.
- No trainer execution foundation, model training execution, or mapping Excel
  update execution changes.
- No production sample/default/prefill restoration.

## Verification

- Design image existence checked with `file` and `ls`.
- Design images visually inspected.
- Current Predict and Train shells rendered offscreen to temporary screenshots.
- `git diff --check`: to be run before slice closeout.
- `git status --short`: to be run before slice closeout.

## Next

Slice 2 - Visual token adapter and shared PySide6 styling.
