# 039_implement-ks-c9306-cspf-standalone-body

## Goal
- KS C 9306 CSPF를 ISO16358Calculator delegate가 아니라 `KSC9306Calculator` 내부의 standalone 계산 본문으로 새로 작성한다. measured input 준비, point resolution(`points` + `derived_rules`), declared_capacity 기반 building load, bin loop, regime 판단(최저단 cycling / 사이단 KS intersection / 최고단 saturated), 누적/결과 dict 합성을 모두 KS module 안에서 수행한다. ISO delegate 경로는 즉시 삭제하지 않고 비교/안전망 용도로 private fallback helper(`_calculate_cspf_via_iso_delegate`)로 보존한다.

## Scope
- `core/calculator_ks_c9306.py`
  - 신규 private method `_resolve_ks_cspf_points(measured_inputs)` 추가.
    - `cspf_test_profile`이 config에 있으면 기존 `_resolve_cspf_profile_points`로 위임.
    - 없으면 (Korea) `self.config["points"]`/`derived_rules`를 직접 처리: measure 검증, default 연쇄 파생, `round_test_values=true`이면 derived도 정수화, 미해결 default는 ValueError.
  - 신규 private method `_interpolate_ks_cspf(tj, resolved_points)` 추가.
    - `{temp}_{load_type}` 형식을 load_type 별로 묶고 ISO `interpolate`와 동일하게 ascending sort + 선형 보간/외삽.
  - 신규 private method `_calculate_ks_c9306_cspf(measured_inputs, declared_capacity=None)` 추가.
    - 입력 정수화 → declared_capacity 정수화 → KS point resolution → building_load_source 분기 → bin loop → regime 판정 → accumulation → 결과 dict 합성.
    - regime 분기 안 사이단에서 `power_interpolation_method=="ks_intersection"`이면 기존 `_ks_cspf_intersection_power`로 power 추정, 실패 시 capacity 선형 보간으로 fallback (Korea config는 ks_intersection 사용).
  - 신규 private helper `_calculate_cspf_via_iso_delegate(measured_inputs, declared_capacity=None)` 보존.
    - 기존 `_prepare_measured_inputs` + `_resolve_cspf_profile_points` + ISO delegate 호출 경로를 그대로 캡슐화. main path에서는 사용되지 않으며, 비교/안전망 용도.
  - `KSC9306Calculator.calculate_cspf(...)` main path를 `_calculate_ks_c9306_cspf(...)`로 교체. public signature와 반환 schema는 그대로.
  - 기존 KS CSPF helper(`_ks_cspf_performance_line`, `_ks_cspf_intersection_power`)와 KS HSPF 코드는 그대로.

## Non-goals
- `core/calculator_iso16358.py` 수정 금지 (ISO `calculate_cspf` 자체, `_ks_intersection_power` wrapper, `_resolve_cspf_profile_points`, `resolve_points`, `interpolate`, `_iso_boundary_eer_power` 모두 그대로).
- ISO `ks_intersection` 분기 제거 금지.
- ISO common engine 정리 / 중복 코드 제거 금지.
- profile resolver / dispatcher / UI / region config JSON / tests / fixtures / docs / workbook 수정 금지.
- KS HSPF body 수정 금지.
- 새 테스트 추가 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업.
- `result_reports/{active,archive,summaries}` 최대 번호 038 확인 후 다음 번호 039 사용 (사용자가 예시로 적은 038은 이미 037→038 분리 turn에 소비됨).
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py` → 통과.
- Standalone vs ISO delegate 비교: 동일 spot 입력에 대해 top key set / `cspf` / `annual_cooling_kwh` / `annual_power_kwh` / `bin_details` 길이 / 각 bin의 모든 key가 일치. 수치 차이 1e-9 미만 (실제로 모두 정확히 일치).
- KS CSPF spot check: `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852` (기존 기준값).
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- 전체 `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 통계 / failure set 완전 동일. 회귀 없음.
- `git diff --stat`으로 source 변경이 `core/calculator_ks_c9306.py` 1개 (337 insertions, 12 deletions)로 한정됨.

