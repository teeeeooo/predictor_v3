# 064 Connect Calculator UI Result Action

## Goal

Give `app_calculator.py` / `ui/calc_window.py` a minimal real calculation interaction path beyond launch smoke.

## Scope

- `ui/calc_window.py`
- `tests/test_app_calculator_ui_smoke.py`

## Non-goals

- No UI redesign.
- No ISO 2-point widget restructuring.
- No AHRI formula or HSPF2 formula changes.
- No calculator result schema or ML adapter implementation.

## Changed Files

- `ui/calc_window.py`
- `tests/test_app_calculator_ui_smoke.py`
- `result_reports/active/064_connect-calculator-ui-result-action.md`

## Verification

- `python3 -B -m py_compile app_calculator.py ui/calc_window.py`
  - passed
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest tests/test_app_calculator_ui_smoke.py tests/test_ahri_seer2_smoke.py -q`
  - `5 passed`
- `rg -n "QPushButton|clicked|result_label|button_calculate|calculate_ahri\\(|setText" ui/calc_window.py tests/test_app_calculator_ui_smoke.py`
  - confirmed button wiring and result label update path.
- `git diff --check`
  - passed.

## Task Results

- Added a common `계산 실행` button to `CalculatorWindow`.
- Connected the button to `on_calculate()`.
- Added a result label and updated it with returned calculation text.
- Preserved existing calculator methods and return strings.
- Added an offscreen AHRI AC smoke test that fills SEER2 inputs, clicks the button, and verifies the result label contains the AHRI SEER2 result text.

## Known Risks

- The smoke covers the AHRI AC path only. HP/HSPF2 UI inputs and EN/ISO manual-result behavior remain separate follow-up coverage.
- Error paths still use modal message boxes as before; this task did not redesign validation UX.

## Commit / Push

- Source commit: `7dbe1d9` (`feat: connect calculator UI result action`).
- Report commit: this commit (`report: record calculator UI result action`).
- Push: deferred until final objective push.
