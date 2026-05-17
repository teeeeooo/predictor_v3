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

### Do not generalize KS-specific rules to ISO common path

위의 KS C 9306 전용 관행들은 ISO common path로 무리하게 흡수하거나 보편 적용해서는 안 된다. 이는 golden mismatch 해결이나 리팩토링 과정에서 임의로 변경하면 안 되는 강력한 safety boundary다.

- **ROUND_HALF_UP 반올림**: KS 시험값(Korean path)에만 적용하며, ISO 16358 common calculator 전체에 보편 적용하지 않는다.
- **BL(t_j) 산정 기준**: KS HSPF load line 및 `BL(t_j)`는 declared/rated cooling capacity 기반 계약을 엄격히 유지한다.
- **전력 보간 방식**: KS C 9306 전력 보간은 `ks_intersection` path를 유지하며, 타 region에 강제 적용하지 않는다.

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
| Maximum power line | Equation E.2.33 | 최대 운전 난방 소비전력선 | `P_h(t_j) = P_h3(-7.0) + (P_def - P_h3(-7.0)) * (t_j - (-7.0)) / (2 - (-7.0))`로 확정한다. 최대 능력 부족 구간에서 heat pump power로 사용한다. |
| Rated-maximum operating selection | Equation E.2.36 | rated-maximum interpolation | `P_h(t_j) = P_h23(t_j) = P_h3(t_g) + (P_h2(t_b) - P_h3(t_g)) * (t_j - t_g) / (t_b - t_g)`. 여기서 `P_h2(t_b)`는 Equation E.2.30의 `t_j`에 `t_b`를 대입한 값이고, `P_h3(t_g)`는 Equation E.2.33의 `t_j`에 `t_g`를 대입한 값이다. |
| 3-point operating selection, non-frost region | Equation E.2.37, Equation E.2.38 | minimum-intermediate, intermediate-rated interpolation | building load가 두 운전 능력선 사이에 있을 때 각 운전선과 building load의 교점 온도를 기준으로 power를 보간한다. 식 본문은 아래 확정 표를 따른다. |
| 3-point operating selection, frost region | Equation E.2.39, Equation E.2.40 | frost-region interpolation | 착상 영역에서 동일한 구조를 적용한다. 식 본문은 아래 확정 표를 따른다. |

### 9.1.1 Confirmed HSPF Performance Equations

아래 식은 원문 이미지, 기계판 추출물, 사용자 수기 확인을 종합해 구현 기준으로 고정한 난방 능력 및 소비전력 식이다. 괄호, stage 첨자, 교점 온도 방향은 그대로 유지한다.

Capacity curve:

| Equation | Region / case | Confirmed formula | Evaluation note |
| --- | --- | --- | --- |
| E.2.20 | minimum, non-frost | `Phi_hr(t_j) = Phi_hr1(t_j) = Phi_hr1(-7.0) + (Phi_hr1 - Phi_hr1(-7.0)) * (t_j - (-7.0)) / (7 - (-7.0))` | `Phi_hr1`은 7°C 최소 운전 난방 능력이다. |
| E.2.21 | minimum, frost | `Phi_hr(t_j) = Phi_def1(t_j) = Phi_hr1(-7.0) + (Phi_hr1(2) * (Phi_def / Phi_nof) - Phi_hr1(-7.0)) * (t_j - (-7.0)) / (2 - (-7.0))` | 2°C 최소 운전점에 defrost/no-frost ratio를 적용한다. 이중 제상 보정을 피한다. |
| E.2.22 | rated, non-frost | `Phi_hr(t_j) = Phi_hr2(t_j) = Phi_hr2(-7.0) + (Phi_hr2 - Phi_hr2(-7.0)) * (t_j - (-7.0)) / (7 - (-7.0))` | `Phi_hr2`는 7°C 정격 운전 난방 능력이다. |
| E.2.23 | rated, frost | `Phi_hr(t_j) = Phi_def2(t_j) = Phi_hr2(-7.0) + (Phi_hr2(2) * (Phi_def / Phi_nof) - Phi_hr2(-7.0)) * (t_j - (-7.0)) / (2 - (-7.0))` | 2°C 정격 운전점에 defrost/no-frost ratio를 적용한다. |
| E.2.24 | intermediate, non-frost | `Phi_hr(t_j) = Phi_hrm(t_j) = Phi_hrm(-7.0) + (Phi_hrm - Phi_hrm(-7.0)) * (t_j - (-7.0)) / (7 - (-7.0))` | `Phi_hrm`은 7°C 중간 운전 난방 능력이다. |
| E.2.25 | intermediate, frost | `Phi_hr(t_j) = Phi_defm(t_j) = Phi_hrm(-7.0) + (Phi_hrm(2) * (Phi_def / Phi_nof) - Phi_hrm(-7.0)) * (t_j - (-7.0)) / (2 - (-7.0))` | 2°C 중간 운전점에 defrost/no-frost ratio를 적용한다. |
| E.2.26 | maximum operation | `Phi_hr(t_j) = Phi_hr3(t_j) = Phi_hr3(-7.0) + (Phi_def - Phi_hr3(-7.0)) * (t_j - (-7.0)) / (2 - (-7.0))` | 최대 운전 저온 능력과 2°C 제상 능력을 연결한다. |

