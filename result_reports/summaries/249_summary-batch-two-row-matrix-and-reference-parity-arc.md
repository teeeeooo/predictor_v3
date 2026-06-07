# 249 Summary - Batch Two-Row Matrix And Reference Parity Arc

## Covered Reports

Archived by this summary:

- `237_batch-two-row-matrix-layout-preflight.md`
- `238_batch-matrix-model-spec-helpers.md`
- `239_per-cell-role-controller-compatibility.md`
- `240_tk-two-row-matrix-table-skeleton.md`
- `241_fix-tk-two-row-matrix-skeleton-guards.md`
- `242_hong_kong_cspf_matrix_migration.md`
- `243_fix-hong-kong-cspf-restore-autocalc-ordering.md`
- `244_reference-parity-and-standardization-gate.md`
- `245_audit-batchmatrixtable-repair-vs-rebuild.md`
- `246_repair-batchmatrixtable-interaction-parity.md`
- `247_copy-all-and-csv-export-parity.md`
- `248_audit-main-notebook-vs-batch-lifecycle.md`

Reports intentionally kept active: none. The next technical action
(result/detail/export common contract check) can use this summary,
`docs/WORK_PLAN.md`, and the archived source reports if deeper evidence is needed.

## Arc Purpose

- Complete the batch two-row matrix foundation from preflight through migration,
  interaction parity repair, export parity, and lifecycle boundary audit.
- Establish a reusable common table foundation path (`BatchMatrixSpec` +
  `BatchMatrixTable` + `TkTableController`) for future profile expansion.
- Apply the reference parity / standardization gate to avoid repeating already-solved
  behavior bugs.

## Starting State

- Hong Kong CSPF batch was a flat row-per-case `BatchCaseTable` with
  `BatchCalculationController`.
- The 236 window/dialog/batch viewport arc had closed dialog sizing, state
  persistence, and viewport wheel behavior, but the batch table itself was still
  row-per-case.
- The next batch work was a unified two-row matrix layout preflight (237).

## Completed Work

### Foundation slices (237–240)
- 237: Accepted two-row matrix layout with constraints (blank read-only cells,
  no merge, no repeated Case value, physical grid parity).
- 238: Added headless `BatchMatrixSpec` and `MatrixCellDescriptor` with per-cell
  input/result key mapping.
- 239: Added per-cell `cell_role(position)` hook to `TkTableController` while
  preserving existing column-role fallback.
- 240: Built `BatchMatrixTable` Tk surface with two-row per logical case,
  `TkTableController` reuse, and `BatchTableViewport` containment.

### Migration and guards (241–243)
- 241: Fixed header grid overlap in `BatchMatrixTable._build_headers()` and
  corrected snapshot/restore test logic.
- 242: Migrated Hong Kong CSPF batch dialog to `BatchMatrixTable` via
  `HongKongCspfMatrixController` adapter; preserved row-per-case fallback.
- 243: Verified `HongKongCspfBatchSection` callback-restore ordering was already
  correct (no code change needed).

### Reference parity and process gate (244)
- 244: Added a broad reference parity / standardization gate to
  `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`,
  `RESULT_REPORT_WORKFLOW.md`, and `UI_SURFACE_WORKFLOW.md`.
- Trigger: 242 migration reproduced paste tiling, repeated undo, and restore
  flicker issues that had already been solved in the existing row-per-case surface.

### Interaction parity repair (245–246)
- 245: Audited repair vs rebuild for `BatchMatrixTable`; recommended repair
  (add same-shape restore path) over partial rewrite or rebuild.
- 245 initially and incorrectly judged paste tiling as not a common helper gap.
- 246 corrected that judgment and implemented:
  - `editable_paste_targets_by_role()` MxN repeat-fill via modulo tiling.
  - `BatchMatrixTable.restore_snapshot()` same-shape in-place update to preserve
    widget continuity.

### Export parity (247)
- 247: Added `BatchMatrixTable.table_export_data()` and `copy_all()` using
  existing `table_clipboard` and `table_csv_export` helpers.
- Added Copy All and Export CSV buttons to `HongKongCspfBatchSection`.

### Lifecycle boundary audit (248)
- 248: Confirmed main notebook/tab path is partially corrected legacy with
  nested notebook, profile switch, and dynamic refit scheduler.
- Confirmed batch dialog/table path is newer stable path with hidden-first sizing,
  internal viewport, and common table foundation.
- Concluded `BatchMatrixTable` 422 LOC should not trigger a base class now;
  instead, adopt a containment rule (no new responsibilities without helper
  extraction).

## Important Decisions

- Blank read-only cells, no merge, no repeated Case value: accepted as the
  two-row matrix invariant.
- `BatchMatrixSpec` + per-cell `cell_role(position)` + `TkTableController` is the
  standard integration path for matrix tables.
- Hong Kong CSPF batch matrix migration is complete; row-per-case code is
  preserved as importable fallback.
- `BatchMatrixTable` repair was chosen over rebuild; the public surface contract
  is stable.
- MxN paste repeat-fill is common helper behavior, not surface-specific.
- Same-shape restore should preserve widget continuity (proven by `BatchCaseTable`).
- Copy/export formatting lives in dedicated helpers (`table_clipboard`,
  `table_csv_export`); the surface only provides a thin `table_export_data()`
  shape contract.
- Batch path is newer stable path; main notebook path is partially corrected
  legacy. No retroactive base class extraction now.
- `BatchMatrixTable` LOC containment rule: next responsibility addition must
  trigger helper extraction, not file growth.

## Windows / Manual Smoke Results

- 246 Windows smoke: MxN paste works correctly, flicker is gone, undo works
  without clicking another cell.
- 247 Windows smoke: copy-all / CSV export behavior confirmed; no remaining
  manual smoke blocker for this arc.

## Superseded / Corrected Judgments

- 245 audit incorrectly concluded "paste tiling is not a common helper gap."
  This was superseded by 246, which identified `editable_paste_targets_by_role()`
  else path as the actual root cause and fixed it with modulo tiling.

## Accepted Limitations

- `BatchMatrixTable` is at 422 LOC (soft limit 400). Further additions must go
  through helper extraction.
- Headless tests skip Tk focus/selection continuity verification.
- Main notebook/tab path remains partially corrected legacy; full migration to
  the newer stable path is a separate future design slice.

## Remaining Next Actions

1. **Result/detail/export common contract check**
   - Check common result/detail/export contracts before HSPF detail, EN14825,
     AHRI, and KS expansion.
2. **Main table migration candidate check**
   - Assess how existing table surfaces can converge on the common table
     foundation and define a safe migration slice.
3. **ui_tk folder cleanup**
   - Review compatibility wrappers, root table file sprawl, owner locations,
     and duplicate helpers after window/table foundations stabilize.
4. **HSPF detail/bin extension**
5. **EN14825 / AHRI 210/240 / KS profile expansion**

## Project Memory Seed Sync Judgment

- Add `249_summary-batch-two-row-matrix-and-reference-parity-arc.md` to the
  Source Summaries list in `project_memory_seed.md`.
- Two durable entries are candidates for the seed:
  - batch two-row matrix path completed and Hong Kong CSPF migration stabilized.
  - main notebook legacy vs batch newer stable path / no extraction now /
    BatchMatrixTable LOC containment rule.
- Existing seed entries for window geometry and common table foundation remain
  valid and are not superseded.
