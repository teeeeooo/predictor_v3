# 123 — Summary: Calculator Tkinter Quality + Xfail Audit

## Summary Scope

Active reports 115-122. Workstream: Calculator helper extraction, calculator-only deployment pivot, Tkinter MVP spike/audit/reset/manual smoke, project-wide code quality guard, legacy/unused script audit, and xfail retirement audit.

This lifecycle maintenance creates one summary and archives the covered active reports. It does not create a new `result_reports/active/123_*.md` report.

## Covered Reports

- `115_calculator-errors-helper-extraction.md`
- `116_lightweight-calculator-ui-feasibility-pivot.md`
- `117_tkinter-calculator-mvp-structure-audit.md`
- `118_tkinter-calculator-clean-foundation-reset.md`
- `119_project-wide-code-quality-gate.md`
- `120_tkinter-manual-smoke-checklist.md`
- `121_legacy-unused-script-cleanup-audit.md`
- `122_xfail-retirement-audit.md`

## Key Decisions

- Calculator error/shared validation helpers moved from `ui/calc_window.py` into `ui/calculator_errors.py` (115). Public helper surface: `InputValidationError`, `parse_number`, `bind_error_reset`, `apply_error_style`, `clear_error_style`, `get_float_val`.
- PyQt calculator deployment direction is on hold for calculator-only packaging while lightweight Tkinter feasibility is evaluated (116).
- Tkinter calculator-only direction went through spike -> structure audit -> clean foundation reset (116-118). The 116 single-file spike was explicitly not accepted as the lasting structure.
- `ui_tk/calculator_app.py` was reduced to a shell, with resolver/result/input/tabs/sections separated into focused modules (118).
- Project-wide New Code Quality Gate and `tools/check_code_structure.py` were introduced to prevent new multi-responsibility files across UI, core, tools, scripts, and ML-adapter work (119).
- Legacy/unused script audit found no immediate delete/move/rename candidate (121).
- Xfail audit found no stale marker-only removal candidate under targeted `--runxfail` (122).

## Completed Work

- Extracted calculator validation/error helper module and tests (115).
- Added lightweight calculator UI feasibility design and packaging measurement guide; PyInstaller size remains not measured (116).
- Added initial Tkinter MVP skeleton and then audited its single-file growth risk (116-117).
- Replaced the Tkinter spike structure with a clean module foundation:
  - `app_calculator_tk.py` thin entrypoint.
  - `ui_tk/calculator_app.py` shell.
  - `ui_tk/profile_resolver.py` pure resolver.
  - `ui_tk/result_panel.py`, `ui_tk/input_widgets.py`.
  - `ui_tk/tabs/iso16358_tab.py`.
  - `ui_tk/sections/iso_cspf_section.py`, `ui_tk/sections/iso_hspf_section.py`.
- Added tests for the Tkinter profile resolver and foundation smoke (118).
- Added project-wide code structure guard and 20 guard tests (119).
- Added macOS Tkinter manual smoke checklist with Hong Kong CSPF/HSPF expected values and PyQt environment separation (120).
- Completed read-only legacy/unused script inventory (121).
- Completed xfail inventory and targeted `--runxfail` audit (122).

## Remaining Work

- Windows PyInstaller size measurement remains pending until a Windows host is available.
- Tkinter MVP still needs manual smoke execution using `docs/guides/lightweight_calculator_tk_manual_smoke.md`.
- PyQt calculator UI slices ζ/η/β/γ/δ and Hong Kong HSPF PyQt UI surface remain on hold until deployment direction is decided.
- ISO section input-dict construction and result formatting can be split into pure helpers later, but this is not part of lifecycle maintenance.
- Legacy/unused script cleanup follow-up remains split into small docs/audit slices; no cleanup was executed in 121.
- Xfail cleanup remains future work; no marker, expected, fixture, assertion, or core change was made in 122 or this lifecycle task.

## Architecture / Quality Gate Decisions

