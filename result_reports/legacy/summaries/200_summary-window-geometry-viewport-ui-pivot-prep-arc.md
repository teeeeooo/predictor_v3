# 200 Summary - Window Geometry, Viewport, and UI Pivot Prep Arc

## Arc Purpose

- Close the Tkinter calculator polish arc that followed ISO detail graph/copy work.
- Stabilize input-table typing, multi-monitor window geometry, launch/detail auto-fit, and viewport policy before the UI technology pivot design gate.
- Reduce active reports so the next worker sees the current decision target instead of completed hotfix history.

## Starting State

- Graph min/max scale labels needed Windows confirmation after the 196-a hotfix.
- Metric input table single-click typing appended/prepended to existing values instead of replacing them.
- Detail open/profile fit could move a window from monitor 2 back to monitor 1.
- First launch and detail-open auto-fit could create oversized or clipped windows.
- Window geometry decisions were implemented in Tkinter but not yet captured as toolkit-neutral UX policy.

## Completed Work

- 196-a graph min/max scale label manual smoke passed on Windows dual-monitor setup.
- 197-a attempted MetricInputTable replace-on-type; Windows manual smoke showed it still prepended/appended.
- 197-a2 fixed replace-on-type robustly by making selection-mode Entry text actually selected, so first typing replaces the existing value. Windows manual smoke passed.
- 197-b split initial launch geometry from profile/detail fit:
  - `initial_window_geometry()` remains initial-launch centered placement.
  - profile/detail fit preserves current x/y and current monitor while applying shared size caps.
  - negative and monitor2-like x coordinates remain valid and are not primary-clamped.
- 198-a added one-shot first-launch ISO fit after idle and made SASO T3 use 4-point as default while still showing 3-point required-only comparison. Windows manual smoke passed.
- 198-b/198-d refined vertical-only detail/profile clamps so x/current monitor are preserved while y is adjusted to reduce lower clipping.
- 198-c lowered automatic fit max height to about 80% of display height and kept manual user resizing unrestricted. Windows manual smoke accepted the 80% cap.
- 199-a added top-safe y placement for large detail-like surfaces while preserving x/current monitor. Windows manual smoke passed.
- 199-b created the toolkit-neutral viewport owner document: `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`.
- 199-c fixed UI/UX document numbering by renaming the window geometry policy from duplicate `05_` to `07_`.

## Windows Manual Smoke Result

- Simple movement between monitors did not reproduce clipping.
- Monitor 2 detail open/close no longer jumps back to monitor 1.
- Profile changes preserve current monitor/location.
- First launch ISO size is normal and not clipped.
- Detail open does not clip at the lower edge after the 80% cap plus top-safe y policy.
- User manual window resizing remains available.
- ISO/ISEER, SASO T3, Hong Kong CSPF detail, CSV/copy, and graph behavior remained intact.
- SASO T3 opens as 4-point default, shows 4-point and 3-point comparison rows, and exposes both detail sources.

## Final Policy State

- Initial launch, profile/content switch, detail open/close, and saved geometry restore are separate placement modes.
- Automatic fit uses viewport/work-area caps; it should not impose a hard `MaxHeight` that blocks manual resizing.
- Large detail surfaces prefer top-safe y placement.
- Profile/detail auto-fit preserves current x/current monitor and avoids primary monitor recenter.
- Raw screen height is not treated as the reliable visible work area because of taskbar, DPI scaling, and window chrome.
- Overflow belongs inside predictable scroll surfaces.

## Packaging Note

- Windows `calculator_tk` packaged size was measured at approximately 11 MB.
- This is acceptable for the current lightweight calculator deployment candidate.

## Remaining Decisions

- Next action: UI technology pivot design gate.
- Decide whether the next calculator shell direction is C# WPF with a reusable grid or another UI strategy before implementation.
- Hong Kong HSPF heating trace schema/implementation remains a separate future decision.
- Graph export/HTML export remains deferred until graph parity/readability is stable.

## Covered Active Reports

- `196a_graph-min-max-scale-label-hotfix.md`
- `197a_input-table-replace-on-type-hotfix.md`
- `197a2_input-table-replace-on-type-windows-followup.md`
- `197b_multi-monitor-geometry-role-split-hotfix.md`
- `198a_tkinter-launch-fit-saso-default-router-output-budget.md`
- `198b_detail-open-vertical-clamp-hotfix.md`
- `198c_auto-fit-height-cap-packaging-closeout.md`
- `198d_detail-open-vertical-clamp-bottom-margin-hotfix.md`
- `199a_window-geometry-top-safe-cleanup.md`
- `199b_window-geometry-viewport-policy.md`
- `199c_ui-ux-doc-numbering-cleanup.md`

## Project Memory Seed Sync Judgment

- Update the previous open multi-monitor geometry clipping seed entry to resolved/superseded.
- Add one compact decision entry for the final viewport/window geometry policy and next UI pivot gate state.
