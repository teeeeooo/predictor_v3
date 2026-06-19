# 409 EN14825 SCOP batch headless foundation

## Goal

Add the adapter-backed SCOP batch matrix specification and tested-only row
handler without wiring a dialog or changing calculation ownership.

## Scope

- Added a dynamic SCOP `BatchMatrixSpec` builder driven by
  `ScopAdapter.resolve_point_availability()`.
- Added a tested-only row handler with case-local `Pdesignh` and common
  climate/Tbiv/TOL/auxiliary inputs.
- Added focused spec, mapping, real-adapter, formatting, and row-state tests.
- Updated WORK_PLAN and regenerated the code reference map.

## Non-goals

- No dialog, section action, snapshot, export, or common-input UI wiring.
- No dynamic matrix rebuild/preservation policy decision.
- No core, config, adapter availability, calculation, or golden changes.

## Task Results

- The builder creates only `required_independent_points`; mapped, inactive,
  and threshold-only points do not receive input columns.
- `Pdesignh` is editable only on the Capacity physical row and remains a
  per-case input.
- Each required point maps Capacity/Power rows to tested capacity/power.
- Results expose only `scop` and `qh_kwh`.
- Blank and partial rows are PENDING; invalid text and adapter failures are
  ERROR.

## Reference Parity

- Reused the established SEER headless module shape, shared
  `BatchMatrixSpec`, row-state contract, numeric parser, and adapter boundary.
- SCOP remains a separate feature module because its matrix columns are
  adapter-resolved and climate/Tbiv/TOL dependent.
- Dialog parity remains deferred until the SCOP rebuild/snapshot policy is
  explicitly decided.

## Verification

- `python3 -B -m py_compile apps/calculator/ui/en14825/scop_batch.py tests/test_apps_calculator_ui_en14825_batch.py`: OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_batch.py -q`: OK, 13 passed.
- `python3 -B tools/check_code_structure.py`: OK with three warnings; two are
  existing section LOC soft warnings and one pre-regeneration map freshness
  warning.
- `python3 -B tools/code_checker/build_reference_map.py`: OK; map changed for
  the new module, symbol inventory, and import edge.
- `git diff --check`: OK.

## Changed Files

- `apps/calculator/ui/en14825/scop_batch.py`
- `tests/test_apps_calculator_ui_en14825_batch.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/409_en14825_scop_batch_headless_foundation.md`

## Known Failures / Risks

- SCOP dialog wiring is still blocked on the dynamic matrix rebuild and
  snapshot preservation policy recorded in preflight 406.
- No GUI/manual smoke was run because this slice is headless only.

## Scope Compliance

- No core, data, config, section, dialog, batch shell, ML, or golden file was
  modified.
- The new module delegates availability and calculations to `ScopAdapter`.

## Code Map

- `code_map_check`: regenerated.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` is included in the diff.

## Commit / Push

- Final validation passed; implementation and report are committed and pushed
  together.

## Project Memory Delta

- none.

## Next Suggested Action

EN14825 SEER batch dialog wiring.
