# 051 ISO Separation Step 5 Profile Dispatcher UI

## Goal

`iso_seperation_plan.md` Step 5 범위에서 새 ISO/ASNZS calculator series를 profile/dispatcher/UI 생성 경로에 연결한다.

## Scope

- ISO CSPF profiles 4개를 `core/calculator_profiles.py`에 등록했다.
- `asnzs_excel_hspf_compat` profile을 `enabled=False`로 등록했다.
- `core/calculator_dispatcher.py`에 `iso16358`와 `asnzs_excel_hspf` calculator id mapping을 추가했다.
- `ui/calculators_2point.py`의 legacy ISO direct import/instantiation을 dispatcher profile lookup으로 교체했다.
- profile/dispatcher tests를 확장했다.

## Modified Files

- `core/calculator_profiles.py`
- `core/calculator_dispatcher.py`
- `ui/calculators_2point.py`
- `tests/test_calculator_profiles.py`
- `tests/test_calculator_dispatcher.py`
- `project_brief.md`
- `project_log.md`

## Verification

- `python3 -B -m py_compile core/calculator_profiles.py core/calculator_dispatcher.py ui/calculators_2point.py` passed.
- `python3 -B -m pytest tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q`
  - Result: `30 passed`.
- `rg -n "calculator_iso16358_legacy|from core\\.calculator_iso16358_legacy import ISO16358Calculator|import core\\.calculator_iso16358_legacy as iso" ui core tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py tests/test_asnzs_hspf_excel_compat_*.py` returned no matches.
- `python3 -B -m pytest tests -q`
  - Result: `280 passed, 16 failed, 13 xfailed`.
  - The 16 failures remain the known ISO HSPF baseline group.

## Remaining Risk

- UI was verified by compile/import-level checks only; no interactive Qt smoke was run.
- AS/NZS compatibility profile remains disabled until explicit exposure criteria are decided.
