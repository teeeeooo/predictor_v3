# ISO16358 Dev Notes

## 1. Purpose

이 문서는 ISO 16358 기반 CSPF/HSPF 엔진을 수정하거나 검증할 때 구현자가 따라야 할 순서, 실수 방지 규칙, 디버깅 방법, 테스트 전략을 정리한다. 용어 본문은 이 문서에 중복 작성하지 않으며, 상세 용어는 [iso16358_glossary.md](./iso16358_glossary.md)를 참조한다.

## 2. Current Calculator Structure

`core/calculator_iso16358.py`는 현재 하나의 `ISO16358Calculator` 안에 아래 경로를 포함한다.

| Path | Entry / helper | Role |
| --- | --- | --- |
| CSPF path | `calculate_cspf` | ISO16358-1 common CSPF bin loop, point resolution, PLF, accumulation |
| generic HSPF fallback | `calculate_hspf`, `interpolate_heating`, `calc_auxiliary_heat` | heating point 보간/외삽과 shortage auxiliary 처리 |
| variable HSPF path | `_variable_heating_bin` | stage별 heating point 기반 bin detail 계산 |
| KS C 9306 HSPF profile path | `_calculate_ks_c9306_hspf`, `_ks_hspf_*` helpers | KS C 9306 profile-specific required points, curves, load line, branch selection |

이 클래스는 이미 과대화되고 있으나 지금은 구조적 리팩토링을 수행하지 않는다. 리팩토링 후보는 [REFACTOR_PLAN.md](../REFACTOR_PLAN.md)를 따른다.

## 3. bin_details 표준 구조 (디버그/검증용)

CSPF/HSPF 계산 과정에서 각 bin별 중간 결과값은 `bin_details` 리스트에 저장됩니다. 필드명은 계산 경로(CSPF, HSPF, KS C 9306 등)에 따라 다를 수 있으나, ISO common HSPF를 기준으로 아래 표준 필드를 주로 사용합니다.

- **온도/시간**: `tj` (Bin temp), `nj` (Bin hours)
- **부하/능력**: `bl_h` (Heating load), `pi_j` (Heating capacity), `P_j` (Power input)
- **소비전력**: `heat_pump_energy`, `auxiliary_energy`, `E_j` (Total energy)
- **상태**: `case` (Operating case: Case 1, 2, 3 등)

**핵심 검증식:**
- `E_j` (Total bin energy) = `heat_pump_energy` + `auxiliary_energy`
- `HSTL` (Seasonal Total Load) = `sum(bl_h * nj)`
- `HSEC` (Seasonal Total Energy) = `sum(E_j)`
- `bl_h * nj` = `pi_j * nj` + (Shortage capacity) (부하 만족 여부 확인)

## 4. Safety Rules

| Rule | Required action |
| --- | --- |
| CSPF golden `6.504`가 깨짐 | 즉시 중단하고 CSPF 변경 여부를 먼저 확인한다. |
| HSPF golden mismatch | expected를 임의 수정하지 말고 수식/fixture/config 변경 원인을 보고한다. |
| production region config | 규격값과 공식 계수만 둔다. golden/sample/test fixture 값을 삽입하지 않는다. |
| golden fixture | production `korea.json`과 분리한다. |
| numpy/pandas | ISO16358 calculator에서는 사용하지 않는다. |
| region-specific rule | ISO common 경로에 하드코딩하지 않고 JSON/profile 또는 region helper에 둔다. |

## 4. Correct CSPF Calculation Order

1. region configuration을 로드한다.
2. metadata key를 계산 대상에서 제거한다.
3. `measure` point가 모두 입력되었는지 검증한다.
4. `default` point를 derived rule로 생성한다.
5. `building_load_source`에 따라 L_c_ref를 결정한다.
6. `t_100_load - t_0_load`가 0인지 확인한다.
7. bin-hour를 순회하며 `nj <= 0`인 bin을 제외한다.
8. 각 bin에서 BL(tj)를 계산한다.
9. 각 load type의 capacity/power를 outdoor temperature 기준으로 보간 또는 외삽한다.
10. Lc가 최저 용량 이하인지, 최고 용량 초과인지, 중간 용량 범위인지 판단한다.
11. 각 bin의 cooling output과 power에 `nj`를 곱해 누적한다.
12. total power가 0 이하이면 0 결과를 반환하고, 아니면 CSPF를 산정한다.