## Task Results
### task 1 결과
- ISO `calculate_cspf` (line 2148-2316) 분석:
  - `_prepare_measured_inputs` 호출.
  - `_has_cspf_test_profile()` 분기: 있으면 `_resolve_cspf_profile_points` + `_calculate_cspf_profile`, 없으면 `resolve_points` 기반 main flow.
  - main flow: `building_load_source=="declared"`이면 declared_capacity 정수화 후 `L_c_ref` 결정, 그 외 reference point capacity. `delta_t = t_100_load - t_0_load`로 division by zero 방어.
  - bin loop: `tj`, `nj`, `nj<=0` skip placeholder, `Lc = L_c_ref*(tj-t_0_load)/delta_t`, `Lc<=0` skip, `interpolate(tj, resolved_points)`, `"full" not in interp_tj` skip, `loads`를 capacity 기준 sort.
  - regime: `Lc<=lowest_cap`이면 cycling X/PLF/Cd; `Lc>highest_cap`이면 saturated highest; 그 외 `c1<Lc<=c2` 사이 구간에서 `ks_intersection`(Korea)/`iso_boundary_eer`/선형 보간.
  - 누적: `cstl += cooling_output*nj`, `csec += P_tj*nj`. bin_detail key set: `bin_no, tj, nj, lc, capacity, power, eer, cstl_bin, csec_bin`.
  - 결과 dict: `cspf=round(cstl/csec,3)`, `annual_cooling_kwh=round(cstl/1000,3)`, `annual_power_kwh=round(csec/1000,3)`, `bin_details`. `csec<=0`이면 0 결과.
- ISO `resolve_points` (line 136-217), `interpolate` (line 219-280), `_ks_intersection_power` (line 282-298) 동작 확인.
- KS 기존 helper 확인: `_prepare_measured_inputs`/`_round_test_value` (037), `_resolve_cspf_profile_points` (038), `_ks_cspf_performance_line`/`_ks_cspf_intersection_power` (CSPF helper 섹션).
- Baseline capture (Korea spot input, declared_capacity=6000):
  - top keys: `['annual_cooling_kwh','annual_power_kwh','bin_details','cspf']`.
  - `cspf=6.504`, `annual_cooling_kwh=1943.798`, `annual_power_kwh=298.852`.
  - bin_details 길이 15. bin key set: `['bin_no','capacity','csec_bin','cstl_bin','eer','lc','nj','power','tj']`.

### task 2 결과
- `_resolve_ks_cspf_points` 추가: cspf_test_profile 있으면 기존 helper 위임, 없으면 measure/default + derived_rules 직접 처리. derived 결과는 `round_test_values=true`이면 정수화. 미해결 default는 ValueError.
- `_interpolate_ks_cspf` 추가: ISO `interpolate`와 동일한 grouping/sort/선형 보간/외삽 로직.
- `_calculate_ks_c9306_cspf` 추가: 위 helper들과 기존 `_prepare_measured_inputs` / `_round_test_value` / `_ks_cspf_intersection_power`로 ISO main flow를 KS module 안에서 standalone 실행. config에서 직접 `t_100_load`/`t_0_load`/`Cd`/`reference_point`/`building_load_source`/`power_interpolation_method` 읽음.
- `_calculate_cspf_via_iso_delegate` private helper로 기존 delegate 경로 보존 (비교/안전망 용도). main path에서는 사용되지 않음.
- `calculate_cspf` 본문을 단 한 줄 `return self._calculate_ks_c9306_cspf(measured_inputs, declared_capacity)`로 교체.
- public API/signature/return key 모두 그대로.

### task 3 결과
- 동일 spot 입력으로 standalone과 `_calculate_cspf_via_iso_delegate` 비교:
  - `cspf`/`annual_cooling_kwh`/`annual_power_kwh` 완전 동일 (6.504 / 1943.798 / 298.852).
  - top keys 동일.
  - bin_details 길이 동일 (15).
  - 모든 bin의 9개 key가 정확히 동일 (수치 절대 오차 1e-9 미만, 실제로는 ==).
- 차이 없음. expected 수정 없이 통과.

