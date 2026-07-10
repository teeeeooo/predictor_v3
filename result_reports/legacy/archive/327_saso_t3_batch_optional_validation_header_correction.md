# 327 SASO T3 Batch Optional Validation and Header Correction

## Goal (목표)

- 326 SASO T3 batch dialog implementation에서 발생할 수 있는 optional 35 Min partial 입력 처리 불일치 문제를 보정한다.
- SASO T3 batch result header를 3pt / 4pt 표현으로 바꾸어 더 직관적으로 보정하고, 사용자가 주로 보는 4pt 결과를 먼저 노출하도록 컬럼 순서를 조정한다.
- project_log.md를 수정하지 않고 micro correction을 완결한다.

## Discrepancies (발견된 불일치)

- **Optional Partial Validation**: 기존 구현에서는 optional 필드가 둘 다 빈 값일 때 계산이 required-only로만 돌며 `BatchRowState.OK`로 처리되었으나, 하나만 채워진 partial 입력 케이스도 에러로 처리되지 않고 required-only OK로 그냥 넘어가는 허점이 있었습니다.
- **Header Labels & Order**: 기존 `Req CSPF` 등의 label은 사용자에게 직관적이지 않았으며, 4pt 결과보다 3pt(Req) 결과가 더 앞에 있어 우선순위 확인에 아쉬움이 있었습니다.

## Modifications (수정 내용)

- **Partial Validation Logic**:
  - `ui_tk/batch_dialogs/profiles/saso_t3.py` 내 `SasoT3BatchHandler.calculate_row`를 수정하여 optional 필드 중 하나만 입력된 경우 `BatchRowState.ERROR` 상태로 확실히 리턴하도록 보정하였습니다.
  - optional 필드 양쪽 모두 빈 값이거나, 양쪽 모두 정상 양수값인 케이스에만 `BatchRowState.OK`가 되도록 로직을 다듬었습니다.
- **Header Formatting & Ordering**:
  - `SASO_T3_MATRIX_SPEC.result_metrics`를 수정하여 4-point 결과(`opt_*`)를 3-point 결과(`req_*`)보다 앞으로 오도록 순서를 바꿨습니다.
  - Label 문구를 `Req`에서 `3pt`로 변경하여 `3pt CSPF`, `3pt CSTL`, `3pt CSEC`와 `4pt CSPF`, `4pt CSTL`, `4pt CSEC` 형식으로 통일되게 개선했습니다.

## Test Reinforcement (테스트 보강 내용)

- `tests/test_ui_tk_saso_t3_batch_dialog.py` 내의 테스트를 강화하여 아래 사항들을 엄격히 검증합니다:
  - `min_35` 관련 필드가 둘 다 빈 값일 때는 `BatchRowState.OK`이고 4pt 결과는 공백.
  - capacity만 입력되거나 power만 입력된 partial case는 `BatchRowState.ERROR`.
  - optional 값 중 음수 등 non-positive invalid 값이 포함되면 `BatchRowState.ERROR`.
  - spec result keys 순서가 4pt first, 3pt second인지 검증.
  - result labels에서 "Req" 문자열이 모두 배제되었는지 검증.

## Document and Project Log Sync (문서 동기화 상태)

- **326 Report Update**: `result_reports/active/326_saso_t3_batch_dialog_implementation.md` 하단에 correction note를 명확히 기록해 두었습니다.
- **WORK_PLAN**: `docs/WORK_PLAN.md`에 327 correction 완료 내용을 간결하게 기록하고 Next Actions 순서를 유지했습니다.
- **project_log.md**: 규칙에 따라 project_log.md는 전혀 수정하지 않고 원본 상태를 유지했습니다.

## Verification & Test Results (검증 결과)

- `python3 -B -m pytest tests/test_ui_tk_saso_t3_batch_dialog.py` 결과, 4개 focused tests가 성공적으로 통과하였습니다.
- `python3 -B -m pytest tests/test_ui_tk_iso_saso_t3_controller_switch.py tests/test_ui_tk_metric_input_table_validation.py` 결과, 35개 테스트가 모두 성공하였습니다.
- `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py` 결과, 54개 테스트가 모두 성공하여 기존 auto-calc 및 switch 동작이 안전하게 보존됨을 확인했습니다.
- `git diff --check` 결과, whitespace 및 EOF 관련 에러가 없음을 확인했습니다.
- `tools/check_code_structure.py` 도구의 architecture layer boundary 규칙을 완전히 충족했습니다.

## Excluded Areas (제외 범위)

- `project_log.md` 파일은 수정 금지 대상이므로 변경하지 않았습니다.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 재생성은 작업 지시에 따라 생략하였습니다.
- PyQt5 및 Core calculator calculation/result schema 변동은 없습니다.

## Next Actions (향후 작업)

1. **Batch foundation foldering audit**
2. **Batch foundation foldering implementation**
3. **Calculator entrypoint handover from PyQt to Tkinter**
4. **ui_tk root folder inventory audit**
5. **EN14825 / AHRI 210/240 / KS profile expansion**

## Active Report Count Status (액티브 리포트 수 상태)

- active report count meets lifecycle threshold criteria. (활성 리포트 수가 임계 기준에 맞춰 유지되고 있으며, 이후 batch foundation 작업 도중 report archive 처리가 수반될 것을 제안합니다.)
