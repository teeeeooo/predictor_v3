# ISO 16358 Design Notes

## 1. Purpose

이 문서는 ISO 16358 계열 계절 효율 지표(CSPF, HSPF)가 제품 설계 의사결정에 주는 압력을 설명한다. ISO 16358 계열 지표는 한 개의 정격 운전점 성능만 평가하지 않고, 계절 bin-hour, 건물 부하선, 부분부하 운전, 보조열 또는 단속 운전 손실을 함께 반영한다. 국가별 보정이나 지역 특이 조건은 다루지 않으며, 공통적인 seasonal performance 관점만 정리한다.

근거: ISO 16358-1:2013 Chapter 5, Chapter 6. ISO 16358-2. UN AC proposal Annex 4는 seasonal calculation이 outdoor temperature bin hours에 의해 가중된다는 점을 보여준다.

엔지니어링 해석: ISO 16358 계열의 설계 핵심은 "정격점에서 좋은 제품"이 아니라, 실제 계절 운전 영역에서 부하선과 성능선이 잘 맞는 제품을 만드는 것이다.

---

## 2. Quick Glossary

상세 용어와 수식 기호는 같은 폴더의 `iso16358_glossary.md`를 참조한다.

| Term | Physical meaning | Design impact | Glossary reference |
| --- | --- | --- | --- |
| Seasonal Performance Factor, SPF | 계절 전체의 유효 출력량을 계절 전체 소비전력량으로 나눈 값 | 단일 COP/EER보다 실제 운전 영역의 평균 성능을 더 강하게 반영한다. | `iso16358_glossary.md` |
| Cooling Seasonal Performance Factor, CSPF | 냉방 계절 전체의 냉방 처리량과 소비전력량의 비 | 중간/저부하 냉방 운전 효율과 단속 손실을 함께 반영한다. | `iso16358_glossary.md` |
| Heating Seasonal Performance Factor, HSPF | 난방 계절 전체의 난방 부하량과 소비전력량의 비 | 저온 능력, 제상 영향, 보조열 발생 여부를 함께 반영한다. | `iso16358_glossary.md` |
| Bin-hour | 특정 외기온도가 계절 중 몇 시간 발생하는지를 나타내는 시간 가중치 | 시간이 많은 온도대에서의 작은 소비전력 차이가 최종 등급에 크게 작용한다. | `iso16358_glossary.md` |
| Building load | 외기온도별로 제품이 처리해야 하는 냉방 또는 난방 부하 | 제품 능력선과 부하선의 상대 위치가 운전 case를 결정한다. | `iso16358_glossary.md` |
| Capacity curve | 외기온도와 운전 단계에 따른 냉난방 능력선 | 부하선보다 너무 높으면 단속 손실, 너무 낮으면 부족 운전이 발생한다. | `iso16358_glossary.md` |
| Power curve | 외기온도와 운전 단계에 따른 소비전력선 | 계절 효율의 분모를 직접 결정하므로 능력선만큼 중요하다. | `iso16358_glossary.md` |
| Part-load | 정격보다 낮은 부하에서 운전하는 상태 | 최소/중간 운전 효율과 용량 제어 범위가 중요해진다. | `iso16358_glossary.md` |
| Cycling loss | 최소 운전 능력이 부하보다 커서 압축기가 반복적으로 켜지고 꺼질 때의 손실 | 최소 운전 능력이 너무 높으면 저부하 구간에서 계절 효율이 낮아진다. | `iso16358_glossary.md` |
| Degradation coefficient | 사이클링 손실을 나타내는 계수 | 저부하 구간에서 과대 용량 설계의 불리함을 키운다. | `iso16358_glossary.md` |
| Rated capacity | 기준 시험 조건의 냉난방 능력 | 부하선의 기준점이 되어 계절 전체 계산의 크기를 정한다. | `iso16358_glossary.md` |
| Capacity modulation | 용량을 낮추거나 높여 부하를 추종하는 능력 | 낮은 부하에서도 연속 운전할 수 있으면 PLF 손실을 줄일 수 있다. | `iso16358_glossary.md` |
| Auxiliary heat | heat pump 능력이 난방 부하보다 부족할 때 부족분을 보조열로 채우는 에너지 | HSPF를 급격히 낮출 수 있으므로 저온 능력 margin이 중요하다. | `iso16358_glossary.md` |

---

## 3. Metric Structure

ISO 16358 계열 지표는 계절 총 처리량을 계절 총 소비전력량으로 나누는 구조이다.

