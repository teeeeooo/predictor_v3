# 036_audit-ks-c9306-cspf-iso-dependency

## Goal
- `KSC9306Calculator.calculate_cspf()`가 아직 ISO common CSPF engine에 delegate하고 있는 현재 구조를 감사하고, KS C 9306 CSPF를 독립 calculator로 만들기 위해 옮겨야 할 최소 로직 단위와 다음 구현 작업 후보 1건을 식별한다. code/test/docs/config/UI는 수정하지 않는다.

## Scope
- `core/calculator_ks_c9306.py`의 `KSC9306Calculator` 진입점(`calculate_cspf`, `calculate_hspf`, `from_config_path`, `from_iso_calculator`, `_ks_cspf_*` helper).
- `core/calculator_iso16358.py`의 KS-aware footprint (`_round_test_value`, `_prepare_measured_inputs`, `resolve_points`, `_ks_intersection_power` thin wrapper, `_calculate_cspf_profile`, `calculate_cspf` 안의 KS 분기).
- `data/region_configs/korea.json`의 KS-specific config flag 확인 (값 변경 없음).
- 기존 KS 회귀 가드 테스트의 존재만 확인.

## Non-goals
- calculator/dispatcher/profile resolver/UI 코드 / region config JSON / tests / fixtures / docs 수정 금지.
- ISO common HSPF, AS/NZS workbook oracle, AHRI dispatch 작업 금지.
- 새 테스트 추가, 구현 실행, expected/tolerance/xfail/pass 수정 금지.
- ISO `calculate_cspf`의 `ks_intersection` 분기 제거 또는 ISO common engine reorganize 금지.

## Current KS CSPF Entry Flow
- `core/calculator_ks_c9306.py:63-81`의 `KSC9306Calculator.calculate_cspf(measured_inputs, declared_capacity=None)`:
  - `self._iso_calculator_ref`가 설정되어 있으면 (`from_iso_calculator` 경유) 그 ISO 인스턴스의 `calculate_cspf(measured_inputs, declared_capacity=...)`를 직접 호출하고 결과를 그대로 반환한다.
  - 그렇지 않으면 lazy import (`from core.calculator_iso16358 import ISO16358Calculator`) 후 `self._config_path`로 새 ISO16358Calculator 인스턴스를 만들고 `calculate_cspf(measured_inputs, declared_capacity=...)`를 호출한다.
  - `_config_path`도 없는 경우 명확한 `ValueError` fail-fast.
- KS CSPF 본문(measured input preparation, reference point resolution, bin loop, cycling/saturated/interp regime, accumulation, result composition)은 KS 모듈 안에 존재하지 않는다. 현재 `calculate_cspf`는 compatibility wrapper / thin delegate이지 독립 계산 entry가 아니다.
- KS CSPF helper (`_ks_cspf_performance_line`, `_ks_cspf_intersection_power`)는 KS 모듈 안에 존재하지만, 호출은 ISO common engine 내부의 `_ks_intersection_power` thin wrapper(`core/calculator_iso16358.py:282`)에서 일어난다. 즉, helper만 KS 모듈에 있고 호출 흐름은 여전히 ISO engine 안에서 시작된다.
- KS HSPF entry (`KSC9306Calculator.calculate_hspf`, line 829)는 `_calculate_ks_c9306_hspf`로 위임되어 KS 모듈 안에서 독립 계산을 수행한다. KS CSPF와는 분리된 상태.

## ISO Dependency Map
ISO common engine 안에 남아 있는 KS-aware / KS-driven 잔여물:

| # | 위치 | 코드 | 성격 |
|---|---|---|---|
| 1 | `core/calculator_iso16358.py:35-39` (`__init__`) | `self.round_test_values`, `self.rounding_method`, `self.power_interpolation_method`, `self.building_load_source`, `self.reference_point` 파싱 | generic config flag지만 production에서는 `korea.json`이 KS-specific 값으로 활성화한다 |
| 2 | `core/calculator_iso16358.py:48-53` | `_round_test_value(value)` ROUND_HALF_UP helper. docstring에 “KS C 9306 시험값 정수 반올림용 helper입니다” | KS naming이지만 generic Decimal helper. ISO `_prepare_measured_inputs`와 `resolve_points`에서만 호출됨 |
| 3 | `core/calculator_iso16358.py:65-85` | `_prepare_measured_inputs(measured_inputs)` — `round_test_values=true`일 때 `capacity`/`power`를 `_round_test_value`로 정수화 | `calculate_cspf`와 `calculate_hspf`의 첫 단계에서 호출. 현재 production에서는 Korea만 활성화 |
| 4 | `core/calculator_iso16358.py:205-207` (`resolve_points` 내부) | `if self.round_test_values: resolved[point_key]["capacity"] = self._round_test_value(...)` | resolved point 재정수화 |
| 5 | `core/calculator_iso16358.py:282` | `_ks_intersection_power(...)` thin wrapper → `_ks_calculator()._ks_cspf_intersection_power(...)` | KS helper로 위임하는 wrapper. KS 모듈로 옮긴 본체와 동일 시그니처 |
| 6 | `core/calculator_iso16358.py:2088-2089` (`_calculate_cspf_profile` 내부) | `if self.power_interpolation_method == "ks_intersection": P_tj = self._ks_intersection_power(...)` | `cspf_test_profile`이 있는 경로의 KS-aware 분기 |
| 7 | `core/calculator_iso16358.py:2148-`, `2177-2178` (`calculate_cspf`) | `if self.round_test_values: declared_capacity = self._round_test_value(declared_capacity)` | declared building load 정수화 (Korea의 `building_load_source=declared` 경로) |
| 8 | `core/calculator_iso16358.py:2266-2272` (`calculate_cspf` 내부) | `if self.power_interpolation_method == "ks_intersection": ks_power = self._ks_intersection_power(...)` | non-profile CSPF 경로의 KS-aware 분기 (Korea 실 사용 경로) |

`data/region_configs/korea.json`의 KS-driving flags:
- `power_interpolation_method: "ks_intersection"` (현재 production에서 Korea만 사용 — 보고 027/030에서 확인).
- `round_test_values: true` (현재 production에서 Korea만 활성화).
- `rounding_method: "nearest_integer_half_up"`.
- `building_load_source: "declared"` (Hong Kong도 사용하지만 HK는 `iso_boundary_eer`, ks-intersection 아님).
- `reference_point: "35_full"`, `t_100_load: 35.0`, `t_0_load: 23.0`, `Cd: 0.25` (config-driven, KS-special 아님).

## KS Residual Logic Map
KS calculator 안에 이미 자리한 KS-specific 자산:
- `KSC9306Calculator._ks_cspf_performance_line(resolved_points, load_type)` — `core/calculator_ks_c9306.py:87`.
- `KSC9306Calculator._ks_cspf_intersection_power(tj, L_c_ref, resolved_points, lower_type, upper_type, t_100_load, t_0_load)` — line 110.
- `KSC9306Calculator.calculate_hspf(...)` 및 그 backing helpers (`_validate_ks_*`, `_ks_hspf_*`, `_calculate_ks_c9306_hspf`) — line 829 등. KS HSPF는 이미 self-contained.
- 인스턴스 상태: `config` (Korea JSON dict), `bin_hours`, `Cd`, optional `_config_path`, `_iso_calculator_ref`.

