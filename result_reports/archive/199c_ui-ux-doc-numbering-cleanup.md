# 199-c UI/UX Doc Numbering Cleanup

## Goal

- Resolve the duplicate `05_` prefix in the UI/UX SSOT document set.
- Keep the window geometry / viewport policy content unchanged except for document number, title, and references.

## Scope

- `docs/ui_ux/05_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` -> `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
  - Renamed title to `# 07. Window Geometry And Viewport Policy`.
- `docs/ui_ux/00_UI_UX_SYSTEM.md`
  - Updated the policy reference and kept `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` intact.
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
  - Updated the viewport policy owner reference.
- `result_reports/active/199b_window-geometry-viewport-policy.md`
  - Updated the created policy path in scope.
- `docs/WORK_PLAN.md`
  - Added a compact checkpoint for the numbering cleanup.

## Verification

- Process check found no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- Reference check confirmed no remaining `05_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` reference in the checked UI/UX, work plan, and 199-b report scope.
- `git diff --check`
  - Passed.
- `git status --short`, `git diff --name-only`, `git diff --stat`
  - Confirmed docs/report-only changes.
- Pytest was not run because this was docs-only.

## Excluded

- No code changes.
- No `ui_tk/`, C# WPF, PySide/PyQt migration, seasonal detail/trace adapter, router, AGENTS, project log, memory seed, summaries, archive, or lifecycle movement changes.

## Project Memory Delta

- none