| Metric | Numerator | Denominator | Design meaning | Reference |
| --- | --- | --- | --- | --- |
| CSPF | 계절 냉방 처리량 | 냉방 운전 소비전력량 | 중간/저부하 냉방 운전의 효율과 단속 손실이 중요하다. | ISO 16358-1:2013 Chapter 5 |
| HSPF | 계절 난방 부하량 | heat pump 소비전력량 + 보조열 소비전력량 | 저온 능력, 제상 성능, 보조열 발생 억제가 중요하다. | ISO 16358-2 |
| Outdoor bin distribution | — | 온도별 발생 시간 | 자주 발생하는 온도에서의 효율이 더 큰 가중치를 가진다. | UN AC proposal Annex 4 |
| Part-load correction | — | 장비가 부하보다 클 때의 손실 | 최소 용량이 높을수록 불리해질 수 있다. | ISO 16358-1:2013 Chapter 6 |

엔지니어링 해석: CSPF는 "남는 능력을 얼마나 효율적으로 줄여 쓰는가"가 중요하고, HSPF는 "부족한 능력을 보조열 없이 얼마나 버티는가"가 중요하다.

---

## 4. What Actually Drives the Rating

ISO 16358 계열 지표는 시험점 성능이 그대로 평균되는 구조가 아니다. 시험점은 온도별 capacity curve와 power curve를 만들고, 이 curve가 계절 bin-hour와 building load를 만나면서 최종 지표가 결정된다. 계절 지표는 최고 외기온 정격점 하나만으로 결정되지 않는다. bin hours가 큰 중간 외기온 구간에서 요구 부하를 효율적으로 따라가는 능력이 중요하다.

| Driver | CSPF impact | HSPF impact |
| --- | --- | --- |
| Bin-hour concentration | 시간이 많은 냉방 온도대의 part-load 효율이 중요하다. | 시간이 많은 난방 온도대의 중간부하 효율이 중요하다. |
| Minimum capacity | 너무 높으면 cycling loss가 커진다. | 너무 높으면 저부하 난방에서 cycling loss가 커진다. |
| Intermediate capacity/power | 계절 평균 소비전력에 큰 영향을 준다. | 중온 난방 효율에 큰 영향을 줄 수 있다. |
| Maximum capacity | 고온 냉방 부하 처리 능력을 결정한다. | 저온에서 auxiliary heat 발생 여부를 결정한다. |
| Defrost behavior | 냉방에는 직접 영향이 없다. | capacity 저하와 power 증가를 동시에 유발할 수 있다. |

엔지니어링 해석: 높은 정격 효율을 만들더라도 중간 부하에서 소비전력이 높거나 최소 용량이 너무 크면 계절 누적 전력량이 증가한다. 따라서 냉난방 설계는 고온/저온 능력, 중간온도 효율, 저부하 연속 운전 범위를 함께 조정해야 한다.

---

## 5. High Impact Design Parameters

| Parameter | Why it matters | Design direction |
| --- | --- | --- |
| Compressor turndown range | 최소 운전 능력을 낮출 수 있는지가 part-load 손실을 좌우한다. | 저부하 안정 운전이 가능하도록 최소 Hz, 토크 안정성, 윤활 조건을 함께 검토한다. |
| Intermediate operating efficiency | 계절 bin-hour가 많은 영역에서 자주 사용된다. | 중간 운전점의 압축기 효율, 팬 소비전력, 냉매 순환 안정성을 우선 확인한다. |
| Heat exchanger margin | 같은 capacity를 더 낮은 압축비와 낮은 fan power로 달성할 수 있다. | 면적, 풍량, 접근온도 trade-off를 계절 운전점 기준으로 본다. |
| Fan power | capacity는 유지하면서 denominator를 직접 증가시킬 수 있다. | 실내외 fan RPM 증가가 효율에 주는 손익을 capacity 증가와 함께 본다. |
| Defrost control | 난방 capacity와 power를 동시에 악화시킬 수 있다. | 제상 진입 조건, 제상 시간, 복귀 안정성을 성능 시험점 기준으로 검토한다. |
| Low-temperature maximum capacity | auxiliary heat 발생을 막는다. | 저온 max 성능은 capacity 증가와 power 증가의 trade-off로 판단한다. |
| 용량 단계 간 간격 | 단계 사이 소비전력 보간 결과에 영향을 준다. | 단계 간 능력 차이를 과도하게 벌리지 않는다. |

### Required-only vs optional minimum test impact

ISO 16358 CSPF에서 variable-capacity 장비가 minimum capacity test를 수행하지 않는 경우, half capacity point가 실질적인 최저 연속 운전점처럼 작용한다. 이 경우 half capacity가 실제 저부하 영역보다 높게 설정되어 있으면, 장시간 bin에서 cycling loss가 커질 수 있다.

Optional minimum test를 포함하면 저부하 연속 운전 능력을 더 직접적으로 반영할 수 있으므로, minimum capacity와 minimum power의 실제 설계 품질이 계절 효율에 드러난다.

