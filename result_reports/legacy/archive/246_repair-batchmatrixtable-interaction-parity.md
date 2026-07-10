# 246 Repair BatchMatrixTable Interaction Parity And Common MxN Paste Fill

## Goal

Fix Windows manual smoke issues in BatchMatrixTable:
1. M-row x N-column clipboard paste repeat-fill gap in common helper.
2. Same-shape restore rebuild causing flicker/focus loss/undo issues.

## Scope

- `ui_tk/table/interaction_core.py`: generalize paste fill to MxN repeat-tile.
- `ui_tk/batch_matrix_table.py`: add same-shape in-place restore path.
- Tests for both fixes.

## 245 Audit Correction

245 audit incorrectly concluded that "paste tiling is not a common helper gap."
This was wrong. The root cause was `editable_paste_targets_by_role()` else path,
which pasted multi-row clipboard only once regardless of selection size.
This report supersedes that incorrect judgment.

## Reference Parity Evidence

- BatchCaseTable `restore_snapshot`: preserves widgets on same-shape restore by
  updating model rows and StringVars directly without `_rebuild_table()`.
- BatchCaseTable `set_positions_batch`: direct StringVar updates with
  `_batch_depth` coalescing.

## Root Cause

### 1. Paste repeat-fill gap
`editable_paste_targets_by_role()` else branch pasted multi-row clipboard
exactly once. A 2-row clipboard pasted onto a 6-row selection produced targets
only for the first 2 rows, leaving the remaining 4 rows empty.

Fix: tile/repeat the clipboard matrix across the full selection rectangle using
modulo indexing. Single-cell anchor and 1x1/1-row special cases remain unchanged.

### 2. Same-shape restore rebuild
`BatchMatrixTable.restore_snapshot()` unconditionally called `_rebuild_table()`,
destroying all widgets even when the logical case count did not change.
This caused focus loss, selection loss, and visible flicker on undo and paste.

Fix: add a same-shape path that updates `self.cases` and `self._variables`
directly, using `_batch_depth` coalescing for `_notify_changed()`, matching
BatchCaseTable's proven pattern.

## Fixed Behavior

### Common paste helper
- 2x2 clipboard into 6x4 selection: repeats as tiled blocks.
- 3x3 clipboard into 9x3 selection: repeats row-by-row.
- Single-cell anchor with multi-row clipboard: still pastes full clipboard
  top-left anchored (existing behavior preserved).
- 1x1 fill and 1-row fill: unchanged.
- Non-editable cells are still skipped by role resolver.

### BatchMatrixTable restore
- Same logical case count: in-place update without rebuild.
- Different logical case count: rebuild as before.
- Snapshot keys missing from current case are cleared to empty string.
- `_batch_depth` coalescing prevents duplicate notifications.

## MVC/SoC Boundary

- `interaction_core.py`: common helper, no profile-specific logic.
- `batch_matrix_table.py`: surface-level fix only; public contract unchanged.
- `table/controller.py`: no changes; controller reuse confirmed.

## Tests

### interaction_core (headless)
- `test_multi_cell_clipboard_repeats_to_fill_larger_selection`: 2x2 into 4x3.
- `test_mx_n_clipboard_repeats_to_fill_selection`: 2x2 into 6x4.
- `test_3x3_clipboard_repeats_to_fill_larger_selection`: 3x3 into 9x3.
- Existing paste tests updated and passing.

### BatchMatrixTable (Tk available only)
- `test_same_shape_restore_preserves_widgets`: widget IDs unchanged after restore.
- `test_shape_changing_restore_rebuilds_widgets`: rebuilds when case count changes.

### Existing regression
- `test_ui_tk_table_interaction_core.py`: 11 passed
- `test_ui_tk_batch_table_controller.py`: 13 passed
- `test_ui_tk_hong_kong_cspf_matrix_migration.py`: 14 passed
- `test_ui_tk_batch_matrix_models.py`: 9 passed
- `test_ui_tk_table_controller_per_cell_roles.py`: 4 passed
- `test_ui_tk_batch_matrix_table.py`: 1 skipped (Tk unavailable)
- `test_ui_tk_hong_kong_cspf_batch_spec.py`: 5 passed

## Manual Smoke Checklist (Windows)

- [ ] 2-row one-case block paste into multiple selected cases repeats correctly.
- [ ] Arbitrary M-row block paste fills selection rectangle by tiling.
- [ ] Single-cell anchor paste still pastes full clipboard top-left anchored.
- [ ] Repeated Ctrl+Z works without clicking another cell.
- [ ] Undo no longer visibly rebuilds/flickers for value-only changes.
- [ ] Range delete then undo restores the whole range as one action.
- [ ] Existing calculate CSPF/CSEC result still works.
- [ ] Wheel scroll and close/reopen persistence still work.

## Known Risks

- `batch_matrix_table.py` now exceeds 400 LOC soft limit (408). Consider helper
  extraction in a future cleanup slice.
- Headless tests skip Tk focus/selection continuity verification.
- Windows manual smoke is required before treating interaction parity as stable.

## Excluded Scope

- No copy-all / CSV / xlsx export.
- No EN/AHRI/KS profile expansion.
- No controller fork or core changes.
- No BatchCaseTable modifications.
- No 245 report direct edits.

## Next Suggested Action

- Windows manual smoke for the checklist above.

## Project Memory Delta

- 245 audit's "paste tiling is not common helper gap" judgment is superseded.
- `editable_paste_targets_by_role()` repeat-fill is now generalized to MxN tiling.
- Same-shape in-place restore is the confirmed pattern for both flat and matrix
  tables.
