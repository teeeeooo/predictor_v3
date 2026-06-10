# 326 SASO T3 Batch Dialog Implementation

## Goal (목표)

- Hong Kong CSPF 및 ISO 2-point batch dialog에서 정립된 `BatchDialogShell` + `profiles/` 구조를 재사용하여 SASO T3 batch dialog를 성공적으로 구현하고 통합한다.
- SASO T3의 required (3-point) 입력 및 optional 35 Min (4-point) 입력 정책을 보존한다.
- `BatchDialogShell`과의 명확한 boundaries를 준수하여 profile adapter만 개별 profile 특화 로직을 갖도록 격리한다.

## Research & Checked Shapes (확인한 기존 규격 및 화면 형태)

- **Input Keys**: `full_46_capacity`, `full_46_power`, `full_35_capacity`, `full_35_power`, `half_35_capacity`, `half_35_power` (필수 6개) + `min_35_capacity`, `min_35_power` (선택 2개).
- **Optional 35 Min Policy**: 필수 6개 필드가 채워지면 3-point calculations (`required_only` 모드)이 수행되고 정상 EER/CSPF/CSTL/CSEC가 결과 컬럼에 안착한다. 선택 35 Min 필드가 채워지면 4-point calculations (`with_optional_test` 모드)도 수행된다. 만약 선택 필드가 비어있으면 4-point 결과는 빈 문자열로 표시되며 `BatchRowState.OK` 상태가 유지된다. 둘 중 하나만 입력되거나 비정상 입력 시 `BatchRowState.ERROR`로 처리된다.
- **Result Schema / Display Columns**: `req_cspf`, `req_cstl`, `req_csec`, `opt_cspf`, `opt_cstl`, `opt_csec`.

## Created Files (생성 파일)

- `ui_tk/batch_dialogs/profiles/saso_t3.py`: SASO T3 batch profile-specific matrix spec, calculation handler, matrix controller, batch section, profile adapter, and dialog wrapper.
- `tests/test_ui_tk_saso_t3_batch_dialog.py`: SASO T3 batch dialog open/close, snapshot save/restore, and batch calculation handler unit/focused tests.

## Modified Files (수정 파일)

- `ui_tk/batch_dialogs/profiles/__init__.py`: `SasoT3BatchDialog`를 package-level로 export 하도록 등록.
- `ui_tk/sections/iso_saso_t3_section.py`: "Multi 입력" 버튼 추가 및 `SasoT3BatchDialog`를 연결하여 snapshot save/restore 연계.
- `tests/test_ui_tk_iso_table_autocalc.py`: refit scheduler의 bound method mocking 타겟 버그, SASO T3 invalid input status 변경 및 profile reuse assertion 오정렬을 교정.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: 새 파일 추가 및 코드 구조 변경 사항을 반영하여 재생성.
- `docs/WORK_PLAN.md`: 작업 상태 및 Next Actions 업데이트.
- `project_log.md`: SASO T3 batch dialog implementation 내역 추가.
- `result_reports/active/325_iso_iseer_2point_batch_dialog_report_closeout_correction.md`: closeout note 추가 보정.

## Adaptation Details & Responsibilities (어댑터 및 책임 분할)

- **Common Shell (`BatchDialogShell`)**: Toplevel lifecycle, geometry, close protocol, snapshot handoff.
- **SASO T3 Profile Adapter (`SasoT3BatchAdapter` / `SasoT3BatchHandler`)**:
  - `SASO_T3_MATRIX_SPEC`을 정의하여 Required (3-point)와 Optional (4-point) 비교 컬럼 구조 정립.
  - `SasoT3BatchHandler` 내에서 `required_only` 및 `with_optional_test` 모드로 각각 core dispatcher 호출.
  - required 필드가 누락되었을 때 `BatchRowState.PENDING`으로 복귀하며, 계산 오류 시 `BatchRowState.ERROR` 상태와 cell highlight 적용.

## Section Integration (섹션 통합 내용)

- `IsoSasoT3Section` 내부에 `Multi 입력` 버튼 (`batch_button`)을 생성하고 `saso_t3_batch_open` surface role을 부여.
- `_open_batch_dialog` 및 `_clear_batch_dialog`을 구현하여 기존 2-point/Hong Kong과 일관된 snapshot persistence 흐름 구축.

## Boundaries & Verification (경계 및 검증 결과)

- **Shell / Profile Boundary**: `SasoT3BatchAdapter`는 UI Toplevel geometry나 lifecycle을 직접 관리하지 않고, `BatchDialogShell`에 content frame 빌드 권한을 이관함.
- **Tests**:
  - `tests/test_ui_tk_saso_t3_batch_dialog.py` 신설하여 4개 테스트 케이스 정상 통과 검증.
  - `tests/test_ui_tk_iso_table_autocalc.py`를 포함한 기존 55개 테스트 케이스 교차 정상 통과 확인.
- **Reference Map**: `python3 -B tools/code_checker/build_reference_map.py` 실행 완료하여 FRESH 상태 확인.
- **Code Structure**: `tools/check_code_structure.py` 결과 soft LOC warnings 외 layer boundary 위반 없이 양호.

## Excluded Areas (제외 범위)

- `app_calculator.py` / `app_calculator_tk.py` 등의 entrypoint 리네임이나 리팩토링은 수행하지 않음.
- PyQt5 및 Core calculator calculation/result schema 변동 없음.
- `ui_tk/batch_*.py` foundation 파일 이동/폴더링 배제.

## Next Actions (향후 작업)

1. **Batch foundation foldering audit**
2. **Batch foundation foldering implementation**
3. **Calculator entrypoint handover from PyQt to Tkinter**
4. **ui_tk root folder inventory audit**
5. **EN14825 / AHRI 210/240 / KS profile expansion**

## Active Report Count Status (액티브 리포트 수 상태)

- active report count meets lifecycle threshold criteria. (활성 리포트 개수가 임계점에 도달해 있으므로, 이후 작업 중 summary/archive maintenance 수행을 적극 권장함.)
