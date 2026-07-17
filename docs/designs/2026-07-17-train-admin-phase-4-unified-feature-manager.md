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
- no cross-contract dependency command for Feature rename/delete;
- the current training publication path replaces the fixed active model path at
  completion instead of preserving a validated candidate/promotion boundary;
- standalone Predict has no cross-process persisted-generation detection
  boundary.

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
- One-hot selector/group policy and source-mode-owned category definition;
- Result/Target definition;
- Target registry definition and association to validated existing model groups;
- ordering contracts;
- validation, impact, and safe persistence of related contracts.

### Data Mapping

Data Mapping continues to own concrete `mapping.json` rows, values, value
editing, validation, and persistence. Data Definition may define a mapping
attribute requirement but does not edit its concrete row values. `mapping.json`
values are outside the multi-artifact definition Save.

### Train / Model

Train owns training-data selection, explicit training start, progress, cancel,
result review, candidate model artifact creation, and the explicit owner-
controlled promotion workflow. Data Definition defines compatibility metadata
needed to classify an artifact but never starts training, promotes a candidate,
activates a model, or calls the Train controller directly.

### Predict

Predict consumes the saved Predict schema, saved Feature contract, promoted
compatible active model, and mapping runtime values. It never treats training
success or an unpromoted candidate as active-model availability. When a saved
Feature contract makes the active model incompatible, Predict exposes a
retraining-required state. Predict's internal UI redesign remains deferred.

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

Selector option vocabulary and emitted ML Feature lists remain distinct
contracts. A group declares one category source mode with an explicit mutation
owner:

- **Static category vocabulary** — Data Definition owns category identity,
  definition, and ordering. Categories are independent of concrete Data Mapping
  values, and emitted ML Features derive from this Definition contract.
- **Mapping-backed category vocabulary** — Data Mapping concrete option values
  are the selector vocabulary source. Data Definition owns selector identity,
  One-hot group identity, emitted-name policy, category-to-emitted mapping rules,
  and validation. Removing or renaming a Definition rule never silently deletes
  Data Mapping rows. Mapping option changes produce Preview, validation, and
  compatibility impact rather than implicit Definition-row mutation.
- **External/provider-backed vocabulary** — the provider owns category identity
  and values. Data Definition exposes them read-only or permits only bounded
  policy edits and cannot persist categories absent from the provider.

Phase 4A finalizes canonical category identity, ordering, unknown/missing policy,
and allowed mutations for each source mode. Users manage the applicable policy
or owned vocabulary rather than manually aligning raw emitted rows.

## 12. Result/Target and Registry Management

The workflow supports Result/Target add/edit/delete/rename, Predict-result
visibility, training-Target intent, applicable model group, target-specific
allowed/exclude policies, registry candidate generation, and simultaneous schema
and registry validation.

New validated Targets appear dynamically in Train. Rename/delete validates
dependencies and model artifact compatibility. Users do not edit a Python
registry directly. The audit evaluates a validated provider or projection while
preserving existing runtime consumer APIs where practical.

The initial Phase 4 boundary supports Result/Target CRUD, association to a
validated existing model group, and target-level allowed/exclude policy. Target
CRUD does not imply arbitrary model-family creation. New model groups,
trainer/algorithm binding, artifact naming, `use_rfe`, and other model-level
training policy remain a separate advanced contract and are not editable through
the default Feature Manager. Phase 4A may expand this only by approving a
separate explicit workflow, validation contract, and artifact owner; otherwise
unsupported group creation/reference is blocked with an actionable reason.

## 13. Multi-artifact Persistence

Disk publication and application runtime activation are separate stages:

```text
definition draft validation
    → persisted artifact transaction
    → consumer reload preflight
    → process-wide generation cutover
```

The persisted artifact transaction:

1. snapshots one immutable candidate draft;
2. produces every required candidate artifact;
3. validates each artifact independently;
4. performs cross-contract validation and impact projection;
5. assigns one immutable generation/version identity and combined fingerprint;
6. publishes the complete valid set atomically or equivalently transactionally;
7. preserves the previous valid set on any failure.

Concrete `mapping.json` values are never part of this transaction. Compatibility
migration and rollback details remain an explicit Phase 4A/4B design question;
existing guards remain active until that owner is approved and implemented.
Persistence success does not mean runtime cutover success. The consumer preflight
and process-wide cutover contract belongs to Slice 4H and consumes the
persisted generation identity defined by Slice 4B. A post-persistence cutover
failure leaves an explicit stale-runtime/restart-required recovery state; it is
never reported as fully applied.

