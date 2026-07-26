# Predictor V3 Phase 5 — Train/Model Lifecycle, UX, and Agent-Assisted Experiment Design

- **Status:** Design confirmed
- **Date:** 2026-07-22
- **Project:** `predictor_v3`
- **Scope:** Train/Model workflow, model lifecycle, training analysis artifacts, headless experiment execution, and agent-assisted experiment loop
- **Follow-up phase:** Predict UI/UX overhaul
- **Recommended repository location:** `docs/designs/2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md`

---

## 1. Purpose

Phase 5 reorganizes the Train/Model workflow around four product goals.

1. Training must no longer overwrite the only `model.pkl` on every successful run.
2. A newly trained model must remain a reviewable candidate until the user explicitly chooses to use it.
3. The Train UI must remain simple while still exposing the numerical and machine-learning information needed to judge and tune training quality.
4. The same training and experiment capabilities must be usable headlessly from a terminal so that a local coding agent can run bounded experiments, analyze results, and make recommendations without gaining production decision authority.

The intended end state is:

```text
Training run
→ immutable candidate and analysis artifacts
→ human/agent review
→ explicit user approval
→ active model
→ optional immutable deployment export
```

A separate later phase will redesign the Predict UI/UX. Phase 5 must preserve current Predict behavior except for the minimum model lifecycle and safe reload boundaries required by the new active-model contract.

---

## 2. Current problem

The current production training flow writes a temporary model and then replaces the configured final `model.pkl`. This has several practical limitations.

- Each successful training run replaces the previous model.
- Comparing multiple training results is difficult.
- Rollback depends on external manual backups.
- The result cannot be safely reviewed before it affects Predict.
- Model history, training metadata, feature analysis, and tuning results are not treated as one durable experiment record.
- A terminal-based agent cannot reliably run and compare experiments through a stable machine-readable contract.
- Packaging expects a simple single model, while the training workflow needs richer multi-candidate management.

Phase 5 must solve these without turning the main Train UI into a software administration console.

---

## 3. Product principles

### 3.1 Simple main UI, detailed numerical information

“Simple” means hiding software-internal complexity, not hiding the information needed to judge model quality.

The main Train workflow must show enough information to answer:

- What data and targets are being trained?
- Which preprocessing is active?
- Is RFECV running, and what did it select?
- Is Optuna running, and how is the search progressing?
- What are the key target-level metrics?
- Which features are influential?
- Is the new result better, more stable, or simpler?
- Can the model be used now, or is another action required?

The main UI must not expose implementation-level details such as:

- artifact identifiers
- fingerprints and raw schema hashes
- generation internals
- temporary paths
- process arguments
- serialization details
- raw compatibility payloads
- full tracebacks

Those belong in Advanced or Diagnostics surfaces.

### 3.2 Training does not imply activation

These are separate events:

```text
Training completed
≠ candidate validated
≠ candidate compatible
≠ candidate promoted
≠ Predict using candidate
```

A new candidate never becomes active automatically.

### 3.3 Agent recommends; user decides

A local agent may:

- run bounded experiments
- inspect structured results
- adjust permitted experiment parameters
- include or exclude existing features
- create experimental derived-feature proposals
- compare candidates
- recommend a candidate or recommend further experiments

A local agent may not:

- promote a model
- publish canonical feature definitions
- modify production feature meaning
- delete protected artifacts
- change deployment inputs
- increase its own iteration budget
- declare its own proposal approved

### 3.4 One shared training capability

GUI and CLI must use the same experiment specification, validation, training application service, candidate publication, analysis generation, and compatibility checks.

There must not be separate “GUI training” and “agent training” implementations.

### 3.5 Reproducibility before convenience

Campaigns must freeze the data snapshot, evaluation plan, and training execution contract. If any of those change in a way that affects training meaning, a new campaign is required.

---

## 4. Scope

### 4.1 In scope

- candidate and active model lifecycle
- first-use Bootstrap mode
- immutable candidate preservation
- explicit promotion and rollback
- training result comparison
- Train main UI simplification
- Advanced and Diagnostics separation
- preprocessing, RFECV, Optuna, metric, and feature-analysis presentation
- CSV and XLSX training analysis artifacts
- optional SHAP analysis as an Advanced capability
- headless single-run experiment interface
- campaign-based experiment execution
- local agent-assisted experiment loop
- configurable loop budget with default maximum of 5 iterations
- data snapshot and evaluation-plan reproducibility
- target-specific exploratory runs and full production confirmation runs
- workspace-wide single training writer lock
- pause, cancel, resume, retry, and failure recovery
- artifact retention and user-approved cleanup
- active-model deployment export
- safe Predict active-model reload boundary
- result-contract versioning and backward-readable history

### 4.2 Out of scope

