# 040_audit-iso-cspf-ks-aware-branch-removal

## Goal
- 039에서 `KSC9306Calculator._calculate_ks_c9306_cspf(...)` standalone body 구현이 완료된 시점에서, `core/calculator_iso16358.py` 안에 남은 KS-aware CSPF 잔여물(`power_interpolation_method=="ks_intersection"` 분기, `_ks_intersection_power` wrapper, `KSC9306Calculator` import 등)이 (a) 어떤 호출 경로에서 아직 사용되는지, (b) 즉시 제거 가능한지, (c) 어떤 선행 작업이 필요한지를 audit-only로 정리한다. code/test/docs/config/UI는 일절 수정하지 않는다.

## Scope
- 읽기 전용 대상:
  - `core/calculator_ks_c9306.py` — KS standalone 경로 확인.
  - `core/calculator_iso16358.py` — KS-aware 잔여물 식별.
  - `core/calculator_profiles.py`, `core/calculator_dispatcher.py` — KS profile 호출 경로.
  - `data/region_configs/*.json` — `power_interpolation_method` 사용 분포.
  - `ui/calc_window.py`, `ui/calculators_2point.py` — KS 직접 호출 경로 유무.
  - `tests/` — `korea.json` / `ISO16358Calculator` / `KSC9306Calculator` 호출 경로.

## Non-goals
- code/UI/tests/region config/docs/profile/dispatcher/workbook 수정 금지.
- ISO `calculate_cspf` 로직, KS standalone body, KS HSPF body 수정 금지.
- 새 테스트 추가 또는 expected/tolerance/xfail/pass 변경 금지.
- 구현 작업 수행 금지 (다음 작업 후보 1개만 제안).
- KS HSPF delegation block (`ISO16358Calculator._ks_hspf_*`, line 645-803) 제거 가능성은 본 audit 범위 밖 — 본 audit는 CSPF 잔여물에 한정.

## KS Standalone Confirmation
- `core/calculator_ks_c9306.py`
  - `calculate_cspf` (line 527-528): 단 한 줄 `return self._calculate_ks_c9306_cspf(measured_inputs, declared_capacity)` 호출. ISO delegate 호출 없음.
  - `_calculate_ks_c9306_cspf` (line 320~): 037 입력 정수화 + 038 point resolution + 039 standalone bin loop / regime / accumulation을 KS module 내부에서 전부 수행.
  - `_resolve_ks_cspf_points` (line 177), `_interpolate_ks_cspf`, `_ks_cspf_intersection_power` (line 557) 모두 KS module 내부에서 자급자족.
  - `_calculate_cspf_via_iso_delegate` (line 493): 함수 정의 본문과 자신의 ValueError 메시지 외에 KS module 내 호출처 없음. UI/dispatcher/test에서도 호출처 없음(외부 grep 0건). main path에서 사용되지 않는 dead code (안전망 보존 목적).
- 결론: KS CSPF main path는 ISO delegate에 더 이상 의존하지 않는다.

## ISO KS-Aware Residual Map
`core/calculator_iso16358.py`에 남은 KS 흔적을 분류:

1. **`from core.calculator_ks_c9306 import KSC9306Calculator` (line 7)**
   - 카테고리: KS-only. CSPF + HSPF 양쪽에서 KS 모듈을 호출하기 위함.
   - 현재 사용처: `_ks_calculator()` (line 653)에서 호출 → CSPF 측 `_ks_intersection_power`와 HSPF delegation block(line 645-803) 양쪽이 사용.
   - HSPF delegation이 ISO HSPF 경로의 KS 분기를 유지하는 한 import 제거 불가.

2. **`_ks_calculator()` 팩토리 (line 653-654)**
   - 카테고리: KS-only.
   - 현재 사용처: `_ks_intersection_power`(CSPF) + 24+개 KS HSPF delegation wrapper(line 657-798).
   - HSPF 측 delegation이 살아 있는 한 제거 불가.

3. **`_ks_intersection_power(self, tj, L_c_ref, resolved_points, lower_type, upper_type)` (line 282-298)**
   - 카테고리: KS-only.
   - 현재 사용처: 같은 파일의 `_calculate_cspf_profile` (line 2089), `calculate_cspf` (line 2267) 두 분기에서만 호출. 외부 사용 없음 (`grep _ks_intersection_power core/ ui/ tests/`에서 ISO 파일 내부 호출만 보임).
   - ISO 측 두 분기와 함께 제거 가능 (호출처 동시 정리).

