# 190-b SASO T3 Tkinter Implementation

## Background

190-a/190-a2 chose Candidate A: add `SASO T3` as a dedicated Tkinter ISO section using the existing `saso_t3_cspf` profile/config path. The result display is a section-local scenario comparison, not a shared `ResultPanel` change.

## Modified / New Files

- `ui_tk/profile_resolver.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/sections/iso_saso_t3_section.py`
- `ui_tk/sections/iso_saso_t3_result_table.py`
- `tests/test_ui_tk_profile_resolver.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`

## Implementation

- Added `SASO T3` as the third ISO profile selector label after `ISO / ISEER 2-point` and `Hong Kong`.
- Added `IsoSasoT3Section` with `MetricInputTable`, `ExcelLikeTableController`, and `DebouncedAutoCalc`.
- Required columns: `46 Full`, `35 Full`, `35 Half`.
- Optional column: `35 Min`.
- Added `35 Min optional test 사용` toggle.
- Toggle off disables/ignores 35 Min and renders only the required-only 3-point result.
- Toggle on with valid 35 Min renders both `Required only (3-point)` and `With 35 Min (4-point)`.
- Toggle on with invalid 35 Min keeps the 3-point row when required inputs are valid and renders a safe 4-point error row.
- Required input invalid state clears rows and shows a safe status.

## Calculation

- Both scenarios use `create_calculator_for_profile("saso_t3_cspf")`.
- Required-only calculation applies `calculator.config["cspf_test_profile"]["test_selection"] = "required_only"` on the calculator instance only.
- Optional-min calculation applies `test_selection = "with_optional_test"` on the calculator instance only.
- Production config, profile registry, region config, golden, and fixtures were not modified.

## Verification

- `ps -axo pid,args | rg 'pytest|python3 -B -m pytest|Python -B'`
- `python3 -B tools/check_code_structure.py`
- `python3 -B -m py_compile ...`
- Quick smoke: SASO default render + full app widget tree.
- Final focused pytest: profile resolver, ISO table auto-calc, calculator foundation.
- `git diff --check`
- `git status --short`
- `git diff --name-only`
- `git diff --stat`

## Manual Check Needed

- App opens with `ISO / ISEER 2-point` default.
- `SASO T3` selector renders the SASO section.
- Optional 35 Min off shows required-only 3-point result only.
- Optional 35 Min on shows both 3-point and 4-point rows.
- Invalid optional 35 Min shows safe 4-point status without stale success values.
- Switching `ISO / ISEER 2-point` / `Hong Kong` / `SASO T3` keeps existing modes intact.

## Excluded Scope

- No core calculator changes.
- No `core/calculator_profiles.py` changes.
- No `data/region_configs/*.json` changes.
- No golden/fixture changes.
- No PyQt changes.
- No `ResultPanel` shared comparison mode.
- No generic section framework extraction.
- No SASO multi/batch/detail/graph.

## Next Action

Manual smoke for 190-b, then choose the next Design First Gate slice.
