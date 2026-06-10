# 323 Remove Private Shell Access from Batch Dialog Test

## Goal (목표)

- `322_batch_dialog_relocation_smoke_closeout_private_access` 작업에서 production private access는 제거했으나, 통합 테스트인 `tests/test_ui_tk_iso_table_autocalc.py`에 남아있던 `first_dialog._shell.snapshot()` 직접 접근 코드를 완전 제거한다.
- 테스트가 `HongKongCspfBatchDialog` 내부 composition detail인 `_shell`에 직접 의존하지 않도록 분리하고, 캡슐화 검증을 완결한다.

## Private Access Identification Results (private 접근 위치 확인 결과)

- **Search Results**:
  - `tests/test_ui_tk_iso_table_autocalc.py` 내 `assert first_dialog._shell.snapshot()[0]["declared_capacity"] == "3500"` 구문 발견.
  - 이 외에 `_shell._adapter`나 기타 외부 모듈에서의 `first_dialog._shell` 직접 접근은 발견되지 않음.
  - production source 내에서는 `HongKongCspfBatchDialog.snapshot()`이 자신의 인스턴스 멤버인 `self._shell.snapshot()`을 직접 호출하는 것 외에 private attribute 침해 사례 없음 확인.

## Test Correction (테스트 보정 내용)

- `tests/test_ui_tk_iso_table_autocalc.py`의 `test_hong_kong_cspf_batch_opens_dialog_not_metric_tab` 테스트에서 `first_dialog._shell.snapshot()` 직접 호출 assertion을 제거했습니다.
- 대신 public wrapper API인 `first_dialog.snapshot()` 호출 검증을 남겨두어 캡슐화를 훼손하지 않으면서 snapshot close/reopen 흐름 및 데이터 원복 동작에 대한 검증을 보존했습니다.

## New Shell-Level Test (신규 shell-level test 추가 여부와 이유)

- **추가 여부**: 추가 (`tests/test_ui_tk_batch_dialog_shell.py` 신규 생성 완료).
- **이유**: 통합 테스트인 `test_ui_tk_iso_table_autocalc.py`에서 `first_dialog._shell.snapshot()` 직접 검증을 제거했으므로, generic `BatchDialogShell`의 `snapshot()` 메서드 위임 구조와 `close()` 콜백 흐름을 안전하게 격리 unit test할 장치가 필요하다고 판단했습니다.
- **검증 내용**:
  - `FakeProfileAdapter` mock 객체를 사용하여 `BatchDialogShell.snapshot()`이 어댑터의 snapshot 데이터를 그대로 위임해 반환하는가?
  - `BatchDialogShell.close()` 호출 시 어댑터의 `dispose()`가 정상 호출되고 수집된 snapshot 데이터가 `on_close` 콜백에 안전하게 넘겨지는가?

## 322 Report Note Correction (322 report note 보정 내용)

- [322_batch_dialog_relocation_smoke_closeout_private_access.md](../../result_reports/active/322_batch_dialog_relocation_smoke_closeout_private_access.md)의 최하단에 `Post-Commit Correction Note` 섹션을 추가하여, test-side private access 직접 검증을 제거하고 shell-level focused unit test로 이관하여 검증 구조를 교정했음을 기록했습니다.

## Verification & Test Results (검증 결과)

- `python3 -B -m py_compile` 명령을 활용하여 수정한 `tests/test_ui_tk_iso_table_autocalc.py` 파일의 컴파일 이상 무를 확인했습니다.
- `tests/test_ui_tk_batch_dialog_shell.py` (2 passed) 및 `tests/test_ui_tk_iso_table_autocalc.py` (1 passed)를 포함한 3개 focused batch/shell tests가 모두 정상 `PASSED` 함을 확인했습니다.
- `python3 -B -m pytest tests/test_ui_tk_hong_kong_cspf_matrix_migration.py`를 실행하여 14개 마이그레이션 테스트가 정상 통과함을 재확인했습니다.
- `python3 -B tools/check_code_structure.py` 결과, 구조 check 규칙(soft limit warnings 3개 제외)을 완벽히 충족함을 검증했습니다.
- `git diff --check` 결과, whitespace 및 blank line warning 등 git 포맷 경고가 전혀 없음을 확인했습니다.

## Excluded Areas (제외 범위)

- production Python source 파일 수정은 본 작업 범위 외로 엄격히 제외되었습니다.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 재생성은 structural change가 없으므로 [수정 금지] 규칙을 준수하여 수행하지 않았습니다.
- ISO 2-point 및 SASO T3 batch dialog의 구현은 작업 범위 외로 엄격히 제외되었습니다.

## Next suggested Actions (향후 작업 제안)

1. **ISO 2-point batch dialog implementation** (matrix-based comparison result rendering)
2. **SASO T3 batch dialog implementation** (matrix-based optional 35 Min toggle rendering)
3. **Calculator entrypoint handover from PyQt to Tkinter**
4. **ui_tk root folder inventory audit**
5. **EN14825 / AHRI 210/240 / KS profile expansion**
