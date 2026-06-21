# 469 Remove Legacy Tk Naming Remnants

## Goal

Align live calculator packaging and manual-smoke instructions with the
canonical `app_calculator.py` entrypoint and empty-state policy.

## Scope and Results

- Renamed current Tkinter PyInstaller outputs from `app_calculator_tk*` to
  `app_calculator*` throughout the live packaging guide.
- Kept `app_calculator.py` as the source that delegates to
  `apps.calculator.app:main`.
- Replaced obsolete `ui_tk` import/source wording in the live smoke guide.
- Replaced the single-tab and performance-prefill expectations with the
  current three-tab and empty-performance-input contracts.
- Preserved historical reports, archives, design provenance, test filenames,
  and guard compatibility roots.

## Non-goals

- No entrypoint, launch behavior, calculator code, archive, history, report,
  calculation, schema, fixture, or golden content changed.

## Verification

- Canonical entrypoint suite: 3 tests passed.
- Structure guard passed hard rules with the existing hotspot and code-map
  freshness warnings.
- Code-map check was run and judged `no-change` because this slice changes only
  live prose and output artifact names.
- Diff check passed; cached staged gate recorded at commit closeout.

## Changed Files

- `docs/guides/lightweight_calculator_packaging_check.md`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `result_reports/active/469_remove-legacy-tk-naming-remnants.md`

## Architecture Judgment

The executable boundary remains one thin root wrapper and one package main.
Artifact naming is documentation, not a second runtime entrypoint. Historical
names were deliberately left only where they are evidence rather than live
instructions.

## Known Risks

- Historical feasibility prose and `test_ui_tk_*` test filenames retain their
  original names; neither is a live application import or packaging target.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: no-change
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- both allowed live guides: matched legacy-name and stale-default ranges;
  reason: update only executable instructions and current expectations.
- canonical entrypoint test: complete small file; reason: verify the documented
  delegation boundary.
- repository live-reference search excluding reports/archive/design history;
  reason: distinguish active consumers from evidence.
- broad read: none.
- repeated read: none.

## Commit / Push

This slice is committed independently and pushed with the complete arc.

## Next Suggested Action

Record the completed manual smoke and move the work plan to Arc 2.
