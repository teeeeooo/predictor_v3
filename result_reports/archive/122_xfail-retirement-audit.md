# 122 — Xfail Retirement Audit

## Goal

현재 남아 있는 xfail 23개를 audit-only로 전수 조사하고, 제거 가능성 / 유지 필요성 / 별도 설계 필요성을 분류한다. 이번 작업에서는 xfail marker, expected, fixture, core, test assertion을 수정하지 않는다.

## Scope

- `tests/` xfail 선언 위치 inventory.
- pytest `-rxX` reason 확인.
- targeted `--runxfail` 실행으로 stale 후보 여부 확인.
- `docs/WORK_PLAN.md`에 짧은 상태와 후속 slice 후보 반영.
- 본 report 작성.

## Non-goals

- xfail marker 제거 또는 reason 수정.
- expected / fixture / assertion / core calculator / profile / dispatcher 수정.
- PyQt fatal-abort 4개 파일 재현 또는 해결.
- Tkinter 기능 구현.
- legacy cleanup 실행.
- result report lifecycle maintenance, archive/summaries 이동.
- `project_log.md`, `ACTIVE_DOCUMENTS.md`, architecture 문서 수정.
- `AGENTS_FULL.md` 열람.

## Verification

- Branch check: `git branch --show-current` -> `work/ui-ux-ssot-adoption`.
- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `python3 -B -m pytest -q -rxX --ignore=tests/test_iso16358_result_table_copy_tsv.py --ignore=tests/test_iso16358_table_excel_like_behavior.py --ignore=tests/test_app_calculator_ui_smoke.py --ignore=tests/test_spreadsheet_table_view.py` -> **568 passed, 1 skipped, 23 xfailed**.
- `python3 -B -m pytest tests/_legacy -q -rxX` -> **35 passed, 17 xfailed**.
- `python3 -B -m pytest tests/test_iso16358_hspf_pure_iso_track_a.py tests/test_asnzs_hspf_excel_compat_case3_exact_match_contract.py tests/test_asnzs_hspf_excel_compat_packet_mapper.py -q -rxX` -> **19 passed, 6 xfailed**.
- `rg "xfail|XFAIL|pytest.mark.xfail|xfail" tests docs -n` executed for declaration inventory.

## Count Summary

| bucket | count | source |
| --- | ---: | --- |
| Total xfailed in full-ish suite | 23 | pytest `-rxX` |
| `tests/_legacy/` xfailed | 17 | `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py` |
| non-legacy xfailed | 6 | ISO pure-route 4 + AS/NZS case3 2 |
| stale xfail candidates | 0 | targeted `--runxfail` all still fail |

No pytest config file was found at repo root among `pytest.ini`, `pyproject.toml`, `setup.cfg`, or `tox.ini`.

## Xfail Inventory

### Legacy xfails