Definition persistence and model artifact lifecycle are separate transactions:

```text
Definition contract transaction
    ≠ training candidate artifact publication
    ≠ active model promotion
```

Slice 4B owns only the Definition contract transaction. Phase 4 defines the
generation/fingerprint and Target/registry metadata required to validate model
compatibility, but does not publish a training candidate or replace the active
model. Those artifact operations remain isolated under the established model/
artifact owner and the Phase 5 workflow.

## 14. Live Contract Reload and Process Scope

Every persisted contract set has one immutable generation/version identity or an
equivalent fingerprint. Predict schema, ML projection, Derived policy, One-hot
policy, Mapping requirements, and Target/registry projection share that identity
or carry proof that they derive from it. Each consumer reports its currently
active generation. A definition-changed event, or equivalent coordination
contract, carries the persisted generation and relevant fingerprints without
merging controllers or letting Data Definition perform their work.

### In-process generation cutover

Within one TrainShell process composition, embedded Predict, Train / Model, Data
Definition, and Data Mapping share one process-wide active generation. Normal
state never mixes generations across these required owners. Live reload uses a
staged cutover:

```text
new persisted generation
    → consumer reload preflight
    → candidate in-memory projections
    → every required owner ready
    → process-wide generation commit
```

If any required owner cannot prepare, Phase 4A must approve one explicit policy:
all owners retain the previous active generation, or the persisted generation
remains on disk while the entire process composition enters a visible stale-/
restart-required state. Some owners silently activating the new generation while
others retain the old one is forbidden. Persistence failure, consumer preflight
failure, in-memory cutover failure, stale runtime generation, and restart-required
recovery are distinct user-facing states. Save success and runtime-apply success
are never presented as the same outcome.

The refresh responsibilities below prepare candidate state only. No required
owner swaps its active projection before the process-wide generation commit.

### Data Definition refresh

- prepare the saved baseline and activate it only at generation commit;
- distinguish persisted Save from active runtime application before clearing or
  relabeling state;
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

Definition reload never silently discards a Data Mapping unsaved draft. Clean
Data Mapping may prepare the new requirement generation immediately. Dirty Data
Mapping retains its draft and reports a visible pending contract update with
Review, Save Mapping, and Discard and Reload paths. Automatic draft replacement
is forbidden while dirty.

Phase 4A decides whether stable group/attribute identity can safely rebase a
dirty draft, how new requirements preserve unsaved rows, how rename/delete
conflicts with unsaved cells are resolved, whether such a conflict blocks the
process-wide cutover, and how a stale Data Mapping generation affects the
whole runtime state. Until reconciliation succeeds, the pending update is not
hidden and the application cannot claim a fully active mixed generation.

Reload or cutover failure preserves the previous valid in-memory state and user
drafts where applicable, then provides an actionable stale/restart-required
recovery state rather than partially refreshing tabs.

### Cross-process generation detection

Process-wide cutover does not promise atomic simultaneous activation across OS
processes. Standalone `app_predict` and any separately launched Train/Predict
instance independently track:

- persisted contract generation;
- the process-wide active generation;
- promoted model artifact generation/fingerprints;
- mapping/provider generation when required by its consumer contract.

Standalone Predict checks for a newer persisted generation at application
startup, immediately before prediction execution, on explicit Refresh/Reload,
and after model reload or artifact promotion. Prediction follows this boundary:

```text
prediction requested
    → read persisted generation
    → compare with process-wide active generation
    → equal: validate promoted model compatibility and execute
    → different: full consumer reload preflight
        → success: process-wide cutover, then execute
        → failure: preserve rows/results, mark stale/restart-required,
          and block the new prediction
```

A stale process never silently continues new prediction. Existing input rows and
results may remain available for review and safe recovery, but reload failure
must not quietly discard them or imply execution availability. A promoted model
whose generation/fingerprints do not match the active Definition contract is not
Predict-compatible. IPC or file watching is optional Phase 4A design scope;
startup and prediction-boundary generation validation remain required even
without them.

## 15. Train Boundary

Phase 4 completion requires Train to consume the latest validated dynamic
Feature/Target contract, validate selected training data against it, and show
retraining-required state for an incompatible existing model. The user still
starts training explicitly in Train. After success, existing Train/Predict owners
may reevaluate artifact compatibility.

At training start, Train freezes an immutable run contract snapshot containing,
or proving equivalently:

- Data Definition generation;
- ML Feature projection fingerprint;
- Target/model-registry fingerprint;
- Derived/One-hot preprocessing fingerprint or one combined contract fingerprint;
- preprocessing version.

The Training result and model artifact preserve the same run identity. An active
run continues using its start snapshot even if Data Definition persists a newer
generation. The recommended default is not to block Definition Save solely
because training is active; changes never apply retroactively to that run. Phase
4A must explicitly confirm this concurrency policy or justify a stronger Save
block and its cross-tab coupling.

At completion, Train distinguishes run success, artifact-save success, current-
contract compatibility, and Predict availability by comparing the run contract
fingerprint with the current active fingerprint. An artifact trained under an
older generation is stale/incompatible unless separately proven compatible; it
is never automatically activated for the current contract. The existing
compatible model remains preserved until the new artifact passes compatibility.

Training output is first a candidate artifact, not the active model:

```text
training run
    → run/generation-scoped candidate artifact
    → artifact structure and metadata validation
    → run-contract versus current-contract compatibility
    → recorded candidate state
    → explicit owner-controlled promotion
    → atomic active-model replacement where supported
```

The candidate lives separately from the active model path, is identifiable by
run ID and generation/fingerprints, and preserves the start contract identity in
its metadata and TrainingResult projection. Training success alone never
overwrites or activates the active model.

Before promotion, the artifact/model owner validates loadability, artifact
format/version where applicable, run generation and fingerprints, compatibility
with the current Feature/Target/Derived/One-hot/preprocessing contract,
Target/model-group association, and expected output contract. Training success,
candidate Save success, compatibility, promotion success, and Predict
availability remain separate states.

Promotion is an explicit Phase 5 Train/Model action owned by the established
artifact/model boundary. Only a validated compatible candidate may atomically or
equivalently replace the active model. Promotion failure preserves the existing
compatible model. Stale/incompatible candidates remain reviewable or removable
under the future artifact lifecycle but cannot be promoted. Automatic promotion
and automatic activation are excluded.

Phase 4 owns the compatibility metadata contract, stale/incompatible
classification, current-model preservation invariant, and relationship between
Target/registry fingerprints and artifact metadata. It does not own the training
UI, candidate generation execution, or promotion action.

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
resolution, process-wide generation contract, standalone Predict detection
policy, immutable training snapshot contract, candidate-versus-active artifact
lifecycle and promotion owner/rollback, dirty Mapping draft reconciliation
policy, One-hot category source modes, Target/model-group scope, and an ordered
implementation plan without production changes.

Validation purpose: prove later slices do not start from a false owner or
consumer assumption and do not omit protected dependencies, training races,
dirty-draft conflicts, runtime cutover failure states, current fixed-path model
overwrite migration, or stale standalone prediction.

### 4B — Unified Contract and Multi-artifact Persistence

Purpose: generate all candidate contracts from one draft, validate each artifact
and the cross-contract set, assign the persisted generation identity, and provide
an all-or-nothing disk publish/rollback boundary. Slice 4B exposes the persisted
generation and candidate-loader contract consumed by Slice 4H; it does not own
process-wide in-memory cutover, model candidate publication, or active-model
promotion. It may expose only the Definition generation/compatibility metadata
provider required by the later artifact lifecycle.

Required outcome: successful Save makes every artifact reflect the same draft;
failed Save preserves every previous artifact.

Validation purpose: distinguish candidate validation, disk artifact publication,
persisted generation identity, consumer preflight input, and runtime cutover;
inject write failures and prove there is no partial disk publication.

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

Required outcome: static category CRUD, mapping-backed option reconciliation,
external/provider restrictions, emitted ML contract, training headers, and
compatibility impact remain consistent without cross-owner deletion.

Validation purpose: prove static category mutation, deterministic category and
emitted ordering, unknown/missing policies, and that Mapping option changes do
not silently delete or rewrite Data Definition category contracts.

### 4G — Result/Target and Registry Management

Purpose: manage Result/Target and model-registry mutation together and make Train
consume a dynamic Target contract.

Required outcome: schema, Target, registry, target/registry fingerprint,
target-level policies, existing model-group association, and training contract
are generated and validated consistently, with the Target/registry fingerprint
available to candidate artifact metadata validation.

Validation purpose: prove dynamic Train Target refresh, dependency-safe
rename/delete, allowed existing-group association, rejection of unknown group
references, explicit blocking of new model-group creation when out of scope, and
model compatibility impact. Any approved new-group workflow requires separate
model-level contract validation.

