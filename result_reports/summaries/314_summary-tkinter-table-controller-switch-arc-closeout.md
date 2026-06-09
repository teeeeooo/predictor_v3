# Summary 314: Tkinter Table Controller Switch Arc Closeout

## Executive Summary

본 문서는 legacy `ExcelLikeTableController`에서 `TkTableController` + `interaction_core.py` 공통 기반으로의 마이그레이션 및 SASO T3 validation 정렬, codebase reference map 도구 고도화 및 재생성까지 포함하는 `ui_tk controller switch` 아크의 최종 요약본이다.

## Summary Coverage (대상 범위)

본 요약본은 아래의 active reports(총 16개)를 커버하고 아카이빙한다:
- [298_controller_switch_expansion_readiness_preflight.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/298_controller_switch_expansion_readiness_preflight.md)
- [299_implement_hong_kong_hspf_controller_switch.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/299_implement_hong_kong_hspf_controller_switch.md)
- [300_fix_tk_table_controller_type_replace_selection_carryover.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/300_fix_tk_table_controller_type_replace_selection_carryover.md)
- [301_post_type_replace_selection_fix_gui_smoke_closeout.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/301_post_type_replace_selection_fix_gui_smoke_closeout.md)
- [302_implement_iso_iseer_2point_section_controller_switch.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/302_implement_iso_iseer_2point_section_controller_switch.md)
- [303_post_2point_controller_switch_gui_smoke_closeout.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/303_post_2point_controller_switch_gui_smoke_closeout.md)
- [304_implement_iso_saso_t3_section_controller_switch.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/304_implement_iso_saso_t3_section_controller_switch.md)
- [305_code_checker_and_reference_map_gate_audit.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/305_code_checker_and_reference_map_gate_audit.md)
- [306_align_305_code_checker_audit_with_original_intent.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/306_align_305_code_checker_audit_with_original_intent.md)
- [307_saso_t3_section_input_validation_alignment.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/307_saso_t3_section_input_validation_alignment.md)
- [308_post_saso_t3_controller_switch_validation_gui_smoke_closeout.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/308_post_saso_t3_controller_switch_validation_gui_smoke_closeout.md)
- [309_reference_evidence_gate_warning_first_workflow_patch.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/309_reference_evidence_gate_warning_first_workflow_patch.md)
- [310_code_checker_metadata_freshness_improvement.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/310_code_checker_metadata_freshness_improvement.md)
- [311_code_checker_task_number_label_decoupling.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/311_code_checker_task_number_label_decoupling.md)
- [312_regenerate_codebase_reference_map.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/312_regenerate_codebase_reference_map.md)
- [313_controller_switch_arc_final_summary_closeout.md](file:///Users/sunjaekim/Downloads/%ED%83%9C%EC%9A%B0%20%EC%9E%91%EC%97%85/predictor_v3/result_reports/archive/313_controller_switch_arc_final_summary_closeout.md)

## Key Achievements (주요 완료 내용)

1. **Table Controller Migrations**:
   - Hong Kong HSPF, Hong Kong CSPF, ISO/ISEER 2-Point, SASO T3의 모든 table controller를 legacy `ExcelLikeTableController`에서 공통 `TkTableController`로 성공적으로 이관 완료.
   - type-replace selection carryover 및 focus/undo/paste/clear 기능과의 정렬 완료.
2. **SASO T3 Validation Alignment**:
   - `IsoSasoT3Section`의 로컬 positivity 파싱 우회 문제를 해결하고, `MetricInputTable` 표준 visual invalid marking API와 연계하여 red cell painting 및 required/optional partial fallback calculation 정상 구현.
3. **iMac GUI Smoke Validation**:
   - iMac Aqua/Tk native GUI 환경에서 각 controller switch 대상 및 validation recovery에 대해 3회에 걸친 manual smoke closeout을 완료.
4. **Code Checker & Reference Map Calibration**:
   - Reference Evidence Gate에 warning-first preflight checklist 적용.
   - `tools/code_checker`에 Git commit, dirty 여부 등의 metadata 임베딩 기능 및 non-hard-gate freshness check CLI 옵션 추가.
   - 하드코딩된 task number 결합 해제 후 `CODEBASE_REFERENCE_MAP.md`를 성공적으로 재생성하여 codebase structure map을 동기화함.

## Architecture Design: MVC & SoC Summary

- **View Layer**: `MetricInputTable`이 cell grid presentation 및 visual invalid state 하이라이트 표현을 전담.
- **Controller Layer**: `TkTableController` + `interaction_core.py`가 paste stack, undo history, cell data sync의 controller 관심사 전담.
- **Model / Section Layer**: `IsoSasoT3Section`과 같은 도메인 section 클래스가 business validation rules, positivity constraints, calculator dispatching 관심사 전담.

## Known Limitations / Risks

- **Commit Freshness Discrepancy**: 재생성된 map의 metadata에 기록된 commit short hash와 새 커밋 생성 후의 HEAD commit short hash 사이에 불일치(stale warning)가 발생하는 것은 git versioning상 정상 동작이며, 다음 아크 작업 개시 전에 regeneration할 것을 권장하는 evidence로 작동함.

## Next Action Suggestions

1. **Main table migration check**: legacy table 클래스들을 공통 table foundation으로 수렴하기 위한 preflight 점검.
2. **ui_tk folder cleanup**: window/table 안정화 이후 compatibility wrapper 및 중복 helper 정리.
3. **EN14825 / AHRI 210/240 / KS profile expansion**.

---
*Note: active report count exceeds lifecycle threshold; cleanup pending.*
