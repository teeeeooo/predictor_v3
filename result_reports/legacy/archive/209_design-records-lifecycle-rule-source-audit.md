# 209 — Design Records Lifecycle and Rule-Source Audit

## Goal

Audit `docs/designs`, `ACTIVE_DOCUMENTS.md`, UI/UX owner docs, architecture, and `WORK_PLAN` to separate historical design records from active repeated rule sources. This is report-only: no design docs, owner docs, architecture docs, router rules, or code were changed.

## Scope

- Checked actual `docs/designs/*.md` inventory.
- Compared that inventory with `ACTIVE_DOCUMENTS.md` Design Records.
- Classified each design record by lifecycle role.
- Proposed rule-source ownership for table UX and related UI/boundary rules.
- Left cleanup implementation to a later task.

## Inventory Check

| Item | Count |
| --- | ---: |
| Actual `docs/designs/*.md` files | 18 |
| `ACTIVE_DOCUMENTS.md` Design Records first-column entries | 12 |
| Listed files not found on disk | 0 |
| Actual files missing from ACTIVE_DOCUMENTS Design Records | 6 |

Missing from `ACTIVE_DOCUMENTS.md` Design Records:

| Missing file |
| --- |
| `docs/designs/2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md` |
| `docs/designs/2026-05-29-tkinter-iso-iseer-2point-single-design.md` |
| `docs/designs/2026-05-29-tkinter-saso-t3-profile-design.md` |
| `docs/designs/2026-05-30-tkinter-detail-trace-graph-result-surface-design.md` |
| `docs/designs/2026-05-30-tkinter-excel-like-table-contract-recovery.md` |
| `docs/designs/2026-05-30-tkinter-result-surface-export-boundary.md` |

## Lifecycle Classification

| Design record | Classification | Basis |
| --- | --- | --- |
| `TEMPLATE_DESIGN_GATE.md` | active template/reference | Template for future design gates, not a product rule source. |
| `2026-05-06-iso16358-2-hspf-core-boundary.md` | active decision reference / watchlist | Core boundary decision remains useful, but repeated boundary rules should live in architecture/ISO owner docs. |
| `2026-05-08-asnzs-hspf-excel-compat-boundary.md` | historical/archive candidate | AS/NZS compatibility boundary is evidence for future work, not an active repeated rule owner. |
| `2026-05-10-iso16358-2-hspf-h8-routing-resolver-design.md` | active decision reference | H-8 routing/resolver design remains relevant for ISO HSPF work; ACTIVE already notes outbound owner docs. |
| `2026-05-17-iso-remaining-work-completion.md` | historical/archive candidate | Completion boundary record; not an ongoing rule source. |
| `2026-05-17-calculator-horizontal-table-input-ui.md` | absorbed by owner docs | Table/input UI rules are now owned by `docs/ui_ux/03...`, `05...`, and adapters. |
| `2026-05-17-calculator-result-envelope-ml-adapter.md` | active decision reference / architecture absorption candidate | Calculator-result vs ML-adapter boundary should be owned by architecture/WORK_PLAN, with this as evidence. |
| `2026-05-22-calculator-action-model-alignment.md` | absorbed by owner docs | Auto-calc vs explicit action policy is now covered by UI/UX system and input/result surface rules. |
| `2026-05-22-calculator-ui-module-boundary.md` | absorbed by architecture | Module boundary belongs in architecture and AGENTS code-quality gates. |
| `2026-05-22-lightweight-calculator-ui-feasibility.md` | historical decision reference | Tkinter lightweight direction and packaging tradeoff record; not repeated UI contract owner. |
| `2026-05-23-tkinter-calculator-final-ux-contract.md` | absorbed by owner docs | Matrix input, auto-calc, and result-surface rules are now in `05_INPUT_MATRIX...` and Tkinter adapter docs. |
| `2026-05-24-pyqt-calculator-reference-feature-migration-contract.md` | active decision reference | Still useful for PyQt reference parity and retirement gate decisions. |
| `2026-05-29-tkinter-iso-iseer-2point-result-visual-refinement.md` | inventory correction needed / absorbed | Result visual decision appears implemented; owner should be UI/UX/result surface docs, not designs. |
| `2026-05-29-tkinter-iso-iseer-2point-single-design.md` | inventory correction needed / historical | Mode/profile decision is implemented; keep as decision record, not active rule source. |
| `2026-05-29-tkinter-saso-t3-profile-design.md` | inventory correction needed / active decision reference | SASO T3 follow-ups may still reference it; should be registered in ACTIVE. |
| `2026-05-30-tkinter-detail-trace-graph-result-surface-design.md` | inventory correction needed / active decision reference | Detail/trace/graph result arc still affects follow-ups; owner rules should migrate to UI/UX/schema docs. |
| `2026-05-30-tkinter-excel-like-table-contract-recovery.md` | inventory correction needed / rule-source migration needed | Repeated Excel-like contract must live in UI/UX table contract and Tkinter adapter, not only this design record. |
| `2026-05-30-tkinter-result-surface-export-boundary.md` | inventory correction needed / rule-source migration needed | `WORK_PLAN` currently calls this an owner; export boundary should be migrated into UI/UX/architecture owner docs. |

