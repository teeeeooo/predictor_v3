# ISO Separation Result

## Objective Checklist

- Read `AGENTS.md` and follow task routing/report rules: done. Result reports were written under `result_reports/active/`.
- Work on a new branch: done on `work/iso-separation-plan`, pushed to origin.
- Follow `iso_seperation_plan.md`: Steps 1-5 completed.
- Commit/push during work: done with source/docs commits separated from report commits where practical.
- Update `result_reports` and `project_log.md`: done through reports 044-051 and project log follow-ups.
- Update docs/data when needed: docs were updated for the ISO/KS/ASNZS boundary, current workbook snapshot, work plan, architecture notes, and project brief. No `data/region_configs/*.json` change was needed.
- Clean unnecessary tests under `tests`: diagnostic/mixed legacy tests were moved to `tests/_legacy/`; active tests were retargeted to the new calculators where appropriate. No further tracked test deletion was made because remaining legacy-target tests preserve case3/golden diagnostics or active baseline evidence.
- Write Markdown result: this file plus `result_reports/active/044` through `051`.

## Completed Work

- KS C 9306 HSPF tests now use `KSC9306Calculator` directly.
- Existing mixed ISO implementation was renamed to `core/calculator_iso16358_legacy.py`.
- New `core/calculator_iso16358.py` now owns ISO 16358 CSPF/HSPF common logic without KS or AS/NZS workbook helper code.
- `core/calculator_ks_c9306.py` no longer keeps the old ISO compatibility factory/reference.
- `core/calculator_asnzs_hspf_excel.py` owns AS/NZS Excel compatibility snapshot calculation under `ASNZS_EXCEL_COMPAT` only.
- ISO/KS/ASNZS profiles and dispatcher routing were registered, and the calculator UI now constructs ISO CSPF calculators through profile routing rather than legacy direct instantiation.

## Verification Summary

- Step 5 targeted checks: `30 passed` for profile/dispatcher tests.
- AS/NZS compatibility checks: `85 passed, 2 xfailed`.
- Full suite after Step 5: `280 passed, 16 failed, 13 xfailed`.
- The 16 failures remain the known ISO HSPF baseline group and were not hidden with expected/tolerance/xfail edits.
- UI verification was compile/import-level only; no interactive Qt smoke was run.

## Reports

- `result_reports/active/044_iso-separation-step1-ks-hspf-test-routing.md`
- `result_reports/active/045_iso-separation-step2a-prerename-audit.md`
- `result_reports/active/046_iso-separation-step2b-legacy-rename.md`
- `result_reports/active/047_iso-separation-step2c-ks-factory-cleanup.md`
- `result_reports/active/048_iso-separation-step3a-new-iso-cspf.md`
- `result_reports/active/049_iso-separation-step3b-new-iso-hspf.md`
- `result_reports/active/050_iso-separation-step4-asnzs-workbook-snapshot.md`
- `result_reports/active/051_iso-separation-step5-profile-dispatcher-ui.md`

## Remaining Work

- Resolve the known ISO HSPF 16-failure baseline in a separate pure ISO / workbook oracle routing task.
- Historical AS/NZS case3 full-dump exact parity remains Z-phase until the matching workbook/full dump is available.
- Run an interactive Qt smoke for Calculator UI before treating UI exposure as production-ready.
