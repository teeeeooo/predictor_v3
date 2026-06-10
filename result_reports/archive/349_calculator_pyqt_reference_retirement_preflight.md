# Active Report 349: Calculator PyQt Reference Retirement Preflight

## 목표 (Goal)

* EN14825 / AHRI 210/240 / KS profile expansion 전에 legacy PyQt calculator reference를 retire해도 되는지 preflight audit한다.
* 이번 작업은 read-only inventory와 실행 순서 판단이며, 소스/테스트의 실제 삭제나 이동은 수행하지 않는다.

## 확인한 기준 문서/report (Reference Documents)

* [AGENT_TASK_ROUTER.md](../../AGENT_TASK_ROUTER.md): Documentation Sync / Result Report Workflow / Architecture / UI / Reference Evidence Gate 섹션의 라우팅 정보 확인.
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md): 최신 이력 및 Next Actions 확인.
* [docs/architecture/project_architecture.md](../../docs/architecture/project_architecture.md): 앱 및 UI 경계 정의, 레거시 PyQt 계산기 reference 성격 및 라우팅 계약 확인.
* [154_pyqt-calculator-retirement-audit.md](../archive/154_pyqt-calculator-retirement-audit.md): 레거시 PyQt calculator-only 소스 및 테스트 분류 이력 확인.
* [156_shared-pyqt-utility-retention-decision.md](../archive/156_shared-pyqt-utility-retention-decision.md): shared utility quarantine/hold 결정 사항 및 mixed test blocker 확인.
* [346_summary-batch-foundation-apps-calculator-relocation-closeout.md](../summaries/346_summary-batch-foundation-apps-calculator-relocation-closeout.md): apps/calculator relocation 완료 요약 확인.
* [347_active_report_lifecycle_cleanup_after_apps_calculator_relocation.md](347_active_report_lifecycle_cleanup_after_apps_calculator_relocation.md): 차기 최우선 과제인 preflight 진단 정보 확인.

## Current Runtime Ownership Inventory

현재 canonical calculator entrypoint는 [apps/calculator/app.py](../../apps/calculator/app.py)이며, Tkinter calculator UI는 [apps/calculator/ui/](../../apps/calculator/ui/) 패키지가 완전히 소유하고 있습니다.

* **루트 entrypoint 확인**:
  * [app_calculator.py](../../app_calculator.py)는 `apps.calculator.app:main`의 thin wrapper이며, 더 이상 `ui.calc_window`를 임포트하지 않습니다.
  * [app_calculator_tk.py](../../app_calculator_tk.py) 또한 `apps.calculator.app:main`으로 위임하는 deprecated wrapper입니다.
* **PyQt Train/Predict entrypoint 확인**:
  * [app_train.py](../../app_train.py)와 [app_predict.py](../../app_predict.py)는 각각 PyQt5 기반의 [ui/train_window.py](../../ui/train_window.py) 및 [ui/predict_window.py](../../ui/predict_window.py)를 계속 사용하고 있습니다.
* **레거시 PyQt 계산기 전용 소스**:
  * [ui/calc_window.py](../../ui/calc_window.py), [ui/calculators_2point.py](../../ui/calculators_2point.py), [ui/calculator_errors.py](../../ui/calculator_errors.py)는 현재 런타임 진입 경로가 완전히 분리되어 있는 calculator-only 레거시입니다.

## EN/AHRI/KS Reference Value Inventory

향후 Tkinter 기반 계산기로 확장 이식할 때 보존해야 할 레거시 UI/입력/계산 연결 사양입니다:

