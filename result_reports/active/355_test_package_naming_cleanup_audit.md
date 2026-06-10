# Active Report 355: Test/Package Naming Cleanup Audit

## 목표 (Goal)

* `ui_tk/`가 `apps/calculator/ui/`로 relocation 완료되었고 PyQt calculator-only source retirement/active docs update도 완료되었다.
* 이번 audit의 목적은 실제 rename 실행 전에 어떤 test 파일명이 stale한지, 어떤 것은 유지해야 하는지, rename 전략을 어떻게 가져갈지 분류하고 판단하는 것이다.
* source/test rename, import 수정, code map regeneration은 이번 작업에서 수행하지 않는다.

## 기준 Reports/Docs

* [Report 346 Summary](../summaries/346_summary-batch-foundation-apps-calculator-relocation-closeout.md): ui_tk/ → apps/calculator/ui/ 53파일 relocation 완료, import 전역 교정 완료
* [Report 353](353_pyqt_calculator_only_source_retirement.md): PyQt calculator-only source retirement 완료
* [Report 354](354_pyqt_calculator_docs_support_matrix_update.md): active docs/support matrix update 완료
* [docs/guides/pyqt_test_support_matrix.md](../../docs/guides/pyqt_test_support_matrix.md): retained PyQt test scope 확인

## ui_tk Naming Inventory (Task 2 결과)

### 분류 결과 요약

| 위치 | 종류 | 분류 |
|------|------|------|
| `tests/test_ui_tk_*.py` (36개) | 파일명 | **current-state stale filename** — 내부 import는 이미 `apps.calculator.ui.*`로 교정 완료 |
| `tests/` 파일 내부 `ui_tk` 문자열 | import/string | **없음** — 모두 `apps.calculator.ui.*`로 교정됨 |
| `apps/` 내부 `ui_tk` 문자열 | import/string | **없음** |
| `docs/WORK_PLAN.md` | historical wording | historical record (274, 313 entries), Active Constraints 잔존 2줄 |
| `docs/architecture/project_architecture.md` | historical note | `(이전 ui_tk/가 이 위치로 완전히 이주됨)` 설명 |
| `result_reports/active/*.md` | historical record | report 번호 기록에서 `test_ui_tk_*` 파일명 참조 |
| `docs/designs/*.md` | historical design docs | design 작성 시점 경로 참조, 수정 불필요 |
| `docs/archive/project_log/*.md` | historical archive | 수정 불필요 |
| `tools/check_code_structure.py` | stale guard logic | `ui_tk/`를 PRODUCTION_ROOT로 hardcode — **별도 cleanup 슬라이스 필요** |

### 핵심 발견

1. **파일명만 stale**: 36개 `test_ui_tk_*.py` 파일의 내부 import/string은 이미 `apps.calculator.ui.*`로 완전 교정되어 있다.
2. **`tools/check_code_structure.py`**: `ui_tk/`를 `PRODUCTION_ROOTS`, `UI_VISUAL_SCAN_ROOTS`, banned import check 대상으로 hardcoded. 해당 디렉토리가 없으므로 scan 결과에 영향은 없으나, guard 로직 자체가 stale하다.
3. **docs/WORK_PLAN.md Active Constraints**: `ui_tk/table_clipboard.py`, `ui_tk cleanup direction` 언급이 현재 Active Constraints 섹션에 남아 있다.

## Test File Rename Candidates (Task 3)

총 36개 `test_ui_tk_*.py`. 그룹별 분류:

### Group A: Batch / Table / Model (8개)

| 현재 파일명 | 권장 파일명 | rename 필요 | 위험도 |
|---|---|---|---|
| `test_ui_tk_batch_dialog_shell.py` | `test_apps_calculator_ui_batch_dialog_shell.py` | 권장 | 낮음 |
| `test_ui_tk_batch_matrix_models.py` | `test_apps_calculator_ui_batch_matrix_models.py` | 권장 | 낮음 |
| `test_ui_tk_batch_matrix_table.py` | `test_apps_calculator_ui_batch_matrix_table.py` | 권장 | 낮음 |
| `test_ui_tk_batch_models.py` | `test_apps_calculator_ui_batch_models.py` | 권장 | 낮음 |
| `test_ui_tk_batch_table_controller.py` | `test_apps_calculator_ui_batch_table_controller.py` | 권장 | 낮음 |
| `test_ui_tk_batch_table_viewport.py` | `test_apps_calculator_ui_batch_table_viewport.py` | 권장 | 낮음 |
| `test_ui_tk_table_controller.py` | `test_apps_calculator_ui_table_controller.py` | 권장 | 낮음 |
| `test_ui_tk_table_controller_per_cell_roles.py` | `test_apps_calculator_ui_table_controller_per_cell_roles.py` | 권장 | 낮음 |

