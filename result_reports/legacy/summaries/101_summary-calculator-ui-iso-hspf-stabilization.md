# 101 Summary — Calculator UI table workflow + ISO16358-2 HSPF stabilization

## Summary Scope
result_reports/active 누적분 (082~100, 19건) 정리. 두 개의 큰 workstream을 하나의 summary로 묶는다.
- Workstream A: Calculator UI horizontal spreadsheet table 전환과 global Excel-like table contract 확립.
- Workstream B: ISO16358-2 HSPF official exact 16-case golden 정상화 (root-cause audit → -7_ext factor fix → fixture expected 정렬).
두 흐름 모두 종료 상태이며, 다음 슬라이스는 ISO table UI를 contract에 맞추는 alignment 작업이다.

## Covered Reports
- 082 audit-iso16358-2-hspf-xlsm-verification
- 083 iso16358-2-hspf-official-exact-golden-verification
- 084 fixture-hygiene-and-calculator-table-unit-boundary-design
- 085 calculator-unit-normalization-and-envelope-chain-smoke
- 086 global-spreadsheet-table-contract
- 087 spreadsheet-table-component-harness
- 088 ahri-seer2-horizontal-table-input-slice
- 089 ahri-hspf2-horizontal-table-input-slice
- 090 spreadsheet-table-view-controller
- 091 iso16358-hspf-reference-status-hold
- 092 en14825-multiclimate-table-input-slice
- 093 spreadsheet-table-ux-polish
- 094 iso16358-table-contract-alignment-audit
- 095 excel-like-table-contract-clarification
- 096 iso16358-hspf-frost-trace-patch
- 097 iso16358-hspf-boundary-cop-alignment
- 098 iso16358-hspf-remaining-mismatch-root-cause-audit
- 099 iso16358-hspf-minus7-ext-default-factor-fix
- 100 iso16358-hspf-official-exact-golden-update

## Key Decisions
- 전역 PyQt table UI는 `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` 단일 owner로 두고, 모든 table surface는 Excel-like behavior (Ctrl+C/V TSV, Delete clear, Ctrl+Z undo, Tab/Enter navigation, invalid numeric 시각화) 를 기본으로 한다 (086, 095).
- AHRI / EN14825 입력은 horizontal spreadsheet table로 전환하고, ML W ↔ profile-native 단위 변환은 `core/calculator_unit_adapter.py` 한 곳에서만 수행한다 (085, 088, 089, 092).
- ISO16358-2 HSPF 공통 path는 XLSM 원문 reference와 formula 단위 일치 (082). frost flag는 bin trace에 명시 노출 (096). Formula 44/45/47/48/49/50 boundary COP 보간은 ISO 원문 표현과 alignment-only rewrite (097).
- ISO16358-2 HSPF mismatch의 dominant cause는 `_iso_hspf_extended_minus7_default()`가 0.734/0.877을 2°C frost measured에 직접 곱하던 점. 2-step (×1.12/×1.06 → ×0.734/×0.877) 으로 정정 (098 audit → 099 fix).
- 091 시점의 "external reference script 해석 오류" 가설은 부분적이었고, 실제 원인은 repo 내부 default factor 적용 대상 오류였음 (099/100에서 종결).
- ISO16358-2 HSPF official exact fixture expected는 원문 audit + 099 fix 이후 actual을 final golden으로 둔다 (100). `XFAIL_CASE_IDS`는 빈 frozenset.

