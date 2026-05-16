# 027_prepare-ks-c9306-cspf-public-entry

## Goal
- `KSC9306Calculator`에 KS C 9306 CSPF public entry (`calculate_cspf`)를 behavior-preserving한 thin delegation으로 추가하여, 향후 profile resolver/UI 작업이 ISO `ISO16358Calculator(config_path).calculate_cspf(...)` 대신 KS calculator를 직접 호출할 수 있도록 진입점을 준비한다. ISO16358 측 `calculate_cspf()` 결과와 동작은 변경하지 않는다.

## Scope
- `core/calculator_ks_c9306.py`
  - `__init__`에 `_config_path`, `_iso_calculator_ref` 슬롯 추가.
  - `from_config_path(...)`이 `_config_path`를 저장하도록 갱신.
  - `from_iso_calculator(...)`이 원본 ISO 인스턴스 reference를 `_iso_calculator_ref`로 저장하도록 갱신.
  - 새 public method `KSC9306Calculator.calculate_cspf(measured_inputs, declared_capacity=None)` 추가. 본문은 다음과 같다.
    - `_iso_calculator_ref`가 있으면 해당 ISO 인스턴스의 `calculate_cspf(...)`로 위임.
    - 없으면 `_config_path`로 lazy import한 `ISO16358Calculator(config_path)`를 만들고 위임.
    - 둘 다 없으면 명확한 `ValueError` 발생.
- 위임은 ISO common CSPF engine을 그대로 사용하므로 KS 고유 동작 (`round_test_values`, `rounding_method`, `power_interpolation_method=ks_intersection`, `building_load_source=declared`)은 모두 config flag로 그대로 적용된다.
- `core/calculator_iso16358.py`는 수정하지 않았다 (task 3의 조건부 위임 분기는 의도적으로 보류, Task Results 참조).

## Non-goals
- ISO16358 CSPF/HSPF 계산식 수정 금지.
- KS C 9306 HSPF 계산식 수정 금지.
- AS/NZS workbook oracle / `core/calculator_asnzs_hspf_excel.py` 구현 금지.
- profile resolver (`core/calculator_profiles.py`) / UI 수정 금지.
- tests / fixture / xfail / golden / docs 수정 금지.
- 새 테스트 추가 금지.
- `_round_test_value` 이동 금지.
- ISO common CSPF helper (resolve_points, interpolate, bin loop, PLF 등)를 KS 모듈로 복제하지 않음.

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py` → compile OK.
- KS public entry 결과 동등성 spot check (Python REPL 1회):
  ```
  KSC9306Calculator.from_config_path("data/region_configs/korea.json").calculate_cspf(
      {"35_full": {"capacity": 6035.8, "power": 1641.4},
       "35_half": {"capacity": 3420.4, "power": 679.4},
       "29_min":  {"capacity": 1759.6, "power":  201.7}},
      declared_capacity=6000)
  → cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852
  ```
  이는 `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py::test_korea_cspf_regression_unchanged_by_diagnostics`가 ISO 경로에서 어서트하는 값과 정확히 일치한다.
- KS/CSPF keyword 테스트: `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf"` → `79 passed`.
- 전체: `python3 -B -m pytest tests -q` → `258 passed, 16 failed, 13 xfailed`.
- Baseline (보고 026 직후 main HEAD) 통계는 `258 passed, 16 failed, 13 xfailed`로 동일, 실패 항목 set 동일. 본 변경에 의한 신규 회귀 없음.

## Task Results
### task 1 결과
- grep으로 `power_interpolation_method` 사용처를 확인했다.
  - `data/region_configs/korea.json` → `"ks_intersection"`
  - `data/region_configs/india_iseer.json` → `"iso_boundary_eer"`
  - `data/region_configs/saso.json` → `"iso_boundary_eer"`
  - `data/region_configs/iso_t1_default_2point.json` → `"iso_boundary_eer"`
  - `data/region_configs/hong_kong.json` → `"iso_boundary_eer"`
