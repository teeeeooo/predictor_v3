# ISO16358 Dev Notes

## 1. Purpose

이 문서는 ISO 16358 기반 CSPF/HSPF 엔진을 수정하거나 검증할 때 구현자가 따라야 할 순서, 실수 방지 규칙, 디버깅 방법, 테스트 전략을 정리한다. 용어 본문은 이 문서에 중복 작성하지 않으며, 상세 용어는 [iso16358_glossary.md](./iso16358_glossary.md)를 참조한다.

## 2. Current Calculator Structure

`core/calculators/standards/iso16358.py`는 stable facade이며, private
`_iso16358/` package의 CSPF와 HSPF engine을 하나의 config context로 조립한다.

| Path | Entry / helper | Role |
| --- | --- | --- |
| CSPF path | `_iso16358/cspf_points.py`, `cspf_performance.py`, `cspf_engine.py`, `cspf_result.py` | ISO16358-1 point resolution, boundary performance, PLF/bin accumulation, result assembly |
| generic HSPF fallback | `_iso16358/hspf_legacy_points.py`, `hspf_legacy_engine.py` | heating point 보간/외삽과 shortage auxiliary 처리 |
| ISO common HSPF | `_iso16358/hspf_points.py`, `hspf_curves.py`, `hspf_extended.py`, `hspf_load.py`, `hspf_snapshot.py`, `hspf_cases.py`, `hspf_engine.py`, `hspf_result.py` | common point/fallback, curve, building load, branch, bin, result responsibility |
| KS C 9306 HSPF profile path | `core/calculators/standards/ks_c9306.py`의 `_calculate_ks_c9306_hspf`, `_ks_hspf_*` helpers | KS C 9306 profile-specific required points, curves, load line, branch selection |

Facade의 import path, public method, config attributes는 유지한다. Application과
UI는 private `_iso16358` owner를 import하지 않고 capability를 통해 계산한다.

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
| HSPF golden | official/sample HSPF fixture가 유지되는지 확인한다. | `tests/test_iso16358_hspf_official_exact_golden.py` |
| HSPF validation | required point, load_line schema, fallback 정책을 검증한다. | `tests/test_iso16358_hspf_validation.py` |
| HSPF smoke | generic/variable path와 aux_cop denominator 처리를 빠르게 확인한다. | `tests/test_iso16358_hspf_smoke.py` |
| Korea CSPF regression | KS CSPF `6.504`가 유지되는지 확인한다. | one-liner 또는 golden fixture |
| compile check | syntax regression을 확인한다. | `python3 -B -m py_compile core/calculators/standards/iso16358.py` |
| JSON validation | production region config가 유효한 JSON인지 확인한다. | `python3 -B -m json.tool data/region_configs/korea.json` |
| CSPF profile resolver | T1/T3 profile의 measured/default/not_used point resolution을 검증한다. | `tests/test_iso16358_cspf_iso_t1_default_golden.py`, `tests/test_iso16358_cspf_t3_profile.py` |
| CSPF profile calculation | active profile path의 고정 결과와 branch를 검증한다. | `tests/test_iso16358_cspf_iso_t1_default_golden.py` |
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
-   **`iso16358.py` Alignment:** The `iso_boundary_eer` direction within `core/calculators/standards/iso16358.py` is structurally aligned with the XLSM's approach. This architectural choice should be preserved and further developed to accurately model the boundary EERs.
-   **India Boundary Temperature Rounding:** The rounding of India boundary temperatures is structurally meaningful because `CK5` through `CK7` (tb, tc, tp) directly drive the interpolation of branch EERs. Any deviation in these boundary temperatures will impact the subsequent EER calculations.
-   **SASO T3 and `cspf_test_profile` Schema:** SASO T3 Phase R2-2 is aligned through the `cspf_test_profile` opt-in path, not a one-off public calculator method. The legacy T1 `_iso_boundary_eer()` behavior remains unchanged, while T3 uses `_iso_boundary_eer_t3_piecewise()` only when `cspf_test_profile.climate_profile == "T3"`. This helper selects 29↔35 for `tj <= 35` and 35↔46 for `tj > 35`, and `_iso_boundary_eer_power()` handles both `{min, half}` and `{half, full}` brackets under that T3 guard.
-   **SASO T3 Boundary Diagnostics:** The verified golden sample produces Tb ≈ 45.2479°C, Tc ≈ 34.6371°C, and Tp ≈ 29.1799°C. For the `tj > 35` full segment, the intersection is 46.0°C because `46_full` is the building-load reference point.
-   **T3 29_full default point:** The T3 resolver behavior for 29_full is confirmed and maintained: capacity is `1.077 × 35_full capacity`, and power is `0.914 × 35_full power`. Treat this as confirmed resolver behavior and test coverage, not as a Phase R2-2-only new rule.
-   **Hong Kong CSPF load anchor:** Hong Kong measured CSPF uses measured 35_full / 35_half capacity and power for the performance curve, but uses declared/rated 35_full capacity as the building-load anchor. Use `building_load_source = "declared"` and pass rated 35_full capacity as `declared_capacity`. Do not tune Cd or derived factors to match the source tool.
-   **Hong Kong HSPF boundary:** Hong Kong HSPF should share the ISO 16358-2 common HSPF bin integration core, not become a separate core algorithm. Hong Kong MEELS / Code of Practice specific 7°C Full/Half inputs and low-temperature extrapolation belong in a region/profile handler or preprocessor that emits canonical ISO 16358-2 HSPF input points before calling the common core.
-   **Hong Kong HSPF extrapolation examples:** Treat values such as `Calculated Full Capacity at 0°C = 0.82 × phi_full(7°C)` and `Calculated Full Power Input at 0°C = 0.91 × P_full(7°C)` as handler/preprocessor-derived canonical points. The common core must not branch on Hong Kong, MEELS, region/country flags, or `trace_metadata`; it should only consume the resulting canonical points.