## 5. HSPF Aux COP Rule

HSPF 경로에서 auxiliary 또는 make-up heat는 denominator인 HSEC에 포함한다.

| Path | Required behavior |
| --- | --- |
| generic HSPF fallback | `auxiliary_energy = auxiliary_heat × hours / aux_cop` |
| variable HSPF path | `auxiliary_energy = auxiliary_heat × hours / aux_cop` |
| KS C 9306 HSPF profile path | `auxiliary_energy = auxiliary_heat × hours / aux_cop` |

`aux_cop <= 0`은 `ValueError`로 처리한다. 호출부 검증과 helper 내부 방어 검증이 중복되어도 허용한다.

## 6. Profile-Driven Branch Rules

`hspf.profile == "ks_c_9306_hspf"`이면 반드시 KS C 9306 HSPF path로 진입한다. `measured_inputs`에 `ks_c_9306_hspf`가 없으면 common fallback으로 가지 않고 `ValueError`를 발생시킨다.

이 규칙의 목적은 KS profile이 선택된 상태에서 입력 누락이 조용히 HSPF `0.0` 또는 legacy fallback 결과로 바뀌는 것을 막는 것이다.

## 7. HSPF Load Line Schema

지원 key는 `hspf.load_line.source`이다. `capacity_source`는 사용하지 않는다.

`hspf.load_line`을 정의할 경우 아래 field는 모두 필수이다.

| Field | Meaning |
| --- | --- |
| `source` | 기준 capacity source |
| `zero_load_temp` | zero heating load temperature |
| `full_load_temp` | full heating load temperature |
| `rated_capacity_factor` | 기준 capacity에 곱하는 계수 |

허용 `source` 값:

| Source | Meaning |
| --- | --- |
| `rated_heating_capacity` | caller input 또는 KS profile input의 rated heating capacity |
| `rated_cooling_capacity` | caller input의 rated cooling capacity |
| `declared_capacity` | caller input의 declared cooling capacity |

`hspf.load_line = {}` 또는 `source` 누락은 암묵적으로 `rated_heating_capacity`를 사용하지 않고 `ValueError`로 처리한다.

## 8. Top Implementation Pitfalls

| Pitfall | Symptom | Cause | Prevention | Reference |
| --- | --- | --- | --- | --- |
| building load 기준 혼동 | CSPF/HSPF가 region별로 크게 달라진다. | measured, declared, rated heating/cooling reference를 같은 방식으로 처리한다. | `building_load_source`와 `hspf.load_line.source`를 먼저 확인한다. | ISO 16358-1:2013 Chapter 6; ISO 16358-2 |
| 시험점 누락 | `ValueError` 또는 비어 있는 interpolation 결과가 발생한다. | configuration/profile의 required point가 입력에 없다. | CSPF `points`, HSPF profile required points를 분리 검증한다. | ISO 16358-1:2013 Clause 6.4~6.7 |
| 파생점 순서 오류 | default point가 unresolved 상태로 남는다. | derived rule source가 아직 만들어지지 않았다. | default point는 반복 pass로 해석하고 unresolved 목록을 에러로 노출한다. | Project implementation |
| 온도 보간과 부하 보간 혼동 | 중간 부하 소비전력이 과소/과대 계산된다. | temperature interpolation과 capacity-range interpolation을 같은 단계로 취급한다. | 먼저 온도별 성능선을 만들고 이후 load 위치에 따라 power를 정한다. | ISO 16358-1:2013 Chapter 6 |
| auxiliary 누락 | HSPF가 과대 계산된다. | heat pump shortage를 denominator에 더하지 않는다. | HSEC가 heat pump energy plus auxiliary energy인지 확인한다. | ISO 16358-2 |
| profile fallback | KS profile 입력 누락이 조용히 common result로 바뀐다. | profile branch 조건에 input 존재 여부를 같이 둔다. | profile만 보고 KS path로 진입하고 input 누락은 `ValueError`로 처리한다. | Project implementation |
| Profile path가 legacy 결과를 바꿈 | 기존 ISO T1 default regression이 바뀐다. | `cspf_test_profile` 분기가 legacy path에 누출된다. | profile key가 있을 때만 새 path로 진입하고, legacy config 결과를 항상 regression으로 보호한다. |
| required_only에서 min point 합성 | 저부하 bin의 PLF branch가 달라져 CSPF가 변한다. | optional minimum과 required_only를 같은 구조로 처리한다. | required_only에서는 half를 lowest continuous operating point로 사용한다. |
| T3를 35/29 hard-code로 계산 | 46°C high anchor를 사용하는 T3에서 ValueError 또는 잘못된 보간이 발생한다. | 기존 `iso_boundary_eer` 구조를 그대로 재사용한다. | T3는 `tj > 35`에서 46↔35, `tj <= 35`에서 35↔29 segment를 선택한다. |

