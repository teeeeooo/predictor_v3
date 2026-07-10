# Summary 364: PyQt Retirement, EN14825 SEER Foundation, and Source Owner Guard

## Covered Reports
* [347_active_report_lifecycle_cleanup_after_apps_calculator_relocation.md](../archive/347_active_report_lifecycle_cleanup_after_apps_calculator_relocation.md)
* [348_lifecycle_summary_wording_correction.md](../archive/348_lifecycle_summary_wording_correction.md)
* [349_calculator_pyqt_reference_retirement_preflight.md](../archive/349_calculator_pyqt_reference_retirement_preflight.md)
* [350_349_report_local_link_correction.md](../archive/350_349_report_local_link_correction.md)
* [351_mixed_iso_table_test_split_or_retirement.md](../archive/351_mixed_iso_table_test_split_or_retirement.md)
* [352_351_report_wording_validation_note_correction.md](../archive/352_351_report_wording_validation_note_correction.md)
* [353_pyqt_calculator_only_source_retirement.md](../archive/353_pyqt_calculator_only_source_retirement.md)
* [354_pyqt_calculator_docs_support_matrix_update.md](../archive/354_pyqt_calculator_docs_support_matrix_update.md)
* [355_test_package_naming_cleanup_audit.md](../archive/355_test_package_naming_cleanup_audit.md)
* [356_stale_ui_tk_structure_guard_cleanup.md](../archive/356_stale_ui_tk_structure_guard_cleanup.md)
* [357_en14825_declared_tested_gui_design_contract.md](../archive/357_en14825_declared_tested_gui_design_contract.md)
* [358_en14825_gui_contract_correction.md](../archive/358_en14825_gui_contract_correction.md)
* [359_en14825_defaults_hierarchy_contract_correction.md](../archive/359_en14825_defaults_hierarchy_contract_correction.md)
* [360_en14825_seer_model_adapter.md](../archive/360_en14825_seer_model_adapter.md)
* [361_en14825_seer_model_adapter_correction.md](../archive/361_en14825_seer_model_adapter_correction.md)
* [362_source_file_owner_boundary_policy_audit.md](../archive/362_source_file_owner_boundary_policy_audit.md)
* [363_source_file_owner_boundary_guard_implementation.md](../archive/363_source_file_owner_boundary_guard_implementation.md)

## Workstream Summary

### 1. PyQt Legacy UI Retirement (Reports 349-354)
* **목표**: 마이그레이션이 완전히 종료된 레거시 PyQt5 전용 계산기 코드 및 관련 테스트 케이스들을 안전하게 은퇴(삭제)시켜 코드베이스 용량을 줄이고 유지보수 효율성을 극대화한다.
* **진행 내용**:
  * `ui/calc_window.py`, `ui/calculators_2point.py`, `ui/calculator_errors.py` 등 레거시 calculator 전용 소스들을 완전히 삭제하고, generic UI 패키지와의 결합을 방지하기 위해 `ui/spreadsheet_table.py`와 `ui/theme.py`만 quarantine/hold 상태로 분리하여 유지하였습니다.
  * `test_ui_calc_window_smoke.py`, `test_ui_calculators_2point.py` 등 레거시 테스트 파일 5개를 함께 삭제/정리하였습니다.
  * `project_architecture.md`, `project_brief.md`, `pyqt_test_support_matrix.md` 등의 문서를 갱신하여 PyQt UI 은퇴 상태 및 지원 범위를 최신화하였습니다.

### 2. Naming & Relocation Cleanup (Reports 347, 348, 355, 356)
* **목표**: `ui_tk/` relocation 및 apps 패키지 마이그레이션 이후 잔존한 stale 파일, 문서, 그리고 파일 네이밍 불일치를 정리한다.
* **진행 내용**:
  * relocation 및 preflight 관련 active report들을 lifecycle summary 346으로 묶고 아카이브 처리하였습니다.
  * `tools/check_code_structure.py`에서 불필요해진 레거시 `ui_tk` 임포트 배제 검사 규칙을 정리하여 structure guard 경고를 clean하게 조율하였습니다.
  * `tests/` 디렉토리 내의 test 파일 네이밍(`test_ui_tk_*`) 정리를 위한 audit을 완료하고, safe renaming 로드맵을 확정하였습니다. (실제 실행은 push 위험성을 고려해 deferred)

