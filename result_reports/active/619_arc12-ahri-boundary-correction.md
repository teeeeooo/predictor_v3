# Arc 12 Slice 9 - AHRI Boundary Correction

## Goal

Move AHRI SEER2/HSPF2 calculation adapter ownership from UI-local modules into
the calculator application boundary while preserving optional point behavior and
result/detail contracts.

## Scope

- Moved AHRI SEER2/HSPF2 adapters under `apps.calculator.application.ahri`.
- Replaced UI table parser dependency with application-local numeric parsing.
- Left thin UI compatibility shims for existing `apps.calculator.ui.ahri`
  adapter import paths.
- Rewired AHRI sections and batch handlers to import application adapters.
- Added focused boundary guard tests.
- Regenerated the code reference map after moving source owners.

## Non-goals

- No AHRI formula, profile ID, optional point semantics, fixture/golden
  expected, public result contract, or core envelope shape changes.
- No broad AHRI abstraction beyond the existing SEER2/HSPF2 adapters.
- No unrelated calculator standard changes.

## Verification

- `python3 -B -m compileall -q app_calculator.py apps/calculator core/calculators` - OK
- `python3 -B -m pytest tests --collect-only -q -k "ahri or seer2 or hspf2"` - OK, focused selection inspected
- `python3 -B -m pytest tests -k "ahri or seer2 or hspf2"` - OK, 89 passed
- `python3 -B tools/code_checker/build_reference_map.py` - regenerated
- `python3 -B tools/code_checker/build_reference_map.py --check` - OK
- `python3 -B tools/check_code_structure.py` - OK with existing unrelated soft warnings
- `git diff --check` - OK
- `git status --short` - checked

## Task Results

- task 1: OK - boundary decision: moved existing adapters to application package and did not introduce a new envelope shape.
- task 2: OK - SEER2 adapter ownership moved behind application package.
- task 3: OK - HSPF2 adapter ownership moved behind application package while preserving optional point handling.
- task 4: OK - focused boundary guard tests added; existing AHRI focused tests pass.

## Changed Files

- `apps/calculator/application/ahri/__init__.py`
- `apps/calculator/application/ahri/seer2_adapter.py`
- `apps/calculator/application/ahri/hspf2_adapter.py`
- `apps/calculator/ui/ahri/seer2_adapter.py`
- `apps/calculator/ui/ahri/hspf2_adapter.py`
- AHRI UI section and batch import sites
- `tests/test_calculator_ahri_application_boundary.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## Reference Parity

- Preserved the existing AHRI SEER2/HSPF2 adapter APIs through moved source
  files and UI compatibility shims.
- Existing core input/result envelope helpers were not modified and no
  duplicate envelope vocabulary was introduced.

## Read Ledger

- `apps/calculator/ui/ahri/seer2_adapter.py`: targeted adapter definitions, reason: move existing SEER2 calculation owner
- `apps/calculator/ui/ahri/hspf2_adapter.py`: targeted adapter definitions, reason: move existing HSPF2 calculation owner
- `core/calculators/adapters/input_adapter.py`: symbol/range scan, reason: confirm existing envelope helper shape is not duplicated
- `core/calculators/adapters/result_adapter.py`: symbol/range scan, reason: confirm existing envelope helper shape is not duplicated
- `apps/calculator/ui/sections/ahri_seer2_section.py`: import/calculate ranges, reason: rewire to application adapter
- `apps/calculator/ui/sections/ahri_hspf2_section.py`: import/calculate ranges, reason: rewire to application adapter
- `apps/calculator/ui/ahri/seer2_batch.py`: import range, reason: batch adapter ownership alignment
- `apps/calculator/ui/ahri/hspf2_batch.py`: import range, reason: batch adapter ownership alignment
- broad read: none
- repeated read: none

## Known Failures / Risks

- UI compatibility shims remain intentionally for existing imports; they do not
  own calculation orchestration.
- Structure guard reports existing unrelated soft warnings; no changed AHRI
  application source warning was introduced.

## Next Suggested Action

Arc 12 Slice 10 - Batch / Detail / Adapter Consistency Audit.

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

