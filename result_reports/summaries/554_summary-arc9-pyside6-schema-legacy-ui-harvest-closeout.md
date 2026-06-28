# Summary 554 - Arc 9 PySide6 Schema, Legacy UI Retirement, and Harvest Closeout

## Goal

Consolidate completed active reports from the Arc 9 / Arc 9.1 / Arc 9.2
Train/Predict recovery sequence so `result_reports/active/` can return to
current blockers and next-decision evidence only.

## Covered Reports

- `537_active-report-lifecycle-cleanup-arc7-arc85.md`
- `538_arc9-pyside6-schema-mapping-gap-audit.md`
- `539_arc9-predict-schema-adapter.md`
- `540_arc9-table-model-schema-recovery.md`
- `541_arc9-mapping-autofill-recovery.md`
- `542_arc9-prediction-adapter-recovery.md`
- `543_arc9-predict-schema-mapping-closeout.md`
- `544_arc91-legacy-ui-inventory.md`
- `545_arc91-legacy-ux-harvest.md`
- `546_arc91-ui-common-visual-token-adoption.md`
- `547_arc91-legacy-ui-retirement.md`
- `548_arc91-legacy-ui-retirement-closeout.md`
- `549_arc92-harvest-location-audit.md`
- `550_arc92-legacy-ui-detail-recovery.md`
- `551_arc92-harvest-doc-move-and-checklist.md`
- `552_arc92-harvest-routing-update.md`
- `553_arc92-legacy-ui-harvest-closeout.md`

## Completed Arc 9 Scope

- PySide6 Predict schema adapter and table models now consume
  `core/predictor_schema` instead of local mock column definitions.
- Mapping/autofill recovery uses `core/mapping` owners with app-side
  repository/controller boundaries; table models do not load mapping JSON or
  own mapping side effects.
- Row-to-ML conversion uses schema `ml_feature` metadata and recovered
  `ref_type` / `exp_type` one-hot behavior.
- Prediction result mapping uses schema `ml_target` metadata and
  `core.ml.features.TARGETS`, preserving controlled partial/error states.
- `app_predict.py`, `app_train.py`, `PredictWorkspace`, and `TrainShell`
  import/open smokes passed during the closeout; real model success smoke
  remains blocked by absent `model/model.pkl`.

## Completed Arc 9.1 Scope

- Retired the legacy Train/Predict `ui/` path and removed legacy PyQt tests.
- Adopted `ui_common.visual_tokens` as the active toolkit-neutral token owner
  for upcoming visual parity work.
- Confirmed active source/docs/tests/scripts no longer depended on the retired
  `ui.*` path or active PyQt literal references, excluding archive/history.
- Regenerated the code map during the legacy UI retirement closeout.

## Completed Arc 9.2 Scope

- Re-read legacy `ui/base_model.py`, `ui/base_view.py`,
  `ui/spreadsheet_table.py`, `ui/predict_window.py`, `ui/train_window.py`, and
  `ui/theme.py` from pre-retirement ref
  `f8adf7075563838dc8217833b46242ad618fc3ae`.
- Moved the project-specific PySide6 visual/table parity harvest from
  `docs/ui_ux/06_PYSIDE6_VISUAL_AND_TABLE_PARITY_HARVEST.md` to
  `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`.
- Kept `docs/ui_ux/` as the portable UI/UX rule set and routed the moved
  harvest through `docs/designs/README.md`, `ACTIVE_DOCUMENTS.md`,
  `docs/WORK_PLAN.md`, `project_brief.md`, and the PySide6 architecture
  contract.
- Expanded the Arc 9.5 acceptance reference with detailed checklist coverage
  for Predict table parity, spreadsheet UX, mapping/autofill, row-to-ML/result
  parity, Predict hierarchy, Train admin inventory, and token adoption.

## Current Active Owner References

- Current next action and blockers: `docs/WORK_PLAN.md`.
- Phase / Arc map: `project_brief.md`.
- PySide6 Train/Predict architecture contract:
  `docs/architecture/pyside6_train_predict_architecture.md`.
- Arc 9.5 design/harvest reference:
  `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`.
- Portable table and input/result contracts:
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` and
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.

## Known Blockers / Deferred Items

- Real model prediction success smoke is still blocked in this checkout because
  `model/model.pkl` is absent.
- Worker/progress/cancel remains deferred to Arc 10 unless a later prompt
  changes the order.
- Trainer admin execution foundation remains deferred to Arc 11.
- PySide6 table adapter parity is still incomplete: TSV copy/paste,
  Delete/Backspace clear, grouped undo, Tab/Enter navigation, click/type
  replace-on-type, dropdown delegate rendering, and validation rendering remain
  table UX parity work.
- The memory seed remains above the maintenance-audit threshold; a dedicated
  seed maintenance audit is still a candidate.

## Archive Decision

All covered reports are completed history or intermediate evidence now covered
by this summary and by active owner documents. No covered report needs to remain
active for the next Arc 9.5 decision.

## Memory Seed Judgment

Register this summary under Source Summaries and add only compact durable
decision entries for:

- Arc 9 package-owner schema/mapping/result recovery;
- Arc 9.1 legacy `ui/` retirement and `ui_common.visual_tokens` ownership;
- Arc 9.2 harvest relocation to `docs/designs/`.

## Next Action

Arc 9.5 - Predict / Train Visual UI Parity from Design Assets.
