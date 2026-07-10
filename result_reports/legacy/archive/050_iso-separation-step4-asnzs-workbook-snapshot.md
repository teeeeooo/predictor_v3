# 050 ISO Separation Step 4 AS/NZS Workbook Snapshot

## Goal

`iso_seperation_plan.md` Step 4 범위에서 AS/NZS Excel compatibility path를 ISO common path와 분리한 상태로 점검하고, 현재 repo workbook snapshot 기반 exact-match를 별도 namespace로 추가한다.

## Scope

- AS/NZS negative assertion tests의 ISO target을 `core.calculator_iso16358_legacy`에서 새 `core.calculator_iso16358`로 전환했다.
- `reference_files/iso16358_test_sheet.xlsx` current snapshot에서 `Inverter AC` row 21-47 및 workbook output anchors를 추출해 fixture를 추가했다.
- `core/calculator_asnzs_hspf_excel.py`에 `workbook_rows` input path를 추가했다.
- Current workbook exact-match test를 추가했다.
- 관련 관리 문서를 current snapshot / historical case3 full-dump 구분에 맞춰 갱신했다.

## Modified Files

- `core/calculator_asnzs_hspf_excel.py`
- `tests/fixtures/asnzs_excel_hspf_compat/workbook_inverter_ac_current.json`
- `tests/test_asnzs_hspf_excel_compat_workbook_current_exact_match.py`
- `tests/test_asnzs_hspf_excel_compat_*.py` negative assertion import targets
- `project_brief.md`
- `docs/WORK_PLAN.md`
- `docs/REFACTOR_PLAN.md`
- `docs/architecture/project_architecture.md`
- `docs/designs/2026-05-08-asnzs-hspf-excel-compat-boundary.md`
- `iso_seperation_plan.md`
- `project_log.md`

## Verification

- `python3 -B -m py_compile core/calculator_asnzs_hspf_excel.py` passed.
- `python3 -B -m pytest tests/test_asnzs_hspf_excel_compat_*.py -q`
  - Result: `85 passed, 2 xfailed`.
- `python3 -B -m pytest tests -q`
  - Result: `271 passed, 16 failed, 13 xfailed`.
  - The 16 failures remain the known ISO HSPF baseline group.

## Remaining Risk

- Historical case3 exact-match is still not complete because the current local workbook snapshot does not match the older `case3_packet.json` anchors.
- Current workbook row displayed energies sum to within 2 Wh of `CH48`; exact-match uses workbook output anchors and keeps the displayed-row rounding discrepancy inside compatibility diagnostics.
