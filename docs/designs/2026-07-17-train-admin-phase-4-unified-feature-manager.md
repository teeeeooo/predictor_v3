# Train/Admin Phase 4 — Unified Feature Manager

Status: proposed active phase design — current-state audit and finalization pending
Date: 2026-07-17
Depends on: completed Phases 1–3, especially the Phase 3 Data Definition UX foundation

## 1. Goal

> Data Definition을 Predict와 ML 학습에 쓰이는 Feature를 사용자가 직관적으로 추가·수정·삭제·정렬하고 안전하게 저장할 수 있는 통합 Feature Manager로 개선한다.

This is not a cosmetic pass over the existing Data Definition screen. The final
workflow lets a user manage the Predict and ML Feature contract without directly
coordinating internal CSV, JSON, Python registry, or projection files.

Phase 3 remains the completed table-first Data Definition UX foundation. Phase 4
extends that foundation; it does not retroactively change Phase 3 acceptance or
restore the former Feature Catalog UI as a canonical editor.

## 2. Final Feature Scope

The unified workflow must represent:

- Manual Predict input;
- Mapping-backed Feature;
- Predict-only Feature;
- ML-only Feature;
- Derived Feature;
- One-hot selector;
- One-hot group and category;
- Result/Target;
- Helper/Hidden Feature.

Predict visibility and ML-training use are independent intents for every Feature
type for which each intent is meaningful. Users choose purpose and usage intent;
they do not author raw schema rows or internal allowlist values.

## 3. User Workflow

The final manager supports:

- Add, Edit, Duplicate, Remove, and Rename;
- Move Up and Move Down under an explicit ordering contract;
- Enable and Disable;
- export of the current unsaved draft;
- Reset Draft;
- change-impact Preview and dependency inspection;
- safe Save.

Every mutation is a controlled application command, not a widget-local row
operation. An accepted command updates the whole immutable draft atomically; a
rejected command leaves it unchanged and explains the dependency or unsupported
operation plus a resolution direction. A newly added unsaved Feature can be
removed so that a draft equal to its baseline becomes clean again.

## 4. Existing Foundation to Extend

Phase 4 preserves and extends:

- table-first inventory;
- immutable draft and baseline;
- controlled Add/Edit commands and edit policy;
- projection, validation, save plan, and impact projection;
- guarded atomic schema writer;
- Data Mapping handoff and coverage;
- model compatibility fingerprint guard;
- separate Data Definition and Data Mapping owners;
- existing Predict, Train, Data Definition, and Data Mapping tabs;
- Qt-free domain/application-owner direction.

`config/ml/features.csv` does not return to an independent user-edit owner, and
the retired Feature Catalog UI does not return as the canonical editor.

## 5. Current-state Gaps

The merged implementation must be audited for these known gaps before detailed
implementation is frozen:

- no Remove, Duplicate, or Move/Reorder command;
- no persistence owner for active ML-projection changes;
- no transaction that publishes `schema.csv` and `features.csv` consistently;
- no authoring owner for Derived formulas;
- no complete One-hot group CRUD;
- no integrated Result/Target and model-registry editing;
- no post-save live contract refresh for Predict, Train, and Data Mapping;
- some Train Target choices are statically fixed in UI code;
- the model registry is fixed in Python constants;
- some Predict and ML projections are fixed at import time;
- Predict display order and ML projection order are not sufficiently separated;
- no cross-contract dependency command for Feature rename/delete.

These are audit hypotheses, not permission to bypass current guards. Current
production paths continue blocking ML-projection-changing definition saves until
Phase 4 approves and implements a persistence and compatibility boundary.

## 6. Owner Boundaries

### Data Definition

Data Definition is the canonical user-edit owner for:

- Feature structure and stable identity;
- Predict display intent and ML input intent;
- data type and value source;
- mapping requirement definition;
- Derived expression;
- One-hot selector, group, and category definition;
- Result/Target definition;
- Model/Target registry definition;
- ordering contracts;
- validation, impact, and safe persistence of related contracts.

### Data Mapping

Data Mapping continues to own concrete `mapping.json` rows, values, value
editing, validation, and persistence. Data Definition may define a mapping
attribute requirement but does not edit its concrete row values. `mapping.json`
values are outside the multi-artifact definition Save.

### Train / Model

Train owns training-data selection, explicit training start, progress, cancel,
result review, and model artifact creation. Data Definition never starts
training and does not call the Train controller directly.

### Predict

Predict consumes the saved Predict schema, saved Feature contract, compatible
model artifact, and mapping runtime values. When a saved Feature contract makes
an existing model incompatible, Predict exposes a retraining-required state.
Predict's internal UI redesign remains deferred.

## 7. Canonical and Projection Direction

```text
Unified Data Definition
    ├─ Predict schema projection
    ├─ ML feature projection
    ├─ Derived feature policy
    ├─ One-hot group policy
    ├─ Mapping requirements
    └─ Model/Target registry projection
```

The implementation audit will decide the exact canonical file format, package
layout, and number of stored artifacts. The design fixes the outcomes instead:

