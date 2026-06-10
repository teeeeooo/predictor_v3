# 325 ISO 2-point Batch Dialog Report Closeout Correction

## Goal (목표)

- `324` ISO 2-point batch dialog implementation 작업 완료 후, active report에 남아있는 문서 상의 불일치(로컬 절대경로 링크, 사용자 수동 검증 pending 문구 등)를 해결하고 최종 closeout한다.
- 향후 수동 GUI 검증 문항에 대한 운영 원칙을 명문화하여 Codex 프롬프트의 복잡도를 제어한다.

## 324 Report Link Correction Details (324 report 링크 보정 내용)

- `324` active report 내의 모든 `file:///Users/...` 로컬 절대경로 링크를 repo-relative path 또는 plain path로 변경하여 로컬 사용자명 및 절대 경로 흔적을 제거했습니다:
  - `ui_tk/batch_dialogs/profiles/iso_iseer_2point.py`
  - `tests/test_ui_tk_iso_iseer_2point_batch_dialog.py`
  - `ui_tk/batch_dialogs/profiles/__init__.py`
  - `ui_tk/sections/iso_iseer_2point_section.py`
  - `result_reports/active/323_remove_private_shell_access_from_batch_dialog_test.md`
  - `docs/WORK_PLAN.md`
  - `project_log.md`
  - `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## User Verification Status Correction Details (사용자 확인 상태 보정 내용)

- `324` report에서 사용자 수동 GUI 검증 관련 "필요(Pending)" 상태 문구를 삭제하고, 사용자 실측 및 동작 확인 결과 이상 없음("완료") 상태로 갱신 및 보정하였습니다.

## Codex Prompt Manual Smoke Principle (수동 GUI 검증 운영 원칙)

- **운영 원칙**: 앞으로 Codex 프롬프트에는 세부적인 사용자 수동 GUI 확인 문항들을 일일이 명세하여 포함하지 않습니다. 대신, 사용자가 별도의 실제 환경에서 GUI 동작(안착 위치, 스크롤, 단축키 복사/붙여넣기 등)을 점검 및 확인한 뒤, 그 결과만 closeout correction 단계의 active report에 반영하여 일괄 마감하도록 운영 방식을 표준화합니다.

## WORK_PLAN / project_log Update Status (WORK_PLAN / project_log 업데이트 여부)

- **업데이트 완료**:
  - `docs/WORK_PLAN.md`에 `325` correction 완료 사항을 반영하고 Next Actions 순서(SASO T3 batch dialog implementation 우선)를 유지했습니다.
  - `project_log.md` 하단에 `325` correction에 대한 compact한 entry를 추가하고 threshold wording 정책을 적용했습니다.

## Verification & Test Results (검증 결과)

- `git status --short` 및 `git diff --check` 결과, whitespace 경고 없이 깨끗함을 검증했습니다.
- `grep`을 통해 `result_reports/active/324_iso_iseer_2point_batch_dialog_implementation.md` 및 기타 리포트에 `file:///Users` 또는 `Downloads` 패턴이 남아있지 않음을 교차 검증하였습니다.
- `python3 -B tools/check_code_structure.py` 결과, soft limit warnings 4개를 만족하여 정상임을 확인했습니다.

## Excluded Areas (제외 범위)

- production Python source 및 tests 등의 코드 파일에는 수정을 전혀 가하지 않았습니다 (수정 금지 준수).
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 파일은 단순 문서 보정 작업이므로 재생성하지 않았습니다.
- SASO T3 batch dialog 구현은 작업 범위 외로 엄격히 배제되었습니다.

## Next Actions (향후 작업)

1. **SASO T3 batch dialog implementation** (matrix-based optional 35 Min toggle rendering)
2. **Batch foundation foldering audit**
3. **Batch foundation foldering implementation**
4. **Calculator entrypoint handover from PyQt to Tkinter**
5. **ui_tk root folder inventory audit**
6. **EN14825 / AHRI 210/240 / KS profile expansion**

## Active Report Count Status (액티브 리포트 수 상태)

- active report count meets lifecycle threshold criteria.
