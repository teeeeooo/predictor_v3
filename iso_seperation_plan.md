# Calculator Series Reset — Implementation Plan (Steps 1–5)

## Status

Completed on `work/iso-separation-plan`. Final state is summarized in `iso_separation_result.md` and `iso_remaining_work_completion.md`.

- Legacy mixed ISO code now lives at `core/_legacy/calculator_iso16358_legacy.py`.
- Active ISO formula/validation failures from the completion pass are fixed.
- Current local AS/NZS workbook HSPF/CSPF compatibility is implemented under `ASNZS_EXCEL_COMPAT`.
- Historical case3 full-dump parity remains Z-phase.

## Context

037~043 사이클로 `core/calculator_iso16358.py` 안의 KS 잔여물을 부분 cleanup해 왔지만, ISO/KS/ASNZS 책임이 한 파일에 누적된 구조 자체가 정렬되지 않는다는 것이 확인되었다. Step 0 (문서/계획 reset, commit `f81e94b`)으로 방향을 **legacy 격하 + 새 calculator 3종 재작성**으로 확정했다. 이 plan은 그 뒤를 잇는 Step 1~5의 실행 계획이다.

KS C 9306 standalone body (039) / legacy delegate 제거 (041) / ISO ks_intersection 분기 제거 (043)는 이미 완료되었고, audit 결과 KS HSPF는 ISO 의존이 없는 fully standalone 상태다. 따라서 Step 1은 닫힘 작업이고, Step 2의 rename은 31 test files + 3 UI sites + dispatcher reference를 한 commit으로 atomic하게 끊는다. 새 ISO calculator (Step 3)는 KS/ASNZS 책임을 처음부터 가지지 않는 clean module로 작성한다.

**Design decisions (이번 plan 한정):**
- Legacy/archive tests → `tests/_legacy/` 새 디렉터리로 이동.
- Step 2 직후~Step 5 사이 UI는 임시로 `core.calculator_iso16358_legacy`를 import해 동작 유지.
- Step 2는 rename + 모든 import update를 한 commit (atomic green→green).

---

## Current State (audit summary)

- `core/calculator_ks_c9306.py` (1243 lines): CSPF/HSPF 모두 standalone. ISO 모듈 import 없음. `_iso_calculator_ref`는 `from_iso_calculator()` factory 전용 (ISO→KS HSPF delegation block에서만 사용됨).
- `core/calculator_iso16358.py`: line 7 `KSC9306Calculator` import + line 635-782 HSPF delegation block (24+ wrappers + `_calculate_ks_c9306_hspf`) 잔존.
- ISO16358Calculator 직접 import 사이트: **31 test files + 3 UI 사이트 (`ui/calculators_2point.py:12, 1053, 1310`)**.
- Korea config 직접 consumer: `core/calculator_profiles.py:45,55`, `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py:170` (이미 KS 사용), `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py`, `tests/test_iso16358_hspf_ks_oracle.py:30,66`, `tests/test_region_config_integrity.py:7`.
- UI 4개 ISO config (`iso_t1_default_2point.json / india_iseer.json / hong_kong.json / saso.json`) → `ISO16358Calculator(path)` 직접 인스턴스화. Korea config는 UI 진입점 없음.
- profile/dispatcher: `ks_c9306_cspf / ks_c9306_hspf / ahri_usa_seer2 / ahri_usa_hspf2`만 등록. `iso16358` profile 없음.
- Baseline: `269 passed, 16 failed, 13 xfailed` (16 failures는 모두 pre-existing ISO HSPF, 본 plan과 무관).

---

## Step 1 — KSC9306Calculator 완성

KS는 이미 standalone이므로 잔여 cleanup + KS-측 test 사이트 이전이 본질.

### 1a. KS module cleanup (1 cycle, source + report commit 분리)
- 수정 대상: `core/calculator_ks_c9306.py`
- 작업:
  - "ISO common path와 분리된" 식의 transition-시기 주석 정리 (ex. line 57 `power_interpolation_method=ks_intersection` 주석은 사실 정보로 유지).
  - `from_iso_calculator(iso_calculator)` factory의 운명 결정: ISO HSPF delegation block(Step 2에서 legacy로 격하)이 호출처의 전부이므로, Step 2 rename 직후 dead가 됨. **본 단계에서는 유지하고, Step 2 완료 후 별도 cycle에서 제거.**
  - `_iso_calculator_ref` 필드도 동일 결정.
