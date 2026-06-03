# 07. Window Geometry And Viewport Policy

## Purpose

This document defines the toolkit-agnostic UX contract for window
placement, automatic sizing, viewport limits, scrolling, and
multi-monitor behavior.

It records the lessons from the Tkinter calculator geometry work as a
general UI policy, not as a Tkinter implementation guide.

## Scope

This policy applies to:

- the current Tkinter calculator;
- future C# WPF shells;
- PySide/PyQt reference UI surfaces;
- Web UI by analogy, as browser viewport and scroll behavior policy.

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

### Saved Geometry Restore

- Restore saved size and position only if the target monitor/work area
  is still available.
- If saved geometry is outside all current visible work areas, recover
  to a safe default placement.
- Do not blindly clamp saved x to the primary display; first identify
  the intended monitor or nearest current work area.

## Multi-monitor, DPI, And Taskbar

- Determine the monitor/work area from the current window handle or
  window position when the toolkit supports it.
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

## WPF Implementation Guide

- Do not rely only on `WindowStartupLocation="CenterScreen"`.
- Do not keep `SizeToContent` enabled while dynamic detail surfaces are
  opened and closed.
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
- Tables, copy/export, graph/detail content, and calculation behavior
  do not change as a side effect of geometry policy.