- Predict UI/UX redesign
- Predict input/table/graph redesign
- executable or installer packaging
- automatic production feature publication
- automatic model promotion
- arbitrary Python execution for derived features
- unbounded autonomous optimization
- automatic deletion of candidates or reports
- splitting the production bundle into independently promoted target model files
- a GUI button that calls or controls a local AI agent
- external agent API integration
- changing the core ML algorithm solely as part of this phase

---

## 5. Owner and dependency direction

Implementation must preserve the repository’s existing ownership boundaries.

- Core ML remains the owner of model training semantics.
- Application services coordinate training requests, validation, publication, comparison, promotion, and export.
- UI remains an adapter over application-level contracts.
- GUI and CLI share the same application service.
- Predict resolves the active model through an explicit owner rather than assuming that a fixed path was just overwritten.
- Dynamic feature/target registry and runtime generation contracts remain authoritative.
- Experimental derived features do not become canonical definitions without a separate approved publication path.
- Model lifecycle work must not absorb the responsibilities of Definition publication or runtime-generation ownership.

Exact package, class, helper, and file names are intentionally not fixed in this document. The implementation worker must audit existing owners and sibling implementations and choose the smallest structure consistent with current architecture.

---

## 6. Core domain concepts

### 6.1 Candidate

A candidate is the immutable output of a completed training run or confirmation run.

A candidate may contain:

- model bundle
- manifest
- resolved experiment specification
- target-level metrics
- feature selection and importance results
- tuning history
- preprocessing summary
- human-readable report
- machine-readable result
- training log

A candidate is not active by default.

### 6.2 Active model

The active model is the one model bundle currently selected for Predict.

There is at most one active bundle per workspace.

The active state should be represented through an atomic active-model reference or equivalent safe owner-controlled mechanism, not by destroying history through repeated fixed-path replacement.

### 6.3 Campaign

A campaign is a bounded set of comparable experiments sharing:

- immutable data snapshot
- frozen evaluation plan
- frozen execution contract
- target roles
- iteration budget
- experiment policy
- leaderboard and recommendation history

### 6.4 Run / iteration / attempt

- **Iteration:** one experiment hypothesis consuming campaign budget after actual training starts
- **Run:** the durable record of that iteration’s resolved specification and outcome
- **Attempt:** an execution attempt for the same iteration, used for bounded transient retry

### 6.5 Campaign incumbent

The incumbent is the best valid candidate inside a campaign.

It is not necessarily active.

### 6.6 Deployment export

A deployment export is an immutable, explicitly selected, flattened output derived from the active model for later application packaging.

It is not the executable package itself.

---

## 7. Model lifecycle

### 7.1 Required states

The implementation may choose precise internal names, but it must represent at least these user-relevant conditions:

- candidate available for use
- experimental result not eligible for use
- partial result
- performance criteria not met
- invalid result
- active
- previously active / superseded
- rejected
- deleted artifact with retained history

### 7.2 Candidate publication

Current behavior:

```text
train to temporary file
→ replace active model path
```

Required behavior:

```text
train into temporary candidate area
→ write model and analysis artifacts
→ validate artifact completeness and compatibility
→ atomically publish immutable candidate
→ keep current active model unchanged
```

A failed, cancelled, or incomplete run must never replace the active model.

### 7.3 Promotion

Promotion occurs only after explicit user approval.

Before promotion, the system must verify at minimum:

- candidate artifact exists
- artifact hash is valid
- model can be deserialized
- all production-required targets are present
- feature order and preprocessing contract are valid
- current Definition/runtime generation compatibility is satisfied
- no unpublished experimental feature blocks use
- any required bounded prediction smoke succeeds

Promotion failure must preserve the existing active model.

### 7.4 Rollback

Rollback is implemented as re-promoting a previous valid candidate after repeating current compatibility checks.

There is no separate unsafe “copy an old file over the current model” path.

### 7.5 Bootstrap mode

When no active model exists:

```text
no active model
→ first valid candidate becomes campaign baseline only
→ later candidates compare against campaign incumbent
→ final recommendation remains approval-required
→ user promotion creates the first active model
```

The first candidate must not become active automatically.

UI wording should say that no model has been selected yet, not expose a missing-file traceback.

### 7.6 Legacy model import

If a pre-Phase-5 `model.pkl` exists without lifecycle metadata:

- preserve it
- validate it
- import it as a legacy candidate or legacy active reference only when safe
- clearly record limited metadata
- never overwrite it during import
- fall back to Bootstrap mode if it cannot be safely recognized

---

## 8. Candidate artifact contract

A candidate should be self-contained enough for review and reproducibility.

A conceptual structure is:

```text
candidate/
├─ model.pkl
├─ manifest.json
├─ result.json
├─ resolved_experiment.yaml or equivalent
├─ change_delta.json
├─ training_report.xlsx
├─ training.log
└─ analysis/
   ├─ target_metrics.csv
   ├─ selected_features.csv
   ├─ rfecv_ranking.csv
   ├─ feature_importance.csv
   ├─ optuna_trials.csv
   ├─ best_parameters.csv
   ├─ preprocessing_summary.csv
   ├─ failed_targets.csv
   └─ optional_shap_results.*
```