엔지니어링 해석: required-only 평가에서는 half 운전점의 위치가 저부하 효율까지 대표하게 되므로, half capacity를 지나치게 높게 잡는 설계는 불리해질 수 있다. optional minimum 평가에서는 minimum 운전점 자체의 효율과 안정성이 중요해진다.

---

## 6. Low Impact / Misleading Design Parameters

| Misleading focus | Why it can mislead | Better interpretation |
| --- | --- | --- |
| 단일 정격점 COP/EER만 개선 | 계절 지표는 정격점보다 part-load와 bin-hour가 많은 구간을 더 크게 반영할 수 있다. | bin-hour가 큰 구간의 효율 개선과 함께 판단한다. |
| 최대 능력만 키우기 | cooling에서는 저부하 cycling이 나빠질 수 있고, heating에서는 max power 증가로 HSEC가 커질 수 있다. | 최대 능력과 최소 능력의 균형을 본다. |
| minimum capacity를 무조건 낮추기 | cycling은 줄지만, 너무 낮은 운전점의 COP가 나쁘면 전체 계절 전력량이 줄지 않을 수 있다. | 최소 용량 운전점의 효율도 함께 본다. |
| capacity만 보고 power curve를 무시 | 최종 지표의 denominator는 power × hours이므로 power curve가 직접적이다. | 시험점 사이 운전 안정성과 소비전력 곡선을 함께 검토한다. |
| 제상 capacity만 개선 | defrost power 증가가 크면 HSPF 개선이 제한될 수 있다. | defrost power 억제도 함께 본다. |

---

## 7. Seasonal Bin Strategy

Seasonal bin 구조는 설계 우선순위를 정하는 핵심이다. 시간이 많은 외기온 구간은 작은 효율 개선도 계절 전체 전력량에 크게 누적된다.

| Situation | Design interpretation |
| --- | --- |
| 특정 온도대 bin-hour가 큼 | 해당 온도대의 1 W 소비전력 절감 효과가 누적되어 커진다. |
| 극한 온도 bin-hour가 작음 | 단순 power 절감 효과는 작을 수 있지만, capacity shortage 또는 auxiliary가 발생하면 영향이 커질 수 있다. |
| 중간 온도대가 넓게 분포 | intermediate 운전점의 power curve가 중요해진다. |
| 저부하 온도대가 많음 | minimum capacity와 cycling loss 관리가 중요해진다. |

엔지니어링 해석: 계절 효율 개선은 "가장 힘든 온도" 하나를 최적화하는 작업이 아니라, "가장 오래 머무는 운전 영역"의 power를 낮추는 작업이다. 설계 검토 시 각 온도 bin의 요구 부하와 장비 운전 가능 용량을 겹쳐 보고, 장시간 bin에서 part-load 손실이 반복되는지 확인해야 한다.

---

## 8. Part-load Strategy

Part-load 성능은 계절 효율의 안정성을 좌우한다. 요구 부하가 낮을 때 장비가 연속 운전하지 못하면 cycling이 발생하고, degradation correction이 계절 전력량을 증가시킨다. 제품이 building load보다 큰 capacity를 갖는 경우가 많은 part-load 구간에서, 설계자는 capacity를 충분히 줄일 수 있는지, 줄인 상태에서 효율이 유지되는지, 단속 운전으로 넘어가는지 확인해야 한다.

| Part-load issue | Design check |
| --- | --- |
| Minimum capacity가 부하보다 큼 | cycling loss 발생 여부 확인 |
| Minimum power가 높음 | 저부하 bin에서 계절 전력량 증가 가능 |
| Intermediate point가 부하선과 멀리 떨어짐 | power interpolation 구간이 불리해질 수 있음 |
| Capacity step 간격이 큼 | 부하 추종성이 나빠지고 효율 손실 가능 |
| Fan power 비중 증가 | 저부하에서는 fan power의 상대 비중이 커질 수 있음 |

엔지니어링 해석: 최소 용량을 낮추는 것만으로 충분하지 않다. 낮은 용량에서 압축기, 팬, 팽창 장치가 안정적으로 작동하고 열교환기 효율이 유지되어야 한다.

---

## 9. Standby / Off-mode Power Strategy

ISO 16358 적용 국가와 제품 범위에 따라 standby 또는 off-mode 항목의 반영 방식은 달라질 수 있다. 설계 관점에서는 작은 전력값이라도 긴 시간 동안 누적되면 계절 지표에 영향을 줄 수 있다는 점을 우선 고려해야 한다.

