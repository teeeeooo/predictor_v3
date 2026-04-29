# ISO16358 Design Notes

## 1. Purpose

이 문서는 ISO 16358의 seasonal efficiency 구조가 제품 설계 의사결정에 주는 압력을 설명한다. 국가별 보정이나 지역 특이 조건은 다루지 않으며, 공통적인 cooling seasonal performance 관점만 정리한다.

근거: ISO 16358-1:2013 Chapter 5, Chapter 6. UN AC proposal Annex 4는 seasonal calculation이 outdoor temperature bin hours에 의해 가중된다는 점을 보여준다.

## 2. Quick Glossary

상세 용어와 데이터 매핑은 [iso16358_glossary.md](./iso16358_glossary.md)를 참조한다.

| Term | Physical meaning | Design impact | Glossary reference |
| --- | --- | --- | --- |
| CSPF | 계절 전체 냉방량을 계절 전체 전력량으로 나눈 효율 지표 | 단일 정격점보다 계절 운전 전체의 균형이 중요해진다. | [iso16358_glossary.md](./iso16358_glossary.md) |
| building load | 외기온도에 따라 요구되는 냉방 부하 | 고온 정격 능력만큼 중간온도 부하 대응 능력이 중요하다. | [iso16358_glossary.md](./iso16358_glossary.md) |
| bin hours | 외기온도별 계절 발생 시간 | 시간이 많은 온도 구간의 효율 개선이 등급에 크게 반영된다. | [iso16358_glossary.md](./iso16358_glossary.md) |
| part-load | 장비 능력이 요구 부하보다 큰 운전 상태 | 최소 안정 운전 능력과 사이클링 손실이 계절 효율을 좌우한다. | [iso16358_glossary.md](./iso16358_glossary.md) |
| degradation coefficient | 사이클링 손실을 나타내는 계수 | 저부하 구간에서 과대 용량 설계의 불리함을 키운다. | [iso16358_glossary.md](./iso16358_glossary.md) |
| rated capacity | 기준 시험 조건의 냉방 능력 | 부하선의 기준점이 되어 계절 전체 계산의 크기를 정한다. | [iso16358_glossary.md](./iso16358_glossary.md) |
| capacity modulation | 용량을 낮추거나 높여 부하를 추종하는 능력 | 낮은 부하에서도 연속 운전할 수 있으면 PLF 손실을 줄일 수 있다. | [iso16358_glossary.md](./iso16358_glossary.md) |

## 3. Metric Structure

| Component | Physical role | Rating direction | Reference |
| --- | --- | --- | --- |
| Seasonal cooling output | 계절 동안 실제로 처리한 냉방 부하 | 같은 전력에서 커질수록 CSPF가 증가한다. | ISO 16358-1:2013 Chapter 5 |
| Seasonal electric power | 계절 동안 소비한 전력 | 같은 냉방량에서 작을수록 CSPF가 증가한다. | ISO 16358-1:2013 Chapter 5 |
| Outdoor bin distribution | 온도별 발생 시간 | 자주 발생하는 온도에서의 효율이 더 큰 가중치를 가진다. | UN AC proposal Annex 4 |
| Part-load correction | 장비가 부하보다 클 때의 손실 | 최소 용량이 높을수록 불리해질 수 있다. | ISO 16358-1:2013 Chapter 6 |

## 4. What Actually Drives the Rating

계절 지표는 최고 외기온 정격점 하나만으로 결정되지 않는다. bin hours가 큰 중간 외기온 구간에서 요구 부하를 효율적으로 따라가는 능력이 중요하다.

엔지니어링 해석: 높은 정격 효율을 만들더라도 중간 부하에서 소비전력이 높거나 최소 용량이 너무 크면 계절 누적 전력량이 증가한다. 따라서 냉방 설계는 고온 능력, 중간온도 효율, 저부하 연속 운전 범위를 함께 조정해야 한다.

## 5. High Impact Design Parameters