## 14. ISO 16358-2 HSPF Calculation Order

### 14.1. Table 1 / Formula 30 Interpretation Note

ISO 16358-2 Table 1의 measurement/default matrix는 다음처럼 해석한다.

- 7°C Standard heating: Full/Half는 measured required, Min은 optional이다.
- 2°C Low-temperature heating: extended mode가 있으면 Extended_f measured가 required이고 Full_f는 optional이다. extended mode가 없으면 Full_f measured가 required이다. Half_f는 optional/default이고 Min은 tested point가 아니다.
- -7°C Extra-low-temperature heating: Extended/Full/Half는 optional/default이고 Min은 tested point가 아니다.

프로젝트 해석: production ISO Table 1 default에서 -7°C Full/Half default는 capacity factor 0.64, power factor 0.82를 유지한다. `external_calculator_minus7_fallback_override`의 0.5 / 1.105는 seven-case ISO 16358 mode workbook oracle / official-sheet reproduction fixture 전용이며 production ISO default와 섞지 않는다.

ISO 16358-2 Table 1 footnote c/d는 measured 2°C frosting point와 calculated non-frost 2°C point를 같은 값으로 collapse하지 않는다는 의미로 처리한다. footnote d가 적용될 때 `pi_x(2)`와 `P_x(2)`는 -7°C to 7°C line에서 계산한다.

ISO 16358-2 Formula 30의 denominator branch 해석은 다음 boundary를 유지한다.

- Cycling branch는 Formula 9/10을 사용하며 `Σ X × P × nj / F_PL` 형태로 HSEC에 기여한다.
- Half to Full non-frost branch는 Formula 46 + Formula 45 path다.
- Half to Full frost branch는 Formula 49 + Formula 45 path다.
- Full to Extended branch는 Formula 47/50 path다. 현재 common core는 Formula 50 frost full-to-extended branch만 구현한다. Formula 47 non-frost full-to-extended branch와 `L_h > pi_ext,f` extended capacity operation은 아직 구현하지 않는다.

현재 프로젝트 결정: point resolver semantics와 fixture scope가 정리되기 전까지 Formula 46/49를 blind implementation 하지 않는다. seven-case fixture는 ISO 16358 mode workbook oracle / official-sheet reproduction fixture이며 production ISO Table 1 default validation fixture가 아니다. production ISO default와 workbook oracle override는 guard test로 계속 분리한다. Formula 50에서 extended frost curve는 ISO Table 1 default `pi_ext(-7)=0.734*pi_ext(2)`, `P_ext(-7)=0.877*P_ext(2)`와 Formula 25 `P_ext(tj)` 선형 보간을 사용한다.

Case 3 reference clarification: original Windows Excel COM execution of the SEER calculator `Inverter AC` sheet in E5="ISO 16358" mode aligns with `H12 = 1126.120 kWh`, `H13 = 4.33824`, and `CH48 = 1126120.47 Wh`. This baseline is an ISO 16358 mode workbook oracle / reference benchmark. The old CH48 about 1,117,680 Wh, displayed CHSE about 1118 kWh, HSPF about 4.371 observation is demoted to a converted-workbook diagnostic artifact. The trace-only component-sum helper must remain separated from common ISO production output; the next investigation target is the Formula 49 frost half-full branch / optional branch selection matrix in the workbook oracle.

