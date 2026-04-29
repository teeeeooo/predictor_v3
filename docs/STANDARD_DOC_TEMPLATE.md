# Standard Document Template

이 문서는 EN14825, AHRI 210/240, ISO16358 등 규격 문서를 새로 작성할 때 복사해서 사용하는 표준 템플릿이다. 실제 작성 시 `<standard>`는 `en14825`, `ahri210_240`, `iso16358`처럼 프로젝트에서 합의한 짧은 이름으로 바꾼다.

---

## Template A: `<standard>_notes.md`

### 1. Overview

규격의 목적, 평가 지표, 적용 제품군을 요약한다. 핵심 주장은 반드시 `Clause X.X.X`, `Table X`, `Equation X` 형식의 근거를 붙인다.

### 2. Scope

이 프로젝트에서 지원하는 범위와 제외하는 범위를 구분한다. 제품 유형, 운전 모드, 기후 조건, 지역 조건, 용량 제어 방식 등을 표로 정리한다.

### 3. Glossary Reference

용어 본문은 이 문서에 중복 작성하지 않는다. 상세 용어는 같은 폴더의 `<standard>_glossary.md`를 링크하고, notes 본문에는 계산 흐름을 이해하는 데 필요한 최소 참조만 둔다.

| Glossary | Scope | Link |
| --- | --- | --- |
| `<standard>_glossary.md` | 공통 용어, 수식 기호, 코드/스키마 매핑, 데이터 위치 |  |

### 4. Input Schema

계산에 필요한 입력 항목을 정리한다. 단위, 필수 여부, 허용 범위, 누락 시 처리 방식을 포함한다.

| Field | Standard symbol | Unit | Required | Validation rule | Reference |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

### 5. Output Schema

계산 결과 항목을 정리한다. 최종 등급 지표와 중간 산출물을 구분하고, 각 값이 어떤 검증이나 UI 표시에서 사용되는지 적는다.

| Field | Meaning | Unit | Derived from | Reference |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### 6. Calculation Flow

입력 검증부터 최종 지표 산출까지의 순서를 단계별로 적는다. 계절 합산, 보간, 보정계수 적용, 경계 조건은 별도 단계로 분리한다.

### 7. Formula Mapping

규격 수식을 표로 정리한다. 수식 번호가 없으면 조항이나 표 번호를 기준으로 적고, 프로젝트 해석이 필요한 부분은 별도 열에 분리한다.

| Formula | Standard reference | Inputs | Outputs | Project interpretation |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### 8. Code Mapping

규격 수식과 프로젝트 파일, 함수, 반환 항목의 대응 관계를 적는다. 규격 원식과 구현상 단순화가 다르면 반드시 구분한다.

| Standard item | File | Function | Output key | Notes |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### 9. Critical Implementation Notes

구현자가 반드시 지켜야 하는 규칙을 적는다. 단위 변환, 입력 누락, 보간 방식, 계절 시간 가중치, 보정계수 적용 조건처럼 오류가 성능값을 크게 바꾸는 항목을 우선한다.

### 10. Unsupported / Not Yet Implemented

지원하지 않는 규격 범위를 명시한다. 단순히 "미지원"이라고 쓰지 말고, 왜 현재 범위에서 제외되었는지와 추가 시 필요한 입력을 적는다.

| Item | Reason | Required data to support | Reference |
| --- | --- | --- | --- |
|  |  |  |  |

### 11. Golden Sample Verification

검증 샘플의 입력, 기대값, 허용 오차, 실행 결과를 정리한다. 규격 예제, 인증 리포트, 내부 기준값을 구분한다.

| Case | Source | Expected | Actual | Tolerance | Result |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

### 12. References

사용한 규격 문서, 조항, 표, 부속서, 내부 검증 자료를 적는다. 문서명과 버전을 반드시 포함한다.

### 13. Prompt for Future Agent

향후 Agent에게 같은 규격을 수정하게 할 때 사용할 프롬프트를 적는다. 읽어야 할 문서, 수정 범위, 금지 범위, 검증 명령을 명시한다.

