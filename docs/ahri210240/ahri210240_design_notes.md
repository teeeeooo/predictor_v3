# AHRI 210/240 Design Notes

## 1. Purpose

이 문서는 AHRI 210/240 Appendix M의 SEER/HSPF와 Appendix M1의 HSPF2/SEER2가 실제 히트펌프와 에어컨 제품 설계에 주는 의미를 정리한다. M과 M1은 서로 다른 standard edition과 시험점/계절 계산 경로이므로 설계 해석을 분리한다. M HSPF는 Region IV 난방 성능을 중심으로 다루고, M1 HSPF2/SEER2는 현재 확인 가능한 범위까지만 다룬다.

핵심 관점은 단일 정격점의 높은 효율보다, 계절 중 자주 발생하는 외기온에서 건물 부하를 얼마나 낮은 전력으로 안정적으로 따라가는지가 최종 등급을 좌우한다는 점이다. M과 M1의 등급은 bin table, 부하선, 보간/제상 규칙이 다르므로 숫자만으로 직접 비교하지 않는다. 근거: AHRI 210/240-2017 Appendix M Tables 19/20 및 AHRI 210/240-2026 Table 16, Section 11.

## 2. Quick Glossary

전체 용어 및 기호 정의는 `ahri210240_glossary.md`를 참조하라.

| 용어 | 간략 의미 | 설계상 핵심 |
| --- | --- | --- |
| HSPF2 | 난방 계절 성능 계수 2 | 저온 용량, 부분부하 효율, 보조열 사용량이 함께 반영된다. |
| SEER2 | 냉방 계절 에너지 효율 2 | 저속 및 중간속 냉방 효율이 계절 에너지 사용량을 좌우한다. |
| BL(tj) | 외기온 bin별 건물 부하 | 장비 용량선과의 교차 위치가 운전 Case를 결정한다. |
| fractional bin hours | 외기온 bin 시간 가중치 | HLH와 곱해 계절 부하와 에너지 합산 시간을 만든다. |
| Case I | 저속 cycling 구간 | 최소 용량이 너무 크면 cycling 손실이 커진다. |
| Case II | 중간속 보간 구간 | low와 full 사이의 중간속 효율 위치가 중요하다. |
| Case III | full-speed 및 보조열 구간 | 용량 부족분이 보조열로 전환되어 HSPF2를 낮춘다. |
| H2Int | 중간속 난방 시험점 | Case II COP 보간의 중심이 된다. |
| H32/H42 | 저온 full-load 난방 시험점 | 17°F 및 5°F 주변 저온 용량 유지 능력을 나타낸다. |
| Fdef | 제상 보정계수 | frost 조건의 제상 시간과 회복 손실 영향을 추적한다. |

### Appendix M / M1 distinction

| 구분 | Appendix M | Appendix M1 |
| --- | --- | --- |
| 표준 계열 | AHRI 210/240-2017 Appendix M; HSPF는 Addendum 1 포함 | AHRI 210/240-2026 |
| 지표 | SEER / HSPF | SEER2 / HSPF2 |
| 현재 제품 범위 | variable-speed, non-ducted, single-split; HSPF는 Region IV | current variable-capacity 경로; HSPF2는 Region IV 중심 |
| 냉방 시험점 | A2, B2, EV, B1, F1 | A/B/E/F 계열의 M1 schema |
| 난방 시험점 | H01, H11, H1N, H2V, H32; H12/H22 optional | H01, H11, H1N, H2Int, H32; H12/H22/H42 및 product policy |
| 해석 규칙 | M 전용 bin, intermediate 및 defrost semantics | M1 전용 bin, Case 및 product/region policy |

M의 `H2V`와 M1의 `H2Int`, M의 `HSPF`와 M1의 `HSPF2`는 이름이 비슷해도 같은 입력 또는 같은 성능 지점을 뜻하지 않는다.

## 3. Metric Structure

