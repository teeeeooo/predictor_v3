# predictor_v3 Agent Rules

본 문서는 실무 작업을 수행하는 에이전트가 매 세션 시작 시 반드시 준수해야 할 **Active Working Rules**다.
상세한 설계 근거(Rationale)나 역사적 배경은 archived detailed reference인 `docs/archive/AGENTS_FULL.md`를 참조하되, 사용자의 명시적 요청이 있거나 고위험 작업에서 상세 맥락 파악이 필요한 경우에만 제한적으로 확인한다.

## 절대 원칙
- Train/Predict 분리: app_train.py ↔ app_predict.py 병합 금지
- core/predictor.py에 optuna/sklearn/shap/matplotlib import 금지
- COLUMNS → core/constants.py, MODEL_REGISTRY → core/models.py 단일 소스 유지
- Commit/Git 정리 시 `AGENT_TASK_ROUTER.md`의 Documentation Sync & Lifecycle Gate를 수행한다.
- Architecture/resolver/adapter/routing/schema/guard-test decision은 작은 diff라도 `AGENT_TASK_ROUTER.md` 기준에 따라 `project_log.md` 갱신 여부를 판단한다.
- 새 로그를 append하기 전 최근 2~3개 로그와 merge 가능한 관련 작업인지 먼저 판단한다.