### 1. EN 14825 사양
* **Profile Selector**: QComboBox `combo_region_en`은 `list_calculator_profiles()` 중 `standard == "EN_14825"`인 것만 필터 노출하며, SCOP 프로파일이 최상단에 옵니다.
* **SEER/SCOP Visibility**: 선택된 프로파일의 `metric` 정보에 따라 `en_seer_group` 또는 `en_scop_group` 중 하나만 화면에 보이도록 제어합니다.
* **SEER Table Shape**: Columns = `("A", "B", "C", "D")`, Rows = `("능력 [W]", "전력 [W]")`.
* **SCOP Climate Card / Table Shape**:
  * `EN14825_SCOP_CLIMATE_DEFAULTS`에 따라 `Average` (Tbiv=-10.0, TOL=-11.0), `Warmer` (Tbiv=2.0, TOL=-11.0), `Colder` (Tbiv=-15.0, TOL=-22.0) 세 기후 카드가 체크박스형 그룹박스로 제공됩니다.
  * 기후 카드별 Table Columns = `("A", "B", "C", "D", "TOL", "Tbiv")`, Rows = `("능력 [W]", "전력 [W]")`.
* **W → kW 변환 정책**:
  * UI 테이블 입력과 Standby/대기전력 입력은 모두 Watts (W) 단위를 씁니다.
  * 계산 코어(`calculate_seer` / `calculate_scop`) 호출 직전에 `value / 1000.0` 처리를 수행하여 kW 값으로 변환 전달합니다.
* **Auxiliary Inputs**:
  * Standby power (W, 공통): `p_to`, `p_sb`, `p_ck`, `p_off` (기본값 "0.0").
  * SEER p_design_c (W): `p_design_c_w`.
  * SCOP auxiliary (기후별): `p_design_h` (W), `Tbiv` (°C), `TOL` (°C).
* **Result Formatting**:
  * SEER: `EN14825 SEER 결과: {seer}`
  * SCOP: `EN14825 SCOP 결과 — Average SCOP: {scop} / Warmer SCOP: {scop} / ...`

### 2. AHRI 210/240 사양
* **System Type Selector**: `HP (냉난방 겸용)` 및 `AC (냉방 전용)` 라디오 버튼 그룹.
* **SEER2 Table Shape**: Columns = `("A_Full", "B_Full", "B_Low", "E_Int", "F_Low")`, Rows = `("능력 [Btu/h]", "전력 [W]")`.
* **SEER2 Extra Params**: `Cd_low` (기본 0.25), `Cd_full` (선택형).
* **HSPF2 Table Shape**: Columns = `("H01", "H11", "H12", "H1N", "H22", "H2Int", "H32")`, Rows = `("능력 [Btu/h]", "전력 [W]")`.
* **HSPF2 A2 Sourcing**: 난방 HSPF2 계산 시 필요한 `A2` 조건의 능력/전력 값은 SEER2 테이블의 `A_Full` 열 데이터를 가져와 병합합니다.
* **HSPF2 Auxiliary Inputs**: `t_off` (°F), `t_on` (°F), `defrost_t_test_minutes`, `defrost_t_max_minutes` (별도 입력).
* **Result Formatting**:
  * AC: `AHRI SEER2 (AC) 결과: {seer2}`
  * HP: `AHRI SEER2 (HP) 결과: {seer2} / HSPF2 v3 결과: {rounded_hspf2}`

### 3. KS C 9306 사양
* 레거시 PyQt 계산기 UI([ui/calc_window.py](../../ui/calc_window.py))에는 KS 관련 탭이나 UI 요소가 설계되지 않았습니다 (inventory 결과: 없음).

## Test Ownership / Blocker Inventory

* **Calculator-only retirement candidate**:
  * (기존 155번에서 `test_app_calculator_ui_smoke.py`와 `test_calculator_errors.py`는 이미 삭제/정리 완료됨)
* **Mixed test blocker (분리 필수)**:
  * [tests/test_iso16358_table_excel_like_behavior.py](../../tests/test_iso16358_table_excel_like_behavior.py): `ui/calculators_2point.py`의 `ProfileInputGridModel`/`ProfileInputGridView`를 직접 임포트하여 Excel-like 상호작용을 테스트하고 있습니다. 소스 삭제 전에 반드시 이 테스트를 분리(split)하거나 PyQt 의존성을 retire해야 합니다.
