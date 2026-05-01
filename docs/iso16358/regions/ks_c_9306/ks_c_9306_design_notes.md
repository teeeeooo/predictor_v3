# KS C 9306 Design Notes

## 1. Purpose

이 문서는 KS C 9306 기준의 CSPF/HSPF를 제품 설계 관점에서 해석하기 위한 문서이다. KS C 9306은 ISO 16358 계열 계절 효율 구조를 한국 region 조건에 맞게 적용하며, 냉방과 난방 모두 시험점이 계절 성능선의 기준점으로 작용한다. 공통 ISO 계절 효율 개념은 [../../iso16358_design_notes.md](../../iso16358_design_notes.md)를 참조하고, 이 문서는 한국 확장 조건에서 중요한 engineering heuristic만 다룬다.

근거: KS C 9306:2017 Annex E, Table E.2, Table E.4, Table E.5, Equation E.1.4, Equation E.2.20~E.2.40.

엔지니어링 해석: KS C 9306에서 중요한 것은 특정 시험점의 단일 COP/EER가 아니라, 시험점들이 만드는 capacity curve와 power curve가 한국 bin-hour 및 building load와 어떻게 만나는가이다.

---

## 2. Quick Glossary

상세 용어와 수식 기호는 같은 폴더의 `ks_c_9306_glossary.md`와 parent standard의 `iso16358_glossary.md`를 참조한다.

| Term | Physical meaning | Design impact | Glossary reference |
| --- | --- | --- | --- |
| ta | minimum 운전선과 building load line이 만나는 낮은 부하 쪽 기준 온도 | 이 온도 이하에서는 cycling 손실 회피가 핵심이다. | `ks_c_9306_glossary.md` |
| tb | 중간 용량 설계 판단에 쓰는 중간 기준 온도 | half capacity target을 잡을 때 부하와 운전점 간 균형을 보는 기준이다. | `ks_c_9306_glossary.md` |
| tc | half 운전선과 building load line의 관계를 판단하는 목표 온도 | 중간 부하 구간의 소비전력 민감도를 낮추는 설계 목표가 된다. | `ks_c_9306_glossary.md` |
| PLF | part-load에서 cycling 손실을 반영하는 계수 | 최소 용량이 높으면 저부하 bin에서 효율 손실이 커진다. | `ks_c_9306_glossary.md` |
| CD | part-load 손실 강도를 나타내는 계수 | cycling 회피 설계의 중요도를 키운다. | `ks_c_9306_glossary.md` |
| bin hours | 한국 냉방/난방 계절에서 온도별 발생 시간 | 시간이 많은 온도 구간을 설계 타겟으로 우선 검토해야 한다. | `ks_c_9306_glossary.md` |
| 표기 정격 능력 (declared capacity) | 제품 표시 또는 평가 기준이 되는 대표 능력 | building load 기준과 시험점 해석에 영향을 준다. | `ks_c_9306_glossary.md` |
| 최소 운전 | 제품이 안정적으로 낮출 수 있는 낮은 capacity 운전 | 저부하 bin의 cycling loss와 직결된다. | `ks_c_9306_glossary.md` |
| 중간 운전 | 최소와 정격 사이의 대표 part-load 운전 | 계절 bin-hour가 많은 영역의 전력량에 큰 영향을 준다. | `ks_c_9306_glossary.md` |
| 정격 운전 | 표준 조건에서의 대표 운전점 | 기준 성능선의 anchor가 된다. | `ks_c_9306_glossary.md` |
| 최대 운전 | 저온 난방 부족을 막기 위한 high-stage 운전 | auxiliary heat 발생 여부를 좌우한다. | `ks_c_9306_glossary.md` |
| 제상 조건 | 착상 영향을 포함한 난방 시험 조건 | capacity 저하와 power 증가가 동시에 반영된다. | `ks_c_9306_glossary.md` |
| 착상 영역 | 제상 영향이 성능선에 들어가는 외기온 구간 | HSPF에서 중요한 난방 성능 저하 구간이다. | `ks_c_9306_glossary.md` |
| 전열 장치 (auxiliary heat) | heat pump 부족분을 보충하는 보조열 | HSPF denominator에 포함되어 지표를 낮춘다. | `ks_c_9306_glossary.md` |
| 효율 저하 계수 | 단속 운전 손실을 반영하는 계수 | minimum capacity가 부하보다 클 때 영향이 커진다. | `ks_c_9306_glossary.md` |

