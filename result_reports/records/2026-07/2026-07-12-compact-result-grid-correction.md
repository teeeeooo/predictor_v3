```yaml
record:
  date: 2026-07-12
  topic: compact-result-grid-correction
  tags: calculator, tkinter, compact-result, focus, clipboard, correction
  memory_review: no-change
  memory_reason: The existing table-family memory already owns the durable boundary; this correction restores its intended focus and clipboard delegation.
```

# Change Reason

Compact Result Grid bound keyboard copy only to its outer frame, used one fixed
Tk widget name, and duplicated TSV/clipboard behavior already owned by the
shared Calculator table clipboard helper.

# Contract / Behavior Changed

Visible header/body cells and labels now focus their owning compact grid on
click, after which Ctrl/Cmd+C copies the whole logical table. Grid surfaces use
Tk default unique names, allowing siblings under one parent. TSV encoding and
clipboard writes delegate to `table_clipboard`; `as_tsv()`, ISO status text,
export data, and profile-local wrapper behavior remain compatible.

# Evidence And Verification

- 197 focused foundation, ISO, interaction, lifecycle, refit, and token tests passed.
- Tests cover click-to-focus, keyboard copy bindings, sibling identity/state
  isolation, helper-identical TSV, empty-safe cell encoding, update, and clear.
- Targeted compilation, whitespace check, and structure guard completed.

# Changed Files

- `apps/calculator/ui/table/compact_result_grid.py`
- `apps/calculator/ui/table/grid_primitives.py`
- `tests/test_ui_tk_iso_iseer_2point_controller_switch.py`

# Known Risks

Focus event delivery is toolkit/platform-sensitive; production retains both
Control and Command bindings, and focused Tk tests exercise real visible-widget
click bindings. No selection model was added.