| 지표 | 구성 | 설계상 의미 | 근거 |
| --- | --- | --- | --- |
| HSPF2 | Region IV 계절 난방 부하 / 압축기 에너지와 보조열 에너지 합 | 저온 용량, 부분부하 효율, 보조열 사용이 함께 반영된다. | AHRI 210/240-2026 Section 11, Table 16 |
| 난방 bin 부하 | 외기온별 건물 부하선 | 온도가 낮아질수록 부하가 커지고, 용량 부족 시 보조열이 증가한다. | AHRI 210/240-2026 Equation 11.104 |
| SEER2 | 냉방 bin별 냉방량 / 냉방 에너지 합 | 중간 외기온의 저속 및 중간속 효율이 중요하다. | AHRI 210/240 cooling rating sections |
| HSPF | Appendix M Region IV 계절 난방 부하 / 압축기 및 저항 보조열 에너지 합 | H2V intermediate 위치, 저온 용량, 제상 credit이 함께 반영된다. | AHRI 210/240-2017 Appendix M Addendum 1, Table 20 |
| SEER | Appendix M cooling bin별 냉방량 / 냉방 에너지 합 | EV intermediate 위치와 A2/B2/F1/B1 curve가 계절 효율을 좌우한다. | AHRI 210/240-2017 Appendix M, Table 19 |

왜 중요한가: 계절 등급은 시험점 효율의 단순 평균이 아니다. 외기온 bin의 시간 가중치와 부하선이 결합되므로, 자주 나타나는 온도에서의 운전 안정성과 효율이 최종 지표에 더 큰 영향을 준다.

## 4. What Actually Drives the Rating

| 우선순위 | 등급을 움직이는 요소 | 영향 방향 | 근거 |
| --- | --- | --- | --- |
| 1 | Region IV에서 시간이 큰 난방 bin의 부분부하 효율 | 해당 구간 소비전력이 낮을수록 HSPF2가 오른다. | AHRI 210/240-2026 Table 16 |
| 2 | 저온 full-speed 용량 유지 | 건물 부하를 넘지 못하면 보조열 에너지가 증가한다. | AHRI 210/240-2026 Case III path |
| 3 | 저속 최소 운전 용량과 cycling 손실 | 저부하에서 과대 용량이면 부분부하 보정 손실이 커진다. | AHRI 210/240-2026 Case I path |
| 4 | 중간속 성능의 위치 | low와 full 사이에서 효율 보간 경로를 결정한다. | AHRI 210/240-2026 Equation 11.199~11.204 |
| 5 | 제상 운전 영향 | frost 조건에서 시험 시간과 제상 특성이 난방 계절 성능에 영향을 준다. | AHRI 210/240-2026 Equation 11.107 |
| 6 | 냉방 중간속/저속 효율 | SEER2에서 부분부하 구간 에너지 사용을 낮춘다. | AHRI 210/240 cooling rating sections |

## 5. High Impact Design Parameters

| 설계 인자 | 효과 | 설계 방향 | 근거 |
| --- | --- | --- | --- |
| 압축기 저속 안정 범위 | Case I cycling 손실을 줄인다. | 낮은 부하에서도 정지/재기동 없이 안정 운전하도록 최소 용량을 낮춘다. | AHRI 210/240-2026 Case I path |
| 중간속 운전점 | Case II 효율을 좌우한다. | low와 full 사이에서 물리적으로 자연스러운 용량과 전력 위치를 만든다. | AHRI 210/240-2026 Equation 11.199~11.204 |
| 17°F 및 5°F 저온 용량 | 보조열 사용을 줄인다. | 열교환기, 압축기 운전 영역, 냉매량을 저온 난방에 맞춘다. | AHRI 210/240-2026 Case III path |
| 35°F frost 조건 성능 | H22와 중간속 계열의 기준이 된다. | frost accumulation 조건에서 용량과 전력 악화를 억제한다. | AHRI 210/240-2026 Equation 11.44, Equation 11.50 |
| 제상 제어 | 난방 에너지 손실을 줄인다. | 필요한 시점에만 제상하고 제상 회복 시간을 짧게 한다. | AHRI 210/240-2026 Equation 11.107 |
| 냉방 중간 외기온 효율 | SEER2 부분부하 성능을 높인다. | 82~87°F 부근에서 중간속 효율을 높인다. | AHRI 210/240 cooling rating sections |