---

## 3. Metric Structure

| Metric | KS C 9306 design focus | Key test anchors | Reference |
| --- | --- | --- | --- |
| CSPF | 냉방 part-load 효율과 저부하 단속 손실 관리 | 35°C full, 35°C half, 29°C minimum | KS C 9306 Annex E, Table E.2, Equation E.1.1~E.1.6 |
| HSPF | 난방 중온 효율, 제상 조건, 저온 maximum capacity 관리 | 7°C full/half/min, 2°C defrost, -7°C maximum | KS C 9306 Annex E, Table E.4, Table E.5, Equation E.2.1~E.2.7 |

엔지니어링 해석: KS C 9306에서는 시험점 하나가 단일 성능값으로 끝나지 않고, 온도별 성능선과 운전 case를 결정하는 anchor가 된다.

---

## 4. What Actually Drives the Rating

### CSPF

| Driver | Design meaning | Reference |
| --- | --- | --- |
| 35°C full | 고온 냉방 기준 능력과 소비전력의 anchor | KS C 9306 Annex E, Table E.1, Table E.3 |
| 35°C half | 중간부하 냉방 power curve에 큰 영향을 주는 anchor | KS C 9306 Annex E, Table E.1, Equation E.1.18~E.1.26 |
| 29°C minimum | 저부하 냉방 capacity와 cycling 영역을 결정하는 anchor | KS C 9306 Annex E, Table E.1, Table E.3 |
| 냉방 bin-hour | 중간 외기온의 part-load 운전 누적 영향이 큼 | KS C 9306 Table E.2 |

### HSPF

| Driver | Design meaning | Reference |
| --- | --- | --- |
| 7°C full/half/min | 중온 난방 운전 성능선의 기본 anchor | KS C 9306 Annex E, Table E.1, Equation E.2.20~E.2.33 |
| 2°C defrost | 착상 영역의 capacity/power curve에 직접 영향 | KS C 9306 Annex E, Table E.5, Equation E.2.21, E.2.23, E.2.25, E.2.28, E.2.30, E.2.32 |
| -7°C maximum | 저온에서 auxiliary heat 발생을 막는 방어선 | KS C 9306 Annex E, Equation E.2.26, E.2.33 |
| 난방 bin-hour | 0~7°C 주변의 중간부하 효율과 저온 shortage 가능성을 함께 반영 | KS C 9306 Table E.4 |

---

## 5. ta / tb / tc Definition

KS C 9306 설계 검토에서 ta, tb, tc는 시험점 세 개를 단순히 통과시키기 위한 이름이 아니라 building load line과 운전 성능선의 상대 위치를 읽기 위한 engineering heuristic이다.

| Symbol | Design definition | Engineering heuristic |
| --- | --- | --- |
| ta | minimum 운전 능력선이 building load line과 만나는 낮은 부하 쪽 온도 | ta가 한국 bin-hour가 큰 구간보다 높으면 저부하 cycling 손실 가능성이 커진다. |
| tb | ta와 고온 기준점 사이에서 중간 용량 타겟을 검토하는 기준 온도 | half capacity가 tb 부근의 요구 부하를 과도하게 초과하지 않도록 본다. |
| tc | half 운전선이 building load line과 만나는 설계 판단 온도 | tc를 bin-hour가 의미 있는 구간에 맞추면 중간 부하 소비전력을 안정화하기 쉽다. |

이 세 온도는 모든 제품 조건을 한 번에 결정하는 해답을 의미하지 않는다. 시험점과 한국 bin-hour 구조 안에서 설계자가 빠르게 방향을 잡기 위한 engineering heuristic이다.

---

## 6. Three-point Power Interpolation Insight

KS 구조는 full, half, minimum 세 운전 영역의 전력 특성을 함께 보게 만든다. 전력 보간은 단순히 시험점 소비전력을 평균내는 문제가 아니라, building load line이 어느 운전선 사이를 지나가는지에 따라 계절 누적 전력에 다른 압력을 준다.

