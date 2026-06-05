# 228 — Tkinter Content-Hugging Shell First Slice

## Goal

Implement the first Tkinter content-hugging shell slice from the 227 preflight.
The slice creates a shell owner for visible-content measurement and one-shot
geometry application while keeping refit scheduling and geometry primitives in
their existing owners.

## Scope / Boundary

Implemented:

- new `ui_tk/window_shell.py`;
- first content-hugging target geometry helper;
- first Tk shell apply wrapper;
- `Iso16358Tab` integration through the shell owner;
- focused shell tests and an updated Iso16358Tab boundary test;
- compact `docs/WORK_PLAN.md` next-action update.

Not implemented:

- no calculator core changes;
- no region config or golden/fixture changes;
- no table foundation changes;
- no batch dialog sizing work;
- no PySide/PyQt/WPF/Web adapter implementation;
- no UI policy document changes.

## Shell Owner Responsibility

Added `ui_tk/window_shell.py`.

Responsibilities:

- accept visible content preferred size from the content owner;
- include a positive vertical overflow delta before applying geometry;
- calculate a content-hugging target geometry;
- apply geometry with at most one `root.geometry(...)` call;
- preserve the current x coordinate to avoid multi-monitor jumps during
  profile/detail refits;
- clamp y through the existing vertical visible-bounds policy;
- return whether geometry was actually applied.

Non-responsibilities:

- event-loop scheduling;
- profile/region/Hong Kong knowledge;
- calculator logic;
- table logic;
- toolkit-neutral policy ownership.

## Boundary With `window_refit.py`

`ui_tk/window_refit.py` was not changed. It remains the owner for:

- coalesced event-loop scheduling;
- pending/running guard;
- settled refit sequencing;
- suppress guard.

The shell receives a call only after the scheduler decides a refit should run.

## Boundary With `window_geometry.py`

`ui_tk/window_geometry.py` was not changed. It remains the owner for:

- geometry parsing/formatting;
- capped window size policy;
- preferred-content geometry primitive;
- visible-bounds vertical clamp;
- legacy direct helper functions still used by existing tests and launch code.

The new shell composes existing primitives instead of moving primitive
calculation into `Iso16358Tab`.

## `Iso16358Tab` Integration

`Iso16358Tab._fit_toplevel_to_current_content()` now delegates to
`TkContentHuggingShell.fit_visible_content(...)`.

Before this slice, the path could apply geometry in multiple visible steps:

1. fit to preferred content;
2. grow by vertical overflow delta;
3. clamp vertically.

After this slice, `Iso16358Tab` supplies only:

- `preferred_initial_size()`;
- `vertical_overflow_delta()`;
- scroll reset after the shell fit.

The shell combines preferred height and overflow before applying geometry, so
the profile/detail refit path has one geometry apply target where possible.

Direct metric notebook tab-change refit remains disabled. Hidden metric tabs
still protect width during preferred-size measurement, and height remains based
on the current visible metric tab.

## Lower Blank / Flicker Intent

This slice is intended to reduce flicker by avoiding fit-grow-clamp geometry
mutation chains during Hong Kong profile/detail refits. It should also reduce
the stale lower blank-space path because overflow is folded into the final
visible-content target before geometry is applied.

Windows manual smoke is still required because the remaining issue depends on
real Tk requested-size settling on Windows.

## Tests

Added `tests/test_ui_tk_window_shell.py`:

- visible preferred size target geometry;
- overflow delta folded into target geometry;
- screen-height clamp through existing policy;
- shell applies geometry once;
- shell skips no-op geometry apply.

Updated `tests/test_ui_tk_calculator_foundation.py`:

- `Iso16358Tab` fit path now asserts shell delegation instead of direct vertical
  clamp calls.

## Validation

- `python -m pytest -q tests/test_ui_tk_window_shell.py`: passed.
- `python -m pytest -q tests/test_ui_tk_window_refit.py`: passed.
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py`: passed with Tk
  skips in this environment.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py`: passed with
  Tk skips in this environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing soft warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git diff --check`: passed.
- `git status --short`: only expected files changed before commit.

## Windows Manual Smoke Needed

- Other profile to Hong Kong return: lower blank space removed or meaningfully
  reduced.
- Hong Kong profile reselect: no unexpected size jump.
- Detail open/close: normal content-hugging size.
- Profile/detail transition flicker acceptable.
- No infinite refit loop.
- Selected-range fill paste remains OK.
- Batch dialog sizing remains at the previous state.

## Excluded Scope

- Batch dialog sizing remains excluded.
- Main table migration remains excluded.
- HSPF/EN/AHRI/KS batch expansion remains excluded.
- 07 policy update remains deferred until shell behavior is verified by Windows
  smoke.

## Next Action

Windows smoke closeout for Hong Kong profile-switch sizing and common dynamic
refit owner behavior.