KS calculator에 아직 없는 것 (CSPF 독립화에 필요한 책임):
- measured input 자체 전처리 (`_prepare_measured_inputs` / `_round_test_value`).
- reference / declared building load 처리 (`declared_capacity`에 대한 KS 전용 정수화 및 `building_load_source=declared` 분기).
- bin loop, `Lc = L_c_ref * (tj - t_0_load) / delta_t`, cycling/saturated/interp regime 결정, accumulation (`cstl`, `csec`), result dict 구성 (`cspf`, `annual_cooling_kwh`, `annual_power_kwh`, `bin_details`).
- `_ks_cspf_intersection_power`를 직접 호출하는 interp regime 분기 (현재는 ISO common engine이 wrapper로 호출).
- `resolve_points` (현재 ISO common helper)의 KS-compatible 버전.

## Extraction Candidates
| 대상 함수/분기 | 현재 위치 | 이동 후보 | 필요한 입력 | 계산 결과 변경 위험 | 다음 작업 포함 여부 |
|---|---|---|---|---|---|
| `KSC9306Calculator.calculate_cspf` | KS (delegate-only) | KS 자체 본문으로 reimplement | measured_inputs, declared_capacity, config | 매우 큼 — 전 CSPF 흐름 복제 | 보류 (큰 단위, 단계 분할 필요) |
| `_ks_intersection_power` thin wrapper | ISO `core/calculator_iso16358.py:282` | 제거 후보 (KS 본체 이미 KS 모듈에 존재) | tj, L_c_ref, resolved_points, lower/upper_type | 낮음 — 단 ISO `calculate_cspf` 호출부(line 2089/2267)도 동시에 KS로 라우팅하지 않으면 production Korea path가 끊김 | KS CSPF 본문 reimplement 이후 |
| `_ks_cspf_intersection_power`, `_ks_cspf_performance_line` | KS module (이미 이동 완료) | 변경 없음 | (이미 self-contained) | 0 | 완료 |
| `_round_test_value` | ISO `core/calculator_iso16358.py:48` | KS module로 복제 (ISO도 유지) | value | 낮음 — `Decimal.quantize(...,ROUND_HALF_UP)`는 idempotent하므로 KS 측 선 호출 + ISO 측 후 호출이 동일 결과 보존 | KS measured input preparation 분리 시 함께 |
| `_prepare_measured_inputs` | ISO `core/calculator_iso16358.py:65` | KS module 측에도 동일 본문 복제. ISO 측은 유지 (idempotent 가정) | measured_inputs | 낮음 (idempotent) | KS measured input preparation 분리 시 본체 |
| `power_interpolation_method == "ks_intersection"` 분기 | ISO `_calculate_cspf_profile` (line 2088-2089), `calculate_cspf` (line 2266-2272) | ISO에서 제거하고 KS module 내부 self-contained CSPF 분기로 옮김 | — | 큼 — KS dispatch가 `KSC9306Calculator.calculate_cspf` 본문을 통해 직접 계산하기 전이면 production Korea path가 끊긴다 | KS CSPF 본문 reimplement 이후 |
| `building_load_source=declared` + `round_test_values` declared 정수화 (line 2177-2178) | ISO `calculate_cspf` | KS module 측에서 self-contained 처리 | declared_capacity | 중간 — KS reimplement에 포함 | KS CSPF 본문 reimplement 시 |
| Korea config의 `cspf_test_profile` / `round_test_values` / `power_interpolation_method` | data/region_configs/korea.json | KS calculator가 자기 config 해석을 갖는 형태로 정렬 | — | 0 (값 그대로 유지) | KS reimplement 완료 후 ISO common engine을 KS-unaware로 정리할 때 |

당장 안전하게 이동 가능한 가장 작은 단위:
- KS측 measured input preparation (`_prepare_measured_inputs` + `_round_test_value`)을 KS module 내부에 복제한다. KS module의 `calculate_cspf` 진입점에서 measured_inputs를 자기 helper로 전처리한 뒤 ISO engine에 넘긴다.
- `_round_test_value`는 idempotent (`Decimal(str(int)).quantize(Decimal("1"), ROUND_HALF_UP)`는 이미 정수인 값은 그대로 반환)하므로, KS 전처리 후 ISO 측이 다시 `_prepare_measured_inputs`를 호출해도 결과가 변하지 않는다.
- `declared_capacity`에 대한 정수화도 KS calculator 측에서 선행할 수 있다 (idempotent 동일 이유).