## 9. Data Model Notes

| Key | Meaning | Implementation note |
| --- | --- | --- |
| `t_100_load` | 100% cooling load 기준 온도 | CSPF BL(tj) 직선의 상단 기준이다. |
| `t_0_load` | 0% cooling load 기준 온도 | CSPF BL(tj) 직선의 하단 기준이다. |
| `Cd` | degradation coefficient | CSPF PLF 또는 HSPF cyclic branch에 사용한다. |
| `building_load_source` | CSPF 기준 부하 출처 | `measured` 또는 `declared`를 구분한다. |
| `hspf.load_line.source` | HSPF load line 기준 capacity 출처 | `capacity_source`가 아니다. |
| `round_test_values` | 시험값 반올림 여부 | region-specific 규칙이므로 공통 기본값은 false이다. |
| `power_interpolation_method` | 중간 용량 범위 power 계산법 | 기본값은 capacity-linear이며 지역 확장에서 바꿀 수 있다. |
| `points` | CSPF point별 measured/default 지정 | point 이름은 temperature와 load type을 포함한다. |
| `derived_rules` | CSPF default point 생성 규칙 | source, capacity factor, power factor를 사용한다. |
| `bin_hours` | cooling outdoor temperature와 hour | CSPF seasonal accumulation의 시간 가중치이다. |
| `hspf_bin_hours` | heating outdoor temperature와 hour | HSPF seasonal accumulation의 시간 가중치이다. |
| `cspf_test_profile` | CSPF variable/inverter profile path selector | legacy flat config와 병렬로 동작하는 opt-in key이다. 없는 경우 기존 path를 반드시 유지한다. |
| `cspf_test_profile.climate_profile` | T1/T3 climate profile | T1은 35↔29 단일 segment, T3는 46↔35 / 35↔29 piecewise segment를 사용한다. |
| `cspf_test_profile.test_selection` | required_only / with_optional_test | required_only에서는 minimum point를 합성하지 않는다. optional minimum 선택 시에만 min branch를 활성화한다. |

## 10. Interpolation / Extrapolation Rules

| Rule | Behavior | Debug focus |
| --- | --- | --- |
| 동일 load type에 1개 point만 있을 때 | 해당 capacity/power를 그대로 사용한다. | point 수가 의도된 것인지 확인한다. |
| tj가 최저 시험온도 이하일 때 | 가장 낮은 두 temperature point로 외삽한다. | 외삽된 capacity가 음수로 내려가지 않는지 확인한다. |
| tj가 최고 시험온도 이상일 때 | 가장 높은 두 temperature point로 외삽한다. | 고온/저온 bin에서 capacity shortage branch와 함께 확인한다. |
| tj가 시험온도 사이일 때 | 해당 구간의 두 point로 선형 보간한다. | temperature sorting과 point key parsing을 확인한다. |
| Lc 또는 BL이 capacity 사이일 때 | 기본적으로 capacity 기준 power 선형 보간을 적용한다. | region-specific method가 켜져 있는지 확인한다. |

## 11. Debugging Checklist

