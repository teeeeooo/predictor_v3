# audit_3 Next Actions Completion

## Objective

`AGENTS.md`와 `reference_files/audit_3.md`를 기준으로 “지금 당장 할 수 있는 다음 작업” 5가지를 완료했다.

사용자 조건:
- 단계별 source commit과 result report commit을 분리한다.
- result report를 한 번에 몰아서 만들지 않는다.
- 최종 완료 리포트는 `reference_files/` 아래 Markdown으로 남긴다.

## Completion Checklist

| Requirement | Evidence |
| --- | --- |
| 1. PyQt UI smoke optional dependency guard | `tests/test_app_calculator_ui_smoke.py`에 `pytest.importorskip("PyQt5")` 추가. PyQt가 있으면 기존 offscreen smoke 실행. Report: `result_reports/active/063_pyqt-ui-smoke-optional-guard.md`. |
| 2. `ui/calc_window.py` 계산 버튼 / 결과 표시 최소 연결 | `button_calculate.clicked.connect(self.on_calculate)`와 `result_label.setText(...)` 경로 추가. AHRI AC 입력 smoke가 버튼 클릭 후 `"AHRI SEER2 (AC) 결과:"` 표시를 확인. Report: `result_reports/active/064_connect-calculator-ui-result-action.md`. |
| 3. Calculator adapter helper 첫 slice 구현 | `core/calculator_result_adapter.py`의 `wrap_calculator_result_envelope()` 추가. `ahri_usa_seer2` raw result를 `CalculatorResultEnvelope` 형태로 감싸고 `raw_result`를 보존. Report: `result_reports/active/065_calculator-result-envelope-adapter-slice.md`. |
| 4. Adapter / calculator schema-coupling guard test 추가 | `tests/test_calculator_schema_boundaries.py` 추가. Calculator import boundary, region config runtime key, adapter-owned envelope term guard를 자동화. Report: `result_reports/active/066_guard-calculator-schema-boundaries.md`. |
| 5. EN14825 profile/dispatcher/UI resolver 전환 첫 구현 | `en14825_scop` profile 등록, dispatcher `calculator_id="en14825"` 지원, EN combo profile-id item data 전환. Report: `result_reports/active/067_route-en14825-ui-through-profiles.md`. |
| Managed docs update | `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, `docs/architecture/project_architecture.md`, `project_brief.md`, `project_log.md` 업데이트. |
| Step-by-step reports | `063`~`067` reports were created and committed after each source change, not batched at the end. |
| Final completion report in `reference_files/` | This file: `reference_files/audit_3_next_actions_completion.md`. |

## Verification Evidence

- PyQt availability:
  - `PyQt5: available`
- UI smoke guard and result action:
  - `rg -n "pytest.importorskip\\(\"PyQt5\"\\)|QPushButton|clicked.connect\\(self.on_calculate\\)|result_label|button_calculate" tests/test_app_calculator_ui_smoke.py ui/calc_window.py`
- Adapter envelope:
  - `rg -n "wrap_calculator_result_envelope|raw_result|calculator_profile_id|ahri_usa_seer2" core/calculator_result_adapter.py tests/test_calculator_result_adapter.py`
- Schema boundary guard:
  - `rg -n "BANNED_IMPORT|BANNED_REGION_RUNTIME_KEYS|ADAPTER_ONLY_TERMS|test_calculator_modules|test_region_configs|test_envelope_runtime_terms" tests/test_calculator_schema_boundaries.py`
- EN profile routing:
  - `rg -n "en14825_scop|EN_14825|calculator_id == \\\"en14825\\\"|_populate_en_profiles|combo_region_en|EN14825 SCOP" core/calculator_profiles.py core/calculator_dispatcher.py ui/calc_window.py tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py tests/test_app_calculator_ui_smoke.py docs/WORK_PLAN.md docs/REFACTOR_PLAN.md docs/architecture/project_architecture.md project_brief.md`

## Test Results

- `python3 -B -m py_compile app_calculator.py ui/calc_window.py core/calculator_profiles.py core/calculator_dispatcher.py core/calculator_result_adapter.py tests/test_app_calculator_ui_smoke.py tests/test_calculator_result_adapter.py tests/test_calculator_schema_boundaries.py`
  - passed
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest tests/test_app_calculator_ui_smoke.py tests/test_calculator_result_adapter.py tests/test_calculator_schema_boundaries.py tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py tests/test_en14825_golden.py tests/test_ahri_seer2_smoke.py -q`
  - `49 passed`
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest -q`
  - `301 passed, 23 xfailed`

## Commits

- `9dbf6cf` `test: skip calculator UI smoke without PyQt`
- `21b7b93` `report: record PyQt UI smoke optional guard`
- `7dbe1d9` `feat: connect calculator UI result action`
- `712b60d` `report: record calculator UI result action`
- `628783f` `feat: add calculator result envelope adapter`
- `2b02935` `report: record calculator result adapter slice`
- `8212045` `test: guard calculator schema boundaries`
- `532b632` `report: record calculator schema boundary guards`
- `bc184e7` `feat: route EN14825 UI through calculator profiles`
- `3b07b22` `report: record EN14825 UI profile routing`

## Managed Document Updates

- Updated:
  - `docs/WORK_PLAN.md`
  - `docs/REFACTOR_PLAN.md`
  - `docs/architecture/project_architecture.md`
  - `project_brief.md`
  - `project_log.md`
- Not updated:
  - `AGENTS.md`
  - `AGENT_TASK_ROUTER.md`
  - `ACTIVE_DOCUMENTS.md`

Reason: this work applied existing routing/report rules and did not add a new active owner document or agent workflow route.

## Remaining Risks

- EN tab now constructs `EN14825Calculator` through the resolver/dispatcher path, but `calculate_en()` still returns a placeholder string. Real EN UI calculation output remains a separate task.
- Calculator adapter support is intentionally narrow: only AHRI SEER2 result wrapping is implemented. `CalculatorInputEnvelope`, ranking, and ML / inverse-search caller integration remain future work.
- PyQt-missing behavior was implemented via `pytest.importorskip("PyQt5")`; the current local environment has PyQt5 installed, so skip behavior was not verified by uninstalling PyQt.
