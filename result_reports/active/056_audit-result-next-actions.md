# 056 Audit Result Next Actions

## Goal

Read `AGENTS.md` and `audit_result.md`, then complete four immediately actionable follow-up tasks with staged commits and a root Markdown completion report.

## Scope

- Document/comment consistency cleanup.
- Legacy HSPF golden diagnostic location cleanup.
- UI resolver audit.
- Immediate UI resolver implementation for AHRI SEER2 construction.

## Non-goals

- No ISO/KS/ASNZS calculator math changes.
- No golden expected value changes.
- No EN14825 UI resolver implementation before EN profiles exist.
- No ML / inverse-search adapter implementation.

## Verification

- `python3 -B -m py_compile core/calculator_iso16358.py`
- `python3 -B -m pytest tests/_legacy/test_iso16358_hspf_golden_diagnostic.py tests/_legacy/test_iso16358_hspf_h8_trace.py tests/test_iso16358_hspf_validation.py -q`
- `python3 -B -m py_compile app_calculator.py ui/calc_window.py ui/calculators_2point.py core/calculator_dispatcher.py core/calculator_profiles.py`
- `python3 -B -m pytest tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q`
- `python3 -B -m pytest -q`

## Task Results

- Task 1: `core/calculator_iso16358.py` docstring and ISO separation docs now match implemented HSPF state and report archive/summary state.
- Task 2: legacy HSPF workbook diagnostic file now lives under `tests/_legacy/`.
- Task 3: `ui_resolver_audit_result.md` records remaining non-resolver UI paths and safe implementation boundary.
- Task 4: `ui/calc_window.py` AHRI SEER2 path now uses `create_calculator_for_profile(profile_id="ahri_usa_seer2")`.

## Test Results

- Legacy HSPF diagnostic targeted check: `60 passed, 17 xfailed`.
- UI resolver targeted checks: `30 passed`.
- Full suite: `288 passed, 23 xfailed`.

## Changed Files

- `core/calculator_iso16358.py`
- `iso_separation_result.md`
- `docs/REFACTOR_PLAN.md`
- `docs/WORK_PLAN.md`
- `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py`
- `tests/_legacy/test_iso16358_hspf_h8_trace.py`
- `tests/test_iso16358_hspf_validation.py`
- `docs/designs/2026-05-10-iso16358-2-hspf-h8-routing-resolver-design.md`
- `docs/iso16358/iso16358_dev_notes.md`
- `docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md`
- `docs/iso16358/regions/ks_c_9306/ks_c_9306_glossary.md`
- `iso_seperation_plan.md`
- `ui_resolver_audit_result.md`
- `ui/calc_window.py`
- `ACTIVE_DOCUMENTS.md`
- `project_log.md`
- `audit_result_next_actions_completion.md`
- `result_reports/active/056_audit-result-next-actions.md`

## Known Failures / Risks

- Existing `23 xfailed` remain expected diagnostic/deferred cases.
- EN tab remains non-resolver-backed until EN profiles are registered.
- Interactive Qt smoke was not run.

## Next Suggested Action

Design the calculator result envelope / ML adapter boundary before implementing ML or inverse-search integration.

## Scope Compliance

- No calculator formula behavior was changed.
- No golden expected values were changed.
- Test movement kept original diagnostic behavior and xfail state.

## Commit / Push

- Source commit 1: `cd0498a` (`docs: align ISO separation follow-up state`)
- Source commit 2: `d14a23f` (`test: move legacy HSPF golden diagnostics`)
- Source commit 3: `8566b97` (`docs: audit UI resolver follow-up`)
- Source commit 4: `10849cf` (`feat: route AHRI SEER2 UI through dispatcher`)
- Final docs commit: `f7804f3` (`docs: record audit result next actions`)
- Report commit: this commit (`report: record audit result next actions`)
- Push: confirmed to `origin/work/iso-separation-plan`.
