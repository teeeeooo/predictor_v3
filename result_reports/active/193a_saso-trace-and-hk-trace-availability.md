# 193-a SASO Trace And Hong Kong Trace Availability

## Goal

Reuse the 192-d `BinTraceTable` pattern for a narrow SASO T3 trace table slice and audit Hong Kong CSPF/HSPF trace availability without implementing Hong Kong trace UI.

## Scope

- Corrected 192-d closeout pending wording.
- Added SASO T3 `bin_details` retention and collapsed trace UI.
- Added focused SASO trace lifecycle tests.
- Audited Hong Kong CSPF/HSPF result shape and likely implementation owner.

## Non-goals

- No CSV export, graph, graph export, or internal formula trace.
- No Hong Kong trace implementation.
- No new trace framework.
- No `ResultSnapshot`, `DetailResultTable`, or input-point detail table.
- No core calculator, profile registry, region config, golden, fixture, PyQt source, `ResultPanel`, `window_geometry.py`, `ScrollableFrame`, or `profile_resolver` change.

## Task Results

- task 1: OK - `192d_iso-iseer-bin-details-trace-table-parity.md` now records closeout commit `45da308 192-d: close out bin trace manual smoke` and push completed status.
- task 2: OK - SASO `calculate_cspf()` required-only and optional-min paths return `bin_details`; `BinTraceTable` schema matches the CSPF bin keys.
- task 3: OK - `IsoSasoT3Section` retains only trace `bin_details` in section-local state:
  - `Required only (3-point)` is retained after required-only success.
  - `With 35 Min (4-point)` is retained only when optional 35 Min is enabled and valid.
  - invalid required input clears all trace state.
  - invalid optional input preserves required trace and leaves optional trace unavailable.
- task 4: OK - SASO `Bin trace` control is collapsed by default, uses the existing `BinTraceTable`, and calls tab-owned one-shot fit through the existing narrow callback.
- task 5: OK - recalculation replaces trace state, invalid input clears or safely reports unavailable trace, toggle off removes optional trace, and profile switching with expanded trace is lifecycle-safe in tests.
- task 6: OK - Hong Kong audit only:
  - CSPF raw result contains CSPF-style `bin_details` with `bin_no`, `tj`, `nj`, `lc`, `capacity`, `power`, `eer`, `cstl_bin`, `csec_bin`; this can reuse `BinTraceTable`.
  - HSPF raw result contains heating `bin_details`, but the keys are heating-specific (`bl_h`, `P_j`, `case`, `heat_pump_energy`, `auxiliary_energy`, `E_j`, etc.) and do not match `BinTraceTable`.
  - Hong Kong owner should be section-local for CSPF if implemented; HSPF needs a separate heating trace table/schema decision. The current ResultPanel path can remain untouched for a CSPF-only trace slice.
- task 7: OK - focused tests now cover SASO default collapsed trace, expand/collapse, column parity, required trace rows, optional selector safe status, optional valid trace rows, invalid optional safe status, invalid required stale clear, and profile switch lifecycle.
- task 8: OK - focused verification completed; no lingering pytest process found.
- task 9: OK - this report and WORK_PLAN checkpoint were added compactly.
- task 10: pending at report creation - commit and push will be recorded after commit/push completes.

## Changed Files

- `result_reports/active/192d_iso-iseer-bin-details-trace-table-parity.md`
- `ui_tk/sections/iso_saso_t3_section.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/193a_saso-trace-and-hk-trace-availability.md`

## Verification

- Process check before verification: no lingering pytest process; only the check command and `rg` matched.
- `python3 -B tools/check_code_structure.py`: OK.
- `python3 -B -m py_compile ui_tk/sections/iso_saso_t3_section.py ui_tk/tabs/iso16358_tab.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py`: OK.
- Quick smoke: `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_saso_t3_bin_trace_expands_with_required_bin_details tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs`: 2 passed.
- Final focused: `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs`: 57 passed.
- Process check after final focused: no lingering pytest process; only the check command and `rg` matched.
- `git diff --check`: clean.

## Manual Check Needed

- Manual smoke is still needed for SASO trace expand/collapse, required/optional selector behavior, invalid optional status, invalid required clear, and profile switching.

## Known Risks

- SASO trace uses the existing CSPF bin table columns. This is intentional for this slice and does not cover internal formula trace.
- Hong Kong HSPF trace needs a separate heating trace schema decision before implementation.

## Next Suggested Action

- Manual smoke for 193-a.
- Then choose one follow-up slice:
  - Table CSV export foundation.
  - Bin graph parity with SPOT-style HTML export.
  - Hong Kong trace implementation based on the audit result.

## Scope Compliance

- No forbidden files were modified.
- No core/config/golden/profile registry changes were made.
- No shared trace framework was introduced.
- No lifecycle summary/archive or `project_log.md` update was performed.

## Commit / Push

- Source/test implementation commit: `ad5ce67 193-a: add SASO bin trace table`
- Docs/report commit: pending at report creation.
- Push: pending at report creation.

## Project Memory Delta

- none