- 결론: `ks_intersection`은 KS C 9306 전용이며 다른 region/profile에서는 쓰이지 않는다.
- 그러나 KS CSPF 전체 흐름은 ISO `calculate_cspf`의 generic CSPF engine을 다음 KS-specific config flag로 구동하는 구조다.
  - `round_test_values: true`, `rounding_method: "nearest_integer_half_up"`
  - `building_load_source: "declared"`
  - `power_interpolation_method: "ks_intersection"`
  - `reference_point`, `t_100_load`, `t_0_load`, `Cd`, `bin_hours` 등 일반 ISO config field.
- KS CSPF는 별도 method body로 분리되어 있지 않고 ISO `calculate_cspf` 내부에서 config 분기로 처리된다. 따라서 “KS CSPF body”를 그대로 떼어내는 작업은 ISO 일반 CSPF helper (`resolve_points`, `interpolate`, bin loop, PLF, `_iso_boundary_eer_power` 등) 전체를 복제해야 가능한 큰 작업이다.
- 본 단계에서 안전한 범위: KS 전용 reimplementation 대신 ISO common CSPF engine을 KS calculator에서 호출하는 thin public entry만 추가하는 것. 이는 task 2의 권장 사항 “구현 범위가 커질 것 같으면 중단하고 blocked로 보고한다”와 “단, ISO 일반 CSPF helper 전체를 무리하게 옮기지 않는다”에 부합한다.

### task 2 결과
- `KSC9306Calculator`에 `calculate_cspf(measured_inputs, declared_capacity=None)`를 추가했다.
- ISO 모듈은 thin delegate를 위해 lazy import (`from core.calculator_iso16358 import ISO16358Calculator`)를 method 내부에서 수행한다. 모듈 레벨 import는 추가하지 않아 ISO ↔ KS 사이의 순환 import를 발생시키지 않는다.
- 위임 경로 2가지:
  1. `from_iso_calculator(iso_calc)`로 만든 인스턴스는 `_iso_calculator_ref`를 보유하고 있어 그 ISO 인스턴스로 직접 위임한다 (재로딩 없음).
  2. `from_config_path(config_path)`로 만든 인스턴스는 `_config_path`를 보유하고, 호출 시 `ISO16358Calculator(self._config_path)`로 새 ISO 인스턴스를 생성해 위임한다.
- KS 고유 helper (`_ks_cspf_performance_line`, `_ks_cspf_intersection_power`)는 그대로 KS 모듈 안에 유지된다. ISO `calculate_cspf`는 KS-specific config flag로 KS calculator의 그 helper들을 호출하는 현재 구조(`_ks_intersection_power` thin wrapper 경유)를 그대로 사용한다.
- KS HSPF 본문, ISO HSPF 본문, AS/NZS 로직은 변경하지 않았다.

### task 3 결과
- 위임 조건이 불명확하다는 task 지시에 따라 `core/calculator_iso16358.py`는 수정하지 않았다.
- 그 이유: 현재 `ISO16358Calculator.calculate_cspf`는 KS-only condition (예: `ks_c_9306` profile flag)이 없다. KS CSPF는 generic config flag (`power_interpolation_method`, `round_test_values` 등) 조합으로 정의된다. 만약 ISO 측에서 “KS config면 KSC9306Calculator.calculate_cspf로 delegate”하도록 분기를 추가하면, KS calculator가 다시 ISO engine으로 위임하기 때문에 무한 재귀가 발생한다 (KS public entry가 ISO engine을 호출).
- 따라서 ISO `calculate_cspf` body를 KS-condition-aware로 만드는 작업은 별도 라우팅 전략 (예: profile resolver가 KS 호출 시 `_inside_ks_dispatch` 플래그를 세팅하거나, ISO common engine을 KS-aware하지 않은 private helper로 분리) 설계가 필요하다. 이는 본 “public entry 준비” 작업의 범위를 벗어난다.
- 결론: 기존 `ISO16358Calculator.calculate_cspf` 경로는 100% 보존된다. `_ks_intersection_power` thin wrapper도 변경 없이 유지된다.

