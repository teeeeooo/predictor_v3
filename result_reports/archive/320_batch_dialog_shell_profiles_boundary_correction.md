# 320 Batch Dialog Shell-Profiles Boundary Correction

## Goal

- 기존 `319_ui_tk_batch_dialog_folder_boundary_audit.md`에서 내린 flat `ui_tk/batch_dialogs/` 폴더 결정에 대해, 향후 다수 프로필 확장 시 발생할 수 있는 중복 구현 및 윈도우 보일러플레이트 코드 복사-붙여넣기 문제를 방지하기 위해 `shell + profiles` 구조로 설계를 보정한다.

## Reviewed Reference Documents (확인한 기준 문서)

- **AGENTS.md (New Code Quality Gate / Design Gate)**: 책임을 한 파일에 섞지 않고, 반복 rule을 registry/service로 분리하는 원칙을 준수.
- **docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md (SoC / Responsibility Definitions)**: Dialog shell은 Toplevel lifecycle/geometry를 가지며, View widget/composition은 얇은 어댑터 형태로 격리하여 관심사를 분리해야 함을 확인.
- **docs/agent_workflows/UI_SURFACE_WORKFLOW.md (Dialog / Result Surface Gate)**: 배치 결과 화면의 grid 형태와 controller 매핑 경계 재확인.
- **docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md (Hidden-first Lifecycle)**: Toplevel 다이얼로그의 hidden-first geometry 적용, measure-settle-show lifecycle이 공통 shell 수준에서 관리되어야 함을 확인.
- **docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md (Stateful Input Surface)**: 입력 데이터 snapshot persistence가 다이얼로그 close/reopen 시 올바르게 유지되도록 callback/handoff 설계를 공통 shell에서 규격화해야 함을 확인.

## 319 Decision Audit & Need for Correction

- **유효 부분**: `ui_tk/sections/` 폴더 내에 탭 위젯과 다이얼로그가 혼합되어 있던 구조를 청소하고, 다이얼로그 경계를 별도로 분리한다는 방향성은 완전히 유효합니다.
- **보정 필요 부분**: 기존 319의 flat `ui_tk/batch_dialogs/` 구조는 다가올 EN14825, AHRI, KS 등의 다수 프로필 배치 다이얼로그 확장 시 각각의 파일들이 `tk.Toplevel` 윈도우 생성, focus/reopen 관리, hidden-first geometry settle, close callback, snapshot handoff 등의 공통 제어 로직을 무수히 복사-붙여넣기하게 되는 중복 리스크를 야기합니다.
- **보정 대안**: 따라서 flat 구조를 `batch_dialogs/shell.py + batch_dialogs/profiles/` 구조로 고도화하여, 공통 UI lifecycle 제어와 프로필별 어댑터를 명확히 격리합니다.

## Corrected Shell + Profiles Structure Design

보정된 신규 패키지 및 경계 구조는 다음과 같습니다:

```text
ui_tk/
  batch_dialogs/
    __init__.py
    shell.py
    profiles/
      __init__.py
      hong_kong_cspf.py
```

### 1. `shell.py` (공통 Toplevel Shell) 책임
- `tk.Toplevel` 윈도우 인스턴스화, focus, deiconify/lift 윈도우 재오픈 관리.
- hidden-first geometry settle 및 show lifecycle (구조 빌드 -> settle -> req width/height 측정 -> centering geometry 적용 -> reveal).
- window close (`WM_DELETE_WINDOW`) 가로채기 및 `on_close` 콜백 실행 관리.
- profile-specific adapter frame을 내부에 compositional 주입받아 packaging하는 container 역할.
- 다이얼로그 close 시, active profile adapter로부터 raw snapshot을 획득하여 호출처로 handoff하는 snapshot protocol 책임.

### 2. `profiles/hong_kong_cspf.py` (프로필별 어댑터) 책임
- `BatchMatrixTable`을 활용하여 화면을 드로잉하는 profile-specific GUI composition.
- 기존 `HongKongCspfMatrixController` 및 calculation/result mapping 연동.
- 프로필 타이틀, csv headers/rows export mapping, 35 Min toggle(SASO T3의 경우) 등의 특화 뷰/동작.
- **제약**: dialog shell Toplevel 윈도우 제어나 geometry, lifecycle은 전혀 다루지 않고, 얇은 Frame 어댑터 객체로만 구성됩니다.

## Profile Expansion & Copy-Paste Prevention Rules

- **프로필별 파일 증가 허용**: 향후 ISO 2-point, SASO T3 등 프로필 배치가 확장될 때, `profiles/` 폴더 밑에 해당하는 프로필 전용 파일(`iso_iseer_2point.py`, `saso_t3.py`)을 얇게 추가하는 행위는 정상적이며 권장됩니다.
- **Full Dialog 복사-붙여넣기 금지**: Toplevel geometry 계산이나 window protocol, snapshot callback binding 등 `shell.py`가 제공하는 다이얼로그 껍데기 제어 로직을 개별 프로필 파일에 임의 복사하여 중복 윈도우 클래스를 만드는 것은 엄격히 금지됩니다. 모든 배치는 `shell.py` 컨테이너에 주입되는 구조(Composition)를 따릅니다.
- **과한 공통화 금지**: 공통 base class를 상속 구조로 설계하여 profiles를 묶지 않고, `shell.py`가 profiles의 Frame 위젯을 composition으로 얹어 동작하도록 경량 래퍼로 단순하게 유지합니다.

## Next Implementation Slice Proposal

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

## Closeout Note (June 10, 2026)

- `ui_tk/batch_dialogs/shell.py` 공통 껍데기(Toplevel shell, geometry settle, snapshot handoff)와 `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py` profile adapter 이주를 성공적으로 완료했습니다.
- `ui_tk/sections/hong_kong_cspf_section.py` 및 관련 테스트의 import 경로와 API 호출부를 최신 구조에 맞춰 정상 갱신하였으며, 모든 연동 테스트가 통과하였습니다.

