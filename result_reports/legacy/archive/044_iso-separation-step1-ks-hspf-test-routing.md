# 044_iso-separation-step1-ks-hspf-test-routing

## Goal
- `iso_seperation_plan.md` Step 1 범위에서 KS C 9306 HSPF 테스트가 ISO calculator의 KS delegation을 통하지 않고 `KSC9306Calculator`를 직접 사용하도록 retarget한다.
- KS standalone module 설명에서 Step 1 기준으로 낡은 transitional 표현만 정리한다.

## Scope
- `core/calculator_ks_c9306.py`
  - class docstring의 delegation 중심 표현을 KS module 책임 중심으로 정리.
  - `from_iso_calculator` compatibility factory는 Step 2 전까지 유지한다고 명시.
- `tests/test_iso16358_hspf_ks_oracle.py`
  - KS row는 `KSC9306Calculator`, ISO common row는 `ISO16358Calculator`로 계산하도록 분리.
- `tests/test_iso16358_hspf_validation.py`
  - KS validation tests와 KS config helper를 `KSC9306Calculator`로 retarget.
  - ISO common validation helper는 `ISO16358Calculator` 유지.
- `tests/test_iso16358_hspf_golden.py`
  - phase1 config 생성 helper를 분리하고 `make_ks_phase1_calculator()` 추가.
  - KS golden/helper tests는 KS calculator로 retarget.
  - ISO common golden tests는 ISO calculator 유지.
- `project_log.md`
  - Step 1 routing 결과와 후속 Step 2 경계 기록.

## Non-goals
- `core/calculator_iso16358.py` rename 또는 legacy 이동 없음.
- UI import 변경 없음.
- `from_iso_calculator` / `_iso_calculator_ref` 제거 없음.
- region config, workbook/reference files, golden expected, tolerance, xfail marker 수정 없음.
- ISO HSPF common failures 수정 없음.

## Verification
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py tests/test_iso16358_hspf_ks_oracle.py tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_golden.py` → 통과.
- `python3 -B -m pytest tests/test_iso16358_hspf_ks_oracle.py -q` → `2 passed`.
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py -q -k ks_c9306` → `26 passed, 9 deselected`.
- `python3 -B -m pytest tests/test_iso16358_hspf_golden.py -q -k ks_c9306` → `8 passed, 24 deselected`.
- Combined targeted baseline:
  - Before edit: `11 failed, 51 passed, 7 xfailed`.
  - After edit: `11 failed, 51 passed, 7 xfailed`.
  - Failure set remains ISO common HSPF golden/diagnostic pre-existing failures.

## Task Results
- `tests/test_iso16358_hspf_ks_oracle.py`
  - Added `KSC9306Calculator` import.
  - Replaced direct KS helper calls on ISO instance with `ks_calc._ks_hspf_bin(...)`.
  - Kept `_variable_heating_bin(...)` on ISO instance so the test still compares KS path against ISO common formula behavior.
- `tests/test_iso16358_hspf_validation.py`
  - Added `KSC9306Calculator` import.
  - `make_ks_config_calculator(...)` now returns `KSC9306Calculator.from_config_path(...)`.
  - KS validation tests now use `make_ks_phase1_calculator(...)`.
  - `make_iso_common_calculator(...)` and ISO common tests remain on `ISO16358Calculator`.
- `tests/test_iso16358_hspf_golden.py`
  - Split config creation into `make_phase1_config_path(...)`.
  - Kept `make_phase1_calculator(...)` for ISO callers.
  - Added `make_ks_phase1_calculator(...)` for KS callers.
  - Retargeted KS golden/helper tests to KS calculator.
- `core/calculator_ks_c9306.py`
  - Updated class docstring to describe KS C 9306 helper ownership in this module.
  - Recorded that `from_iso_calculator` compatibility remains until Step 2 legacy rename.
- `project_log.md`
  - Added "ISO separation Step 1 KS HSPF test routing" follow-up entry.

## Changed Files
- `core/calculator_ks_c9306.py`
- `tests/test_iso16358_hspf_ks_oracle.py`
- `tests/test_iso16358_hspf_validation.py`
- `tests/test_iso16358_hspf_golden.py`
- `project_log.md`
- `result_reports/active/044_iso-separation-step1-ks-hspf-test-routing.md`

## Known Failures / Risks
- `tests/test_iso16358_hspf_validation.py` still has one ISO common frost-boundary failure in full-file mode. It existed before this change and was not modified.
- `tests/test_iso16358_hspf_golden.py` still has ten ISO common golden/diagnostic failures in full-file mode. They existed before this change and were not modified.
- Step 2 remains required to rename `core/calculator_iso16358.py` to legacy, add a new ISO skeleton, retarget legacy tests, move diagnostic/mixed tests to `tests/_legacy/`, and then remove KS factory dead code.

## Commit / Push
- source commit: `fae66dc test: route KS HSPF checks to KS calculator`
- source push: `origin/work/iso-separation-plan`
- report commit: pending at report creation time.