- 검증: `python3 -B -m py_compile core/calculator_ks_c9306.py`, KS CSPF spot check (`cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852`), KS-tag pytest 전부 pass.

### 1b. KS HSPF/CSPF test 사이트 이전 (1 cycle)
- 수정 대상:
  - `tests/test_iso16358_hspf_ks_oracle.py` (line 30, 66) — `ISO16358Calculator("data/region_configs/korea.json")` → `KSC9306Calculator.from_config_path("data/region_configs/korea.json")`. `._ks_hspf_bin(...)`, `._variable_heating_bin(...)` 호출은 KS module의 동일 이름 method를 호출하도록 retarget (이미 KS module에 동일 method가 있는지 grep 확인 필요).
  - `tests/test_iso16358_hspf_validation.py` (line ~84-100, `test_ks_c9306_hspf_input_must_be_dict`) — `ISO16358Calculator` 경유를 `KSC9306Calculator`로 retarget.
  - `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py` — Korea config 사용 golden row만 `KSC9306Calculator`로 retarget. ISO common HSPF 부분은 그대로 legacy diagnostic으로 유지.
  - 파일명 자체 rename은 본 단계에서 보류 (Step 2 archive 단계에서 일괄 결정).
- 검증: 위 3개 파일 단독 pytest pass, KS-tag 회귀 0, 전체 baseline 유지.

---

## Step 2 — 기존 calculator_iso16358.py rename + 대량 test 정리

**한 atomic commit으로 진행** (rename + 31 test import update + 3 UI import update + dispatcher 참조 update + tests/_legacy/ 이동).

### 2a. Pre-rename audit (1 cycle, audit-only report)
- 수정 대상: 없음 (report만).
- 작업:
  - `tests/_legacy/` 후보 분류 표 작성:
    - **Pure ISO contract** (`iso_t1_default_*`, `iso_boundary_eer_*`, `clause67_*`, `official_tool_*`, `hspf_pure_iso_track_a`, `hspf_formula_micro`, `hspf_compatibility_boundary`, `hspf_smoke`, `hspf_validation` ISO 부분): Step 3에서 새 ISO 위에서 reactivate 대상. Step 2 시점에는 `_legacy` 모듈로 import retarget해 잠시 살림.
    - **Regional ISO (HK/India/SASO)** (`hong_kong_config`, `india_iseer_config`, `saso_config`, `saso_t3_regression`, `asean_report_examples`, `t3_profile`): Step 3 후반에 새 ISO 위에서 reactivate. Step 2 시점에는 `_legacy` 모듈 import.
    - **Diagnostic/mixed** (`profile_calculation`, `profile_resolver`, `h8_trace`, `cspf_fixture_validation`): `tests/_legacy/`로 이동 + import retarget. 새 calculator 위에서 다시 만들지는 보류.
    - **AS/NZS compat 9개** (`test_asnzs_hspf_excel_compat_*`): `_legacy` 모듈 import로 retarget. Step 4 시점에 새 ASNZS calculator로 다시 retarget.
  - 각 파일을 어디로 둘지 결정한 표를 report에 명시.
- 검증: 코드 무변경, baseline 동일 확인.

