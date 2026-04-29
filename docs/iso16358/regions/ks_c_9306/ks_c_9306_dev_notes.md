# KS C 9306 Dev Notes

## 1. Purpose

이 문서는 KS C 9306 region 구현을 수정하거나 검증할 때 필요한 구현 노하우, 실수 방지 규칙, 디버깅 방법, 테스트 전략을 정리한다. 공통 ISO 용어는 [../../iso16358_glossary.md](../../iso16358_glossary.md)를 참조하고, KS 고유 용어는 [ks_c_9306_glossary.md](./ks_c_9306_glossary.md)를 참조한다. 이 문서에는 glossary 본문을 중복 작성하지 않는다.

## 2. Top Implementation Pitfalls

| Pitfall | Symptom | Cause | Prevention |
| --- | --- | --- | --- |
| ROUND_HALF_UP 누락 | golden sample의 CSPF와 annual power가 어긋난다. | raw float 시험값을 그대로 사용한다. | `round_test_values` 적용 위치를 먼저 확인한다. |
| Python `round()` 사용 | .5 경계에서 인증 계산과 다른 정수가 나온다. | bankers rounding이 적용된다. | Decimal 기반 HALF_UP helper를 사용한다. |
| declared capacity 누락 | ValueError가 발생하거나 BL(tj)가 잘못 잡힌다. | 한국은 measured reference가 아니라 declared source이다. | `building_load_source = declared`를 유지한다. |
| `ks_intersection` 미적용 | 중간 용량 범위 power가 golden과 달라진다. | 기본 capacity-linear interpolation으로 fallback된다. | `power_interpolation_method`를 확인한다. |
| 외삽 과신 | 고온/저온 bin에서 비현실적인 capacity/power가 나온다. | 시험점 두 개로 선형 외삽한다. | 외삽 bin과 BL > max_cap branch를 함께 점검한다. |
| BL > max_cap 처리 변경 | cooling output이 과대 계산된다. | 요구 부하를 항상 처리한다고 가정한다. | 최고 용량 초과 시 output cap을 유지한다. |

## 3. `round_test_values` Application

| Target | Applied | Reason |
| --- | --- | --- |
| measured `capacity` | Yes | KS 시험값은 계산 전 정수 반올림한다. |
| measured `power` | Yes | KS 시험값은 계산 전 정수 반올림한다. |
| derived `capacity` | Yes | 파생 factor 적용 후 정수 반올림한다. |
| derived `power` | Yes | 파생 factor 적용 후 정수 반올림한다. |
| `declared_capacity` | Yes | BL(tj)의 기준값도 정수화된 declared capacity를 사용한다. |
| non-numeric metadata | No | 계산 대상이 아니다. |

## 4. `power_interpolation_method` Separation

`power_interpolation_method = ks_intersection`은 KS C 9306 region 전용 동작이다. ISO 공통 기본 동작인 capacity-linear interpolation과 분리되어야 한다.

| Method | Use case | Risk if mixed |
| --- | --- | --- |
| `capacity_linear` | ISO 공통 기본 보간 | KS golden sample 불일치 |
| `ks_intersection` | KS C 9306 중간 부하 전력 산정 | 타 region에 적용하면 국가별 특례가 누출됨 |

구현 판단: KS method가 실패해 `None`을 반환할 때만 공통 capacity-linear fallback을 허용한다. 이 fallback은 방어 로직이지 KS 주 계산 경로가 아니다.

## 5. Extrapolation Handling

| Condition | Behavior | Debug check |
| --- | --- | --- |
| tj below measured temperature range | 가장 낮은 두 시험온도로 외삽한다. | 24°C bin에서 29°C/35°C 시험선 외삽 결과를 확인한다. |
| tj above measured temperature range | 가장 높은 두 시험온도로 외삽한다. | 36~37°C bin에서 capacity와 power가 의도 범위인지 확인한다. |
| `nj = 0` | 누적에서 제외한다. | 38°C bin은 계산 결과에 영향을 주지 않아야 한다. |
| extrapolated capacity below load | BL > max_cap branch로 넘어갈 수 있다. | cooling output cap과 annual cooling 결과를 확인한다. |

## 6. BL > max_cap Handling

BL(tj)가 해당 온도의 최고 capacity보다 크면 장비가 요구 부하를 모두 처리한다고 가정하지 않는다. 이 경우 cooling output은 highest capacity로 제한되고, power는 highest power를 사용한다.

검증 포인트:

| Check | Expected |
| --- | --- |
| cooling output | Lc가 아니라 highest capacity |
| power | highest power |
| annual cooling | 요구 부하 전체 합보다 작아질 수 있음 |
| CSPF | 출력 cap과 power cap이 함께 반영됨 |

