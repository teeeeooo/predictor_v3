# 081 ISO16358-2 HSPF Official Exact Golden Verification

## Scope
- Source commit: `a5f439b` (`test: add ISO16358 HSPF official exact diagnostic`)
- User requested report path: `result_reports/active/081_iso16358-2-hspf-official-exact-golden-verification.md`
- Note: report number `081` already exists in `result_reports/summaries/081_summary-calculator-ui-v1-audit-2-3.md`; this active report uses the exact path requested by the user.
- Core formulas, expected values, UI paths, EN14825/AHRI paths, adapters, and ML/inverse-search were not modified.

## Task 1 Result

### Modified Files
- Added `tests/fixtures/iso16358_hspf_official_exact_cases.json`
- Added `tests/test_iso16358_hspf_official_exact_golden.py`

### Added Test / Fixture
- The fixture preserves all 16 user-provided ISO16358-2 HSPF official exact expected cases.
- The test maps current public input schema as follows:
  - `7_min yes`: include `7_min`; `7_min no`: omit `7_min`.
  - `extended mode yes`: include `2_ext`; `extended mode no`: omit `2_ext`.
  - `2_full_f measured` / `2_half_f measured`: include current schema keys `2_full` / `2_half`, which the resolver preserves as `_f` reference points.
  - `-7_* measured`: include the corresponding optional `-7_*`; default: omit it and let the resolver path run.
- Case #13/#14 description duplicate, expected identical, preserved as provided.
- Mismatch cases are marked `xfail(strict=True)` so full pytest remains green while preserving the diagnostic evidence.

### Actual vs Expected
| case_id | expected HSTL | expected HSEC | expected HSPF | actual HSTL | actual HSEC | actual HSPF | rounded match | delta HSTL | delta HSEC | delta HSPF | branches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| 1 | 4885.4 | 1079.3 | 4.527 | 4885.4 | 1079.3 | 4.527 | yes | +0.0 | +0.0 | +0.000 | cycling,formula45_half_full,formula49_half_full_frost,saturated |
| 2 | 4885.4 | 1061.4 | 4.603 | 4885.4 | 1061.4 | 4.603 | yes | +0.0 | +0.0 | +0.000 | cycling,formula45_half_full,formula49_half_full_frost,min_half_interpolation,saturated |
| 3 | 4885.4 | 1079.0 | 4.528 | 4885.4 | 1079.3 | 4.526 | no | +0.0 | +0.3 | -0.002 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost |
| 4 | 4885.4 | 1061.1 | 4.604 | 4885.4 | 1061.4 | 4.603 | no | +0.0 | +0.3 | -0.001 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost,min_half_interpolation |
| 5 | 4885.4 | 1079.3 | 4.527 | 4885.4 | 1079.3 | 4.527 | yes | +0.0 | +0.0 | +0.000 | cycling,formula45_half_full,formula49_half_full_frost,saturated |
| 6 | 4885.4 | 1077.2 | 4.535 | 4885.4 | 1077.2 | 4.535 | yes | +0.0 | +0.0 | +0.000 | cycling,formula45_half_full,formula49_half_full_frost,saturated |
| 7 | 4885.4 | 1080.7 | 4.520 | 4885.4 | 1080.7 | 4.520 | yes | +0.0 | +0.0 | +0.000 | cycling,formula45_half_full,formula49_half_full_frost,saturated |
| 8 | 4885.4 | 1077.2 | 4.535 | 4885.4 | 1078.5 | 4.530 | no | +0.0 | +1.3 | -0.005 | cycling,formula45_half_full,formula49_half_full_frost,saturated |
| 9 | 4885.4 | 1058.0 | 4.617 | 4885.4 | 1058.7 | 4.614 | no | +0.0 | +0.7 | -0.003 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost,min_half_interpolation |
| 10 | 4885.4 | 1064.4 | 4.590 | 4885.4 | 1064.7 | 4.588 | no | +0.0 | +0.3 | -0.002 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost,min_half_interpolation |
| 11 | 4885.4 | 1061.1 | 4.604 | 4885.4 | 1061.8 | 4.601 | no | +0.0 | +0.7 | -0.003 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost,min_half_interpolation |
| 12 | 4885.4 | 1079.0 | 4.528 | 4885.4 | 1111.8 | 4.394 | no | +0.0 | +32.8 | -0.134 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost |
| 13 | 4885.4 | 1079.0 | 4.528 | 4885.4 | 1077.5 | 4.534 | no | +0.0 | -1.5 | +0.006 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost |
| 14 | 4885.4 | 1079.0 | 4.528 | 4885.4 | 1077.5 | 4.534 | no | +0.0 | -1.5 | +0.006 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost |
| 15 | 4885.4 | 1079.0 | 4.528 | 4885.4 | 1116.0 | 4.378 | no | +0.0 | +37.0 | -0.150 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost |
| 16 | 4885.4 | 1066.3 | 4.582 | 4885.4 | 1111.2 | 4.396 | no | +0.0 | +44.9 | -0.186 | cycling,formula45_half_full,formula49_half_full_frost,formula50_full_extended_frost,min_half_interpolation,saturated |

