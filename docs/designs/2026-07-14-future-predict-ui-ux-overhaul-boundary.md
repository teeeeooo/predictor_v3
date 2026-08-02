# Predict Input/Result Overhaul — Approved Product and Integration Boundary

Status: approved boundary; Slices 1–6 closed; Target applicability correction implemented on a focused branch pending independent exact-head audit
Created: 2026-07-14
Updated: 2026-08-02
Prerequisite: Train/Admin Phases 1–5 and Predict Findings #1–#7 complete

## 1. Purpose and Authority

This record is the authoritative product and integration boundary for the
**Predict input workflow broad overhaul**. It absorbs the completed disposable
layout comparison and existing-application owner audit into a production-facing
design direction. Slices 1–6 are closed. No successor source slice is authorized
by this close; future work requires its own product/owner decision and review
boundary.

This record distinguishes:

- **approved product direction**, which future work must preserve;
- **existing owners**, which future work must reuse rather than duplicate;
- **Predict seams delivered by Slices 1–6**, which remain bounded by their closed
  contracts;
- **Active compatibility invariants**, which are not Case-specific; and
- **the Case-scoped Target applicability integration gap**, whose Owner Audit is
  complete and whose source correction remains a separate gate.

No source, test, schema, public result type, model, mapping data, Calculator
formula, or runtime behavior changes are made by this documentation decision.

## 2. Preserved Contracts

The overhaul preserves:

- one logical prediction case per visible row;
- stable `case_id` association for canonical case and result ownership;
- one canonical `PredictSession` per workspace;
- standalone and Train-embedded Predict using the same workspace implementation,
  generation-derived presentation, and runtime coordination;
- Feature Manager / Data Definition, Data Mapping, Train/model lifecycle,
  prediction execution, and Calculate as their existing authoritative owners;
- current mapping dropdown, cascade, and autofill semantics;
- row isolation, progressive and partial results, cancellation, validation, and
  the no-usable-model execution gate;
- Active observation, atomic reload, reload-failure fallback, and no-hot-swap
  behavior;
- fail-closed Active compatibility against the full runtime Target contract; and
- production model and data mutation as separately authorized operations.

The historical split-table implementation and its synchronization owner are not
restored. Input and Result Review read the same canonical session; neither owns a
mutable joined copy of cases or results.

## 3. Approved Input Authoring

Expected usage remains approximately 70% Excel paste and 30% on-screen dropdown
authoring. Both are first-class workflows.

The first paste format is headerless value-only TSV interpreted in active Predict
input-column order. Paste creates every required overflow row rather than
discarding values. Header recognition, arbitrary column matching, and an import
wizard remain outside the first scope.

The row lifecycle includes:

- append an empty row;
- insert at the selected position;
- duplicate selected rows;
- delete multiple selected rows;
- reset all rows; and
- expand rows automatically during paste.

Deleting the last row when no row is selected is not accepted as the final
fallback. Duplication copies the input configuration into a new stable
`case_id`, recalculates mapping-backed Auto values, and does not copy prediction
results or terminal status.

A single dropdown edit may provide bounded local feedback for changed options,
cleared stale dependents, recalculated Auto values, and an actionable issue.
Large paste provides one aggregate completion summary and keeps persistent
emphasis only on rows or cells that require user action.

## 4. Approved Shared Workspace

### 4.1 Layout B — Full-Surface Switch

Input Authoring and Result Review each use the full Predict workspace. This
Layout B direction is approved and is not an open layout candidate.

- Standalone and embedded Predict use the same composition and canonical session.
- Both surfaces share the same stable `case_id` and selected-case state.
- Each surface keeps its own table interaction, focus, cell selection, and
  horizontal scrolling behavior.
- No persistent selected-case detail panel is added.
- Full Context is not added as a separate screen or mode.
- The visible `Case` value is a simple row number. Stable `case_id` remains the
  underlying association identity and is not replaced by that ordinal.

### 4.2 Workspace-State Owner

A Predict-owned workspace-state controller is required and is shared by both
shell compositions. It owns:

- the current Input or Result surface;
- the selected stable case identity;
- the surface visible when a run starts;
- whether the user explicitly changed surface during that run; and
- whether terminal completion may reveal Result Review.

Initial behavior:

- validation-blocked execution remains on Input;
- terminal completion with at least one complete or partial result may switch to
  Result Review;
- if the user explicitly selects Input during execution, completion does not
  force a Result Review switch;
- standalone and embedded shells do not create separate Predict sessions,
  lifecycle controllers, or view-state policies; and
- process-restart persistence is not part of the first implementation.

## 5. Result Review Contract

