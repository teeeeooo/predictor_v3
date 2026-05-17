# 034_audit-calculator-ui-profile-dispatcher-wiring

## Goal
- Calculator UI(`ui/calc_window.py`, `ui/calculators_2point.py`)가 현재 어떤 방식으로 사용자 입력을 받아 calculator 인스턴스를 생성·호출하는지 감사하고, profile resolver/dispatcher 기반 전환을 위한 최소 안전 단계와 다음 구현 작업 후보 1건을 식별한다. code/test/docs/config/UI는 수정하지 않는다.

## Scope
- `ui/calc_window.py` (412 lines) 의 calculator tab 구성, 입력 위젯, 영역별 calculator 인스턴스화 흐름.
- `ui/calculators_2point.py` (1387 lines) 의 `IsoCspfSingleWidget`와 CSPF profile selector(`ISO / ISEER 2점식`, `Hong Kong CSPF`, `SASO T3`) 동작.
- `core/calculator_profiles.py`에 등록된 profile 목록과 `core/calculator_dispatcher.py`가 지원하는 `calculator_id` 매트릭스와의 비교.

## Non-goals
- UI 코드 / calculator code / dispatcher code / profile manifest 수정 금지.
- tests / fixture / golden expected / region config JSON 수정 금지.
- docs 수정 금지 (result report 생성만 허용).
- 새 profile 등록 / 새 UI selector / 새 입력 스키마 / EN14825 활성화 / KS HSPF UI 설계 등 어떤 구현도 수행하지 않는다.

## Current UI Input Map
- Calculator window 탭 구성 (`ui/calc_window.py:65-77`):
  - Tab 1 `ISO 16358`: `IsoCspfSingleWidget(self.config_dir)` 임베드. CSPF 전용 (HSPF UI 없음).
  - Tab 2 `EN 14825`: stub. `on_region_changed_en()`은 pass.
  - Tab 3 `AHRI 210/240`: SEER2 cooling 입력 4그룹과 HSPF2 v3 heating 입력 1그룹.
- ISO 탭 (`IsoCspfSingleWidget`, `ui/calculators_2point.py:1021~`):
  - `combo_profile`: `ISO / ISEER 2점식`(PROFILE_TWO_POINT), `Hong Kong CSPF`(PROFILE_HONG_KONG), `SASO T3`(PROFILE_SASO_T3). KS / Korea CSPF 선택지 없음.
  - 입력 grid: 2-point 모드에서 `35 Full`, `35 Half`. SASO 필수 `46 Full / 35 Full / 35 Half`, optional `35 Min`.
  - `declared_capacity` 입력은 별도 placeholder가 보이지 않으며, Hong Kong/SASO 등 `building_load_source=declared` 흐름은 widget 내부에서 처리 (구체 form은 calculators_2point의 panel 구성에 의존).
- AHRI 탭 (`ui/calc_window.py:123~`):
  - Cooling SEER2: A_Full, B_Full, B_Low, E_Int, F_Low 등 5개 시험점의 cap/pow + `Cd_default_low`, `t_off`, `t_on` 등.
  - Heating HSPF2 v3: `H42, H32, H22, H12, H1N, H11, H2Int, H21, H32_low, H4_low` test point 묶음과 `t_off`, `t_on`, `defrost_t_test_minutes`, `defrost_t_max_minutes`.
- HSPF (non-AHRI): UI에 ISO HSPF / KS HSPF / EN HSPF 진입점 없음. 따라서 HSPF 측 dispatcher wiring은 아직 UI 입력 자체가 부재한 상태.

## Current Calculator Construction Map
- `ui/calc_window.py`:
  - `self.config_dir = os.path.join(self.project_root, "data", "region_configs")` (line 42) — UI가 region_configs 폴더를 직접 알고 있다.
  - `scan_configs()` (line 233~) — `os.listdir(self.config_dir)`로 `.json` 목록을 만들어 AHRI 영역 dropdown(`self.combo_region_ahri`)을 채운다. profile resolver를 사용하지 않는다.
  - `on_region_changed_ahri()` (line 264~) — 선택된 파일명으로 `AHRICalculator(path)` 직접 생성. `_load_hspf2_calc()`도 호출.
  - `_load_hspf2_calc()` (line 276~) — `os.path.join(self.project_root, "data", "region_configs", "usa_hspf2.json")` 하드코딩 경로로 `AHRIHSPF2Calculator(...)` 직접 생성.
  - `calculate_*` 호출 (line 353/363/398/404) — `self.ahri_calc.calculate_seer2(...)`와 `self.hspf2_calc.calculate_hspf2_v3(test_points, **kwargs)` 직접 호출.