Formula 45/49 routing contradiction (superseded): Previous observation noted that wiring Formula 45/49 into the main routing broke Case 2 (shifting HSPF from 4.289 to 4.478). However, CAL-01~08 dry-runs confirmed that the workbook oracle mathematically uses COP-linear (Formula 45/49) logic but applies it conditionally based on selector/boundary states. Do not attempt to fit the ISO common core to this workbook oracle convention before the golden case 1~8 diff audit is complete.

Case 3 workbook branch model note: Windows Excel COM (ISO 16358 mode) selects active HSPF components from `BA` building load and boundary capacity columns. Non-frost candidates are `BM` cycling, `BO` min-half, `BQ` half-full, `BS` full-extd, `BT` extd, `BU` extd+backup; frost candidates are `BX` cycling, `BZ` min-half, `CB` half-full, `CD` full-extd, `CE` extd, `CF` extd+backup. Middle branch component power is not direct capacity-power interpolation; it is `BA / COP_helper(tj)` such as `BN` non-frost min-half, `BP` non-frost half-full, `BY` frost min-half, `CA` frost half-full, and `CC` frost full-extd. Case 3 observed routing is 1°C -> `CD`, 2~5°C -> `CB`, and 6°C -> `BQ`. The `BN` / `BP` / `BY` / `CA` / `CC` helper columns are treated as workbook oracle convention, not a mathematically equivalent common implementation of ISO Formula 47/49/50. Do not copy workbook anchor cell values directly into production or reproduce the helper convention in the ISO common path.

### 14.2. ISO16358-2 HSPF common path baseline

As of commits `07ca56a` and `2ca1040`, the ISO16358-2 HSPF common path is the pure ISO baseline, not a workbook-helper reproduction path.

- Common HSPF branch power uses X-based stage-to-stage interpolation, not workbook/COP intersection helper columns.
- CAL01/02/08 are implementation references for load line / HSTL, cycling + Cd / PLF, and saturated auxiliary behavior.
- CAL03~07 workbook reconstruction numbers are branch evidence only; do not use them as expected-matching targets for the common core.
- Formula 47 non-frost full-to-extended is enabled only when canonical `7_ext` and `-7_ext` inputs are both present.
- Formula 50 frost full-to-extended is enabled only when canonical `-7_ext` and either `2_ext` or `2_ext_f` are present.
- The common core must not synthesize `7_ext` or `-7_ext` from `2_ext`.
- If extended points are incomplete, the bin falls back to full-stage saturated / auxiliary handling.
- Workbook- or region-specific extended point synthesis belongs in a preprocessor or handler, not in the common ISO core.

### 14.3 Pure ISO Track A Validation Baseline

To ensure a robust validation baseline independent of external workbook conventions (such as the seven-case matrix derived from the ISO 16358 mode workbook oracle), we maintain a `Pure ISO Track A` namespace.

- **Design Philosophy**: 
  - Fixtures are hand-calculated based strictly on ISO 16358-2 equations, avoiding any non-standard interpolation or fallback logic present in workbook-derived samples.
  - Test suites utilize dedicated namespaces (`tests/test_iso16358_hspf_pure_iso_track_a.py`) to prevent cross-contamination with external legacy references.
  - Branch-level contracts (Formula 44-50) are established as `xfail` tests until the main routing core is updated to fully implement pure ISO logic.
- **Role and Relationship**:
  - Pure ISO Track A is a branch-level formula verification aid (branch 수식 단위 검증 보조 fixture).
  - Workbook goldens (ISO 16358 mode) serve as seasonal oracle benchmarks.
  - The two paths are complementary: Track A focuses on mathematical correctness of individual formulas, while workbook goldens focus on seasonal integration parity with the official-sheet reproduction.
- **Provenance Integrity**:
  - `Pure ISO` fixtures are marked with `ISO16358_COMMON_TRACK_A` metadata and include loader guards to prevent any accidental usage of workbook-derived anchor values (e.g., `4.33824`).

### 14.4 ISO 16358 Workbook Golden Tolerance Calibration Plan

워크북 골든(Workbook Golden) 검증 시 허용 오차(Tolerance)를 체계적으로 결정하기 위한 캘리브레이션 계획이다. 단순 감(Intuition)이 아니라 독립 손계산/Python 계산과의 비교를 통해 오차 범위를 확정한다.

