# 571 - Arc 9.5 Predict Visual Parity Correction

## Goal

Correct the Predict workspace visual hierarchy toward the local B-option
unified case table reference.

## Scope

- Re-check `docs/designs/assets/predict_ref_img.png` as the current local
  visual reference.
- Tune shared semantic tokens and PySide6 style adapter values for lower-chrome
  table/status presentation.
- Align the Predict workspace title, column group band, table hierarchy, and
  status badge intensity with the unified case table reference.
- Add focused style adapter coverage for table group label styling.
- Update Work Plan next action to Slice 10.

## Non-goals

- No ML, calculator, mapping schema, or preprocessing behavior changes.
- No table business logic changes.
- No new search/filter/export behavior.
- No worker/progress implementation.
- No push before Slice 11.

## Boundary Decision

Owner boundary: visual tokens, shared PySide6 style adapter, Predict status
widgets, and Predict workspace presentation.

The unified table model/schema and prediction session contracts remain intact;
this slice only changes display styling and workspace composition.

change_gate:
  new_source: none
  hotspot_delta: visual-style-only
  code_map_check: skipped
  ui_literal_exemption: visual-copy-within-existing-surface
  reuse_commonization: reused-existing-token-and-style-owners
  report_exemption: none
  read_ledger: included

Change gate notes:

- `hotspot_delta`: touched shared visual token/style owners plus the Predict
  workspace/status widgets; no core or mapping owners changed.
- `code_map_check`: skipped because prompt allowed-file scope excludes code-map
  regeneration and no new source module was introduced.
- `ui_literal_exemption`: title/group labels are existing Predict UI copy in
  the visual parity surface.

Read Ledger:

- `docs/designs/assets/predict_ref_img.png`: visual inspection, reason:
  confirm current B-option reference.
- `ui_common/visual_tokens.py`: lines 1-165, reason: semantic color/font token
  tuning.
- `apps/common/ui/style.py`: lines 1-194, reason: shared table, badge, and
  group-label styling.
- `apps/predict/ui/workspace.py`: lines 60-230, reason: title, group band,
  and table visual hierarchy.
- `apps/predict/ui/status_widgets.py`: lines 1-58, reason: status badge
  intensity correction.
- `apps/predict/ui/command_bar.py`: lines 1-45, reason: confirm command
  grouping without adding behavior.
- `tests/test_pyside6_style_adapter.py`: lines 1-42, reason: focused style
  coverage.
- broad read: none.
- repeated read: reference screenshot and generated offscreen screenshots for
  visual comparison.

## Visual Evidence

- Reference image: `docs/designs/assets/predict_ref_img.png`.
- Current shell screenshot before final badge correction:
  `/tmp/arc95_slice9_predict_shell_after.png`.
- Current shell screenshot after correction:
  `/tmp/arc95_slice9_predict_shell_after_badges.png`.

Observed corrections:

- Workspace title now matches the B-option reference title.
- Status badges use low-intensity dot/text presentation instead of filled
  alert-style chips.
- Unified table group labels use subtle input/auto/result/status tints.
- Table fonts, header padding, selected color, and result/status tints are
  denser and less saturated.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py apps/common/**/*.py ui_common/*.py app_predict.py`: passed.
- `python3 -B -m pytest tests -k "predict and (visual or table or workspace or style or token)"`: passed, 35 selected.
- `python3 -B -c "from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); from apps.predict.ui.workspace import PredictWorkspace; w=PredictWorkspace(); assert w is not None"`: passed.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft warnings plus code-map freshness reminder; no changed/new
  source file warning.
- `git diff --check`: passed.
- `git status --short`: checked; Slice 9 style/workspace/status widget/test,
  Work Plan, and this report were dirty before commit.

Structure Warnings:

- none from `tools/check_code_structure.py` for changed/new source files.

## Known Risks

- Offscreen screenshot uses empty production initial rows because demo data
  loading is not part of this slice.
- Command bar icon/search/filter controls from the reference remain visual
  follow-up candidates unless separately scoped as functional UI behavior.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 10 - Trainer Visual Asset Parity Correction.