| Step | Check | Expected |
| --- | --- | --- |
| 1 | configuration path | 파일이 존재해야 한다. |
| 2 | required measured points | CSPF `points` 또는 HSPF profile required point가 모두 입력되어야 한다. |
| 3 | derived points | 모든 `default` point가 resolved 되어야 한다. |
| 4 | CSPF L_c_ref | measured 또는 declared source가 region 의도와 일치해야 한다. |
| 5 | HSPF load line | `hspf.load_line.source`와 필수 field가 명시되어야 한다. |
| 6 | load temperature | load 기준 온도 두 값이 달라야 한다. |
| 7 | bin loop | `nj <= 0`인 bin은 누적하지 않아야 한다. |
| 8 | PLF/cyclic branch | load가 lowest capacity 이하일 때만 degradation이 적용되어야 한다. |
| 9 | shortage branch | heating load가 max capacity보다 크면 auxiliary가 HSEC에 포함되어야 한다. |
| 10 | accumulation | Wh 누적 후 필요한 출력에서 kWh로 변환되어야 한다. |
| 11 | CSPF profile parity | profile path와 legacy path의 CSTL/CSEC/CSPF가 같은 fixture에서 일치해야 한다. |
| 12 | profile active load levels | `required_only`는 full/half, `with_optional_test`는 full/half/min인지 확인한다. |
| 13 | profile segment selection | T1은 35↔29, T3는 46↔35 및 35↔29 segment가 맞는지 확인한다. |

## 12. Test Strategy

| Test type | Purpose | Required cases |
| --- | --- | --- |
| HSPF golden | official/sample HSPF fixture가 유지되는지 확인한다. | `tests/test_iso16358_hspf_golden.py` |
| HSPF validation | required point, load_line schema, fallback 정책을 검증한다. | `tests/test_iso16358_hspf_validation.py` |
| HSPF smoke | generic/variable path와 aux_cop denominator 처리를 빠르게 확인한다. | `tests/test_iso16358_hspf_smoke.py` |
| Korea CSPF regression | KS CSPF `6.504`가 유지되는지 확인한다. | one-liner 또는 golden fixture |
| compile check | syntax regression을 확인한다. | `python3 -B -m py_compile core/calculator_iso16358.py` |
| JSON validation | production region config가 유효한 JSON인지 확인한다. | `python3 -B -m json.tool data/region_configs/korea.json` |
| CSPF profile resolver | `cspf_test_profile`의 measured/default/not_used point resolution을 검증한다. | `tests/test_iso16358_cspf_profile_resolver.py` |
| CSPF profile calculation | profile path가 legacy ISO T1 default path와 parity를 유지하는지 검증한다. | `tests/test_iso16358_cspf_profile_calculation.py` |
| SASO T3 golden | T3 piecewise boundary EER, min-half/half-full bracket, `46_full` load line을 검증한다. | `tests/test_iso16358_cspf_saso_t3_regression.py` |
| Hong Kong CSPF golden | declared/rated full capacity load anchor와 measured performance curve 분리 동작을 검증한다. | `tests/test_iso16358_cspf_hong_kong_config.py` |

## 13. Prompt Snippets for Agent

Agent 재사용 프롬프트:

> AGENTS.md와 docs/DOCS_GUIDELINES.md를 먼저 읽는다. ISO16358 공통 엔진을 수정할 때는 docs/iso16358/iso16358_notes.md, docs/iso16358/iso16358_dev_notes.md, docs/iso16358/iso16358_glossary.md를 확인한다. 국가별 특이사항은 ISO 공통 문서에 넣지 말고 docs/iso16358/regions/<region>/ 문서에 분리한다. 계산 변경 후에는 HSPF golden, HSPF validation, HSPF smoke, Korea CSPF regression을 실행한다.


## 15. Official XLSM Analysis: Variable Capacity Unit CSPF Structure

This section documents the detailed analysis of the official ISO16358-1_AMD1 Calculation Tool XLSM file, specifically focusing on the T1 variable-capacity CSPF calculation structure within the 'Variable Capacity unit' sheet.

### 15.1. Analysis Background

