# Predict Input Workflow Overhaul — Product Direction and Mock Baseline

Status: active product exploration; final layout and implementation boundary open
Created: 2026-07-14
Updated: 2026-07-31
Prerequisite: Train/Admin Phases 1–5 and Predict Findings #1–#7 complete

## 1. Purpose

Preserve the confirmed product direction and the evaluation baseline for the
**Predict input workflow broad overhaul** before disposable mock comparison or
production source implementation begins.

This record is not a final UI design. It deliberately separates:

- **confirmed product direction**, which every layout candidate must preserve;
- **open design decisions**, which require comparable mock evidence and a user
  decision; and
- **implementation gates**, which remain closed until the evidence and decision
  exist.

No source, schema, public API, model, mapping data, or runtime behavior changes
are authorized by this record.

## 2. Preserved Contracts

The exploration preserves:

- one logical prediction case per row and stable `case_id` result association;
- one canonical case/result ownership for each Predict session;
- standalone and embedded Predict using the shared workspace behavior;
- active-generation-driven Predict presentation;
- existing mapping dropdown, cascade, and autofill semantics;
- existing prediction execution, cancellation, partial-result, and row-isolation
  behavior;
- existing runtime generation, preprocessing, inference, result mapping, model
  lifecycle, reload, Active observation, and no-hot-swap contracts;
- Data Definition, Data Mapping, Train, Predict, and Calculator owner directions;
- read-only result/status ownership; and
- no production model or data mutation authority.

A later split presentation may change visible arrangement, but it must not split
logical case ownership or introduce a hidden joined copy.

## 3. Confirmed Product Direction

### 3.1 Input Methods and Paste Scope

- Expected usage is approximately 70% Excel paste and 30% on-screen dropdown
  authoring.
- Both paths are first-class workflows. Paste is not an import afterthought, and
  dropdown authoring is not a fallback-only path.
- The first-overhaul paste contract is headerless **value-only TSV**.
- Values are interpreted in the defined order of the active Predict input
  columns.
- Header recognition, arbitrary column matching, and an import wizard are outside
  the first scope.
- When pasted rows exceed the current row count, Predict creates every required
  row. It must not silently discard overflow rows.

### 3.2 Bulk Paste Transaction

Paste involving tens or hundreds of rows is one bulk transaction, not a series
of independent cell-edit callbacks. The required order is:

1. parse the complete TSV payload;
2. create all required rows as one bounded operation;
3. stage raw input values per row;
4. construct each row's final input combination;
5. reuse the loaded mapping data;
6. run each row's cascade and autofill against that final combination;
7. run validation and invalidate stale results;
8. perform a bounded UI refresh; and
9. record one compound undo operation.

If ODU, FIN, PI, and ROW arrive together for one row, intermediate edit order
must not erase dependent values. Validation and cascade operate on the final
staged combination.

An explicitly pasted invalid combination is preserved. Predict must not silently
clear or correct it; the affected cell or row remains in an actionable invalid or
warning state.

### 3.3 Single-Edit and Bulk Feedback

A direct single-dropdown edit may provide local feedback such as:

- refreshed dropdown options;
- cleared dependent values;
- recalculated autofill values;
- a short state explanation; and
- a bounded highlight on the changed cell when useful.

A large paste must not produce hundreds of cell highlights or sequential
messages. It provides one aggregate completion summary, for example:

> 320개 케이스 붙여넣기 완료 · 새 행 317개 · Auto 값 2,184개 갱신 · 조합 확인 7개

Normal cells receive no persistent per-cell emphasis after a bulk operation.
Only cells or rows that require action retain invalid or warning presentation.

### 3.4 Row Lifecycle

The broad overhaul direction includes:

- append an empty row;
- insert at the selected position;
- duplicate selected rows;
- delete multiple selected rows;
- reset all rows; and
- expand rows automatically during paste.

The current fallback that deletes the last row when no row is selected is not an
accepted final behavior.

