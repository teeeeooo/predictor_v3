# 033_summary-calculator-architecture-ks-profile-dispatch

## Covered Reports
- `021_audit-doc-workflow-links.md`
- `022_add-packaging-route.md`
- `023_calculator-architecture-reset.md`
- `024_refine-calculator-architecture-docs.md`
- `025_separate-ks-c9306-calculator.md`
- `026_separate-ks-c9306-cspf-helper.md`
- `027_prepare-ks-c9306-cspf-public-entry.md`
- `028_correct-region-config-architecture.md`
- `029_add-modified-line-to-agent-output.md`
- `030_register-ks-c9306-profiles.md`
- `031_update-calculator-profile-snapshot-tests.md`
- `032_add-calculator-profile-dispatcher.md`

## Workstream Summary
Reports 021~032는 하나의 큰 흐름을 다룬다. 먼저 021/022는 docs/router workflow를 정비해 (021) `AGENTS.md` ↔ `AGENT_TASK_ROUTER.md` ↔ project docs / standard docs / 참고 문서 사이의 inbound/outbound 링크와 archive 사용 현황을 audit하고, (022) Packaging 작업의 active owner 문서로 `docs/PACKAGING.md`를 연결했다. 이어 029는 같은 docs/router 흐름 위에 agent 출력 표준 3-line(`modified:` 줄 포함) 규칙을 더해 workflow를 표준화했다. 그 위에서 (1) calculator architecture를 ISO 16358 / KS C 9306 / AS/NZS workbook oracle 3-module boundary로 reset하고 문서를 정정한다(023/024/028). (2) 그 boundary대로 KS C 9306 코드를 `core/calculator_iso16358.py`에서 분리해 `core/calculator_ks_c9306.py` (`KSC9306Calculator`)로 옮기고 CSPF/HSPF public entry를 마련한다(025~027). (3) profile manifest에 KS C 9306 두 profile을 등록하고 snapshot test를 정렬한다(030/031). (4) profile resolver 결과를 calculator 인스턴스로 잇는 thin dispatch helper(`core/calculator_dispatcher.py`)를 추가해 Calculator UI 연결 전 단계의 foundation을 완성한다(032).

## Key Decisions
- Calculator 모듈은 세 축으로 고정: `core/calculator_iso16358.py` (ISO 16358 전용), `core/calculator_ks_c9306.py` (KS C 9306 special calculator), `core/calculator_asnzs_hspf_excel.py` (AS/NZS workbook oracle compatibility, Z-phase 후보).
- `data/region_configs/`는 ISO16358 전용 저장소가 아니라 여러 calculator가 공유하는 정적 standard/region config 저장소이다. 각 JSON을 한 calculator가 직접 해석한다 (ISO16358은 ISO 기반 regional profile, KS C 9306은 `korea.json`, AHRI는 `usa.json` / `usa_hspf2.json`).
- `data/region_configs/korea.json`은 유지하되 ISO common path가 아니라 `KSC9306Calculator`가 직접 해석해야 한다는 boundary를 architecture / REGION_CONFIG_RULES / project_log에 명시했다.
- KS C 9306 profile 두 개가 `calculator_id=ks_c9306`으로 manifest에 등록되었다 (`ks_c9306_cspf`, `ks_c9306_hspf`, `enabled=True`, `config_path=data/region_configs/korea.json`).
- profile resolver와 calculator dispatcher는 UI 연결 전 foundation layer로 분리한다. profile resolver(`core/calculator_profiles.py`)는 순수 manifest/selector를 유지하고, instance 생성은 `core/calculator_dispatcher.py`의 `create_calculator_for_profile(...)`이 담당한다.
- agent 작업의 터미널 결과 보고는 task별 OK/NG 한 줄 → `modified: <paths>` 한 줄 → `report: <path>` 한 줄 3-line 형식으로 표준화했다.
- Packaging 작업의 active owner 문서는 `docs/PACKAGING.md`로 고정하고 `AGENTS.md` / `AGENT_TASK_ROUTER.md` / root `README.md` / `docs/README.md` 문서 맵에서 inbound 링크를 보강한다 (보고 022).
- active docs workflow audit (보고 021)은 `AGENTS.md` ↔ `AGENT_TASK_ROUTER.md` ↔ project docs / standard docs / 참고 문서 사이의 link 상태를 path/reference 기준으로 점검하는 report-only 활동이며, source docs 수정은 후속 작업에서 별도로 처리한다.

