# Arc 12 Slice 6 - Hong Kong CSPF UseCase Extraction

## Goal

Extract Hong Kong CSPF single-section calculation orchestration into a
UI-neutral calculator application usecase.

## Scope

- Added `apps.calculator.application.hong_kong_cspf`.
- Rewired `HongKongCspfSection` to call the application usecase and render the
  returned status, summary, and detail DTO.
- Added focused HK CSPF usecase and source-guard tests.
- Regenerated the code reference map after adding the application package.

## Non-goals

- No formula, config semantics, profile ID, fixture/golden expected, or public
  result dict contract changes.
- No HK HSPF, SASO, EN14825, AHRI, or batch extraction in this slice.

## Verification

- `python3 -B -m compileall -q app_calculator.py apps/calculator core/calculators` - OK
- `python3 -B -m pytest tests --collect-only -q -k "hong_kong_cspf or hk_cspf or cspf"` - inspected, too broad
- `python3 -B -m pytest tests --collect-only -q -k "hong_kong_cspf or hk_cspf"` - OK, focused selection inspected
- `python3 -B -m pytest tests -k "hong_kong_cspf or hk_cspf"` - OK, 41 passed
- `python3 -B tools/code_checker/build_reference_map.py` - regenerated
- `python3 -B tools/code_checker/build_reference_map.py --check` - OK
- `python3 -B tools/check_code_structure.py` - OK with existing unrelated soft warnings
- `git diff --check` - OK
- `git status --short` - checked

## Task Results

- task 1: OK - HK CSPF usecase model added without UI imports.
- task 2: OK - parsing, profile resolution, core call, summary, and detail assembly moved to the usecase.
- task 3: OK - UI section now reads table values and renders returned DTOs.
- task 4: OK - focused usecase parity and source-guard tests added.

## Changed Files

- `apps/calculator/application/hong_kong_cspf/__init__.py`
- `apps/calculator/application/hong_kong_cspf/models.py`
- `apps/calculator/application/hong_kong_cspf/usecase.py`
- `apps/calculator/ui/sections/hong_kong_cspf_section.py`
- `tests/test_calculator_hong_kong_cspf_usecase.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## Reference Parity

- Reused the existing app-side dispatcher adapter and application profile
  resolver.
- Kept the usecase profile-specific rather than introducing a broad CSPF
  abstraction across all regions.

## Read Ledger

- `apps/calculator/ui/sections/hong_kong_cspf_section.py`: lines 1-280, reason: target section orchestration extraction
- `apps/calculator/application/profile_resolver.py`: lines 1-90, reason: confirm application-owned HK profile resolution
- `apps/calculator/ui/result_models.py`: lines 1-35, reason: confirm UI rendering model boundary
- `apps/calculator/ui/sections/result_formatting.py`: lines 1-75, reason: preserve summary formatting parity
- `tests/test_ui_tk_hong_kong_cspf_controller_switch.py`: lines 1-90, reason: focused UI smoke expectations
- broad read: none
- repeated read: none

## Known Failures / Risks

- HK CSPF batch handler still owns row-level core orchestration and remains a
  Slice 10 consistency-audit target.
- Structure guard reports existing unrelated soft warnings; no changed HK CSPF
  application source warning was introduced.

## Next Suggested Action

Arc 12 Slice 7 - Hong Kong HSPF UseCase Extraction.

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