### Group B: Table Core / Grid (4개)

| 현재 파일명 | 권장 파일명 | rename 필요 | 위험도 |
|---|---|---|---|
| `test_ui_tk_table_grid.py` | `test_apps_calculator_ui_table_grid.py` | 권장 | 낮음 |
| `test_ui_tk_table_grid_model.py` | `test_apps_calculator_ui_table_grid_model.py` | 권장 | 낮음 |
| `test_ui_tk_table_interaction_core.py` | `test_apps_calculator_ui_table_interaction_core.py` | 권장 | 낮음 |
| `test_ui_tk_excel_like_table_controller.py` | `test_apps_calculator_ui_excel_like_table_controller.py` | 권장 | 낮음 |

### Group C: MetricInputTable / Adapter (3개)

| 현재 파일명 | 권장 파일명 | rename 필요 | 위험도 |
|---|---|---|---|
| `test_ui_tk_metric_input_table_adapter.py` | `test_apps_calculator_ui_metric_input_table_adapter.py` | 권장 | 낮음 |
| `test_ui_tk_metric_input_table_controller_parity.py` | `test_apps_calculator_ui_metric_input_table_controller_parity.py` | 권장 | 낮음 |
| `test_ui_tk_metric_input_table_validation.py` | `test_apps_calculator_ui_metric_input_table_validation.py` | 권장 | 낮음 |

### Group D: Section / Profile / Controller Switch (7개)

| 현재 파일명 | 권장 파일명 | rename 필요 | 위험도 |
|---|---|---|---|
| `test_ui_tk_hong_kong_cspf_controller_switch.py` | `test_apps_calculator_ui_hong_kong_cspf_controller_switch.py` | 권장 | 낮음 |
| `test_ui_tk_hong_kong_hspf_controller_switch.py` | `test_apps_calculator_ui_hong_kong_hspf_controller_switch.py` | 권장 | 낮음 |
| `test_ui_tk_iso_iseer_2point_controller_switch.py` | `test_apps_calculator_ui_iso_iseer_2point_controller_switch.py` | 권장 | 낮음 |
| `test_ui_tk_iso_saso_t3_controller_switch.py` | `test_apps_calculator_ui_iso_saso_t3_controller_switch.py` | 권장 | 낮음 |
| `test_ui_tk_controller_type_replace_flicker_diagnostic.py` | `test_apps_calculator_ui_controller_type_replace_flicker_diagnostic.py` | 권장 | 낮음 |
| `test_ui_tk_profile_resolver.py` | `test_apps_calculator_ui_profile_resolver.py` | 권장 | 낮음 |
| `test_ui_tk_section_result_formatting.py` | `test_apps_calculator_ui_section_result_formatting.py` | 권장 | 낮음 |

### Group E: Batch Dialog / Batch Spec (3개)

| 현재 파일명 | 권장 파일명 | rename 필요 | 위험도 |
|---|---|---|---|
| `test_ui_tk_iso_iseer_2point_batch_dialog.py` | `test_apps_calculator_ui_iso_iseer_2point_batch_dialog.py` | 권장 | 낮음 |
| `test_ui_tk_saso_t3_batch_dialog.py` | `test_apps_calculator_ui_saso_t3_batch_dialog.py` | 권장 | 낮음 |
| `test_ui_tk_hong_kong_cspf_batch_spec.py` | `test_apps_calculator_ui_hong_kong_cspf_batch_spec.py` | 권장 | 낮음 |

### Group F: Hong Kong / ISO Helpers / Autocalc / Result (5개)

| 현재 파일명 | 권장 파일명 | rename 필요 | 위험도 |
|---|---|---|---|
| `test_ui_tk_hong_kong_cspf_matrix_migration.py` | `test_apps_calculator_ui_hong_kong_cspf_matrix_migration.py` | 권장 | 낮음 |
| `test_ui_tk_hong_kong_hspf_detail.py` | `test_apps_calculator_ui_hong_kong_hspf_detail.py` | 권장 | 낮음 |
| `test_ui_tk_iso16358_helpers.py` | `test_apps_calculator_ui_iso16358_helpers.py` | 권장 | 낮음 |
| `test_ui_tk_iso_table_autocalc.py` | `test_apps_calculator_ui_iso_table_autocalc.py` | 권장 | 낮음 |
| `test_ui_tk_result_panel_stable_update.py` | `test_apps_calculator_ui_result_panel_stable_update.py` | 권장 | 낮음 |

