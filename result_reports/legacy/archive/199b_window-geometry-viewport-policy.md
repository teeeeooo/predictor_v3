# 199-b Window Geometry Viewport Policy

## Goal

- Close out the 199-a Windows manual smoke.
- Document window geometry and viewport policy as a toolkit-neutral UX contract.
- Make the policy reusable for Tkinter, C# WPF, PySide/PyQt, and Web UI viewport work.

## Scope

- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
  - New owner document for window placement, automatic fit, viewport caps, scrolling, multi-monitor/DPI/taskbar handling, saved geometry restore, WPF implementation guidance, and acceptance checklist.
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
  - Adds a short owner reference from layout tokens/screen caps to the new viewport policy.
- `docs/ui_ux/00_UI_UX_SYSTEM.md`
  - Adds the new policy document to the UI/UX SSOT index.
- `result_reports/active/199a_window-geometry-top-safe-cleanup.md`
  - Converts Manual Check Needed to Manual Check Result.
- `docs/WORK_PLAN.md`
  - Moves next action to UI technology pivot design gate.

## Non-goals

- No code changes.
- No `ui_tk/`, C# WPF, PySide/PyQt migration, seasonal detail/trace adapter, router, AGENTS, project log, memory seed, summaries, archive, or lifecycle movement changes.

## Manual Check Result

- User completed Windows local GUI smoke for 199-a.
- First launch size was normal.
- Detail open did not clip at the lower edge.
- Monitor 2 detail open/close preserved location.
- Profile changes preserved location.
- Manual window resizing remained available.
- ISO/SASO/Hong Kong detail, CSV/copy, and graph behavior remained intact.

## Policy Summary

- Initial launch and profile/detail auto-fit are separate placement modes.
- Automatic fit uses viewport caps; manual user resize is not blocked by the auto-fit cap.
- Large detail surfaces prefer top-safe placement.
- Profile/detail changes preserve current x/current monitor and avoid primary monitor recenter.
- Raw screen height is not treated as reliable visible work area because of taskbar, scaling, and window chrome.
- Overflow is handled with internal scroll, and detail open should leave scroll position predictable.

## WPF Reuse Notes

- Do not rely only on `WindowStartupLocation="CenterScreen"`.
- Do not keep `SizeToContent` enabled for dynamic detail surfaces.
- Resolve monitor/work area from the current window handle.
- Apply max auto height only during automatic fit calculations.
- Do not use `Window.MaxHeight` just to enforce an auto-fit cap.
- Use `ScrollViewer` for overflow and centralize placement in a service/helper such as `WindowPlacementService`.

## Verification

- Process check: no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git diff --check`
  - Passed.
- `git status --short`, `git diff --name-only`, `git diff --stat`
  - Confirmed docs/report-only changes.
- Pytest was not run because this was docs-only.

## Project Memory Delta

- none
