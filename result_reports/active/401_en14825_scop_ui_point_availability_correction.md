# 401 EN14825 SCOP UI point availability correction

## Goal

Make SCOP UI required/editable point behavior follow the unified
`scop.point_contract` resolver instead of treating every A/B/C/D/TOL/Tbiv point
as an independent input.

## Scope

- Added `ScopAdapter.resolve_point_availability(...)` to translate core resolver
  output into UI-ready point metadata.
- Changed SCOP adapter completeness checks and core input construction to use
  required independent points only.
- Updated `ScopTableModel` to consume point availability metadata without
  reading core/config directly.
- Updated `En14825ScopSection` to resolve/apply availability before parsing table
  text, blank unavailable cells, and expose unavailable cells as readonly.
- Added focused SCOP UI/adapter/model tests for Warmer inactive/mapped/threshold
  behavior and Average required behavior.
- Updated WORK_PLAN and regenerated code map.

## Non-goals

- Did not edit core calculator or region config.
- Did not edit SEER UI, batch, ML, profiles, memory, summaries, archive, or
  project log.
- Did not run GUI/manual smoke.
- Did not change golden expected values.

## Availability Source

- UI availability comes from `ScopAdapter.resolve_point_availability(...)`.
- The adapter calls the existing core/config point contract resolver and exposes:
  - `required_independent_points`
  - `mapped_points`
  - `inactive_points`
  - `resolved_temperatures`
  - per-point state: `required`, `mapped`, `inactive`, or `threshold_only`
- Table model receives this metadata from section/adapter and does not import or
  read core/config directly.

## Adapter Behavior

- Declared/tested completeness now checks only required independent points.
- Core declared/tested point dictionaries include only required independent
  points.
- Mapped, inactive, and threshold-only points are not filled with dummy values.
- Warmer `A`, `TOL`, and `Tbiv` are not required for the default
  `Tbiv=2°C`, `TOL=-11°C` contract case.
- Average keeps A required and keeps `TOL=-11°C` required.

## Table Behavior

- Non-required SCOP input cells are blank and readonly/unavailable.
- Warmer A input rows are blank readonly.
- Warmer `Tbiv=2°C` input rows are blank readonly because Tbiv maps to B.
- Warmer low TOL input rows are blank readonly because TOL is threshold-only.
- Required cells return to editable when the active climate/temperature contract
  requires them.

## Tests

- Added adapter availability tests for Warmer and Average.
- Added adapter calculation test for Warmer without A/TOL/Tbiv inputs.
- Added table model blank/readonly tests for unavailable points.
- Added section wiring test for Warmer table readonly roles and Average required
  cells.

## code_map_check

- Targeted pre-edit code_map check covered ScopAdapter, ScopTableModel,
  En14825ScopSection, and point-contract resolver references.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md`; changes are metadata
  and LOC/function-length evidence for the touched SCOP UI/adapter files.

## Verification

- `python3 -B -m py_compile apps/calculator/ui/en14825/scop_adapter.py apps/calculator/ui/en14825/scop_table_model.py apps/calculator/ui/sections/en14825_scop_section.py`
  OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py` OK:
  29 passed.
- `python3 -B -m pytest tests/test_en14825_golden.py` OK: 16 passed.
- `python3 -B tools/check_code_structure.py` OK with existing EN14825 SEER/SCOP
  section LOC soft warnings.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Project Memory Delta

- SCOP UI point editability now follows the core/config point contract via
  adapter-resolved availability metadata.
- Warmer inactive/mapped/threshold-only points are no longer independent UI
  inputs.

## Next Action

EN14825 SCOP UI point availability manual smoke.
