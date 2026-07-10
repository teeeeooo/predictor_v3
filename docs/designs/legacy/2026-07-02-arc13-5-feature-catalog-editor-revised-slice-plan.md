# Arc 13.5 — Feature Catalog Editor 보강 반영 작업 계획서

작성일: 2026-07-02  
대상 repo: `https://github.com/teeeeooo/predictor_v3`  
기준 branch: `main`  
용도: Arc 13.5 Feature Catalog Editor를 Codex/agent에게 slice 단위로 작업시키기 위한 보강 반영 문서

---

## 1. 전체 판단

Arc 13.5 작업 계획은 현재 방향으로 진행해도 된다.

핵심적으로 좋은 점은 다음과 같다.

- `config/ml/features.csv`를 사용자가 Excel/Numbers에서 직접 수정하는 workflow로 보지 않고, Train/Admin surface 안에서 관리하도록 한 점
- `Feature Catalog`를 `TrainShell` top-level tab으로 분리하려는 점
- Export와 Save를 분리한 점
- Read-only viewer를 먼저 만들고, save/edit은 뒤 slice로 미룬 점
- `UI -> Controller -> Application Service -> Core/File Adapter` 흐름으로 boundary를 잡은 점
- `ml_name`, `feature_id`, `role`, `ui_key`, `order`를 초기 edit 대상에서 제외한 점

다만 실제 구현 안정성을 위해 아래 보강 사항을 Arc 13.5 설계 문서와 slice prompt에 반영한다.

---

## 2. 보강 반영 사항 요약

### 2.1 Validation 범위 명확화

Feature Catalog UI에서 표시하는 validation은 다음 두 단계로 구분한다.

| 구분 | 의미 | Slice 1 적용 |
| --- | --- | --- |
| Catalog validation | `features.csv` 자체 schema/row/value 검증 | 필수 |
| Project consistency validation | registry/projection/reference consistency까지 포함한 검증 | clean하게 호출 가능하면 포함, broad import/순환 의존 위험이 있으면 제외 후 report에 남김 |

Slice 1 MVP의 기본 기준은 Catalog validation이다.

Project consistency validation은 기존 validation owner를 clean하게 호출할 수 있는 경우에만 포함한다. 만약 이를 포함하기 위해 broad import, dependency 역류, 순환 의존, Train/Predict runtime side effect가 발생할 가능성이 있으면 Slice 1에서는 제외하고 result report에 명확히 기록한다.

목적은 UI에 `Validation OK`가 표시되었는데 CI의 feature catalog 관련 guard가 실패하는 애매한 상태를 줄이는 것이다.

---

### 2.2 Save 전 DTO 변환 실패 처리 명확화

Slice 3에서 editable table row를 저장할 때, table/service DTO를 `FeatureCatalogRow` 또는 equivalent canonical row로 변환할 수 없는 경우는 validation error로 수집한다.

예시:

- `active = yes`
- `active = 1`
- `zero_fill_policy = allow`
- required field가 비어 있음
- row dict가 required header를 만족하지 못함

처리 원칙:

- 예외를 UI까지 그대로 던지지 않는다.
- validation error message로 표시한다.
- save는 block한다.
- dirty state는 유지한다.
- 사용자가 값을 고치거나 revert/reload할 수 있어야 한다.
- invalid 값을 조용히 coercion하지 않는다.

---

### 2.3 Canonical save safe-write 정책 명확화

Canonical save 대상은 다음 파일 하나다.

- `config/ml/features.csv`

Canonical save 정책:

- UTF-8 without BOM 유지
- `REQUIRED_HEADERS` 순서 유지
- unknown header 추가 금지
- required header 제거 금지
- 가능한 경우 temp file 작성 후 `os.replace` 기반으로 교체
- save 실패 시 기존 `config/ml/features.csv` 보존
- validation 통과 전에는 canonical file write 금지
- save 후 reload + validate 수행
- save 실패 시 dirty state 유지

Export 정책과 구분:

| 동작 | 대상 | Encoding | canonical 변경 여부 |
| --- | --- | --- | --- |
| Export CSV | user-selected path | UTF-8-SIG | 변경 없음 |
| Save | `config/ml/features.csv` | UTF-8 without BOM | validation 통과 시 변경 |

---

### 2.4 GUI test 우선순위 조정

