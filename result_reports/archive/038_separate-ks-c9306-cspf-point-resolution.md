# 038_separate-ks-c9306-cspf-point-resolution

## Goal
- 보고 037의 후속 단계로 KS C 9306 CSPF 독립화를 한 단위 더 진행한다. ISO `_resolve_cspf_profile_points`의 T1 / T3 derived point 생성 책임을 `KSC9306Calculator`로 복제·분리하고, `KSC9306Calculator.calculate_cspf(...)`에서 measured input 선전처리 직후 KS 측에서 derived point를 먼저 채운 뒤 기존 ISO delegate 경로에 넘긴다. ISO common engine은 수정하지 않으며 ISO 측 `_set_point`의 overwrite 방지 동작에 의해 결과는 변하지 않는다.

## Scope
- `core/calculator_ks_c9306.py`
  - `KSC9306Calculator`에 KS CSPF용 `_resolve_cspf_profile_points(measured)` 추가.
    - 입력 dict를 mutate하지 않고 새 dict 반환. point_data dict도 새 dict로 얕게 복사.
    - `cspf_test_profile.climate_profile`이 `T1`이면 `29_full / 29_half`, optional `29_min` 생성.
    - `T3`이면 `46_half / 29_full / 29_half`, optional `46_min / 29_min` 생성.
    - `cspf_test_profile` 자체가 없으면 derived point를 만들지 않고 shallow copy만 반환 (Korea처럼 `points`+`derived_rules` 기반 region은 ISO delegate 쪽 `resolve_points()`가 이어서 처리).
    - 이미 존재하는 key는 overwrite하지 않는다 (`_set_point`).
  - `KSC9306Calculator.calculate_cspf(...)` 진입점 흐름:
    1. `_prepare_measured_inputs(...)` (037에서 도입)
    2. `declared_capacity` 선정수화 (037)
    3. KS 측 `_resolve_cspf_profile_points(...)` (이번 단계)
    4. 기존 ISO delegate (`_iso_calculator_ref` 우선, 없으면 lazy import `ISO16358Calculator(self._config_path)`)
  - 기존 `calculate_hspf`, `_ks_cspf_*`, `_ks_hspf_*`는 수정하지 않았다.

## Non-goals
- `core/calculator_iso16358.py` 수정 금지 (`_resolve_cspf_profile_points` / `resolve_points` / `_get_active_load_levels` / `_get_cspf_temperature_segments` / `calculate_cspf` 모두 그대로).
- KS CSPF full bin loop / regime selection / interpolation / accumulation / result composition KS module 복제 금지.
- ISO `ks_intersection` 분기 제거 금지.
- ISO delegate 자체 제거 금지.
- `_ks_intersection_power` wrapper 제거 금지.
- KS HSPF body 수정 금지.
- profile resolver / dispatcher / UI / region config JSON / tests / fixtures / docs / workbook 수정 금지.
- 새 테스트 추가 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업.
- `result_reports/{active,archive,summaries}` 전 디렉터리 최대 번호 037 확인 후 다음 번호 038 사용.
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py` → 통과.
- KS CSPF spot check (`KSC9306Calculator.from_config_path("data/region_configs/korea.json").calculate_cspf({35_full: cap=6035.8/pow=1641.4, 35_half: cap=3420.4/pow=679.4, 29_min: cap=1759.6/pow=201.7}, declared_capacity=6000)`) → `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852` (기존 기준값 동일).
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- 전체 `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 통계 / failure set 동일, 회귀 없음.
- `git diff --stat`으로 source 변경이 `core/calculator_ks_c9306.py` 1개 (76 insertions, 0 deletions)로 한정됨을 확인.

## Task Results
### task 1 결과
- ISO 측 흐름 확인 (`core/calculator_iso16358.py`):
  - `_resolve_cspf_profile_points` (line 109): `resolved = {k: v for k, v in measured.items()}`로 shallow copy 후 `_set_point(key, cap, pwr)`(line 116-118)이 `if key not in resolved`만 채워 overwrite 방지. T1은 `29_full/29_half` (+optional `29_min`), T3은 `46_half/29_full/29_half` (+optional `46_min/29_min`).
  - `resolve_points` (line 136): `_has_cspf_test_profile()`이면 `_resolve_cspf_profile_points`로 위임, 아니면 `points` config의 measure/default + `derived_rules`로 채움.
  - `_get_active_load_levels` (line 96): `cspf_test_profile.test_selection`이 `with_optional_test`이면 `["full","half","min"]`, 그 외 `["full","half"]`.
  - `_get_cspf_temperature_segments` (line 103): T3이면 boundary 35로 high/low 분기, 그 외 boundary None.
  - `calculate_cspf` (line 2148): `_prepare_measured_inputs` 호출 후 `_has_cspf_test_profile()`이면 `_resolve_cspf_profile_points` → `_calculate_cspf_profile`, 아니면 `resolve_points` → declared_capacity 정수화 → bin loop.
