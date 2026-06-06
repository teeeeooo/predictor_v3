# 07. Window Geometry And Viewport Policy

## Purpose

This document defines the interface-framework-agnostic UX contract for window
placement, automatic sizing, viewport limits, scrolling, and
multi-monitor behavior.

Observed implementation lessons may be recorded as evidence, but concrete
framework names are not scope boundaries.

## Scope

This policy applies to GUI, web, and external interface shells that manage
window or viewport placement, automatic sizing, scrolling, and dynamic content
refit.

`02_DESIGN_TOKENS_AND_LAYOUT.md` owns layout tokens and ratios.
This document owns how those values are used to place windows and
manage viewports.

## Problem Types Observed

- Initial launch was sometimes too tall or clipped near the lower edge.
- Detail open could grow the window downward beyond the visible area.
- Profile/detail auto-fit reused initial centering and moved a window
  back to the primary monitor.
- Raw screen height did not reliably represent the usable work area
  because of taskbars, scaling, and window chrome.
- Fixes that clamp x can break dual-monitor workflows.

## Principles

- Initial launch and profile/detail auto-fit are different problems.
- Automatic fit must not grow beyond a safe fraction of the visible
  viewport.
- Manual user resizing must not be blocked just because automatic fit
  has a cap.
- Large detail surfaces prefer top-safe placement.
- Preserve current x and current monitor for profile/content/detail
  changes.
- Avoid primary-monitor recentering unless the current placement is no
  longer recoverable.
- Treat raw screen height as an approximation, not the true visible
  work area.
- Overflow belongs inside the content viewport through scrolling.
- After detail open, scroll position must be predictable.

## Placement Modes

### Initial Launch

- Render the default content first, then measure natural requested size.
- Apply content margin and max auto-size cap.
- Center the initial window near the active or default display.
- Clamp to visible bounds so first launch does not start off-screen.
- This is the only mode where centering is normally appropriate.

### Profile / Content Switch

- Refit size to the new content within the auto-fit cap.
- Preserve current x/current monitor.
- Preserve y for small changes unless it would push the lower edge out
  of view.
- Do not recenter to the primary monitor.

### Detail Open / Close

- Treat detail surfaces as potentially large.
- Apply the same max auto-height cap used by other automatic fit paths.
- Prefer top-safe y placement for large detail surfaces.
- Preserve x/current monitor.
- Use internal scroll for content beyond the visible area.
- Reset the detail/content scroll position in a predictable way after
  opening or switching content.

### Nested Notebook / Dynamic Sub-tab Refit

- Nested notebooks, dynamic sub-tabs, detail toggles, and scrollable
  content can settle later than a single static section. A single fit
  immediately after render may not be enough.
- Hidden tab width may be measured to avoid horizontal jump, but
  automatic fit height should use the currently visible tab or sub-tab
  unless a product decision explicitly wants the tallest hidden content
  to reserve vertical space.
- Profile switches, nested tab switches, and detail open/close should
  use the same refit scheduling policy.
- If the first post-render fit is not stable enough, schedule a settled
  refit on a later event-loop turn. Toolkit APIs such as a double
  `after_idle` are implementation examples, not the policy itself.
- Nested tab change events are refit triggers.
- If an interface implementation temporarily selects hidden tabs for
  measurement, suppress tab-change refit callbacks during that
  measurement.
- Geometry measurement and geometry mutation must not run in the same
  synchronous configure path in a way that creates an event loop.
- Preferred-size or refit scheduling behavior should be covered by a
  focused helper/fake-trigger test when possible, so Windows smoke is
  not the first place the scheduling bug appears.

### Hidden-first Window / Dialog Lifecycle

- New windows, dialogs, Toplevels, and comparable shell surfaces should use a
  hidden-first lifecycle where the implementation builds content, lets layout
  settle, takes a visible-content snapshot measurement, applies geometry and
  placement, and only then shows the shell.
- Avoid making users see content build -> measure -> resize for a first show.
- This is different from repeatedly hiding and showing an already-visible
  window. Repeated withdraw/deiconify, fixed-size fallbacks, or excessive
  synchronous update calls are local hacks and should not be the first response
  to flicker.
- Content-hugging is appropriate for first show and dialog open, but repeated
  content-hugging during visible profile/page transitions can create visible
  flicker if content mutation and geometry mutation are not coalesced.
- Close/reopen behavior for stateful input surfaces follows
  `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`; this document owns shell
  geometry/lifecycle, not user input state lifetime.

### Stable-container Profile / Page Switch

- Dynamic profile, page, or screen switches inside an already-visible shell
  should prefer stable containers and cached/reusable pages over repeated
  destroy/create when the content identity is still valid.
- If a page must be rebuilt, group visible mutation so the user sees one
  settled transition rather than intermediate empty, oversized, or partially
  measured states.
- Treat concrete project/screen examples as evidence only; these lifecycle
  rules apply to interface shells regardless of toolkit.

### Saved Geometry Restore

- Restore saved size and position only if the target monitor/work area
  is still available.
- If saved geometry is outside all current visible work areas, recover
  to a safe default placement.
- Do not blindly clamp saved x to the primary display; first identify
  the intended monitor or nearest current work area.

## Multi-monitor, DPI, And Taskbar

- Determine the monitor/work area from the current window handle or
  window position when the interface framework supports it.
- Preserve negative x and x values greater than the primary display
  width when they belong to another monitor.
- Account for taskbars, scaling, title bars, and window borders when
  computing vertical safety.
- Raw screen size is acceptable only as a fallback; it should still
  include a safety margin.

## Scroll Policy

- Root-window horizontal scrolling is not allowed.
- Large tabular or detail content scrolls inside its own viewport.
- Automatic fit may reveal a scrollbar; scrollbar visibility must not
  trigger a geometry loop.
- Detail open should start at a useful scroll position, normally the top
  of the newly opened detail content.

## Manual Resize Policy

- Automatic fit caps are not user resize limits.
- Do not set a hard max window size only to enforce the automatic fit
  policy.
- Users may enlarge the window when they want more content visible.
- Minimum size should protect usability, not force oversized launch.

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
