# 319 ui_tk batch dialog folder boundary audit

## Goal

- ISO 2-point 및 SASO T3에 batch dialog를 확장하기 전에 ui_tk 내부 batch dialog 관련 파일의 적절한 폴더 boundary를 먼저 정하고, next implementation slice를 제안하여 향후 구현 시의 import churn 및 file 구조 중복을 방지한다.

## Audit Scope (확인한 범위)

- `ui_tk/sections/hong_kong_cspf_batch_section.py` (Hong Kong CSPF batch dialog 및 section)
- `ui_tk/sections/hong_kong_cspf_section.py` (batch dialog 호출처)
- `ui_tk/sections/iso_iseer_2point_section.py` (batch dialog 미도입 상태 확인)
- `ui_tk/sections/iso_saso_t3_section.py` (batch dialog 미도입 상태 확인)
- `ui_tk/batch_case_table.py` (row-per-case table foundation)
- `ui_tk/batch_matrix_table.py` (two-row matrix table foundation)
- `ui_tk/batch_controller.py` (row-per-case controller foundation)
- `ui_tk/batch_matrix_models.py` (matrix model/spec foundation)
- `ui_tk/batch_models.py` (case table model/spec foundation)
- `tests/test_ui_tk_iso_table_autocalc.py` (batch dialog 관련 테스트 suite)

## Current ui_tk batch/dialog Inventory

현재 `ui_tk` 내의 batch dialog 및 batch table foundation 파일 목록과 그 분류는 다음과 같습니다:

1. **Batch Dialog (Toplevel Shell Wrapper)**:
   - `HongKongCspfBatchDialog` (in `ui_tk/sections/hong_kong_cspf_batch_section.py`)
2. **Batch Section (UI Widget & Controller Adapter)**:
   - `HongKongCspfBatchSection` (in `ui_tk/sections/hong_kong_cspf_batch_section.py`)
   - `HongKongCspfMatrixController` (in `ui_tk/sections/hong_kong_cspf_batch_section.py`)
3. **Batch Table Foundation (Reusable presentation & logic)**:
   - `BatchMatrixTable` (in `ui_tk/batch_matrix_table.py`)
   - `BatchCaseTable` (in `ui_tk/batch_case_table.py`)
   - `BatchTableViewport` (in `ui_tk/batch_table_viewport.py`)
   - `BatchTableController` (in `ui_tk/batch_table_controller.py`)
   - `BatchCalculationController` (in `ui_tk/batch_controller.py`)
   - `HONG_KONG_CSPF_MATRIX_SPEC`, `BatchMatrixSpec` (in `ui_tk/batch_matrix_models.py`)
   - `BatchRowState`, `BatchColumnRole`, `BatchProfileSpec`, `BatchTableModel` (in `ui_tk/batch_models.py`)

## Hong Kong CSPF Batch Dialog Owner Analysis

- **호출 및 Lifecycle**:
  `HongKongCspfSection`이 `_open_batch_dialog()`를 통해 `HongKongCspfBatchDialog`를 인스턴스화하여 `Toplevel` 창을 열고, 내부 state `self._batch_snapshot`에 데이터 행 목록(snapshot)을 보관합니다.
- **Snapshot Persistence**:
  대화상자가 닫힐 때 `on_close` 콜백(`_clear_batch_dialog`)이 트리거되어 최신 데이터 snapshot을 탭의 수명 주기와 함께 유지합니다.
- **Dialog vs Section**:
  `hong_kong_cspf_batch_section.py` 파일명은 "section"이지만, 실제 창을 띄우는 `HongKongCspfBatchDialog` (Toplevel wrapper)와 내부 프레임 위젯인 `HongKongCspfBatchSection`이 혼재되어 있습니다. 이 둘은 다이얼로그 윈도우 수명 주기 관리와 테이블 레이아웃 구성이라는 다른 성격의 책임을 가지므로 구조적으로 분리되어야 합니다.

## Folder Boundary Candidates Evaluation

향후 ISO 2-point 및 SASO T3 batch dialog를 추가적으로 확장하여 배치 연산을 완성할 때 적합한 폴더링 후보들은 다음과 같습니다.

### Candidate A: `ui_tk/batch_dialogs/` (Shell + Profiles Package)
- **구조**:
  - `ui_tk/batch_dialogs/shell.py` (공통 Toplevel 윈도우 관리 및 lifecycle 소유)
  - `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py` 등 (프로필별 구체 어댑터 구성)