## Architecture / Process Rules Fixed
- ISO common path가 KS C 9306 또는 AS/NZS Excel compatibility 로직을 흡수하지 않는다. KS region config 해석을 ISO common path에 합치지 않고, AS/NZS workbook oracle convention을 ISO common path에 섞지 않는다.
- profile resolver는 `region` 또는 `standard` metadata만으로 KS C 9306 또는 AS/NZS Excel compatibility를 자동 활성화하지 않는다. `calculator_id` 값으로 명시적 라우팅한다.
- `work/iso-hspf-refactor-ui-followup` 브랜치는 merge 대상이 아니라 reference/spike로만 둔다. diff cherry-pick 또는 merge는 수행하지 않는다.
- `data/region_configs/REGION_CONFIG_RULES.md`에 “여러 calculator가 공유하는 정적 standard/region config 저장소” 원칙과 KS / AHRI / AS/NZS 해석 boundary를 명시했다.
- 모든 agent 작업의 터미널 출력은 표준 3-line 형식(OK/NG → `modified:` → `report:`)을 따른다. `modified:`에는 실제 수정/생성/삭제 파일만 포함하며, blocked는 `modified: none`을 사용한다.
- Packaging 작업 요청 시 `docs/PACKAGING.md`가 active owner 문서이며, `AGENTS.md`와 `AGENT_TASK_ROUTER.md`의 Packaging route, root `README.md` / `docs/README.md` 문서 맵을 통해 inbound가 연결되어 있다.
- active docs workflow audit는 source docs 수정 없이 path/reference 기준으로 link 상태만 점검한다. `*_design_notes.md`, `docs/archive/**`, `result_reports/**`, `.pytest_cache/README.md`는 audit 대상에서 제외한다.

## Implementation Progress
- 보고 021: active docs workflow audit. `AGENTS.md` / `AGENT_TASK_ROUTER.md` / project docs / standard docs / 참고 문서의 inbound/outbound link 상태와 archive 사용 현황을 path/reference 기준으로 점검. source docs 수정은 후속 turn으로 분리. Report-only artifact.
- 보고 022: `AGENTS.md`와 `AGENT_TASK_ROUTER.md`에 Packaging route를 추가하고 root `README.md`, `docs/README.md` 문서 맵에 `docs/PACKAGING.md` inbound를 보강. `project_log.md`에 Packaging route owner 연결 결정 기록.
- 보고 025: `core/calculator_ks_c9306.py` 신규 생성. `KSC9306Calculator` 클래스가 KS C 9306 HSPF 본문(`_validate_ks_*`, `_ks_hspf_*`, `_calculate_ks_c9306_hspf`)을 보유하고, ISO16358 측은 thin delegating wrappers로 기존 호출 경로를 유지한다.
- 보고 026: KS CSPF intersection helper (`_ks_intersection_power`, `_performance_line`)를 `KSC9306Calculator`로 이동. ISO16358 측은 `_ks_intersection_power` thin wrapper만 유지하고 `_performance_line`은 제거.
- 보고 027: `KSC9306Calculator.calculate_cspf(measured_inputs, declared_capacity=None)` public entry 추가 (현재는 ISO common CSPF engine을 lazy import해 delegate 하는 thin path). `from_iso_calculator` / `from_config_path` 두 factory 모두 calculate_cspf를 지원한다.
- 보고 030: `core/calculator_profiles.py`에 `ks_c9306_cspf`, `ks_c9306_hspf` 두 profile record 등록 (`calculator_id=ks_c9306`, `config_path=data/region_configs/korea.json`, `enabled=True`).
- 보고 031: `tests/test_calculator_profiles.py`의 enabled snapshot 갱신(KS 두 profile 포함) + KS resolver lookup 가드 테스트 4건 추가.
- 보고 032: `core/calculator_dispatcher.py` 신규 추가. `create_calculator_for_profile(...)`이 profile resolver 결과를 받아 `KSC9306Calculator.from_config_path(...)`, `AHRICalculator(...)`, `AHRIHSPF2Calculator(...)`로 instance를 생성한다. unsupported `calculator_id`는 fail-fast. `tests/test_calculator_dispatcher.py`에 KS × 4, AHRI × 2, fail-fast × 1 총 7건 smoke tests를 추가.
- 보고 023, 024, 028은 architecture 문서(`docs/architecture/project_architecture.md`, `docs/REFACTOR_PLAN.md`, `docs/WORK_PLAN.md`, `project_log.md`, `data/region_configs/REGION_CONFIG_RULES.md`) 정렬 / 표현 정정.
- 보고 029는 `AGENTS.md`와 `AGENT_TASK_ROUTER.md`에 터미널 출력 `modified:` 표준 3-line 규칙 추가.