## Completed Work
- Global Excel-like spreadsheet table contract 확정 및 entry doc hook 적용 (086, 095).
- `SpreadsheetTableModel` / `SpreadsheetTableView` 공통 component + regression harness (087, 090).
- AHRI SEER2 / AHRI HSPF2 / EN14825 SEER / EN14825 SCOP (multi-climate) horizontal table-input UI slice (088, 089, 092).
- Invalid numeric visual indicator + Tab/Shift+Tab/Enter/Shift+Enter navigation (093).
- ISO16358 UI table contract gap audit — alignment 후보 식별 (094, audit only).
- `core/calculator_unit_adapter.py` 도입과 envelope chain end-to-end smoke (085).
- ISO16358-2 HSPF XLSM reference verification + official exact diagnostic 도입 (082, 083).
- ISO16358-2 HSPF frost trace 명시 노출 (096).
- Formula 44/45/47/48/49/50 boundary COP alignment + helper / focused test (097).
- 남은 mismatch root-cause cluster 분류 + 원문 audit 5항목 식별 (098).
- `-7_ext` default factor 2-step 변환 정정 (099).
- official exact 16-case fixture expected 갱신 + `XFAIL_CASE_IDS` 비우기, 16/16 pass (100).

## Remaining Work
- ISO16358 (CSPF 2-point / Hong Kong / SASO T3) 입력 table을 공통 `SpreadsheetTableView` + Excel-like behavior로 정렬 (094 audit 결과 alignment 후보).
- ISO result/read-only table (TwoPointTableModel / RegionResultTableModel / TraceTableModel / RegionDetailTab.table) 에 TSV copy 추가.
- `core/calculator_unit_adapter.py`에 ISO / KS / EN profile 추가.
- ML / inverse-search 복귀 준비.

## Known Risks
- 100 fixture가 final golden이 된 이후 ISO16358-2 HSPF 계산 path를 추가 수정하면 16-case golden이 다시 흔들릴 수 있다. 그런 수정이 들어올 때는 원문 audit + expected 재정렬을 동반해야 한다.
- 094 audit 결과 ISO table 입력 UI는 contract drift 상태. UI alignment 슬라이스를 시작하기 전 contract gap을 다시 한 번 확인해야 한다.
- Hong Kong HSPF audit은 이번 lifecycle maintenance 범위 밖이며, 별도 작업으로 분리해야 한다 (본 summary에 포함하지 않음).

## Project Log Sync Judgment
- 099/100 시점에 ISO16358-2 HSPF -7_ext fix + golden update를 이미 `project_log.md`에 phase log로 append함 (2026-05-19 항목).
- UI 흐름 (086~095) 은 contract 문서가 single owner이고 active doc에도 반영되어 있어 별도 log entry는 불필요.
- 본 lifecycle maintenance 자체는 metadata-only 정리이므로 새 project_log 항목을 만들지 않는다. 기존 2026-05-19 항목에 lifecycle-maintenance 흔적을 한 줄 정도 짧게 추가하는 정도면 충분.

## Archive Candidates
- Covered Reports 19건 (082~100) 전부를 `result_reports/archive/`로 이동.
- 이동 시 파일명/번호 변경 없음.
- 본 summary (`101_summary-*.md`) 는 `result_reports/summaries/`에 그대로 둔다.

## Active Reports After Maintenance
- 없음 (active 폴더는 비어 있는 상태로 전환).

## Next Suggested Actions
1. ISO table Excel-like behavior patch (`ProfileInputGridModel` / `ProfileInputGridView`).
2. ISO result/read-only table copy TSV (`TwoPointTableModel` / `RegionResultTableModel` / `TraceTableModel` / `RegionDetailTab.table`).
3. unit adapter 확장 — ISO / KS / EN profile을 `core/calculator_unit_adapter.py`에 추가.
4. ML / inverse-search 복귀 준비.

## Verification
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → pass (lifecycle 작업 안전 확인).
- `python3 -B -m pytest -q` → 425 passed, 4 skipped, 23 xfailed (100 commit 시점과 동일).
- git working tree는 lifecycle 시작 시점 clean. unrelated dirty file 없음.

## Commit / Push
- lifecycle maintenance commit 하나로 묶음 (summary 생성 + active → archive 이동 + project_log + ACTIVE_DOCUMENTS 갱신 여부).
- `ACTIVE_DOCUMENTS.md` update: scope에 따라 result_reports lifecycle 이 별도 항목이 아니므로 변경 불필요. summary 작성 시점 기준으로 active doc owner 관계 변화 없음 → "ACTIVE_DOCUMENTS.md update not needed".
