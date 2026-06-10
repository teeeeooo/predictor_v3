# Active Report 361: EN14825 SEER Model, Adapter, and Table Model Correction

## 목표 (Goal)
* 360에서 구현한 EN14825 SEER data model, table model, adapter를 section integration 단계 전에 보조하여, 내부/외부 필드 분리, status code 구조화, zero/negative 처리 일관화, 그리고 테스트 명시성과 커버리지를 보강한다.
* 이번 작업은 correction slice이며, 실제 EN14825 section 화면 조립, profile selector 연결, 실시간 GUI event binding은 수행하지 않는다.

## 기준으로 확인한 docs/reports/files (Reference Sources)
* [AGENT_TASK_ROUTER.md](../../AGENT_TASK_ROUTER.md): UI / Calculator Adapter / Tests / Result Report Workflow / Reference Evidence Gate 섹션
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md): History 및 Recommended Next Action
* [docs/designs/2026-06-10-en14825-declared-tested-gui-contract.md](../../docs/designs/2026-06-10-en14825-declared-tested-gui-contract.md): SEER UI 계약 사항
* [result_reports/active/360_en14825_seer_model_adapter.md](360_en14825_seer_model_adapter.md): 이전 foundation slice 구현 결과

## 수정 파일 (Modified Files)
* [apps/calculator/ui/en14825/seer_models.py](../en14825/seer_models.py): declared_power 필드명 변경 및 status_code 도입
* [apps/calculator/ui/en14825/seer_adapter.py](../en14825/seer_adapter.py): status_code 반환, zero/negative 처리 일관화
* [apps/calculator/ui/en14825/seer_table_model.py](../en14825/seer_table_model.py): 내부용 필드 노출 차단 주석 및 검증
* [tests/test_apps_calculator_ui_en14825.py](../../tests/test_apps_calculator_ui_en14825.py): FakeCalculator stub 및 threshold tests 보강
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md): 작업 완료 기록 반영

## Correction 요약 (Correction Details)

### 1. Declared power 내부용 명시 강화
* `declared_power` 필드를 `declared_power_w_for_core`로 변경하여 내부 core 입력 계산용 derived value임을 더 명확히 하였습니다.
* `SeerPointComputed` 내에 "Internal adapter/core-only derived value. Must never be exposed as an editable or display table row." 주석을 명시적으로 달아 row 노출 가능성을 차단하였습니다.
* `SeerTableModel.ROW_KEYS`에 포함되지 않음을 검증하는 테스트(`test_seer_table_model_and_row_protection`)를 추가하여 UI row 노출을 원천적으로 막았습니다.

### 2. Status 구조 보정 (SoC)
* `SeerResultSummary`에서 한국어 사용자 표시 문구(`status: str = "대기 중"`) 대신 status code 중심의 `status_code`와 디버깅용 `message` 필드로 분리하였습니다.
* 반환 가능한 `status_code` 값들을 다음과 같이 정리하였습니다:
  * `idle`: 초기 상태
  * `complete`: 자동 계산 완료
  * `input_incomplete`: 입력 부족
  * `invalid_design_load`: 설계 냉방 부하 검증 실패
  * `invalid_t_design`: t_design_c 검증 실패
  * `declared_error` / `tested_error`: core 계산 중 Exception 발생
* 사용자 표시용 한국어 문구 매핑 및 GUI 표시는 이번 slice 범위가 아니므로 뷰 레이어 바인딩 단계로 이관하였습니다.

### 3. Zero/Negative 처리 일관화
* capacity, power, EER $\le 0$인 경우의 point-level comparison 및 complete set 판단 기준을 일관되게 정돈하였습니다:
  * inputs $\le 0$ 인 경우, cell state를 `invalid`로 일관되게 처리하고 point-level comparison 계산을 수행하지 않습니다.
  * inputs가 제공되지 않은 누락 상태(None)인 경우, cell state를 `unavailable`로 처리합니다.
  * tested_capacity $\le 0$, tested_power $\le 0$, declared_capacity $\le 0$, declared_eer $\le 0$ 등의 분모/분자 조건 모두에서 positive 값 조합인 경우에만 tested EER, capacity %, EER % 등의 계산을 수행하여 division by zero 및 음수 비율 계산으로 인한 crash를 방지합니다.

### 4. 테스트 보강 (Test Coverage Expansion)
* **W -> kW conversion 검증**: `FakeCalculator` stub을 구현하여 `p_design_c_w`, `p_to_w`, `p_sb_w`, `p_ck_w`, `p_off_w`, 그리고 각 포인트의 capacity/power W 값들이 core로 전달될 때 정확히 `kW` 단위(`W / 1000.0`)로 변환되어 전달되는지 100% controlled stub 검증을 추가하였습니다.
* **Missing datasets**:
  * missing declared인 경우 tested-only calculation만 완수되는지 확인.
  * missing tested인 경우 declared-only calculation만 완수되는지 확인.
* **Point-level & Final Thresholds**:
  * capacity % < 90 및 >= 110 invalid 상태 전환 검증.
  * EER % < 90 invalid 상태 전환 검증.
  * final SEER % < 92 invalid 상태 전환 검증.
  * final SEER % >= 92 pass 상태 전환 검증.
* **Zero/Negative values**: zero/negative 입력 시 crash 없이 정상적으로 incomplete/invalid state가 반환되는지 검증 완료.

## 구현하지 않은 범위 (Non-goals in this slice)
* EN14825 SCOP 구현 및 batch 계산 구현.
* 실제 GUI widget (layout, guide card, result panel, section) 조립 및 실시간 GUI event binding.
* core/calculator_en14825.py 및 data/region_configs 수정.

## 검증 결과 (Verification Results)
* `python3 -m py_compile apps/calculator/ui/en14825/*.py`: **OK**
* `python3 -m pytest tests/test_apps_calculator_ui_en14825.py -q`: **12 passed**
* `python3 -B tools/check_code_structure.py`: **code structure guard: OK (no findings)**
* `git diff --check`: whitespace 에러 없음.
* `git status --short`: `docs/WORK_PLAN.md` 수정, `result_reports/active/361_en14825_seer_model_adapter_correction.md` 신규 생성 외 clean.

## Next Action
* **EN14825 SEER section integration with real-time updates** 구현 (GUI 화면 조립 및 controller event binding).