## 7. `recommend_35_half_capacity` Structure

이 helper는 CSPF 본계산에 사용하지 않는 독립 추천 계산이다. 목적은 35°C half capacity 목표값을 설계 검토용으로 산정하는 것이다.

| Step | Meaning |
| --- | --- |
| 1 | 29°C minimum capacity를 35°C minimum capacity로 환산한다. |
| 2 | minimum capacity line과 building load line의 교점 온도 `T_min`을 구한다. |
| 3 | `T_min`과 35°C 사이의 중간 온도 `T_mid`를 구한다. |
| 4 | `T_mid`의 building load를 구한다. |
| 5 | 29↔35°C capacity factor를 반영해 35°C half target을 산정한다. |

실수 방지: 이 helper의 반환값을 CSPF 계산 입력으로 자동 대체하면 안 된다. 시험값과 설계 추천값의 역할을 분리해야 한다.

## 8. Test Strategy

| Test | Input | Expected |
| --- | --- | --- |
| golden sample | declared 6000 W, 35_full 6035.8/1641.4, 35_half 3420.4/679.4, 29_min 1759.6/201.7 | CSPF 6.504 |
| rounding test | .5 경계 capacity/power | ROUND_HALF_UP 결과 |
| missing declared capacity | `declared_capacity = None` | ValueError |
| method separation | `power_interpolation_method` changed | golden mismatch should be detected |
| BL cap branch | artificially low max capacity | cooling output capped |
| recommendation helper | positive full/min capacity | returns T_min, T_mid, target half capacity |

## 9. HSPF Variable-Capacity Implementation Notes

이 섹션은 `KS_C_9306.pdf` OCR, 원문 이미지 확인, standard.go.kr 기계판 추출을 기반으로 ISO 16358-2 / KS C 9306 HSPF 구현 전에 따라야 할 구현 순서를 정리한다. OCR은 수식 기호, 첨자, 표 구조를 오인식할 수 있으므로, 식의 계수와 기호를 코드에 반영하기 전에는 반드시 원문 이미지를 다시 확인한다. 기계판 추출 결과는 [ks_c_9306_machine_extract.md](./ks_c_9306_machine_extract.md)를 참조한다.

상세 용어 정의는 [ks_c_9306_glossary.md](./ks_c_9306_glossary.md)와 [../../iso16358_glossary.md](../../iso16358_glossary.md)를 참조한다. 이 문서에는 glossary 본문을 중복 작성하지 않는다.

### 9.1 Source Equation Map

| Implementation item | KS C 9306 reference | Role | Implementation note |
| --- | --- | --- | --- |
| HSPF seasonal heat load | Equation E.2.1 | 난방 기간 총 난방량 합계 | `load * hours`를 Wh 단위로 누적한다. |
| HSPF seasonal energy | Equation E.2.2 | 난방 기간 총 난방 소비 전력량 합계 | heat pump energy와 auxiliary energy를 합산한다. |
| HSPF ratio | Equation E.2.3 | 난방 기간 에너지 소비 효율 | `HSTL / HSEC`로 계산한다. |
| Heating building load | Equation E.2.4 | 온도별 건물 난방 부하 | golden HSTL 검증이 이미 맞는 helper는 임의 변경하지 않는다. |
| Heating load ratio | Equation E.2.5 | 건물 부하와 난방 능력의 비 | ratio는 cyclic/PLF 구간에서 0~1 범위로 제한한다. |
| Heating PLF | Equation E.2.6 | 단속 운전 효율 저하 | building load가 minimum capacity 이하일 때만 적용한다. |
| Auxiliary heater energy | Equation E.2.7 | 난방 능력 부족분 보조 전열 장치 소비 전력량 | heat pump capacity가 building load보다 작을 때 부족분을 Wh로 합산한다. |
| Minimum capacity, non-frost region | Equation E.2.20 | 최소 운전 난방 능력선 | 원문 이미지에서 `t_j <= -7.0°C` 또는 `5.5°C <= t_j` 무착상 구간을 확인했다. |
| Minimum capacity, frost region | Equation E.2.21 | 착상 영역 최소 운전 난방 능력선 | 원문 이미지에서 `-7.0°C < t_j < 5.5°C` 착상 구간을 확인했다. |
| Rated capacity lines | Equation E.2.22, Equation E.2.23 | 정격 운전 난방 능력선 | 무착상/착상 영역을 분리한다. OCR의 첨자와 계수는 원문 이미지 대조 필요. |
| Intermediate capacity lines | Equation E.2.24, Equation E.2.25 | 중간 운전 난방 능력선 | 무착상/착상 영역을 분리한다. H1 중간점만 있을 때의 fallback은 별도 TODO로 둔다. |
| Maximum capacity line | Equation E.2.26 | 최대 운전 난방 능력선 | 최대 능력 부족 구간에서 heat pump output cap으로 사용한다. |
| Minimum power lines | Equation E.2.27, Equation E.2.28 | 최소 운전 난방 소비전력선 | 무착상/착상 영역을 분리한다. |
| Rated power lines | Equation E.2.29, Equation E.2.30 | 정격 운전 난방 소비전력선 | 무착상/착상 영역을 분리한다. |
| Intermediate power lines | Equation E.2.31, Equation E.2.32 | 중간 운전 난방 소비전력선 | 무착상/착상 영역을 분리한다. |
| Maximum power line | Equation E.2.33 | 최대 운전 난방 소비전력선 | 최대 능력 부족 구간에서 heat pump power로 사용한다. |
| Rated-maximum operating selection | Equation E.2.36 | rated-maximum interpolation | `P_h(t_j) = P_h23(t_j) = P_h3(t_g) + (P_h2(t_b) - P_h3(t_g)) * (t_j - t_g) / (t_b - t_g)`. 여기서 `P_h2(t_b)`는 Equation E.2.30의 `t_j`에 `t_b`를 대입한 값이고, `P_h3(t_g)`는 Equation E.2.33의 `t_j`에 `t_g`를 대입한 값이다. |
| 3-point operating selection, non-frost region | Equation E.2.37, Equation E.2.38 | minimum-intermediate, intermediate-rated interpolation | building load가 두 운전 능력선 사이에 있을 때 각 운전선과 building load의 교점 온도를 기준으로 power를 보간한다. |
| 3-point operating selection, frost region | Equation E.2.39, Equation E.2.40 | frost-region interpolation | 착상 영역에서 동일한 구조를 적용한다. 원문 이미지로 식 분자/분모의 온도 방향을 재확인한다. |

