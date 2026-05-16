# 026_separate-ks-c9306-cspf-helper

## Goal
- `core/calculator_iso16358.py`에 잔존하던 KS CSPF intersection helper (`_ks_intersection_power`, 그리고 그 전용 의존성인 `_performance_line`)를 `core/calculator_ks_c9306.py`의 `KSC9306Calculator`로 behavior-preserving하게 이동한다. ISO16358 측에는 기존 `calculate_cspf()` / `_calculate_cspf_profile()` 호출 경로를 보호하기 위한 thin delegating wrapper만 남긴다.

## Scope
- `KSC9306Calculator`에 KS CSPF 전용 helper 두 개를 추가했다.
  - `_ks_cspf_performance_line(resolved_points, load_type)`
  - `_ks_cspf_intersection_power(tj, L_c_ref, resolved_points, lower_type, upper_type, t_100_load, t_0_load)`
- `t_100_load`, `t_0_load`는 ISO 계산기 상태를 직접 참조하지 않도록 명시적 인자로 받게 만들었다. KS calculator는 다른 ISO 상태에 의존하지 않는다.
- `ISO16358Calculator._ks_intersection_power(...)`는 동일 시그니처를 유지하되 본문을 `self._ks_calculator()._ks_cspf_intersection_power(...)` 위임으로 교체했다.
- `ISO16358Calculator._performance_line(...)`은 ISO 모듈 안에서 다른 호출자가 없고 외부(tests/UI/scripts/profile resolver)에서도 호출되지 않음을 확인한 뒤 ISO에서 제거했다. 동일 본문은 KS 모듈의 `_ks_cspf_performance_line`으로 이동했다.
- `_round_test_value`는 이번 작업 범위에서 제외하고 ISO 모듈에 그대로 두었다.

## Non-goals
- ISO16358 CSPF/HSPF 계산식 수정 금지.
- KS C 9306 HSPF 계산식 수정 금지.
- AS/NZS workbook oracle / `core/calculator_asnzs_hspf_excel.py` 구현 금지.
- profile resolver (`core/calculator_profiles.py`) / UI 수정 금지.
- tests / fixture / xfail / golden / docs 수정 금지.
- 새 테스트 추가 금지.
- `_round_test_value` 이동 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py` → compile OK.
- KS/CSPF keyword 테스트: `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf"` → `79 passed`.
- 전체: `python3 -B -m pytest tests -q` → `258 passed, 16 failed, 13 xfailed`.
- Baseline: 직전 commit (보고 025 직후) 기준 전체 통계 `258 passed, 16 failed, 13 xfailed`와 동일 (실패 set 일치). 본 refactor에 의한 신규 회귀 없음.
- 작업 전 grep 확인: `_ks_intersection_power`와 `_performance_line`은 `tests/`, `ui/`, `scripts/`, `core/calculator_profiles.py` 어디에서도 직접 호출되지 않는다.

## Task Results
### task 1 결과
- `_ks_intersection_power` 호출부: `core/calculator_iso16358.py` 두 군데
  - `_calculate_cspf_profile`의 intermediate-interpolation regime (`ks_intersection` config flag 분기, 원본 라인 2130).
  - `calculate_cspf`의 piecewise intermediate regime (`ks_intersection` config flag 분기, 원본 라인 2308).
  - 두 호출부 모두 시그니처 동일: `self._ks_intersection_power(tj, L_c_ref, resolved_points, lower_type, upper_type)`.
- `_performance_line` 호출부: `_ks_intersection_power` 내부의 `lower_line`, `upper_line` 두 번 호출만 존재. 그 외 ISO/tests/UI/scripts/profile resolver 어디에서도 호출되지 않음.
- `_ks_intersection_power`가 필요로 하는 입력 값:
  - 인자: `tj`, `L_c_ref`, `resolved_points`, `lower_type`, `upper_type`.
  - ISO 인스턴스 상태: `self.t_100_load`, `self.t_0_load`.
  - 내부 dependency: `_performance_line(resolved_points, load_type)`.
- 분리 가능 조건 정리:
  - KS calculator가 `t_100_load`, `t_0_load`를 인자로 받으면 ISO 상태 의존성 없이 동일 계산 가능.
  - `_performance_line`은 ISO 다른 경로에서 사용되지 않으므로 KS 모듈로 이동 가능.

