# ISO/ISEER 2-point UseCase Extraction

## Goal
- Extract ISO/ISEER 2-point single calculation orchestration from the Tk section into an application usecase.
- Keep the Tk section responsible for widget text reads and rendering only.

## Scope
- Added `apps.calculator.application.iso_iseer_2point` models and usecase.
- Updated `apps/calculator/ui/sections/iso_iseer_2point_section.py` to call the usecase and render its returned DTOs.
- Added focused usecase and source-guard tests.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- Updated `docs/WORK_PLAN.md` next action.

## Non-goals
- No batch handler migration; that is Slice 3.
- No SASO, Hong Kong, EN14825, or AHRI changes.
- No calculator formula, config, profile ID, fixture, golden expected, or public result contract changes.
- No UI visual redesign.

## Verification
- OK: `python3 -B -m pytest tests/test_calculator_iso_iseer_2point_usecase.py tests/test_ui_tk_iso_table_autocalc.py -k "iso_iseer_2point or iso_iseer_detail" -q`
- OK: `python3 -B -m py_compile apps/calculator/application/iso_iseer_2point/*.py apps/calculator/ui/sections/iso_iseer_2point_section.py`
- OK: `python3 -B -m py_compile app_calculator.py apps/calculator/**/*.py core/calculators/**/*.py`
- OK: `python3 -B -m pytest tests -k "iso_iseer or calculator or cspf or usecase"`
- OK after regeneration: `python3 -B tools/code_checker/build_reference_map.py --check`
- OK with pre-existing soft warnings: `python3 -B tools/check_code_structure.py`
- OK: `git diff --check`
- OK: `git status --short`

## Task Results
- task 1: OK - UI-neutral usecase result models added.
- task 2: OK - usecase handles empty, invalid, valid, and calculation-error statuses.
- task 3: OK - Tk section no longer imports core dispatcher or calls `calculate_cspf`.
- task 4: OK - focused tests added.

## Changed Files
- `apps/calculator/application/iso_iseer_2point/__init__.py`
- `apps/calculator/application/iso_iseer_2point/models.py`
- `apps/calculator/application/iso_iseer_2point/usecase.py`
- `apps/calculator/ui/sections/iso_iseer_2point_section.py`
- `tests/test_calculator_iso_iseer_2point_usecase.py`
- `tests/test_ui_tk_iso_iseer_2point_controller_switch.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/612_iso-iseer-2point-usecase-extraction.md`

## Reference Parity
- Existing reference checked: `apps/calculator/ui/sections/iso_iseer_2point_section.py`.
- Existing app boundary reused: `apps.calculator.application.profile_resolver` and `apps.calculator.adapters.core_calculator_dispatcher`.
- Local formatting reason: row/detail string formatting moved into the usecase because the existing formatter lives under the UI package and cannot be imported by application code.

## Structure Warnings
- none on changed/new source files.
- Existing soft warnings remain in calculator core/UI hotspot files outside this
  slice's changed source ownership.

## Read Ledger
- `apps/calculator/ui/sections/iso_iseer_2point_section.py`: lines 1-320, reason: explicit extraction target and method boundary.
- `apps/calculator/ui/sections/iso_iseer_2point_result_table.py`: lines 91-140, reason: result row/status rendering contract.
- `apps/calculator/ui/sections/result_formatting.py`: lines 18-55, reason: existing formatting behavior to preserve without importing UI from application.
- `tests/test_ui_tk_iso_table_autocalc.py`: lines 287-520, reason: current visible ISO/ISEER single behavior expectations.
- `tests/test_ui_tk_iso_iseer_2point_controller_switch.py`: lines 1-130, reason: broader selected-suite failure showed undo scenario needed explicit sample input setup.
- `tests/calculator_ui_sample_values.py`: lines 1-45, reason: focused sample input values.
- broad read: `iso_iseer_2point_section.py` full file, reason: extraction target method and helper boundaries are contiguous and under 320 lines.
- repeated read: none

```yaml
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
  report_exemption: none
  read_ledger: included
```

## Known Failures / Risks
- Batch still duplicates ISO/ISEER row calculation until Slice 3.
- Remaining standards still have direct UI calculation orchestration and are follow-up candidates.
- Broader selected-suite validation exposed a stale direct-section undo fixture
  that expected sample values without setting them; the test now injects the
  focused sample explicitly.

## Next Suggested Action
- Arc 12 Slice 3 - ISO/ISEER 2-point Batch Reuse.

## Commit / Push
- commit: completed in slice commit; final hash reported in terminal output
- push: deferred until all Arc 12 slices are complete per user request

## Project Memory Delta
- none
