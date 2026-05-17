# 054 Summary: Calculator UI, KS Cleanup, ISO Separation

## Covered Reports

- `034_audit-calculator-ui-profile-dispatcher-wiring.md`
- `035_wire-ahri-hspf2-ui-to-dispatcher.md`
- `036_audit-ks-c9306-cspf-iso-dependency.md`
- `037_separate-ks-c9306-measured-input-prep.md`
- `038_separate-ks-c9306-cspf-point-resolution.md`
- `039_implement-ks-c9306-cspf-standalone-body.md`
- `040_audit-iso-cspf-ks-aware-branch-removal.md`
- `041_cleanup-ks-c9306-cspf-legacy-iso-delegate.md`
- `042_audit-iso-cspf-ks-intersection-removal.md`
- `043_remove-iso-cspf-ks-intersection-residuals.md`
- `044_iso-separation-step1-ks-hspf-test-routing.md`
- `045_iso-separation-step2a-prerename-audit.md`
- `046_iso-separation-step2b-legacy-rename.md`
- `047_iso-separation-step2c-ks-factory-cleanup.md`
- `048_iso-separation-step3a-new-iso-cspf.md`
- `049_iso-separation-step3b-new-iso-hspf.md`
- `050_iso-separation-step4-asnzs-workbook-snapshot.md`
- `051_iso-separation-step5-profile-dispatcher-ui.md`
- `052_iso-separation-completion-audit.md`
- `053_iso-remaining-work-completion.md`

## Workstream Summary

### Calculator UI / Dispatcher

- Audited calculator UI profile/dispatcher wiring.
- Wired AHRI HSPF2 UI flow through dispatcher/profile boundaries.
- Preserved UI boundary rules while moving calculator construction toward explicit profile routing.

### KS C 9306 / ISO CSPF Cleanup

- Audited ISO dependency in KS C 9306 CSPF path.
- Split KS C 9306 measured input preparation and point resolution out of ISO common assumptions.
- Completed KS C 9306 CSPF standalone body and removed legacy ISO delegate cleanup remnants.
- Removed ISO CSPF KS-aware branch and `ks_intersection` residuals from active ISO common logic.

### ISO / KS / ASNZS Calculator Series Reset

- Routed KS HSPF tests to KS calculator ownership.
- Renamed and then archived the old mixed ISO implementation under `core/_legacy/`.
- Rebuilt ISO 16358 CSPF/HSPF common logic without KS or AS/NZS workbook responsibilities.
- Added AS/NZS Energy Rating workbook compatibility as explicit `ASNZS_EXCEL_COMPAT` path.
- Reconnected profile/dispatcher/UI route for the new calculator series.
- Completed remaining active ISO HSPF formula routing and current workbook HSPF/CSPF compatibility checks.

## Decisions Preserved

- ISO common calculator must not branch on AS/NZS workbook `reference_type`.
- KS C 9306 remains a special calculator, not an ISO wrapper behavior.
- AS/NZS workbook compatibility is explicit opt-in and does not claim official production formula parity.
- Historical case3 full-dump exact parity stays deferred until the matching workbook/full dump is available.
- Result report original files 034~053 can be archived after this summary is committed.

## Verification Snapshot

- Latest full suite recorded in covered report 053: `288 passed, 23 xfailed`.
- Latest targeted ISO/ASNZS checks recorded in covered report 053: `81 passed, 21 xfailed`.

## Archive Candidates

Move covered active reports 034~053 to `result_reports/archive/` without renaming.

## Project Log Sync Judgment

`project_log.md` update required and performed in the active document inventory task, because this summary closes a multi-report calculator/ISO separation workstream and establishes an active document inventory lifecycle rule.
