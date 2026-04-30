# 프로젝트 전체 리팩토링 백로그 (Refactor Plan)

## 1. Docs 구조 리팩토링 (Docs Structure Refactor)
- glossary/ 분리
- notes / design_notes / dev_notes 구조화
- 내부 링크 정리

현재 docs 구조는 임시 구조이며, 향후 아래 구조로 재편이 필요하다:
docs/
├── ahri210240/
│   ├── glossary.md (신규 분리)
│   ├── notes.md
│   ├── design_notes.md
│   └── dev_notes.md
├── en14825/
│   ├── glossary.md (신규 분리)
│   ├── notes.md
│   ├── design_notes.md
│   └── dev_notes.md
└── ...

### 작업 범위
- AHRI / EN14825 / ISO16358 관련된 모든 문서를 위 구조로 이동 및 정규화
- 규격별 glossary 분리 및 내부 링크 수정
- DOCS_GUIDELINES.md 업데이트

### 트리거 조건 (이 조건이 만족되기 전까지 실행 금지)
- ISO16358 구현 완료 이후
- predictor / trainer 1차 안정화 이후

### 우선순위
🔥 HIGH (반드시 수행해야 함)

---

## 2. ML 파이프라인 리팩토링 (ML Pipeline Refactor)
- predictor 구조 정리
- trainer pipeline 단순화
- feature schema 통합

### 트리거 조건
- ISO16358 완료 및 predictor/trainer 안정화 이후

### 우선순위
🔥 HIGH (반드시 수행해야 함)

---

## ISO16358 Calculator Refactor Candidates

`ISO16358Calculator`는 현재 CSPF, generic HSPF, variable HSPF, KS C 9306 CSPF/HSPF helper를 모두 포함하고 있어 클래스가 과대화되고 있다.

당장 리팩토링하지 않는다. 현재 우선순위는 region config 확장, `calc_window` 연결, predictor/calculator 연동이다. 리팩토링은 태국/베트남/말레이시아/인도/SASO region config 확장 후 수행한다.

후보 구조:

| Module | Responsibility |
| --- | --- |
| `calculator_iso16358.py` | ISO16358 common entry point, CSPF common path, generic HSPF fallback |
| `calculator_iso16358_ks.py` 또는 `regions/ks_c9306.py` | KS C 9306 CSPF/HSPF profile-specific helpers, `_ks_hspf_*` helpers, `ks_intersection` helper |

현재는 inheritance/plugin 구조를 도입하지 않는다. region-specific 예외가 더 쌓인 뒤 분리 여부를 판단한다.
