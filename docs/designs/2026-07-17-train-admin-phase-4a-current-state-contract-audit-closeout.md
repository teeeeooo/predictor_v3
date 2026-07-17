# Train/Admin Phase 4A — Current-state and Contract Audit Closeout

Status: approved — Phase 4A complete; Phase 4B is the next implementation slice
Date: 2026-07-17
Parent design: `2026-07-17-train-admin-phase-4-unified-feature-manager.md`
Baseline: merged `main` at `76747f61cdb12f32884f606d6ee7d1251857a135`

## 1. Purpose

Close the Phase 4A audit with an approved contract map for the Unified Feature
Manager before production implementation begins.

The approved product objective remains:

> Data Definition을 Predict와 ML 학습에 쓰이는 Feature를 사용자가 직관적으로 추가·수정·삭제·정렬하고 안전하게 저장할 수 있는 통합 Feature Manager로 개선한다.

This closeout resolves the parent design's Phase 4A open questions. Where the
parent design still uses pending or open-question wording for Phase 4A, this
closeout is the authoritative decision amendment. It does not change Phase 3
acceptance or begin Phase 4 production implementation.

## 2. Audited Current State

The merged foundation is safe for Phase 3 behavior but is not a sufficient
canonical contract for the final Unified Feature Manager:

- Data Definition drafts identify rows by source kind plus `column_key` or
  `ml_name`, so a rename changes the draft identity instead of preserving one
  stable Feature identity.
- `config/predict/schema.csv` owns Predict-facing definition metadata, while
  `config/ml/features.csv` remains a separate ML compatibility source.
- Derived formulas and the model registry remain Python-owned rather than
  persisted Definition contracts.
- active ML-projection-changing Definition saves remain blocked because there is
  no `features.csv` projection writer or multi-artifact transaction.
- Predict and ML consumers still retain import-time or cached schema, Feature,
  Target, One-hot, zero-fill, mapping, and model state.
- Train currently writes through a fixed active model path, so candidate and
  active artifact storage are not yet separated in runtime code.
- Data Mapping currently reprojects latest saved requirements over its current
  draft/session state without an explicit pending-generation reconciliation
  contract.

These findings confirm the existing guards rather than authorizing bypasses.

## 3. Approved Canonical Contract Direction

### 3.1 Canonical representation

Phase 4 adopts one versioned structured JSON manifest as the canonical persisted
Data Definition contract.

The exact repository path, package layout, DTO names, and JSON field spelling are
owned by Slice 4B and must follow the repository architecture audit. Slice 4B may
choose the minimum consistent implementation shape, but it must not restore
multiple independently edited canonical files or replace the structured manifest
with an unversioned CSV-only contract without a new design gate.

The canonical manifest represents, at minimum:

```text
Unified Feature Contract
├─ feature definitions
├─ derived definitions
├─ one-hot groups and category policies
├─ result/target definitions
├─ mapping requirements
├─ isolated ordering contracts
└─ generation and compatibility metadata
```

### 3.2 Projection surfaces

The following remain generated compatibility or consumer projections rather than
independent user-edit owners:

- `config/predict/schema.csv`;
- `config/ml/features.csv`;
- Derived runtime projection;
- One-hot runtime projection;
- Target/model-registry projection;
- Mapping-requirement projection.

Concrete `mapping.json` rows and values remain outside the Definition transaction
and remain owned by Data Mapping.

### 3.3 Stable identity

Every canonical managed object has an immutable opaque identity independent of
its display label, `column_key`, `ml_name`, category value, or emitted name.

Required identity classes are:

- Feature identity;
- Derived definition identity;
- One-hot group identity;
- One-hot category identity;
- Target identity;
- validated model-group reference identity;
- mapping-requirement identity where one requirement must survive an ordinary
  rename.

Rename preserves the object's identity and changes validated names or references.
Duplicate creates a new identity. Remove deletes or disables the identified
object only after dependency validation. Existing string keys remain projection
and compatibility values, not the sole canonical identity.

## 4. Approved Ordering Contract

Five order meanings remain independent:

1. Predict display order;
2. ordered ML training/inference Feature order;
3. One-hot emitted Feature order inside a group;
4. Derived execution order;
5. Target/result presentation order.