| test file | test name / marker | reason | strict | related feature | status | likely original intent |
| --- | --- | --- | --- | --- | --- | --- |
| `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py` | `test_iso16358_2_hspf_seven_case_golden_matrix[case_1]` | case 1 workbook oracle discrepancy / undocumented branch-specific rounding | true | ISO16358-2 HSPF workbook golden | legacy diagnostic | preserve workbook-oracle mismatch while active formula routes moved elsewhere |
| same | `case_2` | workbook-golden optional/frost/boundary routing not fully implemented | true | ISO16358-2 HSPF workbook golden | legacy diagnostic | pin legacy seven-case matrix mismatch |
| same | `case_3` | workbook oracle aligns with CHSE 1126/HSPF 4.338 while common path remains high; investigate Formula 49 or optional branch selection | true | ISO16358-2 HSPF case3 | legacy + external reference compatibility | preserve workbook/reference mismatch for later AS/NZS or workbook-oracle decision |
| same | `case_4` | workbook-golden optional/frost/boundary routing not fully implemented | true | ISO16358-2 HSPF workbook golden | legacy diagnostic | pin legacy seven-case matrix mismatch |
| same | `case_5` | workbook-golden optional/frost/boundary routing not fully implemented | true | ISO16358-2 HSPF workbook golden | legacy diagnostic | pin legacy seven-case matrix mismatch |
| same | `case_6` | workbook-golden optional/frost/boundary routing not fully implemented | true | ISO16358-2 HSPF workbook golden | legacy diagnostic | pin legacy seven-case matrix mismatch |
| same | `case_7` | workbook-golden optional/frost/boundary routing not fully implemented | true | ISO16358-2 HSPF workbook golden | legacy diagnostic | pin legacy seven-case matrix mismatch |
| same | `case_8` | workbook-golden optional/frost/boundary routing not fully implemented | true | ISO16358-2 HSPF workbook golden | legacy diagnostic | pin legacy seven-case matrix mismatch |
| same | `test_case3_common_path_bin_level_trace_diagnostic` | archived legacy workbook diagnostics use pre-separation workbook oracle expectations | true | ISO16358-2 HSPF case3 trace | legacy diagnostic | keep trace comparison to old workbook oracle without blocking active ISO path |
| same | `test_case3_formula49_equivalent_simulation_diagnostic` | same shared legacy workbook diagnostic reason | true | Formula 49 / case3 simulation | legacy diagnostic | retain diagnostic trace for old hypothesis |
| same | `test_case3_excel_dynamic_routing_simulation_diagnostic` | same | true | case3 Excel dynamic routing | legacy diagnostic | retain workbook-route simulation experiment |
| same | `test_case3_excel_formula_structure_cop_simulation_diagnostic` | same | true | case3 COP formula structure | legacy diagnostic | retain formula structure comparison |
| same | `test_case3_excel_bm_cycling_simulation_diagnostic` | same | true | case3 BM cycling | legacy diagnostic | retain partial Excel anchor simulation |
| same | `test_case3_excel_anchor_bm_cycling_simulation_diagnostic` | same | true | case3 Excel anchor BM cycling | legacy diagnostic | retain partial Excel anchor simulation |
| same | `test_case3_excel_bo_min_half_simulation_diagnostic` | same | true | case3 BO min/half | legacy diagnostic | retain partial Excel anchor simulation |
| same | `test_case3_excel_cd_full_extd_simulation_diagnostic` | same | true | case3 CD full/extd | legacy diagnostic | retain partial Excel anchor simulation |
| same | `test_iso16358_hspf_case3_y_min_y_extd_trace_only_component_sum` | same | true | case3 component sum trace | legacy diagnostic | retain trace-only component-sum comparison |

### Non-legacy xfails

| test file | test name / marker | reason | strict | related feature | status | likely original intent |
| --- | --- | --- | --- | --- | --- | --- |
| `tests/test_iso16358_hspf_pure_iso_track_a.py` | `test_pure_iso_track_a_half_to_full_formula_45_non_frost_route_level_xfail` | Formula 45 half-to-full routing deferred; current main route uses capacity-linear interpolation | true | ISO pure-route Formula 45 | active known mismatch | guard deferred pure ISO routing work |
| same | `test_pure_iso_track_a_half_to_full_formula_49_frost_route_level_xfail` | Formula 49 frost half-to-full routing deferred; current main route uses capacity-linear interpolation | true | ISO pure-route Formula 49 | active known mismatch | guard deferred pure ISO routing work |
| same | `test_pure_iso_track_a_full_to_extended_formula_47_non_frost_route_level_xfail` | Formula 47 non-frost full-to-extended routing deferred; current main route falls back to saturated handling | true | ISO pure-route Formula 47 | active known mismatch | guard deferred pure ISO routing work |
| same | `test_pure_iso_track_a_full_to_extended_formula_50_frost_route_level` | Formula 50 frost full-to-extended routing active but differs from hand-calculated pure ISO contract | true | ISO pure-route Formula 50 | active known mismatch / design needed | pin route-level discrepancy for later calculator audit |
| `tests/test_asnzs_hspf_excel_compat_case3_exact_match_contract.py` | `test_case3_exact_match_from_component_rows_xfail_until_full_data_exists` | Case 3 exact matching requires full row data; current packet only has observed_power | false | AS/NZS Excel compatibility case3 | external reference compatibility | mark missing workbook row inputs required for exact reconstruction |
| `tests/test_asnzs_hspf_excel_compat_packet_mapper.py` | `test_packet_rows_to_component_details_xfail_until_load_hours_available` | Case 3 component row reconstruction requires load/helper/hour fields; current subset is diagnostic only | false | AS/NZS packet mapper | external reference compatibility | mark current packet as diagnostic-only until full row data exists |

