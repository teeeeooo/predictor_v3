# 477 Batch Matrix Controller Audit

## Goal

Decide whether repeated matrix recalculation summaries/loops should share a
controller without forcing case-table and matrix-table workflows together.

## Evidence

- Hong Kong CSPF, ISO/ISEER 2-point, and SASO T3 each duplicate the same frozen
  three-count summary and the same loop over `BatchMatrixTable.cases`.
- Each loop calls a profile handler, writes `result.values` through
  `set_result`, and counts `OK`, `ERROR`, or pending/blank state identically.
- `BatchCalculationController` already owns equivalent policy for
  `BatchCaseTable`, but its input/result methods are deliberately different:
  `input_rows` / `set_row_results` versus `cases` / `set_result`.
- Focused matrix profile suites: 23 tests passed.

## Decision

**Accept a common matrix controller as a later bounded implementation slice.**
It should reuse the existing public `BatchCalculationSummary` value object and
introduce a matrix-specific controller/protocol around `cases` and
`set_result`.

Do not merge case-table and matrix-table controllers into one conditional or
duck-typed mega-controller. Their physical-row model, result write method, and
table contracts are meaningfully different. Sharing the summary type is useful;
sharing one recalculate implementation across incompatible table shapes is not.

## Suggested Implementation Boundary

- Allow: `apps/calculator/ui/batch/controller.py`, a matrix table protocol,
  three profile controller replacements, focused matrix tests, report/map.
- Preserve: all handlers, status strings, result values, row states, table
  shapes, snapshot behavior, and auto-calc scheduling.
- Forbid: case-table migration, handler commonization, schema/result changes,
  and generic adapter flags selecting table type.

## Changed Files

- `result_reports/active/477_batch-matrix-controller-audit.md`

## Architecture Judgment

A sibling matrix controller keeps orchestration in the controller layer and
profile calculations in handlers, improving MVC/SoC and extension for another
matrix profile. A single polymorphic controller would save few lines while
obscuring the two table contracts, so it is rejected as overengineering.

## Known Risks

- Status-line formatting is repeated separately in profile sections and is not
  part of the accepted controller boundary.
- Implementation is not authorized by this audit commit.
- Active report lifecycle cleanup remains excluded.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- common case controller: lines 1-56; reason: compare existing controller and
  summary ownership.
- three matrix profiles: controller/handler/status symbol ranges only; reason:
  compare loop and table contracts without reading complete calculations.
- matrix table: public cases/set_result symbols from search evidence; owner was
  already clear, so no broad read.
- three focused matrix tests: selected behavior names; reason: validate current
  parity evidence.
- broad read: none.
- repeated read: none.

## Commit / Push

Audit-only commit; published with the complete arc.

## Next Suggested Action

Audit repeated batch dialog open/focus/snapshot handles.