#### 14.4.1 목적
- 워크북의 내부 반올림 및 중간 helper column 처리에 따른 오차 한계를 명확히 한다.
- 공통 엔진(Track A)이 워크북 골든을 어디까지 추적해야 하는지 가이드라인을 제공한다.

#### 14.4.2 Calibration Design Principles
- **최소 입력 원칙**: 특정 브랜치(Branch)만 활성화되도록 입력을 최소화하여 변수를 격리한다.
- **정수/단순 소수점 우선**: 반올림 오차를 추적하기 쉬운 입력을 우선 사용한다.
- **독립 검증**: 워크북의 중간 helper(BN, BP, BY, CA, CC 등)를 무시하고 규격 공식(Formula 44-50)에 따른 직접 계산값과 비교한다.

#### 14.4.3 Calibration Case 세부 설계

| Case ID | Case Name | 목적 | 입력 설계 원칙 | 기대 확인 항목 | Workbook 기록 항목 | 독립 계산 비교 항목 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CAL-01** | **Load line / HSTL** | Bin 누적 오차 격리 | Bin hours 100개 이상, Load line slope가 큰 경우 | `sum(bl_h * nj)`의 정밀도 | `HSTL` (kWh/Wh) | `sum(rated_cap * factor * temp_ratio * nj)` |
| **CAL-02** | **Cycling + Cd** | 저부하 degradation 오차 | `load < min_capacity`, `Cd=0.25` 고정 | `PLF`, `X`, `X*P/PLF` 정밀도 | `FPL`, `X`, `BM`/`BX` | Formula 9/10 기반 직접 PLF 계산 |
| **CAL-03** | **Min-to-Half (F44/48)** | 저부하 보간 오차 | `min < load < half`, non-frost | Formula 44/48 보간 정밀도 | `BN`, `BO` | Formula 44/48 직접 보간 |
| **CAL-04** | **Half-to-Full (F45)** | 중간부하 보간 오차 | `half < load < full`, non-frost | Formula 45 보간 정밀도 | `BP`, `BQ` | Formula 45 직접 보간 |
| **CAL-05** | **Frost Half-to-Full (F49)** | 성애 보간 오차 | `half < load < full`, frost (2~5°C) | Formula 49 보간 정밀도 | `CA`, `CB` | Formula 49 직접 보간 |
| **CAL-06** | **Full-to-Extended (F47)** | 고부하 보간 오차 | `full < load < extended`, non-frost | Formula 47 보간 정밀도 | `BS` | Formula 47 직접 보간 |
| **CAL-07** | **Frost Full-to-Ext (F50)** | 성애 고부하 보간 오차 | `full < load < extended`, frost | Formula 50 보간 정밀도 | `CC`, `CD` | Formula 50 직접 보간 |
| **CAL-08** | **Saturated Auxiliary** | 백업 히터 오차 | `load > extended_capacity` 또는 `load > full_capacity` | `auxiliary_heat` 누적 정밀도 | `BU`, `CF`, `HSEC` | `(load - cap) * hours / aux_cop` |

#### 14.4.5 Excel Workbook (Inverter AC) 입력 가이드

워크북의 `Inverter AC` 시트에서 캘리브레이션을 위해 조정해야 할 주요 셀 주소와 항목이다.

| 항목 | 셀 주소 (추정) | 설정값 / 비고 |
| :--- | :--- | :--- |
| **Zone Selector** | `E5` | "ISO 16358" 고정 |
| **Standby/Off Power** | `C64:C67` | 0 (변수 격리를 위해 0 권장) |
| **Degradation Coeff (Cd)**| `E59` | 0.25 (표준값) |
| **7min YES/NO** | `K25` | YES 또는 NO |
| **Extended YES/NO** | `K26` | YES 또는 NO |
| **7°C Full Cap/Power** | `G41` / `H41` | 설계값 입력 |
| **7°C Half Cap/Power** | `G42` / `H42` | 설계값 입력 |
| **7°C Min Cap/Power** | `G43` / `H43` | 설계값 입력 |
| **2°C Ext_f Cap/Power** | `G44` / `H44` | 설계값 입력 (Extended YES 시) |
| **2°C Full_f (Optional)** | `G46` / `H46` | **D46="Measured"** 시 active 반영 |
| **2°C Full_f (Required)** | `G48` / `H48` | Measured 행 우선 사용 권장 |
| **2°C Half_f (Optional)** | `G50` / `H50` | **D50="Measured"** 시 active 반영 |
| **-7°C Ext Cap/Power** | `G54` / `H54` | **D54="Measured"** 시 active 반영 |
| **-7°C Full Cap/Power** | `G55` / `H55` | **D55="Measured"** 시 active 반영 |
| **-7°C Half Cap/Power** | `G56` / `H56` | **D56="Measured"** 시 active 반영 |

