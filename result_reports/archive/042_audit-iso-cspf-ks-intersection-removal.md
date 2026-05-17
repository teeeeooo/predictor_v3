# 042_audit-iso-cspf-ks-intersection-removal

## Goal
- 041 cleanup으로 Korea CSPF의 ISO direct test caller가 사라진 시점에서, `core/calculator_iso16358.py` 안의 KS CSPF 전용 잔여물(`power_interpolation_method=="ks_intersection"` 분기 2곳, `_ks_intersection_power(...)` wrapper)이 (a) 실제로 어떤 호출 경로에서 아직 사용되는지, (b) 즉시 제거 가능한지, (c) 어떤 선행 조건/사이드이펙트가 있는지를 audit-only로 최종 확인한다. code/test/docs/config/UI는 일절 수정하지 않는다.

## Scope
- 읽기 전용 대상:
  - `core/calculator_iso16358.py` — CSPF KS 잔여물 식별 및 호출처 분석.
  - `core/calculator_ks_c9306.py` — KS standalone CSPF가 ISO에 의존하지 않음을 재확인.
  - `core/calculator_profiles.py`, `core/calculator_dispatcher.py` — KS dispatcher path.
  - `data/region_configs/*.json` — `power_interpolation_method` 분포.
  - `ui/calc_window.py`, `ui/calculators_2point.py` — UI가 ISO `ks_intersection` 분기에 도달하는지.
  - `tests/` — CSPF/HSPF 측 ISO direct caller 잔존 여부, integrity test 영향.

## Non-goals
- code / UI / tests / region config / docs / profile resolver / dispatcher / workbook 수정 금지.
- ISO `calculate_cspf` 로직 / `_iso_boundary_eer_power` / KS standalone body / KS HSPF body 수정 금지.
- ISO HSPF delegation block (`_ks_calculator()`, `KSC9306Calculator` import 공유) 제거 논의 확장 금지 — 본 audit는 CSPF KS intersection에 한정.
- 새 테스트 추가 / expected / tolerance / xfail-pass 변경 금지.
- 구현 작업 금지. 다음 구현 작업 후보 1개만 제안.

## Legacy Caller Check
- `grep -Rn "ISO16358Calculator.*korea.json\|korea.json.*ISO16358Calculator" tests ui core`
  - hit: `tests/test_iso16358_hspf_ks_oracle.py:30`, `:66` (둘 다 HSPF 경로: `_ks_hspf_bin`, `_variable_heating_bin` 호출. CSPF `calculate_cspf` 호출 없음).
  - CSPF 측 ISO direct caller: **0건**.
- `grep -Rn "test_korea_cspf_regression" tests`
  - hit: `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py:169 def test_korea_cspf_regression_matches_ks_c9306_calculator()` (041에서 rename + KS calculator로 전환됨).
- `grep -Rn "KSC9306Calculator.from_config_path" tests ui core`
  - hit: `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py:170` (rename된 Korea CSPF regression test), `core/calculator_dispatcher.py:64` (`ks_c9306` 분기 본문).
- 결론: Korea CSPF에 대한 ISO direct caller(CSPF main path 진입)는 testsuite 기준 0건. KS standalone path만 활성.

## ISO CSPF KS Residual Map
- `core/calculator_iso16358.py` 안 KS-aware 잔여물 (CSPF 한정):