Duplicate copies the input configuration and creates a new stable case identity.
Autofill is recalculated from the copied inputs. Prediction results and terminal
status are not copied.

## 4. Feature Manager and Predict Relationship

Result Review columns and context must not become an independent hard-coded list
of feature keys or labels.

The owner direction is:

- Feature Manager / Data Definition owns stable feature identity, label, role,
  Predict visibility, Predict ordering, mapping relationship, and the active
  generation.
- Predict projects input, auto, and result presentation columns from the active
  generation.
- Standalone and embedded Predict use the same generation-derived projection.
- Result Review is also projected from that active generation.
- Label, visibility, ordering, and generation changes must reconcile safely into
  Result Review.
- A compact Result Review column preference is a Predict presentation concern,
  not ML or schema meaning.

The first implementation is not pre-authorized to add a `review_context` field or
similar presentation preference to the Feature Definition contract. If Predict
owns a review profile, stable feature identity—not a mutable label or raw key—is
the preferred reconciliation basis.

The implementation audit must determine whether the current presentation adapter
carries stable feature identity through the complete projection. If it does not,
that is an owner gap to resolve in the later implementation boundary. This
documentation step changes no schema or public API.

## 5. Result Review Case Distinguishability

The earlier proposal to show only these six raw inputs in Result Review is
rejected:

- 냉방능력;
- 난방능력;
- 실내기;
- 실외기;
- 압축기; and
- 냉매종류.

Those values cannot distinguish:

- the same indoor unit with different Evap indices;
- the same outdoor unit with different FIN, PI, or ROW values; or
- the same refrigerant with different expansion devices.

Result Review must preserve the meaning of the current 11-input configuration.
Two context directions remain under evaluation.

### 5.1 Compact Context Candidate

- 냉방능력
- 난방능력
- Indoor configuration: 실내기 + Evap index
- Outdoor configuration: 실외기 + FIN + PI + ROW
- Compressor: 압축기
- Cycle configuration: 냉매종류 + 팽창장치

This composite context is a product candidate, not a final column contract.

### 5.2 Full Context Candidate

Full Context shows every visible input feature from the active generation as raw
columns.

The roles of Compact and Full Context, the switching mechanism, and preference
persistence remain open until mock evidence exists.

## 6. Result Review Visibility

Confirmed direction:

- Result Review is hidden by default while inputs are being prepared.
- Prediction completion makes result availability clearly discoverable.
- The user can hide or reopen Result Review.

Open decisions:

- whether completion automatically changes the visible surface or steals focus;
- whether completion only reveals a badge, affordance, or panel;
- whether a Result Review manually closed by the user is reopened after every
  subsequent run.

No candidate may treat forced context switching as already approved.

## 7. Unified Ownership and Split Presentation

The historical split-table module will not be restored.

Current unified case ownership and stable `case_id` remain authoritative.
Whether one or multiple visible table widgets provide the best experience is
open. A split or multi-view candidate must use:

- one `PredictSession`;
- one canonical case/result data owner;
- presentation projections derived from the active generation;
- the same case identity in Input and Result Review;
- no hidden joined-copy behavior;
- independent horizontal scrolling and cell selection per view; and
- only row selection and vertical-position synchronization when required.

The existing unified table is not preselected as the only possible visible
widget. A projection-based split presentation remains eligible when it produces
a meaningful UX improvement and its synchronization risk is demonstrably
controlled.

## 8. Open Layout Candidates

No candidate in this section is the final layout.

### Candidate A — Collapsible Top/Bottom

- Input and Result Review each use full width.
- Closing Result Review maximizes Input space.
- Opening it may reduce visible row count.
- Row selection and vertical-scroll synchronization are required.

### Candidate B — Full-Surface Switch

- Input and Result Review each use the full window.
- Focus and keyboard interaction are comparatively simple.
- The two surfaces cannot be viewed simultaneously.
- Automatic switching after completion remains a separate decision.

