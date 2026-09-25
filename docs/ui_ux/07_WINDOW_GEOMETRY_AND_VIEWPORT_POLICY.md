# 07. Window Geometry And Viewport Policy

## Purpose and scope

This document owns predictor_v3's window/viewport adoption and implementation routing. Reusable placement/refit procedures are owned by the global `desktop-window-lifecycle` Skill and its `references/geometry-and-refit.md`. Read that reference for first-show placement, automatic fit, monitor recovery, or dynamic refit work, then the matching local owner below. This does not govern other repositories. The adopted [canonical workflow](https://github.com/teeeeooo/operating-envelope/blob/8232094b13abea6dc37ea315325e7b3c658173d6/skills/desktop-window-lifecycle/references/geometry-and-refit.md) provides a source reference when inspecting this adoption.

The [temporary behavior baseline](README.md#temporary-behavior-baseline) remains in force: policy consolidation preserves existing product behavior and records gaps without fixing them. The criteria below are adopted requirements, not a declaration that every surface currently passes them.

## Predictor adoption

- Initial launch centers near the active/default display, with default content measured and capped inside visible bounds. Profile/content/detail changes preserve current x/current monitor and do not reuse initial centering. Large detail uses top-safe placement, the same auto-height cap, and internal scrolling; manual resize remains available.
- Root-window horizontal scrolling is not allowed. Detail starts at a predictable useful scroll position, normally the newly opened content's top.
- Use hidden-first build/settle/visible-measurement/apply/show for new windows/dialogs where supported; prefer stable containers or cached valid pages for visible transitions. This does not authorize toolkit or product-flow changes.
- [Tokens and layout](02_DESIGN_TOKENS_AND_LAYOUT.md) owns concrete margins, caps, ratios, and minimum sizes. [Input/result surface rules](05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md) owns close/reopen input-state lifetime. Geometry changes must preserve table, copy/export, graph/detail, and calculation behavior.

## Current implementation owners

| Responsibility | Owner to inspect |
| --- | --- |
| Calculator geometry, cap calculations, parent placement | [window_geometry.py](../../apps/calculator/ui/window_geometry.py) |
| Visible-content snapshot measurement | [window_measurement.py](../../apps/calculator/ui/window_measurement.py) |
| One settled shell geometry application | [window_shell.py](../../apps/calculator/ui/window_shell.py) |
| Coalesced event-loop refit and measurement suppression | [window_refit.py](../../apps/calculator/ui/window_refit.py) |
| Profile/nested-tab/detail event composition and scroll reset | [lifecycle/controller.py](../../apps/calculator/ui/lifecycle/controller.py) |
| Focused geometry/monitor evidence | [calculator foundation tests](../../tests/test_ui_tk_calculator_foundation.py) |

These are Calculator owners, not replacement owners for Train/Predict's PySide6 surfaces. Inspect the affected application's current shell before reusing them. Calculator's raw screen dimensions and vertical clamp are implementation fallbacks; this mapping does not claim true per-monitor work-area/DPI acceptance or saved-geometry persistence is implemented.

## Conditional adapter reference

Read the WPF examples below only when explicitly adapting this contract to a WPF shell. They are retained implementation guidance, not the active Predictor toolkit choice. Toolkit APIs stay local; use the global workflow for toolkit-neutral reasoning.

## Adapter / Implementation Notes

- Framework-specific names in this section are examples/evidence, not scope
  boundaries.
- In WPF-style shells, do not rely only on
  `WindowStartupLocation="CenterScreen"`.
- In WPF-style shells, do not keep `SizeToContent` enabled while dynamic detail
  surfaces are opened and closed.
- Determine the current monitor/work area from the current window
  handle before fitting.
- Apply max auto-height only during automatic fit calculations.
- Do not use `Window.MaxHeight` to enforce an auto-fit cap unless a
  product decision explicitly wants to block manual resizing.
- Use `ScrollViewer` for overflow and make scrollbar behavior explicit.
- Put placement logic in a shared service/helper, for example
  `WindowPlacementService`, rather than scattering geometry literals
  across views.
- Keep initial launch, profile/content switch, detail open/close, and
  saved-geometry restore as separate code paths.

## Acceptance Checklist

- First launch appears near the expected display center and is not
  clipped.
- Profile changes do not move the window to the primary monitor.
- Detail open does not clip the lower edge.
- Detail open does not make the window excessively tall; overflow is
  reachable through internal scroll.
- Monitor 2 detail open/close leaves the window on monitor 2.
- Position is preserved across monitors with different resolution or
  DPI.
- Manual resize larger or smaller remains available.
- Saved geometry outside the current monitor set recovers to a safe
  default.
- Nested notebook profile/tab/detail changes trigger a refit after the
  visible sub-tab has settled.
- Hidden tab measurement does not reserve unnecessary visible height and
  does not recursively trigger geometry mutation.
- New dialogs/windows use hidden-first build/settle/measure/apply/show
  lifecycle where the framework allows it.
- Dynamic profile/page switches prefer stable containers or cached valid
  surfaces over repeated visible destroy/create.
- Tables, copy/export, graph/detail content, and calculation behavior
  do not change as a side effect of geometry policy.
