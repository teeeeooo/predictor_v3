# 125 — Legacy Diagnostic Xfail Reason / Owner Cleanup

## Goal

Clarify that the remaining `tests/_legacy` xfails are active diagnostic/reference xfails for historical workbook-oracle context, not deletion candidates and not current production ISO16358-2 HSPF official-exact failures.

## Scope

- Inspect `tests/_legacy` xfail count and reasons.
- Update reason/owner/status wording in `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py`.
- Add `tests/_legacy/README.md` to document active diagnostic/reference ownership.
- Update `docs/WORK_PLAN.md` with the completed cleanup and next action.
- Do not change marker count, expected values, fixtures, assertions, or core code.

## Non-goals

- Removing xfail markers.
- Changing xfail targets.
- Updating expected values, fixtures, assertions, profiles, dispatchers, or core calculator logic.
- Modifying AS/NZS xfails.
- Modifying ISO pure-route tests.
- Solving PyQt fatal-abort files.
- Tkinter work or PyInstaller work.
- Legacy file deletion/move/rename.
- Result report lifecycle maintenance.
- `project_log.md`, `ACTIVE_DOCUMENTS.md`, or architecture doc changes.
- AGENTS_FULL.md access.

## Task 1 Results

`tests/_legacy` baseline before edits:

- `python3 -B -m pytest tests/_legacy -q -rxX` -> 35 passed, 17 xfailed.
- All 17 xfails are in `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py`.
- 8 xfails come from `test_iso16358_2_hspf_seven_case_golden_matrix[case_1..8]`.
- 9 xfails use `LEGACY_WORKBOOK_DIAGNOSTIC_XFAIL` on case3 diagnostic/trace/reference tests.

Current reason/owner issues found:

- Some reason strings still used old phrases such as "current Python common routing" and "pure ISO formula/validation tests".
- The reasons did not consistently say that these are legacy workbook-oracle diagnostic/reference xfails.
- The reasons did not consistently state that production ISO16358-2 HSPF official-exact coverage is separate.
- There was no folder-level README explaining that `_legacy` is still pytest-collected active diagnostic/reference coverage and not a deletion queue.

Production ISO path separation judgment:

- These 17 xfails are not current production official-exact failures.
- Production official-exact HSPF is covered by `tests/test_iso16358_hspf_official_exact_golden.py`, where `XFAIL_CASE_IDS` is empty.
- The legacy xfails preserve historical workbook-oracle and AS/NZS investigation context and require a separate decommission/design decision.

## Task 2 Results

Updated reason/owner/status wording:

- Added module-level `LEGACY_WORKBOOK_ORACLE_OWNER`:
  - `legacy workbook-oracle diagnostic/reference`
  - `not production ISO16358-2 HSPF official-exact path`
  - `decommission requires a separate design decision`
- Updated `LEGACY_WORKBOOK_DIAGNOSTIC_XFAIL` reason to use that owner string and mention historical workbook/AS-NZS oracle investigation context.
- Updated `iso_hspf_xfail_reason(case)` for the seven-case matrix:
  - case 1: historical workbook-oracle rounding/boundary diagnostic.
  - case 3: historical CHSE 1126/HSPF 4.338 workbook-oracle reference and Formula 49/optional-branch investigation.
  - other cases: historical optional/frost/boundary routing diagnostics.

README:

- Added `tests/_legacy/README.md`.
- It states that the folder is still collected by pytest.
- It states that `_legacy` does not mean safe to delete.
- It states that the xfails are active diagnostic/reference tests for historical workbook-oracle and AS/NZS investigation context.
- It states that these xfails are not production ISO16358-2 HSPF official-exact failures.
- It states that marker removal, expected/core changes, and decommission require a separate design decision.

Behavior unchanged:

- Xfail markers were not removed.
- Xfail target set was not changed.
- Expected values, fixtures, assertions, and core code were not changed.

## Task 3 Results

Post-change `tests/_legacy` result:

- `python3 -B -m pytest tests/_legacy -q -rxX` -> 35 passed, 17 xfailed.
- The 17 xfail reasons now show legacy workbook-oracle diagnostic/reference ownership and the production official-exact separation.

Official exact golden:

- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` -> 17 passed.

Full-ish suite:

- `python3 -B -m pytest -q -rxX --ignore=tests/test_iso16358_result_table_copy_tsv.py --ignore=tests/test_iso16358_table_excel_like_behavior.py --ignore=tests/test_app_calculator_ui_smoke.py --ignore=tests/test_spreadsheet_table_view.py` -> 568 passed, 1 skipped, 19 xfailed.

Xfail count:

- `tests/_legacy` xfail count is intentionally unchanged at 17.
- Full-ish suite remains 19 xfailed: 17 legacy diagnostic/reference + 2 AS/NZS case3 prerequisite xfails.

## Task 4 Results

`docs/WORK_PLAN.md` now records:

- ISO pure-route obsolete xfails were already removed by 124.
- `tests/_legacy` 17 xfails now have clarified legacy workbook-oracle diagnostic/reference owner/status.
- Remaining xfails are `tests/_legacy` 17 + AS/NZS case3 2.
- Next recommended action:
  1. AS/NZS case3 external reference compatibility decision.
  2. Windows PyInstaller size measurement when a Windows host is available.
  3. PyQt fatal-abort environment handling.

Lifecycle maintenance is excluded:

- This task creates one active report (`125`) and does not archive or summarize reports.
- `project_log.md` and `ACTIVE_DOCUMENTS.md` are intentionally unchanged.

## Task 5 Results

Verification:

- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `python3 -B -m pytest tests/_legacy -q -rxX` -> 35 passed, 17 xfailed.
- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` -> 17 passed.
- Full-ish suite excluding 4 PyQt fatal-abort files -> 568 passed, 1 skipped, 19 xfailed.

Remaining xfail count:

- 19 xfailed: 17 `tests/_legacy` diagnostic/reference xfails + 2 AS/NZS case3 prerequisite xfails.

## Changed Files

- `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py`
- `tests/_legacy/README.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/125_legacy-diagnostic-xfail-reason-owner-cleanup.md`

## Known Risks

- The legacy diagnostics still xfail by design; this task only clarifies ownership/status.
- The folder name `_legacy` can still be misunderstood without reading the README. A future design-gated decommission or rename decision remains separate.
- AS/NZS case3 xfails remain untouched and should be handled in a separate compatibility decision slice.

## Scope Compliance

No xfail marker was removed or retargeted. No expected value, fixture, assertion, core calculator, profile, dispatcher, AS/NZS test, ISO pure-route test, PyQt test, Tkinter code, `project_log.md`, `ACTIVE_DOCUMENTS.md`, architecture doc, archive, or summary was modified.

## Commit / Push

- Commit: this source/docs/report commit.
- Push: pending.
