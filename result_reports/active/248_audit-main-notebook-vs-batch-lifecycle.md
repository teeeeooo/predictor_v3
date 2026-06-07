# 248 Audit Main Notebook Legacy vs Batch Dialog/Table Lifecycle Before Extraction

## Goal

Determine whether apparent duplication between main notebook path and batch
dialog/table path is bad duplication that needs extraction, or a healthy
separation between legacy and newer stable policy paths. Identify safe
extraction candidates without premature base classes.

## Scope

- Audit memory seed and summaries for the evolution of window/dialog/table policy.
- Inventory main notebook/tab lifecycle (legacy/partially corrected path).
- Inventory batch dialog/table lifecycle (newer stable path).
- Classify duplication into extraction/migration/hold categories.
- No code changes.

## Memory/Summary Evidence

### Main notebook/tab path evolution
- **Summary 200 (196-a–199-c)**: Closed window geometry polish for the main
  calculator: multi-monitor geometry, first-launch fit, detail open, profile
  switch, 80% height cap, top-safe y.
- **Summary 231/236 (221-c–235)**: Extracted visible content measurement,
  mapped-surface lifecycle, unified profile switch/reselect/detail toggle,
  hidden-first window/dialog policy, batch dialog sizing/state/viewport.
- The main `Iso16358Tab` still carries legacy complexity: nested notebook,
  profile switch frame hide/show, `DynamicContentRefitScheduler` with settle
  cycles, `TkVisibleContentMeasurement` with overflow and scrollbar state.

### Batch dialog/table path evolution
- Created **after** the 229–235 arc (summary 236).
- Uses hidden-first dialog sizing via `HongKongCspfBatchDialog._apply_initial_geometry`.
- Uses internal viewport via `BatchTableViewport` (mouse-wheel containment,
  scrollbar auto-show).
- Uses common table foundation (`TkTableSurface`, `TkTableController`,
  `interaction_core` helpers).
- Close/reopen state persistence via parent section `_batch_snapshot`.
- Batch dialog has **no** nested notebook, no profile switch, no dynamic refit
  scheduler, no visible measurement adapter.

## Main Notebook/Detail Lifecycle Inventory

### Iso16358Tab responsibilities
- Mode/profile switch (`_render_mode`, `_on_mode_changed`)
- Nested notebook for Hong Kong CSPF/HSPF metrics
- ScrollableFrame with canvas/scrollbar
- `TkVisibleContentMeasurement` (preferred size, overflow, scrollbar, nested
  notebook active state)
- `DynamicContentRefitScheduler` (coalesce settle -> measure -> fit)
- `TkContentHuggingShell` registration for geometry apply
- Section lifecycle: hide/show frames, cancel pending calculations
- Mouse-wheel routing through `_on_mousewheel` with containment check

### Classification: partially corrected legacy path
- The refit loop and flicker issues were mitigated but not fully eliminated.
- The nested notebook + profile switch + dynamic measurement + shell geometry
  stack is complex because it evolved through multiple hotfixes.
- It is **not** the reference path for new work.

## Batch Dialog/Table Lifecycle Inventory

### HongKongCspfBatchDialog responsibilities
- `Toplevel` creation, hidden-first sizing, centering
- Simple `HongKongCspfBatchSection` pack
- `WM_DELETE_WINDOW` → snapshot + destroy
- No refit scheduler, no measurement adapter, no nested notebook

### HongKongCspfBatchSection responsibilities
- `BatchMatrixTable` + `TkTableController` + `HongKongCspfMatrixController`
- `DebouncedAutoCalc` for calculation scheduling
- Action row: Add Case, Remove Case, Copy All, Export CSV
- Status label

### BatchMatrixTable responsibilities (422 LOC)
- `TkTableSurface` contract implementation
- Two-row widget grid construction (`_build_headers`, `_build_case_rows`)
- `StringVar` creation and trace binding per logical case
- `_batch_depth` coalescing (`set_positions_batch`, `restore_snapshot`)
- Same-shape in-place restore (246 fix)
- `cell_role(position)` per-cell role resolution
- Thin `table_export_data()` and `copy_all()` (247 addition)
- Viewport sync via `BatchTableViewport`

### Classification: newer stable path
- Uses post-236 hidden-first policy.
- Uses common table foundation (`TkTableSurface`, `TkTableController`).
- Uses dedicated viewport helper (`BatchTableViewport`).
- Lifecycle is intentionally simpler than main tab because context is simpler
  (no profile switch, no nested notebook, no dynamic measurement).

## Duplication Classification

### A. Immediate helper extraction candidates

| Item | Location | Why extract |
|---|---|---|
| TSV/CSV encode | `table_clipboard.py`, `table_csv_export.py` | Already extracted; both batch and main result tables reuse it. |
| `table_export_data` shape generation | `BatchMatrixTable.table_export_data()` (3 lines), result tables | Could become a generic `table_surface_export_data(surface)` helper, but surface contract differences make it thin enough to leave as-is. |

### B. Future main migration reference (batch is newer stable)