### Candidate C — Left/Right Compact Context

- Context and result can be compared at the same row height.
- Wide standalone windows may benefit.
- The design depends on a viable compact-context projection.
- Small windows and embedded Predict may not provide sufficient width.

### Candidate D — Full-Width Review with Selected-Case Detail

- Batch result comparison receives the largest area.
- A separate detail region shows the selected case's complete input/auto
  configuration.
- Comparing detailed configurations across several cases may be difficult.

## 9. Disposable PySide6 Mock Evaluation Baseline

Mock comparison is the next step. It has not been created or run.

### 9.1 Prototype Method

- Use a disposable harness below `/tmp`.
- Reuse current PySide6 widgets, styles, `PredictSession`, active-generation
  projection, and fixtures where practical.
- Do not modify production source, schema, models, or mapping data.
- Build interactive prototypes with real Qt geometry and behavior rather than
  image-only wireframes.
- Treat every prototype output as design evidence, not production
  implementation.

### 9.2 Common Fixture

Every layout candidate uses the same data:

- 30 populated cases;
- normal, warning, invalid, and runtime-error states;
- the same IDU with different Evap-index combinations;
- the same ODU with different FIN, PI, and ROW combinations;
- different compressor, refrigerant, and expansion-device combinations; and
- a separate 300-row density state.

### 9.3 Required Screen Conditions

- standalone at 1440×820;
- embedded at 1440×820;
- standalone at 1000×640; and
- embedded at 1000×640.

### 9.4 Evaluation Areas

- Input authoring space;
- result comparability;
- case-configuration distinguishability;
- 30-row and 300-row density;
- small-window degradation;
- embedded Predict suitability;
- keyboard focus;
- dropdown editing;
- row-selection and scroll relationships;
- case correspondence after insert, delete, and reset;
- runtime-generation refresh;
- Result Review reveal behavior; and
- implementation complexity and regression risk.

### 9.5 Feature Manager Variation

Use in-memory generation variations, not real schema changes, to evaluate:

- label changes;
- Predict ordering changes;
- addition of a visible input;
- a context feature becoming hidden or unavailable;
- standalone/embedded projection consistency after runtime refresh;
- stable-identity reconciliation of a compact review profile; and
- generation-derived Full Context refresh.

### 9.6 Expected Evidence

- screenshots captured under identical conditions;
- a layout contact sheet;
- candidate-specific advantages, disadvantages, and observable failures;
- interaction findings; and
- a comparison that lets the user select the final direction.

## 10. Decision and Delivery Sequence

The required sequence is:

1. preserve product direction and mock baseline in documentation;
2. prepare and run the disposable layout comparison;
3. present comparable evidence and obtain the user's layout/context decision;
4. fix the implementation boundary, acceptance, and owner gaps; and
5. prepare the Lane C Build handoff.

Production source implementation and Worker Build handoff remain blocked until
steps 2–4 are complete.

## 11. Current Exclusions

This exploration does not perform or decide:

- production source implementation;
- mock prototype creation or execution in this documentation slice;
- final layout selection;
- Worker or Lane C Build handoff;
- a Feature Definition schema field;
- Result Review preference persistence;
- header-aware import or a CSV import wizard;
- graph, export, or Advanced surfaces;
- ML feature, model artifact, or Calculator formula changes;
- restoration of the legacy split-table module;
- broad architecture refactoring; or
- production data/model mutation, packaging, or deployment.

## 12. Exploration Exit Criteria

The exploration may advance to a Lane C implementation handoff only when:

- all candidates were compared with the common fixture and screen conditions;
- the evidence distinguishes confirmed contracts from candidate behavior;
- the user selected the layout, Result Review reveal behavior, and context
  direction;
- stable-identity and generation-projection owner gaps are understood;
- bulk-paste transaction, single/bulk feedback, row lifecycle, and case identity
  acceptance are explicit; and
- preserved runtime, model, mapping, and result/status contracts remain intact.