### 5.1 Review Order

The default Result Review follows the user's review sequence:

```text
Case
→ 상태
→ 냉방능력
→ 난방능력
→ 사양 요약
→ EER
→ COP
→ 냉방 주파수
→ 난방 주파수
→ 냉매량
```

The user first locates the row and its state, confirms the requested cooling and
heating capacities, verifies the entered hardware configuration, and then
compares its predicted results. `사양 요약` is therefore case-identifying
information, not optional decoration, and remains before the result metrics.

Status and issue presentation must be discoverable through text and accessible
detail or tooltip behavior. Color-only row tint is supplemental.

### 5.2 사양 요약

The default review has one user-facing `사양 요약` column. It must distinguish:

- IDU / Evap index;
- ODU / FIN / PI / ROW;
- Compressor; and
- Refrigerant / Expansion device.

The semantic display order is:

```text
IDU / Evap
· ODU / FIN / PI / ROW
· Compressor
· Refrigerant / Expansion
```

Summary composition follows three separate concerns:

- authoritative value selection uses stable feature identity;
- visible labels and values come from the active generation; and
- grouping, formatting, and display order belong to Predict presentation.

Slice 4 resolves the presentation detail as four deterministic groups joined by
` · `, with entries inside a group joined by ` + `. The projection retains the
complete active-generation label/value text. The table cell stays single-line
and may visually elide at narrow widths, while its tooltip exposes the complete
summary; no shortened semantic value is persisted or exported.

Mutable labels, current column positions, and arbitrary string keys are not
authoritative identity. Predict-specific summary grouping, width, and Result
priority are not added to the Feature Definition semantic schema.

### 5.3 Current Result Metrics

The default Result Review exposes:

- EER;
- COP;
- cooling frequency;
- heating frequency; and
- refrigerant quantity.

Cooling and heating power remain in the canonical result contract as prediction
outcomes and as the source values for EER/COP. They are not priority columns in
the default review, but diagnostics and a future full-row copy/export projection
must retain access to their raw values and provenance.

EER and COP are not ML targets:

```text
EER = cooling capacity W ÷ cooling power W
COP = heating capacity W ÷ heating power W
```

Their calculation owner is a Qt-free Predict application result-enrichment
boundary. It consumes raw typed inputs and target outcomes, preserves raw numeric
precision and unit/source provenance, and returns deterministic W/W metrics or an
explicit unavailable reason. The Qt projection performs display formatting and
rounding only. EER and COP display exactly two decimal places; their raw
`DerivedMetricOutcome` values remain unchanged for typed application and
copy/export consumers.

Missing, failed, non-finite, zero, or negative required inputs do not become
silent numeric values. EER and COP availability is determined independently by
whether its mode was requested and whether the corresponding power outcome was
actually accepted. Failure of one requested Target does not fabricate failure or
availability for a Target that was not requested for that Case.

### 5.4 CSPF and HSPF2 Capability

A single current Predict row does not provide the multiple operating points and
standard-specific inputs required to calculate CSPF or HSPF2. Neither metric is
shown in Result Review until a real runtime calculation capability exists.

Calculate remains the authoritative standard-formula and Calculator result
contract owner. Predict does not copy its formulas. A future application seam may
collect several pinned, provenance-bearing operating-point predictions, assemble
a standard request, and call the Calculate application boundary.

Multi-point orchestration, standard input contracts, unit adapters, incomplete
point handling, and seasonal calculation integration are a separate future
workstream. Existing mock or formula-placeholder columns are not implemented
Predict capabilities.

## 6. Existing Owner and Dependency Boundaries

```text
Feature Manager / Data Definition
  stable identity, meaning, role, visibility, active generation,
  Predict ordering, ML ordering
             │
             ▼
Predict application/runtime seams
  identity descriptor, typed results and execution context,
  derived metrics, Result Review projection, workspace state,
  bulk transaction
       ├────────► Data Mapping: dropdown/cascade/autofill rules
       ├────────► Train/model lifecycle: Candidate/Active/reload
       ├────────► Prediction execution: row requests/results/cancellation
       └────────► Calculate: future standard capability/formula execution
             │
             ▼
Shared standalone/embedded Predict presentation
```

Qt views depend on Predict application contracts. Predict application seams
reuse the existing semantic, mapping, lifecycle, execution, and Calculate owners.
Feature semantics and Calculator formulas do not depend on Predict layout
preferences.

### 6.1 Feature Manager / Data Definition

Feature Manager / Data Definition owns:

- stable feature identity and feature meaning;
- role and visibility;
- active generation;
- Predict ordering; and
- ML ordering.