Headless 환경에서 Panel GUI test를 과도하게 요구하지 않는다.

테스트 우선순위는 다음과 같다.

1. Application service test
2. File adapter test
3. Table model test
4. Controller test
5. Panel/Shell test는 기존 Qt headless test pattern이 있을 때만 최소 smoke 수준으로 추가

GUI manual smoke는 수행 가능한 환경에서만 실제 확인한다.

Headless 환경이면 manual smoke를 fake하지 않고 `pending`으로 report에 남긴다.

---

## 3. Arc 13.5 권장 Slice Plan

## Slice 0 — Design Gate / Boundary Audit

### 목적

구현 전에 Arc 13.5 설계와 boundary를 확정한다.

### 할 일

- `Feature Catalog`를 `TrainShell` top-level tab으로 둘지 확정
- UI/controller/service/adapter/core boundary 확정
- Export와 Save 분리 확정
- editable column whitelist 확정
- UTF-8-SIG export policy 확정
- validation 범위를 Catalog validation / Project consistency validation으로 구분
- canonical save safe-write 정책 확정
- `docs/WORK_PLAN.md`의 Arc 13.5 slice plan을 0/1/2/3/4로 갱신
- design gate 문서에 위 결정을 반영
- Slice 0 result report 작성

### 금지

- 코드 구현 금지
- `apps/`, `core/`, `config/ml/features.csv`, tests 수정 금지
- calculator 파일 수정 금지
- report lifecycle cleanup 금지
- push 금지

### 검증

- git diff --check
- git status --short

### Commit

- `docs: finalize arc13.5 feature catalog editor design`

---

## Slice 1 — Read-only Viewer / Validate

### 목적

`app_train.py` 실행 후 Train/Admin window에서 현재 Feature Catalog를 read-only table로 보고 validation 상태를 확인할 수 있게 한다.

### 할 일

- `TrainShell`에 `Feature Catalog` tab 추가
- `FeatureCatalogPanel` 추가
- read-only `FeatureCatalogTableModel` 추가
- `FeatureCatalogController` 추가
- Feature Catalog application service 추가
- 기존 `load_feature_catalog()` 재사용
- 기존 `validate_feature_catalog()` 재사용
- path, row count, active count, validation status, validation messages 표시
- validation display는 Catalog validation을 기본으로 한다
- Project consistency validation은 clean하게 연결 가능할 때만 포함하고, 어렵다면 report에 deferred로 기록

### 금지

- export 구현 금지
- save 구현 금지
- edit 구현 금지
- UI에서 raw CSV parsing/writing 금지
- Train execution behavior 변경 금지
- Predict schema/result behavior 변경 금지
- calculator 파일 수정 금지

### 예상 파일

- `apps/train/ui/shell.py`
- `apps/train/ui/feature_catalog_panel.py`
- `apps/train/ui/models/feature_catalog_table_model.py`
- `apps/train/controllers/feature_catalog_controller.py`
- `apps/train/application/feature_catalog/__init__.py`
- `apps/train/application/feature_catalog/models.py`
- `apps/train/application/feature_catalog/service.py`
- focused tests
- result report

### 검증

- python3 -B -m compileall -q apps/train core/ml tests
- focused feature catalog service/controller/table model tests
- relevant shell/panel test if existing Qt headless pattern supports it
- python3 -B tools/check_code_structure.py
- git diff --check
- git status --short

### Commit

- `feat: add feature catalog viewer tab`

---

## Slice 2 — Excel-safe Export

### 목적

Feature Catalog를 Excel/Numbers 검토와 공유 목적으로 CSV export할 수 있게 한다.

### 할 일

- Feature Catalog panel에 Export CSV button 추가
- export service/usecase 추가
- file adapter에서 CSV write 담당
- UTF-8-SIG export 적용
- export는 current table state 기준으로 수행
- Slice 2에서는 table이 read-only이므로 current table state는 loaded catalog와 동일
- export 결과에 현재 validation 상태를 함께 status/report에 표시

### 금지

- canonical `config/ml/features.csv` 변경 금지
- save 구현 금지
- edit 구현 금지
- UI에서 `csv` 직접 import 금지
- UI에서 file write 직접 수행 금지

### 예상 파일