*주: 셀 주소는 워크북 버전에 따라 다를 수 있으므로 입력 전 확인이 필요함 (cell address check required).*

#### 14.4.6 Calibration Numeric Case 설계 (Final Execution Set)

독립 계산과 비교하기 용이하도록 실제 실행된 숫자 입력 세트이다. 모든 케이스에서 `phi_full(7) = 3000W`, `factor = 0.82` (L_h_ref = 2460W)를 기본으로 가정한다.

| Case ID | Branch Target | 7_full (W) | 7_half (W) | 7_min (W) | 2_ext_f (W) | 2_full_f (W) | 설계 의도 및 핵심 조건 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CAL-01** | **Load line** | 3000 / 1000 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | HSTL 누적 오차 격리 확인. |
| **CAL-02** | **Cycling** | 3000 / 1000 | 2000 / 800 | 1000 / 300 | 0 / 0 | 0 / 0 | `load(434.1) < min(1000)` 유도. |
| **CAL-03** | **Min-to-Half** | 3000 / 1000 | 2000 / 800 | 1000 / 300 | 0 / 0 | 0 / 0 | `min(1000) < load(1447) < half(2000)`. |
| **CAL-04** | **Half-to-Full** | 3000 / 1000 | 1000 / 400 | 300 / 100 | 0 / 0 | 0 / 0 | `half(1000) < load(1447) < full(3000)`. |
| **CAL-05** | **Frost H-to-F** | 3000 / 1000 | 1000 / 400 | 300 / 100 | 4000 / 1500 | 3000 / 1000 | **D46, D50 = "Measured"** 필수 반영. |
| **CAL-06** | **Full-to-Ext** | 1000 / 400 | 500 / 250 | 200 / 100 | 6000 / 2000 | 0 / 0 | **K88=2.5** 조정으로 `load > full` 유도. |
| **CAL-07** | **Frost F-to-E** | 3000 / 1000 | 1000 / 400 | 300 / 100 | 4000 / 1500 | 1000 / 400 | **K88=1.5** 및 boundary extrapolation 기준. |
| **CAL-08** | **Saturated** | 1000 / 400 | 500 / 250 | 0 / 0 | 1500 / 600 | 1000 / 400 | **D54-56="Measured"**, `load > max_cap`. |

#### 14.4.7 Selected Output Capture Results

워크북 실행 후 기록된 최종 결과이다. 독립 계산(Independent Calculation) 열은 손계산 또는 Python 스크립트 결과를 기입한다.

| Case ID | 측정 항목 | Workbook Output (A) | Independent Calc (B) | Delta (A-B) | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HSTL** | CAL-01 Seasonal Load | 3408.402 | 3408.402 | 0.00 | kWh 기준 |
| **P_j (7°C)** | CAL-02 Cycling Power | 142.88 | 142.88 | 0.00 | W 기준 |
| **P_j (7°C)** | CAL-04 Half-Full Power | 553.42 | 554.06 | -0.64 | F45 (COP-linear) |
| **P_j (2°C)** | CAL-05 Frost H-F Power | 721.73 | 723.53 | -1.80 | F49 (Selector-aware) |
| **P_j (2°C)** | CAL-07 Frost F-E Power | 1489.26 | 1487.45 | +1.81 | F50 (Boundary-aware) |
| **Aux_j (-1°C)**| CAL-08 Saturated Aux | 2409.80 | 2409.80 | 0.00 | aux_cop=1.0 |

#### 14.4.8 Calibration Results Summary

