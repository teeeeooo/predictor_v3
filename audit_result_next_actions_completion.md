# Audit Result Next Actions Completion

## Objective

Read `AGENTS.md` and `audit_result.md`, then complete four immediately actionable next tasks with staged commits, result reports, and a root Markdown completion report.

## Completed Tasks

### 1. Document / Comment Consistency Cleanup

- Removed stale HSPF-not-implemented wording from `core/calculator_iso16358.py`.
- Updated `iso_separation_result.md` report paths after result report archive/summary lifecycle cleanup.
- Cleaned stale next-work ordering in `docs/REFACTOR_PLAN.md`.
- Updated `docs/WORK_PLAN.md` to put UI resolver audit and adapter boundary design before ML / inverse-search work.

Commit: `cd0498a`

### 2. Legacy HSPF Golden Diagnostic Location Cleanup

- Moved `tests/test_iso16358_hspf_golden.py` to `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py`.
- Updated imports in `tests/test_iso16358_hspf_validation.py` and `tests/_legacy/test_iso16358_hspf_h8_trace.py`.
- Updated active docs that pointed to the old test path.
- Adjusted fixture/config path lookup after the move.

Commit: `d14a23f`

### 3. UI Resolver Audit

- Created `ui_resolver_audit_result.md`.
- Audited `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`, `core/calculator_profiles.py`, and `core/calculator_dispatcher.py`.
- Identified AHRI SEER2 direct constructor as the immediate implementation target.

Commit: `8566b97`

### 4. UI Resolver Follow-Up Implementation

- Replaced `ui/calc_window.py` AHRI SEER2 direct `AHRICalculator(path)` construction with `create_calculator_for_profile(profile_id="ahri_usa_seer2")`.
- Left EN and ISO stub behavior unchanged.
- Kept HSPF2 profile dispatcher path as-is.

Commit: `10849cf`

## Verification

- `python3 -B -m py_compile core/calculator_iso16358.py`
- `python3 -B -m pytest tests/_legacy/test_iso16358_hspf_golden_diagnostic.py tests/_legacy/test_iso16358_hspf_h8_trace.py tests/test_iso16358_hspf_validation.py -q`
  - `60 passed, 17 xfailed`
- `python3 -B -m py_compile app_calculator.py ui/calc_window.py ui/calculators_2point.py core/calculator_dispatcher.py core/calculator_profiles.py`
- `python3 -B -m pytest tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q`
  - `30 passed`
- `python3 -B -m pytest -q`
  - `288 passed, 23 xfailed`

## Updated Management Docs

- `project_log.md`
- `ACTIVE_DOCUMENTS.md`
- `audit_result_next_actions_completion.md`
- `result_reports/active/056_audit-result-next-actions.md`

## Remaining Work

- EN14825 UI tab still needs profiles before resolver-backed conversion.
- Calculator result envelope / ML adapter boundary design is still required before ML / inverse-search implementation.
- Interactive Qt smoke was not run in this task.