### task 2 결과
- `core/calculator_ks_c9306.py`의 KS HSPF block 앞쪽에 KS CSPF 헤더 섹션을 추가하고 두 helper를 정의했다.
  - `_ks_cspf_performance_line(self, resolved_points, load_type)` — 본문은 ISO에서 그대로 옮겼다.
  - `_ks_cspf_intersection_power(self, tj, L_c_ref, resolved_points, lower_type, upper_type, t_100_load, t_0_load)` — 본문은 ISO에서 그대로 옮기되, `self.t_100_load`/`self.t_0_load` 참조를 인자 `t_100_load`/`t_0_load`로 교체했다.
- `_ks_cspf_intersection_power`는 내부에서 `self._ks_cspf_performance_line(...)`을 호출하여 ISO 인스턴스 상태와 분리된 채 동작한다.
- 계산식, 분기 조건, return 형식은 변경하지 않았다.

### task 3 결과
- `core/calculator_iso16358.py`의 `_ks_intersection_power(...)` 본문을 `return self._ks_calculator()._ks_cspf_intersection_power(tj, L_c_ref, resolved_points, lower_type, upper_type, self.t_100_load, self.t_0_load)` thin delegation으로 교체했다. 메서드 이름과 시그니처는 유지했다.
- `_performance_line(...)`은 ISO 내·외 직접 호출자가 없음을 확인한 뒤 ISO 모듈에서 제거했다.
- `calculate_cspf()`와 `_calculate_cspf_profile()`의 호출부는 그대로 두었다. 두 곳 모두 ISO 측 thin wrapper `_ks_intersection_power(...)`를 호출하는 형태를 유지한다.
- profile resolver, UI, tests, fixtures는 수정하지 않았다.

### task 4 결과
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py` → 정상 통과.
- KS/CSPF keyword tests: `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf"` → `79 passed`.
- 전체: `python3 -B -m pytest tests -q` → `258 passed, 16 failed, 13 xfailed`.
- Baseline 비교: 보고 025 직후 전체 통계 `258 passed, 16 failed, 13 xfailed`와 동일. 실패 항목도 동일 set이며 모두 pre-existing known failures (ISO common formula50 frost branch, pure ISO track A min-to-half, case 3 Excel BM/BO/CD/Y_MIN_Y_EXTD trace, half-to-full, tiny-bin accumulation 등). 이번 refactor로 인한 신규 회귀는 없다.
- 어떤 test, fixture, expected, tolerance, xfail/pass 토글도 수정하지 않았다.

### task 5 결과
- 새 KS 모듈로 이동한 KS CSPF helper:
  - `_ks_cspf_performance_line(resolved_points, load_type)`
  - `_ks_cspf_intersection_power(tj, L_c_ref, resolved_points, lower_type, upper_type, t_100_load, t_0_load)`
- `calculator_iso16358.py`에 남긴 wrapper/delegation:
  - `_ks_intersection_power(self, tj, L_c_ref, resolved_points, lower_type, upper_type)` — 동일 시그니처 thin wrapper. 호출 경로는 `_ks_calculator()._ks_cspf_intersection_power(...)`이며 `t_100_load`/`t_0_load`를 ISO 인스턴스 상태에서 명시적으로 전달한다.
- `_performance_line` 처리 방식: ISO 모듈 외부 호출자가 없음을 grep으로 확인한 뒤 ISO 모듈에서 제거했다. KS 모듈에 동일 본문이 `_ks_cspf_performance_line`으로 존재한다.
- `_round_test_value` 유지 여부: 이동하지 않고 ISO 모듈에 그대로 두었다 (CSPF/HSPF 공통 전처리 `_prepare_measured_inputs`가 호출함).
- ISO16358 CSPF/HSPF path 영향 여부: 계산식, 분기, 결과 dict 구성 모두 변경 없음. ISO CSPF 메서드 안의 `ks_intersection` 분기는 동일 wrapper 호출 형태를 유지한다.
- KS C 9306 HSPF path 영향 여부: 본 작업에서 수정하지 않았다 (HSPF block 위쪽에 CSPF helper section을 추가한 것 외 변경 없음).
- public API 변화 여부: `ISO16358Calculator` 및 `KSC9306Calculator`의 public 메서드 시그니처에 변화 없다. `ISO16358Calculator`에서 private `_performance_line`이 제거되었지만 외부 사용처가 없으므로 영향 없다.
- result schema 변화 여부: `calculate_cspf()`가 반환하는 dict 구성 변화 없음.
- 후속 정리 필요 여부:
  - ISO16358 측 KS thin wrappers (`_ks_intersection_power`, KS HSPF 24개)는 KS calculator dispatch 라우팅이 `core/calculator_profiles.py`에 정식 등록되고 호출자가 `KSC9306Calculator`를 직접 쓰도록 이행된 뒤 최종 제거할 수 있다.
  - `_round_test_value`는 CSPF/HSPF 공통 전처리에서 사용되므로 분리 시 `_prepare_measured_inputs` 자체의 분리 전략을 함께 검토해야 한다.
  - ISO `calculate_cspf` / `_calculate_cspf_profile`의 `power_interpolation_method == "ks_intersection"` 인라인 분기는 향후 KS CSPF가 별도 calculator entry point를 가질 때 strategy 위임으로 정리 가능.