### 9.2 Correct HSPF Calculation Order

1. HSPF region configuration을 로드한다.
2. heating bin-hour를 absolute hours로 준비한다.
3. 각 bin의 outdoor temperature `t_j`와 hours를 읽는다.
4. Equation E.2.4 기준으로 building load `BL_h(t_j)`를 계산한다.
5. `t_j`가 무착상 영역인지 착상 영역인지 판정한다.
6. 해당 영역의 minimum, intermediate, rated, maximum capacity curve를 만든다.
7. 같은 영역의 minimum, intermediate, rated, maximum power curve를 만든다.
8. `BL_h(t_j)`와 운전 능력선을 비교해 operating case를 결정한다.
9. `BL_h(t_j)`가 minimum capacity 이하이면 Equation E.2.5와 Equation E.2.6의 ratio/PLF를 적용한다.
10. `BL_h(t_j)`가 두 운전점 사이이면 Equation E.2.37~E.2.40 구조에 따라 교점 기반 power interpolation을 적용한다.
11. `BL_h(t_j)`가 maximum capacity보다 크면 heat pump output은 maximum capacity로 제한하고, 부족분은 Equation E.2.7의 auxiliary energy로 합산한다.
12. `bin_load = BL_h(t_j) * hours`를 HSTL에 누적한다.
13. `bin_energy = heat_pump_energy + auxiliary_energy`를 HSEC에 누적한다.
14. `HSPF = HSTL / HSEC`를 계산한다.

### 9.3 Operating Case Rules

| Case | Condition | Heat pump output | Heat pump power | Auxiliary |
| --- | --- | --- | --- | --- |
| cyclic minimum | `BL_h(t_j) <= Q_min(t_j)` | `BL_h(t_j)` | minimum power corrected by PLF | 0 |
| minimum-intermediate | `Q_min(t_j) < BL_h(t_j) <= Q_mid(t_j)` | `BL_h(t_j)` | Equation E.2.37 or E.2.39 interpolation | 0 |
| intermediate-rated | `Q_mid(t_j) < BL_h(t_j) <= Q_rated(t_j)` | `BL_h(t_j)` | Equation E.2.38 or E.2.40 interpolation | 0 |
| rated-maximum | `Q_rated(t_j) < BL_h(t_j) <= Q_max(t_j)` | `BL_h(t_j)` | Equation E.2.36 interpolation between `P_h3(t_g)` and `P_h2(t_b)` | 0 |
| maximum shortage | `BL_h(t_j) > Q_max(t_j)` | `Q_max(t_j)` | `P_max(t_j)` | `BL_h(t_j) - Q_max(t_j)` |