## 6. Low Impact / Misleading Design Parameters

| 항목 | 오해 | 실제 판단 |
| --- | --- | --- |
| 최고 난방 용량만 확대 | HSPF2가 자동으로 오른다고 보기 쉽다. | 저부하 bin에서 cycling 손실이 커질 수 있으므로 저속 안정성이 함께 필요하다. |
| 47°F full-load 효율만 개선 | 전체 난방 등급을 대표한다고 보기 쉽다. | Region IV는 여러 외기온 bin을 사용하며, 35°F와 17°F 근처 성능도 중요하다. |
| 보조열을 설계 여유로만 취급 | 용량 부족을 쉽게 보완한다고 보기 쉽다. | 보조열은 계절 에너지 denominator를 크게 늘려 HSPF2를 낮춘다. |
| 제상 시간을 작게만 보이게 함 | 시험값만 좋으면 된다고 보기 쉽다. | 실제 frost 조건에서 빈번한 제상은 용량과 쾌적성 모두에 불리하다. |
| 냉방 A full-load만 최적화 | SEER2가 크게 개선된다고 보기 쉽다. | 저속 및 중간속 냉방 bin 효율이 계절값에 큰 영향을 줄 수 있다. |

## 7. Seasonal Bin Strategy

Region IV HSPF2는 Table 16의 fractional bin hours를 Heating Load Hours와 곱해 계절 시간을 만든다. 근거: AHRI 210/240-2026 Table 16. 설계자는 특정 저온점 하나만 볼 것이 아니라, 시간이 배정된 bin 전체에서 건물 부하선과 장비 용량선이 어디서 만나는지 확인해야 한다.

| 온도 구간 | 설계 초점 | 이유 | 근거 |
| --- | --- | --- | --- |
| 온화한 난방 bin | 낮은 최소 용량과 높은 저속 효율 | 부하가 낮아 cycling 손실이 등급을 깎을 수 있다. | AHRI 210/240-2026 Case I path |
| 중간 난방 bin | 중간속 효율과 smooth capacity transition | Case II에서 COP 보간 경로가 중요하다. | AHRI 210/240-2026 Equation 11.199~11.204 |
| 저온 난방 bin | full-speed 용량과 보조열 억제 | 부하가 용량을 넘으면 보조열이 증가한다. | AHRI 210/240-2026 Case III path |
| frost 조건 근처 | 제상과 frost 성능 유지 | 35°F 주변 성능은 저온 slope와 중간속 판단에 영향을 준다. | AHRI 210/240-2026 Equation 11.44, Equation 11.50 |

## 8. Part-load Strategy

부분부하 전략은 HSPF2와 SEER2 모두에서 핵심이다. 난방에서는 부하가 저속 용량보다 작을 때 cycling 손실이 생기고, 냉방에서는 저속과 중간속의 효율이 seasonal energy를 좌우한다. 근거: AHRI 210/240-2026 Case I path, AHRI 210/240 cooling rating sections.

| 전략 | 기대 효과 | 주의점 |
| --- | --- | --- |
| 최소 안정 운전 용량을 낮춘다. | low-load bin에서 cycling을 줄인다. | 너무 낮은 운전은 오일 회수와 냉매 분배 안정성을 해칠 수 있다. |
| 중간속 운전점을 효율 좋은 위치에 둔다. | Case II 구간의 COP를 높인다. | 용량은 low와 full 사이에 물리적으로 놓여야 한다. |
| full-speed 저온 용량을 확보한다. | 보조열 투입을 줄인다. | 전력 증가가 용량 증가보다 크면 효율 개선이 제한된다. |
| 냉방 저속 팬 전력을 낮춘다. | SEER2 저부하 에너지를 낮춘다. | 열교환 성능 저하와 실내 쾌적성을 함께 봐야 한다. |

## 9. Standby / Off-mode Power Strategy

