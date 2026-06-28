# Calculator Application Boundary Foundation

## Goal
- Add the UI-runtime-neutral calculator application boundary foundation for Arc 12.
- Move pure calculator profile routing ownership out of `apps/calculator/ui/`.
- Add an app-side adapter around the core calculator dispatcher without changing calculator behavior.

## Scope
- Added `apps.calculator.application` and `apps.calculator.adapters` packages.
- Moved profile label routing tables/functions to `apps.calculator.application.profile_resolver`.
- Kept `apps.calculator.ui.profile_resolver` as a short compatibility shim.
- Migrated active calculator UI imports to the new application resolver.
- Added focused tests for resolver parity, import guards, and dispatcher adapter delegation.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md`.

## Non-goals
- No calculator formula, config, profile ID, fixture, golden expected, or public result contract changes.
- No UI layout or batch UX changes.
- No ISO/ISEER usecase extraction in this slice.

## Verification
- OK: `python3 -B -m pytest tests/test_calculator_application_boundary.py tests/test_ui_tk_profile_resolver.py tests/test_calculator_dispatcher.py -q`
- OK: `python3 -B -m py_compile app_calculator.py apps/calculator/**/*.py core/calculators/**/*.py`
- OK: `python3 -B -m pytest tests -k "calculator or profile_resolver or dispatcher or application"`
- OK after regeneration: `python3 -B tools/code_checker/build_reference_map.py --check`
- OK with pre-existing soft warnings: `python3 -B tools/check_code_structure.py`
- OK: `git diff --check`
- OK: `git status --short`

## Task Results
- task 1: OK - application package created.
- task 2: OK - profile resolver ownership moved to application package with UI compatibility shim.
- task 3: OK - dispatcher adapter delegates to the existing core dispatcher.
- task 4: OK - focused tests added.

## Changed Files
- `apps/calculator/application/__init__.py`
- `apps/calculator/application/profile_resolver.py`
- `apps/calculator/adapters/__init__.py`
- `apps/calculator/adapters/core_calculator_dispatcher.py`
- `apps/calculator/ui/profile_resolver.py`
- `apps/calculator/ui/sections/iso_iseer_2point_section.py`
- `apps/calculator/ui/sections/hong_kong_cspf_section.py`
- `apps/calculator/ui/sections/hong_kong_hspf_section.py`
- `apps/calculator/ui/sections/hong_kong_cspf_batch_spec.py`
- `apps/calculator/ui/sections/iso_saso_t3_section.py`
- `apps/calculator/ui/batch_dialogs/profiles/hong_kong_hspf.py`
- `apps/calculator/ui/batch_dialogs/profiles/saso_t3.py`
- `apps/calculator/ui/tabs/iso16358_tab.py`
- `tests/test_calculator_application_boundary.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/611_calculator-application-boundary-foundation.md`

## Reference Parity
- Existing owner checked: `apps/calculator/ui/profile_resolver.py`.
- Reuse decision: reused existing resolver behavior by moving it to the application owner and leaving the UI file as a compatibility shim.
- Dispatcher behavior reused through `core.calculators.dispatcher`; no parallel construction policy was introduced.

## Structure Warnings
- none on changed/new source files.
- Existing soft warnings remain in calculator core/UI hotspot files outside this
  slice's changed source ownership.

## Read Ledger
- `apps/calculator/ui/profile_resolver.py`: lines 1-125, reason: existing resolver owner and mapping migration.
- `core/calculators/dispatcher.py`: lines 1-115, reason: app dispatcher adapter delegation target.
- `core/calculators/profiles.py`: lines 147-190, reason: resolver selector contract.
- `tests/test_ui_tk_profile_resolver.py`: lines 1-121, reason: resolver parity and import guard pattern.
- `tests/test_calculator_dispatcher.py`: lines 1-105, reason: existing dispatcher test style.
- broad read: none
- repeated read: none

```yaml
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

## Known Failures / Risks
- Remaining calculator UI sections still own calculation orchestration until later Arc 12 slices.
- The UI resolver shim is retained for compatibility and should not regain mapping ownership.

## Next Suggested Action
- Arc 12 Slice 2 - ISO/ISEER 2-point UseCase Extraction.

## Commit / Push
- commit: completed in slice commit; final hash reported in terminal output
- push: deferred until all Arc 12 slices are complete per user request

## Project Memory Delta
- none