| Parameter | Why it matters | Design direction |
| --- | --- | --- |
| 중간 외기온 부분부하 효율 | 많은 bin-hour가 중간온도에 몰릴 수 있다. | 열교환기 접근온도와 압축기 효율을 중간 부하에서도 유지한다. |
| 최소 안정 운전 용량 | 요구 부하보다 최소 용량이 크면 사이클링 손실이 커진다. | 낮은 부하에서도 안정적인 연속 운전이 가능하도록 용량 제어 범위를 넓힌다. |
| 팬 및 보조 소비전력 | 계절 누적 전력에 계속 반영된다. | 냉매 회로 효율뿐 아니라 공기측 소비전력도 함께 줄인다. |
| 고온 능력 유지 | 최고 온도 구간에서 능력이 부족하면 냉방량이 제한된다. | 고온 조건에서 압축기 운전 한계와 열교환 성능을 확보한다. |
| 용량 단계 간 간격 | 단계 사이 소비전력 보간 결과에 영향을 준다. | 단계 간 능력 차이를 과도하게 벌리지 않는다. |

## 6. Low Impact / Misleading Design Parameters

| Parameter | Risk | Better interpretation |
| --- | --- | --- |
| 단일 정격점 COP만 개선 | 계절 시간 가중치를 반영하지 못한다. | bin-hour가 큰 구간의 효율 개선과 함께 판단한다. |
| 최대 용량만 확대 | 저부하 PLF 손실을 키울 수 있다. | 최대 능력과 최소 능력의 균형을 본다. |
| 시험점 사이 비선형 특성 무시 | 실제 운전 효율과 seasonal estimate가 벌어질 수 있다. | 시험점 사이 운전 안정성과 소비전력 곡선을 함께 검토한다. |

## 7. Seasonal Bin Strategy

Seasonal bin 구조는 설계 우선순위를 정하는 핵심이다. 시간이 많은 외기온 구간은 작은 효율 개선도 계절 전체 전력량에 크게 누적된다.

엔지니어링 해석: 설계 검토 시 각 온도 bin의 요구 부하와 장비 운전 가능 용량을 겹쳐 보고, 장시간 bin에서 part-load 손실이 반복되는지 확인해야 한다.

## 8. Part-load Strategy

Part-load 성능은 계절 효율의 안정성을 좌우한다. 요구 부하가 낮을 때 장비가 연속 운전하지 못하면 cycling이 발생하고, degradation correction이 계절 전력량을 증가시킨다.

엔지니어링 해석: 최소 용량을 낮추는 것만으로 충분하지 않다. 낮은 용량에서 압축기, 팬, 팽창 장치가 안정적으로 작동하고 열교환기 효율이 유지되어야 한다.

## 9. Practical Design Checklist

| Check | Purpose | Reference |
| --- | --- | --- |
| bin-hour가 큰 온도 구간의 요구 부하를 확인한다. | 설계 타겟 온도를 선정한다. | UN AC proposal Annex 4 |
| 최소 안정 운전 용량과 낮은 bin 부하를 비교한다. | PLF 손실 가능성을 판단한다. | ISO 16358-1:2013 Chapter 6 |
| 중간 부하에서 압축기와 팬 효율을 함께 본다. | 계절 전력량을 줄인다. | ISO 16358-1:2013 Chapter 5 |
| 고온 bin에서 능력 부족이 발생하는지 확인한다. | cooling output cap에 따른 성능 손실을 방지한다. | ISO 16358-1:2013 Chapter 6 |

## 10. References

| Source | Usage |
| --- | --- |
| ISO 16358-1:2013 Chapter 5 | CSPF metric structure |
| ISO 16358-1:2013 Chapter 6 | cooling load, capacity control, part-load calculation |
| UN AC proposal Annex 4 | outdoor temperature bin hours의 설계 영향 |
| Lost-in-translation, Energy for Sustainable Development, 2020 | seasonal performance 규격 비교 맥락 |
