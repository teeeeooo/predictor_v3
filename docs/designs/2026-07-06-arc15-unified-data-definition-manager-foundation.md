# Arc 15 - Unified Data Definition Manager Foundation

Status: active reference

Follow-up (2026-07-17): Arc 15's unified user-edit owner and projection direction
remains the foundation for Train/Admin Phase 4 — Unified Feature Manager. Phase 4
extends it with Feature authoring, transaction-safe persistence, and owner-
preserving live reload. Concrete mapping values remain owned by Data Mapping;
training remains an explicit user action in Train; automatic retraining is out
of scope. Arc 15's historical slice plan and exclusions are unchanged.

## Purpose

Arc 15 establishes the Unified Data Definition Manager direction. The goal is
to manage Predict columns, ML features, mapping attribute requirements, one-hot
projection, and training/model readiness through one Data Definition workflow.

Actual mapping value editing remains in Data Mapping Manager. Data Definition
Manager defines what mapping values are required and how they project into
Predict/ML contracts; it does not edit row values in `mapping.json`.

This record is needed because the current design index has Arc 13.5R and Arc 14
records that prepare schema projection and mapping editing, but no Arc 15
record that names the unified owner boundary, compatibility staging, or slice
order.

## Current Codebase State

| Area | Current state |
| --- | --- |
| `config/predict/schema.csv` | Holds Predict column order/key/label, role, editor, data type, visibility/required/readonly flags, value source, mapping entity/attribute, trigger/rule references, model input flag, `ml_name`, and `one_hot_group`. |
| Predict runtime column assembly | `core.predictor_schema.columns.COLUMNS` is assembled through the v2 schema projection path, not the old Feature Catalog plus UI-column merge path. |
| `config/ml/features.csv` | Still acts as the ML feature/target/one-hot/derived contract, including zero-fill and training-header projection behavior. |
| Derived rows | `features.csv` has active `derived` rows. Current `schema.csv` alone does not express the full derived feature contract. |
| Data Mapping Manager | The Train/Admin Data Mapping tab is a mapping value editor backed by runtime `mapping.json` projection, validation, save, reload, and read-only export surfaces. |
| Feature Catalog tab | The Train/Admin shell still exposes a Feature Catalog tab during the transition period. |

## Core Decision

- `schema.csv` is promoted to the primary Data Definition source.
- Do not describe `schema.csv` as sufficient to generate all of `features.csv`
  by itself.
- A separate derived feature policy is required for ML rows that are not direct
  Predict columns or one-hot emissions.
- `features.csv` is demoted after Arc 15C into an ML projection and
  compatibility output.
- During Arc 15A and Arc 15B, `features.csv` remains the existing compatibility
  contract and parity/diff target.
- `mapping.json` remains the mapping value SSOT.
- Data Definition Manager owns column, feature, mapping requirement, and
  readiness editing.
- Data Mapping Manager owns actual mapping value editing.
- Feature Catalog direct edit is not removed immediately. After projection
  parity and save contract stabilization, it should be demoted to an advanced
  or legacy compatibility surface.

## Canonical Relationship

| Artifact / Surface | Canonical role |
| --- | --- |
| `config/predict/schema.csv` | Primary Data Definition source for Predict column, model input, mapping requirement, rule reference, and one-hot selector metadata. |
| Derived feature policy | Source for ML derived features that are not represented by schema rows alone. |
| `config/ml/features.csv` | ML projection and compatibility output after the staged owner switch. Existing compatibility contract during Arc 15A/B. |
| `data/mapping.json` | Mapping value SSOT consumed by runtime dropdown/autofill and edited through Data Mapping Manager. |
| Data Definition Manager | Definition, requirement, projection, validation, and readiness owner. |
| Data Mapping Manager | Value editor for concrete mapping rows and attributes. |
| Feature Catalog Manager | Transition-period compatibility surface until projection parity and save contracts are stable. |

## UX Principle

The user-facing workflow should let an admin express intent directly:

- Add "Evap Inner Surface Area" as a prediction input feature.
- Add "Fan Diameter" as a manual numeric feature.
- Add "Tube Type" as a one-hot selector.

The user should not need to manually understand or coordinate these internal
details:

- the exact `schema.csv` row;
- the exact `features.csv` row;
- the difference between `mapping_key` and `mapping_attribute`;
- manual Data Mapping group column expansion;
- training header readiness;
- model activation state;
- whether a restart is required.

## Add Feature Workflow Examples

| Example | User input | Saved / validated result | Data Mapping Manager connection |
| --- | --- | --- | --- |
| Mapping lookup auto feature | Feature label, target mapping entity, mapping attribute, trigger selector, ML activation intent. Example: `Evap Inner Surface Area` from `evap_index.Inner Surface Area`. | Data Definition stores a schema row with `value_source=mapping_lookup`, validates mapping requirement shape, projects an ML compatibility row only when allowed by the slice, and reports training/model readiness. | Data Definition Manager creates the requirement. Data Mapping Manager exposes the required attribute column and lets the user fill values in the matching mapping group. |
| Manual numeric input feature | Feature label, numeric editor, required/optional flag, ML activation intent. Example: `Fan Diameter`. | Data Definition stores a manual numeric input row, validates model input metadata and training header readiness, and reports inactive model state until retrain. | No mapping value is edited. Data Mapping Manager is unaffected unless the feature later gains a mapping-backed option source. |
| One-hot selector | Selector label, option source, one-hot group name, emitted ML feature names. Example: `Tube Type`. | Data Definition distinguishes selector option source from emitted ML feature list, validates one-hot parity, and keeps runtime owner switch deferred until Arc 15E. | If options are mapping-backed, Data Mapping Manager owns option values. Data Definition Manager owns selector and emitted feature definition. |