| Item | Batch pattern | Main legacy pattern |
|---|---|---|
| Dialog sizing | Hidden-first, content-hugging shell | Direct geometry, manual fit |
| Table viewport | `BatchTableViewport` with wheel routing | ScrollableFrame canvas/scrollbar inline |
| Table interaction | `TkTableController` + `interaction_core` | `ExcelLikeTableController` / per-table controller |
| State persistence | Parent snapshot, explicit restore | Embedded in section state, mixed with UI |
| Close/reopen | Explicit snapshot, not implicit reset | Implicit reset risk in some paths |

**Judgment**: The batch path should **not** be retrofitted to match main legacy.
If anything, main should migrate toward batch patterns where applicable.

### C. Should NOT commonize (shape/lifecycle difference)

| Item | Reason |
|---|---|
| Row-per-case vs two-row matrix | Different semantic models; `BatchMatrixSpec` handles the mapping. |
| `BatchCaseTable` vs `BatchMatrixTable` grid construction | Different column/header logic, different variable ownership (flat rows vs logical cases). |
| Notebook/profile switch vs dialog | Completely different contexts; no shared lifecycle. |
| Main refit scheduler vs batch simple geometry | Main has nested notebooks and dynamic content; batch does not. |
| `MetricInputTable` vs `BatchMatrixTable` | `MetricInputTable` is single-case immediate-calc; `BatchMatrixTable` is multi-case batch with logical/physical row mapping. |

### D. Hold candidates (batch table LOC)

| Item | Current state | Risk of extraction |
|---|---|---|
| BatchMatrixTable 422 LOC | borderline soft limit | Extracting a base class now would create an abstract layer that only has two concrete implementations with different shapes. Wait for a third shape or a main-table migration preflight. |
| Header/width label logic | `_header_label`, `_header_width` | Could move to `BatchMatrixSpec`, but spec is frozen/headless and should not own Tk width concerns. Keep as thin surface method. |
| Entry creation/styling | `_make_entry` | Both `BatchCaseTable` and `BatchMatrixTable` have similar 5-line Entry creation. Extracting would save ~5 LOC per file but add a helper import and obscure the local styling. Not worth it yet. |
| Same-shape restore batching | `restore_snapshot` | The pattern is now proven (246). If a third table surface needs it, then extract a `TableSnapshotRestorer` helper. Two instances is not enough for a generic helper. |

## Extraction Risk Judgment

- **Base class creation risk**: Creating a `BaseBatchTable` or `AbstractTableSurface`
  now would be premature. We have two batch table shapes (flat row-per-case and
  two-row matrix) and one main single-case table (`MetricInputTable`). Their
  semantic models, state ownership, and grid construction differ enough that a
  base class would either be too abstract to be useful or too concrete to fit all
  three.
- **Helper extraction risk**: Small helpers like `_make_entry` or header label
  formatting are safe to extract but provide minimal LOC savings. The real
  complexity in `BatchMatrixTable` is the two-row logical/physical mapping and
  variable lifecycle, not the widget construction boilerplate.
- **Main migration risk**: The main tab (`Iso16358Tab`) has a complex lifecycle
  that was built before the hidden-first/measurement-snapshot policy. Migrating
  it to the batch pattern would be a large, risky refactor. It should be a
  separate design slice, not a side effect of batch cleanup.

## Recommendation

**Do not extract a base class or helper now.**

**Instead, adopt a containment rule:**
- `BatchMatrixTable` is at 422 LOC. The next addition to this file should trigger
  extraction of the new responsibility to a helper, adapter, or the section
  controller. No new responsibilities should be added to `BatchMatrixTable`
  directly until a helper extraction slice is completed.

**Concrete next actions (in order):**
1. **Result/detail/export common contract check** (WORK_PLAN next action #1):
   Check whether result tables, detail tables, and batch tables can share a
   common `table_export_data()` contract or whether each surface type needs its
   own shape. This is a contract question, not an extraction question.
2. **Main table migration preflight** (WORK_PLAN next action #2):
   Assess how `MetricInputTable` and main-tab table surfaces can migrate toward
   the common table foundation (`TkTableSurface`, `TkTableController`). This is
   a design slice, not an implementation slice.
3. **ui_tk folder cleanup** (WORK_PLAN next action #3):
   After the contract check and migration preflight, review whether helpers
   like `table_clipboard`, `table_csv_export`, and `interaction_core` need
   consolidation or whether new helpers like `table_surface_exporter` should be
   introduced.

## Excluded Scope

- No code changes.
- No base class creation.
- No helper extraction.
- No main tab refactoring.
- No tests modified.

## Known Risks

- The 422 LOC soft warning may pressure future developers to add a base class
  prematurely. The containment rule (no new responsibilities without extraction)
  is the safer guard.
- If a third table shape appears before the migration preflight, the extraction
  decision may need to be revisited.

## Project Memory Delta

- Batch dialog/table path is the newer stable path; main notebook/tab path is the
  partially corrected legacy path.
- Apparent duplication between `BatchCaseTable` and `BatchMatrixTable` is
  shape-specific construction, not generic boilerplate. A base class would be
  premature with only two concrete shapes.
- `BatchMatrixTable` LOC containment rule: next responsibility addition triggers
  helper extraction, not file growth.