`tests/test_iso16358_hspf_official_exact_golden.py` still contains `XFAIL_CASE_IDS`, but it is an empty `frozenset()` and contributes 0 xfailed tests.

## Targeted `--runxfail` Results

| target | result | failure type | retirement judgment |
| --- | --- | --- | --- |
| `tests/_legacy` | 17 failed, 35 passed | assertion mismatch against workbook/oracle or stale diagnostic constants | no stale marker removal; classify as legacy diagnostic / external reference compatibility |
| `tests/test_iso16358_hspf_pure_iso_track_a.py` | 4 failed, 7 passed | calculator logic mismatch and one runtime `ValueError` for required `7_half` input | no stale marker removal; split into pure ISO routing audit |
| AS/NZS case3 files | 2 failed, 12 passed | missing fixture/input fields (`load`, `hours`, `energy_wh`) | no stale marker removal; requires external row-data prerequisite decision |

Representative failures:

- legacy seven-case matrix: HSPF / CHSE mismatches remain for cases 1-8.
- legacy case3 diagnostics: expected `CASE3_COMMON_HSEC_WH` / `4.308` constants no longer match current common result (`4.324` in targeted output).
- Formula 45: expected HSEC `333.3333333333333`, actual `332.4593827903378`.
- Formula 49: expected HSTL `1150.0`, actual `1500.0`.
- Formula 47: current normalizer raises `ValueError` because `7_half` is required.
- Formula 50: expected HSEC `516.1290322580645`, actual `535.6634845349414`.
- AS/NZS: packet rows are still missing load/hours or energy reconstruction fields.

## Classification

| category | tests | count | judgment |
| --- | --- | ---: | --- |
| stale xfail candidate | none | 0 | no marker-only cleanup found |
| active known mismatch | ISO pure-route Formula 45/49/47/50 | 4 | needs calculator-specific design/audit before any marker removal |
| legacy diagnostic xfail | legacy seven-case matrix + case3 diagnostics | 17 | keep for now; reason/owner wording may be cleaned separately |
| external reference compatibility xfail | AS/NZS case3 exact/component-row tests; legacy case3 overlaps | 2 direct + legacy overlap | requires full workbook row-data/reference decision |
| environment-dependent xfail or skip confusion | none in xfail set | 0 | PyQt fatal-abort files are excluded baseline problems, not xfails |
| reason unknown / identity unclear | none | 0 | all active xfails have explicit reasons |

## Cleanup Slice Candidates

### 1. stale xfail marker removal

- **Purpose**: remove markers only when targeted `--runxfail` passes.
- **Target xfail/test files**: currently none.
- **Include**: marker removal only after fresh passing evidence.
- **Exclude**: expected/fixture/core/assertion changes.
- **Prerequisite**: at least one xfail passes with `--runxfail`.
- **Verification**: targeted pytest with and without `--runxfail`; full-ish suite excluding PyQt crash files.

### 2. `tests/_legacy` diagnostic xfail reason cleanup

- **Purpose**: clarify that 17 legacy xfails are active diagnostic/reference tests, not deletion candidates.
- **Target xfail/test files**: `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py`.
- **Include**: reason/owner cleanup only, possibly README/status documentation if separately approved.
- **Exclude**: marker removal, expected changes, core changes.
- **Prerequisite**: decide naming/owner policy for active diagnostic tests under `_legacy`.
- **Verification**: `python3 -B -m pytest tests/_legacy -q -rxX`.