* **Retained shared utility tests (유지 대상)**:
  * [tests/test_spreadsheet_table_model.py](../../tests/test_spreadsheet_table_model.py), [tests/test_spreadsheet_table_view.py](../../tests/test_spreadsheet_table_view.py): `ui/spreadsheet_table.py`를 커버하며, PyQt의 재사용 가능한 스프레드시트 뷰 기능을 보호합니다.
  * [tests/test_ui_theme_tokens.py](../../tests/test_ui_theme_tokens.py): `ui/theme.py` 토큰 검증용입니다.
* **Retained PyQt environment guard tests (유지 대상)**:
  * [tests/test_pyqt_environment_guard.py](../../tests/test_pyqt_environment_guard.py) 및 [tests/helpers/pyqt_env.py](../../tests/helpers/pyqt_env.py).

## Shared Utility Hold Status

* [ui/spreadsheet_table.py](../../ui/spreadsheet_table.py) 및 [ui/theme.py](../../ui/theme.py)는 Predict/Train 화면이나 미래의 PyQt5/PySide6 인터페이스에서 재사용될 수 있는 spreadsheet 및 디자인 토큰 컴포넌트입니다.
* 156번 리포트의 Hold 결정 정책에 따라, 본 파일들은 은퇴 대상에서 제외하고 **quarantine/hold** 상태로 계속 유지합니다.

## Retirement Readiness Judgment

* **판단**: **Not ready; specific blockers must be resolved first** (특정 blocker 해결 후 소스 은퇴 가능).
* **근거**:
  * 런타임 경로상으로는 PyQt 계산기 전용 소스들이 안전하게 분리되어 있습니다.
  * 하지만 `tests/test_iso16358_table_excel_like_behavior.py`가 여전히 `ui.calculators_2point`를 참조하고 있으므로, 이 blocker 테스트를 분리/제거하기 전까지는 소스 삭제가 불가능합니다.
  * 또한 본 리포트에 정리된 EN/AHRI 입력/단위 변환 레퍼런스 값들은 향후 `apps/calculator` 확장 완료 전까지 보존되어야 합니다.

## Recommended Next Slices

1. **Mixed ISO table test split or retirement (추천)**:
   * 목적: `tests/test_iso16358_table_excel_like_behavior.py`에서 레거시 PyQt 계산기 의존 영역을 분리하거나 은퇴시켜 blocker 해제.
   * 수정 대상: `tests/test_iso16358_table_excel_like_behavior.py`
   * 금지 대상: 프로덕션 소스 삭제, shared utility 삭제.
   * 검증 명령: `pytest tests/test_iso16358_table_excel_like_behavior.py`
2. **PyQt calculator-only source retirement**:
   * 목적: 계산기 전용 레거시 PyQt 소스 삭제.
   * 수정 대상: `ui/calc_window.py`, `ui/calculators_2point.py`, `ui/calculator_errors.py` 삭제, `app_calculator.py` cleanup.
   * 금지 대상: `ui/spreadsheet_table.py`, `ui/theme.py` 삭제 금지.
3. **PyQt support matrix guide update**:
   * 목적: 테스트 은퇴 후 환경 정책 가이드 갱신.

## 제외 범위 (Non-goals)

* 프로덕션 소스 코드 및 테스트 코드를 절대 수정/삭제하지 않았습니다.
* `docs/code_map/CODEBASE_REFERENCE_MAP.md`, 아키텍처 가이드라인 등은 수정하지 않았습니다.

## 검증 결과 (Verification Results)

* `python3 -B tools/check_code_structure.py`: `code structure guard: OK (no findings)`.
* `git diff --check`: whitespace 오류 없음.
* `git status --short`: clean.
* active report count: active report count is below lifecycle threshold.

## WORK_PLAN 업데이트 여부

* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md)에 preflight 완료 상태를 업데이트하고 차기 recommended next slice를 등록하였습니다.

## Next Action

* **Slice 1: Mixed ISO table test split or retirement** 실행을 추천합니다.

## Commit / Push

* 본 preflight 보고서 및 WORK_PLAN 수정을 스테이징 후 함께 푸시합니다.
* 커밋 메시지: `reports: Audit PyQt calculator retirement readiness`

## Project Memory Delta

- none