- **장점**:
  - `ui_tk/` 루트의 components 개수를 지나치게 늘리지 않으면서, 배치 연산 전용 다이얼로그의 아키텍처 경계를 명확히 분리.
  - Toplevel shell, geometry, focus, snapshot handoff 등 공통 UI 책임을 `shell.py`로 격리하여 코드 복사-붙여넣기 방지 및 유지보수성 향상.
  - 신규 프로필 확장 시 `profiles/` 폴더 하위에 얇은 어댑터 파일만 추가하면 되므로 확장성이 우수함.
- **단점**:
  - flat 구조에 비해 초기 설계 구성(shell과 profile의 분리) 비용이 약간 발생함.

### Candidate B: `ui_tk/dialogs/batch/`
- **구조**: `ui_tk/dialogs/batch/hong_kong_cspf.py` 등
- **장점**:
  - 배치 다이얼로그 외에 향후 다른 성격의 다이얼로그(예: settings, about 등)가 생길 경우 `dialogs/` 폴더 하위에 계층 구조로 깔끔하게 묶을 수 있음.
- **단점**:
  - 현재 프로젝트 규모상 다이얼로그가 많지 않아 2단계 하위 폴더링은 과도한 추상화일 수 있음.

### Candidate C: `ui_tk/batch/`
- **구조**: `ui_tk/batch/hong_kong_cspf_dialog.py` 등
- **장점**:
  - 재사용 가능한 배치 테이블 기반구조(`BatchMatrixTable` 등)와 프로필별 배치 다이얼로그를 하나의 `batch` 패키지로 모을 수 있음.
- **단점**:
  - 공통 기반구조(generic foundation) 파일들과 특정 계산 로직(profile-specific dialogs)이 동일한 패키지에 섞이게 되어 MVC/SoC 레이어 경계가 모호해짐.

### Candidate D: 현 위치 유지 (`ui_tk/sections/`)
- **장점**: 파일 이주 비용과 import churn이 전혀 없음.
- **단점**: 일반 탭 내부의 static section widget들과 popup dialog window들이 섞여 `sections/` 폴더가 혼잡해지고 책임을 알아보기 어려워짐.

### 결론: **Candidate A (`ui_tk/batch_dialogs/` Shell + Profiles) 채택**
- 프로필별 배치 다이얼로그들은 독립적인 사용자 화면 흐름을 구성하되, 공통 Toplevel window lifecycle, hidden-first geometry settle/show, focus, snapshot handoff 등은 `shell.py`로 공통화하고, `profiles/` 하위 어댑터가 이를 채우도록 아키텍처 경계를 보정합니다.
- 이는 flat 구조 채택 시 발생하는 "프로필별 full-dialog 코드 복사-붙여넣기(anti-pattern)" 위험을 미연에 방지합니다.

## Batch Dialog Commonization Feasibility (공통화 필요성 판단)

1. **공통 Dialog Base 도입 여부**:
   - **판단**: 거대한 abstract base class를 만들지는 않습니다. 대신 `shell.py`가 공통 Toplevel lifecycle 및 snapshot handoff 계약을 관리하고, profile-specific 파일들이 얇은 adapter/composition 형태로 동작하도록 결합(Composition-first)을 유도합니다.
2. **이유 및 리스크**:
   - SASO T3는 **35 Min optional test toggle** 제어 및 trace profile combo가 결합되어 동작합니다.
   - ISO 2-point는 **ISO 16358-1과 India ISEER의 두 가지 비교 연산 결과**를 출력하는 비교 테이블 위젯과 visual canvas를 포함합니다.
   - 반면 Hong Kong CSPF는 단일 프로필 연산 결과와 Matrix 데이터만 관리합니다.
   - 상속 기반의 공통화를 서두르면 다이얼로그 껍데기에 지나치게 많은 다형성 옵션이나 분기 코드가 생기게 됩니다. 따라서, 공통 책임은 `shell.py`에 두고, 화면 구성의 변형은 profile-specific adapter frame에 위임하는 방식이 가장 안전합니다.
3. **공통화 가능 범위**:
   - 창 크기 및 hidden-first geometry settle/show, Toplevel 윈도우 핸들링, snapshot persist 콜백 실행 등 공통 윈도우 제어 책임을 `shell.py`에 내장합니다.

## Clean Architecture MVC/SoC 관점 판단