The physical layout may change after repository audit, but these information categories must remain available.

### 8.1 Manifest contents

The manifest must provide enough information to verify identity and compatibility, including:

- artifact/candidate identifier
- creation time
- artifact format version
- model hash
- training execution contract identifier
- Definition/runtime generation identity
- feature/target fingerprints required by existing architecture
- production target list
- feature list and order
- preprocessing contract version
- training data snapshot identity
- candidate eligibility state

### 8.2 Result contract

`result.json` or equivalent must be machine-readable and must contain:

- run and campaign identifiers
- status
- baseline type and baseline identifier
- candidate identifier
- target-level metrics
- stability metrics
- feature counts and selected features
- best parameters
- artifact locations through safe relative references or owned identifiers
- promotion eligibility
- blocking reasons
- recommendation inputs
- schema version

Natural-language logs must not be the only source for agent decisions.

---

## 9. Training analysis artifacts

### 9.1 Required human-readable report

Each valid or partial completed run must generate a consolidated XLSX report with, at minimum, the following information categories:

- Summary
- Target Metrics
- Selected Features
- RFECV Ranking
- Feature Importance
- Optuna Best Parameters
- Optuna Trials
- Preprocessing
- Run Information

Exact sheet names may follow existing project conventions, but the report must be understandable without opening internal JSON.

### 9.2 Required machine-readable analysis

CSV or equivalent tabular files must remain available for automation and independent analysis.

At minimum:

#### Target metrics

- target
- train/CV/validation scope
- R²
- MAE
- RMSE
- sample count
- fold/seed stability where applicable

#### RFECV

- target
- feature
- selected
- rank
- evaluation score or score context
- selection order when available

#### Feature importance

- target
- feature
- importance method
- raw value
- normalized value
- rank

The importance method must be recorded because gain, weight, permutation importance, and SHAP do not mean the same thing.

#### Feature data quality

- feature
- missing count/rate
- unique count
- variance or equivalent low-variance signal
- outlier summary
- target usage

#### Optuna

- trial number
- parameters
- score
- state
- duration
- selected best-trial indicator

### 9.3 SHAP

SHAP is optional and Advanced.

- It is not required for every training run.
- Its cost and scope must be explicit.
- The output must record target, sample strategy, explainer/method, and computation conditions.
- Lack of SHAP must not make an otherwise valid candidate ineligible.

---

## 10. Train UI design

### 10.1 Main page

Train uses a single main workflow page whose central area changes by state:

```text
ready
→ training
→ result review
→ apply or continue experimenting
```

The default flow must not require moving through multiple administrative tabs.

### 10.2 Always-visible summary

The main page should expose:

- current active-model status
- selected dataset
- target summary
- training readiness
- preprocessing summary
- RFECV summary
- Optuna summary
- evaluation-mode summary
- active external campaign status, when one exists

### 10.3 Numerical information shown on the main page

Main UI must show concise but meaningful numerical information:

- current training stage
- target being trained
- Optuna trial progress and best score
- RFECV selection summary
- elapsed time
- target-level key metrics
- feature count before/after selection
- top influential features
- comparison with campaign baseline or active baseline when valid
- absolute metrics and CV stability in Bootstrap mode

### 10.4 Separate surfaces

#### Detailed Results

- full target metrics
- baseline comparison
- RFECV details
- feature importance
- Optuna history
- preprocessing results
- report and CSV access

#### Advanced

- detailed search spaces
- sampler/pruner
- target-specific tuning
- evaluation split/seed configuration
- derived-feature experiments
- early stopping
- campaign execution policy

#### Model Management

- active model
- candidate history
- previous model selection
- protected/pinned state
- retention and cleanup
- deployment export

#### Diagnostics

- compatibility details
- runtime generation/fingerprint details
- artifact integrity
- raw logs
- tracebacks

### 10.5 UI language

Prefer user-facing wording:

| Internal concept | UI wording |
|---|---|
| Candidate | 새로 학습한 모델 / 학습 결과 |
| Active model | 현재 사용 모델 |
| Promotion | 이 모델 사용 |
| Rollback | 이전 모델로 변경 |
| Experimental candidate | 실험 결과 |
| Promotion blocked | 현재 상태에서는 적용할 수 없음 |
| Deployment export | 배포용 모델 만들기 |

### 10.6 No agent-control button

The GUI must not provide:

- Agent loop start button
- natural-language agent prompt box
- agent session controls
- agent API configuration
- automatic agent execution

The GUI may display externally created campaign status and results because GUI and CLI share the same campaign store.

---

## 11. Shared Experiment Specification

GUI and CLI must consume the same declarative experiment specification.

The format may be YAML, JSON, or an existing repository-native configuration representation after audit, but it must express:

