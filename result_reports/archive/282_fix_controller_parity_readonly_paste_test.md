# 282 Fix Controller Parity Readonly Paste Test

## Goal

Correct the readonly paste test in the controller switch parity test suite
so that it validates actual paste behavior on a mixed editable/readonly
table, not just role logic on an all-editable fixture.

## Scope

- Modify `tests/test_ui_tk_metric_input_table_controller_parity.py` only.
- Add a `mixed_table` fixture (2x2: left column editable, right column readonly).
- Replace `test_paste_ignores_readonly_target` with a real behavior test.
- No production code changes.
- No controller switch implementation.

## 281 Test Gap

`test_paste_ignores_readonly_target` in 281 had two problems:

1. The `sample_table` fixture defines **all four** cells as editable, so there
   was no readonly cell to test against.
2. The test body did not actually call `_paste()`.  It only verified
   `cell_role((0,0)) == CellRole.EDITABLE`, which confirms intent but not
   behavior.

This left the parity contract claim “Paste role-filtering ignores readonly
cells” unverified.

## Mixed Editable/Readonly Fixture

Added `mixed_table` and `mixed_ctrl` fixtures:

| Position | Role | Field | Initial Value | Display |
|----------|------|-------|---------------|---------|
| (0, 0) | EDITABLE | a | "1" | "1" |
| (0, 1) | READONLY | — | — | "-" |
| (1, 0) | EDITABLE | b | "2" | "2" |
| (1, 1) | READONLY | — | — | "-" |

Only cells in `editable_cells` are editable; everything else is READONLY per
`MetricInputTable.cell_role`.

## Corrected Readonly Paste Test

Replaced the placeholder test with a real behavior test:

1. Select `(0, 0)` on `mixed_ctrl`.
2. Load a 2x2 TSV clipboard matrix:
   ```
   10\tREADONLY_SHOULD_NOT_APPLY
   20\tREADONLY_SHOULD_NOT_APPLY
   ```
3. Call `mixed_ctrl._paste()`.
4. Assert editable cells changed:
   - `(0, 0)` → `"10"`
   - `(1, 0)` → `"20"`
5. Assert readonly cells unchanged:
   - `(0, 1)` → `"-"`
   - `(1, 1)` → `"-"`
6. Assert underlying snapshot contains only editable field keys (`a`, `b`)
   with updated values, and length == 2.

This now exercises the actual `_paste → editable_paste_targets_by_role →
_is_mutable_position` filter path on a table with mixed roles.

## Production Code Change

**None.**  The production paste and role-filtering logic already behaves
correctly; the gap was only in test coverage.

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Parity tests | `pytest tests/test_ui_tk_metric_input_table_controller_parity.py -rs -vv` | 15 skipped, 0 failures |
| Compile check | `py_compile tests/...controller_parity.py` | OK |
| Structure guard | `python3 -B tools/check_code_structure.py` | No new violations |
| Git diff check | `git diff --check` | Clean |

## Next

- Windows/iMac GUI focused parity test confirmation.
- After GUI pass: controller switch pilot implementation.