Predict reuses those semantics and separately owns Result Review priority,
`사양 요약`, and workspace view state.

The current presentation descriptors lose canonical identity before the final
Predict application/presentation boundary. Implementation therefore requires a
Predict-owned, immutable, identity-bearing runtime descriptor seam. It must
preserve identity alongside the existing generation-derived label, role,
visibility, order, mapping, and value-source metadata without adding
Predict-specific review fields to Feature Definition.

### 6.2 Data Mapping and Bulk Paste

The existing single-cell owners remain authoritative:

- IDU drives Evap options and indoor Auto values;
- ODU drives FIN → PI → ROW and condenser Auto values;
- Compressor drives compressor-derived Auto values; and
- Refrigerant and Expansion remain mapping-backed selectors.

The first bulk-paste contract remains headerless value-only TSV in active Predict
input order. Header recognition, arbitrary column matching, and an import wizard
are outside the first scope.

Bulk paste is not implemented as repeated cell edits. A separate Predict
application transaction slice must own:

1. complete TSV parse and required row expansion;
2. raw value staging and preservation of each final pasted combination;
3. reuse of loaded mapping data;
4. final-combination cascade and autofill;
5. clearing only stale dependent values that were not explicitly pasted;
6. retention of invalid pasted combinations with exact cell/row issues;
7. validation and canonical result invalidation;
8. one bounded batch refresh;
9. rollback on transaction failure; and
10. one compound undo operation.

Large-paste feedback remains aggregate; single-dropdown edits may retain bounded
local feedback. Layout B composition and bulk paste are separate Lane C slices
and must not be bundled in one PR.

### 6.3 Train and Model Lifecycle

Existing ownership remains:

- Train `ModelManagementService` and the promotion repository own Candidate and
  Active lifecycle;
- Predict lifecycle service observes the Active revision, performs explicit
  atomic reload, and preserves the previous usable model when reload fails; and
- the shared runtime participant coordinates standalone/embedded generation
  cutover.

Predict workspace and Result Review do not duplicate Train lifecycle or
promotion authority.

Current results lack enough run, model/runtime generation, session, and input
revision provenance to prevent stale attachment after edits or cutover. A typed
execution-context seam and acceptance gate are required before Result Review
implementation.

### 6.4 Prediction Result Contract

The existing row-isolated, progressive, partial, cancellation, validation, and
no-usable-model behaviors remain.

A future typed contract distinguishes target outcome from aggregate row outcome:

- target available;
- target unavailable;
- target failed;
- row invalid;
- row error;
- row cancelled;
- row partial; and
- row complete.

It preserves raw numeric value, unit, stable source identity, run ID,
model/runtime generation, session identity, case identity, and input revision.
Before a result mutates the canonical session, the acceptance gate rejects any
outcome whose run, generation, session, case, or input revision no longer matches
the active execution context.

### 6.5 Active Compatibility and Case-Scoped Target Applicability

Active compatibility and Case execution are separate contracts.

An Active artifact must provide the complete capability required by the current
runtime Target contract and must prove that compatibility before Predict may use
it. A Target capability missing from an Active artifact is an incompatible
Active and a fail-closed error. It is not supported partial-target capability and
must not be treated as a compatibility relaxation. Existing Candidate/Active
promotion, explicit reload, reload-failure fallback to the previous usable
model, Active observation, and no-hot-swap semantics remain unchanged.

A compatible Active can still produce a runtime `partial` result when actual
inference fails for only some Targets requested by a particular Case. Therefore:

- missing model artifact capability means incompatible Active / FAIL; and
- failed execution for a subset of requested Targets on a valid Active means
  runtime `partial`.

The existing ML policy already establishes mode-specific missing and feature
boundaries: `Cooling Capa`, `Heating Capa`, `Cooling Power`, and `Heating Power`
may use mode-specific missing; cooling Power/Hz Targets exclude heating-side
leakage and risk features; heating Power/Hz Targets exclude cooling-side leakage
and risk features; and ordinary missing hardware or Mapping features are not
equivalent to an absent operating mode. The ML/Data Definition owners remain the
authority for those rules; this design does not copy or redesign them.

Predict must consume that established policy as a Case-scoped requested Target
contract. The correction boundary is:

- inspect canonical raw user input before zero-fill or preprocessing;
- request cooling-mode Targets when cooling capacity is present;
- request heating-mode Targets when heating capacity is present;
- do not request the opposite mode's Targets when its capacity is blank;
- distinguish blank from numeric `0`, negative, and non-numeric invalid input;
- keep mode-independent Targets such as refrigerant quantity under their
  existing Target/feature policy and request them as common Targets for a
  runnable Case;
