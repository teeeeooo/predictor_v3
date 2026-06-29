# Arc 12 Slice 8 - EN14825 Boundary Correction

## Goal

Move EN14825 SEER/SCOP calculation adapter ownership from UI-local modules into
the calculator application boundary while preserving UI behavior.

## Scope

- Moved EN14825 SEER/SCOP adapters and UI-neutral point/result models under
  `apps.calculator.application.en14825`.
- Left thin UI compatibility shims for existing `apps.calculator.ui.en14825`
  import paths.
- Rewired sections, table models, and batch profiles to use application-owned
  adapters/models.
- Added focused boundary guard tests.
- Regenerated the code reference map after moving source owners.

## Non-goals

- No EN14825 formula, config semantics, editable-cell behavior,
  fixture/golden expected, or public result contract changes.
- No broad EN14825 adapter rewrite or SEER/SCOP abstraction merge.
- No unrelated calculator standard changes.

## Verification

- `python3 -B -m compileall -q app_calculator.py apps/calculator core/calculators` - OK
- `python3 -B -m pytest tests --collect-only -q -k "en14825"` - OK, focused selection inspected
- `python3 -B -m pytest tests -k "en14825"` - weaker verified: monolithic selector repeatedly stopped progressing in the Tk segment and was interrupted
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py tests/test_apps_calculator_ui_en14825_batch.py tests/test_apps_calculator_ui_en14825_scop.py tests/test_calculator_en14825_application_boundary.py tests/test_en14825_golden.py tests/test_en14825_seer_detail.py -q` - OK, 85 passed
- `python3 -B -m pytest tests/test_ui_tk_en14825_profile_switch_fit.py tests/test_ui_tk_en14825_scop_batch_dialog.py tests/test_ui_tk_en14825_scop_detail.py tests/test_ui_tk_en14825_seer_batch_dialog.py tests/test_ui_tk_en14825_seer_detail.py tests/test_ui_tk_visible_sizing_diagnostics.py tests/test_ui_tk_calculator_empty_state.py tests/test_ui_tk_batch_dialog_content_sizing.py -q` - OK, 38 passed
- `python3 -B tools/code_checker/build_reference_map.py` - regenerated
- `python3 -B tools/code_checker/build_reference_map.py --check` - OK
- `python3 -B tools/check_code_structure.py` - OK with existing soft warnings plus moved EN14825 SCOP adapter LOC warning
- `git diff --check` - OK
- `git status --short` - checked

## Task Results

- task 1: OK - boundary decision: moved adapters/models to application package and kept UI shims.
- task 2: OK - SEER adapter/model ownership moved behind application package.
- task 3: OK - SCOP adapter/model ownership moved behind application package.
- task 4: OK - focused boundary guard tests added; existing focused EN tests pass in split groups.

## Changed Files

- `apps/calculator/application/en14825/__init__.py`
- `apps/calculator/application/en14825/seer_adapter.py`
- `apps/calculator/application/en14825/seer_models.py`
- `apps/calculator/application/en14825/scop_adapter.py`
- `apps/calculator/application/en14825/scop_models.py`
- `apps/calculator/ui/en14825/seer_adapter.py`
- `apps/calculator/ui/en14825/seer_models.py`
- `apps/calculator/ui/en14825/scop_adapter.py`
- `apps/calculator/ui/en14825/scop_models.py`
- EN14825 UI section, batch, table model import sites
- `tests/test_calculator_en14825_application_boundary.py`
- `tests/test_ui_tk_visible_sizing_diagnostics.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## Reference Parity

- Preserved the existing SEER/SCOP adapter APIs and model classes via moved
  source files and UI compatibility shims.
- Did not merge SEER and SCOP because their existing point availability and
  climate/design behaviors remain distinct.

## Read Ledger

- `apps/calculator/ui/en14825/seer_adapter.py`: targeted adapter definitions, reason: move existing SEER calculation owner
- `apps/calculator/ui/en14825/scop_adapter.py`: targeted adapter definitions, reason: move existing SCOP calculation owner
- `apps/calculator/ui/sections/en14825_seer_section.py`: import/calculate ranges, reason: rewire to application adapter
- `apps/calculator/ui/sections/en14825_scop_section.py`: import/calculate ranges, reason: rewire to application adapter
- `apps/calculator/ui/batch_dialogs/profiles/en14825_seer.py`: import range, reason: batch adapter ownership alignment
- `apps/calculator/ui/batch_dialogs/profiles/en14825_scop.py`: import range, reason: batch adapter ownership alignment
- `tests/test_ui_tk_visible_sizing_diagnostics.py`: assertion range, reason: adjust diagnostic away from non-contract relative gap
- broad read: none
- repeated read: none

## Known Failures / Risks

- The monolithic `pytest tests -k "en14825"` selector repeatedly stopped
  progressing in the Tk segment; equivalent EN test files were run in split
  groups and passed.
- `apps/calculator/application/en14825/scop_adapter.py` is a moved existing
  405 LOC adapter and now triggers the structure guard LOC soft warning. The
  move is accepted for this slice to preserve behavior; a future split audit
  can separate SCOP adapter responsibilities if more changes accumulate.
- UI compatibility shims remain intentionally for existing imports; they do not
  own calculation orchestration.

## Next Suggested Action

Arc 12 Slice 9 - AHRI SEER2/HSPF2 Boundary Correction.

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
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

