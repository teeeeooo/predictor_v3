# 230D — UI/UX Portable-Document Neutralization First Slice

## Goal

Apply the 230C audit by making the first `docs/ui_ux/` portable-document
neutralization slice. The goal was not to remove concrete examples, but to keep
portable principle bodies from reading as project-, screen-, or framework-bound.

## Scope Confirmation

- `230C` identified `04`, `05`, and `07` as the first neutralization targets.
- Adapter documents were intentionally excluded because toolkit-specific names
  are expected in adapter owners.
- No code, tests, behavior policy changes, design records, or report lifecycle
  moves were included.

## Modified Documents

- `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
- `docs/ui_ux/README.md`
- `ACTIVE_DOCUMENTS.md`
- `docs/WORK_PLAN.md`
- `project_log.md`
- `result_reports/active/230d_ui-ux-portable-document-neutralization.md`

## 04 Neutralization Summary

- Reframed the document as a portable visual design architecture owner for
  engineering/data-work applications.
- Replaced project/toolkit-specific scope wording with interface-framework
  neutral wording.
- Preserved neutral-first chrome, semantic roles, table-first interaction,
  typography, spacing, focus, result/status surface, and adoption-order rules.
- Moved concrete PyQt/Tkinter/current-codebase wording into adoption/evidence
  notes so example names remain evidence, not scope boundaries.

## 05 Neutralization Summary

- Reframed the document as a portable repeated-input matrix and result-surface
  owner.
- Generalized calculator / Predictor / Trainer / ML wording into single-case
  calculation, prediction, training/model-operation, batch, and future
  structured input/result surfaces.
- Kept the matrix rule strong: repeated structured input belongs in one
  matrix-like surface, and core/domain logic must not depend on UI matrix
  orientation.
- Preserved validation policy distinctions between auto-calculation batch
  surfaces and prediction/training batch surfaces.
- Kept ISO / Predictor / Trainer examples in an examples section as evidence,
  not scope boundaries.

## 07 Neutralization Summary

- Kept the window geometry and viewport policy behavior unchanged.
- Reframed scope as GUI, web, and external interface shells rather than a list
  of concrete implementations.
- Converted implementation-specific wording into adapter/implementation notes.
- Preserved nested/dynamic refit, placement, scroll, multi-monitor, saved
  geometry, and manual resize rules.

## ACTIVE_DOCUMENTS Sync

- Updated `04`, `05`, and `07` role/outbound wording to describe portable
  UI/UX owner documents.
- Left adapter rows toolkit-specific because adapter docs are implementation
  owners for named frameworks.
- Did not change design-record or architecture inventories.

## README Addition

Added `docs/ui_ux/README.md` as a navigation/adoption index:

- `00_UI_UX_SYSTEM.md` remains the UI/UX root SSOT.
- `01` through `07` are portable principle/policy documents.
- `adapters/` contains framework-specific implementation adapters.
- `_source/` contains historical or evidence sources.
- Concrete project/library/screen/standard names may appear as examples,
  evidence, or adoption notes, not principle scope boundaries.

## WORK_PLAN / Log

- Updated `docs/WORK_PLAN.md` to mark the neutralization slice complete.
- Set the next action to result report lifecycle cleanup because active reports
  exceed the lifecycle follow-up threshold.
- Added a short `project_log.md` note under the existing architecture/UI
  neutralization entry instead of creating a duplicate long entry.

## Excluded

- No adapter document neutralization.
- No UI behavior, code, test, or architecture boundary implementation changes.
- No `docs/designs` changes.
- No report lifecycle/archive movement in this task.

## Validation

- `git diff --check`: pass.
- `python3 -B tools/check_code_structure.py`: pass with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git status --short`: expected documentation/report changes only.

Not run:

- `pytest`: documentation neutralization only.
- GUI smoke: no UI code or behavior change.

## Next Action

Result report lifecycle cleanup.
