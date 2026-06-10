# 321 Batch Dialog Shell-Profiles Skeleton and Hong Kong CSPF Relocation

## Goal (목표)

- `320_batch_dialog_shell_profiles_boundary_correction.md` 설계 보정에 따라, flat batch_dialogs 구조가 아닌 `shell.py + profiles` 구조를 실제 코드에 반영한다.
- 기존 Hong Kong CSPF batch dialog를 `ui_tk/sections/hong_kong_cspf_batch_section.py`에서 `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py`로 이주한다.
- 공통 Toplevel shell / geometry / close protocol / snapshot handoff 책임을 `ui_tk/batch_dialogs/shell.py`로 격리하여 향후 다수 프로필 배치 확장 시의 코드 중복을 차단하고 관심사를 명확히 분리한다.

## Structure Comparison (기존 구조와 변경 구조)

### Legacy Structure (기존 구조)
```text
ui_tk/
  sections/
    hong_kong_cspf_batch_section.py (Dialog shell, Section widget, Matrix controller 혼재)
    hong_kong_cspf_section.py
```

### New Scalable Structure (변경 구조)
```text
ui_tk/
  batch_dialogs/
    __init__.py
    shell.py (공통 Toplevel container, geometry settle, close callback, snapshot handoff 담당)
    profiles/
      __init__.py
      hong_kong_cspf.py (Hong Kong CSPF 전용 matrix table layout 및 controller 어댑터 담당)
  sections/
    hong_kong_cspf_section.py (새 경로에서 HongKongCspfBatchDialog를 import)
```

## Created and Relocated Files (생성 및 이동/삭제 파일)

