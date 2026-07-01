# KOREA Midpoint Guide Recommended Capacity Fix

## Goal

Fix KOREA midpoint guide recommended Mid capacity so it reports the rated
test-point Mid capacity input needed to place tc at the recommended midpoint.

## Scope

- Updated CSPF guide output from raw load at recommended tc to the equivalent
  35°C Mid capacity input.
- Updated HSPF guide output from raw load at recommended tc to the equivalent
  7°C Mid capacity input.
- Updated KOREA focused expected values.
- Added a CSPF regression sample matching the checked user example.

## Changed Files

- `apps/calculator/application/korea/midpoint_guide.py`
- `tests/test_calculator_korea_cspf_usecase.py`
- `tests/test_calculator_korea_hspf_usecase.py`
- `result_reports/active/646_korea-midpoint-guide-recommended-capacity-fix.md`

## Verification

- `python3 -B -m pytest -q tests/test_calculator_korea_cspf_usecase.py tests/test_calculator_korea_hspf_usecase.py`:
  OK, 9 passed.
- `python3 -B -m compileall -q apps/calculator tests`: OK.
- `python3 -B -m pytest -q tests/test_calculator_korea_cspf_usecase.py tests/test_calculator_korea_hspf_usecase.py tests/test_calculator_korea_detail_contract.py tests/test_ui_tk_korea_batch_profiles.py tests/test_apps_calculator_ui_korea_tab.py`:
  OK with headless Tk skips, 17 passed and 2 skipped.
- `python3 -B tools/check_code_structure.py`: OK with existing hotspot warnings
  and a code-map freshness reminder.
- `git diff --check`: OK.

## Value Check

- User CSPF sample after fix:
  - `current_tc`: `30.231029`
  - `recommended_tc`: `30.788534`
  - `recommended_mid_capacity`: `3694.6 W`
- Existing CSPF focused sample changed from raw-load `2258 W` to 35°C input
  recommendation `2141 W`.
- Existing HSPF focused sample changed from raw-load `2216 W` to 7°C input
  recommendation `2450 W`.

## Known Risks

- Power inputs remain intentionally ignored in this fix per user direction.
- Code map was not regenerated because this is a formula/test correction with
  no source surface or symbol inventory change.
- Tk visual/manual smoke was not run in the headless environment.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: performed after commit; final remote match is reported in the terminal
  response.