| 위치 | 내용 | 영향 범위 |
|---|---|---|
| `:7` | `from core.calculator_ks_c9306 import KSC9306Calculator` | CSPF + HSPF 양쪽. HSPF delegation block이 `_ks_calculator()`로 KS 인스턴스를 만든다. **CSPF 제거만으로는 import 제거 불가.** |
| `:39` | `self.power_interpolation_method = self.config.get("power_interpolation_method", "capacity_linear")` | CSPF 일반 attribute. `iso_boundary_eer` 등 비-KS 값도 함께 보관. 제거 불가. |
| `:282-298` | `def _ks_intersection_power(self, tj, L_c_ref, resolved_points, lower_type, upper_type)` wrapper. 본문은 `self._ks_calculator()._ks_cspf_intersection_power(...)` 위임. | 호출처: 같은 파일 `_calculate_cspf_profile`(:2089), `calculate_cspf`(:2267) **두 곳뿐.** 외부 호출 없음 (`grep _ks_intersection_power core tests ui` 결과 ISO 파일 자체만). |
| `:653-654` | `def _ks_calculator(self): return KSC9306Calculator.from_iso_calculator(self)` | CSPF측 `_ks_intersection_power` + HSPF delegation 24+개에서 호출. CSPF 잔여물만으로 제거 불가. |
| `:2037-` `_calculate_cspf_profile` | cspf_test_profile 경로(T1/T3 region) | India / Hong Kong / SASO / ISO T1 default가 이 경로를 탄다. |
| `:2088-2089` | `_calculate_cspf_profile` 내부 `if self.power_interpolation_method == "ks_intersection": P_tj = self._ks_intersection_power(...)` | cspf_test_profile + ks_intersection 동시 region 없음 (모두 `iso_boundary_eer`). 활성 caller 0건의 **dead branch**. |
| `:2148-` `calculate_cspf` (non-profile path) | Korea처럼 `points`+`derived_rules` region 경로 | KS dispatcher가 이제 KS standalone으로 처리. |
| `:2266-2271` | non-profile `calculate_cspf` 내부 `if self.power_interpolation_method == "ks_intersection": ks_power = self._ks_intersection_power(...)` | korea.json만 이 분기를 트리거할 수 있었지만, 041 이후 CSPF 측 ISO direct caller 0건이라 활성 호출 없음. |
| `:401-` `_iso_boundary_eer_power` | ISO boundary EER power 계산 | India / Hong Kong / SASO / ISO T1 default가 사용. 비-KS 일반 로직. 제거 불가. |

- 결론: **CSPF 측 `_ks_intersection_power` wrapper와 두 ks_intersection 분기 모두 활성 caller 0건 (dead). HSPF delegation block(`_ks_calculator()`, `KSC9306Calculator` import)은 유지해야 함.**

## Config / Test / UI Usage Map
- `data/region_configs/*.json` 의 `power_interpolation_method`:
  - `korea.json:12` → `"ks_intersection"` (유일).
  - `iso_t1_default_2point.json:10`, `india_iseer.json:10`, `hong_kong.json:10`, `saso.json:16` → 모두 `"iso_boundary_eer"`.
- profile/dispatcher:
  - `core/calculator_profiles.py`: `ks_c9306_cspf` → `korea.json`, `calculator_id=ks_c9306`.
  - `core/calculator_dispatcher.py:64`: `ks_c9306` → `KSC9306Calculator.from_config_path(config_path)`. dispatcher 경유 시 KS standalone body 사용.
- UI:
  - `ui/calculators_2point.py:1047-1053`: `iso_t1_default_2point.json / india_iseer.json / hong_kong.json / saso.json` 4개만 `ISO16358Calculator`로 instantiate. **korea.json 미사용.**
  - `ui/calc_window.py:234-256` `scan_configs()`: standard에 "ahri" 들어간 config만 AHRI 콤보에 추가. korea.json은 `"standard": "KS C 9306"`이라 어디에도 추가되지 않아 UI 진입점 없음.
- tests:
  - CSPF `ISO16358Calculator(korea.json).calculate_cspf(...)` 직접 호출: **0건**.
  - HSPF `ISO16358Calculator(korea.json).<HSPF API>` 직접 호출: `tests/test_iso16358_hspf_ks_oracle.py:30,66`, `tests/test_iso16358_hspf_golden.py:1691` — CSPF 분기에 도달하지 않음. CSPF 잔여물 제거와 무관.
  - `tests/test_region_config_integrity.py:14-18` `ALLOWED_POWER_INTERPOLATION_METHODS = {"capacity_linear", "ks_intersection", "iso_boundary_eer"}`. `korea.json:12`이 `ks_intersection`을 쓰므로 valid set에 남아 있어야 한다 (allowed set에서 제거하면 integrity test 회귀).
  - `core/calculator_ks_c9306.py:441` `if power_interp_method == "ks_intersection": ks_power = self._ks_cspf_intersection_power(...)` — KS standalone body 내부 분기. ISO 측과 무관한 KS-자체 로직. ISO 잔여물 제거의 영향 없음.