| CAL ID | Target Branch | Inspected tj | Workbook Result | Independent Candidate | Diff | Closest Method | Confidence | Remaining Uncertainty |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **CAL-01** | Load-line/HSTL | N/A | 3408.402 kWh | 3408.402 kWh | 0.00 | Exact | High | None |
| **CAL-02** | Cycling + Cd | 14°C | 142.88 W | 142.88 W | 0.00 | Exact | High | None |
| **CAL-03** | Min-to-Half | 7°C | 491.75 W | 488.73 W | +3.02 | COP-linear | Medium | Extrapolation precision |
| **CAL-04** | Non-frost H-to-F | 7°C | 553.42 W | 554.06 W | -0.64 | COP-linear (F45) | High | 0.1% rounding |
| **CAL-05** | **Frost H-to-F** | 2°C | **721.73 W** | 723.53 W | **-1.80** | COP-linear (F49) | High | 0.25% boundary |
| **CAL-06** | Non-frost F-to-E | 7°C | 575.27 W | 580.12 W | -4.85 | COP-linear (F47) | High | 0.8% extrapolation |
| **CAL-07** | **Frost F-to-E** | 2°C | 1489.26 W | 1487.45 W | +1.81 | COP-linear (F50) | High | 0.1% boundary |
| **CAL-08** | Saturated Aux | -1°C | 2409.80 W | 2409.80 W | 0.00 | Exact | High | None |

*주: CAL-05의 초기 결과(788.6 W)는 입력값(7_half/7_min) 불일치로 인한 오염된 결과였으며, 최종 보정 실행(721.73 W)을 통해 모든 브랜치가 COP-linear 체계임을 실증함.*

#### 14.4.9 Selector and Active Value Logic (Lessons Learned)

워크북의 `Inverter AC` 시트는 입력값과 실제 계산값이 아래와 같은 다중 레이어 구조를 가짐:

- **B열 (Availability)**: `YES`/`NO` 필터. 계산 가용 여부 결정.
- **D열 (Source Selector)**: `Measured`/`Default` 토글. 핵심 변수.
- **G/H열 (Measured Input)**: 사용자 직접 입력 필드.
- **J/K열 (Default Value)**: 규격 외삽/계산에 의한 자동 생성 필드.
- **M/N열 (Active Value)**: 실제 계산 엔진이 참조하는 최종 필드.

**핵심 교훈**:
1. Optional row(46, 50, 54, 55, 56 등)는 G/H열에 값을 넣는 것만으로는 부족하며, 반드시 **D열을 "Measured"로 변경**해야 M/N열(Active)에 반영됨.
2. `K25`(7min) 및 `K26`(Extended) 가용성 플래그가 `YES`여야 관련 브랜치가 활성화됨.
3. 2°C Full/Half 등의 경계값 결정 시, 워크북은 입력 행(`Row 48` 등)보다 외삽 열(`BE` 등)의 수치를 우선 참조하는 경향이 있음.

#### 14.4.10 Tolerance Decision (Draft)

캘리브레이션 결과를 바탕으로 한 초기 허용 오차 가이드라인 (dry-run 기반 1차 확인/정리):

- **HSTL / Load-line**: 매우 엄격한 오차(Very Tight, ±0.01 kWh) 적용 가능.
- **Cycling / Saturated Auxiliary**: 물리적 한계값으로 매우 엄격한 오차(±0.1 W) 적용 가능.
- **Non-frost Formula 45/47**: COP-linear 체계를 따르므로 엄격한 오차(±1~5 W) 적용 가능.
- **Frost Formula 49/50**: 보정 로직을 포함하되 COP-linear에 수렴하므로 중간 오차(±2~10 W) 적용 가능.
- **Min-to-Half**: 외삽 정밀도에 따라 약간의 편차 허용 필요.

#### 14.4.11 다음 작업 (Next Steps)
1. **Golden Case 1~8 Current Python Diff Audit**: 현재 구현된 Python 코드와 워크북 골든 사이의 bin-level 차이 전수 조사.
2. **Tolerance Finalization**: 전수 조사 결과를 바탕으로 최종 `pytest` 허용 오차 수치 확정.
3. **H-8 Routing Implementation Design**: 캘리브레이션으로 규명된 워크북 동작을 Python common core에 이식하기 위한 상세 설계.

- Fixture/golden/test expected values for ISO common HSPF must not be silently changed to match workbook oracle output before final tolerance decision.

Track A validation strategy:

- Treat ISO16358-2 common HSPF as the production standard path, with workbook goldens (ISO 16358 mode) serving as oracle benchmarks.
- `H13 = 4.33824` and `H12 = 1126.120 kWh` are the ISO 16358 mode workbook oracle references for Case 3.
- Until final-result coverage is sufficient, prefer formula micro golden and invariants: branch routing, cycling PLF, HSTL/HSEC accumulation, and auxiliary energy inclusion.
- Candidate edge cases include load equal to half/full capacity, load equal to `0.5 * min capacity` for PLF, full-to-extended Formula 50 routing, and load greater than extended capacity with auxiliary energy.

