# 233B — Visible Measurement Snapshot Contract

## Goal

Implement the first slice from 233A: preferred size and overflow delta must be
read from one visible measurement snapshot before shell geometry is applied.
This is a shell/form measurement contract change, not a Hong Kong hotfix.

## Current Contract Evaluation

Before this change, `TkContentHuggingForm.fit()` read:

1. `preferred_size_provider()`;
2. `overflow_provider()`;
3. shell geometry apply.

Those providers could observe different layout states. `preferred_size` could
temporarily select hidden notebook tabs and update layout, while
`vertical_overflow_delta` could later read canvas bbox / canvas height from a
separate state. That matched the 233A finding and did not contradict it.

## Snapshot Data Shape

Added `VisibleContentSnapshot` in `ui_tk/window_measurement.py`:

- `preferred_size: tuple[int, int]`
- `vertical_overflow_delta: int`
- `include_overflow_in_fit: bool`
- `diagnostics: Mapping[str, int]`

Diagnostics include current content requested size, nested notebook dimensions,
current visible tab height, and measured overflow delta. They are measurement
evidence only and contain no calculator/profile/domain data.

## Measurement Adapter Change

`TkVisibleContentMeasurement.snapshot()` now returns one object containing both
preferred size and overflow delta from one measurement turn.

Compatibility wrappers remain:

- `preferred_size()` returns `snapshot().preferred_size`.
- `vertical_overflow_delta()` returns `snapshot().vertical_overflow_delta`.

The adapter still owns:

- hidden tab width protection;
- current visible tab height;
- notebook chrome height calculation;
- measurement suppress guard;
- scroll overflow reading.

It does not know Hong Kong, region config, formulas, or profile logic.

## Shell/Form API Change

`TkContentHuggingShell.register_content(...)` now accepts
`snapshot_provider`.

Behavior:

- if `snapshot_provider` exists, `TkContentHuggingForm.fit()` reads one
  snapshot and uses that for the fit;
- legacy `preferred_size_provider` / `overflow_provider` paths still work;
- plain `content=widget` registration still works.

Overflow policy:

- snapshot overflow is not added to target height unless
  `include_overflow_in_fit` is true;
- this prevents stale/intermediate overflow from automatically preserving
  extra height during profile-switch shrink paths;
- detail/large-content paths can still opt in by returning a snapshot with
  `include_overflow_in_fit=True`.

## Iso16358Tab Integration

`Iso16358Tab` now registers:

- `snapshot_provider=self._measurement.snapshot`

instead of separate preferred-size and overflow providers. Compatibility
methods remain as wrappers for existing callers/tests.

No Hong Kong-only branch, settle-cycle increase, or direct metric tab-change
refit was added.

## MVC / Clean Architecture Boundary

- `window_measurement.py`: Tk-specific measurement adapter and snapshot owner.
- `window_shell.py`: shell/form API and geometry apply owner.
- `window_refit.py`: scheduling/guard owner, unchanged.
- `window_geometry.py`: primitive geometry helper, unchanged.
- `Iso16358Tab`: View/consumer that wires the adapter to the shell.

The View no longer chooses how to combine preferred size and overflow; that
contract lives in adapter/shell boundaries.

## Tests

Added/updated:

- `tests/test_ui_tk_window_measurement.py`
  - snapshot returns preferred size, overflow, and diagnostics;
  - hidden tabs protect width while height follows current visible tab;
  - compatibility methods read from snapshots.
- `tests/test_ui_tk_window_shell.py`
  - shell uses snapshot provider first;
  - snapshot overflow is ignored by default;
  - overflow can be included when policy opts in;
  - legacy provider and widget-content paths remain compatible.
- `tests/test_ui_tk_calculator_foundation.py`
  - `Iso16358Tab` registers the measurement snapshot provider with the shell.

## Validation

- `python -m pytest -q tests/test_ui_tk_window_measurement.py`: passed.
- `python -m pytest -q tests/test_ui_tk_window_shell.py`: passed.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py`: passed with
  Tk skips in this environment.
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py`: passed with Tk
  skips in this environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git diff --check`: passed.
- `git status --short`: showed only expected 233B changes before commit.

## Windows Manual Smoke Needed

- Other profile to Hong Kong return: lower blank space removed or meaningfully
  reduced.
- Hong Kong profile reselect: no size jump.
- Detail open/close: normal content-hugging size.
- Profile/detail transition flicker acceptable.
- No infinite refit loop.
- Selected-range fill paste remains OK.
- Batch dialog sizing remains at the previous state.

## Excluded

- No full profile switch / reselect / detail lifecycle unification.
- No render -> mount -> settle -> snapshot -> fit orchestration helper.
- No Hong Kong-only branch.
- No settle-cycle-only patch.
- No direct metric tab-change refit reintroduction.
- No batch dialog sizing, main table migration, policy doc change, calculator
  core change, region config change, or fixture/golden change.

## Next Action

Windows smoke closeout for Hong Kong profile-switch sizing. If lower blank
space remains, create 233C for mapped-surface lifecycle orchestration.