### 2b. Rename + 대량 retarget (1 atomic commit)
- 수정 대상:
  - `core/calculator_iso16358.py` → `core/calculator_iso16358_legacy.py` (git mv).
  - 새 `core/calculator_iso16358.py` 생성: skeleton 클래스 + `from core.calculator_iso16358_legacy import ISO16358Calculator as _LegacyISO16358Calculator  # transition`은 두지 않음. 정말 빈 skeleton.
    ```python
    """ISO 16358 CSPF/HSPF common standard calculator (new series).

    이 모듈은 Step 3에서 본문이 채워진다. 현재는 contract 시그니처만 표시한다.
    """

    class ISO16358Calculator:
        def __init__(self, config_path: str):
            raise NotImplementedError(
                "New ISO16358Calculator is not yet implemented. "
                "Use core.calculator_iso16358_legacy.ISO16358Calculator until "
                "Step 3 implementation lands."
            )

        def calculate_cspf(self, measured_inputs: dict, declared_capacity: float = None) -> dict:
            raise NotImplementedError

        def calculate_hspf(self, measured_inputs: dict) -> dict:
            raise NotImplementedError
    ```
  - 모든 ISO test (Step 2a에서 _legacy 분류된 것 전부): `from core.calculator_iso16358 import ISO16358Calculator` → `from core.calculator_iso16358_legacy import ISO16358Calculator`.
  - `tests/_legacy/` 디렉터리 생성, diagnostic/mixed 분류 test들을 `git mv`로 이동.
  - `tests/_legacy/__init__.py` 빈 파일 추가 (pytest collection 정상화).
  - UI `ui/calculators_2point.py:12, 1053, 1310`: 동일하게 `_legacy` 모듈 import (Step 5에서 다시 swap).
  - `core/calculator_dispatcher.py:44` docstring의 ISO 언급 정정 (legacy 표기).
- 검증:
  - `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_iso16358_legacy.py core/calculator_ks_c9306.py ui/calculators_2point.py`.
  - 전체 pytest baseline `269 passed, 16 failed, 13 xfailed` 동일 유지 (test 위치만 이동, behavior 변화 없음).
  - UI smoke: PyQt5 Calculator window가 띄워지고 ISO T1 default / India / Hong Kong / SASO 4개 config로 instantiate되는지 spot check (자동화 불가 시 사용자 측 manual).
  - `grep -Rn "from core.calculator_iso16358 import" core tests ui` → 새 ISO skeleton import만 (NotImplementedError 호출자 없음).

### 2c. KS factory dead code 제거 (1 cycle)
- 수정 대상: `core/calculator_ks_c9306.py`
- 작업:
  - Step 2b 완료 후 `from_iso_calculator(iso_calculator)` factory와 `_iso_calculator_ref` 필드의 호출처를 grep으로 0건 재확인.
  - 두 항목 모두 제거. `__init__`의 `self._iso_calculator_ref = None` 라인과 docstring 정리.
- 검증: spot check + KS pytest + baseline.

---

## Step 3 — 새 ISO16358Calculator 구현

CSPF → HSPF 순서. KS / AS/NZS / workbook helper / legacy diagnostic 흔적 일절 금지.

### 3a. CSPF skeleton + Hong Kong + ISO T1 default contract (1 cycle)
- 수정 대상: `core/calculator_iso16358.py`
- 작업:
  - `__init__(config_path)`: JSON 파싱, `points / derived_rules / bin_hours / Cd / t_100_load / t_0_load / reference_point / building_load_source / power_interpolation_method` 기본 검증. KS-specific keys (`round_test_values`, `rounding_method`, `ks_intersection` etc.)는 알지 않음.
  - `resolve_points(measured_inputs)`: ISO `points` + `derived_rules` 표준 해석.
  - `interpolate(tj, resolved_points)`: 온도 기준 선형 보간.
  - `_calculate_cspf_profile(measured, L_c_ref)`: `cspf_test_profile` 기반 T1/T3 (HK/India/SASO/ISO T1 default).
  - `calculate_cspf(measured_inputs, declared_capacity=None)`: bin loop / regime / `iso_boundary_eer` / capacity-linear fallback. `ks_intersection` 분기 없음, `_ks_intersection_power` 없음, `_round_test_value` 호출 없음.
  - `_iso_boundary_eer_power(...)` + 보조 (`_iso_boundary_temperature`, `_iso_linear_29_35`, `_iso_boundary_eer`, `_iso_boundary_eer_t3_piecewise`)를 legacy에서 직접 이식 (ISO 전용이므로 안전).
- Test reactivation (같은 commit):
  - Hong Kong / India / SASO / ISO T1 default CSPF 관련 test의 import를 `_legacy`에서 새 `core.calculator_iso16358`로 다시 swap.
- 검증:
  - 위 4개 region CSPF test 전부 pass.
  - Korea CSPF spot check는 KS calculator에서 계속 통과.
  - `_legacy` 모듈에 남은 test가 여전히 pass (legacy implementation 유지).
  - Baseline 269 passed 유지.