## Removal Candidates
| # | 대상 | 위치 | 현재 호출 가능성 | 제거 가능 여부 | 제거 전 선행 조건 | 다음 구현 포함 |
|---|---|---|---|---|---|---|
| A | non-profile `calculate_cspf`의 `ks_intersection` 분기 | `core/calculator_iso16358.py:2266-2271` | 활성 caller 0건 (041 후 testsuite 기준). dead branch. | **즉시 제거 가능** | 없음 (외부 ad-hoc 스크립트 부재 가정 — 다음 turn에서 grep 재확인 권장) | **예** |
| B | `_calculate_cspf_profile`의 `ks_intersection` 분기 | `core/calculator_iso16358.py:2088-2089` | cspf_test_profile + ks_intersection 동시 region 부재. 042 시점에도 dead. | **즉시 제거 가능** | 없음 (cspf_test_profile region이 미래에 ks_intersection을 쓸 정책 결정 없음) | **예** |
| C | `_ks_intersection_power(...)` wrapper | `core/calculator_iso16358.py:282-298` | A/B 분기에서만 호출. 외부 호출 0건. | **즉시 제거 가능** | A, B 분기 제거와 동시 진행 | **예** |
| D | `KSC9306Calculator` import (`:7`) | ISO module top-level | HSPF delegation block 24+ wrappers가 `_ks_calculator()` 통해 사용 | **불가** | HSPF delegation block 정리 audit/구현 (별도 사이클) | 아니오 |
| E | `_ks_calculator()` 팩토리 (`:653-654`) | ISO module | C (CSPF wrapper) + HSPF delegation 24개 | **불가** | D와 동일 | 아니오 |
| F | `tests/test_region_config_integrity.py:16` `"ks_intersection"` valid entry | integrity test 정책 | `korea.json:12`이 ks_intersection 사용 중. valid set에 유지 필요. | **불가** | korea.json의 `power_interpolation_method` 자체 정책 결정 + KS standalone body의 ks_intersection 분기 정리 | 아니오 |
| G | `korea.json` `power_interpolation_method="ks_intersection"` | region config | KS standalone body가 `self.config.get("power_interpolation_method")`로 읽어 `ks_intersection`일 때 KS intersection 사용. 제거하면 KS standalone 결과가 capacity_linear fallback으로 바뀌어 회귀. | **불가** | KS standalone body의 ks_intersection 분기 정책 결정 + spot check 재검증 | 아니오 |

## Recommended Next Action
- **후보: ISO CSPF `ks_intersection` 분기 + `_ks_intersection_power` wrapper 제거 (Removal Candidates A + B + C 묶음)**
  - 목적: 041 이후 활성 caller가 사라진 ISO CSPF `ks_intersection` 분기 두 곳과 `_ks_intersection_power` wrapper를 한 번에 제거한다. ISO common engine에서 KS CSPF 전용 잔여물이 사라지며, KS CSPF는 `KSC9306Calculator._calculate_ks_c9306_cspf(...)`가 단독 책임을 진다.
  - 수정 대상 예상 파일:
    - `core/calculator_iso16358.py` — wrapper(line 282-298, 약 17줄) + non-profile path 분기(line 2266-2271, 약 6줄) + cspf_test_profile path 분기(line 2088-2089, 약 2줄) 제거. 약 25-30줄 감소 예상. else로 떨어지는 분기 정리(`elif self.power_interpolation_method == "iso_boundary_eer"`가 `if`로 바뀔 수 있음 — 비교 정합성 유지).
    - 새 result report 1개.
  - 금지해야 할 작업:
    - `KSC9306Calculator` import (`:7`) 제거 금지.
    - `_ks_calculator()` 팩토리 (`:653-654`) 제거 금지.
    - HSPF delegation block (line 645-803) 일절 수정 금지.
    - KS module (`core/calculator_ks_c9306.py`) 수정 금지 — KS standalone body의 ks_intersection 분기는 유지.
    - `tests/test_region_config_integrity.py`의 valid set 수정 금지.
    - `data/region_configs/korea.json` 수정 금지.
    - profile resolver / dispatcher / UI / fixtures / docs / 다른 tests 수정 금지.
    - 새 test 추가 금지.
  - 검증 방법:
    - `grep -Rn "ks_intersection\|_ks_intersection_power" core/calculator_iso16358.py` → 0건.
    - `grep -Rn "_ks_intersection_power" core tests ui` → 0건 (KS module도 wrapper를 갖고 있지 않으므로).
    - `grep -Rn "ks_intersection" core tests ui` → KS module 본체(`core/calculator_ks_c9306.py:441`)와 integrity test allowed set / 주석만 잔존.
    - `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py`.
    - KS CSPF spot check (`cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852`) 유지.
    - `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` 통과.
    - 전체 `python3 -B -m pytest tests -q`로 baseline `269 passed, 16 failed, 13 xfailed` 동일 유지.
  - 왜 지금 이 순서가 안전한가:
    - 041 cleanup 직후라 CSPF 측 활성 caller 0건이 grep으로 검증됨. ks_intersection 분기 제거가 어떤 active 테스트/UI도 깨지 않는다.
    - HSPF delegation은 무수정이므로 HSPF 측 ISO direct test(`test_iso16358_hspf_ks_oracle.py`, `test_iso16358_hspf_golden.py`)는 영향 없음.
    - 다른 region(India/Hong Kong/SASO/ISO T1 default)은 모두 `iso_boundary_eer`라 `ks_intersection` 분기를 한 번도 트리거하지 않았다. `_iso_boundary_eer` 분기는 그대로 남는다.
    - KS standalone body가 ks_intersection 책임을 단독으로 갖게 되어 책임 경계가 명확해진다.
    - F/G (integrity test allowed set, korea.json 자체)는 KS standalone에 영향을 주므로 별도 사이클로 분리하는 것이 안전.
  - 짧은 구현 프롬프트 초안 (참고용, 본 작업에서 실행 금지):
    > `core/calculator_iso16358.py`에서 `_ks_intersection_power` wrapper(line 282-298), `_calculate_cspf_profile`의 ks_intersection 분기(line 2088-2089), `calculate_cspf` non-profile의 ks_intersection 분기(line 2266-2271)만 제거한다. `KSC9306Calculator` import / `_ks_calculator()` 팩토리 / HSPF delegation block은 그대로 둔다. KS module / tests / region config / UI / docs / profile / dispatcher 수정 금지. spot check + baseline `269 passed, 16 failed, 13 xfailed` 동일 유지 확인 후 source/report 분리 commit + push.