-   **Workbook:** `20181107 ISO16358-1_AMD1 Calculation_tool_FINAL (1).xlsm`
-   **Sheet:** `Variable Capacity unit`
-   **Direct Extraction:** Formulas for row 18, columns CC:CZ were directly extracted. Key boundary temperature and EER cells (CK5, CK6, CK7, CN5, CN6, CN7, CN8) were also directly extracted.

### 15.2. Row 18 Column Interpretation (CC:CZ)

The following table summarizes the interpretation of key columns in row 18, which represents a single bin calculation.

| Column | Meaning |
| :----- | :------ |
| CC     | bin temperature (Outdoor Temperature) |
| CD     | bin hour (`nj`) |
| CE     | Cooling Load (`Lc(tj)`) |
| CF     | Part Load Factor (`FPL(tj)`) |
| CG     | Operation Factor (`X(tj)`) |
| CH     | Full Capacity at `tj` (`φful(tj)`) |
| CI     | Half Capacity at `tj` (`φhaf(tj)`) |
| CJ     | Minimum Capacity at `tj` (`φmin(tj)`) |
| CK     | LCST (Cooling Seasonal Total Load) row component |
| CL     | Full Power Input at `tj` (`Pful(tj)`) |
| CM     | Half Power Input at `tj` (`Phaf(tj)`) |
| CN     | Minimum Power Input at `tj` (`Pmin(tj)`) |
| CO     | Full EER at `tj` (`EER,ful(tj)`) |
| CP     | Half EER at `tj` (`EER,haf(tj)`) |
| CQ     | Minimum EER at `tj` (`EER,min(tj)`) |
| CR     | Branch EER (`Lc<=min` case) |
| CS     | Branch EER (`min<Lc<=half` case) |
| CT     | Branch EER (`half<Lc<=full` case) |
| CU     | Branch EER (`full<Lc` case) |
| CV     | Branch Power (`Lc<=min` case) |
| CW     | Branch Power (`min<Lc<=half` case) |
| CX     | Branch Power (`half<Lc<=full` case) |
| CY     | Branch Power (`full<Lc` case) |
| CZ     | CCSE (Cooling Seasonal Energy Consumption) row component |

### 15.3. Key Boundary Cells

The following cells define critical boundary temperatures and EER values used in the calculation logic, particularly for interpolation and branching.

-   `CK5` = `tb` (Balance Temperature 1)
-   `CK6` = `tc` (Balance Temperature 2)
-   `CK7` = `tp` (Balance Temperature 3)
-   `CN5` = `EER(t0)` (EER at reference temperature t0, possibly CH8)
-   `CN6` = `EER,ful(tb)` (Full capacity EER at balance temperature tb)
-   `CN7` = `EER,haf(tc)` (Half capacity EER at balance temperature tc)
-   `CN8` = `EER,min(tp)` (Minimum capacity EER at balance temperature tp)

### 15.4. Key Formulas

Extracted formulas from the XLSM file:

-   **`CE18` (Cooling Load `Lc(tj)`):**
    `=IF($CC$3*($CC18-$CH$8)/($CH$9-$CH$8)<0,0,$CC$3*($CC18-$CH$8)/($CH$9-$CH$8))`

-   **`CF18` (Part Load Factor `FPL(tj)`):**
    `=1-$CH$5*(1-$CG18)`

-   **`CG18` (Operation Factor `X(tj)`):**
    `=IF($CE18<$CJ18,$CE18/$CJ18,1)`

-   **`CK18` (LCST row component):**
    `=IF($CE18<$CH18,$CE18*$CD18,$CH18*$CD18)`

-   **`CS18` (Branch EER `min<Lc<=half` case):**
    `=IF(AND($CJ18<$CE18,$CE18<=$CI18),$CN$8+($CN$7-$CN$8)/($CK$6-$CK$7)*($CC18-$CK$7),0)`

-   **`CT18` (Branch EER `half<Lc<=full` case):**
    `=IF(AND($CI18<$CE18,$CE18<=$CH18),$CN$7+($CN$6-$CN$7)/($CK$5-$CK$6)*($CC18-$CK$6),0)`

