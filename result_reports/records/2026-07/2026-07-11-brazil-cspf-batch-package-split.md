```yaml
record:
  date: 2026-07-11
  topic: Brazil CSPF batch package split
  tags: calculator, brazil, cspf, batch, package, architecture, tkinter
  memory_review: updated
  memory_reason: Preserve Brazil batch package ownership and public import compatibility for future feature work.

change_gate:
  new_source: split
  hotspot_delta: split-required
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Split the completed Brazil CSPF batch surface from one mixed schema, row
calculation, Tk section, and dialog wrapper module into a bounded Brazil-only
feature package before merge. The refactor keeps shared batch infrastructure
and all calculation behavior unchanged.

# Contract / Behavior Changed

- The former `brazil_cspf.py` module is now the
  `brazil_cspf/` package with explicit `schema`, `row_adapter`, `section`, and
  `dialog` owners.
- The package `__init__` preserves the existing public import surface for the
  Brazil matrix spec, key constants, row result/handler, section, adapter, and
  dialog symbols.
- Schema/result and row adapter modules do not import Tk; Tk construction and
  dialog lifecycle remain in the section/dialog modules.
- The shared `BatchMatrixCalculationController`, `BatchMatrixTable`,
  `BatchDialogShell`, snapshot handling, copy-all, CSV export, and the Brazil
  application usecase remain the existing owners.
- No core capability, config, golden, single UI, shared batch framework, or
  other profile implementation was changed.

# Evidence And Verification

- Brazil application/UI plus affected shared batch tests passed: `79 passed`
  in 1.92 seconds.
- The final full active suite passed: `1665 passed, 2 xfailed` in 47.78
  seconds.
- Package/import boundary coverage confirms the package export identity, no
  stale single-module file, and no Tk attribute in schema or row adapter.
- `python3 -B tools/check_code_structure.py`, calculator/application/UI
  `py_compile`, and `git diff --check` passed. The structure guard reported
  only the existing ten soft warnings.
- Manual GUI interaction remains skipped because the Computer Use path cannot
  inject events into this Tk application; automated Tk smoke passed.

# Changed Files

- `apps/calculator/ui/batch_dialogs/profiles/brazil_cspf/`
- `tests/test_calculator_brazil_application.py`
- `docs/WORK_PLAN.md`

# Known Risks

The refactor preserves the public import path through package exports, but
future Brazil batch additions should continue to use the four package owners
instead of restoring mixed responsibilities. Main merge, packaging, and
deployment remain outside this correction.