Power curve:

| Equation | Region / case | Confirmed formula | Evaluation note |
| --- | --- | --- | --- |
| E.2.27 | minimum, non-frost | `P_h(t_j) = P_h1(t_j) = P_h1(-7.0) + (P_h1 - P_h1(-7.0)) * (t_j - (-7.0)) / (7 - (-7.0))` | `P_h1`은 7°C 최소 운전 난방 소비전력이다. |
| E.2.28 | minimum, frost | `P_h(t_j) = P_def1(t_j) = P_h1(-7.0) + (P_h1(2) * (P_def / P_nof) - P_h1(-7.0)) * (t_j - (-7.0)) / (2 - (-7.0))` | 2°C 최소 운전점에 defrost/no-frost power ratio를 적용한다. |
| E.2.29 | rated, non-frost | `P_h(t_j) = P_h2(t_j) = P_h2(-7.0) + (P_h2 - P_h2(-7.0)) * (t_j - (-7.0)) / (7 - (-7.0))` | `P_h2`는 7°C 정격 운전 난방 소비전력이다. |
| E.2.30 | rated, frost | `P_h(t_j) = P_def2(t_j) = P_h2(-7.0) + (P_h2(2) * (P_def / P_nof) - P_h2(-7.0)) * (t_j - (-7.0)) / (2 - (-7.0))` | 2°C 정격 운전점에 defrost/no-frost power ratio를 적용한다. |
| E.2.31 | intermediate, non-frost | `P_h(t_j) = P_hm(t_j) = P_hm(-7.0) + (P_hm - P_hm(-7.0)) * (t_j - (-7.0)) / (7 - (-7.0))` | `P_hm`은 7°C 중간 운전 난방 소비전력이다. |
| E.2.32 | intermediate, frost | `P_h(t_j) = P_defm(t_j) = P_hm(-7.0) + (P_hm(2) * (P_def / P_nof) - P_hm(-7.0)) * (t_j - (-7.0)) / (2 - (-7.0))` | 2°C 중간 운전점에 defrost/no-frost power ratio를 적용한다. |
| E.2.33 | maximum operation | `P_h(t_j) = P_h3(-7.0) + (P_def - P_h3(-7.0)) * (t_j - (-7.0)) / (2 - (-7.0))` | `P_h3(-7.0)`는 최대 운전 저온 소비전력, `P_def`는 2°C 제상 조건 최대 운전 소비전력으로 해석한다. 중간 운전 첨자와 섞지 않는다. |
| E.2.37 | non-frost, minimum-intermediate | `P_h(t_j) = P_h1m(t_j) = P_hm(t_e) + (P_h1(t_c) - P_hm(t_e)) * (t_j - t_e) / (t_c - t_e)` | `P_h1(t_c)`는 E.2.27에 `t_c`를 대입한 값이고, `P_hm(t_e)`는 E.2.31에 `t_e`를 대입한 값이다. |
| E.2.38 | non-frost, intermediate-rated | `P_h(t_j) = P_h2m(t_j) = P_h2(t_a) + (P_hm(t_e) - P_h2(t_a)) * (t_j - t_a) / (t_e - t_a)` | `P_h2(t_a)`는 E.2.29에 `t_a`를 대입한 값이고, `P_hm(t_e)`는 E.2.31에 `t_e`를 대입한 값이다. |
| E.2.39 | frost, minimum-intermediate | `P_h(t_j) = P_h1m(t_j) = P_hm(t_f) + (P_h1(t_d) - P_hm(t_f)) * (t_j - t_f) / (t_d - t_f)` | `P_h1(t_d)`는 E.2.28에 `t_d`를 대입한 값이고, `P_hm(t_f)`는 E.2.32에 `t_f`를 대입한 값이다. |
| E.2.40 | frost, intermediate-rated | `P_h(t_j) = P_hm2(t_j) = P_h2(t_b) + (P_hm(t_f) - P_h2(t_b)) * (t_j - t_b) / (t_f - t_b)` | `P_h2(t_b)`는 E.2.30에 `t_b`를 대입한 값이고, `P_hm(t_f)`는 E.2.32에 `t_f`를 대입한 값이다. |

