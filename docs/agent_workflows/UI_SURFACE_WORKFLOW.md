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

- UI/UX local index: `docs/ui_ux/README.md`
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

## Preflight Structure Guard

Before editing UI surface code:

- check the target owner file size (`wc -l`) when adding a new UI
  responsibility or helper-like behavior;
- check sibling surfaces before adding local lifecycle, mapping, formatting,
  sizing, style, copy/export, or validation logic that is likely to repeat;
- treat soft LOC limits, including 400 LOC warnings, as preflight triggers,
  not automatic hard failures or automatic extraction requirements;
- if the owner file is near or over a soft limit, first decide whether the new
  responsibility is a distinct helper/adapter concern, likely to repeat, or
  likely to mix owner boundaries;
- extract helpers/adapters when responsibility boundaries are clear; do not
  split code only to satisfy a line-count number;
- for structure-impacting UI work, `python3 -B tools/check_code_structure.py`
  can be used as a preflight guard, not only as a commit-time validator.

When the UI task independently requires a compact result record, preserve a
nontrivial reuse/commonization decision there. Ordinary UI source work remains
warning-first and does not require a record merely for changing source.

## Post-implementation Soft Warning Triage

After creating or substantially changing a UI surface, adapter, helper,
controller, or view file, do not move directly to the next feature/code slice if
`check_code_structure.py` reports a soft LOC warning for that changed/new file.
Record a short responsibility triage first:

- current responsibilities in the file;
- responsibilities that still belong inside the current owner;
- candidate responsibilities for helper/adapter/controller/view split;
- next action: accepted for this slice with reason, split audit before the next
  code slice, split implementation before continuing, or blocked.

A soft warning is not an automatic hard failure and does not require mechanical
line-count reduction. Small hotfixes or unchanged legacy warnings may be
accepted with reason. If the next task would add more responsibility to the same
warning file, complete the split audit or split implementation first.

## Table Surface Gate

When creating or changing a table-shaped UI:

- confirm `03_SPREADSHEET_TABLE_UX_CONTRACT.md` parity checklist;
- confirm the matching toolkit adapter or record an adapter gap;
- if an existing surface already implements the same or similar user-visible
  behavior, check it as source-of-truth evidence before implementing a new
  helper/adapter;
- broad reference parity gate: before creating a new table-shaped surface,
  confirm whether an existing stable implementation already covers the same
  interaction, lifecycle, or cleanup concerns, and record why it was or was not
  reused;
- table scroll, wheel routing, paste/copy, selection, export, and viewport
  containment require user-behavior parity, not only structural similarity;
- prefer the existing owner/helper/adapter when it fits; if not reused, record
  the incompatibility or reuse-blocking reason before implementation;
- do not treat an Entry/Label grid as a table surface by appearance alone;
- preserve table-parity evidence in focused tests; add it to a compact record
  only when the task matches a normal record trigger;
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
- calculator profile tabs must route visible-content lifecycle assembly through
  `apps/calculator/ui/lifecycle/`; direct measurement/shell/scheduler construction
  in production `tabs/*.py` is a structure-gate error.

## Result / Input / Export Surface Gate

When UI changes affect input matrices, result summaries, detail/bin surfaces,
status/error handling, copy, or export:

- confirm `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`;
- for stateful input dialogs or batch surfaces, confirm close/reopen state
  ownership; closing the shell must not reset rows/values unless an explicit
  reset/clear action exists;
- keep dialog shell lifecycle, table/input snapshot behavior, and
  parent/controller state ownership separate;
- keep domain result schemas separate from UI table/export schemas;
- prefer existing copy/export helpers and report gaps before adding new export
  paths.

If two or more profile/result/detail/export surfaces repeat the same coercion,
mapping, summary, status, or lifecycle policy, pause for a bounded owner
decision. Keep profile-specific field maps, labels, precision, and schema
contracts local unless the repeated policy itself has a clear common owner.

## Boundary Gate

If the UI task also changes calculator input/output, profile selection, schema,
region config, ML features, or public result keys:

- stop and run architecture/boundary triage before implementation;
- do not mix UI convenience changes with core/domain/config/schema changes;
- use `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` for boundary
  decisions.

## Manual Smoke-loop Fast Lane

Use this fast lane only when the user explicitly requests smoke-loop mode or
asks for an immediate micro-fix based on manual UI smoke. It applies to
same-surface Tkinter/PyQt display, focus, scroll, selection, shortcut, spacing,
or interaction corrections.

- Limit the loop to source and focused test changes. Do not use it for
  calculator core, golden/fixture/config/schema, ML/Predictor, public API or
  diagnostics, or work that needs broader design.
- Reuse already confirmed policy context. If more policy context is necessary,
  read only the short relevant owner section.
- Do not update current-state plans, project logs, or memory during the loop.
  At a stable checkpoint, update a manual-smoke guide, current-state owner, or
  memory owner only when its owned state actually changed.
- Ordinary smoke-loop corrections need no result record. Create a compact
  record only for a normal trigger such as a repeated, non-obvious,
  platform/manual-only, cross-owner bug or one without an automated regression
  guard.
- Do not run full pytest. Validate in tiers: changed-surface owner tests first,
  impacted boundary tests only when shared behavior changed, then requested
  import, `py_compile`, or targeted smoke guards.
- Keep onscreen or Computer Use checks bounded: run focused guards first when
  practical, use one state read and the minimum keyboard/click action, and if a
  source bug appears, update the focused guard before one bounded rerun.
- When the user declares the loop stable, close the checkpoint with the
  terminal/final validation note; only perform owner-state or compact-record
  updates when the conditions above apply.

## Validation

Use focused validation by owner:

- controller/helper tests for table interaction semantics;
- fake/scheduler/provider tests for window/refit/measurement semantics;
- focused UI import or smoke tests for changed surfaces;
- Windows/manual smoke only for platform behavior that cannot be reliably
  automated.
- if UI source structure changed, run the focused structure guard for the
  changed surface and owner;
- for visual-only or manual-smoke result reflection, do not repeat focused UI
  tests or the structure guard unless source changed again.

For GUI / Computer Use smoke, keep the expensive accessibility-tree reads last
and bounded:

1. Lock behavior first with focused pytest, fake/controller tests, or a
   programmatic Qt check where practical.
2. Run onscreen / Computer Use smoke only after source and tests are stable.
3. Prefer one `get_app_state` plus the minimum keyboard or click action needed
   to prove the platform behavior. Avoid repeated state reads after every action
   unless the action output itself is the acceptance evidence.
4. If smoke reveals a small source bug, add or update the focused automated
   guard first, then rerun one bounded smoke pass after the fix.
5. Note any skipped extra smoke in the terminal/final output instead of
   expanding the UI interaction loop.

Do not rerun broad focused tests just because they were used in an earlier
slice. Rerun them only when the changed helper/controller/provider path is
actually touched again.