### 3b. HSPF skeleton + Hong Kong + ISO T1 default contract (1 cycle)
- 수정 대상: `core/calculator_iso16358.py`
- 작업:
  - `calculate_hspf(measured_inputs)`: ISO 16358-2 standard. KS HSPF / workbook oracle / `_ks_hspf_*` 일절 없음.
  - `_variable_heating_bin(...)` 등 ISO 공통 HSPF helper만 이식.
- Test reactivation: ISO HSPF golden / pure ISO Track A / formula micro / smoke / validation 중 ISO common 부분을 새 모듈로 재연결.
- 검증: 위 test 전부 pass, baseline 유지.

### 3c. Regional ISO HSPF (필요 시 추가 cycle)
- Hong Kong HSPF (`tests/test_iso16358_hspf_hong_kong_config.py` 등)도 새 ISO로 retarget.

---

## Step 4 — AS/NZS workbook oracle calculator

**중요 audit 결과 (plan 작성 중 발견):** `core/calculator_asnzs_hspf_excel.py`는 **이미 존재** (267 lines, 15 methods, complete skeleton). 14개 `test_asnzs_hspf_excel_compat_*.py`도 이미 작성되어 현재 `8 passed, 1 xfailed` 상태로 동작 중. ISO legacy 모듈에는 ASNZS 로직이 0건이고, 9개 ASNZS test의 `ISO16358Calculator` import는 모두 **negative assertion**(ISO common에 helper가 들어가지 않았음을 guard)이다. 따라서 Step 4의 실제 작업은 원래 plan보다 훨씬 작다.

**진행 메모 (Step 4 실행 후):** ASNZS negative assertion tests는 새 `core.calculator_iso16358` target으로 전환했다. `reference_files/iso16358_test_sheet.xlsx` current workbook snapshot은 `tests/fixtures/asnzs_excel_hspf_compat/workbook_inverter_ac_current.json`로 분리했고, exact-match는 `core/calculator_asnzs_hspf_excel.py`의 `ASNZS_EXCEL_COMPAT` path에서만 검증한다. Historical case3 packet/full-dump parity는 여전히 Z-phase다.

### 4a. ASNZS negative-assertion test의 import target 재확인 (1 cycle)
- 수정 대상:
  - `tests/test_asnzs_hspf_excel_compat_*.py` 중 `from core.calculator_iso16358 import ISO16358Calculator as iso` 패턴 사용 파일들.
  - Step 2b에서 일괄 `_legacy` 모듈로 retarget됐을 것이고, Step 3a/3b에서 ISO test가 새 모듈로 다시 swap될 때 ASNZS의 negative-assertion target도 다시 검토 필요.
- 작업:
  - 각 negative assertion이 무엇을 검사하는지 확인 (예: ISO module source에 helper 함수가 없음, ISO class에 method가 없음, import path가 다름 등).
  - 새 ISO calculator(`core/calculator_iso16358.py`)는 ASNZS helper를 가지지 않도록 설계됐으므로, ASNZS test의 negative target을 새 ISO 모듈로 swap (확신이 있는 항목) 또는 `_legacy` 그대로 유지 (legacy 잔재 검증 의도가 있는 항목).
  - 14개 ASNZS test가 여전히 `8 passed, 1 xfailed` (또는 동등) 상태를 유지하도록 보존.
- 검증: ASNZS 14개 test pass/xfail 통계 동일 유지, baseline 회귀 0.

### 4b. ASNZS Excel exact-match 본 구현 — `reference_files/iso16358_test_sheet.xlsx` 기반으로 본 plan 범위 안 (FEASIBLE)

**Workbook investigation 결과 (plan 작성 중 추가 조사):** `reference_files/iso16358_test_sheet.xlsx`의 `Temp Bin hrs` 시트와 `Inverter AC` 시트에 case3와 다른 *현재 workbook state*에 대한 완전한 row-level data가 존재한다. case3 target(`hstl_kwh=1126.120 / hspf=4.33824 / ch48_wh=1126120.47`)은 다른 workbook snapshot의 결과이므로 그것 자체는 여전히 blocked이지만, **현재 workbook state에 대한 numeric exact-match는 본 plan에서 가능**하다.

**Workbook에서 확보 가능한 데이터:**