- experiment name and purpose
- data source/snapshot request
- target roles
- included/excluded features
- experimental derived features
- preprocessing
- RFECV
- Optuna
- evaluation plan
- campaign budget
- early stopping
- retry policy
- recommendation thresholds

Before training, defaults must be fully resolved and the complete resolved specification must be stored with the run.

Each iteration must also store its delta from the selected incumbent or baseline.

### 11.1 Default precedence

Conceptually:

```text
explicit one-run override
→ campaign configuration
→ project default
```

Defaults must not remain implicit after execution.

### 11.2 Configuration safety

The experiment specification must not provide a bypass for:

- arbitrary Python
- arbitrary output overwrite
- automatic promotion
- automatic Definition publication
- iteration-budget self-increase
- protected artifact deletion
- path escape outside owned storage

---

## 12. Headless CLI capability

Phase 5 must provide a headless application boundary suitable for local agents and users operating in a terminal.

Required capability categories:

- validate an experiment specification
- run a single experiment
- start a campaign
- inspect status
- inspect structured results
- compare candidates
- pause after current run
- cancel current run
- resume campaign
- extend a user-approved budget
- produce a recommendation artifact
- export an approved active model

Exact command names are implementation choices after audit.

The CLI must return reliable exit status and structured machine-readable output where applicable.

A local agent should prefer CLI inspection commands over guessing internal file semantics.

---

## 13. Agent-assisted experiment loop

### 13.1 Invocation

The agent loop starts only when the user explicitly instructs a local agent in a CLI, IDE, or local agent application to run code and perform the experiment workflow.

The product GUI does not initiate the agent.

### 13.2 Default budget

- Default `max_iterations`: **5**
- The value is configuration, not a hardcoded invariant.
- The user may choose 10 or another permitted value for a specific campaign.
- `max_iterations` means total campaign allowance, not additional iterations.
- An agent may recommend extension but may not increase the limit itself.

Example behavior:

```text
completed: 5
user changes max_iterations to 10
remaining allowance: up to 5
```

### 13.3 Agent permissions

Allowed inside an approved campaign policy:

- parameter/search-space adjustments
- RFECV changes
- preprocessing changes
- include/exclude existing features
- experimental declarative derived features
- target-scoped exploratory runs
- candidate comparison
- recommendation generation

Forbidden:

- canonical feature publication
- active-model promotion
- deployment replacement
- protected artifact deletion
- unbounded retries
- budget escalation
- arbitrary code insertion
- silent execution-contract changes

### 13.4 Iteration discipline

By default each iteration must have:

- one explicit hypothesis
- one primary change category
- a pre-recorded change plan
- incumbent reference
- result
- interpretation
- next-step rationale

Optuna may explore multiple parameters inside one tuning iteration.

Combined experiments are permitted only when marked as such, and the agent must state that individual causal contribution cannot be separated.

### 13.5 Recommendation output

The agent must produce both machine-readable and human-readable recommendations containing:

- recommended candidate
- runner-up
- current active or campaign baseline
- target-level changes
- stability changes
- feature-count changes
- feature additions/removals
- derived-feature proposals
- rejected candidates and reasons
- uncertainty and limitations
- additional experiment recommendation
- explicit `approval required` state

The agent may also conclude:

```text
No candidate is recommended.
Keep the current active model.
```

---

## 14. Derived-feature experiments

### 14.1 Declarative-only execution

Experimental derived features must use a restricted declarative expression contract.

Initial supported expression categories may include:

- arithmetic
- parentheses
- absolute value
- powers and square roots
- logarithmic transforms
- min/max/clipping
- deterministic conditional replacement
- differences, ratios, and products of existing features

Forbidden:

- `eval` / `exec`
- imports
- file access
- network access
- subprocesses
- arbitrary lambdas
- target references
- prediction-result references
- time- or randomness-dependent expressions
- future-row access

### 14.2 Shared evaluator

Train GUI, Train CLI, agent experiments, and Predict must use the same derived-feature evaluator owner.

### 14.3 Preflight

Before training, the evaluator must check:

- missing inputs
- target leakage
- cycles
- division by zero
- invalid log/sqrt domain
- excessive NaN/inf
- unsupported expressions
- constant/empty output
- Predict reproducibility

Warnings such as high correlation or ambiguous units should be reported but not always hard-blocked.

### 14.4 Experimental vs production

A candidate using an unpublished derived feature is experimental and not promotable.

Required production flow:

```text
experimental derived feature
→ performance evidence
→ agent proposal
→ user approval
→ formal feature implementation/publication
→ new generation
→ retrain under production definition
→ new promotable candidate
→ user promotion
```

The experimental candidate itself must not be relabeled as production-ready without retraining.

---

## 15. Data and evaluation reproducibility

### 15.1 Campaign data snapshot

A campaign must own an immutable or equivalently reproducible data snapshot.

