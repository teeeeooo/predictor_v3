# 279 Controller Switch Design Preflight

## Goal

Assess the feasibility of migrating from `ExcelLikeTableController` to the
common `TkTableController` + `interaction_core.py` foundation, and define the
safest next implementation slice.

## Scope

- Reference Evidence Gate usage on `CODEBASE_REFERENCE_MAP.md`.
- Current main table/controller contract analysis.
- Common table foundation contract analysis.
- Parity/gap assessment between the two controllers.
- Switch blockers and prerequisites identification.
- Pilot strategy and next slice recommendation.

## Excluded Scope

- No code changes.
- No test changes.
- No controller switch implementation.
- No ui_tk/sections/* changes.
- No schema/public API changes.

## Reference Evidence Gate Usage

Per `docs/agent_workflows/DIFF_READ_BUDGET.md`:

- Map read: targeted `grep` on `ExcelLikeTableController`,
  `MetricInputTable`, `TkTableController`, `TkTableSurface`,
  `interaction_core` in `CODEBASE_REFERENCE_MAP.md`.
- Code read: `rg` for class/function boundaries, then targeted range reads
  for paste, undo, selection, invalid-field, and clipboard methods.
- No broad map reads. No map regeneration (no structural code changes).

## Current Main Table Contract (Task 2)

**ExcelLikeTableController + MetricInputTable:**

- **Value storage**: `_values` dict (field_key -> str), backed by Tk StringVar
- **Editable mapping**: per-field entries; positions mapped via
  `field_key_for_address` / `_by_position`
- **Paste**: raw text, boundary-clipped via `clip_paste_targets`, no role
  filtering, no validation rejection (per 265)
- **Undo**: simple list of dict snapshots; push on every
  `set_address_values_batch`
- **Selection**: per-cell background painting; `TABLE_INVALID_BG` for invalid
  fields, `TABLE_SELECTED_BG` for selected, `TABLE_EDITABLE_BG` for editable
- **Invalid field state**: checked in `_base_background_for_field`; fields set
  via `set_invalid_fields`
- **Callback**: `_values_changed_callback` called via `set_values_batch`
- **Keyboard**: entry-level binds (Tab, Return, arrows, Ctrl-C/V/Z, F2)
- **Replace-on-type**: `KeyPress` bind on entries -> `_type_replace`
- **Edit mode**: F2 / double-click -> `_enter_edit_mode`; Escape -> restore
  snapshot

## Common Table Foundation Contract (Task 3)

**TkTableController + interaction_core:**

- **Surface protocol**: `TkTableSurface` / `PerCellRoleTableSurface`
- **Paste**: role-filtered via `editable_paste_targets_by_role` using
  `cell_role`; respects `EDITABLE` / `READONLY`
- **Undo**: `UndoStack` class (push/pop/clear); push on `_apply`
- **Selection**: paints via `default_cell_background(position)` + selection
  override; `TABLE_ACTIVE_BG` for active cell
- **Invalid field state**: relies on surface's `default_cell_background` (not
  checked directly by controller)
- **Callback**: no built-in callback; notification depends on surface
  `set_positions_batch` implementation
- **Keyboard**: widget-level binds on `cell_frame` and `cell_widget` for every
  cell; `<KeyPress>` -> `_type_replace`
- **Replace-on-type**: `_type_replace` returns "break" after setting char and
  entering edit mode
- **Edit mode**: F2 -> `_enter_edit_mode`; Escape -> restore snapshot

## Parity / Gap Assessment (Task 4)

| Capability | ExcelLike | TkTableController | Gap |
|------------|-----------|-------------------|-----|
| Raw text paste | boundary-clipped | role-filtered | TkTable is BETTER aligned with 265 policy |
| Invalid field visual | direct check in `_paint_selection` | via `default_cell_background` | **Compatible** — MetricInputTable already implements invalid BG in `default_cell_background` |
| Callback notification | `set_address_values_batch` -> callback | `set_positions_batch` -> callback | **Compatible** — chain works through `set_values_batch` |
| Undo mechanism | simple list | `UndoStack` class | Minor — different implementation, same behavior |
| Selection painting | direct | via surface | **Compatible** |
| Replace-on-type | entry bind | widget bind | **Compatible** |
| Edit mode (F2/Escape) | supported | supported | **Compatible** |
| Clipboard surface methods | not needed by ExcelLike | `clipboard_clear/append/get` | **BLOCKER** — MetricInputTable missing these protocol methods |
| `winfo_containing` | not needed | used in `_drag` | **Compatible** — inherited from `ttk.Frame` |

**Key blocker identified:**

`MetricInputTable` is missing three `TkTableSurface` protocol methods:
- `clipboard_clear()`
- `clipboard_append(text: str)`
- `clipboard_get() -> str`

These are called by `TkTableController._copy()` and `._paste()`. Without them,
a direct switch would fail at runtime.

**No-blocker list:**
- Invalid field visual state: already compatible via `default_cell_background`
- Callback chain: already compatible via `set_positions_batch` -> `set_values_batch`
- Selection painting: already compatible
- Paste policy: TkTableController's role-filtered paste is BETTER aligned with
  the 265-approved policy
- Undo: behavior-equivalent

## Switch Blockers and Prerequisites (Task 4 continued)

**Hard prerequisites (must complete before any switch):**
1. Add `clipboard_clear`, `clipboard_append`, `clipboard_get` to
   `MetricInputTable`.

**Soft prerequisites (nice to have before switch):**
2. Focused parity tests exercising `MetricInputTable` + `TkTableController`
   together (paste, undo, selection, invalid field marking, keyboard nav).
3. Verify replace-on-type behavior parity between the two controllers on
   MetricInputTable's entry widgets.

**Not blockers:**
- Invalid field marking (already compatible)
- Callback notification (already compatible)
- Selection painting (already compatible)
- Undo mechanism (behavior-equivalent)

## Pilot Strategy Decision (Task 5)

**Rejected alternatives:**

- **Direct main MetricInputTable switch**: Too risky without first adding
  clipboard methods and running parity tests.
- **One isolated calculator section pilot**: The main table IS the table used
  by sections. Switching a section would require switching the table's
  controller, which is the same blast radius.
- **Hidden/optional controller injection flag**: Adds complexity without clear
  benefit. The switch should be a clean replacement once parity is proven.
- **Single pilot controller switch**: Skipping the prerequisite of adding
  missing surface methods would fail at runtime.

**Recommended strategy:**

1. **Precondition slice**: Add missing `TkTableSurface` protocol methods to
   `MetricInputTable`.
2. **Parity test slice**: Create focused tests verifying `MetricInputTable` +
   `TkTableController` behavior matches `MetricInputTable` +
   `ExcelLikeTableController` for paste, undo, selection, invalid marking,
   keyboard navigation.
3. **Switch slice**: After parity tests pass, switch one section's controller
   in a controlled manner with Windows smoke.

## Recommended Next Implementation Slice (Task 6)

**Slice name**: Add missing `TkTableSurface` protocol methods to
`MetricInputTable`

**Goal**: Implement `clipboard_clear`, `clipboard_append`, `clipboard_get` in
`MetricInputTable` so it fully satisfies the `TkTableSurface` protocol.

**Files to modify**:
- `ui_tk/metric_input_table.py` only

**Implementation**:
```python
def clipboard_clear(self) -> None:
    self.clipboard_clear()

def clipboard_append(self, text: str) -> None:
    self.clipboard_append(text)

def clipboard_get(self) -> str:
    return self.clipboard_get()
```

These are thin wrappers around `ttk.Frame` inherited clipboard methods. Zero
behavior change for existing `ExcelLikeTableController` usage.

**Excluded**:
- No controller switch
- No section file changes
- No test changes (thin wrappers, no logic)
- No other files

**Verification**:
- `python3 -B -m py_compile ui_tk/metric_input_table.py`
- `python3 -B tools/check_code_structure.py`
- `git diff --check`
- No pytest needed (thin wrappers)
- No Windows smoke needed

**After this slice**:
- Controller switch parity test foundation (focused tests for
  MetricInputTable + TkTableController)

## Excluded Scope

- Controller switch implementation
- Section file changes
- Test changes in this slice
- `BinDetailGraph._draw` split (deferred)
- `BinDetailPanel` further cleanup (deferred)

## Risks

- None for the recommended slice (thin clipboard wrapper methods).
- For the eventual switch: binding strategy difference (widget-level vs
  entry-level) may cause subtle keyboard navigation differences. Parity tests
  will catch this.

## Next

- Implement missing `TkTableSurface` clipboard methods in `MetricInputTable`.
- After that: controller switch parity test foundation.
- After that: pilot section controller switch with Windows smoke.