- `ui/calculators_2point.py`:
  - `IsoCspfSingleWidget._load_calculators()` (line 1045~) — 다음 4개 파일을 ISO16358Calculator로 직접 instantiate한다:
    - `iso_t1_default_2point.json` → `self.calculators["iso"]`
    - `india_iseer.json` → `self.calculators["india"]`
    - `hong_kong.json` → `self.calculators["hong_kong"]`
    - `saso.json` → `self.calculators["saso"]`
  - `_saso_calculator(use_min)` (line 1309~) — SASO 호출 시 `ISO16358Calculator(self.saso_path)`를 새로 만들고 `calculator.config.setdefault("cspf_test_profile", {})["test_selection"] = "required_only"`로 in-place 변경한다. min 사용 여부에 따른 분기.
  - `calculate_cspf(...)` 호출 위치 (lines 279, 280, 1219, 1249, 1288) — 4 profile + SASO 모두 ISO16358Calculator 인스턴스에서 직접.
- `core/calculator_profiles.py` / `core/calculator_dispatcher.py`: UI 코드에서 import / 호출 흔적 없음. 둘 다 미사용 상태.

## Hardcoded Configs
- `ui/calc_window.py`:
  - `data/region_configs/` 폴더 경로 (config_dir).
  - `data/region_configs/usa_hspf2.json` (HSPF2 calc path).
  - AHRI SEER2 영역은 폴더 scan 결과 dropdown — 사용자가 어떤 `.json`이라도 고를 수 있음 (현재 manifest의 `ahri_usa_seer2` 단일 profile과 1:1 매칭이 보장되지 않음).
- `ui/calculators_2point.py`:
  - `iso_t1_default_2point.json`, `india_iseer.json`, `hong_kong.json`, `saso.json` (4-config 묶음).
  - 별도 `self.saso_path = os.path.join(self.config_dir, "saso.json")`.
- KS C 9306 (`korea.json`)는 UI 어느 곳에서도 참조되지 않음.

## Dispatcher Readiness
- **AHRI HSPF2** — Manifest에 `ahri_usa_hspf2` profile (`config_path=data/region_configs/usa_hspf2.json`) 등록 완료, dispatcher가 `ahri_hspf2` 분기 지원. UI는 동일 경로를 하드코딩으로 한 번만 로드 (`_load_hspf2_calc`). 즉시 dispatcher 전환 가능 (drop-in 1곳).
- **AHRI SEER2** — Manifest에 `ahri_usa_seer2` profile 등록 완료, dispatcher가 `ahri_seer2` 분기 지원. UI는 region_configs 폴더 scan 후 사용자가 임의 파일을 고르도록 되어 있어 dispatcher가 가정하는 “profile → 단일 config_path” 매핑과 동치가 아니다. dispatcher 전환은 단일 USA SEER2 profile로 고정하거나, filename→profile_id 매핑 정책을 정한 뒤 가능. 선행 작업 필요.
- **KS C 9306 CSPF** — Manifest에 `ks_c9306_cspf` profile (`korea.json`) 등록 완료, dispatcher가 `ks_c9306` 분기 지원 (`KSC9306Calculator.from_config_path`). 단, UI에 Korea selector / Korea 입력 schema (declared_capacity와 KS-specific points 35_full / 35_half / 29_min)가 없다. 선행 작업 필요 (Korea profile combo entry 추가 + 입력 schema 정렬).
- **KS C 9306 HSPF** — Manifest와 dispatcher는 ready. UI에 HSPF 진입점 자체가 없다 (AHRI HSPF2만 존재). 별도 UI 설계 필요. 보류.
- **ISO T1 CSPF / India ISEER / Hong Kong CSPF** — Manifest에 profile 미등록. UI는 ISO16358Calculator를 직접 생성. profile manifest 등록과 dispatcher 분기(`iso16358`) 추가가 선행되어야 dispatcher 전환 가능.
- **SASO T3 CSPF** — Manifest에 profile 미등록. UI는 호출 시 `cspf_test_profile.test_selection`을 `required_only`로 in-place 변경. dispatcher가 인스턴스를 매번 새로 만들면 이 mutation도 매번 반복 필요. profile 등록 + override 처리 정책 설계 필요.
- **EN14825** — UI tab은 stub. profile/dispatcher 모두 미준비. 보류.

## Recommended Next Action
**후보: AHRI HSPF2 UI 한 곳을 dispatcher 기반으로 전환**