- KS 측 흐름 확인 (`core/calculator_ks_c9306.py`):
  - `_prepare_measured_inputs` (037에서 추가): `round_test_values=True`일 때 capacity/power 정수화 새 dict 반환.
  - `calculate_cspf`: 선전처리 후 곧장 ISO delegate (`_iso_calculator_ref` 또는 lazy `ISO16358Calculator(self._config_path)`)로 위임.
- `data/region_configs/korea.json`:
  - `cspf_test_profile` 키 **없음**. Korea CSPF는 `points` + `derived_rules` 기반 (`35_full/35_half` measure, `29_min` measure, `35_min/29_full/29_half` derived; `29_full: factors 1.077/0.864`, `29_half: 1.077/0.864`, `35_min: 0.9285/1.1574`).
  - `round_test_values=true`, `building_load_source=declared`, `power_interpolation_method=ks_intersection`, `reference_point=35_full`, `Cd=0.25`.
- Behavior-preserving 판단:
  - Korea처럼 `cspf_test_profile`이 없는 region에서 KS 측 helper는 derived point를 만들지 않고 shallow copy만 반환하므로, ISO delegate가 기존 `resolve_points()` 경로로 동일하게 derived_rules를 적용한다. 결과 변화 없음.
  - `cspf_test_profile`이 있는 region(T1/T3)에서 KS 측 helper가 미리 derived point를 채워도, ISO 측 `_resolve_cspf_profile_points`의 `_set_point`가 `if key not in resolved`로만 채우므로 KS 측 값이 그대로 유지되고, 동일 factor를 사용하므로 결과 동치.

### task 2 결과
- `KSC9306Calculator._resolve_cspf_profile_points(measured)` 추가.
- 동작:
  - 새 dict `resolved`를 만들고, 각 point_data dict는 `dict(point_data)`로 얕게 복사. dict가 아니면 그대로 보존.
  - `profile_cfg = self.config.get("cspf_test_profile", {})`로 climate / selection 추출. 없으면 둘 다 `None`이라 어떤 분기도 타지 않고 shallow copy만 반환.
  - `_set_point(key, cap, pwr)` inner helper가 `if key not in resolved` 가드로 overwrite 방지.
  - T1 분기: `29_full = 35_full * 1.077 / 0.914`, `29_half = 35_half * 1.077 / 0.914`, `with_optional_test`이면 `29_min`.
  - T3 분기: `46_half = 35_half * 0.859 / 1.25`, `29_full / 29_half`, `with_optional_test`이면 `46_min / 29_min`.
- 입력 mutation 방지: 호출자가 넘긴 dict와 그 안의 point_data dict는 어디서도 수정하지 않음.
- 기존 ISO helper와 동일한 factor / 동일한 key set / 동일한 overwrite 정책.

### task 3 결과
- `calculate_cspf(...)` 진입점 흐름 (037 흐름에 한 줄 추가):
  1. `measured_inputs = self._prepare_measured_inputs(measured_inputs)`
  2. `declared_capacity is not None and round_test_values`이면 `_round_test_value`로 정수화 (예외는 원값 유지)
  3. `measured_inputs = self._resolve_cspf_profile_points(measured_inputs)` ← 이번 단계 추가
  4. `_iso_calculator_ref`가 있으면 그 인스턴스의 `calculate_cspf(...)` 호출, 없으면 lazy import 후 `ISO16358Calculator(self._config_path).calculate_cspf(...)`, 둘 다 없으면 기존 `ValueError` 메시지.
- `calculate_hspf`, `_ks_hspf_*`, `_ks_cspf_performance_line`, `_ks_cspf_intersection_power`는 일절 손대지 않았다.

### task 4 결과
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py` → 통과.
- KS CSPF spot check: `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852` — 기존 기준과 완전 동일.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- 전체 `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline과 통계 / failure set 완전 동일, 신규 회귀 없음.
- 16개 failures는 모두 pre-existing ISO HSPF (case3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundary 등)로 본 변경과 무관.