Track A validation phases:

- Phase H-1: ISO HSPF formula micro golden tests.
- Phase H-2: KS shared-formula oracle consistency gate.
- Phase H-3: Track B / AS/NZS workbook compatibility guard/design.
- Phase H-4: Track B compatibility module skeleton.

Phase H-1 formula micro golden / invariant test design:

- Recommended file: `tests/test_iso16358_hspf_formula_micro.py`.
- Alternative if grouped by properties: `tests/test_iso16358_hspf_invariants.py`.
- H-1 must use hand-calculated micro fixtures, not workbook reproduction values and not KS path result values.
- Micro fixture values belong under the tests namespace only. Do not copy them into production region config.
- Use the public ISO common result first: `bin_details` currently exposes `tj`, `nj`, `bl_h`, `pi_j`, `P_j`, `case`, `heat_pump_energy`, `auxiliary_energy`, and `E_j`; top-level output exposes `hstl_wh`, `hsec_wh`, `heat_pump_energy_wh`, and `auxiliary_energy_wh`.
- Candidate test cases:
  - half boundary identity: load equals half capacity -> `P_j = P_half`, auxiliary energy `0`.
  - full boundary identity: load equals full capacity -> `P_j = P_full`, auxiliary energy `0`.
  - cycling below minimum: load equals `0.5 * min_capacity`; assert `X`, `PLF`, `P_j`, `E_j`, and auxiliary energy by hand calculation.
  - half-to-full interpolation: assert branch and hand-calculated `P_j`.
  - Formula 50 full-to-extended: assert `formula50_full_extended_frost`, hand-calculated `P_j`, and auxiliary energy `0`.
  - above extended auxiliary: confirm current implementation convention before freezing expected values. Current common path falls through to `saturated` outside Formula 50 and computes auxiliary from full-stage capacity.
  - tiny 2-3 bin accumulation: assert `hstl_wh`, `hsec_wh`, and pre-rounded `hstl_wh / hsec_wh`.
- If public diagnostics are insufficient, prefer a private helper micro test over changing production API in H-1. Minimal diagnostics exposure must be a separate design phase.

Phase H-1b extended / auxiliary contract check:

- Current full-to-extended frost behavior is explicit and observable: `pi_full_f(tj) < BL_h(tj) <= pi_ext_f(tj)` selects `formula50_full_extended_frost`.
- Formula 50 uses boundary COP interpolation between full and extended boundary temperatures (`tg`, `tf`) and sets `P_j = BL_h(tj) / COP_fe_f`.
- Public diagnostics for this branch include `case`, `branch`, `pi_ext_f`, `p_ext_f`, `tg`, `tf`, `cop_fe_f`, `P_fe`, `P_j`, and `backup_heat`.
- In the Formula 50 branch, auxiliary energy is `0`, `HSTL` accumulates total building load, and `HSEC` accumulates heat pump energy.
- Current above-extended behavior is not locked as the Track A contract: if `BL_h(tj) > pi_ext_f(tj)`, the common path falls through to `saturated`, uses `P_full`, and computes auxiliary from `BL_h(tj) - pi_full(tj)`.
- Do not write a normative above-extended expected test until the intended ISO common contract is confirmed. If characterization is needed before that, keep it separate from H-1b contract tests.

KS shared-formula oracle consistency gate:

- Use the implemented KS C 9306 HSPF path as a surrogate oracle / cross-path consistency gate only.
- Do not promote KS path results to common ISO expected values.
- Use the gate for shared-formula consistency plus accumulation and branch sanity checking.
- In test fixture scope, apply ISO16358-2 bin hours to the KS path and align the load-line basis with the ISO common path.
- Declare stage mapping explicitly: KS rated <-> ISO full, KS intermediate <-> ISO half, KS min <-> ISO min, KS max <-> ISO extended.
- Control KS-specific correction factors and policy knobs: defrost correction, -7°C fallback / capacity / power factor, `Cd`, `aux_cop`, and Korean-only correction.
- Compare bin-level diagnostics first: branch, load, capacity boundary, `P_j`, `E_j`, auxiliary energy, and HSTL / HSEC accumulation.
- Treat final HSPF assertion as a secondary signal only.

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
| 12 | Formula 50 frost full-to-extended branch | extended candidate가 있고 frost range에서 pi_ful,f(tj) < BL_h(tj) <= pi_ext,f(tj)이면 COP_fe,f(tj)를 tg~tf 사이에서 보간하고 P_fe(tj)=BL_h(tj)/COP_fe,f(tj)를 HSEC에 반영한다. backup heat는 0이다. |
| 13 | Saturated branch | BL_h > pi_ful이고 Formula 50 조건이 아니면 heat_pump_output = pi_ful(tj) × nj, heat_pump_energy = P_ful(tj) × nj. auxiliary_heat = BL_h(tj) - pi_ful(tj). auxiliary_energy = auxiliary_heat × nj / aux_cop. |
| 14 | Accumulate HSTL/HSEC | HSTL += BL_h(tj) × nj (건물 부하 전체). HSEC += heat_pump_energy + auxiliary_energy. |
| 15 | Finalize HSPF | HSPF = HSTL / HSEC, 3 significant digits로 반올림한다. |