- **목적**: `ui/calc_window.py:_load_hspf2_calc()`의 하드코딩된 `AHRIHSPF2Calculator(path)` 호출을 `create_calculator_for_profile(profile_id="ahri_usa_hspf2")`로 교체해, 실제 UI 경로 1개를 dispatcher로 검증한다. behavior-preserving wiring의 첫 단계.
- **수정 대상 예상 파일**:
  - `ui/calc_window.py` (`_load_hspf2_calc` 1개 메서드, 약 5줄 변경 예상)
  - 새 result report 1개
  - 필요 시 `tests/test_calc_window_hspf2_dispatcher.py` 같은 가벼운 smoke test 1건 추가 검토 (옵션)
- **금지해야 할 작업**:
  - AHRI HSPF2 calculator 본문 수정 금지.
  - AHRI SEER2 dispatcher 전환을 같은 turn에 시도하지 말 것 (filename scan dropdown 정책 결정이 별도 필요).
  - ISO/HK/India/SASO/KS UI 전환을 같이 시도하지 말 것 (profile manifest 미등록 또는 입력 schema 부재).
  - `data/region_configs/usa_hspf2.json` 수정 금지.
  - EN14825 tab 활성화 금지.
- **검증 방법**:
  - `python3 -B -m py_compile ui/calc_window.py core/calculator_dispatcher.py core/calculator_profiles.py core/calculator_ahri_hspf2.py`.
  - `python3 -B -m pytest tests -q -k "ahri or hspf2 or dispatcher or profile"`로 회귀 없음 확인.
  - 전체 `python3 -B -m pytest tests -q`가 baseline `269 passed, 16 failed, 13 xfailed`와 동일한 통계 유지.
  - 수동: Calculator UI를 띄워 AHRI 탭의 HSPF2 입력 → 계산 결과가 dispatcher 전환 전과 동일한지 spot check (가능한 환경에서).
- **왜 지금 이 순서가 안전한가**:
  - AHRI HSPF2는 manifest profile과 dispatcher 분기가 모두 준비되어 있다 (보고 030/032).
  - UI 호출 경로가 단일 메서드(`_load_hspf2_calc`)에 고정되어 있고, config path가 한 곳만 하드코딩되어 있어 1:1 drop-in이 가능하다.
  - 입력 schema(test point 묶음)는 그대로 두므로 사용자 입력/계산 결과 행동이 변하지 않는다.
  - AHRI SEER2처럼 filename scan dropdown 정책을 정해야 하는 케이스보다 위험이 낮다.
  - KS C 9306이나 ISO/HK/India/SASO 전환을 시도하려면 새 selector 추가 또는 profile manifest 확장이 선행되어야 하므로, 이번 한 단계로 dispatcher 사용 패턴을 안전하게 검증한 뒤 단계적으로 확장하는 것이 합리적이다.

## Risks
- 본 audit는 path/reference 기준으로 수행했으며 실제 UI 실행 동작은 확인하지 않았다 (calc_window를 띄우는 smoke test는 수행하지 않음). 다음 구현 turn에서 수동 확인 또는 가벼운 smoke test가 권장된다.
- AHRI SEER2 dropdown이 `region_configs/`의 모든 `.json`을 후보로 노출하는 현재 동작은 `usa_hspf2.json` / `korea.json` 등 SEER2 용도가 아닌 파일도 사용자에게 보일 수 있다 (실 사용 시 잘못 선택하면 calculator 생성 단계에서 실패). dispatcher 전환 시 SEER2 profile 단일 또는 SEER2-only filter가 필요하다.
- `IsoCspfSingleWidget._saso_calculator(use_min)`은 ISO16358Calculator의 `config` dict를 in-place 수정한다. dispatcher 전환 시 매번 새 인스턴스를 만들고 같은 mutation을 반복하는 방식 또는 profile-level override 정책을 정해야 한다.
- KS C 9306 CSPF UI 연결은 입력 schema 차이 (`declared_capacity`, `35_full / 35_half / 29_min`) 때문에 단순 dropdown 추가만으로는 부족하며 별도 작업으로 분리해야 한다.
- 본 audit 결과 자체는 코드/문서/테스트에 변화가 없으므로 baseline `269 passed, 16 failed, 13 xfailed`에 영향이 없다. 다음 구현 turn에서 회귀 없음을 baseline 비교로 다시 확인해야 한다.

## Scope Compliance
- code: 수정하지 않았음.
- UI: 수정하지 않았음.
- tests: 수정하지 않았음.
- fixtures/golden expected: 수정하지 않았음.
- docs: 수정하지 않았음.
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 그대로).
- dispatcher code: 수정하지 않았음 (`core/calculator_dispatcher.py` 그대로).
- region config JSON: 수정하지 않았음.
- workbook/reference_files: 수정하지 않았음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- report commit: `report: audit calculator UI dispatcher wiring`
- pushed branch: `origin/main`