4. **CSPF `_calculate_cspf_profile` 안의 `ks_intersection` 분기 (line 2088-2089)**
   - 카테고리: KS-only.
   - 현재 사용처: `_has_cspf_test_profile()`이 True인 region(India T1, Hong Kong, SASO, ISO T1 default) + `power_interpolation_method=="ks_intersection"` 동시 만족 region에서 호출.
   - 실제 region별 분포: cspf_test_profile을 쓰는 4개 region 모두 `power_interpolation_method`가 `iso_boundary_eer`. 즉 현재 dead branch.
   - 다만 미래에 `cspf_test_profile`을 쓰면서 KS intersection을 요구하는 region이 등장하지 않는다는 정책 결정이 있어야 안전하게 제거 가능.

5. **CSPF main `calculate_cspf` 안의 `ks_intersection` 분기 (line 2266-2271)**
   - 카테고리: KS-only.
   - 현재 사용처: `_has_cspf_test_profile()`이 False인 region 중 `power_interpolation_method=="ks_intersection"`인 region. **현재 유일한 매칭 region: `data/region_configs/korea.json`**.
   - 직접 호출 경로 (지금 활성):
     - `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py:169-170` `test_korea_cspf_regression_unchanged_by_diagnostics` — `ISO16358Calculator("data/region_configs/korea.json").calculate_cspf(...)` 직접 호출. KS dispatcher를 거치지 않고 ISO로 직진.
   - 즉, ISO main `ks_intersection` 분기를 지금 제거하면 위 test가 깨진다. 선행: test caller를 `KSC9306Calculator`로 전환하거나 ISO main 분기를 우회하는 정책 결정.

6. **`round_test_values` / `rounding_method` (line 37-38), `_round_test_value` (line 48-53), `_prepare_measured_inputs` (line 65-85)**
   - 카테고리: 이름은 KS 출처지만 ISO common infra로 확장된 상태.
   - 현재 사용처:
     - `_prepare_measured_inputs`: line 1935 (HSPF 경로), line 2160 (CSPF 경로).
     - `_round_test_value`: 위 + line 205-207 (`resolve_points`의 derived 정수화) + line 2178 (declared_capacity 정수화).
     - 모두 `round_test_values=True`일 때만 동작. Korea 외 region은 false라 사실상 no-op이지만, ISO HSPF / CSPF 양쪽 공통 진입점에 박혀 있어 KS-only로 단정 불가.
   - HSPF 측에서도 ISO16358Calculator(korea.json).calculate_hspf(...) 직접 호출 테스트(`tests/test_iso16358_hspf_ks_oracle.py:30,66`, `tests/test_iso16358_hspf_golden.py:1691`)가 존재해 즉시 제거 시 회귀 발생.
   - 결론: 이름은 KS이지만 ISO infra 책임으로 유지. CSPF 잔여물 제거 단계에서는 건드리지 않는다.

7. **KSC9306Calculator import + `_ks_calculator()` + KS HSPF delegation block (line 7, 653-803)**
   - 카테고리: HSPF 책임 (본 audit 범위 밖).
   - HSPF는 아직 ISO→KS delegation 패턴을 유지한다. CSPF 잔여물 제거와 별개 audit/구현 사이클이 필요.

## Caller / Config Usage Map
- `power_interpolation_method == "ks_intersection"`을 쓰는 region (전 region config 스캔):
  - `data/region_configs/korea.json:12` (유일).
  - 나머지 (`iso_t1_default_2point.json`, `india_iseer.json`, `hong_kong.json`, `saso.json`)는 모두 `iso_boundary_eer`.
- KS CSPF dispatcher 경로:
  - `core/calculator_profiles.py:39-45`: `ks_c9306_cspf` profile → `config_path=data/region_configs/korea.json`, `calculator_id=ks_c9306`.
  - `core/calculator_dispatcher.py:62-64`: `ks_c9306` → `KSC9306Calculator.from_config_path(config_path)`.
  - dispatcher 통과 시 KS standalone body 사용 → ISO 측 ks_intersection 분기는 호출되지 않음.
- UI 측 직접 호출 (`ui/calc_window.py`, `ui/calculators_2point.py`):
  - `ui/calculators_2point.py:279,280,1219,1249,1288`: ISO16358Calculator로 `iso_t1_default_2point.json`, `india_iseer.json`, `hong_kong.json`, `saso.json` CSPF 호출. **`korea.json` 호출 없음**, `KSC9306Calculator` 호출 없음.
  - `ui/calc_window.py`: AHRI SEER2/HSPF2만 처리. KS CSPF 미연결.
  - 결론: UI에서 ISO ks_intersection 분기 호출 없음.
