# docs

이 폴더는 EN14825, AHRI 210/240, ISO16358 등 HVAC 효율 규격을 프로젝트 안에서 일관되게 축적하기 위한 문서 공간이다. 목표는 단순한 구현 메모가 아니라, AI Agent와 개발자가 재사용할 수 있고 제품 설계 엔지니어도 참고할 수 있는 규격 구현 자산을 만드는 것이다.

규격 문서를 작성하거나 수정하는 Agent는 반드시 AGENTS.md와 docs/DOCS_GUIDELINES.md를 먼저 읽어야 한다.

## 공통 문서

| 파일 | 목적 |
| --- | --- |
| `DOCS_GUIDELINES.md` | 프로젝트 전체 규격 문서 작성 철학, 금지 규칙, 근거 표기, 품질 기준을 정의한다. |
| `STANDARD_DOC_TEMPLATE.md` | 규격별 `notes`, `dev_notes`, `design_notes`, `glossary` 문서를 만들 때 복사해서 쓰는 표준 템플릿이다. |
| `FORMULA_REFERENCE_GUIDE.md` | 수식, 변수, 용어를 정리할 때 사용하는 공통 형식과 예시를 제공한다. |
| `README.md` | `docs` 폴더의 목적, 문서 구조, 새 문서 작성 순서를 안내한다. |

## 규격별 문서 구조

각 규격은 원칙적으로 아래 구조를 따른다.

```text
docs/<standard>/
- <standard>_notes.md
- <standard>_dev_notes.md
- <standard>_design_notes.md
- <standard>_glossary.md
```

예:

```text
docs/en14825/en14825_notes.md
docs/en14825/en14825_dev_notes.md
docs/en14825/en14825_design_notes.md
docs/en14825/en14825_glossary.md
```

| 문서 | 역할 |
| --- | --- |
| `<standard>_notes.md` | 규격 개요, 계산 구조, 입력/출력 스키마, 수식과 코드 매핑, 검증 결과를 정리한다. |
| `<standard>_dev_notes.md` | 구현 노하우, 실수 방지, 디버깅 방법, 테스트 전략, Agent 재사용 프롬프트를 정리한다. |
| `<standard>_design_notes.md` | 제품 설계 관점에서 효율 측정값을 높이는 전략과 정량적 인사이트를 정리한다. |
| `<standard>_glossary.md` | 규격별 단일 용어 사전이다. 도메인 의미와 코드/스키마 정보를 분리해 관리한다. |

### 파일명 규칙

규격별 canonical 문서는 반드시 `<standard>_<role>.md` 형식을 사용한다.

| 역할 | 파일명 예시 | 비고 |
| --- | --- | --- |
| 기준 노트 | `en14825_notes.md` | 규격 구조와 계산 흐름의 기준 문서 |
| 개발 노트 | `en14825_dev_notes.md` | 구현, 디버깅, 테스트 전략 문서 |
| 설계 노트 | `en14825_design_notes.md` | 제품 설계 엔지니어용 해석 문서 |
| 용어집 | `en14825_glossary.md` | 규격별 용어 단일 출처 |

`notes.md`, `dev_notes.md`, `design_notes.md`, `glossary.md`처럼 규격명이 없는 파일명은 신규 canonical 문서명으로 사용하지 않는다. 기존에 남아 있는 파일은 통합 검토 또는 원본 보존 목적의 임시 자료로 취급하고, 삭제 여부는 별도 지시가 있을 때만 결정한다.

## 현재 규격별 문서 현황

| 규격 | canonical 문서 | 보조/검토 문서 |
| --- | --- | --- |
| EN14825 | `docs/en14825/en14825_notes.md`, `docs/en14825/en14825_dev_notes.md`, `docs/en14825/en14825_design_notes.md`, `docs/en14825/en14825_glossary.md` | `docs/en14825_scop_notes.md` |
| AHRI 210/240 | `docs/ahri210240/ahri210240_notes.md`, `docs/ahri210240/ahri210240_dev_notes.md`, `docs/ahri210240/ahri210240_design_notes.md`, `docs/ahri210240/ahri210240_glossary.md` | `docs/skills/ahri_hspf2.md` |
| ISO16358 | `docs/iso16358/iso16358_notes.md`, `docs/iso16358/iso16358_dev_notes.md`, `docs/iso16358/iso16358_design_notes.md`, `docs/iso16358/iso16358_glossary.md` | `docs/iso16358/korea_ks_c_9306_notes.md` |

## 새 규격 문서를 추가할 때의 순서

1. `AGENTS.md`와 `docs/DOCS_GUIDELINES.md`를 읽고 수정 가능 범위를 확인한다.
2. `docs/STANDARD_DOC_TEMPLATE.md`에서 필요한 템플릿을 복사한다.
3. `docs/<standard>/` 폴더를 만들고 `notes`, `dev_notes`, `design_notes`, `glossary` 4개 문서를 분리해 작성한다.
4. 핵심 주장마다 조항, 표, 부속서, 수식 번호를 붙인다.
5. 수식과 변수는 `docs/FORMULA_REFERENCE_GUIDE.md` 형식에 맞춰 정리한다.
6. 개발 노하우와 제품 설계 노하우가 섞이지 않았는지 점검한다.
7. 빈 문단, 근거 없는 추정, "TODO만 남김" 상태가 없는지 확인한다.

## Agent 문서 작업 필독 파일

문서 작성 또는 수정 작업을 맡은 Agent에게는 아래 파일을 반드시 읽힌다.

| 순서 | 파일 | 이유 |
| --- | --- | --- |
| 1 | `AGENTS.md` | 프로젝트 전체 금지 규칙과 수정 범위를 확인하기 위함 |
| 2 | `docs/DOCS_GUIDELINES.md` | 문서 철학, 구조, 근거 표기, 품질 기준을 맞추기 위함 |
| 3 | `docs/STANDARD_DOC_TEMPLATE.md` | 새 규격 문서의 기본 골격을 통일하기 위함 |
| 4 | `docs/FORMULA_REFERENCE_GUIDE.md` | 수식, 변수, 용어 작성 형식을 통일하기 위함 |