교점 온도 정의:

| Symbol | Meaning |
| --- | --- |
| `t_a` | 무착상 영역에서 building load와 정격 운전 능력선 E.2.22가 만나는 온도 |
| `t_b` | 착상 영역에서 building load와 정격 운전 능력선 E.2.23이 만나는 온도 |
| `t_c` | 무착상 영역에서 building load와 최소 운전 능력선 E.2.20이 만나는 온도 |
| `t_d` | 착상 영역에서 building load와 최소 운전 능력선 E.2.21이 만나는 온도 |
| `t_e` | 무착상 영역에서 building load와 중간 운전 능력선 E.2.24가 만나는 온도 |
| `t_f` | 착상 영역에서 building load와 중간 운전 능력선 E.2.25가 만나는 온도 |
| `t_g` | building load와 최대 운전 능력선 E.2.26이 만나는 온도 |

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

### 9.5 Production Input Schema

아래 구조를 KS C 9306 HSPF production 입력 스키마로 확정한다. 기존 JSON key 변경 없이 HSPF production path 안에서 nested field로 수용한다. Phase 1 synthetic H1/H2/H3 입력은 legacy/simple HSPF path로 유지하고, KS C 9306 production 입력과 같은 의미로 취급하지 않는다.

Canonical nested layout:

```python
{
    "ks_c_9306_hspf": {
        "capacity": {
            "min": {"7": ..., "2": ..., "-7": ...},
            "rated": {"7": ..., "2": ..., "-7": ...},
            "intermediate": {"7": ..., "2": ..., "-7": ...},
            "max": {"-7": ..., "def": ...}
        },
        "power": {
            "min": {"7": ..., "2": ..., "-7": ...},
            "rated": {"7": ..., "2": ..., "-7": ...},
            "intermediate": {"7": ..., "2": ..., "-7": ...},
            "max": {"-7": ..., "def": ...}
        },
        "correction": {
            "capacity_def_over_nof": 1 / 1.12,
            "power_def_over_nof": 1 / 1.06,
            "cd": 0.25
        },
        "load_line": {
            "slope": ...,
            "intercept": ...
        }
    }
}
```

확정 원칙:

1. Stage key는 `min`, `rated`, `intermediate`, `max`를 사용한다.
2. Temperature key는 `"7"`, `"2"`, `"-7"` 문자열을 사용한다.
3. Maximum stage의 2°C defrost anchor는 `"def"`로 둔다.
4. `capacity_def_over_nof`와 `power_def_over_nof`는 반드시 `def / nof` 방향이다.
5. `"-7"` 값은 production에서는 Table E.5 derived value로 보완 가능하지만, golden test fixture에서는 명시 입력한다.
6. `load_line`은 optional이다. 명시되면 E.2.36~E.2.40의 교점 온도 기반 power interpolation에 사용하고, 없으면 load 위치 기반 stage interpolation으로 fallback한다.
7. `load_line.slope`와 `load_line.intercept`는 `BL_h(t_j) = slope * t_j + intercept` 형식의 W 단위 선형 부하선이다.

