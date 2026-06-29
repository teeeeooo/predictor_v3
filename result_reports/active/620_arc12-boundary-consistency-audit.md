# Arc 12 Slice 10 - Batch / Detail / Adapter Consistency Audit

## Goal

Audit Arc 12 calculator application boundary consistency after Slices 2-9 and
apply small wiring/source-guard corrections where appropriate.

## Scope

- Routed SASO T3, Hong Kong CSPF, and Hong Kong HSPF batch row calculations
  through application usecases/evaluators.
- Added guard coverage for completed Arc 12 UI surfaces and application
  packages.
- Verified application packages do not import UI runtimes/packages.
- Regenerated the code reference map after source structure changes.

## Non-goals

- No new large usecase extraction.
- No formula, config semantics, profile ID, fixture/golden expected, or public
  result contract changes.
- No report lifecycle cleanup.

## Verification

- `python3 -B -m compileall -q app_calculator.py apps/calculator core/calculators` - OK
- `python3 -B -m pytest tests --collect-only -q -k "calculator_application or usecase or iso_iseer or saso or hong_kong or en14825 or ahri"` - inspected, broad selection
- `python3 -B -m pytest tests -k "calculator_application or usecase"` - OK, 27 passed
- `python3 -B -m pytest tests -k "iso_iseer or saso or hong_kong"` - OK, 172 passed
- `python3 -B -m pytest tests -k "en14825 or ahri"` - weaker verified: combined selector stopped progressing in the EN Tk segment and was interrupted
- EN split group 1 - OK, 85 passed
- EN split group 2 - OK, 38 passed
- AHRI focused selector from Slice 9 - OK, 89 passed; no AHRI code changed in Slice 10
- `python3 -B tools/code_checker/build_reference_map.py` - regenerated
- `python3 -B tools/code_checker/build_reference_map.py --check` - OK
- `python3 -B tools/check_code_structure.py` - OK with known soft warnings
- `git diff --check` - OK
- `git status --short` - checked

## Task Results

- task 1: OK - import/source guard audit completed and automated guard added.
- task 2: OK - batch/detail consistency improved for SASO and Hong Kong batch paths.
- task 3: OK - adapter consistency confirmed for EN14825 and AHRI application packages/shims.
- task 4: OK - guard tests added/adjusted.

## Changed Files

- `apps/calculator/application/saso_t3/__init__.py`
- `apps/calculator/application/saso_t3/models.py`
- `apps/calculator/application/saso_t3/usecase.py`
- `apps/calculator/ui/batch_dialogs/profiles/saso_t3.py`
- `apps/calculator/ui/batch_dialogs/profiles/hong_kong_hspf.py`
- `apps/calculator/ui/sections/hong_kong_cspf_batch_spec.py`
- `tests/test_calculator_application_boundary.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## Reference Parity

- Reused existing application usecases and moved adapter owners from prior
  slices.
- Kept SASO batch-specific optional blank behavior in an application evaluator
  instead of changing the single-section behavior.

## Read Ledger

- `apps/calculator/ui/batch_dialogs/profiles/saso_t3.py`: row calculation range, reason: remove UI-owned core orchestration
- `apps/calculator/ui/sections/hong_kong_cspf_batch_spec.py`: row calculation range, reason: route batch through CSPF usecase
- `apps/calculator/ui/batch_dialogs/profiles/hong_kong_hspf.py`: row calculation range, reason: route batch through HSPF usecase
- `apps/calculator/application/saso_t3/usecase.py`: calculation helper range, reason: add batch evaluator at application boundary
- `tests/test_calculator_application_boundary.py`: boundary guard range, reason: automate audit result
- broad read: none
- repeated read: none

## Known Failures / Risks

- The combined `pytest tests -k "en14825 or ahri"` selector repeatedly stopped
  progressing in the EN Tk segment. EN was verified in split groups and AHRI
  had already passed its focused selector after Slice 9.
- Existing structure warnings remain for known core/EN hotspots; no new changed
  Slice 10 file warning was introduced.

## Next Suggested Action

Arc 12 Slice 11 - Final Closeout.

## Scope Compliance

No formula/config/profile/golden/public result contract changes were made.

## Commit / Push

- Commit: recorded by the slice commit after this report is staged.
- Push: deferred until all remaining slices are complete per user request.

## Project Memory Delta

- none

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