All campaign iterations use the same snapshot.

Changing the data creates a new campaign.

Snapshot metadata must include:

- source identity
- snapshot time
- file/content hash
- row/column counts
- target list
- feature list
- basic missingness
- filtering rules
- stable row identity or row fingerprint
- split/seed plan

The worker may choose copy, content-addressed storage, or another repository-consistent mechanism after audit.

### 15.2 Evaluation plan

The campaign freezes:

- CV folds
- seeds
- train/validation row assignment
- optional grouping or temporal rules
- valid rows by target
- locked final-test policy

Supported modes must include at least:

#### Cross-validation only

- fixed CV plan
- out-of-fold metrics
- optional multi-seed stability
- no independent final-test claim

#### Holdout guarded

- training/CV for tuning
- fixed validation for candidate comparison
- locked final test for final confirmation only

### 15.3 Locked final test

The agent must not repeatedly inspect the final test and tune against it.

A final-test result must be used only at the independent final confirmation stage.

---

## 16. Active baseline comparison

Historical metrics saved with the active model are reference information only.

Official comparison requires evaluating the active model under the current campaign snapshot and evaluation plan.

Campaign modes:

- `comparable_active`
- `unbenchmarked_active`
- `no_active` / Bootstrap

If the active model cannot be fairly evaluated under current conditions:

- keep it active
- report why it is not comparable
- do not claim improvement over active
- rank campaign candidates using absolute metrics and within-campaign comparisons

---

## 17. Target roles and partial results

Campaign target roles:

- **Primary targets:** intended improvement focus
- **Guardrail targets:** must not degrade beyond configured limits
- **Production-required targets:** must all be present for a promotable bundle

Target-specific exploratory runs are allowed for cost-effective search, but they are never promotable.

A full production confirmation run must retrain all production-required targets using the selected final specification.

### 17.1 Partial results

If some targets fail:

- preserve successful target analyses
- preserve failure evidence
- mark the result partial
- block promotion
- allow the agent to use it for the next proposal

A fully failed run preserves logs and campaign history but does not publish a usable model candidate.

---

## 18. Candidate evaluation and recommendation

### 18.1 Hard gates

A candidate is excluded from final recommendation when any required condition fails, including:

- required target failure
- leakage
- unreproducible Predict feature
- invalid derived-feature output
- incompatible execution/feature contract
- guardrail violation
- excessive instability
- incomplete artifact
- unpublished experimental feature when production eligibility is required

### 18.2 Ranking principles

Among gate-passing candidates, compare in this order:

1. primary-target improvement
2. guardrail-target behavior
3. CV/seed stability
4. feature count and avoidable complexity
5. physical plausibility and explainability
6. training cost and reproducibility

Primary metric defaults and thresholds must be configurable, not hardcoded.

A reasonable default policy may prefer RMSE as the primary metric with MAE and R² as secondary metrics, but the implementation must allow campaign-specific choices.

### 18.3 Bootstrap ranking

Without an active baseline:

- first valid candidate becomes initial incumbent
- later candidates compare against incumbent
- use absolute metrics and stability
- do not claim production readiness without configured acceptance evidence
- keep final promotion approval with the user

---

## 19. Final confirmation gate

The agent-assisted search result is not automatically the final production candidate.

Required end flow:

```text
agent campaign completes
→ recommended resolved specification is frozen
→ all production-required targets are trained
→ no further feature/parameter adjustment
→ independent confirmation evaluation
→ optional locked final test
→ user review
→ promotion
```

A separate retraining run is not mandatory when the final campaign run already satisfies all confirmation requirements and no post-result tuning occurred.

The requirement is an independent final confirmation stage, not unconditional duplicate computation.

If final confirmation fails or does not reproduce the expected result:

- block promotion
- preserve current active model
- retain all evidence
- allow a new user-approved campaign

---

## 20. Execution locking and concurrency

One workspace permits one training writer across:

- GUI training
- headless single runs
- agent campaigns
- campaign resume

All entry points share the same lock owner.

Read-only actions remain available:

- status
- logs
- candidate history
- reports
- active model status

During Phase 5, promotion is blocked while training publication is active. A simpler rule may block promotion for the full training duration if that is the safest minimal implementation.

The lock must record enough information for stale-process diagnosis, including owner, process, start time, heartbeat, and current stage.

An agent must not terminate another execution.

---

## 21. Pause, cancel, resume, and retry

### 21.1 Pause

Preferred user action:

- finish the current run
- stop before the next iteration
- preserve campaign as resumable

### 21.2 Cancel

Immediate cancellation:

- stop the current run
- do not publish an incomplete candidate
- preserve safe partial analysis and logs when available
- leave the campaign paused unless explicitly terminated

### 21.3 Resume

Resume preserves:

- data snapshot
- evaluation plan
- target roles
- execution contract
- completed runs
- leaderboard