## Risks
- 본 audit는 read-only path/reference grep 기반. 외부 스크립트(노트북, 사내 ad-hoc 분석, ML 파이프라인 etc.)가 `ISO16358Calculator("data/region_configs/korea.json").calculate_cspf(...)`를 호출하고 ks_intersection 분기 결과를 기대하고 있다면, 분기 제거 후 동일 입력에서 capacity_linear 보간 결과로 바뀌어 silent drift 가능. 다음 구현 turn에서 grep 재확인 + 가능하면 사용자에게 외부 caller 부재 확인 권장.
- `_calculate_cspf_profile`의 ks_intersection 분기(B)는 042 시점에는 활성 caller가 0건이지만, 미래에 cspf_test_profile region이 추가되며 ks_intersection을 요구할 가능성 자체는 막혀 있지 않다. 제거 시 "cspf_test_profile은 iso_boundary_eer만 지원" 정책을 사실상 확정하는 결과가 된다.
- ISO `_iso_boundary_eer_power` 호출이 `if self.power_interpolation_method == "ks_intersection": ... elif ... == "iso_boundary_eer": ...` 패턴에 묶여 있어, ks_intersection 분기를 삭제할 때 `elif`를 `if`로 바꾸는 미세한 형태 변경이 필요. 동작 의미는 동일하지만 diff가 약간 늘어남.
- `tests/test_region_config_integrity.py`의 valid set은 본 후속 작업에서 수정 금지지만, ISO 코드에 ks_intersection 분기가 사라진 뒤에도 `korea.json:12`이 여전히 `ks_intersection`을 명시하면 의미 불일치(legacy 값)가 생긴다. KS standalone body가 그 값을 직접 사용하기 때문에 silent drift는 없지만, 정책 일관성을 위해 추후 별도 audit 필요.
- HSPF delegation block(line 645-803)은 이번 후속 작업에서도 그대로 유지된다. ISO HSPF의 KS 의존 정리는 별도 audit/구현 사이클이 필요하며, CSPF 정리 완료 후에도 `KSC9306Calculator` import / `_ks_calculator()` 팩토리는 ISO 모듈에 남는다.

## Scope Compliance
- code: 수정하지 않았음.
- UI: 수정하지 않았음.
- tests: 수정하지 않았음.
- fixtures/golden expected: 수정하지 않았음.
- docs: 수정하지 않았음.
- profile resolver code: 수정하지 않았음.
- dispatcher code: 수정하지 않았음.
- region config JSON: 수정하지 않았음 (`data/region_configs/*.json` 그대로, `korea.json` 포함).
- workbook/reference_files: 수정하지 않았음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- report commit: `report: audit ISO CSPF KS intersection removal`
- pushed branch: `origin/main`
