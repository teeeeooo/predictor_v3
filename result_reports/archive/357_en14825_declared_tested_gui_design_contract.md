# Active Report 357: EN14825 Declared/Tested GUI Design Contract

## 목표 (Goal)
* EN14825 GUI 구현 전에 declared/tested 기반 UI 계약을 문서화한다.
* 이번 작업은 design contract 작성 전용이며, production source, tests, apps/calculator/ui 구현은 수정하지 않는다.
* 이미지 mockup은 전달하지 않으며, 프롬프트의 텍스트 계약과 기존 코드/문서 확인 결과로만 구현 기준을 정한다.

## 기준으로 사용한 docs/code/reports (Reference Sources)
* [AGENT_TASK_ROUTER.md](../../AGENT_TASK_ROUTER.md): Documentation Sync / Result Report Workflow / Reference Evidence Gate / UI 관련 섹션
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md): Recent history와 Next Actions
* [core/calculator_en14825.py](../../core/calculator_en14825.py): `calculate_seer` / `calculate_scop` public API와 input/output shape
* [data/region_configs/en14825_scop.json](../../data/region_configs/en14825_scop.json): SCOP climate defaults 및 schema
* [data/region_configs/eu.json](../../data/region_configs/eu.json): SEER 규격 정보 및 test point 기온 데이터
* [result_reports/active/349_calculator_pyqt_reference_retirement_preflight.md](349_calculator_pyqt_reference_retirement_preflight.md): EN/AHRI/KS reference inventory 중 EN 부분
* [result_reports/active/353_pyqt_calculator_only_source_retirement.md](353_pyqt_calculator_only_source_retirement.md): PyQt source retirement 상태
* [result_reports/active/354_pyqt_calculator_docs_support_matrix_update.md](354_pyqt_calculator_docs_support_matrix_update.md): retired/current path 상태

## Core API Contract 요약
* **SEER (`calculate_seer`)**:
  * Input: `test_points` (A, B, C, D key, value는 kW 단위 `(capacity, power)`), `p_to`, `p_sb`, `p_ck`, `p_off`, `p_design_c` (모두 kW 단위).
  * Output: `{"seer": float, "seer_on": float, "qc_kwh": float}`.
* **SCOP (`calculate_scop`)**:
  * Input: `test_points` (A, B, C, D, TOL, Tbiv key, value는 kW/°C 단위 `{"capacity": float, "power": float, "temp_c": float}`), `p_to`, `p_sb`, `p_ck`, `p_off`, `p_design_h` (kW 단위), `climate` (average/warmer/colder), `tbiv_temp_c`, `tol_temp_c`.
  * Output: `{"scop": float, "SCOP": float, "scop_on": float, "qh_kwh": float, "bin_details": list}`.

## Design Contract 문서 경로
* [docs/designs/2026-06-10-en14825-declared-tested-gui-contract.md](../designs/2026-06-10-en14825-declared-tested-gui-contract.md)

## 확정된 UI 계약 요약 (UI Contract Summary)
* **단위 변환**: UI 입력 단위는 **W**이며, core 계산기 호출 직전 UI adapter/controller 경계에서 **kW**로 변환한다 (`W / 1000.0`). 출력값 중 에너지 소모량은 **kWh** 단위를 유지한다.
* **Declared / Tested 데이터 모델**:
  * Declared EER/COP를 통해 내부 adapter에서 `declared_power = declared_capacity / declared_eer_or_cop`를 계산하여 core 입력으로 사용한다. UI에는 `Declared power` row를 노출하지 않는다.
  * Tested EER/COP는 `tested_capacity / tested_power`로 자동 계산하여 read-only로 표시한다.
  * Declared-only, Tested-only, Declared + Tested 계산을 유연하게 처리하며, 어느 한 쪽이 누락되어도 에러를 띄우지 않고 가용한 계산만 수행한다.