---

## Template B: `<standard>_dev_notes.md`

### 1. Purpose

이 문서가 구현자와 Agent에게 제공하는 역할을 설명한다. 규격 해석 문서가 아니라 구현 실수 방지와 검증 재현을 위한 문서임을 명확히 한다.

glossary 본문은 이 문서에 포함하지 않는다. 필요한 경우 같은 폴더의 `<standard>_glossary.md` 링크만 둔다. Parent standard 아래 region extension 문서라면 parent glossary와 region glossary 링크를 모두 둘 수 있지만, 용어 정의 본문은 glossary 문서에만 작성한다.

### 2. Top Implementation Pitfalls

가장 자주 발생하는 오류를 우선순위로 정리한다. 각 항목에는 증상, 원인, 방지 방법을 포함한다.

| Pitfall | Symptom | Cause | Prevention | Reference |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### 3. Correct Calculation Order

계산 순서를 순서대로 적는다. 순서가 바뀌면 결과가 달라지는 단계는 이유를 설명한다.

### 4. Data Model Notes

입력 데이터 구조와 중간 데이터 구조의 의미를 설명한다. 원문 규격의 표 구조와 프로젝트 데이터 구조가 다르면 변환 관계를 명시한다.

### 5. Interpolation / Extrapolation Rules

보간(Interpolation)과 외삽(Extrapolation) 허용 여부를 정리한다. 각 규칙에는 근거 조항과 경계값 처리 방식을 붙인다.

### 6. Degradation / Correction Factor Rules

성능 저하 계수(Degradation factor)와 보정계수(Correction factor)의 적용 조건을 정리한다. 적용하지 않는 조건도 반드시 포함한다.

### 7. Debugging Checklist

계산 결과가 어긋날 때 확인할 순서를 체크리스트로 작성한다. 단위, 시간 가중치, 부하선, 보정계수, 반올림을 포함한다.

### 8. Test Strategy

단위 테스트, golden 테스트, 경계 조건 테스트의 목적을 구분한다. 어떤 변경이 어떤 테스트를 요구하는지 적는다.

### 9. Golden Case Strategy

대표 샘플 선정 기준을 적는다. 최소한 정상 케이스, 경계 케이스, 보정계수 적용 케이스, 미지원 범위 차단 케이스를 고려한다.

### 10. Future Refactor Notes

향후 구조 개선이 필요한 지점을 적는다. 단, 현재 동작을 바꾸지 않아야 하는 항목과 실제 변경 가능한 항목을 분리한다.

### 11. Prompt Snippets for Agent

반복 작업에 사용할 Agent 프롬프트 조각을 적는다. 반드시 읽어야 할 파일, 수정 가능 파일, 수정 금지 파일, 검증 명령을 포함한다.

---

## Template C: `<standard>_design_notes.md`

### 1. Purpose

이 문서가 제품 설계 관점에서 어떤 결정을 돕는지 설명한다. 성능 등급을 높이기 위한 물리적 방향과 규격상 가중치의 의미를 중심으로 쓴다.

### 2. Quick Glossary

제품 설계자가 문서를 읽기 전에 알아야 할 핵심 용어 5~10개를 정리한다. 상세 glossary는 같은 폴더의 `<standard>_glossary.md` 문서를 참조하고, 공통 용어를 이 문서에 중복 작성하지 않는다.

각 용어는 사전식 정의보다 물리적 의미와 설계 영향 중심으로 작성한다.

이 문서에서는 코드 파일명, 함수명, 변수명, JSON key를 언급하지 않는다. 제품 설계 관점의 물리적 의미와 규격 구조 기반 인사이트만 작성한다.

| Term | Physical meaning | Design impact | Glossary reference |
| --- | --- | --- | --- |
|  |  |  |  |

### 3. Metric Structure

평가 지표가 어떤 운전 조건, 계절 가중치, 보조 에너지 항목으로 구성되는지 설명한다. 각 구성요소가 최종 등급에 미치는 방향을 표로 정리한다.