Equation E.2.36은 사용자 원문 확인으로 수식 본문과 보간 방향을 확정했다. 구현 시 `t_b == t_g` 방어는 입력 검증 또는 계산 분기에서 처리한다.

### 9.4 Frost / Defrost Handling

| Item | Current interpretation | Required check before coding |
| --- | --- | --- |
| frost boundary | 원문 이미지에서 `-7.0°C < t_j < 5.5°C`가 착상 영역임을 확인했다. | 경계값 `-7.0°C`, `5.5°C`는 착상 영역에 포함하지 않는다. |
| non-frost boundary | 원문 이미지에서 `t_j <= -7.0°C` 또는 `5.5°C <= t_j`가 무착상 영역임을 확인했다. | 경계값은 무착상 영역으로 처리한다. |
| defrost measured points | KS 문서는 stage별 난방 제상 능력/전력과 난방 제상 무착상 능력/전력을 별도 시험 항목으로 둔다. | production schema에서는 단일 H2 defrost 값을 전체 stage에 공통 적용하지 말고, stage-specific defrost/no-frost fields를 구분한다. |
| fallback rule | H2/H3 half/min 실측이 없으면 H1 partial point를 high-stage 온도 변화율로 보정하는 임시 fallback을 쓸 수 있다. | 공식에 없는 fallback은 TODO로 표시하고 golden test 전용 adapter와 production path를 구분한다. |

### 9.5 HSPF Test Strategy

| Test | Input | Expected |
| --- | --- | --- |
| HSPF golden sample | rated heating capacity 4300 W, H1 full/half/min, H2 defrost/full-equivalent, H3 max/full-equivalent | HSPF 3.689, HSTL 6651225.0 Wh, HSEC 1802769.7 Wh |
| cyclic minimum | `BL_h(t_j) <= Q_min(t_j)` | PLF applied, auxiliary energy 0 |
| minimum-intermediate interpolation | `Q_min < BL_h <= Q_mid` | Equation E.2.37/E.2.39 branch selected |
| intermediate-rated interpolation | `Q_mid < BL_h <= Q_rated` | Equation E.2.38/E.2.40 branch selected |
| rated-maximum interpolation | `Q_rated < BL_h <= Q_max` | Equation E.2.36 branch selected and `P_h2(t_b)`/`P_h3(t_g)` interpolation applied |
| maximum shortage | `BL_h > Q_max` | heat pump output capped, auxiliary energy positive |
| frost boundary | `t_j = -7.0°C`, `t_j = 5.5°C` | boundary values are treated as non-frost region |

## 10. Prompt Snippets for Agent

Agent 재사용 프롬프트:

> AGENTS.md와 docs/DOCS_GUIDELINES.md를 먼저 읽는다. KS C 9306 계산을 수정하기 전에 docs/iso16358/iso16358_dev_notes.md와 docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md를 확인한다. ISO 공통 문서에는 KS 전용 내용을 추가하지 않는다. KS 변경 후 golden sample에서 CSPF 6.504, annual cooling 1943.798 kWh, annual power 298.852 kWh가 유지되는지 확인한다.

HSPF 작업용 프롬프트:

> AGENTS.md Lite 규칙을 따른다. ISO16358/KS C 9306 HSPF를 수정하기 전에 docs/iso16358/iso16358_notes.md, docs/iso16358/iso16358_dev_notes.md, docs/iso16358/regions/ks_c_9306/ks_c_9306_notes.md, docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md를 읽는다. CSPF 로직과 golden expected는 변경하지 않는다. KS C 9306 Equation E.2.20~E.2.40은 OCR 텍스트만 믿지 말고 KS_C_9306.pdf 원문 이미지와 대조한다. 변경 후 HSPF golden, HSPF smoke, KS CSPF golden regression을 실행한다.

## 11. References

| Source | Usage |
| --- | --- |
| [ks_c_9306_notes.md](./ks_c_9306_notes.md) | KS 계산 구조와 golden sample |
| [ks_c_9306_glossary.md](./ks_c_9306_glossary.md) | KS 고유 용어와 데이터 위치 |
| [../../iso16358_dev_notes.md](../../iso16358_dev_notes.md) | 공통 엔진 구현 지침 |
| `KS_C_9306.pdf` | Equation E.2.20~E.2.40 원문 이미지 확인 |
| [ks_c_9306_machine_extract.md](./ks_c_9306_machine_extract.md) | standard.go.kr 기계판 추출 결과, Table E.5 계수, HSPF formula image map |
| `data/region_configs/korea.json` | KS region configuration |
| `core/calculator_iso16358.py` | 구현 동작 확인 |
