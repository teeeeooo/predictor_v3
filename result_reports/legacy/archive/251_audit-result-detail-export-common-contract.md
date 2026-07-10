# 251 Audit Result/Detail/Export Common Contract Before Profile Expansion

## Goal

Inventory current result/detail/export copy and export contracts to determine
what can be reused across HSPF detail/bin, EN14825, AHRI, and KS profile
expansion, and what must remain surface-specific.

## Scope

- Audit existing `table_export_data()`, `table_clipboard`, `table_csv_export`
  usage across result comparison, detail/bin, and batch matrix surfaces.
- Classify contracts into common vs surface-specific.
- Recommend whether profile expansion can proceed with existing helpers.

## Current Contract Inventory

| Surface | Owner | Copy | CSV Export | Header | Output Shape | Helper |
|---|---|---|---|---|---|---|
| Result comparison table | `iso_saso_t3_result_table.py`, `iso_iseer_2point_result_table.py` | TSV (selection) | No | Yes | `column_labels` + `rows` | `table_clipboard` |
| Detail/bin trace table | `bin_trace_table.py` | TSV (all) | No | Yes | `column_labels` + `rows` | `table_clipboard` |
| Detail/bin panel | `bin_detail_panel.py` | TSV (current source) | Yes | Yes | `column_labels` + `rows` | `table_clipboard` + `table_csv_export` |
| Batch matrix table | `batch_matrix_table.py` | TSV (all) | Yes | Yes | physical grid `text_at_position` | `table_clipboard` + `table_csv_export` |
| ResultPanel summary | `result_panel.py` | No | No | N/A | card/summary | N/A |
| Graph/detail panel | `bin_detail_panel.py` (graph) | No | No | N/A | Canvas graph | N/A |

## Common vs Separate Contract Classification

### A. Common table-shaped export contract (already established)

- `table_export_data() -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]`
  is the thin surface contract.
- `table_clipboard.copy_table_to_clipboard(widget, headers, rows)` handles TSV
  clipboard encoding and OS clipboard I/O.
- `table_csv_export.export_table_to_csv(parent, filename, headers, rows)`
  handles file dialog + `csv.writer` output.
- This contract is already shared by result comparison tables, detail/bin tables,
  and batch matrix tables.

### B. Surface-specific contract (should remain separate)

- **ResultPanel summary**: card/summary surface, not table-shaped. Copy/export
  of summary cards is a separate UX question, not a table export question.
- **Graph/detail panel**: Canvas graph, not table-shaped. Graph export (PNG/SVG)
  or HTML export is deferred.
- **Status/error trace**: diagnostic text, not user-facing result table. Should
  not be mixed with result table export.

### C. Profile/domain-specific contract (must stay out of UI export)

- **Calculator result dict**: domain schema. UI export helpers must not import
  calculator core or depend on result dict shape.
- **Bin/schema trace shape**: detail/bin column meaning is domain-specific, but
  the `table_export_data()` surface contract is generic. Domain columns are
  provided by the surface owner, not the export helper.

### D. Deferred/hold

- **xlsx export**: deferred per WORK_PLAN.
- **Graph export/HTML export**: deferred per WORK_PLAN and 249 summary.
- **ResultPanel summary copy/export alignment**: deferred unless manual smoke
  shows it is needed.
- **MetricInputTable full-table copy**: deferred until main table migration
  preflight.

## Expansion Readiness

### HSPF detail/bin extension
- **Ready**: Can reuse existing detail/bin table contract (`table_export_data()`
  + `table_clipboard` + `table_csv_export`).
- HSPF detail/bin columns will be surface-specific, but the export helper path
  is already proven.

### EN/AHRI/KS profile expansion
- **Ready**: Same as HSPF. Detail/bin tables for each profile will define their
  own `column_labels` and `rows`, but the export contract is the same.

### Batch matrix table
- **Ready**: Physical grid export contract is already working. No change needed.
- BatchMatrixTable LOC containment rule means no new responsibilities should be
  added to the surface file.

### Comparison result tables
- **Ready**: TSV copy only is the correct contract. No CSV export needed.

### Main table migration
- **Hold**: `MetricInputTable` does not yet implement `table_export_data()`.
  Full-table copy is deferred until the migration preflight defines the contract.

## MVC/SoC Boundary Judgment

- `table_clipboard` and `table_csv_export` are sufficient helper owners. They
  handle formatting, encoding, and I/O without knowing domain schemas.
- No `table_surface_exporter` wrapper is needed now; the existing two-helper
  pattern is thin enough and proven across 4+ surfaces.
- ResultPanel should not be changed per WORK_PLAN constraint.
- BatchMatrixTable LOC containment is respected: export logic is 3 lines
  (`table_export_data`) + 3 lines (`copy_all`) in the surface, with all
  formatting delegated to helpers.

## Recommendation

**Profile expansion can proceed with existing copy/export contracts.**

No new helper or contract design is needed before HSPF detail/bin or EN/AHRI/KS
profile expansion. The existing `table_export_data()` + `table_clipboard` +
`table_csv_export` pattern is the common contract.

**Next action: HSPF detail/bin extension.**
- The detail/bin table owner for HSPF can follow the same `table_export_data()`
  pattern as existing ISO detail/bin tables.
- Export/copy buttons can reuse the same helper calls.
- No BaseSection or shared result framework is required.

## Excluded Scope

- No code changes.
- No new helper creation.
- No BaseSection or shared result framework.
- No ResultPanel changes.
- No xlsx/graph export.
- No main table migration implementation.

## Known Risks

- If a future surface needs a fundamentally different export shape (e.g. nested
  JSON, multi-sheet xlsx), the current `(headers, rows)` contract will need
  extension. That is out of scope for the current CSV/TSV parity target.
- `table_csv_export` uses `filedialog.asksaveasfilename`; headless test
  environments must mock or skip the dialog portion.

## Project Memory Delta

- The common table-shaped export contract is confirmed: `table_export_data()`
  surface method + `table_clipboard` + `table_csv_export` helpers.
- Profile expansion (HSPF, EN, AHRI, KS) does not require a new export contract
  design slice before implementation.
- Main table migration preflight remains a separate future task.
