# 126 AS/NZS Case3 External Reference Compatibility Decision

## Goal

Decide the policy for the two remaining non-legacy AS/NZS case3 xfails and clarify whether they are current production failures, marker-retirement candidates, or external reference prerequisites.

## Scope

- `tests/test_asnzs_hspf_excel_compat_case3_exact_match_contract.py`
- `tests/test_asnzs_hspf_excel_compat_packet_mapper.py`
- `tests/fixtures/asnzs_excel_hspf_compat/case3.json`
- `tests/fixtures/asnzs_excel_hspf_compat/case3_packet.json`
- `docs/WORK_PLAN.md`
- Prior reports 122, 123, and 125 for current xfail ownership context.

## Non-Goals

- Remove xfail markers.
- Change xfail strictness.
- Delete tests.
- Modify expected values, fixture data, assertions, packet mapper behavior, core calculator code, profile/dispatcher behavior, or AS/NZS compatibility implementation.
- Run Excel COM or create/estimate full row data.
- Perform result report lifecycle maintenance.

## Task 1 Result

Confirmed AS/NZS xfails:

| Test file | Test | Reason before cleanup | Strict | Current failure type |
| --- | --- | --- | --- | --- |
| `tests/test_asnzs_hspf_excel_compat_case3_exact_match_contract.py` | `test_case3_exact_match_from_component_rows_xfail_until_full_data_exists` | Case 3 exact matching requires full row data (load, hours); current packet only has observed_power. | default false | missing fixture/input fields: rows lack `load` and `hours` |
| `tests/test_asnzs_hspf_excel_compat_packet_mapper.py` | `test_packet_rows_to_component_details_xfail_until_load_hours_available` | Case 3 component row reconstruction requires load/helper/hour fields; current subset is diagnostic only. | default false | reconstruction prerequisite failure: extracted rows lack `energy_wh` |

Current fixture/packet field state:

- `case3.json` contains AS/NZS Excel compatibility reference targets: `hstl_kwh=1126.120`, `hspf=4.33824`, and `ch48_wh=1126120.47`.
- `case3_packet.json` is an `excel_com_chat_packet_subset`.
- Packet rows include `tj`, `observed_power_w`, `anchor`, `status`, and `note`.
- Packet helper column anchors list BN/BP/BY/CA/CC as `implementation_check_required`.
- Packet rows do not include full row fields required for exact reconstruction: `load`, `hours`, `energy_wh`, or resolved helper-column values.

Production path separation:

- These xfails do not guard the current ISO common HSPF production path.
- They preserve an AS/NZS Excel compatibility/external workbook reference prerequisite.
- Full row reconstruction depends on data that is intentionally absent from the current diagnostic packet.

Targeted `--runxfail` check:

- Command: `python3 -B -m pytest tests/test_asnzs_hspf_excel_compat_case3_exact_match_contract.py tests/test_asnzs_hspf_excel_compat_packet_mapper.py -q -rxX --runxfail`
- Result: `12 passed, 2 failed`.
- Failure summary:
  - `test_case3_exact_match_from_component_rows_xfail_until_full_data_exists`: `pytest.fail` because row `tj=-1.0` lacks `load` or `hours`.
  - `test_packet_rows_to_component_details_xfail_until_load_hours_available`: `ValueError("Insufficient data for energy reconstruction")` because extracted rows do not have `energy_wh`.

## Task 2 Result

Decision: keep both xfails as deferred external reference compatibility prerequisites.

Policy:

- Keep marker targets unchanged.
- Keep strictness unchanged.
- Do not delete these tests in the current phase.
- Do not fabricate or infer missing full row data.
- Defer exact reconstruction/full component row extraction to the Z-phase AS/NZS Excel compatibility calculator work.

Rationale:

- The current predictor_v3 main calculator and ISO common HSPF production path do not require these workbook exact-reconstruction checks.
- ISO common HSPF completion/verification is separate from AS/NZS Excel compatibility reconstruction.
- Full row data extraction is not in the current phase and should not be simulated with estimated fixture fields.
- Without `load`, `hours`, `energy_wh`, and helper-column values, converting these xfails into passing tests would require changing the contract or inventing data.
- The tests still have value as explicit guards against treating the current partial packet as complete workbook reconstruction input.

## Task 3 Result

Reason/owner/status wording was clarified only.

Updated reasons:

- `test_case3_exact_match_from_component_rows_xfail_until_full_data_exists` now states that the xfail is an AS/NZS Excel compatibility external-reference prerequisite, needs full component row data (`load`, `hours`, `energy_wh/helper columns`), uses a diagnostic-only packet with `observed_power`, and is separate from the ISO common production path until the deferred Z-phase.
- `test_packet_rows_to_component_details_xfail_until_load_hours_available` now states that component rows need full `load`/`hour`/`energy_wh`/helper fields for exact reconstruction, the current packet subset is diagnostic-only, and the work remains deferred to the Z-phase AS/NZS compatibility work.

Unchanged:

- xfail count.
- marker targets.
- strictness.
- expected values.
- fixture contents.
- assertions.
- packet mapper behavior.
- core calculator behavior.

## Task 4 Result

`docs/WORK_PLAN.md` was updated narrowly:

- AS/NZS case3 two xfails are now documented as an external workbook reference/full component row data prerequisite decision.
- Exact reconstruction/full row extraction remains deferred to Z-phase AS/NZS Excel compatibility work.
- Next recommended actions are:
  1. Windows PyInstaller size measurement when a Windows host is available.
  2. PyQt fatal-abort environment handling.
  3. Legacy cleanup C2 docs/archive README status header reinforcement.

`project_log.md` was not modified because this task only clarified test xfail reason/owner wording and WORK_PLAN state; it did not change calculator logic, schema, config meaning, architecture boundaries, or guard-test policy.

Result report lifecycle maintenance was not performed because this task creates a single active report and does not summarize/archive active reports.

## Task 5 Result

Verification:

- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `python3 -B -m pytest tests/test_asnzs_hspf_excel_compat_case3_exact_match_contract.py tests/test_asnzs_hspf_excel_compat_packet_mapper.py -q -rxX` -> `12 passed, 2 xfailed`.
- `python3 -B -m pytest -q -rxX --ignore=tests/test_iso16358_result_table_copy_tsv.py --ignore=tests/test_iso16358_table_excel_like_behavior.py --ignore=tests/test_app_calculator_ui_smoke.py --ignore=tests/test_spreadsheet_table_view.py` -> `568 passed, 1 skipped, 19 xfailed`.

Remaining xfail count:

- 19 xfailed total in the full-ish suite excluding the four PyQt fatal-abort files.
- 17 are `tests/_legacy` diagnostic/reference xfails.
- 2 are AS/NZS case3 external reference/full row data prerequisite xfails.

## Changed Files

- `tests/test_asnzs_hspf_excel_compat_case3_exact_match_contract.py`
- `tests/test_asnzs_hspf_excel_compat_packet_mapper.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/126_asnzs-case3-external-reference-compatibility-decision.md`

## Residual Risk

- The AS/NZS exact reconstruction path remains intentionally incomplete until full component row data is extracted or otherwise provided.
- The current packet remains diagnostic-only and should not be promoted to a full reconstruction fixture.
- Windows Excel COM/full workbook extraction remains deferred and was not attempted.