| 데이터 | 위치 | 비고 |
|---|---|---|
| Per-bin `hours` | `Temp Bin hrs` 시트, 헤더 row 7, data row 8+ | GENERIC / AS/NZS Hot & Humid / Mixed / Cold 프로파일 (Residential + Commercial) 8개 컬럼 |
| Per-bin tj (heating) | `Temp Bin hrs` K열 (row 8-49: -10°C ~ 25°C) | |
| Per-row `load_w` (building heat load) | `Inverter AC` BA열 (rows 21-47) | R21=3800, R22=3589, ... R47=0 |
| Per-row helper COPs | `Inverter AC` BN/BP/BR/BY/CA/CC열 (rows 21-47) | 5종 helper COP candidate per bin |
| Per-row selected power | `Inverter AC` CG열 (rows 21-47) | workbook이 helper들 중 선택해 출력한 actual power |
| Per-row CD power | `Inverter AC` CD열 (rows 21-47) | partial coverage (R21-23만 non-zero) |
| Per-row bin energy | `Inverter AC` CH열 (rows 21-47) | bin별 누적 energy |
| Seasonal total energy | `Inverter AC` `CH48` | 현재 workbook: **1145363 Wh** (= CHSE label) |
| H12 / H13 anchors | `Inverter AC` H12, H13 | 현재 workbook: **H12=1145 (kWh), H13=4.342** (case3와 다름) |

**case3와의 차이 (snapshot mismatch):**

- `case3_packet.json` 기록: CD21=1504.01, CH48=1126120.47, H12=1126.120, H13=4.33824.
- 현재 `reference_files/iso16358_test_sheet.xlsx`: CD21=1521, CH48=1145363, H12=1145, H13=4.342.
- 즉 case3는 **다른 workbook version**에서 추출된 결과이며, case3 그 자체를 재현하려면 Z-phase full_dump가 여전히 필요. 그러나 본 plan은 case3 target에 묶일 필요가 없다 (case3는 historical artifact로 xfail 유지).

**`docs/` 조사 결과 (보조):** `docs/iso16358/regions/aus/aus_notes.md`(region 정책 + season hours 표), `docs/iso16358/excel_com_runner_packet_protocol.md`(packet 규격만), `docs/designs/2026-05-08-asnzs-hspf-excel-compat-boundary.md`(Track B 설계 의도), `docs/iso16358/iso16358_dev_notes.md`(5개 sample 온도 routing 표)는 workbook 데이터 자체는 보유하지 않으나 routing/regime 설계 검증에는 유용.

**4b 본 구현 계획 (본 plan 안에 포함):**

#### 4b-1. Workbook fixture 추출 (1 cycle)

- 수정 대상:
  - `tests/fixtures/asnzs_excel_hspf_compat/workbook_inverter_ac_current.json` (새 파일)
  - 추출 스크립트는 commit하지 않고 1회용으로 사용 (또는 `scripts/dev/` 한 회용 헬퍼).
- 작업:
  - `reference_files/iso16358_test_sheet.xlsx`의 `Temp Bin hrs` (8-49행 heating 블록, GENERIC 컬럼)과 `Inverter AC` (21-47행 BA/BL/BN/BP/BR/BY/CA/CC/CD/CG/CH + 48행 CH48/BB)를 추출해 fixture JSON 작성.
  - workbook_version은 파일 크기/SHA + git blob hash로 표기 (extension `"workbook_source": "reference_files/iso16358_test_sheet.xlsx@<sha256>"`).
  - case3 fixture는 무수정 (historical).
- 검증: openpyxl로 fixture와 workbook 값 일치 spot check, 본 fixture는 numeric only (Excel formula 미포함).

#### 4b-2. Calculator 본 구현 + 새 exact-match contract test (1-2 cycle)