- mark a cooling-only or heating-only Case `complete` when every requested
  Target succeeds;
- mark a Case `partial` only when actual execution fails for part of its
  requested Target set;
- preserve N/A / not-applicable meaning in Result Review for Targets that were
  not requested instead of fabricating failures; and
- resolve EER and COP independently from requested mode and the actually
  accepted corresponding power outcome.

This is a requested execution subset for one Case. It must not shrink the Active
runtime Target registry, change model artifact capability, or weaken full Active
compatibility. The focused Lane C correction now consumes the established ML
policy as this Case-scoped requested Target contract while the full runtime
Target authority remains unchanged. Independent exact-head audit and Close are
still required before merge.

The final execution/validation UX when both cooling and heating capacities are
blank is resolved as normal Case-scoped Target selection:

| Cooling Capa | Heating Capa | Requested Targets |
| --- | --- | --- |
| present | present | `Cooling Power`, `Heating Power`, `Ref Qty`, `Cooling Hz`, `Heating Hz` |
| present | blank | `Cooling Power`, `Ref Qty`, `Cooling Hz` |
| blank | present | `Heating Power`, `Ref Qty`, `Heating Hz` |
| blank | blank | `Ref Qty`, only when its existing required input contract is satisfied |

Both capacities blank does not by itself invalidate a Case. `Ref Qty` is the
existing mode-independent common Target, so a Ref Qty-only execution is a normal
Case when the current authoritative Ref Qty HW/one-hot/model input requirements
and validation are satisfied. This does not make an entirely empty row runnable
or bypass missing Ref Qty inputs. Blank remains distinct from numeric `0`,
negative, and non-numeric invalid input.

For a valid Ref Qty-only Case:

- successful `Ref Qty` execution makes the row `complete`;
- actual `Ref Qty` execution failure follows the existing terminal/error
  semantics;
- Cooling/Heating Power and Hz are not requested and remain N/A;
- EER and COP are N/A; and
- Predict does not fabricate unavailable/failed outcomes for not-requested
  Targets.

This is not a user-selected Ref Qty-only mode and adds no selector, model
artifact, Target-registry reduction, Active compatibility relaxation, or new
TargetOutcome status. Full compatible Active/runtime Target capability remains
mandatory. Existing mode-missing policy, target-specific exclude/allowed and
leakage rules, Ref Qty feature requirements, lifecycle, execution provenance,
EER/COP formula, Result Review, Layout B, and bulk transaction contracts remain
closed and unchanged. The Lane C correction now derives this requested-Target
matrix from canonical raw Case input, pins its stable Target identity order in
execution provenance, and carries it through inference, acceptance, migration,
enrichment, and Result Review without changing the full runtime registry.

### 6.6 Calculate

Calculate owns standard formulas, capability execution, and Calculator result
contracts. Predict never reproduces those formulas.

Future integration may let Predict assemble a provenance-bearing multi-point
request and call a Calculate application boundary. That work begins only after
the operating-point and standard-request contracts are separately defined.

## 7. Implementation Slice Boundary

Slices 1–6 are independently audited, merged, and closed. No successor source
slice is authorized by this bounded close. Any future implementation retains a
separate product/owner decision and review boundary.

### Slice 1 — Stable Identity Seam

**Status: merged and closed.** Canonical Feature identity is carried into Predict
application and presentation through an immutable generation-bound runtime
descriptor. Generation rename, order, visibility, add/hide, migration, and
standalone/embedded parity remain preserved.

### Slice 2 — Typed Result and Execution Context

**Status: merged and closed.** Predict stores raw typed Target outcomes and
immutable session/case/run/input-revision/runtime/model provenance behind one
canonical acceptance boundary. Repository-issued generation authority is the
only source of canonical Predict runtime authority; reload and generation
transitions preserve typed evidence with explicit current/stale semantics, while
sealed migration/rollback artifacts retain atomic lifecycle behavior.

### Slice 3 — EER/COP Enrichment

**Status: merged and closed.** Slice 1 identities and Slice 2 raw outcomes now
calculate deterministic W/W metrics in a Qt-free Predict application owner. The
accepted request pins stable-identity capacity evidence, canonical acceptance
recomputes and validates the exact enrichment attachment, and existing
reload/generation/rollback lifecycle preserves that historical execution
evidence. Feature formula schema, ML Targets, persisted/public Feature Definition
shape, and Calculator formulas remain unchanged.

### Slice 4 — Result Review Projection

**Status: independently audited, merged, and closed.**

Provide a read-only projection over the canonical session with:

- Case ordinal;
- textual status and issue access;
- cooling and heating capacity;
- one `사양 요약`;
- EER and COP;
- cooling and heating frequency;
- refrigerant quantity;
- target and calculation capability gating; and
- a full-row copy/export boundary that retains hidden source results and
  provenance.

Do not create mutable result-row copies, hidden joined tables, a persistent
detail panel, or a separate Full Context surface.

The Slice 4 application boundary also serializes selected full rows as TSV with
headers in canonical case order. The visible ten fields come first, followed by
hidden raw cooling/heating power, freshness, stable case identity, execution
run/input/runtime/model provenance, and typed power source metadata. The richer
application document retains the canonical typed outcomes and execution context;
file export remains deferred.

### Slice 5 — Shared Layout B Composition

**Status: independently audited, merged, and closed.**

Slice 4 is composed with the Input/Result full-surface switch once for standalone
and embedded Predict. One Qt-free workspace-state owner retains surface and
stable selected-case policy, terminal reveal is bounded by run-local user choice,
and runtime replacement rebinds both cached presentations without changing
canonical session, lifecycle, or shell-specific ownership.

### Slice 6 — Bulk Paste Transaction

**Status: independently audited, merged, and closed.**

Headerless TSV is staged in active stable-identity input order against one Mapping
snapshot, then committed as one canonical Predict transaction. Overflow rows,
final-combination cascade/autofill, raw invalid values with precise issues,
affected-only result invalidation, exact rollback, and fail-closed compound undo
share the existing session, Mapping, execution-provenance, and Layout B owners.
Bulk and ordinary authoring reproject the same row-specific Mapping state and
current issue truth.

### Future — Calculate Integration

After a multi-point prediction and standard-request contract exists, add a
separate Predict-to-Calculate application integration workstream.

Dependency direction:

```text
Slice 1 ───────────────┐
                       ├─► Slice 4 ─► Slice 5
Slice 2 ─► Slice 3 ────┘
   └──────────────► Slice 6

Future multi-point contract ─► Calculate integration
```

## 8. Reconciled Gates

Partial-target Active support is closed as a rejected direction. Full runtime
Target capability remains an Active compatibility invariant. Case-scoped
applicability controls only the requested execution subset on a compatible
Active, and actual failure within that requested subset controls
Complete/Partial status.

The read-only Owner Audit, Ref Qty-only product decision, and focused Lane C
source correction are complete. The next correctness gate is a **fresh
independent exact-head Lane C Auditor** and Close. Narrow Viewport Result Review
Pinning remains a later independent presentation slice with Case + 상태 as the
anchor direction; it must not be bundled with the correctness repair. The
default Result Review order and Layout B full-surface direction remain approved.

## 9. Current Exclusions

The closed Slice 6 implementation does not include:

- public schema or result-type changes;
- header matching, arbitrary import mapping, or an import wizard;
- CSPF/HSPF2 implementation;
- model-lifecycle or Feature Definition generation changes;
- Calculator formula changes;
- process-restart workspace-state persistence;
- a persistent detail panel, Full Context screen, or legacy split-table restore;
- graph, Advanced surface, CSV/XLSX file export, export dialog/preferences,
  packaging, or deployment.

## 10. Evidence Baseline and Next Gate

The existing-application owner audit completed without repository mutation and
reported **218 focused tests passed in 30.46s**. The audit established that the
current Feature Manager, Data Mapping, Train/model lifecycle, prediction
execution, and Calculate owners were reusable while the Predict
application/presentation seams in this record were still missing at that
baseline.

That baseline remains navigation evidence for the broader overhaul. Slices 1–6
were subsequently implemented, independently audited at their exact PR heads,
and merged without changing the public/generated Predict projection or persisted
Feature Definition shape. Slice 2 established repository-issued Predict runtime
authority and the canonical typed-result/provenance boundary; Slice 3 added
execution-pinned raw EER/COP enrichment; Slice 4 added the read-only Result
Review projection, stable-identity summary, and provenance-preserving clipboard
boundary; Slice 5 composed that projection with Input through one shared
workspace-state policy and standalone/embedded Layout B; Slice 6 added the
canonical final-combination bulk transaction, Mapping/issue continuity, atomic
rollback, and fail-closed compound undo without changing ML Targets, Feature
formula schema, or Calculator formulas.

The focused correction implements the approved requested subset without changing
ML/Data Definition policy, runtime Target membership, or Active artifact
compatibility. The next action is a **fresh independent exact-head Lane C
Auditor** and Close, followed only after separate authorization by the independent
Narrow Viewport Result Review Pinning presentation slice. CSV/XLSX export,
future multi-point Predict-to-Calculate integration, and other deferred product
work remain separate and unstarted.