| Field group | Candidate fields | Used by | Note |
| --- | --- | --- | --- |
| rated reference | existing rated capacity inputs | E.2.4, HSTL sanity check | 난방 building load가 냉방 기준과 연결되는지 원문 기준을 재확인한다. golden HSTL이 맞는 helper는 임의 변경하지 않는다. |
| minimum heating capacity | `capacity.min.7`, `capacity.min.2`, `capacity.min.-7` | E.2.20, E.2.21, E.2.37, E.2.39 | 7°C, 2°C, -7°C stage 값을 분리한다. `capacity.min.-7`은 Table E.5 derived value일 수 있다. |
| rated heating capacity | `capacity.rated.7`, `capacity.rated.2`, `capacity.rated.-7` | E.2.22, E.2.23, E.2.36, E.2.38, E.2.40 | rated stage capacity curve와 교점 계산에 사용한다. |
| intermediate heating capacity | `capacity.intermediate.7`, `capacity.intermediate.2`, `capacity.intermediate.-7` | E.2.24, E.2.25, E.2.37~E.2.40 | intermediate stage가 없을 때 fallback을 production 공식처럼 숨기지 않는다. |
| maximum heating capacity | `capacity.max.-7`, `capacity.max.def` | E.2.26, maximum shortage | 최대 운전 저온 능력과 2°C 제상 능력을 연결한다. |
| minimum heating power | `power.min.7`, `power.min.2`, `power.min.-7` | E.2.27, E.2.28, E.2.37, E.2.39 | cyclic minimum과 minimum-intermediate interpolation에 필요하다. |
| rated heating power | `power.rated.7`, `power.rated.2`, `power.rated.-7` | E.2.29, E.2.30, E.2.36, E.2.38, E.2.40 | rated branch와 rated-maximum interpolation에 필요하다. |
| intermediate heating power | `power.intermediate.7`, `power.intermediate.2`, `power.intermediate.-7` | E.2.31, E.2.32, E.2.37~E.2.40 | E.2.37~E.2.40 교점 기반 power interpolation의 anchor이다. |
| maximum heating power | `power.max.-7`, `power.max.def` | E.2.33, E.2.36, maximum shortage | E.2.33은 maximum stage 전용이다. intermediate power 변수와 섞지 않는다. |
| correction factors | `correction.capacity_def_over_nof`, `correction.power_def_over_nof`, `correction.cd` | E.2.21, E.2.23, E.2.25, E.2.28, E.2.30, E.2.32, E.2.6 | Table E.5 기본값은 각각 `1 / 1.12`, `1 / 1.06`, `0.25`이다. |
| heating load line | `load_line.slope`, `load_line.intercept` | E.2.36~E.2.40 | 교점 온도 `t_a`~`t_g`를 계산하기 위한 optional 부하선이다. 없으면 production path는 현재 bin의 `load`와 stage capacity 위치로 power를 보간한다. |
| region data | heating bin-hour table, frost boundaries | bin loop, E.2.20~E.2.40 branch selection | `-7.0°C`, `5.5°C` 경계는 non-frost로 처리한다. |

### 9.5.1 Current KS HSPF Implementation Policies

Stage별 2°C fallback 정책:

| Case | Required behavior |
| --- | --- |
| `min`/`rated`/`intermediate` stage에 `"2"` 입력값 있음 | 입력값을 그대로 사용한다. |
| `"2"` 입력값 없음, `"-7"` 입력값 있음 | stage별 `"-7"`과 `"7"` 사이에서 2°C 값을 선형보간한다. |
| `"2"` 입력값 없음, `"-7"` 입력값도 없음 | Table E.5 derived factor로 `"-7"` 값을 만든 뒤 2°C 값을 선형보간한다. |
| capacity derived `"-7"` | `7°C × 0.601` |
| power derived `"-7"` | `7°C × 0.801` |
| derived `"2"` formula | `value_2 = value_minus7 + (value_7 - value_minus7) × 9 / 14` |

`defrost/no-frost` correction은 stage별 2°C 값을 만든 이후 curve 함수에서만 적용한다. `_ks_hspf_stage_value()`에서는 `def_over_nof` correction을 적용하지 않는다.

Maximum stage 정책:

| Rule | Required behavior |
| --- | --- |
| fallback 대상 여부 | max stage는 fallback 대상이 아니다. |
| required anchors | `max.-7`과 `max.def`는 required anchor이다. |
| usage | capacity E.2.26, power E.2.33에 사용한다. |

KS profile fallback 금지:

| Condition | Required behavior |
| --- | --- |
| `hspf.profile == "ks_c_9306_hspf"` | 반드시 KS path로 진입한다. |
| `ks_c_9306_hspf` input 누락 | `ValueError`를 발생시킨다. |
| common fallback | 금지한다. |

Region config `hspf.load_line` schema:

| Field | Required | Note |
| --- | --- | --- |
| `source` | Yes | 허용값은 `rated_heating_capacity`, `rated_cooling_capacity`, `declared_capacity`이다. |
| `zero_load_temp` | Yes | zero heating load temperature이다. |
| `full_load_temp` | Yes | full heating load temperature이다. |
| `rated_capacity_factor` | Yes | 기준 capacity에 곱하는 계수이다. |

현재 Korea는 `source = rated_cooling_capacity`, `full_load_temp = 0.0`, `rated_capacity_factor = 0.82`를 사용한다. `capacity_source` key는 사용하지 않는다.

Production config와 golden fixture 분리:

| Location | Allowed data |
| --- | --- |
| production `data/region_configs/korea.json` | KS 원문 bin과 공식 계수 |
| tests fixture | golden/sample/test 전용 2-bin 값 또는 축약 fixture |