### Group G: Window / Lifecycle (5개)

| 현재 파일명 | 권장 파일명 | rename 필요 | 위험도 |
|---|---|---|---|
| `test_ui_tk_window_lifecycle_repair.py` | `test_apps_calculator_ui_window_lifecycle_repair.py` | 권장 | 낮음 |
| `test_ui_tk_window_measurement.py` | `test_apps_calculator_ui_window_measurement.py` | 권장 | 낮음 |
| `test_ui_tk_window_measurement_side_effect_free.py` | `test_apps_calculator_ui_window_measurement_side_effect_free.py` | 권장 | 낮음 |
| `test_ui_tk_window_refit.py` | `test_apps_calculator_ui_window_refit.py` | 권장 | 낮음 |
| `test_ui_tk_window_shell.py` | `test_apps_calculator_ui_window_shell.py` | 권장 | 낮음 |

### Group H: Bin Detail Schema (1개)

| 현재 파일명 | 권장 파일명 | rename 필요 | 위험도 |
|---|---|---|---|
| `test_ui_tk_bin_detail_schema.py` | `test_apps_calculator_ui_bin_detail_schema.py` | 권장 | 낮음 |

### Special case: 수정 금지 / rename 대상 아님

| 파일명 | 이유 |
|---|---|
| `test_ui_tk_calculator_foundation.py` | pre-existing SyntaxError (`.` 포함 함수명); rename 전 SyntaxError 해소 먼저 필요. **별도 조치 필요** |

> [!IMPORTANT]
> `test_ui_tk_calculator_foundation.py`는 SyntaxError(function name에 `.` 포함)가 pre-existing 상태이며 pytest collection 단계에서 실패한다. rename 실행 슬라이스에서는 이 파일의 SyntaxError를 먼저 해소하거나, 해소 전 rename만 진행하고 별도 fix 슬라이스를 예약해야 한다.

### Rename 시 Update 필요 References

* `docs/WORK_PLAN.md`: 일부 `test_ui_tk_*` 파일명 언급 → 해당 history entry는 historical이므로 수정 불필요
* `result_reports/active/353_*.md`: `test_ui_tk_*` 파일명 — historical record이므로 수정 불필요
* `tools/check_code_structure.py`: `ui_tk/` hardcoded PRODUCTION_ROOT → **rename 슬라이스에서 함께 정리 필요**
  * `BANNED_IMPORTS["ui_tk"]`, `PRODUCTION_ROOTS`, `UI_VISUAL_SCAN_ROOTS`, `check_ui_tk_shell_anti_pattern` 함수
* `tests/test_code_structure_guard.py`: SyntaxError로 인해 현재 collection 불가. 내용 확인 시 `ui_tk` 관련 fixture가 있을 가능성 → rename 슬라이스에서 확인 필요

## Non-Test Reference Audit (Task 4)

| 파일 | ui_tk 표현 | 분류 |
|------|-----------|------|
| `docs/WORK_PLAN.md` L71, L102 | `ui_tk cleanup preflight`, `ui_tk controller switch arc` | historical record — 수정 불필요 |
| `docs/WORK_PLAN.md` L131 | `ui_tk/table_clipboard.py` | **Active Constraints 내 stale path** — docs cleanup 후보 |
| `docs/WORK_PLAN.md` L148 | `ui_tk cleanup direction` | **Active Constraints 내 stale wording** — docs cleanup 후보 |
| `docs/WORK_PLAN.md` L151 | `ui_tk cleanup / controller switch slices` | **Active Constraints 내 stale wording** — docs cleanup 후보 |
| `docs/architecture/project_architecture.md` L21 | `이전 ui_tk/가 이 위치로 완전히 이주됨` | historical 주석 — 수정 불필요 |
| `result_reports/active/347, 353, 354` | `ui_tk` 경로 참조 | historical record — 수정 불필요 |
| `docs/designs/*.md` | `ui_tk/` 경로 | historical design docs — 수정 불필요 |
| `docs/archive/project_log/*.md` | `ui_tk/` 경로 | archive — 수정 불필요 |
| `tools/check_code_structure.py` | `ui_tk` hardcoded | **stale guard 로직** — rename 슬라이스 또는 별도 guard cleanup 슬라이스에서 처리 필요 |

