# 467 Remove Legacy Calculator Tk Entrypoint

## Goal

Delete the deprecated `app_calculator_tk.py` compatibility shim after migrating
its live guide and test consumers to the canonical calculator entrypoint.

## Scope

- Removed the thin root compatibility file.
- Removed its import/delegation expectations from the focused entrypoint test.
- Migrated the active manual-smoke launch/compile commands and packaging source
  commands to `app_calculator.py`.
- Updated the work plan to make the canonical launch boundary and manual-smoke
  closeout explicit.
- Regenerated the code map after the root entrypoint deletion.

## Non-goals

- No batch, EN14825 background, token cleanup, UI behavior, equation, schema,
  fixture, golden, or lifecycle implementation changed.
- Historical design records and prior reports were not rewritten; their shim
  references remain evidence of the superseded migration state.

## Task Results

- `app_calculator.py` remains the documented root wrapper and delegates to
  `apps.calculator.app:main`.
- Active guide commands no longer invoke the deleted shim.
- The focused test now guards only the canonical package and root entrypoints.
- Packaging artifact names may retain `app_calculator_tk` as output labels; the
  input source is canonical `app_calculator.py`.

## Verification

- Focused canonical entrypoint suite: 3 tests passed.
- Canonical wrapper/package/UI shell modules byte-compiled successfully.
- Structure guard passed hard rules with existing soft warnings. The code map
  was stale after Task B and was regenerated once; diff check passed. The staged
  cached gate is recorded at task closeout.

## Changed Files

- deleted `app_calculator_tk.py`
- `tests/test_apps_calculator_entrypoints.py`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/guides/lightweight_calculator_packaging_check.md`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/467_remove-legacy-calculator-tk-entrypoint.md`

## Known Risks

- Older design records still name the removed shim as historical migration
  evidence; they are not live execution instructions.
- The packaging guide retains historical PyQt/Tkinter comparison prose and
  artifact names. Only its current source path was migrated in this slice.
- Canonical GUI launch remains a final manual smoke item because automated tests
  intentionally avoid entering the Tk main loop.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Structure Warnings: existing calculator UI soft warnings only; no production UI
source was modified in Task C.

Read Ledger:

- root/package calculator entrypoints: full thin files; reason: confirm canonical
  delegation before deletion.
- focused entrypoint tests: complete small file; reason: remove only shim-specific
  expectations.
- active manual-smoke and packaging guides: matched entrypoint command ranges;
  reason: migrate live launch/build consumers.
- `docs/WORK_PLAN.md`: current slice/constraint ranges; reason: remove the shim
  retention decision and set the next action.
- repository reference search excluding archive/report history; reason:
  distinguish live execution consumers from historical design evidence.
- broad read: none.
- repeated read: none.

## Commit / Push

Task C is committed independently. After the three-task final validation, Tasks
A–C are published together in one push.

## Project Memory Delta

The work plan and this report supersede the prior active retention decision.
Historical memory/report wording is preserved rather than rewritten.

## Next Suggested Action

Complete the manual smoke closeout, then begin the first approved legacy UI
token cleanup slice.