-   **`CV18` (Branch Power `Lc<=min` case):**
    `=IF($CJ18>=$CE18,$CN18,0)`

-   **`CW18` (Branch Power `min<Lc<=half` case):**
    `=IF($CS18>0,$CE18/$CS18,0)`

-   **`CX18` (Branch Power `half<Lc<=full` case):**
    `=IF($CT18>0,$CE18/$CT18,0)`

-   **`CY18` (Branch Power `full<Lc` case):**
    `=IF($CU18>0,$CH18/$CU18,0)`

-   **`CZ18` (CCSE row component):**
    `=IF($CF18=0,0,$CG18*$CV18*$CD18/$CF18+$CW18*$CD18+$CX18*$CD18+$CY18*$CD18)`

-   **`CK5` (`tb`):**
    `=(6*$CC$3*$CH$8+6*$CC$6*($CH$9-$CH$8)+35*($CC$11-$CC$6)*($CH$9-$CH$8))/(6*$CC$3+($CC$11-$CC$6)*($CH$9-$CH$8))`

-   **`CK6` (`tc`):**
    `=(6*$CC$3*$CH$8+6*$CD$6*($CH$9-$CH$8)+35*($CD$11-$CD$6)*($CH$9-$CH$8))/(6*$CC$3+($CD$11-$CD$6)*($CH$9-$CH$8))`

-   **`CK7` (`tp`):**
    `=(6*$CC$3*$CH$8+6*$CE$6*($CH$9-$CH$8)+35*($CE$11-$CE$6)*($CH$9-$CH$8))/(6*$CC$3+($CE$11-$CE$6)*($CH$9-$CH$8))`

-   **`CN5` (`EER(t0)`):**
    `=($CE$6+($CE$11-$CE$6)/(35-29)*(35-$CH$8))/($CE$7+($CE$12-$CE$7)/(35-29)*(35-$CH$8))`

-   **`CN6` (`EER,ful(tb)`):**
    `=($CC$6+($CC$11-$CC$6)/(35-29)*(35-$CK$5))/($CC$7+($CC$12-$CC$7)/(35-29)*(35-$CK$5))`

-   **`CN7` (`EER,haf(tc)`):**
    `=($CD$6+($CD$11-$CD$6)/(35-29)*(35-$CK$6))/($CD$7+($CD$12-$CD$7)/(35-29)*(35-$CK$6))`

-   **`CN8` (`EER,min(tp)`):**
    `=($CE$6+($CE$11-$CE$6)/(35-29)*(35-$CK$7))/($CE$7+($CE$12-$CE$7)/(35-29)*(35-$CK$7))`

### 15.5. Engineering Interpretation

