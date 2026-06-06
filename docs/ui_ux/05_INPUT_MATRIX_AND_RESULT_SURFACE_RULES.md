# 05. Input Matrix and Result Surface Rules

## Purpose

This document is the portable owner for shaping repeated structured input and
user-facing result output into coherent surfaces.

Repeated measurements, comparisons, or conditions are not rendered as
scattered label-entry forms. They are normalized into matrix tables with
visible row and column headers. Results are not presented as raw text dumps;
they are presented as summary result surfaces.

## Scope

- Applies across single-case calculation screens, prediction workflows,
  training/model-operation workflows, batch workflows, and future structured
  input/result surfaces.
- Governs input/result **surface shape** and the decision to use a matrix or
  summary card/table.
- Does not prescribe metric navigation (e.g., sub-tabs or segmented controls),
  interface widget APIs, visual token values, domain schemas, model schemas,
  or result computation.

## Relationship to Existing UI/UX SSOT

- `00_UI_UX_SYSTEM.md` owns common UI/UX principles and terminology.
- `02_DESIGN_TOKENS_AND_LAYOUT.md` owns token/layout naming and density.
- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` owns interaction behavior after a
  surface is table-shaped: edit, selection, copy/paste, clear, undo,
  navigation, and validation behavior.
- `04_VISUAL_DESIGN_ARCHITECTURE.md` owns neutral-first, semantic-color,
  table-first, and result/status visual philosophy.
- This document owns how repeated input/result data is shaped into matrix and
  summary surfaces before interface-framework implementation begins.
- Adapter documents own framework-specific implementation once this surface shape has
  been selected.
- Existing-screen replacements must first map the current section order,
  default visible state, and primary user flow. A different flow is a design
  change, not an adapter detail.

## Input Matrix Surface Rule

- Repeated measurement values, condition values, and comparison values must
  not be dispersed as unrelated label-entry controls.
- When a surface has at least two condition/stage/sample/case instances and at
  least two repeated measured variables, a matrix table is the default input
  representation.
- The table must show both row and column headers so users can scan and
  compare values without reconstructing relationships from nearby labels.
- A logical matrix must be shown as one structured surface. Splitting it into
  multiple mini-grids or scattered forms is a failed shape unless distinct
  data ownership genuinely makes one matrix misleading.
- Matrix schema belongs in the UI layer. The core calculator, ML core, profile
  resolver, and dispatcher must not depend on UI matrix row/column schema.

## Matrix Inference Rule

The UI derives a matrix candidate whenever the same field family repeats
across comparable items.

- Repeated condition/stage/sample/case labels are one axis candidate:
  - `정격`, `35 Full`, `35 Half`
  - `정격 난방`, `7 Full`, `7 Half`
  - `Baseline`, `Candidate`
  - `Train`, `Validation`, `Test`
  - `Case 1`, `Case 2`, `Case 3`
- Repeated measured-variable labels are the other axis candidate:
  - `능력 [W]`, `전력 [W]`
  - `Predicted`, `Actual`, `Error`
  - `Min`, `Max`
  - `Input`, `Output`
- The thing users naturally compare across should form an explicit axis.
- Prefer the higher-comparison axis as columns when it keeps comparison
  compact and readable.
- Orientation may change for screen width, row count, or entry-flow reasons.
  A deliberate departure from the preferred orientation must be recorded in
  the design record or result report.

## Axis Selection Heuristics

1. Identify repeated domain instances: points, cases, candidates, datasets,
   scenarios, or stages.
2. Identify repeated variables: measurements, metrics, limits, predicted
   values, observed values, or differences.
3. Choose axes that let a user answer the principal comparison question with
   one horizontal or vertical scan.
4. Put units in headers, not repeated inside cell values.
5. Use user-facing labels rather than schema keys or internal IDs.
6. Keep a small 2-by-2, 2-by-3, or 3-by-3 matrix intact rather than replacing
   it with form layout merely because each individual cell is simple.

## Singleton and Reference Values

- A singleton reference or rated value should be folded into the same matrix
  as a reference row or reference column whenever its relationship to the
  repeated values remains accurate.
- A singleton may be shown as a separate compact field only when folding it
  into the matrix would distort meaning, validation, unit, or interaction.
- A separated singleton must remain visually associated with its matrix and
  must not cause the repeated values themselves to fragment into mini-forms.

## Static / Disabled / Not-applicable Cells

- A cell that is logically present but not applicable may appear inside the
  matrix as disabled, static, or blank content.
- Such cells must be visibly distinct from editable and calculated cells.
- A not-applicable cell is not a reason to split one logical matrix into
  multiple mini-grids.
- Whether a static cell participates in copy/export is owned by the table
  behavior contract and the relevant interface adapter.

## Result Summary Surface Rule

- Primary user-visible results are summary surfaces, not raw text dumps,
  serialized dictionaries, diagnostic streams, or uncontrolled float output.
- A summary surface is either a compact metric/value table or a small result
  card set with a visible primary metric, key supporting values, units, and
  concise status.
- Numeric result display follows the common numeric display policy: meaningful
  precision, consistent units, and no raw long-float noise.
- Missing optional result values display a user-facing absence marker such as
  `-` or `N/A`; the literal string `None` is not a valid user-visible result.
- A validation error or calculation error appears as concise status near the
  summary surface; raw tracebacks are never user-visible.
- Copy/export may include a compact textual rendering of the summary, but a
  text representation is not the default visual surface.
- Single-case calculation screens may update the summary immediately as input
  changes. Batch, prediction, training, or other model-operation surfaces may
  use explicit run actions because they represent larger jobs or multiple
  cases.

## Detail and Graph Surface Rule

- Graphs, bin-level details, traces, and diagnostics supplement the summary
  surface; they do not replace it.
- A default workflow first presents inputs and summary result values. Detail
  or graph surfaces appear only when needed for review or diagnosis.
- Existing graph/detail implementations may be retained as reference UX. This
  document does not require porting any implementation verbatim across
  interface frameworks.
- A new lightweight graph/detail surface should be designed with explicit
  acceptance criteria before adding large dependencies.
- Batch calculation results are result tables, not internal formula trace.
  They should use one row per case with user-facing input/output columns.
- Table interaction and validation policy are separate. `03_SPREADSHEET_TABLE_UX_CONTRACT.md`
  owns interaction behavior; this document owns row/cell validation policy
  expected by each surface type.
- The table parity checklist is intentionally not repeated here. If a
  surface is table-shaped, use `03_SPREADSHEET_TABLE_UX_CONTRACT.md` for
  interaction pass/fail validation and this document for validation/error
  policy.
- Auto-calculation batch surfaces may keep blank, partial, or invalid rows
  result-blank while calculating valid rows independently. This avoids repeated
  error text while the user is still typing.
- Calculation batch surfaces may use a compact dialog-level summary when it
  helps review, but should not turn incomplete input into noisy per-cell
  errors.
- Prediction/training batch surfaces must not fail silently. Invalid rows/cells
  need pre-run validation summary, visible cell/row status, or both before
  model execution proceeds.
- Detail/bin schemas should be designed as domain-variant-neutral foundations
  where practical so adapters can share column meaning instead of creating
  incompatible per-variant trace shapes.

## Stateful Input Surface Lifecycle

- Closing a stateful input dialog, window, or surface is not an implicit
  reset or clear action.
- Widget, shell, or Toplevel lifecycle must be separated from user input state
  lifecycle.
- If a stateful input dialog uses destroy-on-close, a parent section,
  controller, or explicit state owner must keep a session-local snapshot and
  restore it on reopen.
- Reset/Clear must be an explicit user action. Close/reopen must not erase
  user-entered rows, values, or comparable structured input as a side effect.
- The dialog shell owns show/close lifecycle. The table or input surface owns
  snapshot/restore behavior. The parent/controller-level state owner decides
  the session-local state lifetime.
- This applies to batch tables, repeated input matrices, structured input
  dialogs, and future profile-specific input surfaces.
- Persistence after app restart is a separate product decision and is not the
  default requirement of this lifecycle rule.

## Acceptance Criteria

- Repeated 2-by-2, 2-by-3, and 3-by-3 input shapes are rendered as matrix
  tables by default.
- Both row headers and column headers are visible.
- Cells occupy one bordered or otherwise clearly structured surface.
- A card containing scattered `label + entry` form controls that merely
  imitate a table fails this rule.
- A bordered `Entry`/`Label` grid is not enough by itself; if the selected
  surface is table-shaped, it must also satisfy the table interaction
  contract and relevant interface adapter.
- Header, row label, editable cell, and static/not-applicable cell meanings
  are visually distinguishable.
- Results are shown as a metric/value table or compact summary card surface.
- User-visible result surfaces must not expose `None`, a raw dictionary, raw
  long floats, or a traceback.
- A graph/detail surface must not displace the default summary result.
- Closing and reopening a stateful input dialog does not reset rows or values
  unless the user has invoked an explicit reset/clear action.

## Anti-patterns

- Repeating `Label`/`Entry` pairs for comparable points when a matrix is
  inferable.
- Rendering rated/reference values in a separate mini-grid solely because one
  intersecting cell is not applicable.
- Presenting a large read-only raw text box as the primary result UI.
- Encoding UI matrix orientation into domain core, model-operation core,
  variant resolver, or dispatcher contracts.
- Copying an inspiration-source or historical layout pixel-for-pixel instead
  of implementing the active portable rule.
- Treating a shell close/destroy as permission to discard user-entered
  structured input state.

## Interface Framework Adaptation Notes

- Eligible table surfaces implement the active table UX contract through the
  selected interface-framework adapter.
- Concrete widgets may differ by framework; the input/result meaning and
  comparison affordance remain the same.
- Visual styling must follow `04_VISUAL_DESIGN_ARCHITECTURE.md`; this
  document does not fix token values or mandate a widget class.

## Examples

Example names are evidence, not scope boundaries.

### ISO CSPF / HSPF

- CSPF condition axis: `정격`, `35 Full`, `35 Half`.
- HSPF condition axis: `정격 난방`, `7 Full`, `7 Half`.
- Measured-variable axis: `능력 [W]`, `전력 [W]`.
- Rated/reference power is not applicable and stays in the same matrix as a
  static `-` cell.

### Predictor

- A comparison surface may use columns `Predicted`, `Actual`, `Error`, or
  `Baseline`, `Candidate`.
- Rows may be target metrics, products, or operating points; repeated
  comparisons are not shown as individual result labels.

### Trainer

- Dataset axis: `Train`, `Validation`, `Test`.
- Metric axis: `Loss`, `Score`, `Count`, or another relevant training metric.
- The trainer chooses orientation for scanability while keeping all
  comparable values within one matrix.

### Result Summary

| Metric | Supporting values |
| --- | --- |
| `CSPF` | `CSTL [kWh]`, `CSEC [kWh]` |
| `HSPF` | `HSTL [kWh]`, `HSEC [kWh]` |

The primary metric and key supporting values appear as a compact table/card
surface. Diagnostics and graphs remain secondary detail surfaces.

## Portable Adoption Order

1. Apply this rule before designing any new repeated-input or repeated-result
   surface.
2. Choose the matrix/result surface shape before selecting a concrete widget
   implementation.
3. Verify one representative surface in the selected interface framework.
4. Refine spacing or semantic styling only if manual smoke exposes a need.
5. Design graph/detail surfaces only if summary-plus-input workflow requires
   additional review capability.

Current-codebase examples such as named standards, current GUI implementations,
packaging measurements, or source retirement decisions belong in the adopting
project's work plan or result reports.