현재 HSPF2 중심 문서에서는 보조열과 압축기 에너지의 영향이 더 크지만, 냉방 SEER2와 전체 제품 등급에서는 비활성 모드 전력도 무시할 수 없다. AHRI 210/240 계열의 seasonal rating은 운전하지 않는 시간의 전력도 별도 항목으로 다룰 수 있으므로, 제어 보드와 히터 대기 소비전력을 낮추는 것이 장기적으로 유리하다.

| 항목 | 설계 방향 | 왜 중요한가 |
| --- | --- | --- |
| 제어 보드 대기전력 | 센서와 통신 회로의 저전력 상태를 명확히 둔다. | 작은 전력도 계절 시간과 곱해진다. |
| 크랭크케이스 히터 | 필요한 조건에서만 작동하게 한다. | 냉매 보호와 에너지 절감의 균형이 필요하다. |
| 저온 대기 제어 | 재가동 안정성과 대기전력을 함께 최적화한다. | 저온 보호 로직이 과도하면 seasonal energy가 증가한다. |

## 10. Heating-specific Strategy

HSPF2 설계에서 가장 중요한 질문은 "Region IV 부하선 위에서 제품이 어느 bin까지 압축식 난방만으로 부하를 감당하는가"이다. 부하가 full-speed 용량을 넘는 bin에서는 보조열이 들어가며, 이는 HSPF2를 빠르게 낮춘다. 근거: AHRI 210/240-2026 Equation 11.104, Case III path.

| 설계 항목 | 등급 영향 | 설계 방향 | 근거 |
| --- | --- | --- | --- |
| H01/H11 저속 성능 | 온화한 bin의 cycling 손실을 좌우한다. | 저속 용량을 낮추면서 COP를 유지한다. | AHRI 210/240-2026 Equation 11.187~11.188 |
| H2Int 중간속 성능 | Case II 효율 보간의 중심이 된다. | 중간속 전력 증가를 억제하고 용량 위치를 안정화한다. | AHRI 210/240-2026 Equation 11.199~11.204 |
| H32 저온 full 성능 | 17°F 근처와 저온 line의 기준이 된다. | 저온 난방 용량을 확보하되 전력 증가를 제한한다. | AHRI 210/240-2026 Equation 11.213~11.218 |
| H42 optional 저온점 | 5°F 근처 저온 extrapolation 신뢰도를 높인다. | 저온 지역 판매 제품은 실측 anchor 확보가 유리하다. | AHRI 210/240-2026 Equation 11.215~11.218 |
| Demand defrost | frost 조건 에너지 손실을 줄인다. | 필요 제상만 수행하고 회복 운전을 짧게 한다. | AHRI 210/240-2026 Equation 11.107 |

## 11. Cooling-specific Strategy

SEER2는 현재 확인 가능한 범위에서 A full, B full, B low, E intermediate, F low 점을 기반으로 냉방 bin별 용량과 효율을 평가한다. 냉방 제품 설계에서는 full-load 효율뿐 아니라 low/intermediate 운전의 전력과 효율이 중요하다.

| 설계 항목 | 등급 영향 | 설계 방향 | 근거 |
| --- | --- | --- | --- |
| B low 효율 | 낮은 cooling load에서 seasonal energy를 낮춘다. | 저속 압축기와 팬 전력을 낮게 유지한다. | AHRI 210/240 cooling rating sections |
| E intermediate 효율 | 중간 cooling load에서 보간 효율을 좌우한다. | 중간속 운전점을 low/full envelope 안에서 효율 좋게 둔다. | AHRI 210/240 cooling rating sections |
| A/B full 효율 | 높은 외기온과 high-load 구간을 담당한다. | 고온 응축 조건에서 전력 상승을 억제한다. | AHRI 210/240 cooling rating sections |
| fan power | 모든 냉방 운전점의 소비전력에 반영된다. | 열교환 이득과 팬 전력 증가의 균형을 맞춘다. | AHRI 210/240 cooling rating sections |

## 11.1 Appendix M Design Implications

### M SEER

