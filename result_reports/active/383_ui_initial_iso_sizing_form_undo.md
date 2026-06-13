# 383 UI Initial ISO Sizing Form Undo

## Goal

Fix the calculator's oversized first-launch ISO 16358 2-point window behavior
and audit/improve EN14825 form Entry undo behavior without touching calculation
logic.

## Scope / Non-goals

- Scope: calculator shell initial fit lifecycle, window geometry parsing
  robustness, EN14825 form Entry undo helper/application, focused tests, and
  `WORK_PLAN` next-action wording.
- Non-goals: core/data/calculation logic, EN14825 adapter/model/table model,
  reversible/heating-only hours behavior, `MetricInputTable` or
  `TkTableController` refactor, fixture/golden changes, or workflow docs.

## Initial ISO Sizing Root Cause

Manual smoke behavior was reproducible locally:

- First launch after idle/update settled to `895x838`.
- ISO 2-point `preferred_initial_size()` was `773x372`.
- Switching to another ISO profile and back settled to `773x372`.

The root cause was the app shell top-level `ttk.Notebook`: hidden EN14825 content
contributed to the notebook requested size during first launch. Profile
re-entry later called the selected tab's content fit after the notebook had
settled, so it returned to the ISO preferred size.

## Initial ISO Sizing Fix

- `CalculatorTkApp` now stores the top-level notebook, sets its initial content
  size from the selected ISO tab, ignores the synthetic initial tab-change
  event, and runs one initial ISO content fit via `after(0)` after the notebook
  has settled.
- Top-level tab changes update the notebook content size from the selected
  tab's preferred size before fitting.
- `parse_window_geometry()` now handles Tk-returned double-negative coordinate
  strings such as `300x250--280+85`.

After correction, local first-launch reproduction with `update_idletasks()` then
`update()` settled to `773x372`, matching ISO preferred size and profile
re-entry size.

## Form Entry Undo Audit / Fix

- Input matrix cells use `TkTableController` and its table undo stack.
- EN14825 common inputs and design/spec entries were raw `ttk.Entry` widgets.
- Tk/ttk Entry does not support a native `undo=True` option in this environment,
  so a small UI-local `form_entry_undo` helper was added.
- The helper tracks `StringVar` changes and binds Ctrl/Cmd-Z to restore the
  previous form value.
- Applied to EN14825 common auxiliary entries, SEER design entries, and SCOP
  Cd/Pdesignh/Tbiv/TOL form entries.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/calculator_app.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/tabs/iso16358_tab.py` OK.
- `python3 -B -m pytest tests/test_ui_tk_calculator_foundation.py -q` OK, 24 passed.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py -q` OK, 18 passed.
- `python3 -B tools/check_code_structure.py` OK with one accepted soft LOC
  warning for `apps/calculator/ui/sections/en14825_scop_section.py` at 459 LOC.
- `git diff --check` OK.
- `git status --short` showed scoped source/test/docs/report changes.
- Active report count check: 19 active reports; lifecycle cleanup remains a
  separate follow-up.

## Known Risks / Gaps

- EN14825 form undo is lightweight per-entry undo, not the full table selection
  undo model.
- Target desktop manual smoke still needs to confirm first-launch size and
  Ctrl/Cmd-Z behavior in visible windows.

## Project Memory Delta

- none

## Commit / Push

- Pending commit/push.
