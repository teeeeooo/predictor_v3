# 238 Batch Matrix Model / Spec Helpers

## Goal

Implement the first batch two-row matrix slice as a headless model/spec/mapping
foundation. The slice represents one logical case as two physical rows without
changing the existing Hong Kong CSPF row-per-case UI, handler, controller,
viewport, calculator core, or tests.

## Scope

- Added a pure Python matrix model/spec helper under `ui_tk/`.
- Added focused headless tests for Hong Kong CSPF matrix mapping.
- Updated `docs/WORK_PLAN.md` to move the next action to per-cell
  surface/controller compatibility.
- Added a compact `project_log.md` durable invariant for no-merge / blank
  read-only physical cells.

## Created Model / Spec / Helper

Created `ui_tk/batch_matrix_models.py`.

Key concepts:

- `MatrixPhysicalRowType`: `CAPACITY`, `POWER`.
- `MatrixCellKind`: `CASE`, `ROW_TYPE`, `INPUT`, `RESULT`,
  `BLANK_READ_ONLY`, `NOT_APPLICABLE`.
- `MatrixMeasurementPointSpec`: profile-defined measurement point with
  row-type-to-input-key mapping.
- `MatrixCellDescriptor`: resolved physical cell metadata, including logical
  case index, physical row type, input key, result key, editability, read-only
  state, blank read-only state, and not-applicable state.
- `BatchMatrixSpec`: headless profile matrix spec with helpers for physical row
  count, logical-case lookup, row-type lookup, cell resolution, editable target
  filtering, display text, and logical-case snapshot/restore.

Boundary:

- no Tk imports;
- no widgets;
- no keyboard/mouse/clipboard controller logic;
- no calculator core calls;
- no migration of existing `BatchCaseTable`.

## Hong Kong CSPF Mapping Contract

Created `HONG_KONG_CSPF_MATRIX_SPEC` as the first profile mapping fixture.

Columns:

- fixed display: `Case`, `Row Type`;
- measurement points: `Declared`, `35 Full`, `35 Half`;
- result metrics: `CSPF`, `CSEC`.

Physical rows:

- first row: `Capacity`;
- second row: `Power`.

Input mapping:

- `Declared` / `Capacity` -> `declared_capacity`;
- `Declared` / `Power` -> not applicable;
- `35 Full` / `Capacity` -> `full_capacity`;
- `35 Full` / `Power` -> `full_power`;
- `35 Half` / `Capacity` -> `half_capacity`;
- `35 Half` / `Power` -> `half_power`.

Result mapping:

- `CSPF` and `CSEC` display only on the first physical row of each logical
  case.
- second-row result metric cells are real blank read-only cells.

The matrix spec input/result keys are tested against the existing Hong Kong
CSPF batch profile contract so the future migration uses the same handler input
and output keys.

## Blank Read-only Cell Decision

Implemented the user-specified no-merge invariant:

- no merged cells;
- no fake-merged cells;
- no rowspan / overlay / widget spanning behavior;
- every visible grid position resolves to a real physical cell descriptor;
- Case value appears only on the first physical row;
- second-row Case cell is a real blank read-only cell;
- result metric values appear only on the first physical row;
- second-row result metric cells are real blank read-only cells;
- blank cells can still be part of rectangular selection/copy later;
- paste/write target candidates are filtered to editable input cells only.

Declared/Power is represented as a not-applicable cell because there is no
meaningful power-row input for declared capacity.

## MVC / SoC Boundary

Model/spec helper owns:

- logical case to physical row mapping;
- physical row type resolution;
- measurement point to input key mapping;
- result metric cell mapping;
- per-cell descriptor resolution;
- logical-case snapshot/restore helpers.

It does not own:

- Tk view rendering;
- controller compatibility;
- paste/copy behavior;
- add/remove UI commands;
- calculation adapter calls;
- Hong Kong CSPF migration.

Existing row-per-case owners remain unchanged:

- `BatchProfileSpec` / `BatchTableModel`;
- `BatchCaseTable`;
- `BatchTableController`;
- `BatchTableViewport`;
- Hong Kong CSPF batch spec/section/handler.

## Tests

Added `tests/test_ui_tk_batch_matrix_models.py`.

Covered:

- one logical case creates two physical rows;
- physical rows map to logical case index and `CAPACITY` / `POWER` row types;
- Case second row is blank read-only and not repeated;
- row type labels display on both physical rows;
- Hong Kong CSPF `Declared`, `35 Full`, and `35 Half` input key mapping;
- result metrics display only on first physical row;
- second-row result cells are blank read-only;
- editable target filtering returns editable input cells only;
- not-applicable cells are not editable;
- display text reads case and result data;
- logical snapshot/restore is logical-case based, not physical-row based;
- Hong Kong matrix input/result keys match the existing batch profile contract.

## Excluded Scope

- No changes to `ui_tk/batch_case_table.py`.
- No changes to `ui_tk/batch_table_controller.py`.
- No changes to `ui_tk/batch_table_viewport.py`.
- No Hong Kong CSPF batch section/spec/handler changes.
- No Tk UI skeleton or table rendering.
- No controller compatibility changes.
- No Hong Kong CSPF matrix migration.
- No copy-all / CSV export / xlsx export.
- No calculator core, region config, profile registry, golden fixture, or
  expected-result changes.

## Validation

- `python -m pytest tests/test_ui_tk_batch_matrix_models.py`: PASS, 9 passed.
- `python -m pytest tests/test_ui_tk_hong_kong_cspf_batch_spec.py tests/test_ui_tk_batch_table_controller.py`:
  PASS, 18 passed.
- `python3 -B tools/check_code_structure.py`: PASS with existing warning only:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `python3 -m py_compile ui_tk/batch_matrix_models.py tests/test_ui_tk_batch_matrix_models.py`:
  PASS.
- `git diff --check`: PASS.
- `git status --short`: expected source/test/doc/report changes before commit.

Not run:

- full pytest;
- GUI smoke;
- calculator smoke.

## Next Suggested Action

Per-cell role surface/controller compatibility:

- adapt or extend the common table surface contract so selection/copy/paste/
  clear can use per-cell editability, read-only result cells, blank read-only
  cells, and not-applicable cells;
- keep existing row-per-case controller behavior stable;
- verify with fake-surface/controller tests before any Tk matrix skeleton.

## Project Memory Delta

- type: decision
  topic: batch matrix blank physical cell invariant
  content: The two-row batch matrix foundation uses physical rectangular grid
    cells only. It forbids merged/fake-merged cells; Case and result values
    display only on the first physical row, while corresponding second-row
    cells are real blank read-only cells. Mutation targets are editable input
    cells only.
  keywords:
    - batch matrix
    - blank read-only
    - no merge
    - physical grid
    - Hong Kong CSPF
  assertionStatus: verified

## Commit / Push

- Commit: final pushed hash recorded in final response to avoid report
  self-reference hash loops.
- Push: final response.
