# KOREA CSPF Single UI And Midpoint Guide

## Goal

Implement Slice 2 of the KOREA calculator notebook sub-arc: KS C 9306 CSPF
single calculation UI plus a separate midpoint guide table.

## Scope

- Added `apps/calculator/application/korea/` for KOREA CSPF application
  orchestration, result DTOs, and UI-neutral midpoint guide calculation.
- Added `KoreaCspfSection` with declared/input tables, official CSPF result
  panel, and a read-only midpoint guide table.
- Wired the CSPF section into the KOREA top-level tab.
- Added focused headless tests for the CSPF usecase and midpoint guide.

## Non-goals

- No KS C 9306 core formula, profile, region config, public result contract,
  fixture, or golden expected changes.
- No KOREA HSPF, batch dialogs, or detail view implementation in this slice.
- Midpoint guide values are not added to the official result dict.

## Reference Parity

- Checked Hong Kong CSPF section/usecase patterns for table input, result panel,
  invalid-field handling, and dispatcher boundary.
- Checked ISO/ISEER 2-point section for table/result idioms.
- Reuse outcome: local KOREA package is used because the feature will expand to
  CSPF/HSPF guide/usecase responsibilities; common UI table/result components
  are reused.

## Verification

- `python3 -B -m pytest -q tests/test_calculator_korea_cspf_usecase.py`: OK,
  4 passed.
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

- owner_boundary: `apps/calculator/application/korea/` owns KOREA application
  DTO/usecase/helper logic; `apps/calculator/ui/sections/korea_cspf_section.py`
  owns CSPF widget composition and event forwarding.
- reuse_commonization: `local-with-reason`; KOREA-specific midpoint guide
  semantics should not be mixed into Hong Kong/ISO sections, while shared
  table/result/lifecycle components were reused.
- code_map_check: `regenerated`; `docs/code_map/CODEBASE_REFERENCE_MAP.md` is
  included in the diff.

## Known Risks

- Tk widget construction assertions were skipped due the headless environment.
- The midpoint guide is an engineering helper based on current input load-line
  geometry, not a KS C 9306 official result or global optimum.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: not run; push is reserved for final Slice 6 closeout.