당장 옮기면 너무 커지거나 위험한 단위:
- ISO `calculate_cspf` 본문 전체 복제 — bin loop, regime 결정, accumulation, result dict 구성까지 한 번에 옮기면 차이가 의도치 않게 들어갈 위험.
- ISO 측 `ks_intersection` 분기 제거 — KS dispatch가 KS module에서 self-contained로 처리되기 전에는 production Korea path가 끊긴다.
- `resolve_points` reimplementation — ISO common helper로서 다른 region 경로와 공유되므로 KS 전용 복제는 KS reimplement 단계에서 함께 고려.

## Recommended Next Action
**후보: KS C 9306 measured input preparation만 KS module로 분리**

- **목적**: `KSC9306Calculator`에 KS-specific measured input 전처리 helper (`_prepare_measured_inputs`, `_round_test_value`)를 복제·소유하게 만든다. KS `calculate_cspf` 진입점에서 incoming `measured_inputs`와 `declared_capacity`를 KS 측 helper로 선전처리한 뒤 ISO engine으로 위임한다. ISO common engine은 그대로 유지하며 이중 전처리가 일어나도 idempotent하므로 production 결과가 변하지 않는다. KS CSPF 독립화의 가장 작은 첫 단위이다.
- **수정 대상 예상 파일**:
  - `core/calculator_ks_c9306.py` (KS-specific `_prepare_measured_inputs`, `_round_test_value` 메서드 추가 + `calculate_cspf` 진입점에서 선전처리 호출 + `declared_capacity` 정수화)
  - 필요 시 idempotency / spot-check를 위한 가벼운 unit test 1건 (`tests/test_ks_c9306_measured_input_preparation.py` 같은 이름)을 추가하는 것은 옵션. 추가하지 않더라도 기존 `test_korea_cspf_regression_unchanged_by_diagnostics`가 production-equivalent regression guard 역할을 한다.
- **금지해야 할 작업**:
  - `core/calculator_iso16358.py` 수정 금지 (`_prepare_measured_inputs`, `_round_test_value`, `calculate_cspf`, `_calculate_cspf_profile` 본문 그대로).
  - ISO `ks_intersection` 분기 제거 금지.
  - `_ks_intersection_power` thin wrapper 제거 금지.
  - `data/region_configs/korea.json` 값 변경 금지.
  - profile resolver / dispatcher / UI 수정 금지.
  - 새 KS CSPF body 작성, bin loop 복제, accumulation 복제 금지.
- **검증 방법**:
  - `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py`.
  - Spot check: `KSC9306Calculator.from_config_path("data/region_configs/korea.json").calculate_cspf(...)` 결과가 보고 027의 기준값 (`cspf=6.504`, `annual_cooling_kwh=1943.798`, `annual_power_kwh=298.852`)와 정확히 일치하는지 확인.
  - `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` 통과.
  - 전체 `python3 -B -m pytest tests -q`가 baseline `269 passed, 16 failed, 13 xfailed`와 동일한 통계와 failure set 유지.