- New code quality gate applies project-wide, not just UI:
  - `app_*.py` entrypoints stay thin.
  - shell/orchestration/business logic/data transform/formatting/I/O should not accumulate in one file.
  - hard-coded region/profile/metric/result/default values should live in a resolver, config, registry, constants, or token module.
  - `core/` must not import `ui`, `ui_tk`, `PyQt5`, or `tkinter`.
  - `ui_tk/` must not import PyQt or the PyQt `ui` package.
  - feasibility spikes are not exempt.
- `tools/check_code_structure.py` is conservative and stdlib-only. It checks layer imports, thin app entrypoints, `ui_tk` multi-responsibility patterns, and soft LOC/class limits with historical allowlists.
- Code-structure-impacting work should include `python3 -B tools/check_code_structure.py` in verification. CI/pre-commit integration was not added.

## Xfail / Cleanup Status

- Full-ish baseline excluding the four macOS PyQt fatal-abort files remains `568 passed, 1 skipped, 23 xfailed`.
- `tests/_legacy/` accounts for 17 xfails. These are active diagnostic/reference tests, not immediate deletion candidates.
- AS/NZS case3 accounts for 2 xfails. They depend on external reference/full row data prerequisites.
- ISO pure-route Formula 45/49/47/50 accounts for 4 xfails. Report 122 classified them as active known mismatches, but the latest judgment is that they should be rechecked as **obsolete experiment / retirement candidates** because ISO16358-2 HSPF official exact golden is currently 16/16 pass.
- No stale marker-only removal candidate was found by targeted `--runxfail`. Any cleanup must be sliced by risk: obsolete-test retirement, legacy diagnostic reason/owner cleanup, external reference compatibility, PyQt environment handling.

## Active Documents Sync Judgment

- `ACTIVE_DOCUMENTS.md` needed a minimal update because reports 116 and 120 introduced active docs not yet registered:
  - `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`
  - `docs/guides/lightweight_calculator_packaging_check.md`
  - `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- This summary itself is a lifecycle artifact and is not added as an active owner document.

## Project Log Sync Judgment

- `project_log.md` already contained the PyQt deployment hold / Tkinter feasibility pivot and the project-wide New Code Quality Gate.
- A short follow-up entry was still needed for the xfail audit result, ISO pure-route obsolete-candidate judgment, and this 115-122 lifecycle summary.
- Archive movement alone is not logged.

## Archive Candidates

The following covered reports move to `result_reports/archive/` with filenames and numbers unchanged:

- `result_reports/active/115_calculator-errors-helper-extraction.md`
- `result_reports/active/116_lightweight-calculator-ui-feasibility-pivot.md`
- `result_reports/active/117_tkinter-calculator-mvp-structure-audit.md`
- `result_reports/active/118_tkinter-calculator-clean-foundation-reset.md`
- `result_reports/active/119_project-wide-code-quality-gate.md`
- `result_reports/active/120_tkinter-manual-smoke-checklist.md`
- `result_reports/active/121_legacy-unused-script-cleanup-audit.md`
- `result_reports/active/122_xfail-retirement-audit.md`

## Active Reports After Maintenance

`result_reports/active/` is empty after moving the covered reports. No active report is intentionally left behind.

## Next Suggested Actions

1. ISO pure-route Formula 45/49/47/50 obsolete test retirement audit/removal slice. Treat these as experiment/guard tests to re-evaluate, not as current ISO HSPF production mismatches.
2. `tests/_legacy` diagnostic xfail reason/owner cleanup. Keep this separate from marker removal and expected/core changes.
3. AS/NZS case3 external reference compatibility decision. Do not fabricate missing full row data.
4. Windows PyInstaller size measurement when a Windows host is available.
5. PyQt fatal-abort environment handling as a separate environment slice.

## Verification

- `git branch --show-current` -> `work/ui-ux-ssot-adoption`.
- Initial working tree was clean.
- Active reports before maintenance: 115-122 (8 files).
- New summary number: 123, computed from current result report max 122.
- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `python3 -B -m pytest tests/test_code_structure_guard.py -q` -> 20 passed.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_calculator_foundation.py -q` -> 15 passed.
