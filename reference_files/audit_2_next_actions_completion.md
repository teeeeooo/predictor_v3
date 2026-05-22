# audit_2 Next Actions Completion

## Objective

`AGENTS.md`와 `reference_files/audit_2.md`를 기준으로 “지금 당장 할 수 있는 다음 작업” 5가지를 완료했다.

사용자 추가 조건:
- 단계별 source commit과 result report commit을 분리한다.
- result report를 한 번에 몰아서 만들지 않는다.
- 최종 완료 리포트는 `reference_files/` 아래 Markdown으로 남긴다.
- PyQt가 없으면 설치해서 테스트하되, 현재 환경에서는 `PyQt5: available`이라 설치가 필요 없었다.
- 필요한 관리 문서는 함께 업데이트한다.

## Completion Checklist

| Requirement | Evidence |
| --- | --- |
| 1. Root audit/result 문서 lifecycle 정리 | `ACTIVE_DOCUMENTS.md`에서 `reference_files/*.md`를 active inventory scope에서 제외하고, root result docs가 `reference_files/` reference snapshot임을 기록. Report: `result_reports/active/057_root-audit-result-lifecycle.md`. |
| 2. Active HSPF validation의 `tests._legacy` helper 의존 제거 | `tests/helpers/iso16358_hspf_samples.py` 추가, `tests/test_iso16358_hspf_validation.py`가 새 helper를 import. `rg -n "tests\\._legacy" tests/test_iso16358_hspf_validation.py tests -g '!tests/_legacy/**'` 결과 없음. Report: `result_reports/active/058_split-active-hspf-validation-helper.md`. |
| 3. `app_calculator.py` / `ui/calc_window.py` interaction smoke audit | `tests/test_app_calculator_ui_smoke.py` 추가. PyQt offscreen launch smoke 통과. `ui/calc_window.py` 내부 calculate button/result display 연결은 발견되지 않아 follow-up risk로 기록. Report: `result_reports/active/059_app-calculator-ui-smoke-audit.md`. |
| 4. AHRI UI profile selector 정리 | `ui/calc_window.py` AHRI combo를 `list_calculator_profiles()` 기반으로 채우고 item data에 `profile_id` 저장. `on_region_changed_ahri()`는 선택된 profile id로 dispatcher 호출. Report: `result_reports/active/060_ahri-ui-profile-selector.md`. |
| 5. Calculator result envelope / ML adapter boundary 설계 | `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md` 작성. Architecture, work plan, refactor plan, project brief, active inventory, project log, docs map 업데이트. Report: `result_reports/active/061_calculator-result-envelope-ml-adapter-design.md`. |
| Step-by-step reports | `057`~`061` reports were created and committed after each source change, not batched at the end. |
| Final completion report in `reference_files/` | This file: `reference_files/audit_2_next_actions_completion.md`. |

## Verification Evidence

- PyQt availability:
  - `PyQt5: available`
- Root lifecycle evidence:
  - `rg -n "Excluded:.*reference_files|Root result docs have been moved|Reference Snapshots" ACTIVE_DOCUMENTS.md`
- Active legacy dependency evidence:
  - `rg -n "tests\\._legacy" tests/test_iso16358_hspf_validation.py tests -g '!tests/_legacy/**'`
  - no matches
- AHRI selector evidence:
  - `rg -n "list_calculator_profiles|itemData\\(index\\)|currentData\\(\\)|ahri_usa_seer2|규격 프로파일" ui/calc_window.py tests/test_app_calculator_ui_smoke.py`
- Design doc evidence:
  - `rg -n "calculator-result-envelope-ml-adapter|PredictedPointsEnvelope|CalculatorResultEnvelope|RankingCandidateEnvelope" docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md docs/architecture/project_architecture.md docs/WORK_PLAN.md docs/REFACTOR_PLAN.md ACTIVE_DOCUMENTS.md project_brief.md project_log.md`

## Test Results

- `python3 -B -m py_compile app_calculator.py ui/calc_window.py core/calculator_profiles.py core/calculator_dispatcher.py`
  - passed
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py tests/_legacy/test_iso16358_hspf_golden_diagnostic.py tests/_legacy/test_iso16358_hspf_h8_trace.py -q`
  - `60 passed, 17 xfailed`
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest tests/test_app_calculator_ui_smoke.py tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q`
  - `32 passed`
- `QT_QPA_PLATFORM=offscreen python3 -B -m pytest -q`
  - `290 passed, 23 xfailed`

## Commits

- `e806407` `docs: clarify reference file lifecycle`
- `afb2fe1` `report: record root audit result lifecycle`
- `e0cafcc` `test: split active HSPF validation helper`
- `31efeea` `report: record active HSPF validation helper split`
- `f17f8da` `test: add calculator UI launch smoke`
- `1767cdd` `report: record app calculator UI smoke audit`
- `0f94441` `fix: drive AHRI UI selector from calculator profiles`
- `86bca20` `report: record AHRI UI profile selector cleanup`
- `cadc65c` `docs: define calculator result envelope boundary`
- `06e736e` `report: record calculator envelope adapter design`

## Managed Document Updates

- Updated:
  - `ACTIVE_DOCUMENTS.md`
  - `docs/README.md`
  - `docs/WORK_PLAN.md`
  - `docs/REFACTOR_PLAN.md`
  - `docs/architecture/project_architecture.md`
  - `project_brief.md`
  - `project_log.md`
- Not updated:
  - `AGENTS.md`
  - `AGENT_TASK_ROUTER.md`

Reason: this work applied existing workflow rules but did not add a new agent rule or routing rule.

## Remaining Risks

- `ui/calc_window.py` still does not show a discovered calculate button/result-label display path for `on_calculate()` return values. This is now a clearly identified UI follow-up, not part of the AHRI selector cleanup.
- Calculator result envelope / ML adapter is design-only. The next implementation should add a narrow adapter helper slice with tests and should keep core calculator public APIs unchanged.
- No web search was needed because local code/docs and installed PyQt were sufficient for the requested work.