## Validation Summary
- 보고 021은 audit/report-only 작업이며 source docs를 수정하지 않았다 (runtime test 영향 없음).
- 보고 022는 docs/router workflow 변경이며 runtime test를 실행하지 않았다 (`git diff --check` 통과). calculator/ML/UI/JSON schema/public API에는 영향 없음.
- 본 workstream의 calculator/test track baseline (보고 022 push 직후): `258 passed, 16 failed, 13 xfailed` (16 failures 모두 ISO common HSPF formula 47/50, pure ISO track A, case 3 Excel BM/BO/CD/Y_MIN_Y_EXTD trace, half-to-full / tiny-bin accumulation, formula50 frost 등 pre-existing known mismatch).
- 025/026: 본 refactor 직후 통계 동일 (`258 passed, 16 failed, 13 xfailed`). KS keyword tests 40/40 pass. 회귀 없음.
- 027: 동일 베이스라인 유지. spot check `cspf=6.504 / annual_cooling=1943.798 / annual_power=298.852`가 `test_korea_cspf_regression_unchanged_by_diagnostics` 기대값과 정확히 일치.
- 030: snapshot test 1건 실패 추가 (`test_list_calculator_profiles_returns_enabled_profiles_only`). 의도된 등록의 직접 증거. 통계 `257 passed, 17 failed, 13 xfailed`.
- 031: snapshot mismatch 해소 + KS lookup 가드 4건 추가. 통계 `262 passed, 16 failed, 13 xfailed`로 baseline failure set 복구.
- 032: dispatcher tests 7건 추가. 통계 `269 passed, 16 failed, 13 xfailed`. baseline failure set 동일.
- 16개 pre-existing failures는 본 workstream 시작부터 종료까지 동일하게 유지되며, 본 workstream으로 인한 신규 회귀는 없다.