- **왜 지금 이 순서가 안전한가**:
  - `_round_test_value`가 idempotent하므로 KS 선전처리 + ISO 후전처리가 동일 결과를 낸다. 즉 “behavior-preserving 더블 호출”이 가능한 안전한 경계.
  - ISO common engine과 `ks_intersection` 분기를 그대로 두므로 production Korea dispatch (`ISO16358Calculator(korea.json).calculate_cspf(...)` 직접 호출 경로 / `KSC9306Calculator.calculate_cspf(...)` delegate 경로) 모두 같은 ISO path를 거치고 결과가 변하지 않는다.
  - KS calculator가 자기 입력 전처리에 대한 self-contained 책임을 갖는 첫 단계가 되어, 후속 turn에서 reference point resolution → bin loop / regime → ks_intersection 호출 → result composition 순으로 점진적으로 본체를 옮길 수 있다.
  - 이미 존재하는 `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py::test_korea_cspf_regression_unchanged_by_diagnostics`가 production Korea CSPF 결과 회귀 가드 역할을 하므로 추가 characterization 없이도 안전성을 검증할 수 있다.
  - Bigger reimplementation (full CSPF body 복제, ISO `ks_intersection` 분기 제거)은 한 turn으로 처리할 위험이 크고 ISO common engine 정리와 짝지어야 하므로 더 작은 단위로 분할되는 것이 합리적이다.

- 구현 프롬프트 초안(다음 turn에서 사용):
  - 제목: “KS C 9306 measured input preparation을 KSC9306Calculator로 분리”
  - 범위: `core/calculator_ks_c9306.py`만 수정. `_prepare_measured_inputs(measured_inputs)`와 `_round_test_value(value)` (KS-specific 본문)을 KS module 내부에 복제하고 `calculate_cspf` 진입점에서 호출. ISO module은 수정하지 않음.
  - 금지: ISO `_prepare_measured_inputs`/`_round_test_value` 수정 금지, ISO `calculate_cspf` 수정 금지, `_ks_intersection_power` wrapper 제거 금지, region config 수정 금지, tests/fixture/golden expected 수정 금지, dispatcher/UI/profile resolver 수정 금지.
  - 검증: 위 “검증 방법” 참고.

## Risks
- 본 audit는 path/reference 기반이며 ISO common engine 실제 호출 흐름을 단일 단계 시뮬레이션하지 않았다 (테스트는 별도 baseline 비교로 검증).
- `_round_test_value`의 idempotency는 `Decimal(str(value)).quantize(Decimal("1"), ROUND_HALF_UP)`이 정수 입력에 대해 동일 정수를 반환하는 사실에 기대고 있다. 사람이 만든 float이 한 번 quantize되어 정수가 되면, 두 번째 호출은 동일 정수를 반환한다. 그러나 float `value`가 NaN/inf 같은 극단값이라면 `InvalidOperation`이 발생할 수 있다. KS preprocessing 단계에서 이미 idempotent guard 적용을 유지하면 충분히 안전하다.
- KS CSPF 독립화 전체 흐름(measured prep → resolve → bin loop → regime → intersection → accumulation → result dict)을 한 turn에 옮기면 production 회귀 위험이 크다. 따라서 추천된 first step은 measured prep만 분리하는 가장 작은 단위에 한정한다.
- ISO common engine 안의 KS-aware 분기(`ks_intersection`, `round_test_values`, `building_load_source=declared`)는 다음 단계가 KS module에서 self-contained body로 분리되기 전까지는 그대로 남아 있다. 이 기간 동안 “문서 contract는 KS calculator가 Korea config를 해석한다”라고 명시되어 있어도 실제 runtime path는 부분적으로 ISO module을 거친다.
- 본 audit 자체는 코드/문서/테스트에 변화가 없으므로 baseline `269 passed, 16 failed, 13 xfailed`에 영향이 없다. 다음 구현 turn에서 회귀 없음을 baseline 비교로 다시 확인해야 한다.

## Scope Compliance
- code: 수정하지 않았음.
- UI: 수정하지 않았음.
- tests: 수정하지 않았음.
- fixtures/golden expected: 수정하지 않았음.
- docs: 수정하지 않았음.
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 그대로).
- dispatcher code: 수정하지 않았음 (`core/calculator_dispatcher.py` 그대로).
- region config JSON: 수정하지 않았음 (`data/region_configs/korea.json` 등 그대로).
- workbook/reference_files: 수정하지 않았음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- report commit: `report: audit KS C9306 CSPF ISO dependency`
- pushed branch: `origin/main`
