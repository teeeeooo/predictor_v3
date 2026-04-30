# KS C 9306 Region Design Notes

## 1. Purpose
이 문서는 KS C 9306 기준의 CSPF/HSPF를 한국 시장 제품 설계 관점에서 해석하기 위한 문서이다. ISO 16358의 구조를 따르되, 한국의 기후 데이터(31-bin)와 고유한 평가 시험점(Anchor points)의 영향을 분석한다.

## 2. Quick Glossary
| Term | Physical Meaning | Design Impact |
| :--- | :--- | :--- |
| **표기 정격 능력** | 제품 스펙상의 대표 능력 | 한국 규격의 부하선(BL) 앵커를 결정하는 기준값이다. |
| **최소 운전 (29_min)** | 29°C에서 기기가 낼 수 있는 최저 능력 | 저부하 Bin의 단속 운전(Cycling) 개시 시점을 결정한다. |
| **중간 운전 (35_half)** | 정격의 약 50% 수준 부하 운전 | 가장 비중이 큰 중간 외기온 영역의 전력량을 지배한다. |
| **제상 조건 (2_defrost)** | 2°C, 다습 조건에서의 난방 시험 | 착상 영역(Frost Region) 성능 곡선의 실질적 앵커이다. |
| **최대 운전 (-7_max)** | -7°C 극한 저온에서의 최대 출력 | 한국 겨울철 영하 구간의 보조열 발생 차단선이다. |

## 3. Metric Structure & Key Test Anchors
KS C 9306에서는 특정 시험점 결과가 단순한 성적표가 아니라, 전체 기후 구간의 성능 곡선을 그리는 **앵커(Anchor)**로 작용한다.

* **CSPF Anchors:** 35°C Full (고온), 35°C Half (중온), 29°C Min (저부하)
* **HSPF Anchors:** 7°C Full/Half/Min (기본), 2°C Defrost (착상), -7°C Max (한한기)

## 4. What Actually Drives the Rating (Korea Specific)
### CSPF
* **29°C Minimum Point:** 한국 CSPF는 저부하 bin 비중이 높다. 29_min 능력을 충분히 낮추지 못하면 단속 운전 패널티($C_d$)를 세게 맞는다.
* **35°C Half Point:** 실측된 중간 소비전력이 계절 전체 소비전력의 기저(Baseline)를 형성한다.

### HSPF
* **31-bin ( -15 ~ 15°C):** 한국은 영하 구간 빈 시간이 매우 길다(2849시간 중 상당수). 단순히 7°C 성능만 좋아서는 등급 달성이 불가능하다.
* **Building Load Anchor:** * **설계 현실:** 규격 원문은 냉방 능력을 요구하나, 본 프로젝트는 공식 인증 시트와의 결괏값 일치를 위해 **'난방 정격 능력'**에 0.82를 곱하는 방식을 채택한다.
    * **설계 시사점:** 난방 용량을 과도하게 키우면 기기가 감당해야 할 가상의 건물 부하선도 함께 가팔라지므로, 용량 설계와 부하 대응력의 균형이 필요하다.

## 5. High Impact Design Parameters (KS Specific)
| Parameter | CSPF Impact | HSPF Impact |
| :--- | :--- | :--- |
| **Comp. Minimum Hz** | 저부하 냉방 Cycling Loss 감소 | 저온 난방 시 저부하 구간 효율 개선 |
| **2°C Defrost 성능** | 직접 영향 없음 | 착상 영역 전체의 성능선(Slope)을 결정 |
| **-7°C Max Capacity** | 직접 영향 없음 | 영하 구간 보조열(Auxiliary) 투입 억제 |
| **Fan Power** | 모든 Bin에 누적 (중요) | 제상 및 저온 고속 운전 시 비중 증가 |

## 6. Low Impact / Misleading Focus
* **35°C 정격(Full) EER만 극대화:** 35°C 고온 Bin은 시간이 짧아 전체 CSPF 기여도가 낮다. 정격을 희생하더라도 중간부하(Half)를 잡는 것이 유리하다.
* **-7°C 능력만 무한정 키우기:** 용량 부족은 해결되나, 소비전력(Max Power)이 과도하게 증가하면 보조열 절감 이득이 상쇄되어 HSPF가 오히려 떨어질 수 있다.

## 7. Practical Design Checklist (Korea)
1.  **[CSPF]** 29°C 실측 시 최소 능력(Min Capacity)이 건물 부하(BL)보다 낮게 내려가는가? (Cycling 방지 확인)
2.  **[HSPF]** -15°C~-7°C 구간에서 보조열 투입량이 전체 HSEC의 5%를 초과하는가? (초과 시 저온 성능 보강 필요)
3.  **[HSPF]** 2°C 제상 성능이 7°C 대비 89%(능력), 94%(소비전력) 수준을 유지하는가? (KS 기본 보정치와의 편차 확인)

## 8. References
* KS C 9306:2017 Annex E (에어컨디셔너의 계절 성적 계수 산출 방법)
* 프로젝트 필드 실무 지침: 난방 부하선 앵커 산정 시 난방 정격 표준 능력 활용.