| Design issue | Design interpretation |
| --- | --- |
| 대기전력이 작아 보여 무시됨 | 계절 시간 가중치가 크면 누적 소비전력에 의미 있게 반영될 수 있다. |
| 제어 보드와 센서 상시 소비전력 | 운전 중 효율 개선과 별도로 denominator를 증가시킬 수 있다. |
| 국가별 반영 방식 차이 | 지역 규격에서 해당 항목이 계절 소비전력에 포함되는지 확인해야 한다. |

---

## 10. Heating-specific Strategy

HSPF에서는 저온 능력 부족과 제상 영향이 핵심이다. 특히 heat pump capacity가 building load보다 작아지면 부족분은 auxiliary heat로 들어가고, 이 값은 HSPF denominator에 포함된다.

| Heating design focus | Design impact |
| --- | --- |
| Low-temperature capacity | auxiliary heat 발생 여부를 결정한다. |
| Defrost capacity 유지 | 착상 구간에서 heat pump output 저하를 줄인다. |
| Defrost power 억제 | 제상 구간 HSEC 증가를 줄인다. |
| Intermediate heating efficiency | 난방 계절 중 자주 발생하는 중온 영역의 효율을 좌우한다. |
| Bivalent region margin | capacity shortage에 대한 실측/공차 안전 여유를 만든다. |

엔지니어링 해석: HSPF가 낮을 때는 먼저 "COP가 낮은가?"보다 "어느 bin에서 auxiliary가 발생하는가?"를 확인하는 것이 효과적이다.

---

## 11. Cooling-specific Strategy

CSPF에서는 고온 정격 능력보다 중간 온도대의 part-load 효율과 minimum capacity 관리가 중요해질 수 있다.

| Cooling design focus | Design impact |
| --- | --- |
| Minimum cooling capacity | 저부하 bin에서 cycling loss를 좌우한다. |
| Intermediate cooling power | 계절 냉방 전력량에 직접 누적된다. |
| High-temperature capacity | 고온 bin에서 output cap 발생 여부를 결정한다. |
| Fan/compressor balance | capacity 증가 대비 power 증가가 크면 CSPF가 개선되지 않을 수 있다. |
| Heat exchanger effectiveness | 같은 capacity를 낮은 power로 처리할 수 있는 기반이 된다. |

---

## 12. Practical Design Checklist

### CSPF checklist

| Check item | Why it matters | Reference |
| --- | --- | --- |
| bin-hour가 큰 온도 구간의 요구 부하를 확인한다. | 설계 타겟 온도를 선정한다. | UN AC proposal Annex 4 |
| 최소 안정 운전 용량과 낮은 bin 부하를 비교한다. | PLF 손실 가능성을 판단한다. | ISO 16358-1:2013 Chapter 6 |
| 중간 부하에서 압축기와 팬 효율을 함께 본다. | 계절 전력량을 줄인다. | ISO 16358-1:2013 Chapter 5 |
| 고온 bin에서 능력 부족이 발생하는지 확인한다. | cooling output cap에 따른 성능 손실을 방지한다. | ISO 16358-1:2013 Chapter 6 |
| 정격 운전점 개선이 실제 bin-hour에서 의미가 있는가? | 정격점 집착을 방지한다. | — |
| fan power 증가가 capacity 증가보다 불리하지 않은가? | denominator 관리를 위함이다. | — |

### HSPF checklist

| Check item | Why it matters | Reference |
| --- | --- | --- |
| 저온에서 maximum capacity가 building load를 충분히 커버하는가? | auxiliary heat 방지 | ISO 16358-2 |
| defrost 조건에서 capacity 하락이 과도하지 않은가? | 착상 구간 output 유지 | ISO 16358-2 |
| defrost 조건에서 power 증가가 과도하지 않은가? | HSEC 증가 방지 | ISO 16358-2 |
| 중온 영역의 intermediate/rated power가 낮은가? | 난방 bin-hour 영향 | ISO 16358-2 |
| auxiliary 발생 bin이 있는가? | HSPF 취약점 직접 확인 | ISO 16358-2 |
| maximum power 증가가 auxiliary 감소 효과보다 큰가? | 저온 max 설계 trade-off 판단 | ISO 16358-2 |

---

## 13. References

| Source | Usage |
| --- | --- |
| ISO 16358-1:2013 Chapter 5 | CSPF metric structure |
| ISO 16358-1:2013 Chapter 6 | cooling load, capacity control, part-load calculation |
| ISO 16358-2 | HSPF 계절 난방 효율 구조 |
| ISO 16358-3 | Annual performance factor 관련 참조 |
| UN AC proposal Annex 4 | outdoor temperature bin hours의 설계 영향 |
| Lost-in-translation, Energy for Sustainable Development, 2020 | seasonal performance 규격 비교 맥락 |