## Data Mapping Manager Boundary

- Data Definition Manager defines mapping requirements.
- Data Mapping Manager edits actual mapping values.
- Data Definition Manager does not directly modify `mapping.json` row values.
- Arc 15D's core work is injecting dynamic mapping attribute requirements into
  Data Mapping Manager so the value editor can expose required columns without
  becoming the definition owner.

## One-hot Boundary

- Arc 15A handles one-hot parity and validation only.
- The generic one-hot owner switch is a separate Arc 15E slice.
- Selector option source and emitted ML feature list are separate contracts:
  option source decides what the user can select; emitted ML features decide
  what the model input receives.

## Readiness / Validation

Arc 15 needs these validators before editable owner switch work becomes safe:

| Validator | Purpose |
| --- | --- |
| Schema shape validator | Validate Data Definition row identity, enum, source, and required-field rules. |
| Feature projection validator | Compare schema plus derived policy projection against the current ML compatibility contract. |
| Derived feature policy validator | Ensure derived features are explicitly owned outside direct schema rows. |
| One-hot validator | Validate selector groups, emitted ML feature lists, and current runtime parity. |
| Mapping requirement validator | Validate mapping entity/attribute/trigger/rule requirements before value editing. |
| Mapping value coverage validator | Report missing mapping values for active mapping-backed requirements. |
| Training header validator | Compare active ML projection with available training CSV headers. |
| Model activation validator | Report whether the current model artifact can consume the active projection. |
| Rule reference validator | Confirm `rule_id` references are known and compatible with runtime primitives. |
| Restart impact validator | Classify changes as live-reloadable or restart-required. |

## Runtime Policy

- Mapping value changes should continue in the live-reload direction.
- Schema and column changes are restart-required.
- A newly enabled model input remains inactive until retraining and artifact
  compatibility are confirmed.
- Training CSV header changes are shown in the readiness panel state instead of
  being hidden behind a save action.
- Legacy wide CSV is not used as an import source.

## Arc 15 Slice Plan

| Slice | Goal | Candidate modification scope | Not in this slice |
| --- | --- | --- | --- |
| Arc 15A — Data Definition Core Projection and Cross-contract Validator | Build the Qt-free projection/validator foundation for Data Definition. | New core Data Definition projection helpers, derived feature policy stub/contract, parity/diff report object, focused validation tests if implementation proceeds. | UI changes, save behavior, runtime behavior changes, `mapping.json` writes, model retrain. |
| Arc 15B — Data Definition Read-only UI | Show Data Definition rows, projection status, mapping requirements, one-hot state, and readiness summaries. | Train/Admin read-only panel/controller/service using Arc 15A report objects. | Editing, saving, Feature Catalog removal, Data Mapping value edits. |
| Arc 15C — Add/Edit/Save Data Definition | Add controlled editable Data Definition save workflow. | Save contract for schema rows and derived policy, compatibility projection checks, dirty-state and restart-required state. | Dynamic Data Mapping value injection, generic one-hot owner switch, automatic model activation. |
| Arc 15D — Data Mapping Dynamic Attribute Requirements | Inject Data Definition mapping requirements into Data Mapping Manager. | Data Mapping editor projection/validation extension for dynamic required attributes. | Data Definition Manager editing `mapping.json` values directly, legacy wide CSV import. |
| Arc 15E — Generic One-hot Owner Switch | Move hard-coded one-hot runtime ownership to generic Data Definition projection. | One-hot selector-to-emitted-feature runtime projection and adapter update. | New feature add/save workflow expansion, model retrain automation. |
| Arc 15F — Training / Model Readiness Panel | Make training headers, projection compatibility, artifact activation, and retrain requirements visible. | Readiness service/panel, model/training artifact checks, restart/retrain state display. | Running retrain automatically, transforming real training data. |

Arc 15A must satisfy these constraints:

- no UI changes;
- no save behavior;
- no runtime behavior changes;
- validate `schema.csv + derived feature policy -> features.csv projection`;
- compare projection parity/diff against the current `features.csv`;
- extract mapping requirements;
- validate one-hot relationships;
- create a readiness report object.

## Excluded Scope

- Calculator formula/config/golden changes.
- Legacy wide CSV import restoration.
- Automatic `mapping.json` value generation.
- Schema live reload.
- Automatic model retrain execution.
- Real training data transformation.
- Broad refactor.
- Data Mapping Manager raw JSON editor conversion.
- Excel edit/reimport workflow.

## Final Decision / Next Action

Final decision: Arc 15 proceeds as Unified Data Definition Manager Foundation.

Next: Arc 15A — Data Definition Core Projection and Cross-contract Validator.