### task 4 결과
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py` → 정상 통과.
- KS/CSPF keyword: `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf"` → `79 passed`.
- 전체: `python3 -B -m pytest tests -q` → `258 passed, 16 failed, 13 xfailed`. 실패 항목 set은 보고 026 직후 baseline과 정확히 동일 (모두 ISO common HSPF formula 47/50 / case 3 Excel BM/BO/CD/Y_MIN_Y_EXTD trace / pure ISO track A / formula50 frost 등 pre-existing known mismatch).
- 추가 spot check: `KSC9306Calculator.from_config_path("data/region_configs/korea.json").calculate_cspf(...)` 결과가 `test_korea_cspf_regression_unchanged_by_diagnostics`의 기대값 `cspf=6.504`, `annual_cooling_kwh=1943.798`, `annual_power_kwh=298.852`과 정확히 일치함을 확인.
- 어떤 test, fixture, expected, tolerance, xfail/pass 토글도 수정하지 않았다.

### task 5 결과
- `ks_intersection` config 사용 범위: 오직 `data/region_configs/korea.json`만 사용한다. 다른 region/profile은 `iso_boundary_eer`을 사용한다. 따라서 `ks_intersection`은 KS C 9306 전용으로 안전하게 분류 가능하다.
- `KSC9306Calculator.calculate_cspf(...)` 추가 여부: 추가했음. ISO common CSPF engine으로 위임하는 thin public entry로 구현 (lazy import 경유).
- ISO `calculate_cspf()` 위임 여부: 위임하지 않음 (무한 재귀 위험 때문). ISO public path는 변경 없이 그대로 유지.
- `_ks_intersection_power` wrapper 유지/변경 여부: ISO 측 thin wrapper와 KS 측 `_ks_cspf_intersection_power` 모두 그대로 유지. 이번 작업에서 수정 없음.
- `_round_test_value` 처리 여부: 이번 작업 범위 밖이므로 ISO 모듈에 그대로 유지. CSPF/HSPF 공통 전처리 `_prepare_measured_inputs`가 사용 중.
- ISO16358 CSPF/HSPF path 영향 여부: 변경 없음. 계산식, 분기, 결과 dict 모두 동일.
- KS C 9306 HSPF path 영향 여부: 변경 없음.
- public API 변화 여부: `ISO16358Calculator` public/private 시그니처 변화 없음. `KSC9306Calculator`에 public method `calculate_cspf(measured_inputs, declared_capacity=None)`이 추가됐고, factory 두 개에 internal slot (`_config_path`, `_iso_calculator_ref`)이 기록되도록 보강됨.
- result schema 변화 여부: 변화 없음. KS public entry는 ISO `calculate_cspf`가 반환하는 dict를 그대로 반환한다 (`cspf`, `annual_cooling_kwh`, `annual_power_kwh`, `bin_details`).
- profile resolver로 넘어갈 준비:
  - HSPF 경로: 보고 025에서 `KSC9306Calculator.calculate_hspf(...)` public entry가 이미 존재한다.
  - CSPF 경로: 본 작업으로 `KSC9306Calculator.calculate_cspf(...)` public entry가 마련되었다.
  - 따라서 `core/calculator_profiles.py`에 `calculator_id=ks_c9306` profile record를 추가하고, dispatch가 KS profile이면 `KSC9306Calculator.from_config_path(profile.config_path).calculate_cspf(...) / .calculate_hspf(...)`를 호출하도록 라우팅하는 후속 단계가 가능하다.
  - 단, ISO `calculate_cspf` body 안의 KS-aware 분기는 그대로 남아 있으므로, 후속 단계에서 ISO common engine을 KS-aware하지 않은 형태로 분리하는 작업이 필요하다 (KS thin wrappers 제거 가능 시점도 그때).