- 수정 대상:
  - `core/calculator_asnzs_hspf_excel.py` — 현재 skeleton(15 methods)에 누락된 부분 채움:
    - `_select_helper_cop(...)`이 BN/BP/BR/BY/CA/CC 중 row별 regime에 따라 selector 적용 (예: BL=1.0이면 BN, BL<1.0이면 다른 helper). 정확한 selection rule은 workbook 관찰 + `iso16358_dev_notes.md`의 routing 표로 도출.
    - `_component_power_from_load_and_cop(load_w, cop)` → load/cop. 이미 존재 확인됨.
    - `_component_energy_from_power(power_w, hours)` → power*hours. 이미 존재.
    - `_sum_component_energies(...)` 및 `_build_component_accumulation_result(...)` — workbook의 CH열 합 = CH48과 일치해야.
    - `calculate_hspf(workbook_input)` public entry — `tj/hours/load_w/helper_cops` per row를 받아 `hsec_wh / hstl_wh / hspf` 출력.
  - 새 `tests/test_asnzs_hspf_excel_compat_workbook_current_exact_match.py`:
    - 4b-1의 fixture 입력 → calculator 출력.
    - 기대값: `CH48=1145363 Wh` (계산 결과 hsec_wh와 일치, 정수 또는 1Wh tolerance), `H12=1145.x` (round/표기 일치), `H13=4.342` (round 후 일치).
    - case3 xfail은 그대로 유지.
- 작업 원칙:
  - ISO common path와 섞지 않음 (이미 격리됨).
  - 새 test는 ASNZS namespace에만.
  - workbook의 selection rule이 docs로 완전히 명세화되지 않은 부분은 fixture row를 보고 reverse-engineer해야 함 (BN/BP/BR/BY/CA/CC 중 어느 것이 CG가 되는지 patterning).
- 검증:
  - `python3 -B -m py_compile core/calculator_asnzs_hspf_excel.py`.
  - workbook-current exact-match test → `pass`.
  - 기존 14개 ASNZS test → `8 passed, 1 xfailed`(또는 동등) 유지 (case3 xfail 그대로).
  - Baseline 전체 test → 회귀 0 (단, ASNZS test count는 신규 1건 추가로 +1 명시).

#### 4b-3. Profile 등록 (Step 5a에 흡수)

- `core/calculator_profiles.py`에 `asnzs_excel_hspf_compat` profile 등록 (`calculator_id=asnzs_excel_hspf`, `enabled=False`, config_path는 fixture path 또는 별도 region config).
- dispatcher `asnzs_excel_hspf` 분기 추가.

**case3 fixture의 향후 처리:**

- case3는 xfail 유지 + 메타에 "extracted from workbook version unknown, current `iso16358_test_sheet.xlsx`와 snapshot mismatch" 명시 (fixture JSON 주석 또는 옆의 README).
- 진짜 case3 numeric match는 별도 Z-phase 작업으로 분리 (Windows Excel COM full_dump의 정확한 workbook version 확보 후 진행).

---

## Step 5 — profile/dispatcher/UI 재연결

### 5a. dispatcher + profile manifest 등록 (1 cycle)
- 수정 대상: `core/calculator_dispatcher.py`, `core/calculator_profiles.py`
- 작업:
  - `iso16358` calculator_id 분기 추가: `ISO16358Calculator.from_config_path(...)` 또는 `ISO16358Calculator(config_path)`로 새 ISO 인스턴스 생성.
  - profile 등록: `iso_t1_default_2point_cspf`, `india_iseer_cspf`, `hong_kong_cspf`, `saso_t3_cspf` (각각 `calculator_id=iso16358`, `config_path=data/region_configs/<file>.json`).
  - `asnzs_excel_hspf_compat` profile은 `enabled=False`로만 등록 (Z-phase).
- 검증: profile snapshot test 통과, dispatcher unit test 통과.

### 5b. UI swap (1 cycle)
- 수정 대상: `ui/calculators_2point.py:12, 1053, 1310`
- 작업: `_legacy` 모듈 import를 새 `core.calculator_iso16358`로 swap. 가능하면 직접 instantiation 대신 `create_calculator_for_profile(profile_id=...)`로 전환 (035 AHRI HSPF2 패턴 따름).
- 검증: PyQt5 Calculator window를 실제 띄워 4개 ISO config (ISO T1 default / India / HK / SASO) CSPF 입력 → 결과 dialog spot check. 결과값이 Step 3 reactivate test와 동일한지 확인.

### 5c. Calculator UI에 KS C 9306 tab 추가 (옵션, 별도 plan 후보)
- 본 plan 범위 밖. KS calculator는 dispatcher 경유로는 호출 가능하나 UI 진입점은 별도 작업.

---

## Cross-cutting Guards (모든 cycle 공통)

