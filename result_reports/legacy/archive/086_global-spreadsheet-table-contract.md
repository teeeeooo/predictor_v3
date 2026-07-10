# 086 — Global Spreadsheet-like Table UI Contract

## Goal

Promote the project-wide PyQt table UI rules — previously split between
the lite AGENTS.md guardrail, the architecture doc §3.3, and the V2
trial-and-error material in `docs/archive/skills_v2_patterns.md` — into
a single active contract that every table surface in the repo must
follow. Wire the new contract into AGENTS.md, AGENT_TASK_ROUTER.md,
the architecture doc, and the calculator-specific horizontal table
design doc so future table UI tasks reach it through every entrypoint.

This task is documentation-only. No `ui/**` code, no calculator code,
no adapter code, no test code is modified.

## Scope

- New active doc: `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`.
- Hooks: `AGENTS.md` UI guardrail line, `AGENT_TASK_ROUTER.md` Shared
  UI Guardrails + UI route, `docs/architecture/project_architecture.md`
  §3.3, `ACTIVE_DOCUMENTS.md` entry.
- Calculator design doc narrowed:
  `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
  now references the global contract and limits itself to
  calculator-specific shape + unit boundary + migration order.
- Result report: this file.

## Non-goals

- No `ui/**` implementation.
- No `QTableWidget` example, even as illustration. The active example
  pattern is always the contract's `QTableView` + `QAbstractTableModel`
  + `QStyledItemDelegate` form.
- No calculator engine, region config, ML feature schema, or
  calculator result schema change.
- No xfail change, no ISO16358-2 HSPF mismatch audit, no calculator
  logic edit, no adapter / unit conversion code change, no ML /
  inverse-search code change.
- No edit to `docs/archive/skills_v2_patterns.md`. The archive stays
  source / history; the active contract is the new file.

## Verification

- `python3 -B -m py_compile $(find . -name "*.py" -not -path
  "./.git/*")` → exit 0 (every tracked / untracked `.py` file compiled
  successfully).
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → `3 passed`. Schema boundary guard unaffected by docs-only changes.
- `python3 -B -m pytest -q` → `407 passed, 34 xfailed`. Identical to
  the post-085 baseline; no test count or xfail change.

## Task Results

### Task 1 — Global spreadsheet table contract

Path: `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` (new file, new
`docs/ui/` folder).

Core rules captured (single owner here, not duplicated elsewhere):

- Required UX baseline: cell selection, `Ctrl+C` TSV copy, `Ctrl+V`
  TSV paste, `Delete` / `Backspace` clear, `Ctrl+Z` undo,
  `Tab` / `Shift+Tab` / `Enter` / `Shift+Enter` navigation, invalid
  numeric cell visual marking, background-color conventions inherited
  from `docs/architecture/project_architecture.md` §3.3.
- Required implementation pattern: `QTableView` mandatory; subclass
  `QAbstractTableModel`; `QStyledItemDelegate` for editor / dropdown /
  custom paint; `QTableWidget` and `setCellWidget` forbidden for any
  new code; per-cell unit choosers forbidden (units live on header /
  table title only).
- Editor lifecycle: 1-click open via `QTimer.singleShot(0,
  editor.showPopup)`; `time.sleep` for UI timing forbidden;
  `editorEvent` must swallow the click that opens the editor; handler
  names must stay stable.
- Path isolation: cell edit, paste (`on_paste_complete`-style), and
  cascade / autofill are three different paths and must not be
  conflated. Paste does not run through the cell-change handler.
- Copy / paste contract: TSV only; non-rectangular selection
  forbidden; non-TSV clipboard payload rejected; paste size mismatch
  rules (top-left anchored fill, single-value repeat-to-selection,
  multi-cell no auto-repeat).
- Clear behavior: `Delete` / `Backspace` clears every editable cell
  in the selection; read-only cells skipped; one undo group per
  clear; master-dropdown clear cascades through the cascade path.
- Undo / redo: per-table undo stack, single group per user action;
  `Ctrl+Z` reverses; stack resets on data-context change; cross-table
  undo out of scope.
- Navigation: Tab / Shift+Tab horizontal with row wrap; Enter /
  Shift+Enter vertical with column wrap; Esc breaks focus out.
- Numeric validation: validator on delegate / model; invalid values
  stored as-is and marked; calculator action paths fail fast via a
  validator helper; painters only render the indicator.
- `blockSignals` discipline: `try/finally` mandatory; bare pair is a
  defect; signal-blocked window must stay short.
- Helper / test harness checklist (§13): 12-item list covering
  pattern compliance, paste path isolation, copy/paste TSV, clear /
  undo behavior, navigation, invalid-cell display, `blockSignals`,
  no cross-layer imports, and `offscreen` Qt platform for fixtures.

Items promoted from archive (`docs/archive/skills_v2_patterns.md`)
into the active contract:

- 1-click dropdown via `QTimer.singleShot` + `editorEvent` swallow.
- Ban on `time.sleep` for UI event timing.
- Paste path must be separated from the cell-change path
  (`on_paste_complete`-style).
- Dropdown handler-name stability (V2 `AttributeError` in paste /
  autofill paths after handler renames).
- `blockSignals` `try/finally` requirement; cascade ordering: data
  lookup → signal-blocked write → UI state update.
- Master dropdown is the sole owner of auto-column lock/unlock state.
- Project-wide `QTableWidget → QTableView + QAbstractTableModel`
  migration; new tables stay on the new pattern.

The new doc explicitly marks `docs/archive/skills_v2_patterns.md` as
source / history only and states the active contract is canonical
when the two disagree.

### Task 2 — AGENTS / router / architecture hooks

Files modified:

- `AGENTS.md` — UI table line now ends with a sentence requiring that
  table UI creation or modification check
  `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`. Existing guardrails
  (`QTableView` + `QAbstractTableModel` + `QStyledItemDelegate`,
  `blockSignals` try/finally) are unchanged.
- `AGENT_TASK_ROUTER.md` — Shared UI Guardrails block adds a bullet
  pointing to the new contract; UI route (§8) adds the contract under
  conditional reads and to step 2 of the procedure. Existing
  `QTableWidget` / `setCellWidget` / `blockSignals` rules are
  unchanged; no rule was weakened or removed.
- `docs/architecture/project_architecture.md` §3.3 — opening bullet
  designates the new contract as the single owner of spreadsheet
  behavior details (copy/paste TSV, multi-cell paste, Delete clear,
  Ctrl+Z undo, Tab/Enter navigation, numeric validation, paste path
  isolation, 1-click editor lifecycle). The remaining bullets
  (View Pattern, Component Injection, State Rendering color
  conventions, Event Safety, 1-click editor UX summary, Paste path
  isolation summary, Handler naming stability, Deprecated V2 example
  note, Calculator Boundary) are kept verbatim.
- `ACTIVE_DOCUMENTS.md` — new inventory row for the contract under
  "Core Project Docs".

No existing architecture guardrail was deleted. The hooks layer on
top of the existing rules so the new contract is reached from every
entrypoint a future table UI task starts at.

### Task 3 — Calculator design doc narrowing

File modified:
`docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`.

Changes:

- Added a top-of-doc **Scope note** that explicitly states this design
  doc is calculator-specific (AHRI / EN14825 column / row shape, ML W
  ↔ calculator-native unit boundary, migration order). Spreadsheet
  behavior is owned by
  `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` and must not be duplicated
  here.
- Confirmed Decisions §"Table input UI" now opens with a bullet
  pointing at the global contract and removes the duplicated
  `QTableWidget`/`setCellWidget`/`blockSignals` re-statement (the
  contract already locks those globally). The `QTableView` +
  `QAbstractTableModel` mandate and the per-cell-unit ban remain in
  place because they are calculator-shape decisions, not generic
  spreadsheet behavior.
- All AHRI / EN14825 table shape tables (columns, rows, unit labels),
  the unit boundary table, the migration order (Slice A → E), and the
  next implementation prompt are kept unchanged.

## Test Results

- `python3 -B -m py_compile $(find . -name "*.py" -not -path
  "./.git/*")` → exit 0. No Python file was modified; the compile is
  a sanity check.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → `3 passed`.
- `python3 -B -m pytest -q` → `407 passed, 34 xfailed` (same as the
  post-085 baseline).

## Changed Files

- `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` — new file. Global PyQt
  table UI contract.
- `AGENTS.md` — UI guardrail line references the new contract.
- `AGENT_TASK_ROUTER.md` — Shared UI Guardrails references the
  contract; §8 UI route reads it as a conditional doc and step 2
  requires the contract checklist on table UI work.
- `docs/architecture/project_architecture.md` — §3.3 opening bullet
  designates the contract as single owner for spreadsheet behavior.
- `ACTIVE_DOCUMENTS.md` — new inventory row for the contract.
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
  — scope note + Confirmed Decisions reference; duplicated rules
  removed; calculator-specific content preserved.
- `result_reports/active/086_global-spreadsheet-table-contract.md`
  — this report.

## Known Failures / Risks

- The contract describes target behavior; existing `ui/**` code has
  not been audited for full compliance in this task. The audit lives
  in the future AHRI SEER2 table-input slice (and subsequent slices)
  and uses the §13 checklist as its gate.
- `docs/archive/skills_v2_patterns.md` is explicitly noted as
  history. Future agents must not treat it as active rules; the new
  contract overrides on conflict. AGENTS.md / router still allow
  reading the archive only when historical context is needed.
- Background-color conventions still live in the architecture doc
  §3.3 (`#FFFFFF` / `#F2F2F2` / `#E6F3E6`). The contract does not
  re-declare them; future palette changes should land in the
  architecture doc, and the contract references that section.

## Next Suggested Action

1. Start the AHRI SEER2 horizontal table-input UI slice (per
   `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
   Slice A) and use the contract §13 checklist as the slice gate.
2. As each subsequent table slice (AHRI HSPF2, EN14825 SCOP, EN14825
   SEER, train UI) lands, audit the slice against the contract and
   capture any deviation in the slice's result report rather than in
   the contract.

## Scope Compliance

- No `ui/**` code modified.
- No calculator engine, region config, adapter, or test code modified.
- No expected / golden value, fixture, or xfail list changed.
- `docs/archive/skills_v2_patterns.md` not modified; it is now
  explicitly demoted to source / history role.
- AGENTS.md / AGENT_TASK_ROUTER.md / architecture doc edits are
  additive references; no existing guardrail or rule was deleted or
  weakened (`QTableView` / `QAbstractTableModel` /
  `QStyledItemDelegate` mandate, `QTableWidget` ban, `setCellWidget`
  ban, `blockSignals` try/finally, 1-click `QTimer.singleShot`,
  paste path isolation, handler naming stability, calculator
  boundary, deprecated V2 example note are all intact).
- The calculator design doc keeps its AHRI / EN14825 table shape and
  unit boundary content; only duplicate spreadsheet rules were
  removed and replaced with a contract reference.

## Commit / Push

- Docs commit: a single commit covering
  `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` (new), the AGENTS / router
  / architecture hooks, the ACTIVE_DOCUMENTS row, and the calculator
  design doc narrowing.
- Report commit: this report as a separate commit (`report: ...`
  style).
- Both commits pushed to `origin/work/iso-separation-plan`.