### 4H — Live Reload and Cross-tab Contract Refresh

Purpose: let Predict, Train, and Data Mapping consume the saved contract without
restart while preserving each owner's responsibility and user state by stable
identity.

Required outcome: every required TrainShell owner reports one process-wide active
generation. On failure, all in-process owners retain the prior generation or the
whole process reports the approved stale/restart-required state; mixed generation
is never normal. Standalone Predict independently detects persisted-generation
mismatch at required execution boundaries.

Validation purpose: prove consumer preflight and atomic cutover, generation
agreement, explicit stable-input preservation failure, dirty Mapping draft
preservation and visible pending update, stale runtime reporting, training-data
revalidation, and compatibility reevaluation. An active run keeps its start
generation, and an artifact completed from an older generation is not
automatically activated for the current generation. Standalone Predict detects a
new generation at startup or prediction boundary, blocks new prediction when
reload fails, reports stale/restart-required state, and does not claim unsupported
cross-process atomic cutover.

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
8. Create, edit, delete, and reorder a supported One-hot group without assuming
   that Data Definition owns every source vocabulary.
9. Define a Result/Target consistently with the model registry.
10. Preserve all prior artifacts when Save fails.
11. Refresh Predict, Train, and Data Mapping after successful Save.
12. Preserve Predict inputs where stable identity is unchanged.
13. Show current Feature and Target lists in Train.
14. Start training only through an explicit user action in Train.
15. Show retraining required when an existing model is incompatible.
16. Complete the workflow without directly editing internal CSV, JSON, or Python
    registry files.
17. After Definition Save, embedded Predict, Train, Data Definition, and Data
    Mapping consume the same TrainShell process-wide active generation.
18. A consumer preflight failure leaves no mixed-generation normal state.
19. Persisted success followed by cutover failure displays an explicit stale/
    restart-required recovery state.
20. A dirty Data Mapping draft survives a Definition requirement update and
    exposes a pending contract update workflow.
21. Static category vocabulary supports Data Definition CRUD and ordering;
    mapping-backed options reconcile with Data Mapping without implicit row
    mutation; external/provider vocabulary remains read-only or policy-limited.
    Every mode exposes emitted Feature Preview, unknown/missing policy, and
    compatibility impact.
22. An active training run continues using its immutable start snapshot after a
    newer Definition generation is persisted.
23. Training results and artifacts identify their source generation and contract
    fingerprints.
24. An older-generation artifact is not treated as current-contract compatible
    without explicit compatibility proof.
25. The existing compatible model is preserved until a new artifact passes
    compatibility checks.
26. Target CRUD permits validated existing model-group association and clearly
    blocks or separately gates new model-group creation.
27. A completed training run produces a separate identifiable candidate artifact
    and does not replace the active model merely because training succeeded.
28. Only a validated current-compatible candidate can be explicitly promoted;
    stale/incompatible candidates cannot become active.
29. Promotion failure preserves the existing compatible model and its Predict
    availability.
30. Standalone Predict detects a newer persisted generation at startup,
    prediction, explicit reload, or model-reload boundaries.
31. A stale standalone Predict process preserves existing rows/results for
    recovery but blocks new prediction when generation reload cannot succeed.

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
- Which consumers participate in one TrainShell process-wide generation commit,
  and does cutover failure retain the old generation or enter process-wide
  stale/restart-required recovery after disk publication?
- Can dirty Data Mapping drafts rebase by stable group/attribute identity, and
  which add/rename/delete conflicts block generation cutover?
- What exact immutable identity crosses TrainingRequest, TrainingResult, and
  model artifacts, and how is stale-artifact compatibility proven?
- What canonical identity, ordering, unknown/missing policy, and mutation set
  applies to static, mapping-backed, and external One-hot category sources?
- Does Phase 4 remain limited to existing model-group association, or is a
  separately validated model-group creation workflow explicitly approved?
- What owner stores run/generation-scoped candidate model artifacts and promotes
  one validated candidate to the active model?
- What metadata and atomic primitive are required for candidate-to-active
  promotion, and which validation/compatibility checks must pass before replacing
  the existing compatible model?
- At which startup, prediction, explicit reload, and model-reload boundaries does
  standalone Predict detect a newer persisted generation?
- Does optional cross-process detection use IPC, file watching, or only the
  required boundary checks, and does failed reload require restart in addition to
  blocking new prediction?
