# Active Report 360: EN14825 SEER Data Model, Table Model, and Adapter Foundation Slice

## 목표 (Goal)
* EN14825 declared/tested GUI design contract에 따라 SEER 전용 data model, table model, adapter를 구현하여 SEER 계산/표시 모델의 foundation을 확립한다.
* 이번 작업은 계산/표시 모델의 foundation slice이며, 실제 EN14825 section 화면 조립, profile selector 연결, 실시간 GUI event binding은 다음 slice로 분리한다.

## 기준으로 확인한 docs/reports/files (Reference Sources)
* [AGENT_TASK_ROUTER.md](../../AGENT_TASK_ROUTER.md): UI / Calculator Adapter / Tests / Result Report Workflow / Reference Evidence Gate 섹션
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md): History 및 Recommended Next Action
* [docs/designs/2026-06-10-en14825-declared-tested-gui-contract.md](../../docs/designs/2026-06-10-en14825-declared-tested-gui-contract.md): SEER UI 계약 사항
* [result_reports/active/357_en14825_declared_tested_gui_design_contract.md](357_en14825_declared_tested_gui_design_contract.md): UI 및 batch 정책
* [result_reports/active/358_en14825_gui_contract_correction.md](358_en14825_gui_contract_correction.md): defaults, threshold(92%) 보정 사항
* [result_reports/active/359_en14825_defaults_hierarchy_contract_correction.md](359_en14825_defaults_hierarchy_contract_correction.md): defaults hierarchy open question 보정 사항
* `apps/calculator/ui/sections/iso_iseer_2point_section.py`: 기존 table, adapter 호출 패턴 참고

## 생성 파일 (Created Files)
* [apps/calculator/ui/en14825/__init__.py](../en14825/__init__.py): package exports 정의
* [apps/calculator/ui/en14825/seer_models.py](../en14825/seer_models.py): inputs, computed, result summaries 데이터 모델 정의
* [apps/calculator/ui/en14825/seer_adapter.py](../en14825/seer_adapter.py): W->kW 변환, EER/derived power 계산, core 호출 및 fallback 처리
* [apps/calculator/ui/en14825/seer_table_model.py](../en14825/seer_table_model.py): row/column keys/labels, values, editability 및 cell state metadata를 제공하는 headless table model 정의
* [tests/test_apps_calculator_ui_en14825.py](../../tests/test_apps_calculator_ui_en14825.py): 9개의 unit tests로 data model, adapter, table model 검증

## 수정 파일 (Modified Files)
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md)

## Model/Adapter/Table 책임 분리 요약 (Responsibility Separation)
* **`seer_models.py`**:
  * `SeerPointInput` 및 `SeerPointComputed`로 각 테스트 포인트(A, B, C, D)의 원시 입력(W) 및 계산된 EER/전력/비교% 및 cell state(tinting 용도) 상태 보관.
  * `SeerResultSummary`로 최종 SEER 결과 및 status 텍스트 관리.
* **`seer_adapter.py`**:
  * UI의 W 단위 입력을 core가 기대하는 kW 단위로 변환(`W / 1000.0`).
  * `declared_power = declared_capacity / declared_eer` 및 `tested_eer = tested_capacity / tested_power` 내부 유도.
  * `calculate_seer`를 안전하게 래핑하여 complete set 검증 및 try-except 블록을 통한 crash 방지.
  * `tj` 외기온도 및 `p_design_c_w`, `t_design_c`를 바탕으로 part load 비율(%) 및 part load W를 구하는 helper method 제공.
* **`seer_table_model.py`**:
  * Tkinter widget 종속성이 전혀 없는 순수 headless 테이블 모델.
  * `get_value`와 `get_state` 메서드로 visual component에 포맷팅된 문자열과 state metadata(neutral/pass/invalid/unavailable)를 실시간 바인딩 방식으로 제공.

## Declared/Tested 지원 범위 (Fallback Logic)
* **Declared-only**: Declared complete set이 있을 때 계산 가능. Tested 및 비교%는 `None` 및 `unavailable`.
* **Tested-only**: Tested complete set이 있을 때 계산 가능. Declared 및 비교%는 `None` 및 `unavailable`.
* **Declared + Tested**: 둘 다 complete일 때 최종 EER%, Capacity% 및 SEER% 비교 계산 수행.
* missing input 또는 zero/negative denominator가 입력되어도 crash 없이 `None` 및 `unavailable` 상태 처리.

## Comparison State / Threshold 요약
* **Capacity %** = tested / declared * 100: `< 90%` 또는 `>= 110%` 이면 `invalid` (red), 그 외 `pass` (pale green).
* **EER %** = tested / declared * 100: `< 90%` 이면 `invalid` (red), 그 외 `pass` (pale green).
* **Final SEER %** = tested / declared * 100: `< 92%` 이면 `invalid` (red), 그 외 `pass` (pale green) (upper bound 없음).

## 구현하지 않은 범위 (Non-goals in this slice)
* EN14825 SCOP 구현 및 batch 계산 구현.
* 실제 GUI widget (layout, guide card, result panel, section) 조립 및 실시간 GUI event binding.
* core/calculator_en14825.py 및 data/region_configs 수정.

## 검증 결과 (Verification Results)
* `python3 -m py_compile $(find apps/calculator/ui -name "*.py")`: **OK**
* `python3 -m pytest tests/test_apps_calculator_ui_en14825.py -q`: **9 passed**
* `python3 -B tools/check_code_structure.py`: **code structure guard: OK (no findings)**
* `git diff --check`: whitespace 에러 없음.
* `git status --short`: 신규 패키지 및 테스트 파일 생성, WORK_PLAN.md 외의 변경 없음.

## Next Action
* **EN14825 SEER section integration with real-time updates** 구현 (GUI 화면 조립 및 controller event binding).
