# Report 337: Batch Foundation Foldering Audit

## Goal (목표)

- `ui_tk/` root 폴더에 남아 있는 batch foundation 파일들의 구조적 위상을 점검하고, Clean Architecture 및 관심사 분리(SoC) 원칙을 준수하는 최적의 폴더링(foldering) 설계안을 도출하여 향후 다수 프로파일 확장 시의 import 혼선과 구조 중복을 방지한다.
- 본 작업은 실제 코드나 파일 이동 없이 진행되는 audit/report 전용 태스크이다.

## 확인한 기준 문서 (Confirmed Standards/Guidelines)

1. **AGENT_TASK_ROUTER.md (Coding / UI-Tk / Result Report Workflow)**: UI 구조 변경 및 리팩토링 시의 clean architecture 경계 및 report 작성 규칙 준수 확인.
2. **docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md (clean architecture 경계)**: View (위젯 구성), Controller (재계산 연산 제어), Model (spec/specifications 및 데이터 저장)의 명확한 책임을 재확인.
3. **docs/agent_workflows/UI_SURFACE_WORKFLOW.md (UI surface gates)**: table scroll, wheel routing, paste/copy, selection 등 table surface 및 dialog lifecycle/geometry 관리 기준 확인.
4. **docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md (spreadsheet contract)**: 2D editable grid의 toolkit-agnostic UX 요구 사양 및 baseline 검증 기준 확인.
5. **docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md (input matrix rules)**: 입력 matrix 및 result surface의 레이아웃 규칙 및 분리 사양 확인.
6. **docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md (geometry policy)**: dialog lifecycle, hidden-first geometry 적용 원칙 확인.
7. **docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md (tkinter table adapter)**: Tk Table surface가 구현해야 하는 interaction 및 surface mapping 기준 확인.

## Reference Evidence 요약

- **262 Main Table Migration (archive)**: `ExcelLikeTableController` 폐기 방향 및 table grid model/compatibility wrapper들의 cleanup timing 분류 기준 획득.
- **274 ui_tk Cleanup Preflight (archive)**: View + adapter hybrid hotspot 분석을 통한 view/adapter 관심사 격리 및 detail panel init/draw split defer 기준 획득.
- **334 Summary (summary)**: `BatchDialogShell` (dialog/shell lifecycle 전용)과 `profiles/` (profile-specific thin adapters)의 캡슐화 완성 및 legacy controller retirement 히스토리 파악.
- **335/336 Reports (active)**: active report count wording policy 및 threshold wording 규칙 준수.

## ui_tk Root Batch Foundation Inventory & Classification

`ui_tk/` root에 잔존하는 batch 관련 파일 8개에 대해, 역할 및 Clean Architecture 책임을 기준으로 다음과 같이 분류하였다:

1. **ui_tk/batch_case_table.py (362 LOC)**
   - *Responsibility*: **table view / widget construction**
   - *Role*: row-per-case 방식의 GUI table grid 및 frame 레이아웃 구성.
2. **ui_tk/batch_matrix_table.py (422 LOC)**
   - *Responsibility*: **table view / widget construction**
   - *Role*: two-row matrix 방식의 GUI table grid 및 frame 레이아웃 구성.
3. **ui_tk/batch_table_viewport.py (142 LOC)**
   - *Responsibility*: **table view / widget construction**
   - *Role*: scrollable canvas를 적용한 batch table Vertical scrolling viewport helper.
4. **ui_tk/batch_controller.py (55 LOC)**
   - *Responsibility*: **table controller / interaction**
   - *Role*: batch table의 행 단위 recalculation 및 result mapping을 제어하는 domain controller.
5. **ui_tk/batch_table_controller.py (9 LOC)**
   - *Responsibility*: **legacy compatibility wrapper** (deprecated candidate)
   - *Role*: common `TkTableController`를 상속받은 batch-specific wrapper.
6. **ui_tk/batch_table.py (69 LOC)**
   - *Responsibility*: **legacy compatibility wrapper**
   - *Role*: old batch interface 호환을 위한 `ui_tk/table/interaction_core.py` 함수 및 클래스 export.
7. **ui_tk/batch_models.py (106 LOC)**
   - *Responsibility*: **matrix model / spec / DTO**
   - *Role*: row-per-case table의 column spec, profile spec, table data model 정의.
8. **ui_tk/batch_matrix_models.py (296 LOC)**
   - *Responsibility*: **matrix model / spec / DTO**
   - *Role*: 두 줄 매트릭스(two-row matrix) table의 spec, cell descriptor, matrix data model 정의.

---

## Candidate Structures 비교

### Candidate A: `ui_tk/batch/` 패키지로 batch foundation 통합 (권장)
- **구조**:
  - `ui_tk/batch/case_table.py` (from `batch_case_table.py`)
  - `ui_tk/batch/matrix_table.py` (from `batch_matrix_table.py`)
  - `ui_tk/batch/viewport.py` (from `batch_table_viewport.py`)
  - `ui_tk/batch/controller.py` (from `batch_controller.py`)
  - `ui_tk/batch/models.py` (from `batch_models.py`)
  - `ui_tk/batch/matrix_models.py` (from `batch_matrix_models.py`)
  - `ui_tk/batch/compat_table.py` (or shims in `__init__.py`)
- **판단**:
  - *root pollution 감소*: 우수 (8개 파일이 root에서 제거됨).
  - *batch foundation owner 명확성*: 우수 (batch-related widget, model, controller가 하나의 패키지로 격리됨).
  - *import churn*: 보통 (sections, dialog profiles, tests 등의 import 경로 수정 필요).
  - *기존 batch_dialogs와의 boundary*: 우수 (dialog/shell lifecycle은 `ui_tk/batch_dialogs/`에 두고, Widget/Model foundation은 `ui_tk/batch/`에 두어 관심사 격리 유지).
  - *future profile expansion 적합성*: 우수 (새로운 EN/AHRI/KS profile이 root가 아닌 `ui_tk/batch/...`에서 widget/model을 깔끔하게 임포트하여 사용).

