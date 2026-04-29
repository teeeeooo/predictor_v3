# KS C 9306 Design Notes

## 1. Purpose

이 문서는 KS C 9306의 한국 냉방 CSPF 구조가 제품 설계에 주는 방향성을 설명한다. 공통 ISO 계절 효율 개념은 [../../iso16358_design_notes.md](../../iso16358_design_notes.md)를 참조하고, 이 문서는 한국 확장 조건에서 중요한 engineering heuristic만 다룬다.

근거: KS C 9306:2017 Annex E, Table E.2, Equation E.1.4.

## 2. Quick Glossary

상세 용어와 데이터 매핑은 [ks_c_9306_glossary.md](./ks_c_9306_glossary.md)를 참조한다.

| Term | Physical meaning | Design impact | Glossary reference |
| --- | --- | --- | --- |
| ta | minimum 운전선과 building load line이 만나는 낮은 부하 쪽 기준 온도 | 이 온도 이하에서는 cycling 손실 회피가 핵심이다. | [ks_c_9306_glossary.md](./ks_c_9306_glossary.md) |
| tb | 중간 용량 설계 판단에 쓰는 중간 기준 온도 | half capacity target을 잡을 때 부하와 운전점 간 균형을 보는 기준이다. | [ks_c_9306_glossary.md](./ks_c_9306_glossary.md) |
| tc | half 운전선과 building load line의 관계를 판단하는 목표 온도 | 중간 부하 구간의 소비전력 민감도를 낮추는 설계 목표가 된다. | [ks_c_9306_glossary.md](./ks_c_9306_glossary.md) |
| PLF | part-load에서 cycling 손실을 반영하는 계수 | 최소 용량이 높으면 저부하 bin에서 효율 손실이 커진다. | [ks_c_9306_glossary.md](./ks_c_9306_glossary.md) |
| CD | part-load 손실 강도를 나타내는 계수 | cycling 회피 설계의 중요도를 키운다. | [ks_c_9306_glossary.md](./ks_c_9306_glossary.md) |
| bin hours | 한국 냉방 계절에서 온도별 발생 시간 | 시간이 많은 온도 구간을 설계 타겟으로 우선 검토해야 한다. | [ks_c_9306_glossary.md](./ks_c_9306_glossary.md) |
| declared capacity load | 표기 정격 능력 기반 부하선 | 시험 full capacity가 아니라 표시 능력이 계절 부하 기준을 만든다. | [ks_c_9306_glossary.md](./ks_c_9306_glossary.md) |

## 3. ta / tb / tc Definition

KS C 9306 설계 검토에서 ta, tb, tc는 시험점 세 개를 단순히 통과시키기 위한 이름이 아니라 building load line과 운전 성능선의 상대 위치를 읽기 위한 engineering heuristic이다.

| Symbol | Design definition | Engineering heuristic |
| --- | --- | --- |
| ta | minimum 운전 능력선이 building load line과 만나는 낮은 부하 쪽 온도 | ta가 한국 bin-hour가 큰 구간보다 높으면 저부하 cycling 손실 가능성이 커진다. |
| tb | ta와 고온 기준점 사이에서 중간 용량 타겟을 검토하는 기준 온도 | half capacity가 tb 부근의 요구 부하를 과도하게 초과하지 않도록 본다. |
| tc | half 운전선이 building load line과 만나는 설계 판단 온도 | tc를 bin-hour가 의미 있는 구간에 맞추면 중간 부하 소비전력을 안정화하기 쉽다. |

이 세 온도는 모든 제품 조건을 한 번에 결정하는 해답을 의미하지 않는다. 시험점과 한국 bin-hour 구조 안에서 설계자가 빠르게 방향을 잡기 위한 engineering heuristic이다.

## 4. Three-point Power Interpolation Insight

KS 구조는 full, half, minimum 세 운전 영역의 전력 특성을 함께 보게 만든다. 전력 보간은 단순히 시험점 소비전력을 평균내는 문제가 아니라, building load line이 어느 운전선 사이를 지나가는지에 따라 계절 누적 전력에 다른 압력을 준다.

엔지니어링 해석: full 효율만 개선하면 고온 bin에는 도움이 되지만, 중간온도 bin에서 half 또는 minimum 운전선의 소비전력이 높으면 CSPF 개선이 제한된다. 따라서 세 운전점의 전력 곡선 기울기를 함께 관리해야 한다.

## 4.1 Midpoint Placement of tc and Energy Minimization

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

\[
t_c \approx \frac{t_a + t_b}{2}
\]

