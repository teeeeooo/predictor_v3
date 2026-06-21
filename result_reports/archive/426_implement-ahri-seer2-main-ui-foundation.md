# 426 Implement AHRI SEER2 Main UI Foundation

## Goal

Add the first AHRI 210/240 calculator UI slice: top-level AHRI access and the
SEER2 main metric surface.

## Scope

- Register an `AHRI 210/240` calculator tab with a `SEER2` metric path.
- Add the HP/AC Type option, exact five-point matrix, read-only condition and
  EER2 cells, auto-calculation, and compact SEER2 result.
- Route UI input through a thin adapter to the existing calculator dispatcher.
- Add focused adapter, table-role, auto-calc, result, and shell-wiring tests.

## Non-goals

- No SEER2 batch or HSPF2 UI.
- No core, config, schema, fixture, golden, or EN14825 changes.
- No new table controller, color palette, public result contract, or broad
  workflow refactor.

## Changed Files

- `apps/calculator/ui/ahri/__init__.py`
- `apps/calculator/ui/ahri/seer2_adapter.py`
- `apps/calculator/ui/sections/ahri_seer2_section.py`
- `apps/calculator/ui/tabs/ahri210240_tab.py`
- `apps/calculator/ui/calculator_app.py`
- `tests/test_apps_calculator_ui_ahri_seer2.py`
- `tools/check_code_structure.py`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/426_implement-ahri-seer2-main-ui-foundation.md`

## Task Results

- The calculator shell exposes `AHRI 210/240`, whose only implemented metric
  tab is `SEER2`; no HSPF2 placeholder or behavior was added.
- Type defaults to HP and maps HP/AC unchanged through the UI adapter.
- The point order is `A_Full`, `B_Full`, `B_Low`, `E_Int`, `F_Low` with
  one-decimal Celsius condition labels.
- Capacity and Power use the shared editable matrix; Condition/Temp and EER2
  are read-only cells. Incomplete input leaves EER2 and SEER2 blank.
- Complete valid input auto-calculates EER2 and calls the existing dispatched
  SEER2 calculator for the compact final result.

## Table Parity Evidence

- Reused `MetricInputTable` with `TkTableController`; no standalone grid or
  new controller was introduced.
- The shared controller retains rectangular selection, TSV copy/paste,
  single-column fill, grouped undo, clear, navigation, replace-on-type, and
  read-only mutation prevention behavior.
- Focused coverage checks the new surface's exact axes and editable/read-only
  role mapping. Existing common-controller tests remain the parity owner.
- Content-hugging measurement and shared scroll shell are reused; manual
  platform sizing smoke remains a lifecycle-closeout concern, not a blocker
  for this foundation slice.

## Verification

- Focused pytest: `python3 -B -m pytest tests/test_apps_calculator_ui_ahri_seer2.py`
  — 4 passed.
- Structure guard: `python3 -B tools/check_code_structure.py`
  — passed with only two pre-existing EN14825 soft-LOC warnings after the new
  AHRI package registry entry was added.
- Code map: `python3 -B tools/code_checker/build_reference_map.py --check`,
  followed by regeneration because the new production modules made it stale.
- Cached gate: `python3 -B tools/check_agent_change_gate.py --cached`
- Whitespace: `git diff --check`

## Known Risks

- Final platform-level visual sizing and keyboard smoke is deferred to the
  AHRI lifecycle closeout; the shared components provide the automated
  interaction contract meanwhile.
- The existing calculator determines formula behavior. This slice validates
  UI mapping and presentation, not formula parity or new core semantics.

## Scope Compliance

- New production responsibility is split across navigation, section, and
  adapter modules, each below the repository soft LOC limit.
- HSPF2, batch, core, config, schema, fixture, and golden paths are untouched.
- `project_log.md` was not updated because this implements the already-approved
  design boundary without a new architecture or public-contract decision.

## Change Gate

```yaml
change_gate:
  new_source: split
  hotspot_delta: none
  code_map_check: regenerated
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENTS.md`: lite entrypoint and non-negotiable boundaries supplied in task
  context; reason: work contract and routing.
- `AGENT_TASK_ROUTER.md`: coding, UI, result-report routes; reason: source/UI
  workflow and reporting gates.
- `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`:
  SEER2 main UI, ownership, acceptance, and slice sections; reason: approved
  implementation contract.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`: completion gate, surface
  architecture, and cell states; reason: new table acceptance.
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`: matrix, result, and
  acceptance sections; reason: input/result shape.
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`: allowed widget, baseline,
  and cell-state sections; reason: Tk table implementation.
- Existing Tk calculator shell, EN14825 tab/section, common table, result,
  auto-calc, measurement, and focused test ranges; reason: reference parity.
- `core/calculator_dispatcher.py` and `core/calculator_ahri_seer2.py`: public
  construction and call signatures only; reason: thin adapter boundary.
- `docs/WORK_PLAN.md` and `project_brief.md`: current slice and Arc 2 ranges;
  reason: status synchronization.
- broad read: none
- repeated read: API-targeted excerpts only

## Next Action

AHRI SEER2 batch, as a separate explicitly approved slice.