### Candidate B: `ui_tk/table/batch/` 로 table foundation만 이동
- **구조**: `ui_tk/table/batch/` 아래에 `case_table.py`, `matrix_table.py` 등 table widgets만 배치하고, model/spec은 root 또는 별도 폴더에 둠.
- **판단**:
  - *table controller common foundation과 가깝지만*, `ui_tk/table/`은 generic table interaction core logic (clipboard, roles, selection)을 담당하는 core-level package이므로, batch-specific 레이아웃 위젯과 비즈니스용 models가 들어오면 responsibilities가 혼재되어 boundary가 오염됨.

### Candidate C: 현재 root 유지 + naming/index만 보강
- **판단**:
  - *import churn*은 발생하지 않으나, `ui_tk/` root pollution이 유지되어 향후 EN/AHRI/KS batch profile 확장 시 root 파일 수 과다 및 standard widgets/models 임포트 시 혼선이 가중됨.

---

## 권장 구조 및 판단

- **선택**: **Candidate A (ui_tk/batch/ 패키지로 batch foundation 통합)**
- **이유**:
  - **관심사 분리(SoC)**: generic batch table foundation (views, viewports, models)을 dialog window lifecycle shells (`ui_tk/batch_dialogs/`) 및 low-level table interaction core (`ui_tk/table/`)와 완전 격리함.
  - **확장성**: 향후 profile 확장 시 root pollution 없이 `ui_tk/batch` 하위 패키지를 단일 소스로 사용하여 widgets 및 models를 재사용할 수 있음.
  - **단순성**: 무리한 abstract base class나 plugin registry architecture를 피하고 단순 파일 이주 및 패키지화로 구성하므로 regression 리스크가 가장 낮음.
- **상태**: **Implementation-ready (구현 준비 완료)**.

---

## Proposed Implementation Slices (구현 슬라이스 계획)

실제 구현 시 발생할 수 있는 리스크를 차단하고 검증을 고도화하기 위해 아래와 같이 2개의 단계적 구현 슬라이스로 나누어 진행할 것을 제안한다.

### Slice 1: Move model and spec files into `ui_tk/batch/`
- **목표**: toolkit-neutral model 및 spec 관련 파일 이주.
- **수정 대상**:
  - 신규 생성: `ui_tk/batch/models.py`, `ui_tk/batch/matrix_models.py`, `ui_tk/batch/__init__.py`
  - 제거 대상: `ui_tk/batch_models.py`, `ui_tk/batch_matrix_models.py`
  - import 수정: `ui_tk/batch_case_table.py`, `ui_tk/batch_matrix_table.py`, sections, batch dialog profiles (`iso_iseer_2point.py`, `saso_t3.py`, `hong_kong_cspf.py`), 관련 test 파일들.
- **금지 대상**: table widgets, viewport, controllers 등 다른 파일의 이동 및 수정 금지.
- **검증 명령**:
  - `python3 -B tools/check_code_structure.py`
  - `pytest tests/test_ui_tk_batch_models.py tests/test_ui_tk_batch_matrix_models.py`
- **Rollback Risk & Mitigations**:
  - *Risk*: import path 누락으로 인한 Tcl/Tk loading failure.
  - *Mitigation*: compatibility shim 대신 전체 import path를 원스텝으로 일괄 교정하고 focused unit tests 실행.

### Slice 2: Move table view, viewport, and controllers into `ui_tk/batch/`
- **목표**: table widgets, viewport, controller foundation 이주 완료 및 root cleanup.
- **수정 대상**:
  - 신규 생성: `ui_tk/batch/case_table.py`, `ui_tk/batch/matrix_table.py`, `ui_tk/batch/viewport.py`, `ui_tk/batch/controller.py`, `ui_tk/batch/table_controller.py`, `ui_tk/batch/compat_table.py`
  - 제거 대상: `ui_tk/` root 내 batch 관련 6개 파일.
  - import 수정: sections, batch dialog profiles, 관련 test 파일들.
- **금지 대상**: `ui_tk/batch_dialogs/` 및 `ui_tk/table/` core 파일 변경 금지.
- **검증 명령**:
  - `python3 -B tools/check_code_structure.py`
  - `pytest` (전체 테스트 실행 및 regression 방어)
  - `git diff --check`
- **Reference Map Sync**: Slice 2 완료 후 최종 검증 단계에서 `CODEBASE_REFERENCE_MAP.md`를 재생성하여 구조 변경을 명문화함.

---

## WORK_PLAN 업데이트 여부

- `docs/WORK_PLAN.md`에 batch foundation foldering audit 완료 및 다음 implementation slice (Slice 1) 등록을 위해 compact하게 업데이트할 것을 제안함.
- `project_log.md` 및 `project_memory_seed.md`는 수정하지 않음.

## 제외 범위 (Excluded Scope)

- production Python source (`.py`), tests, ui_tk, calculator/core, ML predictor 로직 실제 수정 없음.
- 파일 이동/rename 및 import 경로 수정 실제 수행 없음.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 재생성 없음.
- `project_log.md` 및 `result_reports/memory/project_memory_seed.md` 실제 수정 금지.

## 검증 결과 (Verification Results)

- `python3 -B tools/check_code_structure.py` 통과 (OK)
- `git status --short` 확인 결과 허용된 audit report 파일 외의 diff 없음 확인 (OK)
- `git diff --check` 상의 whitespace 문제 없음 (OK)

## Next Action suggested (차기 과제)
1. **Batch foundation foldering implementation - Slice 1**
