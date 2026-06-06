# 229 — Tk Content-Hugging Shell Template

## Goal

Promote `ui_tk/window_shell.py` from a tuple-based geometry helper into a
reusable Tk content-hugging form/shell template. Hong Kong calculator remains
the first consumer and validation target, but the shell must not know Hong Kong,
profile, region, calculator, or table details.

## 228 Failure Cause

228 added a useful shell owner, but Windows smoke still showed:

- profile/detail flicker improved but remained visible;
- Hong Kong lower blank space remained;
- the shell still accepted an already-computed preferred-size tuple, so
  `Iso16358Tab` still owned most measurement orchestration.

The likely remaining sizing path is not only a geometry-apply problem. The root
window can carry minsize/size state from previous content, while the shell had
no reusable contract for content registration, overflow measurement, and
after-fit cleanup.

## Reusable Template API

`ui_tk/window_shell.py` now exposes:

- `TkContentHuggingShell.register_content(...)`
- `TkContentHuggingForm.fit()`
- provider type aliases:
  - `PreferredSizeProvider`
  - `OverflowProvider`
  - `AfterFitHook`

Supported registration modes:

- `content=widget`: default measurement uses widget requested width/height.
- `preferred_size_provider=...`: nested/profile surfaces can provide custom
  visible-content measurement when raw widget requested height would include
  hidden or non-visible content.
- `overflow_provider=...`: scrollable surfaces can add visible overflow before
  one geometry apply.
- `after_fit=...`: consumers can reset scroll or run post-fit cleanup without
  putting that behavior in the shell.

The shell also relaxes `root.minsize(...)` to the target geometry before
applying geometry. This is intended to prevent a larger previous content state
from blocking shrink-to-content behavior.

## Boundary

`window_shell.py`:

- owns the reusable Tk form/shell API;
- owns content/provider registration;
- owns one content-hugging geometry apply target;
- owns minsize relaxation to the target geometry.

`window_refit.py`:

- remains unchanged;
- owns scheduling, pending/running guard, settled refit, suppress guard.

`window_geometry.py`:

- remains unchanged;
- owns geometry primitives, caps, parse/format, and visible-bounds clamp.

`Iso16358Tab`:

- is now a consumer;
- registers preferred-size provider, overflow provider, and after-fit scroll
  reset hook;
- still owns Hong Kong visible-size policy because hidden metric tab width and
  current visible tab height are content-specific;
- does not push Hong Kong/profile/region knowledge into the shell.

## Lower Blank / Flicker Improvement Intent

This slice targets two remaining causes:

- measurement orchestration is now a reusable provider contract instead of a
  per-call tuple handoff;
- shell fit relaxes root minsize to the current target before geometry apply.

Windows manual smoke is still required to determine whether this is enough to
remove the Hong Kong lower blank space and make profile/detail flicker
acceptable.

## Tests

Updated `tests/test_ui_tk_window_shell.py`:

- provider-based content registration;
- widget-content default measurement;
- missing provider/content validation;
- after-fit hook execution;
- overflow provider integration;
- minsize relaxation before geometry apply;
- no-op geometry apply skip.

Updated `tests/test_ui_tk_calculator_foundation.py`:

- `Iso16358Tab` is verified as a shell consumer that registers preferred-size,
  overflow, and after-fit providers.

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
- Profile/detail transition flicker acceptable.
- Hong Kong profile reselect: no size jump.
- Detail open/close: normal content-hugging size.
- No infinite refit loop.
- Selected-range fill paste remains OK.
- Batch dialog sizing remains at the previous state.

## Excluded Scope

- No calculator core changes.
- No region config or golden/fixture changes.
- No table foundation changes.
- No batch dialog sizing.
- No HSPF/EN/AHRI/KS batch implementation.
- No PySide/PyQt/WPF/Web implementation.
- No UI policy document changes.
- No docs/designs changes.

## Next Action

Windows smoke closeout for Hong Kong profile-switch sizing and common dynamic
refit owner behavior.