엔지니어링 해석: full 효율만 개선하면 고온 bin에는 도움이 되지만, 중간온도 bin에서 half 또는 minimum 운전선의 소비전력이 높으면 CSPF 개선이 제한된다. 따라서 세 운전점의 전력 곡선 기울기를 함께 관리해야 한다.

### 6.1 Midpoint Placement of tc and Energy Minimization

KS C 9306의 3점식 전력 보간 구조는 계절 소비전력을 단순 평균이 아니라 구간별 선형 보간으로 계산하도록 설계되어 있다.

설계 관점에서 중요한 특징은 다음과 같다.

- building load가 minimum과 half capacity 사이에 있을 때, 소비전력은 $t_a$와 $t_c$ 사이에서 선형 보간된다.
- building load가 half와 full capacity 사이에 있을 때, 소비전력은 $t_c$와 $t_b$ 사이에서 선형 보간된다.

즉, 계절 소비전력 곡선은 $t_a \rightarrow t_c \rightarrow t_b$를 연결하는 두 개의 직선으로 구성된다.

이 구조에서 $t_c$의 위치는 전체 소비전력 적분값(annual energy)에 직접적인 영향을 준다.

엔지니어링 해석:

- $t_c$가 $t_a$에 가까우면, $t_c \rightarrow t_b$ 구간의 기울기가 커지고 중간~고부하 영역의 소비전력이 증가한다.
- $t_c$가 $t_b$에 가까우면, $t_a \rightarrow t_c$ 구간의 기울기가 커지고 저~중부하 영역의 소비전력이 증가한다.

따라서 두 구간의 전력 증가를 균형화하는 위치는 자연스럽게 두 기준점의 중간이 된다.

이로부터 다음과 같은 설계 인사이트를 얻을 수 있다:

$$t_c \approx \frac{t_a + t_b}{2}$$

이 조건은 KS C 9306의 선형 보간 구조에서 각 구간의 기울기 불균형을 최소화하여, 결과적으로 계절 누적 소비전력을 낮추는 방향으로 작용한다.

> **중요:** 이 관계는 모든 시스템에서 전역 최적을 보장하는 수학적 해가 아니라, KS C 9306의 3점식 전력 보간 구조 하에서 **소비전력 분포를 균형화하는 engineering heuristic**으로 해석해야 한다.
>
> 실제 설계에서는 bin-hour 분포, PLF / CD 손실, 압축기 운전 범위, 고온 영역 capacity 확보를 함께 고려해야 한다.

---

## 7. tc Targeting Strategy

tc 타겟팅은 half 운전 능력이 한국 냉방 bin-hour의 주요 온도 구간에서 building load와 과도하게 떨어지지 않도록 맞추는 전략이다.

| Design check | Intended effect |
| --- | --- |
| tc가 장시간 bin 근처에 있는지 확인한다. | 중간 부하에서 불필요한 cycling 또는 과대 운전을 줄인다. |
| half capacity가 building load를 지나치게 초과하지 않는지 본다. | PLF 손실 가능성을 낮춘다. |
| half power가 full과 minimum 사이에서 완만하게 이어지는지 본다. | 3점식 전력 보간에서 계절 전력 증가를 줄인다. |
| tc만 맞추고 고온 능력을 희생하지 않는지 확인한다. | 최고온 bin의 cooling output cap을 방지한다. |

tc는 단독 설계 기준이 아니다. 실제 제품에서는 압축기 운전 범위, 열교환기 면적, 팬 효율, 소음 제한, 제어 안정성을 함께 고려하는 engineering heuristic으로 사용해야 한다.

---

## 8. High Impact Design Parameters

