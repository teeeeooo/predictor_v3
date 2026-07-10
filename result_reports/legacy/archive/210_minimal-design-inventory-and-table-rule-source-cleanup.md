# 210 — Minimal Design Inventory and Table Rule-Source Cleanup

## Goal

Apply the minimal cleanup proposed by report 209 before any further BatchCaseTable implementation work: align design-record inventory, stop treating design records as active rule owners, and strengthen table-shaped UI routing/owner docs.

## Scope

Changed only documentation owner/gate files and this report:

- `ACTIVE_DOCUMENTS.md`
- `docs/WORK_PLAN.md`
- `AGENT_TASK_ROUTER.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `result_reports/active/210_minimal-design-inventory-and-table-rule-source-cleanup.md`

No code, tests, architecture docs, archived docs, or design record contents were changed.

## 209 Audit Basis

Report 209 found:

- `docs/designs/*.md`: 18 actual files.
- `ACTIVE_DOCUMENTS.md` Design Records first-column entries: 12.
- Missing Design Records inventory entries: 6.
- `WORK_PLAN.md` used two `docs/designs` records as active owners, which could make future agents treat historical decision records as recurring rule sources.
- Table UX rules already existed in UI/UX owner docs but needed a clearer router/adapter gate.

## ACTIVE_DOCUMENTS Inventory

Added 6 missing design records to the Design Records table:

- `docs/designs/2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md`
- `docs/designs/2026-05-29-tkinter-iso-iseer-2point-single-design.md`
- `docs/designs/2026-05-29-tkinter-saso-t3-profile-design.md`
- `docs/designs/2026-05-30-tkinter-detail-trace-graph-result-surface-design.md`
- `docs/designs/2026-05-30-tkinter-excel-like-table-contract-recovery.md`
- `docs/designs/2026-05-30-tkinter-result-surface-export-boundary.md`

Post-change inventory check:

- Actual `docs/designs/*.md`: 18.
- ACTIVE first-column Design Records entries: 18.
- Missing in ACTIVE: none.
- Listed but not found: none.

## WORK_PLAN Owner Wording

Changed design-record owner wording into active owner + decision evidence wording:

- Result/export rules now point to `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`; the 2026-05-30 export boundary design is evidence.
- Excel-like interaction rules now point to `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` and `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`; the 2026-05-30 contract recovery design is evidence.
- SASO T3 design wording changed from owner to reference.

Next-action order was left intact.

## Router Gate

Updated the UI route in `AGENT_TASK_ROUTER.md` so table-shaped UI work must:

- Check `03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Check the relevant toolkit adapter, PyQt or Tkinter.
- Treat a grid that merely looks like a table as insufficient.
- Check `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` for surface-specific validation/error policy.

The router does not duplicate detailed table UX rules; it points to owner docs.

## UI/UX Owner Docs

`03_SPREADSHEET_TABLE_UX_CONTRACT.md` now explicitly distinguishes:

- table-shaped UI as a trigger, and
- compliant table surface as requiring interaction behavior.

`05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` now separates:

- table interaction contract ownership, and
- surface-specific validation policy.

It also records the intended difference between calculator batch row-local handling and ML predict/train batch validation.

`TKINTER_TABLE_ADAPTER.md` now has a compact new-table checklist:

- prefer `MetricInputTable` + `ExcelLikeTableController` when shape fits;
- otherwise use an equivalent common Tk adapter;
- standalone `Entry`/`Label` grids are not compliant table UX;
- verify TSV copy/paste, clear, undo, navigation, replace-on-type, and read-only roles;
- report unimplemented behavior as a gap/NG item.

## Non-Changes

- Did not modify `docs/designs/*.md`.
- Did not archive or move design records.
- Did not modify `docs/archive/**`.
- Did not modify `docs/architecture/**`.
- Did not modify code or tests.
- Did not add `project_log.md`; this cleanup is documented by report 209 and this report.

## Next Action

Run `BatchCaseTable` keep/replace preflight. The key question is whether to adapt the existing batch table to a compliant Tk table adapter or replace it with a reusable surface/controller pattern aligned with `MetricInputTable` and `ExcelLikeTableController`.

## Verification

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing `ui_tk/sections/bin_detail_panel.py` soft LOC warning.
- `git status --short`: expected documentation/report changes only.

Not run:

- `pytest`: document cleanup only; no code/test changes.
- GUI smoke: no UI code changes.