### Mismatch Judgment
- Match: 5/16 cases (`1, 2, 5, 6, 7`)
- Mismatch: 11/16 cases (`3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16`)
- Blocking: yes. The official exact expected values are now captured, but current actual output does not establish an active passing golden anchor.
- Next analysis target: ISO16358-2 HSPF extended-mode and measured/default optional point routing, especially the `2_full` / `2_half` measured frost/extended paths in cases 12, 15, 16.

## Task 2 Result

### Modified Files
- Updated `project_log.md`
- Updated `docs/WORK_PLAN.md`
- Updated `project_brief.md`
- Added this report file

### Document Updates
- `project_log.md`: recorded Tried / Result / Failed-Risk / Decision / Lesson for the official exact verification.
- `docs/WORK_PLAN.md`: marked audit_5 work as completed state and placed ISO16358-2 HSPF official exact mismatch analysis before UI redesign / table-input UI / additional UI slices.
- `project_brief.md`: reflected the 5 match / 11 mismatch diagnostic status and audit_5 adapter completion state.

### Current State Reflected
- Official source exact expected values and current calculator actuals are documented separately.
- The current repo has a strict-xfail diagnostic golden test, not a passing official exact golden anchor.
- Audit 5 adapter work is treated as complete for the first AHRI SEER2 slice.

### Next Work Order
1. Analyze ISO16358-2 HSPF official exact mismatch cases.
2. After mismatch analysis, resume calculator table-input UI design audit / AHRI-EN table UI slice / envelope chain smoke as appropriate.
3. Keep AS/NZS workbook compatibility and ML/inverse-search work separate from this ISO exact mismatch thread.

## Verification
| command | result |
| --- | --- |
| `python3 -B -m py_compile core/calculator_iso16358.py` | passed |
| `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` | `6 passed, 11 xfailed in 0.06s` |
| `python3 -B -m pytest tests/test_iso16358_hspf_formula_micro.py tests/test_iso16358_hspf_validation.py -q` | `49 passed in 0.10s` |
| `python3 -B -m pytest -q` | `370 passed, 34 xfailed in 1.71s` |
| `git diff --check` | passed |

PyQt optional skip: no PyQt-specific command was required for this task; full suite completed without PyQt skips in this environment.

## Checklist
- 16 cases are represented in the fixture/test.
- Case #13/#14 duplicate description was preserved.
- `HSTL`/`HSEC` compare at 1 decimal and `HSPF` compares at 3 decimals.
- Expected values were not changed to match actuals.
- `core/calculator_iso16358.py` was not modified.
- Mismatch cases are strict xfail and explicitly documented.
- `project_log.md`, `docs/WORK_PLAN.md`, and `project_brief.md` were updated.