### 3. EN14825 SEER Foundation (Reports 357-361)
* **목표**: EN14825 declared/tested 규격에 부합하는 GUI design contract 및 SEER 전용 data model, table model, adapter를 독립 패키지 내에 완결된 구조로 구축한다.
* **진행 내용**:
  * **Design Contract**: absolute link 제거, SCOP prefill defaults, A/B/C/D 조건 확정, final SEER % threshold를 `< 92%`로 보정하는 등 GUI 계약을 완성하였습니다.
  * **Defaults Hierarchy**: config 파일과 UI prefill defaults를 명확히 분리하여 prefill defaults는 완전한 user-editable prefill 값임을 정립하였습니다.
  * **SEER models & adapter**: `declared_power`를 `declared_power_w_for_core` 내부용 필드로 명시화하여 UI row 노출을 차단하였으며, 한국어 메시지 대신 status_code를 반환하도록 SoC를 분리하였습니다.
  * **Zero/Negative handling**: $capacity/power \le 0$ 또는 None일 때 crash 없이 unavailable/invalid cell state로 안전하게 귀결되도록 adapter 계산 로직의 강건성을 다졌습니다.

### 4. Source File Owner Boundary Policy & Guard (Reports 362, 363)
* **목표**: 소스 파일 생성 시 broad folder에 flat하게 흩뿌려지는 부채를 원천 차단하기 위해 repo-wide 규칙을 세우고, 정적 검사기(guard)에 차단 및 경고 규칙을 자동화한다.
* **진행 내용**:
  * **Source file owner boundary policy**: (1) 신규 파일 생성 전 도메인/피처 소유주 결정, (2) UI root/sections/core root에 feature-specific flat file 생성 금지, (3) 확장성이 큰 피처는 feature package 디렉토리 신설을 원칙으로 삼았습니다.
  * **AGENT_TASK_ROUTER preflight**: 신규 소스 생성 시에만 질의되는 5단계 preflight 절차를Task Triage 영역에 추가하였습니다.
  * **Guard Implementation**: `tools/check_code_structure.py`에 UI root flat 파일 차단, sections flat 어댑터/모델 차단, core root flat helper 생성 경고, tests mega-test 생성 경고, allowed package registry 경고 등 5개 규칙을 pure helper로 구현하고 pytest로 검증 완료하였습니다.

## Completed Decisions
* **PyQt UI 은퇴**: calculator 전용 PyQt5 뷰 파일들을 물리적으로 제거하고, generic `ui/` 폴더 역할을 train/predict 전용으로 제한하였습니다.
* **EN14825 UI 계약 및 prefill defaults**: prefill defaults는 config의 maximum/minimum limits 검증과 구분되는 독립적 prefill defaults로 작용하고, 사용자의 편집에 의한 resolve value가 core 계산에 사용됩니다.
* **Source Owner Boundary 및 Preflight 강제**: 신규 소스 파일 생성 시 preflight 절차가 task 수준에서 강제됩니다. UI root flat file이나 sections/ 하위의 어댑터/모델 파일 생성은 structure guard에서 즉시 에러로 차단됩니다.

## Verification Summary
* **PyQt Retirement**:
  * `python3 -B tools/check_code_structure.py`: **OK**
  * `pytest`: 관련 obsolete test 5개 제거 완료 후 전체 test가 정상 동작함을 확인.
* **EN14825 SEER Foundation**:
  * `tests/test_apps_calculator_ui_en14825.py`: **12 passed** (FakeCalculator stub을 통한 W->kW conversion 검증 및 zero/negative, point-level/final thresholds 테스트 완료).
* **Source Owner Guard**:
  * `tests/test_code_structure_guard.py`: **29 passed** (신규 가드 5개에 대한 pure unit tests 추가 검증 완료).
  * `python3 -B tools/check_code_structure.py`: **OK (no findings)** (현재 repo가 새로운 strict guard를 정상 통과함을 확인).

## Archived Report List
위 Covered Reports에 기술된 17개의 active report들이 본 summary에 의해 커버링되므로 `result_reports/archive/` 로 일괄 이동(archived) 처리됩니다.

## Reports Kept Active and Reason
* **None**: 현재 cleanup 기준을 넘는 모든 active report들이 완료 및 summary로 커버 가능하여 active에 남겨지는 report는 없습니다.

## Remaining Risks or Next Action
* **Active report lifecycle cleanup**: 완료
* **EN14825 SEER section integration with real-time updates**: 다음 workstream으로 추천되며, GUI 화면 조립 및 controller event binding을 다룹니다.
* **Test/package naming cleanup execution**: `test_ui_tk_*` -> `test_apps_calculator_ui_*` 변경 작업은 push 위험성을 고려하여 필요 시 deferred action으로 유지합니다.

## Project Memory Seed Sync Judgment
* **판단**: 본 arc에서 확정된 "Source File Owner Boundary Policy" 및 "EN14825 prefill defaults hierarchy"는 향후 다른 피처 확장 시 참고해야 할 핵심 의사결정이므로 memory seed에 최소한의 neutral key facts로 추가 갱신이 필요하다고 판단하였습니다.

## project_log Sync Judgment
* **판단**: `project_log.md`는 이미 이 summary 및 memory seed가 충분히 covering하고 있어 중복 기록을 피하기 위해 갱신하지 않습니다 (not updated).