| Parameter | CSPF impact | HSPF impact |
| --- | --- | --- |
| Compressor minimum Hz | 저부하 냉방 cycling loss 감소 | 저부하 난방 cycling loss 감소 |
| Compressor intermediate efficiency | 35°C half, 중간부하 power 개선 | 7°C half, 중온 난방 power 개선 |
| Outdoor heat exchanger margin | 고온 냉방 power 감소 | 저온 난방 capacity 유지 |
| Indoor heat exchanger margin | 실내측 접근온도 개선 | 난방 토출 안정성과 capacity 유지 |
| Fan power | 모든 계절 전력량에 직접 누적 | 제상/저온 운전에서 상대 영향 증가 가능 |
| Refrigerant charge optimization | part-load와 고온/저온 성능 균형 | 제상 전후 안정성과 저온 capacity에 영향 |
| Defrost control | 직접 영향 적음 | 2°C defrost 성능과 HSPF에 직접 영향 |

---

## 9. Low Impact / Misleading Design Parameters

| Misleading focus | Risk | Better interpretation |
| --- | --- | --- |
| 35°C full만 개선 | CSPF가 half/min 구간에서 제한될 수 있다. | bin-hour가 큰 half/minimum 구간도 함께 본다. |
| 7°C full만 개선 | HSPF가 defrost 또는 -7°C maximum에서 제한될 수 있다. | 2°C defrost와 -7°C maximum을 함께 확인한다. |
| -7°C maximum capacity만 키우기 | auxiliary는 줄 수 있지만 maximum power 증가로 이득이 줄어들 수 있다. | maximum power 증가와 auxiliary 감소의 trade-off를 본다. |
| minimum capacity를 무조건 낮추기 | 낮은 capacity에서 COP가 나쁘면 계절 전력량이 줄지 않을 수 있다. | minimum 운전 효율도 함께 확인한다. |
| defrost capacity만 보기 | defrost power 증가가 크면 HSPF 개선이 제한된다. | defrost power 억제도 함께 본다. |

---

## 10. PLF / CD Loss Avoidance

PLF 손실은 요구 부하가 장비 최소 운전 능력보다 낮을 때 발생한다. 한국 bin-hour에서 낮은 냉방 부하 구간의 시간이 누적되면 작은 cycling 손실도 CSPF를 눈에 띄게 낮출 수 있다.

| Loss driver | Design response |
| --- | --- |
| minimum capacity가 너무 높음 | 최소 안정 운전 능력을 낮추고 저속 운전 안정성을 확보한다. |
| 저부하 fan power가 높음 | 낮은 풍량에서도 열교환 효율과 소비전력 균형을 맞춘다. |
| compressor cycling이 잦음 | 제어 deadband와 최소 운전 시간을 계절 효율 관점에서 조정한다. |
| half step이 building load보다 과도하게 높음 | half capacity target을 장시간 bin 부하 근처로 조정한다. |

---

## 11. Seasonal Bin Strategy

KS C 9306의 난방 bin은 -15°C부터 15°C까지 분포하며, 저온과 중온 영역이 함께 반영된다. 한국 냉방 bin-hour는 설계 타겟 온도를 정하는 가중치 역할을 한다. 시간이 많은 온도 구간은 작은 전력 개선도 annual power를 크게 줄일 수 있다.

| Temperature region | CSPF design focus | HSPF design focus |
| --- | --- | --- |
| 낮은 부하 bin | minimum capacity와 PLF 손실 회피 | minimum capacity와 cycling loss 관리 |
| 중간 부하 bin | half capacity target과 소비전력 곡선 | intermediate/rated power 감소 |
| 높은 부하 bin | full capacity 유지와 output cap 방지 | — |
| 착상 영역 | — | defrost capacity 유지, defrost power 억제 |
| 저온 영역 | — | maximum capacity, auxiliary heat, maximum power trade-off |

엔지니어링 해석: 35°C full point는 반드시 확보해야 하지만, 계절 효율 개선의 우선순위는 bin-hour가 큰 중간온도 구간에서 half/minimum 운전이 얼마나 부하를 잘 따라가는지에 있다. 한국 HSPF에서는 저온 maximum만 보는 접근보다, 착상 영역과 중온 영역의 소비전력 누적을 함께 보는 접근이 더 안전하다.

---

## 12. Part-load Strategy

KS C 9306에서 part-load 성능은 최소, 중간, 정격 운전점 사이의 관계로 결정된다. 좋은 설계는 단순히 maximum capacity를 크게 만드는 것이 아니라, minimum–intermediate–rated 운전점이 building load를 자연스럽게 따라가도록 만드는 것이다.

