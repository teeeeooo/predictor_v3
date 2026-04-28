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