이 조건은 KS C 9306의 선형 보간 구조에서 각 구간의 기울기 불균형을 최소화하여, 결과적으로 계절 누적 소비전력을 낮추는 방향으로 작용한다.

중요:

이 관계는 모든 시스템에서 전역 최적을 보장하는 수학적 해가 아니라,  
KS C 9306의 3점식 전력 보간 구조 하에서 **소비전력 분포를 균형화하는 engineering heuristic**으로 해석해야 한다.

실제 설계에서는 다음 요소와 함께 고려해야 한다:

- bin-hour 분포
- PLF / CD 손실
- 압축기 운전 범위
- 고온 영역 capacity 확보

## 5. tc Targeting Strategy

tc 타겟팅은 half 운전 능력이 한국 냉방 bin-hour의 주요 온도 구간에서 building load와 과도하게 떨어지지 않도록 맞추는 전략이다.

| Design check | Intended effect |
| --- | --- |
| tc가 장시간 bin 근처에 있는지 확인한다. | 중간 부하에서 불필요한 cycling 또는 과대 운전을 줄인다. |
| half capacity가 building load를 지나치게 초과하지 않는지 본다. | PLF 손실 가능성을 낮춘다. |
| half power가 full과 minimum 사이에서 완만하게 이어지는지 본다. | 3점식 전력 보간에서 계절 전력 증가를 줄인다. |
| tc만 맞추고 고온 능력을 희생하지 않는지 확인한다. | 최고온 bin의 cooling output cap을 방지한다. |

tc는 단독 설계 기준이 아니다. 실제 제품에서는 압축기 운전 범위, 열교환기 면적, 팬 효율, 소음 제한, 제어 안정성을 함께 고려하는 engineering heuristic으로 사용해야 한다.

## 6. PLF / CD Loss Avoidance

PLF 손실은 요구 부하가 장비 최소 운전 능력보다 낮을 때 발생한다. 한국 bin-hour에서 낮은 냉방 부하 구간의 시간이 누적되면 작은 cycling 손실도 CSPF를 눈에 띄게 낮출 수 있다.

| Loss driver | Design response |
| --- | --- |
| minimum capacity가 너무 높음 | 최소 안정 운전 능력을 낮추고 저속 운전 안정성을 확보한다. |
| 저부하 fan power가 높음 | 낮은 풍량에서도 열교환 효율과 소비전력 균형을 맞춘다. |
| compressor cycling이 잦음 | 제어 deadband와 최소 운전 시간을 계절 효율 관점에서 조정한다. |
| half step이 building load보다 과도하게 높음 | half capacity target을 장시간 bin 부하 근처로 조정한다. |

## 7. Bin Hours and Design Target Relationship

한국 냉방 bin-hour는 설계 타겟 온도를 정하는 가중치 역할을 한다. 시간이 많은 온도 구간은 작은 전력 개선도 annual power를 크게 줄일 수 있다.

엔지니어링 해석: 35°C full point는 반드시 확보해야 하지만, 계절 효율 개선의 우선순위는 bin-hour가 큰 중간온도 구간에서 half/minimum 운전이 얼마나 부하를 잘 따라가는지에 있다.

| Temperature region | Design focus |
| --- | --- |
| 낮은 냉방 부하 bin | minimum capacity와 PLF 손실 회피 |
| 중간 냉방 부하 bin | half capacity target과 소비전력 곡선 |
| 높은 냉방 부하 bin | full capacity 유지와 output cap 방지 |

## 8. Practical Design Checklist

| Check | Why it matters |
| --- | --- |
| declared capacity로 만든 building load line을 먼저 그린다. | 한국 계산은 표시 능력이 계절 부하 기준을 만든다. |
| ta가 장시간 bin보다 높은지 확인한다. | 저부하 cycling 손실 가능성을 판단한다. |
| tc가 주요 중간 bin 근처에 있는지 확인한다. | half 운전 타겟이 계절 가중치와 맞는지 본다. |
| half power가 minimum과 full 사이에서 급격히 튀지 않는지 확인한다. | 3점식 전력 보간의 annual power 증가를 줄인다. |
| 고온 bin에서 full capacity가 building load를 따라가는지 확인한다. | cooling output cap으로 인한 계절 냉방량 손실을 막는다. |

## 9. References

| Source | Usage |
| --- | --- |
| KS C 9306:2017 Annex E | 한국 CSPF 계산 구조 |
| KS C 9306:2017 Table E.2 | 한국 냉방 bin-hour 기반 설계 타겟 |
| KS C 9306:2017 Equation E.1.4 | declared capacity 기반 building load |
| [../../iso16358_design_notes.md](../../iso16358_design_notes.md) | ISO 공통 seasonal design insight |