| Design check | Interpretation |
| --- | --- |
| minimum과 intermediate 간격이 너무 큰가? | 저부하에서 power interpolation이 불리할 수 있다. |
| intermediate와 rated 간격이 너무 큰가? | 중간부하 영역의 power가 과대 산정될 수 있다. |
| minimum power가 충분히 낮은가? | cycling 영역과 저부하 bin에 직접 영향 |
| intermediate power가 낮은가? | 계절 전력량 절감 효과가 큼 |

---

## 13. Standby / Off-mode Power Strategy

KS C 9306의 계절 효율 해석에서 standby 또는 off-mode 항목은 적용 조항과 시험 범위에 따라 별도로 확인해야 한다. 제품 설계 관점에서는 제어 보드, 센서, 통신 모듈의 상시 소비전력이 계절 소비전력에 포함되는 구조인지 확인해야 한다.

| Design issue | Design interpretation |
| --- | --- |
| 제어 보드 상시 소비전력 | 운전 효율 개선과 별도로 계절 전력량을 증가시킬 수 있다. |
| 통신/대기 기능 추가 | 편의 기능이 계절 지표에 미치는 영향을 시험 범위 기준으로 확인해야 한다. |
| 지역별 반영 방식 | parent standard 또는 region 조항에서 포함 여부를 확인해야 한다. |

---

## 14. Heating-specific Strategy

KS HSPF에서는 저온 능력 부족과 제상 영향이 핵심이다. 냉방에서는 capacity excess와 part-load penalty가 주요 손실원이지만, 난방에서는 defrost penalty와 저온 capacity shortage가 동일하게 중요하다.

| Test condition | Design interpretation | Reference |
| --- | --- | --- |
| 7°C full/half/min | 일반 난방 성능선의 기본 형태를 결정한다. | KS C 9306 Annex E, Equation E.2.20~E.2.33 |
| 2°C defrost | 착상 영역에서 capacity 하락과 power 증가를 동시에 반영한다. 단일 시험점처럼 보이지만 착상 영역 성능선 전체에 영향을 주는 핵심 anchor이다. | KS C 9306 Annex E, Table E.5 |
| -7°C maximum | 저온에서 auxiliary heat 발생을 막는 기준점이다. | KS C 9306 Annex E, Equation E.2.26, E.2.33 |

| Design focus | Heating-specific meaning | Design impact |
| --- | --- | --- |
| frost region | 착상 영역에서는 능력과 소비전력 곡선이 무착상 영역과 분리된다. | 2°C 근처 실측 제상 성능을 과소평가하거나 이중 보정하지 않도록 stage별 defrost 성능을 확인해야 한다. |
| maximum capacity | 저온 bin에서 building load가 최대 운전 능력을 넘으면 부족분은 보조열로 채워진다. | 최대 운전 저온 능력이 부족하면 HSPF denominator가 빠르게 증가한다. |
| minimum capacity | 온화한 난방 bin에서 building load가 최소 운전 능력보다 낮으면 cycling 손실이 발생한다. | 최소 안정 운전 능력을 낮추면 저부하 난방 bin의 효율 손실을 줄일 수 있다. |
| intermediate capacity | 최소, 중간, 정격 운전선 사이의 전력 보간이 계절 소비전력을 만든다. | 중간 운전 성능선은 저부하와 고부하 양쪽을 부드럽게 연결하도록 배치해야 한다. |
| auxiliary heat | heat pump가 감당하지 못한 난방 부하는 계절 소비전력에 직접 합산된다. | capacity shortage와 auxiliary heat는 성능 설계에서 같은 사건으로 추적해야 한다. |

엔지니어링 해석: 한국 난방 bin-hour에서 시간이 많은 온도대의 중간 운전 효율을 확보하면서, 저온부 최대 운전 능력이 auxiliary heat를 과도하게 부르지 않는 균형점을 잡아야 한다.

---

## 15. Cooling-specific Strategy

KS CSPF에서 중요한 것은 35°C full, 35°C half, 29°C minimum의 균형이다.