- tests 측 직접 호출:
  - `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py:169-170` `test_korea_cspf_regression_unchanged_by_diagnostics`: `ISO16358Calculator("data/region_configs/korea.json").calculate_cspf(...)` 직접 호출. **ISO main `ks_intersection` 분기를 실행하는 유일한 활성 caller.** 기준값 `cspf=6.504/cooling=1943.798/power=298.852` 검증.
  - `tests/test_iso16358_hspf_ks_oracle.py:30,66`, `tests/test_iso16358_hspf_golden.py:1691`: korea.json을 ISO로 직접 사용하지만 HSPF 호출 (CSPF 잔여물 제거와 무관).
  - `tests/test_region_config_integrity.py:7,16`: korea.json + `ks_intersection`을 valid value로 enumerate. 정책 검증 테스트.
  - `tests/test_calculator_profiles.py:110,120`: ks_c9306 profile snapshot.

## Removal Candidates
| # | 대상 | 위치 | 현재 호출 가능성 | 제거 가능 여부 | 제거 전 선행 조건 | 추천 다음 작업 |
|---|---|---|---|---|---|---|
| A | `KSC9306Calculator._calculate_cspf_via_iso_delegate` | `core/calculator_ks_c9306.py:493` | 0 callers (자기 ValueError 메시지만 셀프참조) | **즉시 제거 가능** | 없음 (dead code) | **예 (최저 위험)** |
| B | ISO `calculate_cspf` main의 `ks_intersection` 분기 | `core/calculator_iso16358.py:2266-2271` | `test_korea_cspf_regression_unchanged_by_diagnostics` (활성 caller 1개) | 직접 호출 caller 전환 후 가능 | (C)/(F) 선행 | 아니오 (선행 필요) |
| C | `test_korea_cspf_regression_unchanged_by_diagnostics` caller 전환 | `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py:168-181` | 활성 | caller만 `KSC9306Calculator.from_config_path("data/region_configs/korea.json")`로 바꿔 동일 expected 유지 | expected 변경 금지, 같은 입력/같은 기준값 유지 | 아니오 (B/D 전환 사이클의 일부, 별도 작업) |
| D | ISO `_ks_intersection_power` wrapper | `core/calculator_iso16358.py:282-298` | (B) + (E) 분기에서만 호출 | (B)/(E) 제거 직후 가능 | (B)/(E) 선행 | 아니오 (B 이후) |
| E | ISO `_calculate_cspf_profile`의 `ks_intersection` 분기 | `core/calculator_iso16358.py:2088-2089` | cspf_test_profile + ks_intersection 동시 region 부재 (dead branch) | 정책 결정 필요 | "cspf_test_profile region은 iso_boundary_eer만" 명시 | 아니오 (정책 단계) |
| F | ISO `from core.calculator_ks_c9306 import KSC9306Calculator` | `core/calculator_iso16358.py:7` | `_ks_calculator()` → CSPF (D) + HSPF delegation 24+개 | 불가 (HSPF 의존) | HSPF 측 ISO→KS delegation 제거 audit + 구현 | 아니오 (HSPF 사이클) |
| G | ISO `_ks_calculator()` 팩토리 | `core/calculator_iso16358.py:653-654` | (D) + HSPF delegation 24개 | 불가 | (F)와 동일 | 아니오 |
| H | ISO `round_test_values`/`rounding_method`/`_round_test_value`/`_prepare_measured_inputs` | `core/calculator_iso16358.py:37-85, 205-207, 1935, 2160, 2178` | ISO HSPF + CSPF 공통 경로 + `ISO16358Calculator(korea.json).calculate_hspf/cspf` 직접 호출 test | **불가**. 이름만 KS이고 ISO common infra 책임 | 영구 유지 또는 별도 naming-only 리팩토링 | 아니오 (naming-only 작업) |
| I | `data/region_configs/korea.json` (수정/이동) | 단일 KS CSPF/HSPF config | 활성 (dispatcher + 직접 호출 test 다수) | **불가** | 본 audit 범위 밖 | 아니오 |