### 3. external reference compatibility xfail decision

- **Purpose**: decide whether AS/NZS case3 and workbook-oracle diagnostics remain reference compatibility pins or move to a new oracle/reference workflow.
- **Target xfail/test files**: AS/NZS case3 files and legacy case3 diagnostic subset.
- **Include**: audit of required workbook row fields and reference packet prerequisites.
- **Exclude**: fabricating row data, updating expected values, core changes.
- **Prerequisite**: full row data or explicit decision that current packet remains diagnostic-only.
- **Verification**: targeted AS/NZS tests with `-rxX`; optional packet fixture schema checks if later added.

### 4. calculator-specific expected/fixture mismatch audit

- **Purpose**: audit ISO pure-route Formula 45/49/47/50 mismatches and decide whether expected, fixture shape, or core routing owns each failure.
- **Target xfail/test files**: `tests/test_iso16358_hspf_pure_iso_track_a.py`.
- **Include**: read-only route trace and design gate before implementation.
- **Exclude**: marker removal mixed with expected/fixture/core changes.
- **Prerequisite**: Design Gate for common-vs-region-specific routing boundary if core behavior might change.
- **Verification**: targeted pure ISO test with `--runxfail`, then normal targeted tests and full-ish suite after any later implementation.

### 5. environment-dependent PyQt test handling

- **Purpose**: keep PyQt fatal-abort handling separate from xfail retirement.
- **Target files**: `tests/test_iso16358_result_table_copy_tsv.py`, `tests/test_iso16358_table_excel_like_behavior.py`, `tests/test_app_calculator_ui_smoke.py`, `tests/test_spreadsheet_table_view.py`.
- **Include**: environment handling/skip strategy only in a separate PyQt slice.
- **Exclude**: xfail cleanup and calculator expected/fixture/core work.
- **Prerequisite**: reproduce or define supported PyQt test host.
- **Verification**: PyQt-targeted tests on supported host; full-ish suite remains with documented ignores until then.

Recommended first actual cleanup: **Slice 2 — `tests/_legacy` diagnostic xfail reason cleanup**. It is lower risk than changing calculator behavior or external workbook data, and it reduces ambiguity before deciding whether any legacy diagnostic should be retired, renamed, or moved. It should not remove markers.

## WORK_PLAN Update

`docs/WORK_PLAN.md` now records:

- xfail audit completed with 23 = 17 legacy + 6 non-legacy.
- no stale marker-only removal candidate found from targeted `--runxfail`.
- xfail retirement audit/cleanup should take priority over legacy cleanup C2 for immediate test debt clarity.
- PyInstaller size measurement remains pending until Windows host is available.
- Tkinter MVP and code structure guard status remain unchanged.

## Lifecycle Maintenance

This task intentionally does not perform result report lifecycle maintenance. After adding report 122, `result_reports/active/` reaches 8 files (115-122). Next work before or after cleanup should review lifecycle maintenance, but archive/summaries moves are out of scope here.

## Changed Files

- `docs/WORK_PLAN.md`
- `result_reports/active/122_xfail-retirement-audit.md`

## Known Risks

- `--runxfail` was targeted, not run across the full suite, to avoid mixing the PyQt fatal-abort files and unrelated broad execution risk.
- Legacy diagnostics may contain stale constants from old common-path output; this audit does not decide whether to update or retire them.
- AS/NZS exact reconstruction cannot be resolved without full row data or an explicit compatibility decision.

## Scope Compliance

No xfail markers, expected values, fixtures, assertions, core calculator code, profiles, dispatchers, `project_log.md`, `ACTIVE_DOCUMENTS.md`, architecture docs, archive/summaries, or lifecycle-maintenance files were modified.

## Commit / Push

- Source/docs commit: `29a1c01` (`docs: record xfail retirement audit status`).
- Report commit: this report commit.
- Push: pending.
