# 322 Batch Dialog Relocation Smoke Closeout and Private Access Correction

## Goal (목표)

- `321_batch_dialog_shell_profiles_skeleton_hk_cspf_relocation` 작업 이후 사용자가 수행한 manual GUI smoke 결과를 closeout한다.
- `321` 리포트에 남아 있던 로컬 절대경로(`file:///Users/...`) 링크들을 repo-relative path 또는 plain path로 교정한다.
- `HongKongCspfBatchDialog.snapshot()`이 `BatchDialogShell`의 private attribute인 `_adapter`에 직접 접근하던 구현을 공통 public 메서드를 신설하여 보정한다.
- 다음 단계인 ISO 2-point batch dialog 구현 전에 구조적인 불편함이나 링크 문제를 완전히 정리한다.

## Manual GUI Smoke Results (수동 검증 결과)

사용자가 수동 검증을 진행한 결과는 다음과 같으며, 어떠한 레이아웃이나 기능 이상 없이 완벽히 동작함이 closeout되었습니다:
- **Hong Kong CSPF 탭**: Multi 입력 버튼 클릭 시 batch dialog가 parent window 정중앙에 올바른 크기(920x320)로 팝업됩니다.
- **Data Persistence**: 다이얼로그를 닫았다가 다시 열어도 이전 입력 snapshot이 완벽하게 유지 및 복원됩니다.
- **Interactive Operations**: Add Case / Remove Case / Copy All / Export CSV 등의 테이블 제어 버튼들이 오류 없이 기존 스펙대로 기능합니다.
- **Auto Calculation**: 입력 셀 값을 수정하면 debounced auto calculation이 정상 호출되며 하단 상태 메시지에 실시간으로 valid/blank/error 카운트가 정상 반영됩니다.

## Private Access Correction (private 접근 보정 내용)

- **문제점**: `HongKongCspfBatchDialog.snapshot()`이 generic shell인 `BatchDialogShell` 내부의 private 어댑터 인스턴스 `self._shell._adapter`를 직접 참조하여 캡슐화 경계를 침범하고 있었습니다.
- **해결 방안**:
  - `ui_tk/batch_dialogs/shell.py`의 `BatchDialogShell` 클래스 내에 `snapshot() -> list[dict[str, str]]` public 메서드를 추가하여 캡슐화를 강화했습니다.
  - `BatchDialogShell.close()` 메서드 또한 중복되는 호출 방식을 리팩토링하여 새로 추가된 `self.snapshot()`을 호출하도록 교정했습니다.
  - `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py`의 `HongKongCspfBatchDialog.snapshot()`이 private 접근 대신 `self._shell.snapshot()`을 호출하도록 정정했습니다.

## Link Correction (321 Report 링크 보정 내용)

- `321` 결과 리포트에 포함되어 있던 로컬 username, Downloads 폴더 경로, 한글 인코딩 등이 섞인 `file:///Users/sunjaekim/Downloads/태우%20작업/predictor_v3/...` 형태의 로컬 절대경로 마크다운 링크들을 전부 `../../ui_tk/...` 및 `../../tests/...`와 같은 **repo-relative path**로 깨끗하게 보정했습니다.
- 이로 인해 개발 머신 외부의 다른 환경이나 GitHub 상에서 문서 링크 접근 시 로컬 유저 환경 정보 유출이나 깨짐 현상 없이 정적으로 접근할 수 있게 되었습니다.

## CODEBASE_REFERENCE_MAP Regeneration (CODEBASE_REFERENCE_MAP 재생성 여부)

- `BatchDialogShell`에 public `snapshot()` 메서드를 추가한 것은 symbol-level structural change이므로, `python3 -B tools/code_checker/build_reference_map.py` 명령을 통해 reference map을 최신 상태로 정상 재생성(`FRESH`)하여 stage 완료했습니다.

## Verification & Test Results (검증 결과)

- `python3 -B -m py_compile` 명령을 사용하여 수정된 모든 파일들의 구문 오류 유무를 체크하고 통과했습니다.
- [tests/test_ui_tk_iso_table_autocalc.py](../../tests/test_ui_tk_iso_table_autocalc.py) 내 `test_hong_kong_cspf_batch_opens_dialog_not_metric_tab` 테스트 코드에 새로 추가된 `first_dialog.snapshot()` 및 `first_dialog._shell.snapshot()` public method를 직접 검증하는 assertion을 보강하여 검증을 견고히 했습니다.
- `tests/test_ui_tk_iso_table_autocalc.py` (focused run) 및 `tests/test_ui_tk_hong_kong_cspf_matrix_migration.py` 테스트 슈트의 모든 연동 테스트가 `PASSED` 됨을 확인했습니다.
- `python3 -B tools/check_code_structure.py` 결과, New Code Quality Gate 상의 layer violation이나 구조적인 오류 없이 검증이 마감되었습니다.
- `git diff --check` 상의 whitespace 및 blank line warning 없음이 검증되었습니다.

## Excluded Areas (제외 범위)

- ISO 2-point 및 SASO T3 batch dialog의 구현은 작업 범위 외로 엄격히 제외되었습니다.
- calculator/core 및 ML/predictor 로직, profile config 등 core layer 변경 또한 완전히 방지되었습니다.

## Next suggested Actions (향후 작업 제안)

1. **ISO 2-point batch dialog implementation** (matrix-based comparison result rendering)
2. **SASO T3 batch dialog implementation** (matrix-based optional 35 Min toggle rendering)
3. **Calculator entrypoint handover from PyQt to Tkinter**
4. **ui_tk root folder inventory audit**
5. **EN14825 / AHRI 210/240 / KS profile expansion**

## Post-Commit Correction Note (June 10, 2026)

- **Test-side Private Access Cleanup**: production 단의 private access 제거에 이어, `tests/test_ui_tk_iso_table_autocalc.py`에 남아 있던 `first_dialog._shell.snapshot()` 직접 검증 코드를 완전히 제거하였습니다.
- **Verification Strategy**: `BatchDialogShell.snapshot()` public method 기능 자체는 신설된 shell-level focused unit test([tests/test_ui_tk_batch_dialog_shell.py](../../tests/test_ui_tk_batch_dialog_shell.py))에서 mock adapter를 사용해 격리 검증하도록 이관하였으며, 통합 테스트에서는 dialog의 public `snapshot()` wrapper만 사용하도록 보정했습니다.