### task 6 결과
- `git status` / `git diff --stat`으로 변경 범위가 `core/calculator_ks_c9306.py` 1개 파일로 한정됨을 확인했다 (`core/calculator_iso16358.py`는 의도적으로 수정하지 않음).
- `py_compile` 통과 후 source commit: `refactor: prepare KS C9306 CSPF public entry` (hash `507a8cd`).
- 본 report 파일을 `result_reports/active/027_prepare-ks-c9306-cspf-public-entry.md`로 생성.
- report commit: `report: record KS C9306 CSPF public entry preparation` (push 후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf"` → `79 passed`.
- `python3 -B -m pytest tests -q` → `258 passed, 16 failed, 13 xfailed`.
- Baseline (보고 026 직후 main HEAD) → `258 passed, 16 failed, 13 xfailed`로 동일. 실패 set 동일. 신규 회귀 없음.
- Spot check: `KSC9306Calculator.from_config_path("data/region_configs/korea.json").calculate_cspf(...)`이 `test_korea_cspf_regression_unchanged_by_diagnostics`의 ISO 경로 기대값 `6.504 / 1943.798 / 298.852`와 정확히 일치.

## Changed Files
- `core/calculator_ks_c9306.py` (calculate_cspf public entry + factory slot 보강)
- `result_reports/active/027_prepare-ks-c9306-cspf-public-entry.md`

## Known Failures / Risks
- 16개 pre-existing test failures는 본 변경과 무관하며 main HEAD에도 동일하게 존재한다.
- `KSC9306Calculator.calculate_cspf(...)`는 ISO common CSPF engine에 thin delegate한다. KS-only reimplementation이 아니므로 향후 profile resolver가 KS dispatch를 `KSC9306Calculator`로 라우팅하더라도 실제 계산은 ISO 모듈에서 일어난다 (이번 단계의 의도된 동작이며, ISO `calculate_cspf`의 KS-aware 분기는 그대로 남아 있다).
- `from_config_path` 경로는 매 `calculate_cspf` 호출 시 ISO 인스턴스를 새로 만든다 (config 재로딩 포함). 다회 호출이 필요한 라우팅 코드는 단일 인스턴스를 재사용해야 한다. `from_iso_calculator` 경로는 attached ISO 인스턴스를 재사용하므로 재로딩하지 않는다.
- ISO `calculate_cspf`는 여전히 KS-aware (`power_interpolation_method == "ks_intersection"`, `_ks_intersection_power` wrapper 사용). 다음 단계에서 ISO common engine을 KS-unaware로 분리해야 라우팅과 thin wrapper를 완전히 제거할 수 있다.

## Next Suggested Action
- `core/calculator_profiles.py`에 `calculator_id=ks_c9306` profile record를 추가하고, KS dispatch가 `KSC9306Calculator.from_config_path(...).calculate_cspf/.calculate_hspf(...)`를 호출하도록 라우팅하는 후속 단계. 그 다음에 ISO `calculate_cspf` 내부의 `power_interpolation_method == "ks_intersection"` 분기를 KS-unaware하게 분리하는 작업으로 이어 ISO 측 thin wrappers 최종 제거를 검토할 수 있다.

## Scope Compliance
- ISO16358 CSPF/HSPF path: 수정 없음.
- KS C 9306 CSPF path: `KSC9306Calculator.calculate_cspf` public entry 추가 (ISO common engine으로 위임).
- KS C 9306 HSPF path: 수정 없음 (보고 025에서 추가된 `calculate_hspf` 그대로).
- AS/NZS compatibility: 구현하지 않았음.
- tests/fixtures/expected: 수정하지 않았음.
- docs: 수정하지 않았음.
- UI: 수정하지 않았음.
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 그대로).
- workbook/reference_files: 수정하지 않았음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- source commit: `507a8cd refactor: prepare KS C9306 CSPF public entry`
- report commit: `report: record KS C9306 CSPF public entry preparation`
- pushed branch: `origin/main`