- A2/B2는 full-capacity curve의 기준이고 F1/B1은 low-capacity curve의 기준이다. EV는 두 curve 사이의 intermediate 위치를 정하므로, 한 정격점의 EER만 올리는 것보다 curve 전 구간의 용량·전력 연속성이 중요하다.
- M cooling bins는 Appendix M Table 19를 사용한다. M1 SEER2의 bin weighting이나 A/B/E/F 명칭을 M SEER의 설계 판단에 그대로 적용하지 않는다.

### M HSPF

- H01/H11은 low-speed 난방 성능, H2V는 intermediate COP 위치, H32는 저온 full-speed 성능을 대표한다. H12/H22가 실측되면 해당 full-load 정보를 우선하며, 비어 있으면 M 전용 fallback 해석을 적용한다.
- M HSPF의 minimum DHR과 Region IV Table 20 bin weighting은 M1 HSPF2의 DHR/Region IV 해석과 동일하다고 가정하지 않는다.
- Demand Defrost가 꺼진 제품은 Defrost Test/Max를 성능 입력으로 해석하지 않고 credit 1.0 조건으로 본다. 켜진 제품은 timing과 제상 회복 손실을 함께 평가한다.
- M HSPF에는 현재 H42 저온 anchor를 사용하지 않는다. H42가 필요한 제품 범위를 추가하려면 M HSPF의 point schema와 별도 golden을 먼저 확정해야 한다.

### Cross-metric comparison

M SEER/HSPF와 M1 SEER2/HSPF2의 수치는 standard edition, 시험점, bin table, rounding이 다르므로 제품 간 단순 우열 비교나 변환식의 입력으로 사용하지 않는다. 비교가 필요하면 동일 standard path 안에서 동일한 config와 시험점 조건을 사용한다.

## 12. Practical Design Checklist

| Check | 질문 | 관련 지표 | 근거 |
| --- | --- | --- | --- |
| 저속 난방 | 온화한 Region IV bin에서 cycling 없이 운전 가능한가? | HSPF2 | AHRI 210/240-2026 Case I path |
| 중간속 난방 | 중간속 용량과 전력이 low/full 사이에서 자연스러운가? | HSPF2 | AHRI 210/240-2026 Equation 11.199~11.204 |
| 저온 난방 | 17°F와 5°F 주변에서 보조열 사용을 줄일 수 있는가? | HSPF2 | AHRI 210/240-2026 Case III path |
| 제상 | frost 조건에서 제상 빈도와 회복 손실이 낮은가? | HSPF2 | AHRI 210/240-2026 Equation 11.107 |
| 부하선 대응 | 건물 부하선과 장비 용량선의 교차가 유리한 위치인가? | HSPF2 | AHRI 210/240-2026 Equation 11.104 |
| 저속 냉방 | 낮은 냉방 부하에서 전력이 낮은가? | SEER2 | AHRI 210/240 cooling rating sections |
| 중간속 냉방 | E 조건 주변에서 효율이 좋은가? | SEER2 | AHRI 210/240 cooling rating sections |

## 13. References

| Reference | Usage |
| --- | --- |
| AHRI 210/240-2017 Appendix M, Table 19 | M SEER cooling test points and seasonal bins |
| AHRI 210/240-2017 Appendix M, Table 20 | M HSPF Region IV bin data and design/load basis |
| AHRI 210/240-2017 Addendum 1 | M HSPF defrost and rating interpretation |
| AHRI 210/240-2026 Section 11 | HSPF2 seasonal calculation structure |
| AHRI 210/240-2026 Table 16 | Region IV fractional heating bin hours and load line parameters |
| AHRI 210/240-2026 Equation 11.104 | 난방 건물 부하선 |
| AHRI 210/240-2026 Equation 11.107 | demand defrost factor |
| AHRI 210/240-2026 Equation 11.181~11.186 | H1Full 결정 |
| AHRI 210/240-2026 Equation 11.187~11.194 | low-speed 난방 용량/전력 |
| AHRI 210/240-2026 Equation 11.199~11.204 | intermediate-speed 난방 slope |
| AHRI 210/240-2026 Equation 11.209~11.218 | full-speed 난방 bin 용량/전력 |
| AHRI 210/240 cooling rating sections | 현재 확인 가능한 SEER2 설계 해석 |