### task 5 결과
- 추가 helper: `KSC9306Calculator._resolve_cspf_profile_points`.
- 지원 climate_profile: `T1`, `T3`. `cspf_test_profile` 자체가 없으면 derived point 미생성 (shallow copy만 반환).
- overwrite 방지: 예 (`_set_point`이 `if key not in resolved`로 기존 key는 그대로 둠).
- input dict mutation 방지: 예 (`resolved`는 새 dict, point_data는 `dict(point_data)`로 얕게 복사).
- `calculate_cspf` 적용 순서: `prepare_measured_inputs` → `declared_capacity` 정수화 → `_resolve_cspf_profile_points` → ISO delegate.
- ISO delegate 유지: 예.
- ISO `ks_intersection` 분기 유지: 예 (`calculator_iso16358.py` 무수정).
- KS HSPF 영향: 없음 (`calculate_hspf` / `_ks_hspf_*` 무수정).
- public API 변화: 없음.
- result schema 변화: 없음 (spot check로 동일 dict 키/값 확인).
- spot check 결과: 통과 (`cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852`).
- 후속 작업 후보 1개: **KS CSPF building load / declared_capacity 분기 분리 audit**. 현재 ISO `calculate_cspf`에서 `building_load_source == "declared"`이면 `declared_capacity`로 `L_c_ref`를 잡고 KS path가 그대로 이어진다. KS측에서 이 분기 책임을 명시적으로 가져올지(`L_c_ref`를 KS module에서 계산 → ISO delegate에 hint로 넘기는 정책), 아니면 ISO delegate를 그대로 두고 KS module은 declared_capacity 검증만 책임질지 결정하는 audit-only turn이 다음 안전 단위로 권장된다.

### task 6 결과
- `git status` / `git diff --stat`로 source 변경 범위 = `core/calculator_ks_c9306.py` (76 insertions) 단일 파일로 한정됨을 확인.
- source commit: `refactor: separate KS C9306 CSPF point resolution` (hash `e95eec4`).
- 본 report 파일을 `result_reports/active/038_separate-ks-c9306-cspf-point-resolution.md`로 생성.
- report commit: `report: record KS C9306 CSPF point resolution separation` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py` → 통과.
- KS CSPF spot check (`korea.json`, declared_capacity=6000) → `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852`.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 동일.

## Changed Files
- `core/calculator_ks_c9306.py`
- `result_reports/active/038_separate-ks-c9306-cspf-point-resolution.md`

## Known Failures / Risks
- 16개 pre-existing ISO HSPF failures (case3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundary config 등)는 본 변경과 무관.
- Korea region (현재 KS CSPF 주 사용 케이스)은 `cspf_test_profile`이 없어 KS 측 `_resolve_cspf_profile_points`가 shallow copy만 반환하고 derived point는 ISO delegate의 `resolve_points()` + `derived_rules` 경로가 그대로 처리한다. 즉 Korea에 대한 행동 변화는 0이며, KS 측 helper는 향후 KS CSPF가 `cspf_test_profile` 기반 region(T1/T3)으로 확장될 때만 실효를 가진다.
- ISO `_resolve_cspf_profile_points`와 KS `_resolve_cspf_profile_points`가 동일 factor를 중복 보유한다. 추후 ISO 측에서 KS-flagged 분기가 정리되거나 KS가 ISO delegate를 거치지 않는 단계로 가면 ISO 측 중복 정의를 제거할 수 있다. 분기 동안 두 helper가 다르게 진화하면 같은 입력에 다른 derived point가 나올 수 있으므로 KS-side에서 ISO 정의를 동기화 유지하는 것이 필요.
- 본 변경은 KS CSPF 경로에 한정되며 KS HSPF, AHRI SEER2/HSPF2, ISO T1 default / India / Hong Kong / SASO CSPF 경로에는 영향이 없다.

## Next Suggested Action
- **KS CSPF building load / declared_capacity 분기 분리 audit**: ISO `calculate_cspf`의 `building_load_source == "declared"` 분기와 `L_c_ref` 결정 로직을 KS 측에서 어디까지 책임질지 audit-only로 정리한다. 옵션은 (a) KS module이 `declared_capacity` 검증과 `L_c_ref` 계산까지 가져오고 ISO delegate에 hint를 넘긴다, (b) ISO delegate를 그대로 두고 KS module은 declared_capacity 정수화/존재 검증만 책임진다, (c) 추가 분리 보류. behavior-preserving 가능한 가장 작은 다음 단위를 결정한 뒤 별도 turn에서 구현.

## Scope Compliance
- KS C 9306 calculator: 수정함 (`core/calculator_ks_c9306.py`).
- ISO16358 calculator: 수정하지 않음 (`core/calculator_iso16358.py` 그대로).
- KS HSPF path: 수정하지 않음 (`calculate_hspf`, `_ks_hspf_*`, `_calculate_ks_c9306_hspf` 그대로).
- profile resolver: 수정하지 않음 (`core/calculator_profiles.py` 그대로).
- dispatcher: 수정하지 않음 (`core/calculator_dispatcher.py` 그대로).
- UI: 수정하지 않음 (`ui/*` 그대로).
- tests: 수정하지 않음.
- fixtures/golden expected: 수정하지 않음.
- docs: 수정하지 않음.
- region config JSON: 수정하지 않음 (`data/region_configs/*.json` 그대로, `korea.json` 포함).
- workbook/reference_files: 수정하지 않음.
- git pull/merge/rebase: 수행하지 않음.

## Commit / Push
- source commit: `e95eec4 refactor: separate KS C9306 CSPF point resolution`
- report commit: `report: record KS C9306 CSPF point resolution separation`
- pushed branch: `origin/main`