production `korea.json`에는 golden/sample/test 전용 2-bin 값을 넣지 않는다.

### 9.6 Implementation Checkpoints

| Step | Fixed decision | Regression risk |
| --- | --- | --- |
| 1 | 기존 CSPF path와 public API를 변경하지 않는다. | CSPF golden `6.504`가 깨지면 HSPF 작업을 중단한다. |
| 2 | KS C 9306 HSPF production path는 ISO common calculator 안에 두되, KS-only assumptions는 region-specific branch로 격리한다. | KS C 9306 식이 ISO 16358 generic HSPF path에 섞이면 다른 region 확장이 어려워진다. |
| 3 | E.2.20~E.2.33 성능선 helper를 먼저 만들고, E.2.36~E.2.40 operating selection은 그 helper의 평가값만 사용한다. | 같은 식을 branch마다 재작성하면 첨자 혼동이 발생한다. |
| 4 | frost/non-frost branch를 먼저 결정한 뒤 해당 영역의 capacity/power curve를 평가한다. | defrost ratio를 interpolation 뒤에 다시 적용하면 이중 보정된다. |
| 5 | capacity shortage와 cyclic minimum은 별도 branch로 유지한다. | shortage를 PLF로 처리하거나 cyclic을 auxiliary로 처리하면 HSEC가 틀어진다. |
| 6 | auxiliary energy는 HSEC에 반드시 포함하고, HSTL은 전체 building load로 유지한다. | auxiliary 누락은 HSPF 과대평가로 이어진다. |

### 9.7 HSPF Test Strategy

| Test | Input | Expected |
| --- | --- | --- |
| HSPF official golden sample | rated heating capacity 4300 W, 7°C full/half/min, 2°C defrost, -7°C max | HSPF 3.689, HSTL 6651225.0 Wh, heat pump energy 1785292.6 Wh, auxiliary energy 17477.1 Wh, HSEC 1802769.7 Wh |
| production schema fixture | same official measured points represented as `ks_c_9306_hspf.capacity.*`, `ks_c_9306_hspf.power.*`, and `correction.*` | fixture keys follow the confirmed nested schema before production implementation starts |
| Phase 1 adapter fixture | official measured points mapped to H1 full/half/min, H2 defrost/full-equivalent, H3 max/full-equivalent | temporary adapter only; do not treat it as the production KS C 9306 input schema |
| E.2.20~E.2.33 curve anchors | one fixture with explicit 7°C, 2°C, -7°C values | each curve returns the exact anchor value at its anchor temperature |
| frost boundary | `t_j = -7.0°C`, `t_j = 5.5°C` | boundary values are treated as non-frost region |
| frost interior | representative `-7.0°C < t_j < 5.5°C` | E.2.21/E.2.23/E.2.25 and E.2.28/E.2.30/E.2.32 are selected |
| cyclic minimum | `BL_h(t_j) <= Q_min(t_j)` | PLF applied, auxiliary energy 0 |
| minimum-intermediate interpolation | `Q_min < BL_h <= Q_mid` | Equation E.2.37/E.2.39 branch selected |
| intermediate-rated interpolation | `Q_mid < BL_h <= Q_rated` | Equation E.2.38/E.2.40 branch selected |
| rated-maximum interpolation | `Q_rated < BL_h <= Q_max` | Equation E.2.36 branch selected and `P_h2(t_b)`/`P_h3(t_g)` interpolation applied |
| intersection interpolation | fixture with `load_line.slope` and `load_line.intercept` | Equation E.2.36~E.2.40 use intersection temperatures instead of direct load-position interpolation |
| maximum shortage | `BL_h > Q_max` | heat pump output capped, auxiliary energy positive |
| denominator accounting | fixture with shortage bins | HSEC equals heat pump energy plus auxiliary energy |
| CSPF regression | existing KS CSPF golden sample | CSPF 6.504 remains unchanged |

### 9.8 Current Regression Checklist

| Check | Command / target |
| --- | --- |
| HSPF validation | `python3 -B -m pytest tests/test_iso16358_hspf_validation.py -v` |
| HSPF golden | `python3 -B -m pytest tests/_legacy/test_iso16358_hspf_golden_diagnostic.py -v` |
| HSPF smoke | `python3 -B -m pytest tests/test_iso16358_hspf_smoke.py -v` |
| Korea CSPF regression | CSPF one-liner must keep `6.504` |
| JSON validation | `python3 -B -m json.tool data/region_configs/korea.json` |
| syntax check | `python3 -B -m py_compile core/calculator_iso16358.py` |

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