## Recommended Next Action
- **후보: KS CSPF dead delegate 제거 (Option 4 / Removal Candidate A)**
  - 목적: `KSC9306Calculator._calculate_cspf_via_iso_delegate(...)`를 제거한다. 039에서 standalone body 검증이 끝나 비교/안전망 용도가 더 이상 필요 없다. callers 0개를 grep으로 재확인하고, KS module에서 정의/ValueError 메시지 블록 한 군데만 삭제.
  - 수정 대상 예상 파일:
    - `core/calculator_ks_c9306.py` (한 메서드 정의 블록 삭제, 약 30줄 추정).
    - 새 result report 1개.
  - 금지해야 할 작업:
    - `core/calculator_iso16358.py` 수정 금지 (ISO ks_intersection 분기/wrapper/import 유지).
    - `KSC9306Calculator.calculate_cspf` / `_calculate_ks_c9306_cspf` / KS CSPF helpers / KS HSPF 수정 금지.
    - tests / fixtures / docs / region config / UI / profile resolver / dispatcher 수정 금지.
    - 새 테스트 추가 금지, `_calculate_cspf_via_iso_delegate` 대체 helper 추가 금지.
  - 검증 방법:
    - `grep -n _calculate_cspf_via_iso_delegate core/ tests/ ui/`로 호출처 0건 재확인.
    - `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py`.
    - KS CSPF spot check `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852` 유지 확인.
    - `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` 통과.
    - 전체 `python3 -B -m pytest tests -q`로 baseline `269 passed, 16 failed, 13 xfailed` 동일 유지 확인.
  - 왜 지금 이 순서가 안전한가:
    - callers 0개로 입증된 dead code. ISO 코드에 손대지 않으므로 ks_intersection 사용처(`test_korea_cspf_regression_unchanged_by_diagnostics`)에 영향 0.
    - HSPF delegation / ISO common infra / 다른 region CSPF에 모두 영향 없음.
    - Option B (ISO ks_intersection 분기 제거), Option D (ISO wrapper 제거)는 직접 caller test 전환(Option C)이 선행되어야 안전한데, 본 audit는 그 caller 전환을 자체 작업으로 분리할지를 사용자 정책 결정에 맡긴다. 그 사이 dead delegate 제거(Option 4)는 ISO 정리와 무관하게 진행 가능한 최저 위험 단위.
    - Option 5 (`_round_test_value`/`_prepare_measured_inputs` naming 정리)는 ISO HSPF/CSPF 공통 infra라 KS-only로 분리해 옮기는 작업 자체가 별도 audit/설계가 필요. 우선순위 낮음.
  - 짧은 구현 프롬프트 초안 (참고용, 본 작업에서 실행 금지):
    > KSC9306Calculator의 `_calculate_cspf_via_iso_delegate` 메서드 정의 블록만 삭제한다. 다른 코드/테스트/문서/설정/UI는 일절 수정하지 않는다. spot check (`cspf=6.504/cooling=1943.798/power=298.852`)와 baseline `269 passed, 16 failed, 13 xfailed`로 회귀 없음을 확인한 뒤 source/report 분리 commit + push.

## Risks
- 본 audit는 read-only path/reference grep 기반이며, 실제 UI 실행이나 외부 caller(외부 스크립트, ML 파이프라인 등) 호출 동작은 확인하지 않았다. `_calculate_cspf_via_iso_delegate`를 외부에서 reflection으로 호출하는 코드가 있을 가능성은 낮지만, 다음 구현 turn에서 grep 재확인이 필요하다.
- ISO `ks_intersection` 분기 제거(Option B)는 `test_korea_cspf_regression_unchanged_by_diagnostics`를 깨므로, 그 test가 “ISO direct path와 KS path의 등가성”을 명시적으로 검증하려는 의도라면 caller 전환 시 의미가 약해진다. 정책 결정자가 그 test의 목적을 재확인하는 것이 안전.
- ISO HSPF delegation block(line 645-803, 24+ wrappers)은 본 CSPF audit 범위 밖이며, HSPF 측 standalone 전환이 별도 audit/구현 사이클로 다뤄져야 한다. CSPF 잔여물만 정리해도 HSPF 측 KS import/`_ks_calculator()`는 그대로 남는다.
- `round_test_values`/`_round_test_value`/`_prepare_measured_inputs`는 이름은 KS이지만 ISO HSPF/CSPF 공통 infra로 사용되고 있어 즉시 제거 불가. 이름이 KS인 것에 끌려 잘못 제거하면 ISO HSPF 회귀가 발생.
- Korea 외 region에서 `power_interpolation_method=="ks_intersection"`을 설정하는 새 config가 추가되면 ISO 분기 제거가 또 어려워진다. region config integrity test(`test_region_config_integrity.py:7,16`)가 valid set을 유지 중이라 우발적 추가는 막혀 있지만, 정책 결정이 필요한 사안.

## Scope Compliance
- code: 수정하지 않았음.
- UI: 수정하지 않았음.
- tests: 수정하지 않았음.
- fixtures/golden expected: 수정하지 않았음.
- docs: 수정하지 않았음.
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 그대로).
- dispatcher code: 수정하지 않았음 (`core/calculator_dispatcher.py` 그대로).
- region config JSON: 수정하지 않았음 (`data/region_configs/*.json` 그대로, `korea.json` 포함).
- workbook/reference_files: 수정하지 않았음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- report commit: `report: audit ISO CSPF KS-aware branch removal`
- pushed branch: `origin/main`
