# 245 Audit BatchMatrixTable Repair vs Rebuild Decision

## Goal

Before patching BatchMatrixTable interaction parity issues, audit whether the
current skeleton can be repaired with small fixes or whether a partial rewrite
or full rebuild is the safer long-term choice. Apply the 244 reference parity
gate by using BatchCaseTable as the reference implementation.

## Scope

- Inventory BatchCaseTable stabilized behavior as the reference.
- Inventory BatchMatrixTable current gaps.
- Assess whether gaps are local-fixable, require partial rewrite, or justify a
full rebuild.
- No code changes; audit and recommendation only.

## Reference Parity Evidence (BatchCaseTable)

### State Ownership
- `BatchCaseTable` owns a `BatchTableModel` which owns `model.rows` (flat
  list of dicts).
- Table surface owns `self._variables` (flat list of dicts mapping column key
  to `tk.StringVar`).
- Model and surface are separate but synchronized via StringVar trace and
  direct model mutation.

### Same-Shape Restore Behavior
- `restore_snapshot(snapshot)` checks `len(normalized) != len(self.model.rows)`.
- If same shape: does **not** call `_rebuild_table()`. Updates `model.rows`
  entries and `_variables[row][key].set(value)` directly.
- Uses `_batch_depth` coalescing around direct StringVar updates.
- **Critical**: Widgets survive the restore; focus and selection continuity are
  preserved.

### Shape-Changing Restore Behavior
- If different shape: calls `_rebuild_table()` which destroys all widgets,
  rebuilds headers and rows, then calls `interaction_controller.refresh()`.

### Batch Mutation (set_positions_batch)
- Does **not** call `_rebuild_table()`.
- Updates `_variables[row][key].set(value)` directly for editable cells.
- Uses `_batch_depth` coalescing for `_notify_changed()`.

### Add/Remove Row
- Calls `_rebuild_table()` because widget grid shape changes.
- Calls `interaction_controller.refresh()` inside `_rebuild_table()`.

### Controller Relationship
- `_rebuild_table()` ends with `interaction_controller.refresh()` if present.
- Controller's `refresh()` rebuilds `_widget_positions` map and re-binds events.

## BatchMatrixTable Gap Inventory

### 1. restore_snapshot always rebuilds (Local Fix)
- Current: `restore_snapshot()` always calls `_rebuild_table()` regardless of
  shape match.
- Gap: Even same-shape restores destroy and recreate all widgets. This causes
  focus loss, selection loss, and flicker on undo and paste.
- Reference parity: BatchCaseTable preserves widgets on same-shape restore.
- **Category: local fix** — add a same-shape path that updates `self.cases` and
  `self._variables` directly without `_rebuild_table()`.

### 2. _notify_changed lacks _batch_depth coalescing (Local Fix)
- Current: `restore_snapshot()` calls `_notify_changed()` unconditionally after
  `_rebuild_table()`. Same for `set_positions_batch` which does have
  `_batch_depth` but `restore_snapshot` does not.
- Gap: During controller paste/undo, multiple notification paths may fire.
- Reference parity: BatchCaseTable uses `_batch_depth` in both
  `set_positions_batch` and `restore_snapshot`.
- **Category: local fix** — wrap `restore_snapshot` updates with `_batch_depth`
  coalescing like BatchCaseTable does.

### 3. ensure_row_count rebuilds unnecessarily (Local Fix)
- Current: `ensure_row_count()` calls `_rebuild_table()` when rows are added.
- Reference parity: BatchCaseTable does the same thing.
- Gap: When controller paste extends rows, `_rebuild_table()` is triggered
  inside `ensure_row_count()`, then `set_positions_batch` runs. The controller
  does not refresh between these steps, so `_widget_positions` may be stale
  until the next explicit refresh. In BatchCaseTable this works because the
  controller handles the flow through `_apply`. In BatchMatrixTable the same
  pattern exists but the extra rebuild during paste may interact differently
  with per-cell role resolution.
- **Category: local fix or common helper** — ensure the controller's `_apply`
  and `_paste` flow handles the intermediate rebuild correctly. The common
  `TkTableController._paste` already calls `ensure_row_count` then `_apply`,
  and `_rebuild_table` is already designed to refresh the controller. This gap
  is smaller than it appears; it may resolve once restore_snapshot same-shape
  handling is fixed.

### 4. No structural problem (Not a Rebuild Trigger)
- Public surface contract (`TkTableSurface`) is well-defined and migration
  section/handler/controller depend only on this contract.
- The internal state model (`cases` as `list[dict]`, `_variables` as
  `list[dict[str, StringVar]]`) is structurally sound.