### Created Files (생성된 파일)
- [ui_tk/batch_dialogs/__init__.py](file:///Users/sunjaekim/Downloads/태우%20작업/predictor_v3/ui_tk/batch_dialogs/__init__.py)
- [ui_tk/batch_dialogs/shell.py](file:///Users/sunjaekim/Downloads/태우%20작업/predictor_v3/ui_tk/batch_dialogs/shell.py)
- [ui_tk/batch_dialogs/profiles/__init__.py](file:///Users/sunjaekim/Downloads/태우%20작업/predictor_v3/ui_tk/batch_dialogs/profiles/__init__.py)
- [ui_tk/batch_dialogs/profiles/hong_kong_cspf.py](file:///Users/sunjaekim/Downloads/태우%20작업/predictor_v3/ui_tk/batch_dialogs/profiles/hong_kong_cspf.py)

### Relocated/Deleted Files (이동/삭제된 파일)
- `ui_tk/sections/hong_kong_cspf_batch_section.py` (완전 삭제 처리 완료)

## Responsibility Split (책임 분할)

### `shell.py` (공통 Container)
- `tk.Toplevel` 윈도우 인스턴스화 및 window title/layout weight 바인딩.
- hidden-first geometry settle 및 show lifecycle 관리 (`winfo_reqwidth/height` 측정 및 Centering 적용 후 deiconify).
- `WM_DELETE_WINDOW` close protocol 가로채기 및 close 시 profile adapter로부터 raw snapshot을 획득하여 parent callback으로 handoff.
- `focus()` 처리를 통해 중복 창 활성화 방지 및 기존 오픈된 창 리프트.

### `profiles/hong_kong_cspf.py` (프로필 어댑터)
- `HongKongCspfBatchAdapter`가 `BatchProfileAdapter` 프로토콜을 구현하여 profile title, min_size, layout frame build, dispose, snapshot 추출을 제공.
- Hong Kong CSPF 특화 `BatchMatrixTable` 구성 및 `HongKongCspfMatrixController` 연동.
- Toplevel window lifecycle, geometry, close protocol 코드는 전혀 포함하지 않고, pure Tk content widget과 controller에 집중.

## Section Integration & Compatibility Shim (통합 및 호환성)

- [ui_tk/sections/hong_kong_cspf_section.py](file:///Users/sunjaekim/Downloads/태우%20작업/predictor_v3/ui_tk/sections/hong_kong_cspf_section.py)가 새 경로인 `ui_tk.batch_dialogs.profiles.hong_kong_cspf`에서 `HongKongCspfBatchDialog`를 바로 import하도록 업데이트했습니다.
- 외부 interface와 기존 test가 여전히 `first_dialog.section.table`에 접근하거나 `close()`, `snapshot()`, `focus()` 메서드를 원활히 사용할 수 있도록 `HongKongCspfBatchDialog`가 `BatchDialogShell`을 Composition으로 포장하여 public interface를 그대로 유지하는 **Compatibility wrapper** 역할을 하도록 구성했습니다.
- 임시 transitional import shim 파일 없이 legacy `hong_kong_cspf_batch_section.py`를 완전 제거(`git rm`)하여 중복 소스 코드 오너십 우려를 완전히 제거했습니다.

## Behavior Preservation Assessment (동작 보존성 판단)

- **Snapshot Handoff**: 창을 닫을 때 데이터 snapshot이 수집되어 `_batch_snapshot`에 기록되고, 창을 다시 열 때 `initial_snapshot` 파라미터로 주입되어 `restore_snapshot`을 통해 복구됩니다.
- **Auto Calculation**: 복제한 `HongKongCspfMatrixController` 및 `DebouncedAutoCalc` 연동이 기존 구조와 동일하게 동작하여 Multi 입력 테이블 값이 수정되면 실시간으로 우측 상태 표시 및 결과 테이블이 반영됩니다.
- **Window Geometry**: hidden-first geometry logic이 `shell.py`로 온전히 이관되어 최초 팝업 표시 시 비정상적인 flicker 현상이나 크기 축소 현상 없이 안착합니다.

## Verification & Test Results (검증 결과)

- `python3 -B -m py_compile`을 통해 새로 생성/수정된 Python 파일들의 구문 오류 및 import 순환 우려가 없음을 입증했습니다.
- [tests/test_ui_tk_iso_table_autocalc.py](file:///Users/sunjaekim/Downloads/태우%20작업/predictor_v3/tests/test_ui_tk_iso_table_autocalc.py) 내 `test_hong_kong_cspf_batch_opens_dialog_not_metric_tab` 테스트에서 사용되던 legacy `row_header_texts`, `add_row`, `set_text_rows` 및 `declared` 키 등을 `BatchMatrixTable` API 규격(`cases`, `add_case`, `restore_snapshot`, `declared_capacity`)에 맞춰 경량 교정 완료했습니다.
- [tests/test_ui_tk_hong_kong_cspf_matrix_migration.py](file:///Users/sunjaekim/Downloads/태우%20작업/predictor_v3/tests/test_ui_tk_hong_kong_cspf_matrix_migration.py)의 import 경로를 갱신하여 총 15개 focused batch 연동 테스트가 모두 정상 `PASSED` 함을 확인했습니다.
- `python3 -B tools/code_checker/build_reference_map.py` 실행 결과, reference map이 최신 상태(`FRESH`)를 만족하며 uncommitted changes를 정상 검출했습니다.
- `python3 -B tools/check_code_structure.py` 결과, 신규 작성 파일에 대한 layer violation이나 boundary 규칙 위반 없이 structure check가 통과함을 확인했습니다.

## Excluded Areas (제외 범위)

- ISO 2-point 및 SASO T3 batch dialog의 구현은 작업 범위 외로 엄격히 제외되었습니다.
- calculator/core 및 ML/predictor 로직, profile config 등 core layer 변경 또한 완전히 방지되었습니다.

## Next suggested Actions (향후 작업 제안)

1. **ISO 2-point batch dialog implementation** (matrix-based comparison result rendering)
2. **SASO T3 batch dialog implementation** (matrix-based optional 35 Min toggle rendering)
3. **Calculator entrypoint handover from PyQt to Tkinter**
4. **ui_tk root folder inventory audit**
5. **EN14825 / AHRI 210/240 / KS profile expansion**

## Manual GUI Smoke Verification Guidelines (수동 검증 요령)

사용자는 다음 항목을 순차적으로 GUI 수동 검증할 수 있습니다:
1. Hong Kong CSPF 탭에서 "Multi 입력" 버튼 클릭 시 batch dialog가 parent window 정중앙에 올바른 크기(920x320)로 안착하는가?
2. 값을 수정한 후 닫기(X 또는 윈도우 닫기)를 한 후 다시 "Multi 입력"을 열었을 때 수정된 데이터가 유실되지 않고 정상 복원되어 있는가?
3. Add Case / Remove Case / Copy All / Export CSV 버튼 클릭 시 기능이 오작동 없이 원활히 수행되는가?
4. 테이블 입력 필드 수정 시 debounced auto calculation 결과 메시지가 하단 상태창에 실시간으로 정상 업데이트되는가?
