# predictor_v3 Agent Rules (Lite)
전체 규칙: AGENTS_FULL.md 참조

## 절대 원칙
- Train/Predict 분리: app_train.py ↔ app_predict.py 병합 금지
- core/predictor.py에 optuna/sklearn/shap/matplotlib import 금지
- COLUMNS → core/constants.py, MODEL_REGISTRY → core/models.py 단일 소스 유지
- Commit/Git 정리 시 `AGENT_TASK_ROUTER.md`의 Documentation Sync & Lifecycle Gate를 수행한다.

## 계산기
- numpy/pandas 금지 (순수 Python only)
- calculate_hspf2_v2() / calculate_hspf2() 무단 수정 금지
- UI / ML 코드 수정 금지 / JSON 필드 삭제 금지
- ISO16358 계산기 수정 시 `docs/iso16358/iso16358_dev_notes.md`를 먼저 확인할 것
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

## 출력
- 코드만 출력, 작업 완료 시 [수정 파일] / [변경 내용] / [테스트 결과] 형식 유지

## Token Budget / File Reading Policy

Codex/agent 작업 시 토큰 사용량을 줄이기 위해 대형 파일 전체를 불필요하게 읽지 않는다.

### 기본 원칙

- 코드 수정 작업에서는 먼저 전체 파일을 읽지 않는다.
- `rg`, `grep -n`, `sed -n` 등을 사용해 수정 대상 함수, 클래스, 테스트, 섹션 위치를 먼저 찾는다.
- 위치를 확인한 뒤 필요한 줄 범위만 읽고 수정한다.
- 관련 없는 문서, 긴 guideline, AGENTS_FULL.md, 대형 source file을 습관적으로 열람하지 않는다.
- AGENTS_FULL.md는 사용자가 명시적으로 요청한 경우에만 읽는다.

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