- `apps/train/ui/feature_catalog_panel.py`
- `apps/train/controllers/feature_catalog_controller.py`
- `apps/train/application/feature_catalog/service.py`
- `apps/train/application/feature_catalog/models.py`
- `apps/train/adapters/feature_catalog_file_adapter.py`
- focused tests
- result report

### 검증

- python3 -B -m compileall -q apps/train core/ml tests
- focused export adapter/service tests
- focused controller/panel tests if practical
- python3 -B tools/check_code_structure.py
- git diff --check
- git status --short

### Commit

- `feat: add feature catalog excel-safe export`

---

## Slice 3 — Editable Table / Save with Validation

### 목적

허용된 column만 안전하게 수정하고, validation 통과 시에만 canonical `config/ml/features.csv`에 저장할 수 있게 한다.

### Editable whitelist

- `label`
- `notes`
- `active`
- `zero_fill_policy`
- `source`
- `mapping_key`
- `one_hot_group`

### Locked columns

- `order`
- `feature_id`
- `ml_name`
- `role`
- `ui_key`

### 할 일

- table model에서 editable whitelist만 edit 가능하게 처리
- dirty state 추적
- Save button 활성/비활성 처리
- Revert 또는 Reload workflow 추가
- save 전 full validation 수행
- edited row를 canonical row로 변환할 수 없는 경우 validation error로 수집
- validation error가 있으면 save block
- canonical save는 temp file + replace 방식으로 구현 가능한지 확인 후 적용
- save 후 reload + validate 수행
- save 실패 시 dirty state 유지

### enum/edit 처리

`active`는 strict value만 허용한다.

- `true`
- `false`

`zero_fill_policy`는 allowed value만 허용한다.

- `disallow`
- `mode_missing_allowed`

`mode_missing_allowed`는 기존 validation rule에 따라 허용 feature에만 사용할 수 있어야 한다.

현재 허용 대상:

- `Cooling Capa`
- `Cooling Power`
- `Heating Capa`
- `Heating Power`

### 금지

- `ml_name`, `role`, `feature_id`, `ui_key`, `order` edit 허용 금지
- row add/delete 금지
- invalid value silent coercion 금지
- validation 실패 상태에서 save 금지
- save 실패 시 canonical file truncate 위험 방치 금지
- Train runtime algorithm 변경 금지
- Predict schema/result behavior 변경 금지
- calculator 파일 수정 금지

### 예상 파일

- `apps/train/ui/feature_catalog_panel.py`
- `apps/train/ui/models/feature_catalog_table_model.py`
- `apps/train/controllers/feature_catalog_controller.py`
- `apps/train/application/feature_catalog/service.py`
- `apps/train/application/feature_catalog/models.py`
- `apps/train/adapters/feature_catalog_file_adapter.py`
- focused tests
- result report

### 검증

- python3 -B -m compileall -q apps/train core/ml tests
- focused table model edit/save tests
- focused controller/service/adapter tests
- python3 -B -m pytest tests/test_ml_feature_catalog.py
- python3 -B tools/check_code_structure.py
- git diff --check
- git status --short

### Commit

- `feat: add feature catalog editable save workflow`

---

## Slice 4 — Closeout / Docs Sync / Final Push

### 목적

Arc 13.5를 closeout하고 Arc 14 real dataset readiness audit로 넘어갈 수 있는 상태를 만든다.

### 할 일

- final focused validation 실행
- `docs/WORK_PLAN.md` next action을 Arc 14 real dataset readiness audit로 변경, 단 blocker 있으면 보류
- 필요 시 `project_brief.md` 업데이트
- Arc 13.5 완료 또는 major decision 변경 시 `project_log.md` 상단 entry 추가
- final closeout report 작성
- 각 slice commit 확인
- manual smoke 가능 여부 기록
- 모든 검증 OK 후 push

### 금지

- report lifecycle cleanup 금지
- unresolved blocker가 있는데 완료 처리 금지
- headless 환경에서 GUI manual smoke를 수행한 것처럼 기록 금지
- calculator 파일 수정 금지
- unrelated refactor 금지

### Final verification

- python3 -B -m compileall -q apps/train core/ml tests
- focused Arc 13.5 tests
- python3 -B -m pytest tests/test_ml_feature_catalog.py
- relevant tests/test_apps_train_shell.py
- relevant tests/test_apps_train_controller.py only if impacted
- python3 -B tools/check_code_structure.py
- git diff --check
- git status --short