### 4. What Actually Drives the Rating

최종 등급에 가장 큰 영향을 주는 요소를 우선순위로 적는다. 영향도가 큰 온도 구간, 부분부하 조건, 대기 전력 항목을 구분한다.

### 5. High Impact Design Parameters

성능 향상 효과가 큰 설계 인자를 정리한다. 압축기 용량 제어 범위, 열교환기 여유도, 팬 효율, 제상 영향, 보조열 사용 시점을 포함할 수 있다.

### 6. Low Impact / Misleading Design Parameters

등급 개선 효과가 작거나 오해하기 쉬운 설계 인자를 정리한다. 특정 정격점의 개선이 계절 지표에서 작게 반영되는 경우를 설명한다.

### 7. Seasonal Bin Strategy

계절 빈(Seasonal bin) 분포가 성능 평가에 주는 영향을 설명한다. 빈 시간이 큰 외기온 구간과 설계 우선순위를 연결한다.

### 8. Part-load Strategy

부분부하(Part-load) 운전에서 효율을 높이는 전략을 설명한다. 최소 안정 운전 용량, 사이클링 손실, 용량 제어 단계 간 간격의 의미를 포함한다.

### 9. Standby / Off-mode Power Strategy

대기전력(Standby power)과 꺼짐 모드 전력(Off-mode power)이 계절 지표에 미치는 영향을 설명한다. 작은 전력값이라도 시간 가중치 때문에 중요한 경우를 구분한다.

### 10. Heating-specific Strategy

난방 운전에서 중요한 설계 전략을 정리한다. 저온 성능 유지, 보조열 억제, 제상 손실 관리, 이원점(Bivalent temperature)의 영향을 포함한다.

### 11. Cooling-specific Strategy

냉방 운전에서 중요한 설계 전략을 정리한다. 중간 외기온 부분부하 효율, 실내외 팬 소비전력, 열교환기 접근온도, 최소 용량 운전을 포함한다.

### 12. Practical Design Checklist

제품 설계자가 검토할 항목을 체크리스트로 정리한다. 각 항목에는 관련 성능 지표와 규격 근거를 붙인다.

### 13. References

근거가 되는 규격 조항, 표, 부속서, 시험 조건을 정리한다. 엔지니어링 해석과 규격 원문 근거를 분리해 적는다.

---

## Template D: Region Extension

공통 규격 엔진을 국가별 또는 지역별 규격으로 확장할 때는 parent standard 아래 `regions/<region_standard>/`에 4개 문서를 둔다.

```text
docs/<parent_standard>/regions/<region_standard>/
- <region_standard>_notes.md
- <region_standard>_dev_notes.md
- <region_standard>_design_notes.md
- <region_standard>_glossary.md
```

예:

```text
docs/iso16358/regions/ks_c_9306/
- ks_c_9306_notes.md
- ks_c_9306_dev_notes.md
- ks_c_9306_design_notes.md
- ks_c_9306_glossary.md
```

### Region Notes

Region notes는 parent standard의 공통 계산 구조를 재작성하지 않고, region-specific 입력 조건, 파생 규칙, 보정 규칙, 출력 차이, golden sample만 정리한다. 공통 계산 구조가 필요하면 parent `<parent_standard>_notes.md`의 해당 섹션을 링크한다.

### Region Dev Notes

Region dev notes는 region-specific 구현 실수 방지, 디버깅 순서, 테스트 전략, Agent 재사용 프롬프트를 작성한다. Parent standard의 공통 구현 지침은 링크로 참조하고 본문을 반복하지 않는다.

### Region Design Notes

Region design notes는 region-specific 제품 설계 인사이트만 작성한다. 코드 언급 금지 규칙은 parent design notes와 동일하게 적용한다.

### Region Glossary

Region glossary는 region 고유 용어, parent 용어와 의미가 달라지는 항목, region 데이터 위치를 관리한다. Parent glossary의 공통 용어를 복사하지 않는다.