**Active Constraints 섹션 stale wording 3줄 (WORK_PLAN L131, L148, L151)**: 현재 동작에 영향을 주지 않으나, apps/calculator/ui/ 기준 path로 업데이트가 권장된다. 이번 작업 scope는 audit 전용이므로 수정하지 않으며, rename 실행 슬라이스에서 함께 정리한다.

## Candidate Strategies 비교 (Task 5)

### Candidate A: Rename all 36 files in one slice

* 장점: naming cleanup 완전 완료, tests/에 ui_tk 명칭 완전 제거
* 위험: 36개 파일 동시 rename → references 누락 위험, 대규모 diff
* 추가 필요: `tools/check_code_structure.py` guard 로직 업데이트, `test_ui_tk_calculator_foundation.py` SyntaxError 처리
* 예상 작업 규모: **중간 — 하루 내 완료 가능**

### Candidate B: Rename by group in multiple slices

* Slice 1: batch/table/model (Group A + B + C, 15개)
* Slice 2: section/profile/dialog (Group D + E + F, 15개)
* Slice 3: window/lifecycle (Group G + H, 6개)
* 장점: 회귀 추적 용이, slice별 full pytest 확인
* 위험: cleanup 기간 길어짐, 도중에 ui_tk/apps 혼용 상태가 유지됨
* 예상 작업 규모: **3 슬라이스 × 소규모**

### Candidate C: Do not rename now — 바로 EN/AHRI/KS 확장으로 이동

* 장점: profile expansion을 최단 경로로 시작 가능
* 위험: EN/AHRI/KS 신규 test 작성 시 `test_apps_calculator_ui_*` 패턴 vs `test_ui_tk_*` 혼용 상태가 더 고착됨
* 그러나 **import 경로는 이미 교정 완료**이므로 기능적 regression 위험은 없음

### 권장 전략: **Candidate C (지금은 EN/AHRI/KS 확장 우선), 이후 Candidate A**

**판단 근거**:

1. 내부 import 경로는 이미 `apps.calculator.ui.*`로 완전 교정됨 — 기능적 문제 없음
2. test 파일명 stale은 naming 불일치이며 blocking 이슈가 아님
3. EN/AHRI/KS 신규 test는 처음부터 `test_apps_calculator_ui_*` 패턴으로 작성 가능 — 혼용 확대 방지
4. rename 36개를 한 번에 하는 것보다 EN/AHRI/KS expansion 후 cleanup이 더 효율적

**단, `tools/check_code_structure.py` guard 로직의 `ui_tk` stale reference는 EN/AHRI/KS expansion 이전에 정리하는 것이 권장된다.** guard가 존재하지 않는 `ui_tk/` 디렉토리를 scan하여 false-clean 결과를 내고 있기 때문이다.

## WORK_PLAN 업데이트 결과 (Task 6)

* Recent history에 355 audit 완료 추가
* Next Actions: EN14825 / AHRI 210/240 / KS profile expansion을 Recommended next slice로 승격
* Test/package naming cleanup execution은 2번으로 "can be deferred"로 명시

## 제외 범위 (Non-Goals)

* test file rename 없음
* import path 수정 없음
* source 수정 없음
* apps/ 수정 없음
* docs/architecture 수정 없음
* README.md, project_brief.md, pyqt_test_support_matrix.md 수정 없음
* code map regeneration 없음
* memory seed 수정 없음
* project_log 수정 없음

## 검증 결과 (Verification)

* `git status --short`: WORK_PLAN 및 355 report 외 diff 없음
* grep "ui_tk|test_ui_tk" in tests/*.py 내부: **결과 없음** (import 경로 교정 완료 확인)
* grep "apps.calculator.ui" in tests/*.py: 정상 import 다수 확인 (lifecycle_repair, controller_switch 등)
* `python3 -B tools/check_code_structure.py`: **OK (no findings)**
* `git diff --check`: whitespace 에러 없음
* source/test/apps/ui 파일 변경 없음

## next action

* **EN14825 / AHRI 210/240 / KS profile expansion** — current next recommended slice
* **추가 권장 (EN/AHRI/KS 이전 소규모)**: `tools/check_code_structure.py`에서 stale `ui_tk/` guard 로직 제거 — `PRODUCTION_ROOTS`, `BANNED_IMPORTS["ui_tk"]`, `UI_VISUAL_SCAN_ROOTS`, `check_ui_tk_shell_anti_pattern` hardcode를 현재 `apps/calculator/ui/` 구조에 맞게 갱신
* **deferred**: 36개 `test_ui_tk_*.py` → `test_apps_calculator_ui_*.py` rename (기능적 blocking 없음, EN/AHRI/KS 이후 한 슬라이스로 실행 가능)