- Data Definition is the canonical user-edit owner;
- all candidate contracts are generated from one draft;
- every artifact and the combined cross-contract set are validated;
- publish occurs only when every candidate is valid;
- partial artifact publication is forbidden;
- failed Save preserves the prior valid artifact set;
- existing runtime and public consumer contracts remain stable where practical;
- `config/ml/features.csv` remains a projection/compatibility surface, not a
  separate user-edit owner.

## 8. Ordering Contract

Before Move Up/Down is implemented, the audit and design finalization must define
separate meanings and dependencies for:

- Predict display order;
- ML training-contract order;
- One-hot emitted Feature order;
- Derived dependency execution order;
- Target/result presentation order.

The UI states which order a user is changing. Changing one order must not alter
another contract order unless an explicit, validated rule requires it.

## 9. Mutation and Dependency Policy

Add, Edit, Duplicate, Remove, Rename, Reorder, Enable, and Disable are controlled
application commands. Each command is all-or-nothing, mutates only the draft,
supports impact Preview, and rejects dependency violations without partial
application.

Remove and Rename check at least:

- Derived-expression references;
- One-hot source/group/category references;
- mapping requirements;
- Predict runtime required columns;
- training headers;
- Result/Target registry entries;
- model groups and target rules;
- existing model fingerprints;
- protected contracts directly required by code;
- triggers or rules owned by other Features.

## 10. Derived Feature Authoring

Phase 4 includes a restricted, statically validatable expression workflow:

- define Feature name and result data type;
- author a restricted expression over existing Features;
- extract dependencies automatically;
- reject missing references, cycles, type errors, and disallowed functions or
  operations;
- Preview with sample inputs;
- preserve identical evaluation meaning in training and inference;
- validate rename/delete dependencies;
- report retraining required when a formula changes.

Arbitrary Python execution, unrestricted scripts, and arbitrary module imports
are excluded.

## 11. One-hot Group Management

The group-centered workflow supports group create/edit/delete/rename, source
selector assignment, category add/edit/delete/order, emitted ML Feature Preview,
unknown/missing-value policies, dependency-safe rename/delete, and training
header/model compatibility impact.

Selector option source and emitted ML Feature lists remain distinct contracts.
Users manage the group and categories rather than manually aligning raw emitted
rows in a table.

## 12. Result/Target and Registry Management

The workflow supports Result/Target add/edit/delete/rename, Predict-result
visibility, training-Target intent, applicable model group, target-specific
allowed/exclude policies, registry candidate generation, and simultaneous schema
and registry validation.

New validated Targets appear dynamically in Train. Rename/delete validates
dependencies and model artifact compatibility. Users do not edit a Python
registry directly. The audit evaluates a validated provider or projection while
preserving existing runtime consumer APIs where practical.

## 13. Multi-artifact Persistence

One Save operation:

1. snapshots one immutable candidate draft;
2. produces every required candidate artifact;
3. validates each artifact independently;
4. performs cross-contract validation and impact projection;
5. publishes the complete valid set atomically or equivalently transactionally;
6. preserves the previous valid set on any failure.

Concrete `mapping.json` values are never part of this transaction. Compatibility
migration and rollback details remain an explicit Phase 4A/4B design question;
existing guards remain active until that owner is approved and implemented.

## 14. Live Contract Reload

After a successful Save, the shell or composition boundary emits a public
definition-changed event, or an equivalent contract, to the existing owners. It
does not merge controllers or let Data Definition perform their work.

### Data Definition refresh

- load the saved baseline and clear dirty state;
- reflect the Save result;
- show current impact and compatibility.

### Predict refresh

- rebuild column projection;
- preserve existing input by stable identity where possible;
- apply defaults for new columns and remove deleted columns;
- refresh mapping dropdown/autofill relationships;
- reevaluate model compatibility.

### Train refresh

- reload Feature, Target, and model-registry contracts;
- update selected-training-data revalidation state;
- expose retraining required.

### Data Mapping refresh

- reload mapping requirements and dynamic columns;
- preserve existing mapping values;
- reevaluate coverage for added requirements.

Reload failure preserves the previous valid in-memory state and provides an
actionable error rather than partially refreshing tabs.

## 15. Train Boundary

Phase 4 completion requires Train to consume the latest validated dynamic
Feature/Target contract, validate selected training data against it, and show
retraining-required state for an incompatible existing model. The user still
starts training explicitly in Train. After success, existing Train/Predict owners
may reevaluate artifact compatibility.

Phase 4 does not include:

- automatic retraining after Data Definition Save;
- training execution or progress in Data Definition;
- `Save and Retrain`;
- a direct Data Definition → TrainController call;
- automatic model activation orchestration.

## 16. Implementation Slices

Exact class names, helpers, package layout, test paths, and fine-grained order
remain open until the audit. Each slice must preserve existing owner boundaries
and exclude unrelated refactoring, production data, ML algorithm changes, and
Predict internal redesign.

### 4A — Current-state and Contract Audit

Purpose: establish merged-main schema, Feature Catalog, Derived, One-hot,
registry, Train Target consumption, reload, canonical/projection owners, runtime
consumers, protected dependencies, and migration risks.

