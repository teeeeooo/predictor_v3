# 025_separate-ks-c9306-calculator

## Goal
- `core/calculator_iso16358.py` 안에 섞여 있던 KS C 9306 HSPF 전용 로직을 `core/calculator_ks_c9306.py` special calculator (`KSC9306Calculator`)로 behavior-preserving하게 분리하고, ISO16358 모듈은 thin delegating wrapper를 통해 기존 public/private 호출 경로(특히 tests의 `calc._ks_hspf_bin(...)`)를 유지한다.

## Scope
- 새 모듈 `core/calculator_ks_c9306.py`를 생성하고 `KSC9306Calculator` 클래스를 정의했다.
- `ISO16358Calculator`의 KS C 9306 HSPF 전용 helper 24개와 `_calculate_ks_c9306_hspf`, `_has_ks_c9306_hspf_input` 본문을 `KSC9306Calculator`로 옮긴 뒤, ISO16358 측은 동일 시그니처의 thin wrapper로 위임하도록 교체했다.
- ISO16358 측 wrapper는 ISO 계산기에서 이미 로드된 config / bin_hours / Cd 상태를 그대로 공유하는 `KSC9306Calculator.from_iso_calculator(self)` factory를 통해 KS calculator 인스턴스를 만든다.
- 새 KS 모듈에는 `from_config_path(...)`와 `from_iso_calculator(...)` 두 factory, 그리고 `calculate_hspf(...)` 공개 진입점을 추가했다.