User-approved changes may include:

- total maximum iteration budget
- time budget
- early-stopping policy
- permitted experiment search range

Changing data or training meaning requires a new campaign.

### 21.4 Iteration consumption

Counts as an iteration:

- actual training started, regardless of success, partial failure, metric failure, or user cancellation

Does not count:

- preflight configuration failure
- missing input before training
- unsupported expression detected before training
- lock conflict
- preflight storage failure

### 21.5 Retry

Transient retry:

- bounded
- configured
- recorded as another attempt for the same iteration
- never infinite
- never increased by the agent without user approval

---

## 22. Execution-contract reproducibility

A campaign freezes the training-meaning contract, including:

- code/build revision identity
- training specification contract version
- Definition/runtime generation
- preprocessing implementation version
- model artifact format
- relevant ML dependency identity
- metric calculation contract
- agent experiment policy version

UI-only changes may not invalidate a campaign when the training contract fingerprint remains unchanged.

Training-meaning changes require a new campaign.

Dirty local execution may be preserved as an experimental result when its state can be fingerprinted, but a production candidate must be retrained in an identifiable supported environment.

---

## 23. Retention and deletion

Default:

```text
automatic cleanup: off
```

Protected artifacts include:

- active model
- rollback-relevant previous active models
- pinned candidates
- current campaign incumbent
- unreviewed recommended candidate
- deployment-referenced model
- in-progress campaign results

Cleanup levels:

- keep all artifacts
- remove model binary but keep analysis and history
- fully remove artifacts while retaining tombstone/history metadata

The agent may recommend cleanup and estimate space recovery but may not delete.

Actual deletion requires explicit user approval.

---

## 24. Deployment export

Phase 5 provides model export, not application packaging.

Eligible source:

- approved active model only
- all production-required targets
- production feature definitions only
- Predict-compatible
- artifact integrity valid
- current required compatibility checks passed

Conceptual export:

```text
deployment_export/
├─ model.pkl
├─ manifest.json
├─ export_summary.json
└─ checksums.*
```

Exports are immutable and never implicitly overwritten.

Packaging must later select an explicit export identity. It must not silently package “whatever file was most recently written.”

---

## 25. Predict integration boundary

When the active model changes:

- update the active reference safely
- newly started Predict uses the new active model
- already running Predict keeps its loaded model
- mark reload required
- allow explicit safe reload when idle
- preserve the old loaded model if reload fails

Phase 5 implements only the safe state and reload boundary.

Detailed Predict notification, table preservation, result-comparison, and broader Predict UX belong to the next phase.

---

## 26. Contract versioning

Experiment specifications, campaign results, candidate manifests, and recommendation outputs must include explicit schema/contract versions.

New versions must:

- read supported older results
- preserve original files
- avoid silent in-place migration
- allow read-only access when resume semantics are no longer valid
- create a new campaign when current execution semantics are required
- reject unsupported future-format results rather than guessing

The CLI should be the preferred compatibility boundary for local agents.

---

## 27. Implementation slices

The exact naming and grouping may be adjusted after audit, but the implementation should preserve the dependency order below.

### Phase 5A — Audit and contract freeze

Purpose:

- reconcile this design with current owners and the previous Phase 5 proposal
- document fixed-path overwrite behavior
- choose repository-consistent storage and application boundaries
- finalize contract versions and compatibility approach
- update stale planning references

No user-facing behavior change is required in this slice.

### Phase 5B — Candidate store and active lifecycle foundation

Purpose:

- immutable candidate publication
- active reference
- Bootstrap mode
- legacy model handling
- promotion and rollback application services
- compatibility and integrity gates
- no automatic active replacement

### Phase 5C — Training result and analysis artifacts

Purpose:

- expanded structured training result
- target metrics
- RFECV output
- feature importance
- Optuna history
- preprocessing summary
- XLSX report
- optional SHAP capability
- partial/failure preservation

### Phase 5D — Train UI overhaul

Purpose:

- single-page Train workflow
- ready/running/result states
- numerical settings and progress visibility
- result comparison
- detailed/advanced/model-management/diagnostics separation
- Bootstrap and blocked-result messaging
- no agent-control UI

### Phase 5E — Promotion, rollback, export, and Predict reload boundary

Purpose:

- explicit “use this model”
- previous-model selection
- safe active change
- immutable deployment export
- running Predict reload-required state
- reload failure preserves prior loaded model

### Phase 5F — Headless experiment interface

Purpose:

- shared Experiment Specification
- single-run CLI
- campaign start/inspect/pause/cancel/resume
- machine-readable output
- GUI/CLI interoperability
- shared execution lock

Current implementation boundary (2026-07-26):

- `predictor_v3.experiment.v1` JSON is the shared GUI/headless contract.
- `apps/train/application/experiments/` owns strict resolution, persisted
  run/campaign records, campaign policy, and the workspace execution lock.