* **비교 % 및 판정**:
  * Declared와 Tested가 모두 있는 경우에만 point별 비교 % 및 최종 SEER/SCOP %를 표시한다.
  * 별도의 OK/NG 텍스트는 표시하지 않으며, % cell의 배경색으로만 판정한다.
  * 판정 기준: Capacity % < 90% 또는 Capacity % >= 110% 이면 pale red(tinted) cell / EER % < 90% 또는 COP % < 90% 이면 pale red(tinted) cell / 그 외는 normal/pale green(pass-tinted) cell.
  * 최종 결과 판정: Final SEER % / SCOP %가 **92% 미만**이면 red-tinted cell로 표시하고, 92% 이상이면 normal/pass-tinted cell로 표시한다 (upper bound limit 적용 없음).
* **SEER GUI**:
  * Columns: A(35°C), B(30°C), C(25°C), D(20°C).
  * Main table + right guide card (two-column layout) + bottom result panel.
  * Real-time calculation 방식 (Calculate 버튼 없음).
* **SCOP GUI**:
  * Climate card: Average (default active), Warmer, Colder. 다중 활성화 및 개별 독립 계산 지원.
  * Climate card별 auxiliary inputs: Pdesign_h [W], Tbiv [°C], TOL [°C]. (Default: Average Tbiv -10°C, TOL -11°C / Warmer Tbiv 2°C, TOL -11°C / Colder Tbiv -15°C, TOL -22°C 와 같이 user-editable default 적용).
  * Columns: A, B, C, D, TOL, Tbiv. Test point 온도는 config 및 user overrides를 동적으로 표기.
* **Guide Cards**:
  * SEER: `SEER Test Conditions` (A/B/C/D outdoor DB temp 및 part load ratio만 표시, wet-bulb/indoor/symbolic 설명 제외).
  * SCOP: `SCOP Test Conditions` (A/B/C/D/TOL/Tbiv outdoor DB temp 및 part load ratio 표시, wet-bulb은 config에 있을 때만 포함, indoor/symbolic 설명 제외).
  * Guide card는 helper text일 뿐이며 계산 소스로 사용하지 않는다.
* **Visual Style**: Clean light engineering-tool look (light gray background, white cards, subtle borders, blue active accent, pale green/red cell tinting). 기존 `apps/calculator/ui` architecture pattern (section owner, thin adapter boundary, reusable table/result components, existing layout token reuse)을 엄격히 준수한다.

## Batch 정책 요약 (Batch Contract Summary)
* Batch 기능은 이번 slice에서 구현하지 않는다.
* Batch 계산은 Tested-only 모드로 제한하며 Declared 입력은 포함하지 않는다.
* Standby 파라미터는 dialog-level 공통 입력으로 처리한다.
* SEER batch: p_design_c 및 A/B/C/D tested capacity/power를 row input으로 입력받는다.
* SCOP batch: single climate 지정 방식(dialog-level)이며, p_design_h, Tbiv, TOL 및 6개 포인트의 tested capacity/power를 row input으로 입력받는다. 다중 기후 동시 batch는 배제한다.

## 구현하지 않은 범위 (Non-goals)
* EN14825 GUI, batch 기능 및 타 profile (AHRI, KS) 실제 코드 구현.
* production Python 코드 변경 및 테스트 코드 변경.
* data/region_configs 수정.

## WORK_PLAN 업데이트 여부
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md)의 Recent History에 357번 항목(design contract 완료)을 추가하고, Next Actions의 1순위 추천 대상을 `EN14825 SEER data model/table model/adapter`로 업데이트하였다.

## 검증 결과 (Verification Results)
* `git status --short`: 수정되거나 새로 생성된 파일 리스트 확인 완료.
* `python3 -B tools/check_code_structure.py`: 실행 결과 이상 없음.
* `git diff --check`: whitespace 에러 없음.

## Next Action
* **EN14825 SEER data model/table model/adapter** 구현 및 테스트/검증.