## Recommended Rule-Source Map

| Rule/source area | Recommended owner | Role |
| --- | --- | --- |
| Task routing / when to read docs / required gates | `AGENT_TASK_ROUTER.md` | Gate and routing owner only; should link to rule owners rather than restating product rules. |
| Agent entrypoint and non-negotiable high-level boundaries | `AGENTS.md` | Lite entrypoint; short common principles only. |
| Module boundaries, resolver ownership, schema separation, dependency constraints | `docs/architecture/project_architecture.md` | Architecture boundary owner. |
| UI/UX root map and common product-flow/dialog rules | `docs/ui_ux/00_UI_UX_SYSTEM.md` | UI/UX SSOT root and map. |
| Toolkit-neutral Excel-like table interaction | `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` | Owner for selection, copy/paste, delete, undo, navigation, keyboard workflow. |
| Repeated input/result shape, batch result shape, validation/result philosophy | `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` | Owner for whether a surface should be a matrix/table/result summary before toolkit implementation. |
| Tkinter-specific implementation adapter | `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md` | Owner for Entry-grid/Treeview implementation expectations and Tkinter-specific verification checklist. |
| Current priority and sequencing | `docs/WORK_PLAN.md` | Scheduling only; should not designate `docs/designs` as owner when active owner docs exist. |
| Design records | `docs/designs/*.md` | Decision evidence/history/design-gate records; not repeated rule-source owners. |

## Current Collision / Drift Risks

- `ACTIVE_DOCUMENTS.md` Design Records inventory is missing 6 actual design files.
- `docs/WORK_PLAN.md` currently labels `docs/designs/2026-05-30-tkinter-result-surface-export-boundary.md` and `docs/designs/2026-05-30-tkinter-excel-like-table-contract-recovery.md` as owners. That can make agents read historical design records as active rules.
- Table UX rules already exist in `03_SPREADSHEET_TABLE_UX_CONTRACT.md` and `TKINTER_TABLE_ADAPTER.md`, but recent batch work still treated a bordered Entry/Label grid as close enough. The missing gate is not a new design record; it is a routing/adapter verification checklist.
- Design records that have been absorbed by UI/UX or architecture docs should remain as evidence but should not be the only source of a recurring rule.

## Table UX Rule Placement Proposal

| Needed rule | Proposed owner | Notes |
| --- | --- | --- |
| “A surface that merely looks like a table is not a compliant table surface.” | `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` acceptance/anti-patterns, with pointer from `03` | `05` owns surface-shaping; `03` owns behavior once table-shaped. |
| Excel-like baseline for every table-shaped UI | `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` | Already present; future cleanup should make task-router acceptance point to it more explicitly. |
| Tkinter table implementation requirements | `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md` | Add a concrete “new table surface checklist”: controller/selection/copy/paste/delete/undo/navigation or explicit NG gap. |
| Calculator batch invalid-row policy | `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` plus architecture schema boundary where needed | UX should say row-local status for repeated-case calculator batch; architecture should keep result/status schema out of core. |
| ML/Predict batch invalid-row policy | `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` for UX, ML/architecture docs for schema | Similar table UX, different execution/error semantics. |
| Test strategy for table-shaped UI | Tkinter adapter and router UI gate | Focused tests should cover TSV paste/copy, Delete/Backspace clear, Tab/Enter navigation, undo, and read-only result/status cells. |
| Items that must not remain report-only | Owner docs above | Recurring rules should be migrated to owner docs, then reports/designs become evidence. |

## Recommended Next Cleanup

Next action: run a minimal design inventory / rule-source cleanup task before another batch UI correction.

Suggested order:

1. Update `ACTIVE_DOCUMENTS.md` Design Records inventory for the 6 missing design records.
2. Change `WORK_PLAN.md` references that call design records “owner” into “decision/reference” and point recurring rules to UI/UX owner docs.
3. Add a short Tkinter table-surface verification checklist to `TKINTER_TABLE_ADAPTER.md`.
4. Add a router UI gate note that any table-shaped UI task must verify the Excel-like baseline or report the gap as NG.
5. Then run a separate `BatchCaseTable` keep/replace preflight and batch table UX correction.

## Non-Changes

- Did not edit `docs/designs/*.md`.
- Did not edit `ACTIVE_DOCUMENTS.md`.
- Did not edit `docs/ui_ux/**`.
- Did not edit `docs/architecture/**`.
- Did not edit `AGENTS.md` or `AGENT_TASK_ROUTER.md`.
- Did not edit code or tests.
- Did not update `docs/WORK_PLAN.md`; the needed correction is larger than a one-line next-action tweak and should be handled as a separate cleanup.

## Verification

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing `ui_tk/sections/bin_detail_panel.py` soft LOC warning.
- `git status --short`: report-only change before commit.

Not run:

- `pytest`: document audit/report only; no code changes.
- GUI smoke: no UI code changes.