- **Model**: `BatchMatrixSpec` 등 배치 스키마 메타데이터가 데이터 레이아웃의 규칙을 정의합니다.
- **View (Matrix Table Surface)**: `BatchMatrixTable`은 오직 2줄씩 렌더링하고 셀 포지션을 이벤트 바인딩에 맞춰 전달하는 Presentation 책임만 가집니다.
- **Controller**: `HongKongCspfMatrixController` 및 배치 다이얼로그는 사용자 데이터 입력 이벤트를 연산 핸들러와 매핑하여 뷰를 갱신합니다.
- **Dialog Shell Wrapper**: `Toplevel` 윈도우 수명 주기 및 snapshot 데이터 영속성 저장을 담당하며, 비즈니스 계산 로직과 UI 뷰 그리드 구조에 직접 개입하지 않습니다.

## Next Implementation Slice Proposal (다음 구현 작업 제안)

- **선택된 작업**: **Batch dialog shell + profiles skeleton and Hong Kong CSPF relocation**
  - 배치 다이얼로그 확장에 앞서 `ui_tk/batch_dialogs/shell.py` 공통 골격과 `ui_tk/batch_dialogs/profiles/` 구조를 신설하고, 기존의 검증된 Hong Kong CSPF 배치 다이얼로그를 신규 패키지 경계에 맞게 분리 이주하는 작업을 최우선 실행합니다.

### Next Slice Details:
- **작업명**: ui_tk: Build batch dialog shell + profiles package and relocate Hong Kong CSPF
- **목적**:
  - `ui_tk/batch_dialogs/shell.py` 공통 껍데기(Toplevel shell, geometry settle, snapshot handoff)를 빌드.
  - `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py`를 신설하여 기존 cspf 배치 데이터 스펙 및 계산 어댑터를 이주.
  - 공통 shell과 profile adapter 간의 clean composition 계약 검증.
- **수정 허용 후보**:
  - `ui_tk/sections/hong_kong_cspf_section.py` (import 경로 수정)
  - `tests/test_ui_tk_iso_table_autocalc.py` (import 경로 수정)
  - `ui_tk/batch_dialogs/shell.py` (공통 shell 작성)
  - `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py` (어댑터 작성)
  - `ui_tk/sections/hong_kong_cspf_batch_section.py` (dialog 제거 및 section만 잔류)
- **수정 금지 후보**:
  - `ui_tk/batch_matrix_table.py` 등 batch table foundation 전체
  - `ui_tk/table/controller.py` 등 interaction controller 전체
  - calculator core 및 ML 관련 파일 전체
- **검증 후보**:
  - `python3 -B tools/check_code_structure.py`
  - `pytest tests/test_ui_tk_iso_table_autocalc.py`
- **GUI smoke 필요 여부**:
  - **필요 (Yes)**: 이주 후 실제 Hong Kong CSPF 탭에서 배치 창이 정상적으로 뜨고, 추가/삭제/복사/엑셀 내보내기 및 실시간 연산 결과 갱신이 비주얼 및 기능 오작동 없이 작동하는지 수동 검증 필수. 특히 shell-profile 간의 snapshot handoff와 hidden-first geometry 안착 여부 검증 관점 추가.

## Verification Result (검증 결과)

- **Python Source Modification**: 전혀 없음 (`git status` 상 소스/테스트 수정 없음).
- **Structure Check**: `python3 -B tools/check_code_structure.py` 결과, 기존의 LOC soft limit 경고 외에 layer violation이나 아키텍처 규칙 위반 사항 없음.
- **Diff Check**: `git diff --check` 상의 whitespace 오류 및 blank line warning 없음.
- **Active Report Count Wording Compliance**: 보고서 본문 및 durable docs에 exact active report count 대신 threshold wording 정책을 철저히 준수함.

## Excluded Areas (제외 범위)

- ISO 2-point 및 SASO T3 batch dialog의 구현 및 calculator core, ML 로직 변경은 범위 외로 제외되었습니다.
- 프로덕션 코드(`.py`)와 테스트 코드의 logic 수정 또는 file move/rename은 설계 단계이므로 수행하지 않았습니다.

## Next Suggested Action

1. **Build batch dialog shell + profiles skeleton and relocate Hong Kong CSPF** (establish package and compose adapter)
2. **ISO 2-point batch dialog implementation** (matrix-based comparison result rendering)
3. **SASO T3 batch dialog implementation** (matrix-based optional 35 Min toggle rendering)
4. **Calculator entrypoint handover from PyQt to Tkinter**
5. **EN14825 / AHRI 210/240 / KS profile expansion**
