# Arc 12 Slice 5 - SASO T3 UseCase Extraction

## Goal

Extract SASO T3 calculation orchestration from the Tk section into a UI-neutral
calculator application usecase.

## Scope

- Added `apps.calculator.application.saso_t3`.
- Rewired `IsoSasoT3Section` to call the SASO T3 usecase and render its DTO.
- Added focused SASO T3 usecase/source-guard tests.
- Regenerated the code reference map after adding the application package.

## Non-goals

- No formula, config semantics, profile ID, golden expected, or public result
  dict contract changes.
- No Hong Kong, EN14825, AHRI, or batch implementation extraction in this slice.

## Verification

- `python3 -B -m compileall -q app_calculator.py apps/calculator core/calculators` - OK
- `python3 -B -m pytest tests --collect-only -q -k "saso or t3"` - OK, focused selection inspected
- `python3 -B -m pytest tests -k "saso or t3"` - OK, 48 passed
- `python3 -B tools/code_checker/build_reference_map.py` - regenerated
- `python3 -B tools/code_checker/build_reference_map.py --check` - OK
- `python3 -B tools/check_code_structure.py` - OK with existing unrelated soft warnings
- `git diff --check` - OK
- `git status --short` - checked

## Task Results

- task 1: OK - SASO usecase model added without UI imports.
- task 2: OK - scenario/test-selection orchestration moved behind the application usecase.
- task 3: OK - UI section now reads table values, calls the usecase, and renders status/detail/table output.
- task 4: OK - focused usecase parity and source-guard tests added.

## Changed Files

- `apps/calculator/application/saso_t3/__init__.py`
- `apps/calculator/application/saso_t3/models.py`
- `apps/calculator/application/saso_t3/usecase.py`
- `apps/calculator/ui/sections/iso_saso_t3_section.py`
- `tests/test_calculator_saso_t3_usecase.py`
- `tests/test_ui_tk_iso_saso_t3_controller_switch.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## Reference Parity

- Reused the existing ISO/ISEER application usecase pattern and the app-side
  core dispatcher adapter.
- Kept SASO-specific row/detail/status formatting local to the SASO application
  package instead of introducing a broad calculator abstraction.

## Read Ledger

- `apps/calculator/application/iso_iseer_2point/usecase.py`: lines 1-160, reason: reference application usecase pattern
- `apps/calculator/adapters/core_calculator_dispatcher.py`: lines 1-26, reason: confirm app-side dispatcher adapter
- `apps/calculator/ui/sections/iso_saso_t3_section.py`: targeted method/import ranges, reason: remove UI-owned orchestration
- `apps/calculator/ui/batch_dialogs/profiles/saso_t3.py`: targeted calculation range, reason: confirm batch debt remains out of Slice 5 scope
- `tests/test_calculator_iso_iseer_2point_usecase.py`: lines 1-70, reason: focused usecase test pattern
- broad read: none
- repeated read: `apps/calculator/ui/sections/iso_saso_t3_section.py`, reason: verify patch context and source guard

## Known Failures / Risks

- SASO batch handler still owns row-level dispatcher/config orchestration; this
  is deferred to the later batch/detail consistency slice per the work spec.
- Structure guard reports existing soft warnings in unrelated hotspots; no new
  changed SASO application source warning was introduced.

## Next Suggested Action

Arc 12 Slice 6 - Hong Kong CSPF UseCase Extraction.

## Scope Compliance

No formula/config/profile/golden/public result contract changes were made.

## Commit / Push

- Commit: recorded by the slice commit after this report is staged.
- Push: deferred until all remaining slices are complete per user request.

## Project Memory Delta

- none

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

