```yaml
record:
  date: 2026-07-11
  topic: Brazil CSPF export section schema correction
  tags: calculator, brazil, cspf, export, clipboard, csv, schema
  memory_review: updated
  memory_reason: Preserve independent Result/Rule/Final schemas for Brazil Copy and CSV output.

change_gate:
  new_source: justified
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Correct the Brazil single-result Copy/CSV contract after the UI polish added a
Rule table with a different schema from the result comparison table. The
previous flat export reused one result header for Result, Rule, and Final rows.

# Contract / Behavior Changed

- Added a Brazil-local `BrazilCspfExportDocument` composed of independent
  `Result`, `Rule`, and `Final` sections.
- Valid Copy, CSV, and `as_text()` now consume the same sectioned document;
  Result rows use the Result header, Rule rows use the Rule header, and Final
  uses the explicit `Final\tOK/NG` section row.
- `table_export_data()` remains a result-table-only compatibility method rather
  than returning a fake mixed schema. Empty/invalid status export keeps the
  existing single Status header/row path.
- The shared CSV/clipboard helpers were not broadened. The existing CSV helper
  assumes one header, so variable-width section serialization is owned by the
  Brazil-local export adapter.
- Screen result/rule tables, detail view, batch output, core result contracts,
  formulas, and golden values are unchanged.

# Evidence And Verification

- Brazil result/export/application/UI tests passed: `13 passed`.
- Affected Brazil core, shared clipboard/CSV/detail, and lifecycle tests passed:
  `138 passed`.
- Final full active suite passed: `1667 passed, 2 xfailed` in 43.51 seconds.
- Sectioned TSV and variable-width CSV rows are fixed by test, including the
  exact Result/Rule/Final order and empty/invalid Status fallback.
- Structure guard, calculator/application/UI `py_compile`, and `git diff --check`
  passed; structure output contained only the existing ten soft warnings.

# Changed Files

- `apps/calculator/ui/sections/brazil_cspf_export.py`
- `apps/calculator/ui/sections/brazil_cspf_result_table.py`
- `apps/calculator/ui/sections/brazil_cspf_section.py`
- Brazil UI export tests and `docs/WORK_PLAN.md`

# Known Risks

The Brazil CSV intentionally contains independently shaped section rows, so
consumers must respect the `[Result]`, `[Rule]`, and `[Final]` labels instead of
assuming one rectangular table. Shared export helpers remain unchanged and
other calculator exports are unaffected. Main merge remains outside this
correction.