### task 6 결과
- `git status` / `git diff --stat`으로 변경 범위가 `core/calculator_iso16358.py` + `core/calculator_ks_c9306.py`로 한정됨을 확인했다.
- `py_compile` 통과 후 source commit: `refactor: move KS C9306 CSPF helper` (hash `b73ffa9`).
- 본 report 파일을 `result_reports/active/026_separate-ks-c9306-cspf-helper.md`로 생성했다.
- report commit: `report: record KS C9306 CSPF helper separation` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf"` → `79 passed`.
- `python3 -B -m pytest tests -q` → `258 passed, 16 failed, 13 xfailed`.
- Baseline (보고 025 직후 main HEAD) → `258 passed, 16 failed, 13 xfailed` — 동일 통계, 동일 실패 set, 회귀 없음.

## Changed Files
- `core/calculator_ks_c9306.py` (KS CSPF helper 2개 추가)
- `core/calculator_iso16358.py` (`_performance_line` 제거, `_ks_intersection_power` → thin wrapper)
- `result_reports/active/026_separate-ks-c9306-cspf-helper.md`

## Known Failures / Risks
- 16개 pre-existing test failures는 main HEAD에도 동일하게 존재하며 본 refactor와 무관하다. 모두 ISO common HSPF formula 47/50 / case 3 Excel trace / pure ISO track A 관련 known mismatch이다.
- ISO `_ks_intersection_power` thin wrapper는 매 호출마다 `KSC9306Calculator.from_iso_calculator(self)` 인스턴스를 새로 만든다. config 참조만 빌리는 경량 객체라 성능 영향은 미미하지만, CSPF bin loop에서 다회 호출되므로 추후 캐시 또는 wrapper 제거 시 정리할 수 있다.
- `_round_test_value`는 여전히 ISO 모듈에 남아 있어 KS naming이 일부 ISO 측에 섞여 있다. CSPF/HSPF 전처리 동작과 분리되어 있지 않으므로 이번 단계에서는 그대로 둔다.

## Next Suggested Action
- ISO16358 측 KS thin wrappers (HSPF 24개 + CSPF 1개) 제거를 위해 `core/calculator_profiles.py`에 `calculator_id=ks_c9306` profile record를 추가하고, dispatch 경로(`calculate_cspf` / `calculate_hspf`)가 KS profile일 때 `KSC9306Calculator`를 직접 호출하도록 전환하는 후속 작업.

## Scope Compliance
- ISO16358 CSPF/HSPF path: 계산식 수정 없음 (CSPF는 thin wrapper만 갱신, HSPF는 unchanged).
- KS C 9306 HSPF path: 수정 없음 (CSPF helper section만 모듈 상단에 추가).
- KS C 9306 CSPF helper: `_ks_cspf_performance_line`, `_ks_cspf_intersection_power`로 분리됨.
- AS/NZS compatibility: 구현하지 않았음.
- tests/fixtures/expected: 수정하지 않았음.
- docs: 수정하지 않았음.
- UI: 수정하지 않았음.
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 그대로).
- workbook/reference_files: 수정하지 않았음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- source commit: `b73ffa9 refactor: move KS C9306 CSPF helper`
- report commit: `report: record KS C9306 CSPF helper separation`
- pushed branch: `origin/main`