Required outcome: an approved contract map, ordering semantics, open-decision
resolution, and an ordered implementation plan without production changes.

Validation purpose: prove later slices do not start from a false owner or
consumer assumption and do not omit protected dependencies.

### 4B — Unified Contract and Multi-artifact Persistence

Purpose: generate all candidate contracts from one draft, validate each artifact
and the cross-contract set, and provide an all-or-nothing publish/rollback
boundary.

Required outcome: successful Save makes every artifact reflect the same draft;
failed Save preserves every previous artifact.

Validation purpose: inject validation and write failures at each boundary and
prove there is no partial publication.

### 4C — Controlled Feature Mutation Commands

Purpose: add atomic Add/Edit/Duplicate/Remove/Rename/Reorder/Enable/Disable
commands with dependency-aware mutation and deterministic ordering.

Required outcome: only accepted commands change the draft; protected dependency
violations return actionable reasons.

Validation purpose: prove atomic mutation, clean-state restoration, stable
identity, dependency protection, and isolated ordering semantics.

### 4D — Basic Feature Manager UI

Purpose: connect full basic Feature lifecycle actions to the table-first
workspace and provide Predict/ML-intent-centered dialogs without raw fields.

Required outcome: users manage manual, mapping-backed, Predict-only, and ML-only
Features through the GUI.

Validation purpose: prove complete GUI workflows, draft/selection preservation,
impact Preview, Reset, unsaved-draft Export, and safe Save.

### 4E — Derived Feature Authoring

Purpose: provide the restricted expression and dependency-aware Derived Feature
workflow.

Required outcome: supported formulas have statically validated references,
types, cycles, operations, Preview, and training/inference semantic parity.

Validation purpose: prove invalid references/types/cycles/operations are
rejected atomically and formula changes report compatibility impact.

### 4F — One-hot Group Management

Purpose: provide group-centered One-hot CRUD, category ordering, policies, and
emitted Feature projection.

Required outcome: selector source, categories, emitted ML contract, training
headers, and compatibility impact remain consistent.

Validation purpose: prove dependency-safe group/category mutation and
deterministic emitted order without raw-row coordination.

### 4G — Result/Target and Registry Management

Purpose: manage Result/Target and model-registry mutation together and make Train
consume a dynamic Target contract.

Required outcome: schema, Target, registry, policies, and training contract are
generated and validated consistently.

Validation purpose: prove dynamic Train Target refresh, dependency-safe
rename/delete, policy enforcement, and model compatibility impact.

### 4H — Live Reload and Cross-tab Contract Refresh

Purpose: let Predict, Train, and Data Mapping consume the saved contract without
restart while preserving each owner's responsibility and user state by stable
identity.

Required outcome: every owner reflects one newly published contract or retains
its prior valid state when reload fails.

Validation purpose: prove cross-tab refresh, stable-input preservation, mapping
coverage refresh, training-data revalidation, and compatibility reevaluation.

### 4I — Diagnostics Simplification and Final Acceptance

Purpose: separate ordinary Feature management from advanced diagnostic evidence
and complete automated plus bounded native acceptance.

Required outcome: normal users complete Feature workflows without raw
diagnostics; advanced evidence remains available for regression and support.

Validation purpose: prove default workflow completeness, progressive disclosure,
cross-tab acceptance, and honest fixture/mock limitations.

## 17. Final Acceptance

1. Add a Manual Feature, set Predict and ML use, and save it.
2. Add a Mapping-backed Feature and see its requirement in Data Mapping.
3. Manage Predict-only and ML-only Features.
4. Duplicate a Feature, change its identity, and save it.
5. Validate dependencies before Remove or Rename.
6. Manage Predict display and ML contract order under explicit isolated policies.
7. Author a Derived formula that passes reference, type, and cycle validation.
8. Create, edit, delete, and reorder a One-hot group and its categories.
9. Define a Result/Target consistently with the model registry.
10. Preserve all prior artifacts when Save fails.
11. Refresh Predict, Train, and Data Mapping after successful Save.
12. Preserve Predict inputs where stable identity is unchanged.
13. Show current Feature and Target lists in Train.
14. Start training only through an explicit user action in Train.
15. Show retraining required when an existing model is incompatible.
16. Complete the workflow without directly editing internal CSV, JSON, or Python
    registry files.

## 18. Non-goals

- Predict internal UI/UX redesign;
- moving concrete Data Mapping value editing into Data Definition;
- Calculator changes;
- ML algorithm, Optuna, or RFECV changes;
- production data additions or real training-data migration;
- unrestricted formula scripting;
- automatic retraining or automatic model activation;
- broad unrelated refactoring.

## 19. Open Questions for 4A

- What minimum canonical representation can generate every required projection
  while preserving stable runtime consumer APIs?
- Which persistence primitive provides recoverable multi-artifact publication on
  every supported platform?
- Which identities remain stable across rename, duplicate, and projection
  changes?
- Which current import-time consumers require provider or reload boundaries?
- How are the five ordering contracts represented without accidental coupling?
- Which protected runtime columns, target rules, and registry entries require
  explicit migration policies rather than ordinary mutation?
