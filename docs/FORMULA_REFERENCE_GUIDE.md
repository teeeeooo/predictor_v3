# Formula Reference Guide

이 문서는 규격 문서에서 수식, 변수, 용어를 일관된 형식으로 정리하기 위한 공통 작성 규칙이다. 목적은 규격 원문, 프로젝트 해석, 물리적 의미를 분리해 장기적으로 재사용 가능한 참조 자료를 만드는 것이다.

## 1. Formula Entry Format

각 수식은 아래 형식으로 정리한다.

| 항목 | 작성 규칙 |
| --- | --- |
| Formula name | 수식의 역할을 짧고 명확하게 적는다. |
| Standard reference | `EN14825:2012 Clause X.X.X`, `AHRI 210/240-2026 Table X`처럼 문서명, 버전, 위치를 적는다. |
| Equation number | 원문 수식 번호가 있으면 적고, 없으면 `N/A`와 근거 조항을 적는다. |
| Formula | 규격 원문 표기를 우선해 작성한다. 프로젝트 내부 이름으로 바꾸지 않는다. |
| Variables | 수식에 등장하는 모든 변수를 표로 풀어 쓴다. |
| Physical meaning | 수식이 물리적으로 무엇을 의미하는지 설명한다. |
| Used in | 어떤 계절 지표, 운전점, 중간 계산에서 쓰이는지 적는다. |
| Common mistakes | 단위, 분모, 시간 가중치, 보정계수 적용 위치 같은 흔한 오류를 적는다. |
| Engineering interpretation | 제품 설계 관점에서 이 수식이 어떤 방향성을 주는지 설명한다. |

### Formula Entry Template

| Field | Content |
| --- | --- |
| Formula name |  |
| Standard reference |  |
| Equation number |  |
| Formula |  |
| Variables |  |
| Physical meaning |  |
| Used in |  |
| Common mistakes |  |
| Engineering interpretation |  |

## 2. Variable Entry Format

각 변수는 아래 형식으로 정리한다.

| 항목 | 작성 규칙 |
| --- | --- |
| Symbol | 규격 원문 기호를 우선한다. |
| Name | 영어 명칭을 적고, 필요하면 한국어를 병기한다. |
| Unit | 단위를 명확히 적는다. 무차원이면 `dimensionless`로 적는다. |
| Meaning | 계산상 의미를 설명한다. |
| Where it appears | 등장하는 수식, 표, 조항을 적는다. |
| Notes | 경계 조건, 주의사항, 프로젝트 해석을 적는다. |

### Variable Entry Template

| Field | Content |
| --- | --- |
| Symbol |  |
| Name |  |
| Unit |  |
| Meaning |  |
| Where it appears |  |
| Notes |  |

## 3. Glossary Entry Format

각 용어는 아래 형식으로 정리한다.

| 항목 | 작성 규칙 |
| --- | --- |
| Term | 규격 원문 용어를 적는다. |
| Korean name | 한국어 명칭을 적는다. |
| Definition | 규격상 정의를 요약한다. |
| Physical meaning | 실제 냉동공조 시스템에서 의미하는 현상을 설명한다. |
| Calculation role | 계산에서 어떤 역할을 하는지 적는다. |
| Design implication | 제품 설계에서 어떤 판단으로 이어지는지 적는다. |

### Glossary Entry Template

| Field | Content |
| --- | --- |
| Term |  |
| Korean name |  |
| Definition |  |
| Physical meaning |  |
| Calculation role |  |
| Design implication |  |

## 4. 예시 항목

아래 예시는 EN14825 문서를 작성할 때의 형식 예시다. 실제 문서에서는 정확한 조항, 표, 수식 번호를 원문 기준으로 보강해야 한다.

### TOL

| Field | Content |
| --- | --- |
| Term | TOL |
| Korean name | 운전 한계 온도 |
| Definition | 히트펌프가 난방 운전을 유지할 수 있는 하한 외기온 조건 |
| Physical meaning | 저온에서 압축기와 냉매 회로가 낼 수 있는 난방 능력의 한계 |
| Calculation role | 저온 구간의 난방 용량, 보조열 필요 여부, 계절 효율에 영향을 준다. |
| Design implication | 낮은 TOL에서 난방 용량을 유지하면 보조열 의존도를 줄일 수 있다. |

### Tbiv

| Field | Content |
| --- | --- |
| Term | Tbiv |
| Korean name | 이원점 온도 |
| Definition | 히트펌프 용량과 건물 난방 부하가 만나는 기준 외기온 |
| Physical meaning | 이 온도 아래에서는 보조열 또는 추가 열원이 필요해질 수 있다. |
| Calculation role | 난방 계절 성능에서 히트펌프 단독 운전과 보조열 개입 구간을 나눈다. |
| Design implication | Tbiv를 낮출수록 보조열 사용 시간이 줄어 계절 효율에 유리하다. |

### Cd

| Field | Content |
| --- | --- |
| Symbol | Cd |
| Name | Degradation coefficient, 성능 저하 계수 |
| Unit | dimensionless |
| Meaning | 부분부하 사이클링으로 발생하는 효율 저하를 나타내는 계수 |
| Where it appears | EN14825 부분부하 성능 보정 규칙 |
| Notes | 용량 제어 방식과 부하율 조건에 따라 적용 여부가 달라진다. |

### CR

| Field | Content |
| --- | --- |
| Symbol | CR |
| Name | Capacity ratio, 용량비 |
| Unit | dimensionless |
| Meaning | 요구 부하 대비 가용 용량의 비율 |
| Where it appears | EN14825 부분부하 성능 계산 |
| Notes | CR이 1보다 큰 조건에서는 사이클링 또는 용량 제어 해석이 중요하다. |

### bin hour

| Field | Content |
| --- | --- |
| Term | bin hour |
| Korean name | 빈 시간 |
| Definition | 특정 외기온 구간에 계절 중 배정된 시간 |
| Physical meaning | 실제 계절에서 해당 외기온 조건이 얼마나 자주 나타나는지를 뜻한다. |
| Calculation role | 부하와 소비전력을 계절 값으로 합산할 때의 시간 가중치 |
| Design implication | 빈 시간이 큰 온도 구간의 효율 개선이 최종 지표에 더 크게 반영된다. |

### backup heater / elbu

| Field | Content |
| --- | --- |
| Term | backup heater / elbu |
| Korean name | 보조 전기 히터 |
| Definition | 히트펌프 난방 용량이 부족할 때 부족 열량을 보충하는 전기 열원 |
| Physical meaning | 저온 난방에서 압축식 사이클이 감당하지 못하는 부하를 직접 전기열로 보충한다. |
| Calculation role | 난방 계절 소비전력을 증가시켜 SCOP를 낮출 수 있다. |
| Design implication | 저온 용량 유지와 제어 최적화로 보조 전기 히터 사용을 줄이는 것이 중요하다. |