## Remaining Risks
- ISO common HSPF 기존 known failures 16건은 본 workstream에서 다루지 않았으며 계속 유지된다 (Formula 47/50, pure ISO track A min-to-half, case 3 Excel BM/BO/CD/Y_MIN_Y_EXTD trace, half-to-full / tiny-bin accumulation, formula50 frost branch).
- `KSC9306Calculator.calculate_cspf(...)`는 아직 ISO common CSPF engine에 delegate하는 thin path 성격이 남아 있다. ISO `calculate_cspf` 내부의 `power_interpolation_method == "ks_intersection"` 분기가 그대로이며, 이 분기와 ISO 측 KS thin wrappers의 완전 제거는 ISO common engine을 KS-unaware로 분리하는 후속 작업이 필요하다.
- `core/calculator_dispatcher.py`는 아직 UI나 다른 core 모듈에 wiring되지 않았다. dispatcher 효과는 향후 Calculator UI selector 연결 작업으로 이어졌을 때 드러난다.
- ISO16358 profile manifest는 아직 등록되지 않았으므로 dispatcher가 `iso16358` calculator_id를 라우팅하지 않는다. ISO 호출 경로는 사용자가 `ISO16358Calculator(config_path)`를 직접 호출하는 방식으로 유지된다.
- `_round_test_value`는 여전히 ISO 모듈에 남아 있어 KS naming이 ISO 측에 일부 섞여 있다.
- `tests/test_calculator_profiles.py::test_list_calculator_profiles_returns_enabled_profiles_only`는 set 동등성 snapshot 형태로 유지되어 새 profile 추가 시 동기화가 필요하다.

## Next Suggested Action
- Calculator UI selector에서 `create_calculator_for_profile(...)`을 호출해 KS / AHRI profile 진입점을 실제 사용 경로에 연결하는 작업.
- ISO16358 profile manifest 등록 + dispatcher에 `iso16358` 분기 추가 (ISO16358 region별 profile 설계 포함).
- ISO `calculate_cspf` 내부의 `ks_intersection` 분기를 KS-unaware로 분리하고 ISO 측 KS thin wrappers (HSPF 24개 + CSPF 1개)를 최종 제거하는 작업.

## Archive Candidates
- `result_reports/active/021_audit-doc-workflow-links.md`
- `result_reports/active/022_add-packaging-route.md`
- `result_reports/active/023_calculator-architecture-reset.md`
- `result_reports/active/024_refine-calculator-architecture-docs.md`
- `result_reports/active/025_separate-ks-c9306-calculator.md`
- `result_reports/active/026_separate-ks-c9306-cspf-helper.md`
- `result_reports/active/027_prepare-ks-c9306-cspf-public-entry.md`
- `result_reports/active/028_correct-region-config-architecture.md`
- `result_reports/active/029_add-modified-line-to-agent-output.md`
- `result_reports/active/030_register-ks-c9306-profiles.md`
- `result_reports/active/031_update-calculator-profile-snapshot-tests.md`
- `result_reports/active/032_add-calculator-profile-dispatcher.md`

## Project Log Sync Judgment
- `project_log.md`의 `2026-05-17 — Calculator architecture reset: ISO / KS / ASNZS boundary` 엔트리는 이미 architecture decision과 region config 표현 정정을 담고 있다. 그러나 implementation 진행 결과(KS HSPF/CSPF body 분리, KS CSPF public entry, KS profile 등록, profile snapshot 정렬, calculator dispatcher foundation 추가)는 아직 기록되지 않았다. 새 섹션을 만들지 않고 기존 2026-05-17 엔트리에 짧은 follow-up bullet로 추가한다.
- `2026-05-16 — Agent result report lifecycle workflow 정착` 엔트리는 agent 출력 표준 3-line 규칙 (보고 029)을 아직 담고 있지 않다. 같은 lifecycle workflow 흐름의 process 변화이므로 짧은 follow-up bullet로 추가한다.
- 보고 022의 Packaging route owner 연결 decision은 `project_log.md`의 기존 `2026-05-16 — Packaging route owner 연결` 엔트리에 이미 반영되어 있어 추가 갱신이 필요 없다.
- 보고 021은 source docs를 수정하지 않은 audit/report-only 활동이며 확정된 decision/failure/lesson을 별도로 남길 항목이 없어 `project_log.md` 갱신이 필요 없다.
- 위 갱신 모두 covered report 전문을 복사하지 않고 결정 수준의 짧은 요약만 남긴다.

## Commit / Push
- summary/archive/project_log 변경은 단일 commit `reports: summarize calculator architecture workstream`으로 처리하고 `origin/main`에 push한다.