## Non-goals
- ISO16358 CSPF / HSPF common path 계산식 수정 금지.
- KS C 9306 CSPF/HSPF 계산식, expected, tolerance 변경 금지.
- AS/NZS workbook oracle / `core/calculator_asnzs_hspf_excel.py` 구현 금지.
- profile resolver (`core/calculator_profiles.py`) / UI 수정 금지.
- tests / fixture / xfail / golden / docs 수정 금지.
- 새 테스트 추가 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py` → compile OK.
- KS keyword 테스트: `python3 -B -m pytest tests -q -k "ks or c9306 or korea"` → `40 passed`.
- 직접 KS internals 호출 테스트: `python3 -B -m pytest tests/test_iso16358_hspf_ks_oracle.py tests/test_iso16358_hspf_validation.py -q` → `36 passed, 1 failed` (실패는 ISO common HSPF formula50 frost branch로 KS와 무관, 후술 Known Failures 참조).
- 전체: `python3 -B -m pytest tests -q` → `258 passed, 16 failed, 13 xfailed`.
- 비교 baseline: 작업 시작 시 main HEAD 상태에서 같은 전체 명령 → `258 passed, 16 failed, 13 xfailed`로 동일. 16 failures는 모두 pre-existing이며 ISO common HSPF / pure ISO track A / case 3 Excel component-sum trace에 관한 known mismatch이다.

## Task Results
### task 1 결과
- `core/calculator_iso16358.py`에서 KS 관련 식별 키워드(`ks_c_9306`, `KS C 9306`, `_ks_`, `_ks_hspf_*`, `_calculate_ks_c9306_hspf`, `round_half_up`, `ks_intersection`)로 범위를 grep했다.
- 분리 대상으로 식별된 KS C 9306 HSPF 전용 로직(원본 라인 683–1358 구간):
  - `_has_ks_c9306_hspf_input`
  - `_ks_hspf_input` / `_ks_hspf_config` / `_ks_hspf_profile_point_path` / `_ks_hspf_required_points`
  - `_validate_ks_hspf_positive_number` / `_validate_ks_c9306_hspf_input`
  - `_ks_hspf_correction` / `_ks_hspf_minus7_factor` / `_ks_hspf_stage_value`
  - `_ks_hspf_linear` / `_ks_hspf_is_frost_region`
  - `_ks_hspf_capacity_curve` / `_ks_hspf_power_curve` / `_ks_hspf_stage_curves`
  - `_ks_hspf_interpolate_power_for_load`
  - `_ks_hspf_load_line` / `_ks_hspf_config_load_line` / `_ks_hspf_bin_load`
  - `_ks_hspf_capacity_line` / `_ks_hspf_intersection_temp` / `_ks_hspf_power_by_intersection`
  - `_ks_hspf_bin`
  - `_calculate_ks_c9306_hspf`
- 유지 대상으로 식별된 항목:
  - `_round_test_value` (line 46): KS C 9306 시험값 정수 반올림용 helper지만 `_prepare_measured_inputs`(CSPF/HSPF 공통 전처리)에서 사용되므로 ISO 모듈에 유지. 단순 ROUND_HALF_UP 헬퍼이며 KS 전용 가정이 없다.
  - `_ks_intersection_power` (line 303): ISO common CSPF 메서드(`calculate_cspf` / `_calculate_cspf_profile`)가 `power_interpolation_method == "ks_intersection"` config flag로 인라인 호출하는 KS-style 보간 helper. 분리 시 ISO CSPF 메서드 구조까지 함께 손대야 하므로 이번 작업에서는 ISO 모듈에 유지하고, KS CSPF 정리 단계에서 후속 처리한다.
- 호출 경로 식별:
  - 메인 dispatch: `calculate_hspf()` 안의 `if self._has_ks_c9306_hspf_input(measured_inputs): return self._calculate_ks_c9306_hspf(...)` 분기.
  - 테스트가 직접 호출: `tests/test_iso16358_hspf_ks_oracle.py`에서 `calc._ks_hspf_bin(tj, load, hours, ks_input)`을 사용. 이 호출을 깨뜨리지 않도록 thin wrapper가 필요했다.

### task 2 결과
- `core/calculator_ks_c9306.py`에 `KSC9306Calculator` 클래스를 생성하고 위 KS 메서드 24개를 동일 시그니처/동일 본문으로 이동했다.
- `__init__(self, config, bin_hours=None, default_cd=0.25)`은 ISO에서 호출되는 의존성을 그대로 받도록 정의했다.
- factory:
  - `from_config_path(config_path)`: KS-only 사용자가 향후 단독 인스턴스화할 수 있도록 추가 (현재 dispatch 경로에서는 사용하지 않음).
  - `from_iso_calculator(iso_calculator)`: ISO16358Calculator 인스턴스에서 config/bin_hours/Cd만 빌려오는 lightweight 생성자. 이번 작업의 ISO→KS delegation 경로에서 사용한다.
- 공개 진입점 `calculate_hspf(measured_inputs, aux_cop=1.0)`는 내부적으로 `_calculate_ks_c9306_hspf`를 호출한다.
- ISO16358 region config common path에 KS 로직을 다시 합치지 않았다. AS/NZS compatibility 로직은 추가하지 않았다.

### task 3 결과
- `core/calculator_iso16358.py` 상단에 `from core.calculator_ks_c9306 import KSC9306Calculator` 추가.
- 위 KS 메서드 본문을 모두 `return self._ks_calculator()._<method>(...)` 형태의 thin wrapper로 교체했다. `_ks_calculator()`는 `KSC9306Calculator.from_iso_calculator(self)`를 매 호출마다 새로 만든다 (KS 인스턴스는 config 참조만 빌리므로 비용이 무시할 수준이며, ISO `self.Cd` 등의 latest 상태가 항상 반영된다).
- ISO16358 측 메서드 이름(`_has_ks_c9306_hspf_input`, `_ks_hspf_bin`, `_ks_hspf_correction`, …)을 그대로 유지했으므로 기존 dispatch 코드(`calculate_hspf`)와 직접 호출 테스트(`calc._ks_hspf_bin(...)`)가 변경 없이 동작한다.
- ISO16358 common HSPF Formula 44~50, ISO CSPF, profile resolver, UI 경로는 수정하지 않았다. KS 위임 외 ISO 모듈 변경은 import 1줄 + 동일 시그니처 wrapper로 한정된다.

### task 4 결과
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py` → 정상 통과.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea"` → `40 passed`.
- `python3 -B -m pytest tests/test_iso16358_hspf_ks_oracle.py -q` → `2 passed` (직접 `_ks_hspf_bin` 호출 포함).
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py -q` → `34 passed, 1 failed` — 실패는 `test_iso_common_hspf_frost_boundaries_come_from_config` (ISO common formula50 frost branch, KS 무관).
- `python3 -B -m pytest tests/test_iso16358_hspf_golden.py -q` → 9 failed (case 3 Excel component-sum trace 관련, pre-existing).
- `python3 -B -m pytest tests/test_iso16358_hspf_formula_micro.py -q` → 4 failed, 2 passed, 1 xfailed (Formula 47/50 / half-to-full / tiny-bin accumulation, pre-existing).
- 전체: `python3 -B -m pytest tests -q` → `258 passed, 16 failed, 13 xfailed`.
- main HEAD baseline (git stash로 작업물 제거 후 동일 명령 재실행) → `258 passed, 16 failed, 13 xfailed`로 정확히 일치. 16 failures는 모두 pre-existing known failures이며 본 refactor에 의한 회귀가 아니다.
- 어떤 test, fixture, expected, tolerance, xfail/pass 토글도 수정하지 않았다.

### task 5 결과
- 새 KS 모듈로 이동한 로직:
  - KS C 9306 HSPF 입력 validation 전체 (`_validate_ks_c9306_hspf_input`, `_validate_ks_hspf_positive_number`, `_ks_hspf_required_points`, `_ks_hspf_profile_point_path`).
  - KS HSPF stage 값 보간/유도 (`_ks_hspf_stage_value`, `_ks_hspf_linear`, `_ks_hspf_minus7_factor`, `_ks_hspf_correction`).
  - KS HSPF capacity/power 곡선 (`_ks_hspf_capacity_curve`, `_ks_hspf_power_curve`, `_ks_hspf_stage_curves`, `_ks_hspf_is_frost_region`).
  - KS HSPF load line / building load (`_ks_hspf_load_line`, `_ks_hspf_config_load_line`, `_ks_hspf_bin_load`).
  - KS HSPF intersection 기반 보간 (`_ks_hspf_capacity_line`, `_ks_hspf_intersection_temp`, `_ks_hspf_power_by_intersection`).
  - 부하 구간별 power 결정 + bin record 생성 (`_ks_hspf_interpolate_power_for_load`, `_ks_hspf_bin`).
  - bin loop / cycling / aux 계산 / HSTL·HSEC accumulation (`_calculate_ks_c9306_hspf`).
- 새 KS 모듈로 이동한 KS CSPF 로직: 없음 (이번 작업은 KS HSPF block 분리에 집중).
- `calculator_iso16358.py`에 남긴 wrapper/delegation:
  - 위 KS 메서드 24개 모두 동일 시그니처 thin wrapper로 유지. 매번 `KSC9306Calculator.from_iso_calculator(self)`를 통해 KS 인스턴스에 위임.
- 아직 남은 KS 관련 중복/위험:
  - `_ks_intersection_power` (line 303 부근)와 `_round_test_value` (line 46 부근)는 ISO 모듈에 그대로 남아 있다. 둘 다 ISO CSPF / 전처리 경로에서 인라인 호출되며, 분리 시 ISO 메서드 구조까지 수정해야 하므로 이번 behavior-preserving 단계에서는 보존했다. 후속 작업에서 KS CSPF 정리와 함께 처리한다.
- ISO16358 path 영향 여부: ISO common CSPF/HSPF 계산식, `calculate_hspf_iso16358_common`, `calculate_cspf` 등은 수정하지 않았다. import 1줄과 thin wrapper로 한정된 변경이다.
- public API 변화 여부: `ISO16358Calculator`의 public/private 메서드 시그니처는 그대로다. 새 `KSC9306Calculator` 클래스가 추가되었을 뿐이다.
- result schema 변화 여부: `_calculate_ks_c9306_hspf`가 반환하는 dict 키/값 구성은 그대로 유지된다(이동 시 본문을 변경하지 않았음).
- 후속 정리 필요 여부:
  - `_ks_intersection_power` 분리 (KS CSPF로 이전) 검토.
  - ISO16358 측 KS thin wrapper 24개의 최종 제거(테스트가 KS calculator를 직접 사용하도록 이행한 뒤).
  - KS C 9306 dedicated profile/calculator_id 라우팅을 `core/calculator_profiles.py`에 추가하는 후속 작업.

### task 6 결과
- 작업 전 `git status` / `git diff --stat`으로 변경 범위가 `core/calculator_iso16358.py` + `core/calculator_ks_c9306.py`로 한정됨을 확인했다.
- `py_compile` 통과 후 source commit 수행: `refactor: separate KS C9306 calculator` (hash `57e5a49`).
- 본 report 파일을 `result_reports/active/025_separate-ks-c9306-calculator.md`로 생성했다.
- report commit: `report: record KS C9306 calculator separation` (commit hash는 push 후 보고).
- push: `origin/main`.

## Test Results
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea"` → `40 passed`.
- `python3 -B -m pytest tests/test_iso16358_hspf_ks_oracle.py -q` → `2 passed`.
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py -q` → `34 passed, 1 failed` (pre-existing ISO common formula50 frost test).
- `python3 -B -m pytest tests/test_iso16358_hspf_golden.py -q` → `9 failed, 9 passed, 7 xfailed` (pre-existing case 3 Excel trace failures).
- `python3 -B -m pytest tests/test_iso16358_hspf_formula_micro.py -q` → `4 failed, 2 passed, 1 xfailed` (pre-existing).
- `python3 -B -m pytest tests -q` → `258 passed, 16 failed, 13 xfailed`.
- Baseline `python3 -B -m pytest tests -q` (작업 시작 시 main HEAD) → `258 passed, 16 failed, 13 xfailed` — 동일 통계로 회귀 없음.

## Changed Files
- `core/calculator_ks_c9306.py` (신규 생성)
- `core/calculator_iso16358.py` (KS HSPF 본문 → thin delegating wrappers, import 1줄 추가)
- `result_reports/active/025_separate-ks-c9306-calculator.md`

## Known Failures / Risks
- 16개 pre-existing test failures는 main HEAD에도 동일하게 존재하며 본 refactor와 무관하다 (Verification 섹션의 baseline 비교로 확인). 대표 항목:
  - `tests/test_iso16358_hspf_validation.py::test_iso_common_hspf_frost_boundaries_come_from_config` — ISO common formula 50 frost branch 활성화 조건 (project_log 2026-05-11 기록과 관련된 known mismatch).
  - `tests/test_iso16358_hspf_golden.py` 의 case 3 Excel BM/BO/CD/Y_MIN_Y_EXTD trace-only 진단 테스트들.
  - `tests/test_iso16358_hspf_formula_micro.py` 의 Formula 50 / half-to-full / tiny-bin accumulation 마이크로 테스트.
  - `tests/test_iso16358_hspf_pure_iso_track_a.py::test_pure_iso_track_a_min_to_half_formula_44_48_route_level`.
- Thin delegation 패턴은 매 호출마다 `KSC9306Calculator` 인스턴스를 새로 만든다. config dict는 공유 참조이며 메서드 본문에서 변형되지 않으므로 동작에는 문제가 없지만, 한 번의 ISO HSPF KS dispatch 안에서 다수의 wrapper가 연쇄 호출될 경우 동일 KS instance를 캐시하지 않는다. 성능 영향은 미미하며, 후속 정리에서 캐시 또는 wrapper 제거로 다룰 수 있다.
- `_ks_intersection_power`와 `_round_test_value`는 여전히 ISO 모듈에 남아 있어 KS-naming이 ISO 측에 일부 섞여 있다. KS CSPF 정리 단계에서 후속 처리가 필요하다.

## Next Suggested Action
- `core/calculator_iso16358.py`를 ISO 16358 CSPF/HSPF 전용으로 정리/재작성하는 단계의 일환으로:
  1. `_ks_intersection_power`를 `KSC9306Calculator` 또는 별도 KS CSPF helper로 이전하고 ISO CSPF 메서드는 strategy 위임 형태로 정리.
  2. ISO16358 측 KS thin wrappers를 최종적으로 제거하고, 테스트 및 dispatch가 `KSC9306Calculator`를 직접 사용하도록 이행.
  3. `core/calculator_profiles.py`에 `calculator_id=ks_c9306` profile record 등록.

## Scope Compliance
- ISO16358 CSPF/HSPF path: 계산식 수정 없음 (import 1줄 + thin wrapper만 추가/교체).
- KS C 9306 path: 본문은 동일하게 새 모듈로 이동, 계산식 변경 없음.
- AS/NZS compatibility: 구현하지 않았음 (`core/calculator_asnzs_hspf_excel.py`는 이번 작업에서 수정하지 않음).
- tests/fixtures/expected: 수정하지 않았음.
- docs: 수정하지 않았음.
- UI: 수정하지 않았음.
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 그대로).
- workbook/reference_files: 수정하지 않았음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- source commit: `57e5a49 refactor: separate KS C9306 calculator`
- report commit: `report: record KS C9306 calculator separation`
- pushed branch: `origin/main`