### task 4 결과
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py` → 통과.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 완전 동일, 신규 회귀 0건.
- 16 failures는 모두 pre-existing ISO HSPF (case3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundary 등)로 본 변경과 무관.

### task 5 결과
- 추가한 private body/helper: `_resolve_ks_cspf_points`, `_interpolate_ks_cspf`, `_calculate_ks_c9306_cspf`, `_calculate_cspf_via_iso_delegate`.
- `calculate_cspf` main path가 새 standalone body를 호출함: 예 (`return self._calculate_ks_c9306_cspf(...)` 단일 호출).
- ISO delegate fallback 유지: 예 (`_calculate_cspf_via_iso_delegate` private helper로 보존, 외부 호출 없음).
- 기존 delegate 대비 numeric diff: 0 (top key + bin key 전 항목 정확 일치).
- spot check: `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852` 통과.
- KS HSPF 영향: 없음.
- ISO calculator 영향: 없음 (`calculator_iso16358.py` 무수정).
- public API/result schema 변화: 없음 (`{cspf, annual_cooling_kwh, annual_power_kwh, bin_details}` 그대로).
- 후속 작업 후보 1개: **ISO `calculate_cspf` 안의 KS-aware 분기 제거 audit**. 이제 KS CSPF가 standalone으로 동작하므로 ISO `calculate_cspf`의 `power_interpolation_method=="ks_intersection"` 분기와 `_ks_intersection_power` wrapper는 KS path에서 더 이상 호출되지 않는다. 다른 region 중 `ks_intersection`을 쓰는 곳이 있는지(현재는 korea.json만), ISO common engine에서 안전하게 제거할 수 있는지를 audit-only로 정리하는 별도 turn이 다음 안전 단위.

### task 6 결과
- `git status` / `git diff --stat`로 source 변경 범위 = `core/calculator_ks_c9306.py` (337 insertions, 12 deletions) 단일 파일로 한정됨을 확인.
- source commit: `feat: implement KS C9306 CSPF standalone body` (hash `a6ac560`).
- 본 report 파일을 `result_reports/active/039_implement-ks-c9306-cspf-standalone-body.md`로 생성.
- report commit: `report: record KS C9306 CSPF standalone body` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py` → 통과.
- KS CSPF spot check (`korea.json`, declared_capacity=6000) → `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852` (standalone과 ISO delegate fallback 모두 동일).
- 모든 bin_details 9개 key가 standalone과 ISO delegate에서 정확 일치.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 동일.

## Changed Files
- `core/calculator_ks_c9306.py`
- `result_reports/active/039_implement-ks-c9306-cspf-standalone-body.md`

## Known Failures / Risks
- 16개 pre-existing ISO HSPF failures (case3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundary 등)는 본 변경과 무관.
- KS `_resolve_ks_cspf_points` / `_interpolate_ks_cspf`는 ISO `resolve_points` / `interpolate`와 별도로 동일 로직을 보유한다. ISO 측이 향후 진화하면 둘이 갈라질 수 있어 동기화 유지가 필요하다. 다만 ISO 측 CSPF main flow는 더 이상 KS path를 위해 호출되지 않으므로 ISO common engine 정리 audit(후속) 단계에서 명시적으로 책임 경계를 정할 수 있다.
- `_calculate_cspf_via_iso_delegate`은 main path에서 사용되지 않지만 비교/안전망 용도로 남겨 두었다. 향후 ISO `calculate_cspf`에서 KS-aware 분기가 제거되면 함께 제거 가능.
- KS standalone body는 Korea config 한 종류에 대해 ISO delegate와 bit-for-bit 동일 결과를 검증했지만, 다른 region(EN14825 등) 미래 도입 시에는 별도 검증이 필요하다.
- ISO common engine 자체는 손대지 않았으므로, India/Hong Kong/SASO/ISO T1 default 등 다른 CSPF region 경로에는 본 변경의 영향이 없다.

## Next Suggested Action
- **ISO `calculate_cspf` 안의 KS-aware 분기 제거 audit**: ISO common engine의 `power_interpolation_method=="ks_intersection"` 분기와 `_ks_intersection_power` wrapper, `_iso_boundary_eer_power`의 KS-overlap 부분이 현재 어떤 region에서 호출되는지 grep로 정리하고, KS CSPF가 standalone으로 분리된 지금 안전하게 제거 가능한지 / 어떤 호출 경로(예: UI/dispatcher 미사용 region)가 잠겨 있는지를 audit-only turn으로 식별. 이후 별도 turn에서 ISO 정리 구현.

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
- source commit: `a6ac560 feat: implement KS C9306 CSPF standalone body`
- report commit: `report: record KS C9306 CSPF standalone body`
- pushed branch: `origin/main`