### Manual smoke checklist

GUI 사용 가능 시에만 실제 확인한다.

1. `python app_train.py` 실행
2. `Feature Catalog` tab 표시 확인
3. table load 확인
4. row count / active count 표시 확인
5. validation status 표시 확인
6. CSV export 후 Excel/Numbers에서 한글 label 가독성 확인
7. 허용 field edit 후 dirty state 확인
8. invalid enum edit 시 save block 또는 validation error 확인
9. valid edit save 후 reload 및 persistence 확인
10. Predict / Train / Data Mapping tab이 기존처럼 열리는지 확인

Headless 환경이면 manual smoke는 pending으로 보고한다.

### Commit / Push

Commit:

- `docs: close arc13.5 feature catalog editor`

Push:

- `git push`

---

## 4. Stop Conditions

아래 상황이 발생하면 구현을 멈추고 사용자에게 보고한다.

1. Viewer 구현에 `config/ml/features.csv` schema 변경이 필요하다.
2. Save 구현에 `core/ml` projection semantics 변경이 필요하다.
3. UI가 raw CSV parsing/writing을 직접 소유해야만 구현 가능해 보인다.
4. `ml_name`, `role`, `feature_id`, `ui_key`, `order`, row add/delete가 필요해 보인다.
5. Save를 safe-write로 만들 수 없어 canonical file truncate 위험이 있다.
6. `load_feature_catalog()`가 현재 canonical file을 load하지 못한다.
7. 기존 `tests/test_ml_feature_catalog.py`가 실패한다.
8. Train execution behavior가 side effect로 바뀐다.
9. Predict schema/result behavior가 side effect로 바뀐다.
10. Calculator 파일 수정이 필요해 보인다.
11. 새 파일 하나가 View, Controller, Application Service, File I/O, validation policy를 모두 소유하는 형태로 커진다.
12. Structure guard가 변경 파일에서 신규 architecture warning을 보고한다.
13. Project consistency validation을 붙이기 위해 dependency direction이 깨진다.

---

## 5. Slice 0용 Codex/Agent Prompt 초안

[PROMPT START]

AGENTS.md는 현재 세션에서 이미 확인했다면 다시 읽지 않는다.  
AGENT_TASK_ROUTER.md는 이번 작업 유형에 필요한 섹션만 확인한다.

[작업]
Arc 13.5 — Feature Catalog Editor  
Slice 0 — Design Gate / Boundary Audit

[우선 읽기]

1. docs/WORK_PLAN.md
2. project_log.md 최신 상단 2~3개 entry
3. docs/designs/2026-07-01-arc13-5-feature-catalog-editor-design-gate.md
4. docs/designs/README.md
5. docs/workflows/ml_feature_catalog_workflow.md
6. core/ml/feature_catalog.py
7. core/ml/feature_catalog_validation.py
8. core/ml/feature_catalog_projection.py
9. apps/train/ui/shell.py
10. apps/train/ui/train_model_panel.py
11. apps/train/ui/data_mapping_panel.py
12. apps/train/ui/models/static_table_model.py

[목적]

Arc 13.5 구현 전 설계와 boundary를 문서로 확정한다.  
이번 slice는 code implementation이 아니라 design gate 정리만 수행한다.

[수정 허용]

- docs/designs/2026-07-01-arc13-5-feature-catalog-editor-design-gate.md
- docs/WORK_PLAN.md
- docs/designs/README.md
- result_reports/active/<slice0_report>.md

[금지]

- apps/ 수정 금지
- core/ 수정 금지
- config/ml/features.csv 수정 금지
- tests 수정 금지
- calculator 파일 수정 금지
- ML algorithm 변경 금지
- Train runtime algorithm 변경 금지
- Predict schema/result behavior 변경 금지
- report lifecycle cleanup 금지
- unrelated refactor 금지
- push 금지

[반영할 설계 결정]

