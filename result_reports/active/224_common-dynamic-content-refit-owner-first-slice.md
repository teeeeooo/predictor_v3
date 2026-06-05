# 224 — Common Dynamic Content Refit Owner First Slice

## Goal

Move dynamic content refit scheduling responsibility out of `Iso16358Tab` into
a small common Tk owner while keeping `ui_tk/window_geometry.py` focused on
geometry calculation/application helpers.

## Scope / Boundary

Implemented:

- common refit orchestration owner;
- duplicate/reentrant request protection;
- settled refit sequencing;
- suppress guard context for measurement side effects;
- `Iso16358Tab` integration for profile/detail/region refit requests.

Not implemented:

- direct metric notebook tab-change refit reintroduction;
- main table migration;
- batch expansion;
- PySide/WPF/Web adapters;
- geometry math/helper changes.

## New Owner

Added `ui_tk/window_refit.py`.

`DynamicContentRefitScheduler` owns:

- coalesced refit scheduling;
- pending/running guard;
- two-step settled refit sequencing via the owner event loop;
- suppress guard context for measurement paths;
- refit callback execution.

It does not know about:

- geometry formulas;
- profile/region/Hong Kong behavior;
- tab composition;
- tables or calculator logic.

## Boundary With `window_geometry.py`

`ui_tk/window_geometry.py` remains unchanged and continues to own one-shot
geometry helpers such as `fit_window_to_preferred_content()`,
`grow_window_by_vertical_delta()`, and visible-bounds clamps.

The new `window_refit.py` owns when a refit callback should run, not how the
window geometry is calculated.

## `Iso16358Tab` Integration

Modified `ui_tk/tabs/iso16358_tab.py`:

- replaced local `_pending_refit_id` / scheduling implementation with
  `DynamicContentRefitScheduler`;
- routed profile switch, region switch, and detail visibility refit requests
  through `_schedule_toplevel_refit()`, now a thin wrapper over the common
  owner;
- used `suppress_requests()` during hidden Hong Kong metric tab measurement in
  `preferred_initial_size()`;
- kept hidden tab width protection and current visible tab height measurement;
- kept direct metric tab-change refit disabled until Windows smoke validates
  the common owner and a later slice chooses to reintroduce that trigger.

## Lower Blank Space

No direct lower-blank-space hotfix was added in this slice. The owner boundary
was corrected first to avoid repeating the 221B loop. Hong Kong lower blank
space should be checked in Windows smoke; if still present, the next fix should
build on this common owner rather than adding another local scheduler.

## Tests

Added `tests/test_ui_tk_window_refit.py`:

- duplicate request coalescing;
- suppress guard request ignoring;
- reentrant request blocking during active fit;
- new request allowed after fit completion.

Updated `tests/test_ui_tk_iso_table_autocalc.py`:

- integration tests now check the common scheduler state;
- measurement suppress test uses the scheduler suppress context;
- metric tab-change refit remains disabled until common-owner smoke validation.

## Validation

- `python -m pytest -q tests/test_ui_tk_window_refit.py` — passed.
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py` — passed with
  Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py` — passed with
  Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git diff --check` — passed.
- `git status --short` — reviewed before commit.

Not run:

- `python app_calculator_tk.py` — `DISPLAY` is not set in the Codex
  environment.

## Windows Manual Smoke

- Hong Kong profile entry has no resize loop.
- Hong Kong CSPF lower blank space behavior.
- Profile switch away and back to Hong Kong has no resize loop.
- CSPF/HSPF metric tab switching has no resize loop.
- Detail open/close has no resize loop.
- Selected-range fill paste remains OK.
- Batch dialog sizing remains OK.

## Excluded Scope

- no calculator core changes;
- no region config, fixture, or golden changes;
- no table foundation changes;
- no main table migration;
- no HSPF / EN14825 / AHRI / KS batch work;
- no PySide/WPF/Web implementation;
- no UI policy or docs/designs changes;
- no report lifecycle/archive maintenance.

## Next Action

Windows smoke closeout for the common dynamic refit owner and Hong Kong metric
notebook sizing.