## 계산기
- numpy/pandas 금지 (순수 Python only)
- calculate_hspf2_v2() / calculate_hspf2() 무단 수정 금지
- UI / ML 코드 수정 금지 / JSON 필드 삭제 금지
- ISO16358 계산기 수정 시 `docs/iso16358/iso16358_dev_notes.md`를 먼저 확인할 것
- ISO16358-2 HSPF Excel reference 추출/해석/runner input-output 작업에서 사용자가 Excel COM, pywin32 runner, 회사 PC Excel, AS/NZS Energy Rating SEER calculator, original workbook reference, chat_packet, full_dump, case 3~8 Excel 기준값 추출을 언급하면 `docs/iso16358/excel_com_runner_packet_protocol.md`를 확인한다. 이 문서는 일반 계산 로직 수정, UI 작업, AHRI/EN/KS 작업에서는 읽지 않는다.
- Excel COM packet 작업 역할: ChatGPT는 runner input packet 설계와 chat_packet 해석, Company PC runner는 original Excel COM 계산/full_dump 저장/chat_packet 생성, Codex는 repo 수정/테스트/diff 확인, User는 회사 PC 실행 후 chat_packet만 전달.
- KS C 9306 관련 수정 시 `docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md`와 `docs/iso16358/regions/ks_c_9306/ks_c_9306_notes.md`를 먼저 확인할 것
- ISO16358/KS C 9306 공통 엔진 파일명은 `core/calculator_iso16358.py`를 기준으로 할 것
- data/region_configs/*.json 수정 전 `data/region_configs/REGION_CONFIG_RULES.md`를 확인할 것.
- 계산기 Phase 1에서는 검증 완료 profile만 UI/배포 대상으로 삼고, SASO T3 및 ISO16358 optional matrix는 REFACTOR_PLAN의 Phase R1/R2 지시에 따를 것.
- production region config에 golden/sample/test 전용 값을 넣지 말 것.
- docs 폴더 내에 *_notes.md 수정 또는 생성 전 `docs/DOCS_GUIDELINES.md`, `docs/STANDARD_DOC_TEMPLATE.md`를 확인할 것.

## ML
- model.fit()에 .values 변환 금지 (feature_names_in_ 보존)
- Cooling / Heating 완전 독립 모델 유지 (MultiOutput 금지)
- 물리 제약 > 통계 수치 (단조 제약 Monotone Constraints 유지)

## UI
- QTableWidget 금지 → QTableView + QAbstractTableModel만 허용
- setCellWidget 금지 → QStyledItemDelegate만 허용
- blockSignals는 반드시 try/finally로 감쌀 것

## 수정 범위
- 지정된 파일/함수만 수정, 관련 없는 코드 수정 금지
- 함수명/JSON key 변경 금지
- 구조 개선 및 리팩토링 예정 사항은 `docs/REFACTOR_PLAN.md`를 참조하라. 명시적인 지시가 없는 한 절대로 먼저 리팩토링을 수행하지 마라.
- routing/schema/architecture-sensitive 변경은 `AGENT_TASK_ROUTER.md`를 먼저 따른다.
- router가 지시하는 경우에만 `docs/architecture/project_architecture.md`의 관련 섹션을 확인한다.
- region config, HW candidate input, ML feature schema, calculator result schema를 섞지 않는다.

## 출력
- 작업 완료 시 상세 결과는 터미널에 길게 출력하지 않고 `result_reports/active/` 아래 Markdown report에 기록한다.
- report 파일명은 `NNN_verb-target-scope.md` 형식을 사용한다 (예: `001_review-iso-hspf-routing.md`).
- 터미널 출력은 task별 `OK/NG` 한 줄 요약과 report path만 남긴다. 문제가 있거나 blocked이면 원인을 짧게 덧붙인다.
- report 파일은 작업 산출물이므로 항상 stage/commit/push한다.
- 코드/문서 변경 커밋과 report 커밋은 가능하면 분리한다.
- 세부 규칙은 `AGENT_TASK_ROUTER.md`의 Result Report Workflow를 따른다.

## Agent Work Discipline

- 새 Codex/agent 세션을 시작하거나 작업 맥락이 불명확하면 `project_brief.md`를 먼저 확인한다.
- 작업 전 Goal / Scope / Non-goals / Verification을 확인한다.
- 요청 범위를 넘는 추상화, 리팩토링, formatting/comment/import 정리를 하지 않는다.
- 불확실한 규격/fixture/case/region 해석은 임의 결정하지 않는다.
- 완료 보고에는 변경 파일, 변경 이유, 검증, 남은 위험을 포함한다.

## Token Budget / File Reading Policy

Codex/agent 작업 시 토큰 사용량을 줄이기 위해 대형 파일 전체를 불필요하게 읽지 않는다.

### 기본 원칙

- 코드 수정 작업에서는 먼저 전체 파일을 읽지 않는다.
- `rg`, `grep -n`, `sed -n` 등을 사용해 수정 대상 함수, 클래스, 테스트, 섹션 위치를 먼저 찾는다.
- 위치를 확인한 뒤 필요한 줄 범위만 읽고 수정한다.
- 관련 없는 문서, 긴 guideline, `docs/archive/AGENTS_FULL.md`, 대형 source file을 습관적으로 열람하지 않는다.
- `docs/iso16358/excel_com_runner_packet_protocol.md`도 조건부 문서다. 이미 확인한 세션에서는 전체를 반복해서 읽지 말고 필요한 heading만 `rg`/`sed`로 확인한다.
- `docs/archive/AGENTS_FULL.md`는 사용자가 명시적으로 요청한 경우에만 읽는다.

### 예외

다음 경우에는 전체 파일 또는 문서 전체 검토를 허용한다.

- 파일이 짧아서 전체를 읽어도 토큰 부담이 거의 없는 경우
- 문서 리팩토링처럼 문서 전체 구조와 중복 확인이 작업 대상인 경우
- 구조 파악 없이는 안전한 수정이 어려운 경우
- 사용자가 명시적으로 전체 검토를 요청한 경우

### 권장 절차

1. `rg`/`grep`으로 대상 위치 검색
2. `sed -n`으로 필요한 범위만 읽기
3. 최소 범위 수정
4. 관련 테스트만 먼저 실행
5. 필요 시 전체 테스트 실행

예시:

```bash
rg -n "def calculate_cspf|class ISO16358Calculator" core/calculator_iso16358.py
sed -n '120,260p' core/calculator_iso16358.py
```

## Task Router

작업자는 작업 시작 전에 아래 유형 중 하나로 작업을 분류한다.
상세 내용은 필요시 AGENT_TASK_ROUTER.md를 참고한다.

- 기본 작업 시작 시 `AGENTS.md`만 필수로 읽는다.
- 작업 유형별 세부 절차가 필요하거나, Commit/Git 정리, Notes 정리/문서 리팩토링, Logic 수정, 테스트 추가 작업을 수행할 때는 `AGENT_TASK_ROUTER.md`의 해당 항목만 확인한다.

- Commit/Git 정리
- Logic 수정
- Smoke/Golden/Validation test 추가
- 단순 docs 문구 수정
- Notes 정리 / 문서 리팩토링
- UI 수정
- ML/Predictor 수정

작업 유형에 맞는 문서만 읽고, 관련 없는 긴 문서를 열람하지 않는다.
대형 파일은 먼저 `rg`/`grep`으로 위치를 찾고 필요한 범위만 `sed -n`으로 읽는다.

Logic 수정 시에는 지역별 하드코딩을 먼저 하지 않는다.
공통 엔진, profile/config, handler 구조로 표현 가능한지 먼저 확인한다.
단순 docs 문구 수정은 지정된 파일/문장만 수정하고, 검색·테스트·주변 문서 검토를 하지 않는다.

## Design Gate Rule

predictor_v3에서는 “먼저 구현하고 나중에 공통화”하는 흐름을 피한다.  
새 작업이 공통 구조와 특화 구조의 경계를 건드릴 가능성이 있으면, 구현 전에 `grill-me` skill로 Design Gate를 통과한다.

기본 원칙은 다음과 같다.

- global standard logic은 canonical core에 먼저 정의한다.
- country/region-specific behavior는 명시적인 handler, adapter, config override, profile branch로 분리한다.
- national variant가 global/common path를 암묵적으로 변경해서는 안 된다.
- UI는 계산기 내부 구현이 아니라 canonical input/output 계약에 의존해야 한다.
- public API 변경은 사용자의 명시 승인 없이는 하지 않는다.
- 테스트는 common behavior와 regional override behavior를 구분해야 한다.

Design Gate 결과는 `docs/designs/` 아래에 기록하거나, 최소한 Codex 구현 프롬프트 안에 포함한다.

Design Gate Summary가 없거나 사용자가 명시적으로 생략을 승인하지 않은 상태에서는 구현을 시작하지 않는다.