## 15. ISO 16358-2 HSPF Top Pitfalls

| Pitfall | Symptom | Prevention |
| :--- | :--- | :--- |
| KS path와 ISO common path 혼용 | KS regression value가 바뀐다. | hspf.profile == "ks_c_9306_hspf"이면 반드시 KS path로만 진입한다. ISO common HSPF는 별도 entry point로 분리한다. |
| frost/non-frost 수식 혼용 | frost 구간 capacity/power가 과대 또는 과소 계산된다. | tj 판정을 수식 적용 직전에 반드시 수행한다. -7.0 < tj < 5.5 → frost 수식, 그 외 → non-frost 수식. |
| 2°C measured Half를 직접 사용 | 규격 각주 c 위반. 결과가 reference sheet와 다르다. | 2°C Half는 measured 값이 있어도 각주 d 수식으로 재계산한다. |
| 각주 d 수식 적용 순서 오류 | -7°C derived point가 없어 각주 d 수식이 실패한다. | -7°C derived point를 먼저 만든 뒤 각주 d 수식을 적용한다. |
| HSTL에 heat pump output만 누적 | auxiliary 발생 bin에서 HSTL이 과소 계산되어 HSPF가 낮게 나온다. | HSTL은 항상 BL_h(tj) × nj 전체를 누적한다. heat pump output이 아니다. |
| auxiliary_energy를 HSEC에서 누락 | HSPF가 과대 계산된다. | HSEC = heat_pump_energy + auxiliary_energy. aux_cop = 1.0 (전기히터 가정, 규격 미명시). |
| BL_h(tj) <= 0인 bin을 누적 | 냉방 구간 bin이 HSTL을 음수로 끌어내린다. | BL_h(tj) <= 0이면 해당 bin을 skip한다. |
| bin_details에서 KS 필드 구조 재사용 | ISO common HSPF bin_details와 KS bin_details가 섞인다. | ISO common HSPF bin_details는 KS 전용 필드를 포함하지 않는다. 표준 필드: tj, nj, bl_h, pi_j, P_j, case, heat_pump_energy, auxiliary_energy, E_j. |
| Hong Kong HSPF를 core 분기로 구현 | ISO common core가 지역별 정책에 오염된다. | Hong Kong MEELS extrapolation은 handler/preprocessor에서 canonical point로 변환하고, core는 region/country/trace_metadata를 계산 분기에 사용하지 않는다. |
| workbook oracle convention을 common path에 연결 | ISO common expected가 workbook layout에 종속된다. | Windows Excel COM (ISO 16358 mode) 값은 oracle benchmark로 분리하고, exact parity는 캘리브레이션을 통한 허용 오차 범위 내에서만 추구한다. |

## 16. ISO 16358-2 HSPF Test Strategy

| Test type | Purpose | Required cases |
| :--- | :--- | :--- |
| HSPF Hong Kong golden #1 | Hong Kong bin_hours 기반 golden 검증 | 7_full=6300W/1500W, 7_half=3200W/800W, Cd=0.25, Expected HSPF: 3.643 |
| HSPF Hong Kong golden #2 | Hong Kong bin_hours 기반 golden 검증 | 7_full=6100W/1300W, 7_half=3000W/600W, Cd=0.25, Expected HSPF: 4.571 |
| KS C 9306 HSPF regression | 기존 golden 유지 확인 | HSPF 3.689 유지 확인 (변경 없어야 함) |
| Korea CSPF regression | Korea CSPF golden 유지 확인 | CSPF 6.504 유지 확인 (변경 없어야 함) |
| validation smoke | 에러 처리 및 경계 조건 검증 | required point 누락 시 ValueError, BL_h <= 0 bin skip 확인, aux_cop = 0 시 ValueError |