Predict and ML order are explicitly user-visible intents and changing one does
not silently rewrite the other. One-hot emitted order is part of model
compatibility. Derived execution order is produced from the validated dependency
DAG rather than arbitrary manual ordering. Target presentation order is separate
from model-group membership and model-level training policy.

## 5. Approved Persistence and Generation Contract

Slice 4B implements an immutable generation bundle and one atomic active-
generation publication boundary:

```text
immutable draft snapshot
    → generate every projection
    → validate each projection
    → cross-contract validation
    → stage immutable generation bundle
    → publish complete generation
    → atomically replace active-generation pointer
```

Required behavior:

- each published generation is immutable;
- every Definition projection proves derivation from the same generation;
- partial publication is forbidden;
- failure preserves the previous active-generation pointer and prior valid
  generation;
- prior generations remain available for bounded rollback/recovery;
- disk publication and runtime cutover remain separate outcomes;
- `mapping.json` values and model artifact promotion are separate transactions.

Directly overwriting multiple live projection files in sequence is not an
approved all-or-nothing implementation.

## 6. Runtime Snapshot and Cutover Contract

Every runtime consumer uses an immutable contract snapshot containing or proving:

- generation identity;
- canonical contract version;
- Predict projection;
- ordered ML projection;
- Derived semantics;
- One-hot encoding contract;
- Target/registry projection;
- Mapping requirements;
- scoped fingerprints and preprocessing version.

New runtime work must receive this snapshot through composition/provider
boundaries. Import-time constants and caches may remain temporary compatibility
facades during migration, but they are not the final canonical owner.

Inside one TrainShell process, embedded Predict, Train / Model, Data Definition,
and Data Mapping use staged prepare/commit/abort generation participation. No
required consumer swaps active state before every required consumer prepares the
candidate generation.

If a required consumer cannot prepare after disk publication:

- every in-process consumer retains the previous active generation;
- the whole composition exposes the persisted-but-not-active stale/restart-
  required state;
- no partial or mixed-generation state is reported as normal.

Standalone Predict does not receive cross-process atomicity guarantees. It checks
persisted generation at startup, immediately before prediction, on explicit
Refresh/Reload, and after model reload or promotion. A failed reload preserves
existing rows/results for recovery, marks stale/restart-required, and blocks the
new prediction. IPC or file watching is optional; these boundary checks are
required.

## 7. Dirty Data Mapping Reconciliation

### Clean Mapping draft

A clean Data Mapping draft may prepare the new requirement generation during the
TrainShell generation preflight.

### Dirty Mapping draft

A dirty draft is not silently reprojected or discarded. Data Mapping retains its
current draft, baseline, values, and command history and records a separate
pending requirement generation.

The user receives these paths:

- Review Update;
- Save Mapping;
- Discard and Reload.

Reconciliation uses stable group and requirement/attribute identity. Existing
concrete rows continue using their established row/source identity. Added
requirements may be projected without deleting unsaved values. Attribute
rename/delete, type change, relation/trigger change, removal of a dirty column,
or conflicting declarations are explicit reconciliation conflicts.

Until reconciliation succeeds, the application cannot claim that the newer
generation is the active mixed runtime. The approved default is to keep the
whole TrainShell on the prior active generation and expose the pending/stale
state rather than activating only unaffected tabs.

## 8. One-hot Contract

Every group declares one category source mode.

### Static

Data Definition owns category identity, source value, emitted ML name, policy,
and order. Full category CRUD and ordering are supported.

### Mapping-backed

Data Mapping owns concrete selector option values. Data Definition owns the
selector/group identity, option-to-emitted mapping, emitted naming/order,
unknown/missing policy, validation, and compatibility impact. Removing or
renaming a Definition rule never silently mutates Mapping rows.

The existing Refrigerant and Expansion groups are treated as mapping-backed
because their option vocabulary comes from `mapping.json`.

### External/provider

The external provider owns category identity and values. Data Definition exposes
provider categories read-only or permits only explicitly bounded policy edits.

Unknown-value and missing-value behavior are distinct explicit policies. The
current warning/all-zero behavior may be represented as a compatibility policy;
it is not an implicit universal default.

## 9. Result/Target and Model-group Scope

Initial Phase 4 Target CRUD supports:

- stable Target identity and validated ML name;
- Predict result visibility and presentation order;
- training-Target intent;
- association to an existing validated model group;
- target-level allowed/exclude policy;
- dynamic validated Train Target projection.

Initial supported model groups remain the existing power, frequency, and
refrigerant groups. Phase 4 does not expose creation of arbitrary new model
groups, trainer/algorithm binding, artifact naming, `use_rfe`, or model-family
policy. Those require a separate advanced contract and design gate.

## 10. Training and Artifact Identity

One all-purpose hash is insufficient. The approved identity carries:

- generation ID;
- combined contract fingerprint;
- Predict projection fingerprint;
- ordered ML projection fingerprint;
- Derived semantics fingerprint;
- One-hot encoding fingerprint;
- Target/registry fingerprint;
- Mapping-requirement fingerprint;
- preprocessing version.

Train freezes the relevant immutable snapshot at explicit training start.
TrainingRequest, TrainingResult, and future candidate artifact metadata preserve
the same run and contract identity. A later Definition Save never changes the
active run's start contract.

Predict-only presentation changes need not invalidate a model when the scoped ML
and preprocessing fingerprints remain compatible. ML order/name membership,
Derived expression, One-hot emitted mapping, Target/registry rule, or
preprocessing changes do affect model compatibility.

Training output is a run/generation-scoped candidate, not the active model.
Ownership remains:

| Responsibility | Owner |
| --- | --- |
| artifact format and metadata validation | Core ML artifact boundary |
| candidate request/result management | Train application service |
| candidate and active filesystem storage | artifact repository adapter |
| explicit promotion workflow | Phase 5 Train / Model |
| active compatible model consumption | Predict |

Only a validated current-compatible candidate may be promoted. Promotion is
explicit and automatic promotion/activation remains excluded. Promotion failure
or a stale/incompatible candidate preserves the prior compatible active model.

## 11. Protected Dependency Policy

Current code still contains protected string-bound consumers, including fixed
Predict column keys, One-hot selector/group names, Derived source names, registry
Target names, training headers, and existing artifact Feature names.

Until each owner migrates to stable identity/provider consumption:

- ordinary Rename/Delete is blocked with an actionable owner/slice reason;
- Python source is never changed by automatic string replacement;
- Impact Preview lists protected dependencies and migration requirements;
- only an explicitly approved atomic migration command may change a protected
  dependency and all of its validated projections.

Current ML-projection-changing Save guards remain active until Slice 4B publishes
and validates the approved canonical and generation boundary.

## 12. Ordered Implementation Plan

The approved order is:

```text
4B canonical manifest, bootstrap migration, projection providers,
   generation bundle, active pointer, cross-contract validation,
   scoped fingerprints
→ 4C stable-ID Feature mutation, rename/remove/dependency and isolated ordering
→ 4D Basic Feature Manager UI
→ 4E Derived authoring and shared evaluator
→ 4F One-hot group/category management
→ 4G Result/Target and registry management
→ 4H in-process cutover and standalone generation detection
→ 4I diagnostics simplification and final acceptance
```

Slice 4B is an architecture/schema migration slice. It must begin on a separate
branch from merged closeout `main`, preserve all existing guards until replacement
acceptance passes, and avoid unrelated UI, ML algorithm, production data, model
artifact, or Predict redesign changes.

## 13. Phase 4A Acceptance

Phase 4A is approved because the audit establishes:

- the actual current owners and fixed consumers;
- canonical and projection direction;
- stable identity and ordering semantics;
- all-or-nothing generation publication and rollback;
- in-process and cross-process runtime policies;
- immutable training-run identity;
- candidate-versus-active artifact ownership;
- dirty Mapping reconciliation;
- One-hot source-mode ownership;
- Target/model-group scope;
- protected dependency policy;
- an ordered implementation path.

No production code, configuration, data, fixture, model artifact, or public API is
changed by this closeout.

## 14. Non-goals

- Phase 4B production implementation;
- Predict internal UI redesign;
- automatic training, promotion, or activation;
- Data Definition editing of concrete Mapping values;
- arbitrary Python formula execution;
- arbitrary new model-group creation;
- ML algorithm, Optuna, RFECV, calculator, production data, or model-quality
  changes.