-   **Complex EER/Power Calculation:** The official Excel sheet does not simply choose one branch and linearly interpolate power by capacity based on temperature. Instead, it computes specific "boundary temperatures" (`tb`, `tc`, `tp` from CK5, CK6, CK7) and "boundary EERs" (`EER(t0)`, `EER,ful(tb)`, `EER,haf(tc)`, `EER,min(tp)` from CN5, CN6, CN7, CN8). These derived boundary EERs are then used to calculate branch EER/power contributions, indicating a more nuanced piecewise linear interpolation approach.
-   **`cspf_calculator.py` Evaluation:** The existing `cspf_calculator.py` is valuable as an exploration tool, but it is not directly production-accurate if it does not precisely replicate this boundary-temperature and boundary-EER driven branching logic. Significant refactoring and re-implementation of the power calculation block in `cspf_calculator.py` would be necessary to align with the XLSM's methodology.
-   **`calculator_iso16358.py` Alignment:** The `iso_boundary_eer` direction within `calculator_iso16358.py` is structurally aligned with the XLSM's approach. This architectural choice should be preserved and further developed to accurately model the boundary EERs.
-   **India Boundary Temperature Rounding:** The rounding of India boundary temperatures is structurally meaningful because `CK5` through `CK7` (tb, tc, tp) directly drive the interpolation of branch EERs. Any deviation in these boundary temperatures will impact the subsequent EER calculations.
-   **SASO T3 and `cspf_test_profile` Schema:** SASO T3 Phase R2-2 is aligned through the `cspf_test_profile` opt-in path, not a one-off public calculator method. The legacy T1 `_iso_boundary_eer()` behavior remains unchanged, while T3 uses `_iso_boundary_eer_t3_piecewise()` only when `cspf_test_profile.climate_profile == "T3"`. This helper selects 29↔35 for `tj <= 35` and 35↔46 for `tj > 35`, and `_iso_boundary_eer_power()` handles both `{min, half}` and `{half, full}` brackets under that T3 guard.
-   **SASO T3 Boundary Diagnostics:** The verified golden sample produces Tb ≈ 45.2479°C, Tc ≈ 34.6371°C, and Tp ≈ 29.1799°C. For the `tj > 35` full segment, the intersection is 46.0°C because `46_full` is the building-load reference point.
-   **T3 29_full default point:** The T3 resolver behavior for 29_full is confirmed and maintained: capacity is `1.077 × 35_full capacity`, and power is `0.914 × 35_full power`. Treat this as confirmed resolver behavior and test coverage, not as a Phase R2-2-only new rule.
-   **Hong Kong CSPF load anchor:** Hong Kong measured CSPF uses measured 35_full / 35_half capacity and power for the performance curve, but uses declared/rated 35_full capacity as the building-load anchor. Use `building_load_source = "declared"` and pass rated 35_full capacity as `declared_capacity`. Do not tune Cd or derived factors to match the source tool.
-   **Hong Kong HSPF follow-up:** Hong Kong HSPF is out of scope for the CSPF golden conversion. Before implementation, write ISO 16358-2 pitfalls / calculation order notes, reconfirm candidate golden values (Measure #1 3.643, Measure #2 4.571), and protect KS C 9306 HSPF regressions. Current Hong Kong HSPF observations are preliminary only, including the `Lh(tj) = cap_0 × (12.75 - tj) / 12.75` candidate, possible `cap_0 = 7°C full heating capacity × 0.82`, frost/non-frost branching, and boundary temperatures `ta`, `td`, `te`, `tg`.

## 14. ISO 16358-2 HSPF Calculation Order

| Step | Action | Description |
| :--- | :--- | :--- |
| 1 | Load configuration | region config를 로드한다. (hspf_bin_hours, load_line, frost 경계, Cd, aux_cop 포함) |
| 2 | Validate points | required measured points를 검증한다. 7°C Full, 7°C Half 필수. 2°C Full (Extended 없는 경우) 필수. 단, source golden 재현용 regional/profile config에서 명시적으로 허용한 경우에만 2°C Full derived 계산을 허용한다. |
| 3 | Resolve derived points | optional/derived points를 해석한다. -7°C Full/Half (Table 1 계수), 2°C Full/Half (각주 d 수식) 등. 2°C Half는 measured 값이 있어도 각주 d 처리 원칙에 따라 재계산한다. |
| 4 | Determine L_h_ref | load line 기준값 L_h_ref를 결정한다. L_h_ref = rated_capacity_factor × pi_source (ISO 16358-2 default: 0.82 × pi_ful(7)). |
| 5 | Iterate bin hours | hspf_bin_hours를 순회한다. nj <= 0인 bin은 skip한다. |
| 6 | Calculate BL_h(tj) | BL_h(tj) = L_h_ref × (t_0_heat - tj) / (t_0_heat - t_100_heat) (ISO 16358-2 default: t_0=17, t_100=0). BL_h(tj) <= 0이면 해당 bin skip. |
| 7 | Determine frost status | tj가 frost 구간인지 판정한다. -7°C < tj < 5.5°C 이면 frost, 그 외 non-frost. |
| 8 | Evaluate performance | frost/non-frost에 따라 stage별(Full, Half, Min) capacity/power curve를 평가한다. pi_x(tj) 및 P_x(tj) 계산. |
| 9 | Determine operating case | operating case를 결정한다. BL_h와 stage별 capacity 비교. stage 우선순위: Min > Half > Full. |
| 10 | Cycling branch | BL_h <= lowest_stage_pi: PLF = 1 - Cd × (1 - X), X = BL_h / pi_min. heat_pump_energy = (X × P_min / PLF) × nj. |
| 11 | Interpolation branch | lowest_stage_pi < BL_h <= pi_ful: 인접 stage 사이 capacity-linear power 보간. heat_pump_energy = P_interp × nj. |
| 12 | Saturated branch | BL_h > pi_ful: heat_pump_output = pi_ful(tj) × nj, heat_pump_energy = P_ful(tj) × nj. auxiliary_heat = BL_h(tj) - pi_ful(tj). auxiliary_energy = auxiliary_heat × nj / aux_cop. |
| 13 | Accumulate HSTL/HSEC | HSTL += BL_h(tj) × nj (건물 부하 전체). HSEC += heat_pump_energy + auxiliary_energy. |
| 14 | Finalize HSPF | HSPF = HSTL / HSEC, 3 significant digits로 반올림한다. |

## 15. ISO 16358-2 HSPF Top Pitfalls

| Pitfall | Symptom | Prevention |
| :--- | :--- | :--- |
| KS path와 ISO common path 혼용 | KS golden이 바뀐다. | hspf.profile == "ks_c_9306_hspf"이면 반드시 KS path로만 진입한다. ISO common HSPF는 별도 entry point로 분리한다. |
| frost/non-frost 수식 혼용 | frost 구간 capacity/power가 과대 또는 과소 계산된다. | tj 판정을 수식 적용 직전에 반드시 수행한다. -7.0 < tj < 5.5 → frost 수식, 그 외 → non-frost 수식. |
| 2°C measured Half를 직접 사용 | 규격 각주 c 위반. 결과가 reference sheet와 다르다. | 2°C Half는 measured 값이 있어도 각주 d 수식으로 재계산한다. |
| 각주 d 수식 적용 순서 오류 | -7°C derived point가 없어 각주 d 수식이 실패한다. | -7°C derived point를 먼저 만든 뒤 각주 d 수식을 적용한다. |
| HSTL에 heat pump output만 누적 | auxiliary 발생 bin에서 HSTL이 과소 계산되어 HSPF가 낮게 나온다. | HSTL은 항상 BL_h(tj) × nj 전체를 누적한다. heat pump output이 아니다. |
| auxiliary_energy를 HSEC에서 누락 | HSPF가 과대 계산된다. | HSEC = heat_pump_energy + auxiliary_energy. aux_cop = 1.0 (전기히터 가정, 규격 미명시). |
| BL_h(tj) <= 0인 bin을 누적 | 냉방 구간 bin이 HSTL을 음수로 끌어내린다. | BL_h(tj) <= 0이면 해당 bin을 skip한다. |
| bin_details에서 KS 필드 구조 재사용 | ISO common HSPF bin_details와 KS bin_details가 섞인다. | ISO common HSPF bin_details는 KS 전용 필드를 포함하지 않는다. 표준 필드: tj, nj, bl_h, pi_j, P_j, case, heat_pump_energy, auxiliary_energy, E_j. |

## 16. ISO 16358-2 HSPF Test Strategy

| Test type | Purpose | Required cases |
| :--- | :--- | :--- |
| HSPF Hong Kong golden #1 | Hong Kong bin_hours 기반 golden 검증 | 7_full=6300W/1500W, 7_half=3200W/800W, Cd=0.25, Expected HSPF: 3.643 |
| HSPF Hong Kong golden #2 | Hong Kong bin_hours 기반 golden 검증 | 7_full=6100W/1300W, 7_half=3000W/600W, Cd=0.25, Expected HSPF: 4.571 |
| KS C 9306 HSPF regression | 기존 golden 유지 확인 | HSPF 3.689 유지 확인 (변경 없어야 함) |
| Korea CSPF regression | Korea CSPF golden 유지 확인 | CSPF 6.504 유지 확인 (변경 없어야 함) |
| validation smoke | 에러 처리 및 경계 조건 검증 | required point 누락 시 ValueError, BL_h <= 0 bin skip 확인, aux_cop = 0 시 ValueError |