| Test condition | Design interpretation | Reference |
| --- | --- | --- |
| 35°C full | 고온 냉방 능력과 power 기준점 | KS C 9306 Annex E, Table E.1, Table E.3 |
| 35°C half | 중간부하 계절 효율에 민감한 지점 | KS C 9306 Annex E, Equation E.1.18~E.1.26 |
| 29°C minimum | 저부하 cycling 및 minimum power에 민감한 지점 | KS C 9306 Annex E, Table E.3 |

엔지니어링 해석: 29°C minimum capacity가 너무 높으면 저부하 bin에서 단속 운전 손실이 커질 수 있다. 반대로 minimum 운전 COP가 낮으면 capacity를 낮춘 이득이 power 증가로 상쇄될 수 있다.

---

## 16. Practical Design Checklist

### CSPF checklist

| Check item | Design question | Reference |
| --- | --- | --- |
| declared capacity로 만든 building load line을 먼저 그린다. | 한국 계산은 표시 능력이 계절 부하 기준을 만든다. | KS C 9306 Equation E.1.4 |
| ta가 장시간 bin보다 높은지 확인한다. | 저부하 cycling 손실 가능성을 판단한다. | KS C 9306 Table E.2 |
| tc가 주요 중간 bin 근처에 있는지 확인한다. | half 운전 타겟이 계절 가중치와 맞는지 본다. | KS C 9306 Table E.2 |
| 35°C half power | 중간부하 영역에서 소비전력이 과도하지 않은가? | KS C 9306 Equation E.1.18~E.1.26 |
| 29°C minimum capacity | 저부하 bin에서 cycling을 유발하지 않는가? | KS C 9306 Table E.3 |
| 29°C minimum power | 낮은 capacity에서 효율이 충분히 좋은가? | KS C 9306 Table E.3 |
| 35°C full capacity | 고온 부하를 처리할 수 있는가? | KS C 9306 Equation E.1.4 |
| half power가 minimum과 full 사이에서 급격히 튀지 않는지 확인한다. | 3점식 전력 보간의 annual power 증가를 줄인다. | KS C 9306 Equation E.1.18~E.1.26 |
| fan power | capacity 개선 대비 fan power 증가가 과도하지 않은가? | KS C 9306 Equation E.1.1~E.1.3 |

### HSPF checklist

| Check item | Design question | Reference |
| --- | --- | --- |
| 7°C half power | 중온 난방 bin에서 전력량을 줄일 수 있는가? | KS C 9306 Equation E.2.31~E.2.32 |
| 7°C minimum capacity | 저부하 난방에서 cycling을 줄이는가? | KS C 9306 Equation E.2.20~E.2.21 |
| 2°C defrost capacity | 착상 영역에서 capacity 하락이 과도하지 않은가? | KS C 9306 Table E.5 |
| 2°C defrost power | 제상 조건 power 증가가 과도하지 않은가? | KS C 9306 Table E.5 |
| -7°C maximum capacity | auxiliary heat를 막을 만큼 충분한가? | KS C 9306 Equation E.2.26 |
| -7°C maximum power | auxiliary 감소 이득보다 power 증가 손해가 크지 않은가? | KS C 9306 Equation E.2.33 |

---

## 17. References

| Source | Usage |
| --- | --- |
| KS C 9306:2017 Annex E | 한국 CSPF/HSPF 계절 효율 구조 |
| KS C 9306:2017 Table E.2 | 한국 냉방 bin-hour 기반 설계 타겟 |
| KS C 9306:2017 Table E.4 | 한국 난방 bin-hour 기반 설계 타겟 |
| KS C 9306:2017 Table E.5 | 난방 보정 계수 및 효율 저하 계수 |
| KS C 9306:2017 Equation E.1.1~E.1.6 | CSPF 계절 합산, building load, PLF |
| KS C 9306:2017 Equation E.1.4 | declared capacity 기반 building load |
| KS C 9306:2017 Equation E.2.1~E.2.7 | HSPF 계절 합산, building load, PLF, auxiliary heat |
| KS C 9306:2017 Equation E.2.20~E.2.40 | 가변 용량형 난방 성능선과 운전 case |
| [../../iso16358_design_notes.md](../../iso16358_design_notes.md) | ISO 공통 seasonal design insight |