- Branch: `main`만. `git checkout / pull / merge / rebase` 금지. `work/iso-hspf-refactor-ui-followup` 절대 merge 금지.
- 각 cycle은 source/test commit과 report commit을 분리. report는 `result_reports/active/NNN_*.md` 형식, max+1 번호.
- `data/region_configs/*.json` 수정 금지 (KS standalone body가 korea.json의 `ks_intersection`을 직접 읽으므로 그 값은 유지).
- `tests/test_region_config_integrity.py:14-18` allowed set의 `ks_intersection` 유지.
- 16 pre-existing ISO HSPF failures를 expected/tolerance/xfail-pass로 무마 금지.
- Baseline 변화는 정확히 보고 (test 이동 / rename이 count에 영향을 주는 경우 명시).
- workbook/reference_files 수정 금지.

---

## Critical Files

- `core/calculator_ks_c9306.py` (Step 1a, 1b, 2c)
- `core/calculator_iso16358.py` (Step 2b — rename + 새 skeleton, Step 3a/3b — 본 구현, Step 5a 사용처)
- `core/calculator_iso16358_legacy.py` (Step 2b 생성)
- `core/calculator_asnzs_hspf_excel.py` (이미 존재하던 compatibility calculator. Step 4a에서 negative-assertion import target을 새 ISO로 재확인했고, Step 4b에서 current workbook snapshot exact-match path를 추가)
- `core/calculator_dispatcher.py` (Step 5a)
- `core/calculator_profiles.py` (Step 5a)
- `ui/calculators_2point.py:12, 1053, 1310` (Step 2b, Step 5b)
- `tests/_legacy/` (Step 2b 생성)
- `tests/test_iso16358_hspf_ks_oracle.py`, `tests/test_iso16358_hspf_validation.py`, `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py` (Step 1b)
- `tests/test_iso16358_cspf_*.py` (Step 2b + Step 3a)
- `tests/test_iso16358_hspf_*.py` (Step 2b + Step 3b)
- `tests/test_asnzs_hspf_excel_compat_*.py` (Step 2b 잠정 retarget + Step 4a 정식 retarget)

## Reused Existing Code

- `KSC9306Calculator._calculate_ks_c9306_cspf`, `_calculate_ks_c9306_hspf` (이미 standalone): Step 1 이후 변경 없음.
- `KSC9306Calculator.from_config_path` (이미 존재): KS HSPF/CSPF test retarget에서 그대로 사용.
- `create_calculator_for_profile` (035에서 도입): Step 5b UI에서 직접 instantiation 대체로 활용 권장.
- ISO `_iso_boundary_eer_power`, `_iso_boundary_temperature`, `_iso_linear_29_35`, `_iso_boundary_eer`, `_iso_boundary_eer_t3_piecewise`: legacy 모듈에서 그대로 이식 (ISO 전용이라 안전).

---

## Verification per cycle

각 cycle 끝에 동일 baseline 패턴으로 검증:

```bash
# Step 1/2/3/4/5 공통
python3 -B -m py_compile <touched files>
python3 -B -m pytest tests -q -k "<step-specific tag>"
python3 -B -m pytest tests -q  # full baseline

# KS spot check (Step 1, 2, 3, 5)
python3 -B -c "
from core.calculator_ks_c9306 import KSC9306Calculator
r = KSC9306Calculator.from_config_path('data/region_configs/korea.json').calculate_cspf(
    {'35_full': {'capacity': 6035.8, 'power': 1641.4},
     '35_half': {'capacity': 3420.4, 'power': 679.4},
     '29_min':  {'capacity': 1759.6, 'power': 201.7}},
    declared_capacity=6000)
assert r['cspf'] == 6.504 and r['annual_cooling_kwh'] == 1943.798 and r['annual_power_kwh'] == 298.852
"

# UI smoke (Step 2b, Step 5b)
# - PyQt5 Calculator window를 실제 띄워 ISO T1 default / India / HK / SASO 4개 tab 입력 → 결과 dialog spot check
# - 자동화 불가 시 manual 보고, 결과값은 reactivate된 ISO test와 동일해야 함
```

**Baseline 목표**: 모든 cycle에서 `269 passed, 16 failed, 13 xfailed` (혹은 test 이동으로 인한 명시적 count 변화) 유지. 신규 회귀 0.