- Feature Catalog는 TrainShell top-level tab으로 둔다.
- UI는 raw CSV parsing/writing을 직접 소유하지 않는다.
- UI event는 controller를 통해 application service로 전달한다.
- catalog load/validate는 기존 core/ml owner를 재사용한다.
- CSV export/save는 file adapter/service가 담당한다.
- Export와 Save는 분리한다.
- Excel-safe export는 UTF-8-SIG를 기본으로 한다.
- canonical save는 UTF-8 without BOM을 유지한다.
- canonical save는 validation 통과 후 config/ml/features.csv에만 수행한다.
- canonical save는 가능한 경우 temp file + os.replace 방식으로 안전하게 수행한다.
- save 후 reload + validate를 수행한다.
- validation display는 Catalog validation과 Project consistency validation을 구분한다.
- Slice 1 MVP는 Catalog validation을 기본으로 한다.
- Project consistency validation은 clean하게 호출 가능할 때만 포함하고, dependency 위험이 있으면 deferred로 report에 남긴다.
- Slice 3에서 DTO -> canonical row 변환 실패는 validation error로 수집하고 save를 block한다.
- editable whitelist는 label, notes, active, zero_fill_policy, source, mapping_key, one_hot_group이다.
- locked columns는 order, feature_id, ml_name, role, ui_key이다.
- ml_name, role, feature_id, ui_key, order edit 또는 row add/delete가 필요하면 stop/report한다.
- GUI panel test는 기존 Qt headless pattern이 있을 때만 최소 smoke로 추가하고, service/adapter/table model/controller test를 우선한다.
- headless 환경에서는 manual GUI smoke를 pending으로 보고한다.

[작업 항목]

task 1

- 목적: Arc 13.5 design gate 문서를 최종 구현 방향에 맞게 갱신한다.
- 수정 대상: docs/designs/2026-07-01-arc13-5-feature-catalog-editor-design-gate.md
- 할 일: slice plan 0/1/2/3/4, boundary, validation scope, export/save 정책, editable whitelist, safe-write, stop conditions를 반영한다.
- 주의 사항: code implementation 지시로 확장하지 않는다.

task 2

- 목적: WORK_PLAN next action을 Arc 13.5 재분할안에 맞게 정리한다.
- 수정 대상: docs/WORK_PLAN.md
- 할 일: 다음 action을 Slice 1 Viewer/Validate, Slice 2 Export, Slice 3 Editable/Save, Slice 4 Closeout, 이후 Arc 14 순서로 정리한다.
- 주의 사항: Arc 14 작업 내용은 시작하지 않는다.

task 3

- 목적: design index가 있으면 Arc 13.5 design gate 상태를 최신화한다.
- 수정 대상: docs/designs/README.md
- 할 일: 필요한 경우에만 index/status를 갱신한다.
- 주의 사항: 불필요하면 수정하지 않는다.

task 4

- 목적: Slice 0 결과 report를 남긴다.
- 수정 대상: result_reports/active/<slice0_report>.md
- 할 일: 목표, 수정 파일, 결정 사항, 검증 결과, 제외 범위, next action을 compact하게 기록한다.
- 주의 사항: report lifecycle cleanup은 하지 않는다.

[검증]

- git diff --check
- git status --short

[결과 보고 형식]

task 1: OK/NG - short summary  
task 2: OK/NG - short summary  
task 3: OK/NG - short summary  
task 4: OK/NG - short summary  
modified: ...  
report: result_reports/active/<slice0_report>.md  
commit: <hash or none>  
push: none

[PROMPT END]

---

## 6. Completion Definition

Arc 13.5 완료 조건은 다음과 같다.

- `app_train.py` 실행 시 TrainShell에 `Feature Catalog` tab이 있다.
- Feature Catalog table이 current `config/ml/features.csv`를 표시한다.
- row count / active count가 표시된다.
- validation status와 validation messages가 표시된다.
- validation scope가 Catalog validation / Project consistency validation으로 구분되어 있다.
- Excel-safe UTF-8-SIG export가 가능하다.
- Export는 canonical file을 변경하지 않는다.
- 허용된 column edit이 가능하다.
- locked column은 edit할 수 없다.
- invalid enum/input은 reject되거나 validation error로 표시된다.
- Save는 validation 통과 후에만 canonical `config/ml/features.csv`에 반영된다.
- Save는 safe-write 정책을 따른다.
- Save 후 reload/validate가 수행된다.
- 기존 core/ml feature catalog tests가 통과한다.
- Train execution behavior는 변경되지 않는다.
- Predict schema/result behavior는 변경되지 않는다.
- Calculator files are untouched.
- 각 slice는 commit되어 있다.
- Slice 4 closeout 후 push가 완료되어 있다.
