# 227 — Toolkit-Neutral Content-Hugging Window/Form Shell Preflight

## Goal

Define the window/screen/dialog shell contract needed to stop repeated local
geometry patches. This is a preflight/report task only; no code or UI policy
implementation was changed.

## Checked Files And Evidence

- `result_reports/active/226_content-hugging-window-sizing-redesign-preflight.md`
- `result_reports/active/224_common-dynamic-content-refit-owner-first-slice.md`
- `result_reports/active/225_hong-kong-profile-switch-sizing-closeout.md`
- `result_reports/memory/project_memory_seed.md`
- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
- `ui_tk/window_refit.py`
- `ui_tk/window_geometry.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/scrollable_frame.py`
- `docs/WORK_PLAN.md`
- SPOT `ui/app.py` through the GitHub Connector, used only as concrete UX
  evidence.

## Current Issue

The infinite Hong Kong resize loop is stabilized, and `ui_tk/window_refit.py`
now owns common refit scheduling. The remaining Windows UX problems are still
visible:

- Other profile to Hong Kong return can leave lower blank space.
- Re-selecting Hong Kong while already on Hong Kong can produce a tighter size.
- Detail open/close can recover the size.
- Profile/detail transitions can visibly flicker.

This is not best treated as a Hong Kong-only or Tkinter-only hotfix. The same
failure mode can recur for any toolkit when nested notebooks, stacked screens,
dynamic detail panels, scrollable viewports, and automatic window fitting are
implemented without a common shell/form owner.

## 226 Direction Confirmed

226's Option B+C remains the right direction:

- measure final visible content after render/settle;
- apply geometry once where possible;
- use hidden content only for width protection;
- keep height based on current visible content;
- avoid adding more settle-cycle patches as the primary strategy.

The refinement from this preflight is that the owner should be a
content-hugging shell/form layer, not another local `Iso16358Tab` sizing path.

## SPOT Evidence

SPOT is not a source of truth, owner, dependency, copy target, or reference
implementation for predictor_v3. It is useful evidence that the desired UX is
feasible in a Tkinter application.

The relevant observed flow in SPOT `ui/app.py` is:

1. build the main screen content;
2. run idle layout update;
3. read requested width/height;
4. clamp the size to min/max bounds;
5. center within the screen;
6. apply a single geometry string and minimum size.

That supports the UX target: content should be built first, then measured,
clamped, placed, and applied through a shell owner rather than through repeated
local post-render refit calls.

## Toolkit-Neutral Shell/Form Contract

New window, screen, dialog, and nested profile surfaces should follow a common
content-hugging shell/form contract:

- A screen provides visible content; the shell owns size, position, scroll, and
  refit orchestration.
- Initial open fits the current visible content.
- Profile or screen switch fits the new visible content.
- Detail open/close fits the visible detail state.
- Lower blank space is a UX failure for content-hugging calculator/form shells.
- Visible resize/flicker should be minimized.
- Geometry apply should be coalesced to one visible mutation per user action
  where possible.
- Hidden content can be used to protect width, but must not inflate automatic
  height.
- Height is based on the current visible content.
- Oversized content should use internal scrolling instead of inflating the
  shell beyond viewport caps.
- Placement must stay within screen bounds and should preserve the current
  center or use screen center consistently.
- Refit loops are not acceptable.
- Whether auto-fit continues after the user manually resizes the window remains
  a separate policy decision.

## Toolkit Adapter Direction

The contract is common; implementation belongs in toolkit adapters.

- Tkinter: introduce `ui_tk/window_shell.py` or an equivalent owner. Keep
  `ui_tk/window_refit.py` as the event-loop scheduling owner and
  `ui_tk/window_geometry.py` as geometry primitives.
- PySide/PyQt: use a QDialog/QMainWindow shell with `sizeHint`,
  `minimumSizeHint`, `adjustSize`, and resize-event adapter rules.
- WPF: use a WindowShell concept around `SizeToContent` and Measure/Arrange
  timing.
- Web: use a layout shell with viewport manager and ResizeObserver/layout effect
  semantics.

No PySide/PyQt/WPF/Web implementation is part of this task.

## predictor_v3 Owner Candidates

Recommended Tkinter owner split:

- `ui_tk/window_shell.py`: content-hugging shell/form flow, final visible
  measurement, clamp/placement orchestration, and one-apply target.
- `ui_tk/window_refit.py`: coalesced scheduling, pending/running guard,
  settled refit, suppress guard.
- `ui_tk/window_geometry.py`: geometry primitive calculation and application.
- `Iso16358Tab`: content-specific preferred visible surface and trigger
  requests only; it should not keep accumulating shell sizing policy.

## 228 First Implementation Slice

Recommended next task:

`228 — Tkinter content-hugging shell first slice`

Include:

- create `ui_tk/window_shell.py` or equivalent;
- implement first content-hugging measurement/apply flow;
- perform final visible-content measurement after render/settle;
- apply min/max clamp and screen-bounds-safe placement;
- coalesce to one geometry apply per refit action where possible;
- keep `window_refit.py` and `window_geometry.py` roles intact;
- reduce direct sizing responsibility in `Iso16358Tab`;
- use the Hong Kong calculator profile-switch/detail flows as the first
  validation target;
- improve lower blank space and flicker.

Exclude:

- batch dialog sizing;
- main table migration;
- batch expansion;
- PySide/PyQt/WPF/Web implementation;
- full `ui_tk` cleanup;
- 07 policy update.

## Why No 07 Policy Update Now

`docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` already contains the
high-level window geometry and nested/dynamic refit policy. The missing piece is
code ownership and implementation proof. The policy should be updated only
after the 228 shell slice and Windows smoke confirm the exact contract wording.

## Excluded Scope

- No code changes.
- No tests added or changed.
- No UI policy document changes.
- No docs/designs changes.
- No report lifecycle/archive work.

## Validation

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing soft warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git status --short`: only this report plus `docs/WORK_PLAN.md` and
  `project_log.md` changed before commit.
- `pytest`: not run; this is a preflight/report-only task.
- GUI smoke: not run; this is a preflight/report-only task.

## Next Action

Tkinter content-hugging shell first slice.
