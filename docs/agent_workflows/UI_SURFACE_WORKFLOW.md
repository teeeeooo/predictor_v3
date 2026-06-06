# UI Surface Workflow

## Role

This document owns detailed workflow gates for UI surface work. Keep
`AGENT_TASK_ROUTER.md` as the short route map; put table, window/dialog, profile
surface, smoke, and validation details here.

## Start Gate

Before implementation, classify the UI change:

- table-shaped surface;
- window, dialog, Toplevel, viewport, or content-hugging shell;
- dynamic profile/page/screen surface;
- input/result/detail/export surface;
- visual-only polish;
- schema/profile/calculator boundary impact.

Read only the owner documents for the matching class. If the change touches
multiple classes, decide the primary owner first and avoid combining unrelated
UI arcs.

## Owner Documents

- UI/UX root: `docs/ui_ux/00_UI_UX_SYSTEM.md`
- Toolkit policy: `docs/ui_ux/01_TOOLKIT_SELECTION_POLICY.md`
- Layout tokens and screen caps: `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- Table interaction contract: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- Result/input/error surface policy:
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- Window/dialog/viewport/dynamic lifecycle policy:
  `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
- Toolkit adapters:
  - `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
  - `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
  - future adapters when present

## Table Surface Gate

When creating or changing a table-shaped UI:

- confirm `03_SPREADSHEET_TABLE_UX_CONTRACT.md` parity checklist;
- confirm the matching toolkit adapter or record an adapter gap;
- do not treat an Entry/Label grid as a table surface by appearance alone;
- record pass/fail evidence for table parity in the report validation;
- if a reference implementation is not reused, record why and add a
  controller/helper-level parity test plan;
- if Windows/manual smoke first finds a core interaction bug, record it as a
  validation gap and add an automated guard candidate.

## Window / Dialog / Dynamic Surface Gate

When creating or changing a window, dialog, Toplevel, viewport, content-hugging
behavior, dynamic profile/page surface, or nested surface lifecycle:

- confirm `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`;
- for new windows/dialogs, prefer hidden-first build -> settle -> snapshot
  measure -> geometry apply -> show;
- for visible profile/page switches, prefer stable containers or valid cached
  surfaces over repeated visible destroy/create;
- do not rely first on fixed sizes, repeated withdraw/deiconify,
  `update()`/`update_idletasks()` flooding, or local settle-cycle patches;
- keep scheduling, measurement, shell geometry, and view composition boundaries
  separate when the owner already exists.

## Result / Input / Export Surface Gate

When UI changes affect input matrices, result summaries, detail/bin surfaces,
status/error handling, copy, or export:

- confirm `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`;
- keep domain result schemas separate from UI table/export schemas;
- prefer existing copy/export helpers and report gaps before adding new export
  paths.

## Boundary Gate

If the UI task also changes calculator input/output, profile selection, schema,
region config, ML features, or public result keys:

- stop and run architecture/boundary triage before implementation;
- do not mix UI convenience changes with core/domain/config/schema changes;
- use `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` for boundary
  decisions.

## Validation

Use focused validation by owner:

- controller/helper tests for table interaction semantics;
- fake/scheduler/provider tests for window/refit/measurement semantics;
- focused UI import or smoke tests for changed surfaces;
- Windows/manual smoke only for platform behavior that cannot be reliably
  automated.

Do not rerun broad focused tests just because they were used in an earlier
slice. Rerun them only when the changed helper/controller/provider path is
actually touched again.