- `app_experiment.py` delegates real work to the same
  `TrainingLifecycleService`, child training job, Candidate publisher, and
  Phase 5C artifact owners used by Train GUI.
- Run and campaign records live below the existing lifecycle workspace in
  `experiments/`; callers cannot select or overwrite output paths.
- Phase 5F runs only explicit campaign experiments. Reserved early-stopping and
  recommendation-threshold fields are preserved but do not execute Phase 5G
  proposal, ranking, recommendation, or autonomous iteration behavior.
- Resume compares the saved current-version execution identity and fails closed
  when Definition/runtime, training, preprocessing, metric, specification, or
  build identity changes. Phase 5H historical adapters and immutable snapshot
  policy remain deferred.
- The first independent audit of head
  `b5ce141711c3660e2ce38b738f58f478a333d251` returned `FAIL`: campaign
  accounting used request acceptance instead of actual training start, build
  identity depended on caller `cwd` and treated unavailable identities as
  comparable, and read-only validation/resolution could publish Bootstrap.
- The bounded repair uses a child Core-training-start acknowledgement before
  consuming one iteration, derives structured build identity from the
  application repository root and blocks uncertain resume without rewriting
  saved evidence, and keeps service construction plus `validate`/`resolve`
  read-only. Only a validated `run` or `campaign-start` mutation path may invoke
  the existing explicit Bootstrap initializer.
- The second independent audit of repaired head
  `e5558e82d7ca736bb45ca71eb94ab83b71a19950` also returned `FAIL`: the child
  still acknowledged immediately before entering Core, resume renewed the
  configured attempt allowance, and identified build mismatch rewrote the
  saved campaign record. Validation run `30195511666` remains successful
  historical evidence.
- The second bounded repair moves acknowledgement into the Core optimization
  owner after configuration and data/pipeline preflight, immediately before
  RFECV/Optuna/training work. `max_attempts` is now one total iteration allowance
  across start and every resume, with a detached `campaign_retry_exhausted`
  outcome when spent. Identified mismatch, missing, lookup-failed, and uncertain
  build compatibility blocks are all detached read-only results and do not
  rewrite persisted campaign or run evidence.

### Phase 5G — Agent-assisted campaign loop

Purpose:

- default configurable 5-iteration budget
- experiment hypothesis and delta records
- bounded parameter/feature/derived-feature experiments
- incumbent and leaderboard
- recommendation artifacts
- user-only budget extension
- no production authority

Current implementation boundary (2026-07-26):

- `apps/train/application/experiments/` owns separate versioned agent campaign,
  proposal, gate, leaderboard, recommendation, and operator-extension
  contracts while retaining `predictor_v3.experiment.v1` as the shared
  resolved training contract.
- External proposals are one-step commands. The application validates the
  category and closed delta paths, resolves the full before/delta/after
  specification, and writes immutable proposal evidence before delegating to
  the Phase 5F training-start-accounted execution path.
- Accepted proposal identity, resolved evidence, stable execution key, and
  total/used/remaining attempt allowance remain pending after a pre-start
  failure. Resume executes the next persisted attempt without proposal
  resubmission; a new proposal ID or descriptive metadata cannot reset the
  same training-meaning scope.
- Agent campaign budget defaults to a configurable total of five. Restart reads
  persisted consumed/remaining allowance; proposal rejection, lock conflict,
  and pre-start failure do not consume it. Only a separate operator command can
  increase the total and must preserve approval evidence.
- Candidate gates project lifecycle/result evidence into production versus
  exploratory eligibility and closed blocking reason codes. The deterministic
  leaderboard ranks only gate-passing Candidates and keeps campaign incumbent
  distinct from Active.
- Configured guardrail and instability requirements distinguish
  `not_configured`, `passed`, `violated`, and `unresolved`; configured
  unresolved evidence fails the production gate and is retained losslessly in
  Candidate, leaderboard, and recommendation history.
- Comparable Active requires matching current data/evaluation evidence;
  unbenchmarked Active receives no improvement claim; Bootstrap selects a
  first valid incumbent without claiming production readiness.
- Recommendation artifacts are immutable approval-required history and cannot
  publish Definition, promote Active, export/replace deployment, or perform
  Phase 5H confirmation.
- Headless commands and the existing Train read-only campaign label use the
  same store. The GUI adds no agent controls, prompt, API configuration,
  promotion, or budget-extension action.
- The first Phase 5G independent audit failed at
  `029fefdd783c21f380f6d43c6bd6efe403a52b28` on resumable retry-scope loss and
  non-fail-closed configured gate evidence. The bounded repair is source
  complete on the same Draft PR and remains pending independent exact-head
  re-audit. Phase 5H remains unstarted.

### Phase 5H — Reproducibility, retention, compatibility, and closeout

Purpose:

- snapshot/evaluation/execution-contract freeze
- final confirmation gate
- retention and deletion approval
- schema-version compatibility
- full lifecycle acceptance and documentation closeout