- `_build_physical_row` creates real widgets per cell with proper StringVar
  trace, matching BatchCaseTable's `_build_row` pattern.
- Cell role resolution via `cell_role(position)` works correctly.
- **Category: no structural issue**.

## Common Helper / Controller Gap Inventory

### Paste Tiling / Repeat-Fill
- `editable_paste_targets_by_role` in `interaction_core.py` is a common helper
  used by both BatchCaseTable (via BatchTableController) and BatchMatrixTable
  (via TkTableController).
- The single-cell repeat and one-row fill-paste logic are matrix-agnostic.
- **Assessment: not a common helper gap**. If tiling occurs, it is likely a
  surface-level restore/rebuild timing issue, not a paste-target calculation
  issue.

### Repeated Undo / Focus Loss
- `TkTableController._undo_last` calls `restore_snapshot(snapshot)` then
  `self.refresh()`.
- If `restore_snapshot` always rebuilds, focus is lost because widgets are
  destroyed before `refresh()` re-binds them.
- **Assessment: controller-level symptom caused by surface-level behavior**.
  Fixing BatchMatrixTable `restore_snapshot` to preserve widgets on same-shape
  restore will resolve this without controller changes.

### Controller Refresh Timing
- `TkTableController.refresh()` rebuilds `_widget_positions` and re-binds all
  events. This is expensive but correct.
- BatchCaseTable's `BatchTableController` may have lighter refresh semantics.
- **Assessment: not a critical gap**. `refresh()` is called inside
  `_rebuild_table()`, so widget destruction/recreation is followed by correct
  controller re-registration. The problem is the unnecessary destruction, not
  the refresh itself.

## Repair vs Partial Rewrite vs Rebuild Recommendation

**Recommended: A. Repair current skeleton.**

### Reasoning
- The public surface contract (`TkTableSurface`) is stable. Migration section,
  adapter, and handler depend only on this contract.
- The internal state model is sound: `cases` + `_variables` mirrors
  BatchCaseTable's `model.rows` + `_variables` pattern.
- The critical gap is a **single method behavior**: `restore_snapshot` does not
  distinguish same-shape from shape-changing restores.
- BatchCaseTable provides a clear, proven same-shape restore pattern that can
  be adapted to BatchMatrixTable's logical-case structure.
- No class names, public APIs, or migration code need to change.
- A partial rewrite would restructure the same state model without solving a
  different problem.
- A full rebuild would discard a functional contract and migration path for a
  single missing optimization.

### Proposed Repair Scope
1. **Add same-shape restore path to `restore_snapshot`**:
   - If `len(snapshot) == len(self.cases)`: update each case dict and each
     StringVar directly (via `_variables[logical_index][key].set(value)`).
   - Use `_batch_depth` coalescing for `_notify_changed()`.
   - Do **not** call `_rebuild_table()`.
2. **Add shape-changing restore path** (current behavior):
   - If lengths differ: call `_rebuild_table()` as today.
3. **Verify `set_positions_batch` batch coalescing** is consistent with the
   same-shape restore path.

### What Is Not In Scope For The Repair
- No change to `add_case`, `remove_case`, or `ensure_row_count` (they correctly
  rebuild because shape changes).
- No change to `HongKongCspfBatchSection`, `HongKongCspfMatrixController`, or
  `HongKongCspfBatchDialog`.
- No change to `TkTableController`, `interaction_core`, or table roles.
- No change to `_build_physical_row` widget construction.

### Safe Boundaries
- `batch_matrix_table.py` internal state/variable ownership changes are allowed.
- Public contract (`TkTableSurface` methods) must remain unchanged.
- Existing tests and migration tests must continue passing.

## Excluded Scope

- No code changes in this audit slice.
- No test changes.
- No UI implementation changes outside `batch_matrix_table.py`.
- No calculator/core/region/config/fixture changes.
- No copy-all / CSV / xlsx export work.
- No EN/AHRI/KS expansion.

## Known Risks

- Same-shape restore fix assumes StringVar lifetime continuity. If any code
  path holds widget or StringVar references across restore, the fix must account
  for it. BatchCaseTable's proven pattern suggests this is safe.
- The headless test environment cannot verify focus/selection continuity. Windows
  manual smoke is required after the repair slice.

## Project Memory Delta

- 244 reference parity gate applied: BatchCaseTable is the confirmed reference
  for same-shape restore behavior.
- BatchMatrixTable's core gap is localized to `restore_snapshot` same-shape
  handling. The rest of the skeleton is structurally sound.
- Repair (not rebuild) is the recommended path for interaction parity recovery.
