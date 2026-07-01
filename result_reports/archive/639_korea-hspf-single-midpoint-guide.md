# KOREA HSPF Single UI And Midpoint Guide

## Goal

Implement Slice 3 of the KOREA calculator notebook sub-arc: KS C 9306 HSPF
single calculation UI plus a separate 7°C midpoint guide table.

## Scope

- Added KOREA HSPF application usecase and result DTO wiring.
- Extended midpoint guide helpers with HSPF load-line geometry based on 7°C
  full/half/min inputs.
- Added `KoreaHspfSection` with rated cooling capacity, official HSPF required
  input points, official result panel, and read-only midpoint guide table.
- Wired the HSPF section into the KOREA top-level tab.
- Added focused headless tests for the HSPF usecase and midpoint guide.

## Non-goals

- No KS C 9306 core formula, profile, region config, public result contract,
  fixture, or golden expected changes.
- No batch dialogs or detail view implementation in this slice.
- HSPF defrost and -7°C maximum points are used for official calculation only,
  not for midpoint guide calculation.

## Reference Parity

- Checked Hong Kong HSPF section/usecase patterns for table input, result panel,
  invalid-field handling, and dispatcher boundary.
- Reuse outcome: local KOREA HSPF usecase/section was added because the KS C
  9306 HSPF required input shape differs from Hong Kong HSPF; shared table,
  result, lifecycle, and controller components were reused.

## Verification

- `python3 -B -m pytest -q tests/test_calculator_korea_hspf_usecase.py tests/test_calculator_korea_cspf_usecase.py`:
  OK, 8 passed.
- `python3 -B -m pytest -q tests/test_apps_calculator_ui_korea_tab.py`: weaker
  verified; 2 skipped because Tk could not open in the headless environment.
- `python3 -B -m compileall -q apps/calculator tests`: OK.
- `python3 -B -m pytest -q tests/test_calculator_dispatcher.py tests/test_calculator_profiles.py`:
  OK, 40 passed.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- `python3 -B tools/check_code_structure.py`: OK with 9 pre-existing soft
  warnings outside the changed source files.
- `git diff --check`: OK.

## Structure Warnings

- No changed/new source file emitted a structure warning.
- New source file sizes stayed below the 250 LOC soft planning threshold.
- Existing warnings remain in calculator core/EN14825/batch hotspot files and
  were not part of this slice.

## change_gate

- owner_boundary: `apps/calculator/application/korea/hspf_usecase.py` owns HSPF
  orchestration; `apps/calculator/ui/sections/korea_hspf_section.py` owns HSPF
  widget composition and event forwarding.
- reuse_commonization: `local-with-reason`; KOREA HSPF has a distinct KS C
  9306 input envelope, while shared UI components were reused.
- code_map_check: `regenerated`; `docs/code_map/CODEBASE_REFERENCE_MAP.md` is
  included in the diff.

## Known Risks

- Tk widget construction assertions were skipped due the headless environment.
- The HSPF midpoint guide intentionally excludes defrost and -7°C maximum
  points; those remain official calculation inputs only.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: not run; push is reserved for final Slice 6 closeout.
