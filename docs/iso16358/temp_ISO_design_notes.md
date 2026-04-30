# ISO 16358 Design Notes

## 1. Purpose
이 문서는 ISO 16358 계열 계절 효율 지표(CSPF, HSPF)를 제품 설계 관점에서 해석하기 위한 지침이다. 단일 정격 운전점의 성능(EER/COP)이 아닌, 전체 계절 기후(Bin-hours)와 건물 부하(Building Load) 조건 하에서의 통합 성능을 최적화하는 것을 목표로 한다.

**엔지니어링 해석:** ISO 16358의 설계 핵심은 "특정 점에서의 초고효율"이 아니라, "실제 운전 시간이 가장 긴 영역에서 부하선과 성능 곡선을 얼마나 일치시키는가"에 있다.

## 2. Quick Glossary
| Term | Physical Meaning | Design Impact |
| :--- | :--- | :--- |
| **Seasonal Performance Factor (SPF)** | 계절 전체 유효 출력량 / 계절 전체 소비전력량 | 단일 성적계수보다 실제 운전 영역의 평균 효율을 더 강하게 반영한다. |
| **Bin-hour** | 특정 외기온도가 계절 중 발생하는 가중 시간 | 운전 시간이 긴 온도 구간에서의 1W 소비전력 차이가 최종 등급을 결정한다. |
| **Building Load (BL)** | 외기온도별로 기기가 처리해야 하는 요구 냉/난방 부하 | 제품 능력선(Capacity)과 부하선의 상대 위치가 운전 케이스(Case)를 결정한다. |
| **Capacity Curve** | 외기온도 및 운전 단계(Hz)별 능력 변화 곡선 | 부하선보다 높으면 단속 손실(Cycling), 낮으면 용량 부족(Shortage)이 발생한다. |
| **Cycling Loss** | 최소 능력이 부하보다 커서 압축기가 On/Off될 때의 손실 | 최소 운전 Hz 하향 능력이 부족하면 저부하 구간 계절 효율이 급락한다. |
| **Auxiliary Heat** | 히트펌프 능력이 부하보다 부족할 때 투입되는 보조 에너지 | COP 1.0으로 취급되므로 HSPF 지표를 무너뜨리는 주범이다. |

## 3. Metric Structure
ISO 16358 지표는 "얼마나 많은 일을 했는가(Numerator)"를 "얼마나 전기를 썼는가(Denominator)"로 나누는 물리적 균형이다.

| Metric | Numerator (일의 양) | Denominator (소비 에너지) | Design Focus |
| :--- | :--- | :--- | :--- |
| **CSPF** | 계절 냉방 처리량 | 냉방 운전 총 전력량 | 중간/저부하 효율 및 단속 손실 관리 |
| **HSPF** | 계절 난방 부하량 | HP 전력량 + 보조열 전력량 | 저온 능력 유지 및 보조열 발생 억제 |

**엔지니어링 해석:** CSPF는 "남는 능력을 얼마나 효율적으로 줄여 쓰는가"가 중요하고, HSPF는 "부족한 능력을 보조열 없이 얼마나 버티는가"가 핵심이다.

## 4. What Actually Drives the Rating
| Driver | CSPF Impact | HSPF Impact |
| :--- | :--- | :--- |
| **Bin-hour Concentration** | 시간이 많은 중온대(27~32°C) 효율이 핵심 | 시간이 많은 중온대(0~7°C) 효율이 핵심 |
| **Minimum Capacity** | 너무 높으면 Cycling loss 가 지표를 깎음 | 저부하 난방 시 단속 운전 패널티 발생 |
| **Maximum Capacity** | 고온 부하 처리 능력을 결정 | 저온(특히 영하)에서 보조열 개입 여부 결정 |
| **Defrost Behavior** | 직접 영향 없음 | 용량 저하와 전력 증가를 동시에 유발하는 변수 |

## 5. High Impact Design Parameters
1.  **Compressor Turndown Range (최소Hz):** 저부하 bin에서의 단속 운전 회피 능력. 최소 운전 Hz를 낮출수록 Cycling Loss가 감소하여 CSPF가 직접적으로 개선된다.
2.  **Intermediate Efficiency (중간부하 효율):** 계절 운전의 70~80%가 머무르는 영역의 효율. 중간 Hz 운전 시의 모터/압축기 효율 최적화가 필수적이다.
3.  **Heat Exchanger Margin:** 응축/증발 온도 접근(Approach) 개선. 같은 능력을 더 낮은 압축비로 달성하여 분모(Power)를 직접 줄인다.
4.  **Defrost Control Logic:** 제상 진입 억제 및 복귀 안정성. 제상 구간에서의 성능 악화는 HSPF 분자를 줄이고 분모를 키우는 이중 손실을 발생시킨다.

## 6. Seasonal Bin Strategy
"가장 힘든 온도 하나를 최적화하는 것이 아니라, 가장 오래 머무는 운전 영역을 최적화하라."
* **특정 온도 Bin-hour가 큰 경우:** 해당 구간의 소비전력 1W 절감이 등급에 미치는 영향력이 누적되어 커진다.
* **극한 온도 Bin-hour가 작은 경우:** 에너지 절감 효과는 작을 수 있으나, 용량 부족으로 인한 보조열(Auxiliary) 투입 여부를 결정하므로 방치해서는 안 된다.

## 7. Practical Design Checklist
### CSPF Checklist
* [ ] 최소 운전 능력이 저부하 Bin(예: 25~28°C) 부하 대비 과도하지 않은가?
* [ ] 중간 운전점(Half)에서의 소비전력이 부하선과 일치하는 영역에서 최적화되었는가?
* [ ] 팬 전력량의 상대적 비중이 저부하 영역에서 효율을 방해하지 않는가?

### HSPF Checklist
* [ ] 저온(-7°C 이하)에서 최대 능력이 건물 부하를 상회하여 보조열을 차단하는가?
* [ ] 제상 조건(2°C 전후)에서 능력 하락이 급격하지 않도록 제어가 안정적인가?
* [ ] 중간 운전점의 효율 개선이 7°C 정격 효율 개선보다 지표 기여도가 높은가?

## 8. References
* ISO 16358-1:2013 (Cooling Seasonal Performance Factor)
* ISO 16358-2:2013 (Heating Seasonal Performance Factor)