The worker may split a slice further when repository change gates require smaller changes.

---

## 28. Global acceptance criteria

Phase 5 is complete only when the implementation demonstrates all of the following.

### Model lifecycle

- A successful training run does not overwrite the active model.
- Each completed run produces a distinct candidate or partial/failure record.
- The user explicitly promotes a candidate.
- Promotion failure preserves the previous active model.
- A previous valid candidate can be re-promoted.
- Bootstrap mode works with no active model.
- Legacy model state is handled without silent loss.

### Train UI

- A user can select data, inspect essential training settings, run training, and review results without understanding software internals.
- Preprocessing, RFECV, Optuna, and target-level metrics remain visible.
- Software-internal details are separated.
- No GUI agent-control button exists.
- Externally executed campaign results can be inspected.

### Analysis

- Target metrics, RFECV ranking, feature importance, Optuna trials, and preprocessing summaries are preserved.
- A consolidated XLSX report is produced.
- Machine-readable CSV/JSON outputs are produced.
- The user can use the outputs to decide whether to add, remove, or derive features.
- SHAP is available only as an optional Advanced capability.

### CLI and campaigns

- GUI and CLI use the same training application service and specification.
- A campaign freezes data, evaluation, and execution contract.
- Default maximum iterations is 5 but user-configurable.
- The agent cannot increase its own budget.
- Pause, cancel, resume, and bounded retry work.
- Workspace-wide single-writer locking prevents conflicting training.

### Agent authority

- The agent can run experiments and make recommendations.
- The agent cannot publish production features.
- The agent cannot promote a model.
- The agent cannot delete protected artifacts.
- Experimental derived-feature candidates are not promotable.
- Recommendations remain approval-required.

### Evaluation

- Active comparison uses the current campaign’s fair baseline evaluation.
- No-active Bootstrap comparison is valid.
- Partial target results are preserved but not promotable.
- All production-required targets pass before promotion eligibility.
- The final independent confirmation gate is enforced.
- Locked final-test results are not repeatedly fed into the loop.

### Export and Predict

- Only the approved active model can produce a deployment export.
- Export is immutable and explicitly identified.
- Phase 5 does not build an executable package.
- Running Predict is not silently hot-swapped.
- Explicit reload failure preserves the prior loaded model.

### Compatibility and retention

- Older supported campaign results remain readable.
- Results are not silently migrated in place.
- Automatic cleanup is off by default.
- User approval is required for destructive cleanup.
- Deleted artifacts leave durable history metadata.

---

## 29. Validation purpose

Validation must prove behavior and boundaries, not merely exercise code paths.

The final validation strategy should demonstrate:

- active model preservation across successful, failed, partial, and cancelled training
- atomic candidate publication
- promotion and rollback guards
- Bootstrap behavior
- GUI/CLI equivalence for the same resolved experiment
- deterministic campaign reuse of snapshot and evaluation plan
- agent loop budget enforcement
- derived-feature safety and non-promotion
- partial-target preservation
- baseline comparison correctness
- report/artifact completeness
- single-writer concurrency behavior
- pause/resume/retry semantics
- retention protection
- deployment export traceability
- Predict reload-required and failure-preservation behavior
- historical result compatibility

Targeted tests, integration tests, and representative end-to-end workflow tests should be chosen according to repository validation owners and change gates after audit.

---

## 30. Deferred implementation choices

The following are intentionally left to repository audit and implementation design:

- exact package and class names
- physical candidate/campaign directory layout
- YAML vs JSON as the primary editable format
- exact active-reference representation
- content-addressed snapshot deduplication strategy
- exact CLI command names
- exact UI widget composition
- exact database/index vs filesystem metadata choice
- exact report writer implementation
- exact lock primitive
- exact compatibility-adapter structure
- exact SHAP library and output format

These choices must not weaken the product and lifecycle decisions in this document.

---

## 31. Follow-up phase

After Phase 5 is complete and audited, the next major product phase is the Predict UI/UX overhaul.

That phase is expected to cover:

- Predict input workflow simplification
- result table and graph improvements
- batch workflow
- current-model presentation
- model-change notification design
- result preservation and comparison
- Predict Advanced surfaces
- packaging and deployment workflow integration

Phase 5 should leave reusable UI patterns and stable model-resolution contracts for that work, but must not absorb the Predict redesign itself.

---

## 32. Final decision summary

The confirmed Phase 5 direction is:

```text
Train produces immutable candidates
→ candidates include model and analysis evidence
→ user or local agent reviews results
→ local agent may run at most the user-approved bounded loop
→ local agent recommends but cannot decide
→ experimental feature changes require formal publication and retraining
→ all production targets pass an independent final confirmation
→ user explicitly selects the active model
→ Predict changes model only through a safe explicit reload boundary
→ packaging later consumes an explicitly selected immutable export
```
