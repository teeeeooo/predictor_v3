# Project Log

이 문서는 milestone decision, durable failure/lesson, process rule를
보존하는 기록입니다.

## Project Log Policy

- `project_log.md`는 milestone decision, durable failure/lesson,
  process-rule change만 기록한다.
- ordinary 작업 상세는 Git diff/commit history, focused validation,
  terminal/final output에 남긴다. compact record는 conditional trigger에서만
  작성한다.
- 장기 기억 후보는 Memory Review Gate를 통해
  `result_reports/memory/project_memory_seed.md`에서 선별 관리한다.
- report 본문이나 seed entry 전문을 `project_log.md`에 반복 복사하지 않는다.
- 기존 과거 로그는 보존하며, policy 추가 작업에서 기존 날짜별 항목을 재작성, 축약, 삭제하지 않는다.
- 새 로그를 추가하기 전 최근 2~3개 로그와 merge 가능한지 먼저 확인하고, 유사한 내용이면 중복 section을 만들지 않는다.
- 과거 로그는 `docs/archive/project_log/YYYY-MM/` capped segment archive 파일에서 heading 검색 후 필요한 범위만 확인한다.

## Historical Log Archives

- `docs/archive/project_log/2026-05/project_log_2026-05_part01_2026-05-18_to_2026-05-10.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part02_2026-05-04_to_2026-05-05.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part03_2026-05-06_to_2026-05-07.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part04_2026-05-11_to_2026-05-17.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part05_2026-05-24_to_2026-05-19.md`
- `docs/archive/project_log/2026-06/project_log_2026-06_part01_2026-06-10_to_2026-06-07.md`
- `docs/archive/project_log/2026-06/project_log_2026-06_part02_2026-06-30_to_2026-06-04.md`

> **Ordering note:** `partNN` 순서는 original `project_log.md` entry order를 보존한다. `project_log.md`는 최신 항목이 위에 오는 reverse chronological order이므로, segment filename의 date range도 reverse chronological일 수 있다. 과거 로그를 찾을 때는 파일명만 보지 말고 `rg -n "^## 2026-" docs/archive/project_log/YYYY-MM/*.md`로 heading을 검색한다.

## 2026-07-26 — Phase 5E post-merge closeout

### Decision

- Record final independent L4 audit `PASS` for accepted exact head
  `cf0b71d86a3e490799c98e8f32a0f2652d6d660b`; required validation run
  `30188757140` succeeded.
- Record PR #32 squash merge to `main` as
  `f372f5d2d5f01c96eb9b547bb5758c9c561e0836` and close Phase 5E.
- Preserve the first two independent audit `FAIL` results and repaired heads
  `5364ff7a106f27975e649d44a3b0059509dc797e` and
  `f22d6e9526bc3c31d0775123a9614b860fadbf5b` as historical evidence.
- Preserve no-hot-swap, explicit idle reload, reload-failure preservation, and
  immutable current-Active-only deployment export. Phase 5F Headless Experiment
  Interface is next and remains unstarted; Campaign, leaderboard, agent loop,
  retention, and packaging remain out of scope.

## 2026-07-26 — Phase 5E second L4 audit repair

### Decision

- Preserve the second independent audit verdict as `FAIL` at exact head
  `f22d6e9526bc3c31d0775123a9614b860fadbf5b`; validation run `30180190868`
  remains successful historical evidence, not audit PASS.
- Repair only its four findings: order every refresh observation/publication,
  prevent stale UI callbacks from starting a new unguarded refresh, route
  prediction-running reload through structured application guidance, and
  contain unexpected export exceptions as structured internal failures.
- Use one application-owned monotonic sequence for reload and refresh. Stale
  callers may receive their own result, while shared status and UI use the
  read-only authoritative current status.
- Preserve loaded runtime, Active/Candidate/history, existing exports, raw
  diagnostics, immutable publication, and all earlier Phase 5E boundaries.
- Leave Draft PR #32 open and unmerged for exact-head independent L4 re-audit;
  do not begin Phase 5F or later scope.

## 2026-07-26 — Phase 5E first L4 audit repair

### Decision

- Preserve the independent audit verdict as `FAIL` at exact head
  `5364ff7a106f27975e649d44a3b0059509dc797e`; prior validation run
  `30168662140` remains successful historical evidence, not audit PASS.
- Repair only its two findings: prevent an older reload completion from
  regressing newer installed/status state, and structure reload/export failure
  reason, preservation, next action, diagnostics, and traceback.
- Keep ordering protection in the Predict application/controller boundary.
  UI button state is not the concurrency guard, and stale UI completion is
  discarded by operation identity.
- Keep default Korean messages free of raw exception type, internal identity,
  fingerprint, and filesystem path while retaining those details in diagnostics.
- Leave Draft PR #32 open and unmerged for exact-head independent L4 re-audit;
  do not begin Phase 5F or later scope.

## 2026-07-26 — Phase 5E deployment export and Predict reload boundary

### Decision

- Keep a running Predict process bound to its actually loaded Candidate and
  Active revision; observing a newer Active only marks explicit reload required.
- Permit model replacement only while idle after a complete detached load and
  compatibility check, with a final serialized Active revision guard. Any
  preparation or race failure preserves the prior loaded bundle and identity.
- Publish checksum-verified deployment exports only from the current guarded
  Active through verified staging and a non-overwriting immutable identity.
  Export never mutates Candidate, Active, history, or source artifacts.
- Hold the worker result in an open Draft PR for independent L4 audit. Do not
  declare audit PASS, merge, or begin Phase 5F and later scope.

## 2026-07-26 — Train/Admin Phase 5D post-merge closeout

### Decision

- Preserve both independent Phase 5D audit `FAIL` results and repair records;
  no independent `PASS` is retroactively declared.
- Record user acceptance of repaired head
  `a2ea64464e595d28d58db77a28d31eac60c6a72d` and explicit merge authority.
- Record PR #31 squash merge to `main` as
  `78e9d097693c3e3b8c23d2ed18dd7e68dc1f44b0` and close Phase 5D.
- Make Phase 5E the next unstarted slice. Preserve completed promotion and
  rollback while bounding new work to immutable deployment export and running
  Predict reload-required/reload-failure behavior.

## 2026-07-26 — Train/Admin Phase 5D training-running guidance repair

### Decision

- Preserve the second independent Phase 5D L4 audit verdict as `FAIL` at
  `89e20055cc45a5c7fad59aa24a2b9d34c16e4237`. The audit confirmed four repair
  areas and identified one remaining default-state guidance blocker.
- Reuse the structured training-running promotion guidance in the normal
  disabled-button QWidget state so it states the problem, Active preservation,
  and retry-after-training action without issuing a command.
- Keep PR #31 open, Draft, and unmerged for a new exact-head L4 re-audit. Do
  not declare audit `PASS` or begin Phase 5E and later scope.

## 2026-07-26 — Train/Admin Phase 5D UI state/projection audit repair

### Decision

- Preserve the first independent Phase 5D L4 audit verdict as `FAIL` at
  `c163da7027cdfdcc1bc8f831c17f6e1285b0d6db`; do not rewrite the original
  implementation record.
- Repair only its five blockers: safe empty/error Qt table transitions, current
  lifecycle-owner compatibility, target-level comparison fidelity, complete
  persisted Advanced evidence, and structured Korean promotion rejection
  guidance.
- Keep availability inspection and final race validation in the same promotion
  compatibility owner. UI continues to avoid filesystem, serialization, hash,
  metric, and eligibility ownership.
- Keep PR #31 open, Draft, and unmerged for independent exact-head L4 re-audit.
  Do not declare audit `PASS` or begin Phase 5E and later scope.

## 2026-07-25 — Train/Admin Phase 5D Candidate/Active UI

### Decision

- Establish a Qt-free model-management application owner over the existing
  lifecycle repository, Phase 5C result contract, and Phase 5B promotion owner.
  UI code does not traverse lifecycle storage, parse JSON, deserialize models,
  compute metrics/deltas, or write Active state.
- Present Active, Candidate history, dynamic target metrics, fair/unfair/no-
  baseline meaning, blocking reasons, and Advanced evidence in the Train/Model
  surface. Preserve no-auto-active after training.
- Keep promotion explicit and revision guarded; selecting an older immutable
  Candidate uses the same promotion owner for rollback. Training, stale
  revision, corruption, and non-promotable states fail closed without changing
  Active.
- Hold audit PASS, merge, Phase 5E, CLI/Campaign, runtime reload, export, and
  retention for later authority. The Draft PR exact head requires independent
  L4 audit.

## 2026-07-25 — Train/Admin Phase 5C post-merge closeout

### Decision

- Record the final independent Phase 5C L4 audit verdict as `PASS`. Required
  validation run `30157872726` succeeded, and PR #30 was merged to `main` at
  exact head `8f74fc613d1ad6f6a1cc2c9d206543198f6d88f8`.
- Close Phase 5C with the Qt-free versioned training-result contract,
  Candidate-owned JSON/CSV/XLSX analysis artifacts, production multi-target
  training integration, lifecycle artifact/version validation, terminal failure
  evidence preservation, and separate Candidate publication versus Active
  promotion.
- Treat `joblib.load()` exception normalization as intentional fail-closed
  behavior at the serialized-model deserialization trust boundary; it was not a
  final blocker.
- Preserve all earlier audit `FAIL`, repair, and validation entries as
  historical evidence. Open Phase 5D Train/Model UI/UX as the next active but
  unstarted phase; CLI, Campaign, leaderboard, the Agent-assisted Experiment
  Loop, runtime reload, export, and retention remain later.

## 2026-07-25 — Train/Admin Phase 5C programmer-error boundary repair

### Decision

- Preserve the third independent Phase 5C L4 re-audit verdict as `FAIL`; its
  sole blocker is the programmer-error versus persisted-corruption boundary.
- Normalize malformed persisted Candidate/result analysis data through one
  explicit artifact-contract error, while allowing unexpected validator,
  parser, and helper `TypeError`/`AttributeError` to propagate unchanged from
  Candidate read and publication validation.
- Promotion must not relabel those programmer defects as blocked Candidate
  corruption. Existing Active state and failure-evidence cleanup remain
  unchanged.
- Keep PR #30 Draft and unmerged and hold Phase 5D and later experiment slices
  for another independent final exact-head re-audit.

## 2026-07-25 — Train/Admin Phase 5C canonical artifact and failure-evidence repair

### Decision

- Preserve the second independent Phase 5C L4 audit verdict as `FAIL` and
  repair only its three direct blockers on PR #30.
- Accept persisted analysis paths only in their canonical POSIX-relative
  spelling and reject aliases, traversal, outside-namespace paths, non-boolean
  `required`, invalid categories, and malformed SHA-256 values without
  coercion.
- Retain Core training evidence as an optional hash-validated Candidate artifact
  on success. Artifact, lifecycle-validation, atomic-publication, and durability
  failures preserve original target status/metrics/reasons plus publication
  failure stage/reason outside the Candidate namespace.
- Use a minimal JSON-only terminal fallback when the consolidated writer remains
  unavailable; do not represent missing CSV/XLSX as completed artifacts.
- Keep PR #30 Draft and unmerged and hold Phase 5D and later experiment slices
  for independent final exact-head re-audit.

## 2026-07-25 — Train/Admin Phase 5C result-integrity audit repair

### Decision

- Preserve the first independent Phase 5C L4 audit verdict as `FAIL` and repair
  only its five merge blockers on the existing Draft PR branch.
- Make manifest v2 Candidate read and promotion share lifecycle-owned validation
  of the exact required analysis set, artifact identity/category/required
  semantics, files, hashes, supported result version, and parsed structured
  payload. Manifest v1 remains read-only without migration.
- Require baseline identity/comparability, deltas, unavailable reasons, and
  target failure reasons to project from one result contract into JSON, CSV,
  and XLSX.
- Keep filesystem evidence/report/hash implementations in outbound adapters and
  inject them at composition. Core retains production preprocessing, target
  policy, RFECV/Optuna, evaluation, and metric ownership.
- Hold Phase 5D and every later CLI/Campaign/agent-loop slice until the repaired
  exact head receives independent L4 re-audit. This worker does not declare
  audit `PASS` or merge readiness.

## 2026-07-25 — Train/Admin Phase 5C training result and analysis

### Decision

- Establish `training_result.v1` as the Qt-free source for target metrics,
  fair-baseline comparison, RFECV, target-local XGBoost gain importance,
  Optuna, preprocessing/data-quality, artifact references, and promotion
  eligibility snapshots.
- Require new manifest v2 Candidates to own hash-verified JSON, CSV, and XLSX
  analysis before immutable publication. Continue read-only support for Phase
  5B manifest v1 without silent artifact generation or migration.
- Preserve partial, failed, cancelled, and artifact-generation-failed evidence
  in an immutable non-Candidate lifecycle namespace. None of these states may
  change Active or appear promotion-eligible.
- Keep promotion authority and compatibility revalidation in the existing
  lifecycle owner. Training completion remains Candidate publication, never
  activation.
- Hold Phase 5D Train/Model UI, CLI, Campaign, and the agent loop until an
  independent L4 audit reviews the exact Phase 5C Draft PR head.

## 2026-07-25 — Train/Admin Phase 5B post-merge closeout

### Decision

- Record the independent audit result for exact Phase 5B head
  `21b98eb38239e0100be3c3700744c69e2fdc11fe` as `PASS` evidence supplied to
  this closeout. PR #28 was squash-merged to `main` as
  `eca6addd38745dadca3b0e4f19cc259090d50e23`; no Phase 5B merge blocker
  remains.
- Close Phase 5B with immutable Candidate publication, explicit
  revision-guarded Active promotion and rollback, recovery, and Predict startup
  resolution as the lifecycle foundation. Training success does not imply
  activation, and Candidate/Active separation remains mandatory.
- Make Phase 5C Training Result & Analysis the next implementation slice:
  Candidate-linked metrics and analysis artifacts, human-readable XLSX,
  machine-readable CSV/JSON, and one Qt-free result contract shared by GUI and
  later headless execution.
- Keep Phase 5D Candidate/model-management Train/Model UI·UX next after Phase
  5C. CLI, Campaign, and the Agent-assisted Experiment Loop remain later.
- Preserve every earlier audit `FAIL`, repair, and validation entry as
  historical evidence. Windows-native and packaging validation remain unrun and
  outside this closeout.

## 2026-07-25 — Train/Admin Phase 5B Active semantic consistency repair

### Decision

- Treat the audit of malformed-Active repair head
  `af7d789dd8f7e8c8aa9a55825747571cb461c7b2` as another merge-blocking
  `FAIL`: actual payload shape/type corruption must be distinguished from an
  unrelated contract implementation `TypeError`.
- Make the shared contract validate history container and record shape before
  construction, and remove `TypeError` from repository and committed-recovery
  artifact catches. Programmer failure preserves committed recovery evidence.
- Treat the audit of semantic-consistency repair head
  `e27f924675c7c516ae23a5ec66cee6687c97022e` as another merge-blocking
  `FAIL`: committed recovery must normalize malformed and non-object Active JSON
  without deleting marker/backup evidence.
- Validate the Active payload object boundary before field access and convert
  only expected read, parse, and contract corruption during committed recovery.
  Unexpected programmer `AttributeError` remains visible.
- Treat the independent audit of head
  `7ac586a7610b02cfd1cb4b47d72bec7a70481a23` as a merge-blocking `FAIL`
  because top-level Active state and latest history were not one validated
  semantic revision unit.
- Require append-only revisions from 1, safe Candidate identities, and exact
  top-level/latest-history identity, revision, and activation-time agreement.
- Bind committed forward reconciliation to both intended revision and intended
  Candidate identity. Semantic corruption preserves marker and backup evidence
  and remains controlled recovery-required.
- Preserve the passing Qt/QProcess, non-Qt CI, narrow resolver exception,
  legacy migration, and revision-guard behavior.
- Keep Phase 5C, merge readiness, and final Phase 5B PASS on hold for a new
  exact-head re-audit. Windows-native and packaging validation remain unrun.

## 2026-07-25 — Train/Admin Phase 5B final bounded audit repair

### Decision

- Treat the audit of second-repair head
  `f944cbc6d40a36db94a599462bb2cdcc21ce2265` as another merge-blocking
  `FAIL`; all earlier validation remains historical evidence.
- Distinguish a durable committed Active revision from an indeterminate
  replacing revision before cleanup. Forward reconciliation preserves the
  committed identity, revision, and history and remains idempotent.
- Limit the shared QApplication fixture to tests that explicitly request it so
  non-Qt CI does not import PySide6.
- Convert only expected lifecycle and filesystem failures to controlled Active
  startup results; unexpected programmer errors propagate.
- Keep Phase 5C, merge readiness, and final Phase 5B PASS on hold for exact-head
  re-audit. Parent-root symlink hardening, arbitrary QCore-first widget order,
  Windows-native validation, and packaging remain outside this repair.

## 2026-07-23 — Train/Admin Phase 5B second independent-audit repair

### Decision

- Treat the independent audit of first-repair head
  `6fb25e86b1e420f18ff98b60b1dc7ac5acbf8045` as a second merge-blocking
  `FAIL`; the implementation and first-repair PASS counts are historical only.
- Anchor POSIX lifecycle lock creation to a validated root descriptor so a root
  symlink replacement cannot redirect the lock write outside the workspace.
- Use rollback-first post-rename semantics for Candidate and Active. When
  rollback cannot be made durable, retain a marker, return
  `recovery-required`, hide the indeterminate state from normal reads, and
  require deterministic repository reconciliation.
- Keep Active pointer and activation history as one atomic revisioned unit;
  preserve mandatory stale-revision guards on promotion, rollback, bootstrap,
  and legacy continuity.
- Keep one QApplication identity across canonical tests and require QProcess
  timeout cleanup to cancel, reap, and release the runner.
- Hold Phase 5C, merge readiness, and final Phase 5B PASS until a new exact-head
  independent audit. Windows-native and packaging validation remain unrun.

## 2026-07-23 — Train/Admin Phase 5B independent-audit repair

### Decision

- Treat the independent audit of PR #28 head
  `61856fe47dab2ea32aa9315c85c450b5ed5f466a` as a merge-blocking failure
  that supersedes the earlier local PASS evidence.
- Keep lifecycle filesystem writes and reads within validated regular objects
  below the exact workspace root; symlink/path-escape states fail closed without
  touching external files.
- Require an explicit current Active revision for promotion, rollback, bootstrap
  activation, and legacy continuity. No nullable or omitted guard is accepted.
- Convert known corrupt legacy-import artifacts to structured Bootstrap or
  Retraining-required outcomes while allowing unexpected programmer errors to
  remain visible.
- Arbitrate QProcess terminal signals once, with an accepted user cancellation
  taking precedence over racing process error/finished signals and genuine launch
  failures remaining failed.
- Hold Phase 5C and any merge-ready claim until the repaired exact head receives
  independent re-audit. Local repair validation is evidence for that audit, not
  final approval.

## 2026-07-23 — Train/Admin Phase 5B model lifecycle foundation

### Decision

- Replace successful fixed-path model activation with immutable Candidate
  publication beneath one default user-state workspace; publication never changes
  Active.
- Make Active a revision-guarded atomic reference with activation history.
  Promotion and rollback both revalidate the current Definition/runtime contract,
  artifact integrity, production Targets, feature order, preprocessing, and
  prediction smoke before changing the reference.
- Preserve Bootstrap as normal state. Import legacy `model.pkl` by deterministic
  hash identity without modifying the original, and create continuity Active only
  when complete current compatibility is proven.
- Make Qt-free training lifecycle orchestration the shared application boundary,
  with TrainController as adapter and QProcess limited to process execution/event
  transport. Core ML writes only to a caller-provided staging path.
- Resolve newly composed Predict processes through the lifecycle Active reference.
  Existing PredictionService instances keep their loaded immutable path; silent
  hot-swap and reload UI remain later work.
- Advance the next implementation action to Phase 5C analysis artifacts while
  preserving Train/Model UI/UX priority over CLI, campaigns, and the agent loop.

## 2026-07-23 — Train/Admin Phase 5A architecture audit closeout

### Decision

- Close the merged-main Phase 5A architecture audit with final result `PASS` and
  advance the next implementation action to Phase 5B lifecycle foundation.
- Make the 2026-07-22 Train/Model lifecycle and agent-assisted experiment design
  authoritative. Retain the earlier Phase 5 Train/Model document as supporting
  UI/UX guidance only where it does not conflict with lifecycle, CLI, campaign,
  agent-loop, migration, or implementation order.
- Store lifecycle state below the user-state root through a stable workspace
  identity. Do not use a repository absolute path as permanent identity, and
  support only one default workspace in Phase 5B.
- Register a pre-Phase-5 `model.pkl` as the initial Active model only after complete
  compatibility proof. Otherwise preserve the original and start in Bootstrap /
  Retraining required state.
- Keep Train/Model UI/UX improvement as the primary Phase 5 product goal. Treat
  lifecycle as its safety foundation and the agent-assisted loop as a later
  capability that cannot delay the UI workstream.
- Defer architecture and packaging documentation changes until the implementation
  slice that establishes the corresponding current behavior.

## 2026-07-22 — Train/Admin Phase 4 runtime generation closeout

### Decision

- Separate immutable Definition publication from process runtime application and
  make one application coordinator the staged owner for Data Definition, embedded
  Predict, Train / Model, and Data Mapping.
- Preserve all active A state until every B prepare succeeds; reject pointer,
  participant, model, and Mapping revision drift before commit. Roll back completed
  swaps on commit failure and require restart when abort/rollback cannot be proven.
- Keep dirty Mapping concrete values, baseline, and history in the Mapping owner
  behind explicit reconciliation actions. Standalone Predict independently checks
  persisted generation at startup, Refresh, and prediction boundaries and blocks
  stale execution without clearing rows or prior results.
- Close Phase 4 for repository-automated scope and advance planning to Phase 5
  only after final audit/merge. Windows-native Train/Predict/Mapping smoke remains
  pre-release verification, not claimed closeout evidence.
- Audit correction binds the reported Predict generation to one immutable actual
  inference snapshot (Derived, One-hot, ordered input, zero-fill, Target/result,
  preprocessing), makes embedded and standalone composition share that owner,
  and retains static/bootstrap paths only as compatibility facades.
- The prepare revision boundary now includes Predict cases/running state, Train
  selected file/header, Definition draft/base/controller state, and Mapping
  draft/provider state. Dirty Definition recovery is explicit, and Mapping dirty
  removal requires exact affected draft-versus-baseline value evidence.
- Final audit correction makes Predict case and ResultRow projection one atomic
  session transition. Result values migrate only by stable active Result Feature
  identity, and reverse rollback restores the exact A key/status/value/message.
- Train idle Target list, order, count, waiting metrics, and Summary now consume
  one committed registry snapshot. Running A presentation remains frozen while
  process B is explicit, then B idle presentation applies after terminal state.

## 2026-07-22 — Train/Admin Phase 4G Target registry authoring

### Decision

- Upgrade new publications to contract v4 with Target-owned Result identity,
  validated group association, identity policy, registry order, presentation order,
  and active lifecycle; keep the three model groups immutable.
- Preserve v1/v2/v3 read and rollback, existing identities, registry membership,
  use_rfe, training iteration, and final per-Target input columns. Retain legacy
  Result-name exclusions as stable compatibility evidence rather than silently
  dropping them.
- Make TrainShell select one canonical generation snapshot at process composition,
  share it with embedded Predict and Train, and freeze it again into each request.
  Definition Save cannot advance Train alone before Phase 4H coordinated cutover.
- Use one ordered training-input identity pool for policy eligibility, UI, Preview,
  validation, and runtime filtering; pin identity/key/name/use_rfe for all three
  validated model groups and include Predict visibility in presentation evidence.
  Keep `MODEL_REGISTRY` only as a generated compatibility facade and defer
  process-wide cutover, model candidate lifecycle, training activation, and
  promotion to their later owners.

## 2026-07-22 — Train/Admin Phase 4F merge closeout

### Decision

- Accept Phase 4F and its audit correction on `main` after PR #23 Ready transition,
  successful PR-head CI, and merge completion.
- Preserve contract v3, selector restore lifecycle, canonical Mapping-backed runtime
  source ownership, provider rejection, v2 rollback, and prepared Preview/Apply as
  the completed Phase 4F baseline.
- Advance the Unified Feature Manager workstream to bounded Phase 4G Target/registry
  CRUD design and implementation; keep Phase 4H cutover and model lifecycle work
  deferred.

## 2026-07-22 — Train/Admin Phase 4F audit correction

### Decision

- Treat ordinary selector assignment as an inactive reservation backed by the
  exact original Feature shape; perform takeover only on validated activation and
  restore exactly on disable/detach. Dedicated historical selectors without restore
  evidence cannot be guessed into ordinary Features.
- Keep selector eligibility and dependency impact in the core policy. Preserve
  IDU/ODU/Mapping/cascade behavior during inactive authoring and block activation
  until affected runtime relations are explicitly migrated.
- Make the canonical runtime group's `source_binding` the shared Mapping-backed
  dropdown/encoder owner, and validate all External provider identities plus
  snapshot revision before producing a prepared candidate.

## 2026-07-18 — Train/Admin Phase 4F One-hot authoring

### Decision

- Store group, selector, category, and emitted Feature relations by stable
  identity in canonical contract v3; retain explicit v2 name-relation decode for
  immutable historical generation reads and rollback.
- Separate Static Data Definition values, Mapping-owned persisted vocabulary,
  and External provider-owned identity/value. Mapping/provider snapshots are
  immutable application inputs and never hidden fingerprint inputs.
- Make category order its own domain and project only the active relative group
  block into global ML order; Predict display order remains unchanged.
- Use controlled group/category commands with exact prepared Preview/Apply,
  atomic selector/emitted-Feature transitions, dependency guards, and inactive
  Add/Duplicate defaults.
- Remove Predict's fixed selector/group table. Encoding and selector options
  consume the same immutable canonical runtime snapshot, while Train retains the
  canonical emitted-header projection.
- Preserve current `warn_all_zero`/`all_zero` behavior and five emitted headers.
  Inactive authoring is publishable; active semantic changes require the existing
  retraining/migration boundary.
- Keep concrete Mapping mutation, dirty Mapping reconciliation, process-wide
  runtime cutover, Target/registry CRUD, training, and model promotion outside
  Phase 4F.

## 2026-07-18 — Train/Admin Phase 4E restricted Derived authoring

### Decision

- Store canonical Derived operands as Feature/Derived stable identities and use
  explicit versioned decoding for historical name-based generations.
- Restrict authoring to `safe_ratio` with constant finite `zero_value`; keep the
  existing eight outputs, `0.0` behavior, and deterministic compatibility order.
- Derive execution order from one validated dependency DAG and centralize Train/
  Predict formula semantics in one pure shared evaluator.
- Use one core policy for Derived operand eligibility across commands, raw contract
  validation, and application presentation; Result/Target and post-model outputs
  are never valid operands, including for inactive authoring.
- Treat role and value source as one runtime shape. Only `input/manual`,
  `auto/mapping_lookup`, and `one_hot_feature/one_hot` can provide Feature operands;
  model-input flags cannot make a mismatched or post-evaluator source eligible.
- Project requested Derived outputs to deterministic transitive base Feature inputs
  from the same immutable evaluator snapshot. Train and Predict share missing-input
  classification, while Predict no longer owns a fixed six-name dependency list.
- Default Add/Duplicate to inactive, distinguish canonical Derived semantics from
  active model compatibility, and preserve retraining/migration Save guards for
  activation or active semantic changes.
- Keep Phase 4H runtime generation cutover, mapping values, model artifacts,
  training, promotion, One-hot, and Target CRUD outside Phase 4E.

## 2026-07-18 — Train/Admin Phase 4C+4D audit correction

### Decision

- Protect Basic Features only from evidence supplied by actual fixed-string or
  import-time consumer owners; canonical presence, visibility, and role do not
  imply a protected dependency.
- Match canonical rows by stable identity whenever present and reserve key
  fallback for explicit identityless legacy compatibility rows, preventing
  Remove/same-key Add from inheriting old Feature or Mapping identities.
- Prepare identity-allocating commands once in the application layer and apply
  the exact previewed transition only while controller revision and source
  generation remain current.
- Expose affected Feature/reference identity, owner/code, automatic migration,
  blocker resolution, compatibility, fingerprint, retraining, and Save evidence
  as application data; keep the View presentation-only.
- Treat exact controlled Remove and Add as independent lifecycle evidence during
  Save validation instead of comparing same-position rows. Require lifecycle
  evidence to match baseline/current identity set differences so direct identity
  replacement and removed-identity reuse remain blocked.

## 2026-07-17 — Train/Admin Phase 4C+4D Feature Manager

### Decision

- Use immutable stable Feature identity for selection, dependency resolution,
  Rename, and persistence; Predict key, ML name, and label remain mutable aliases.
- Route every basic lifecycle mutation through atomic domain commands and keep
  Predict display ordering independent from ordered ML contract ordering.
- Define Rename as one optional atomic label/Predict-key/ML-name payload that
  requires at least one identifier change; label-only changes remain Edit.
- Permit only identity-safe reference updates. Keep fixed-string/import-time,
  Derived, One-hot, Target/registry, training-header, and model-compatibility
  changes blocked until their approved migration or retraining boundary.
- Preserve Data Mapping concrete values and model artifacts. Save accepted drafts
  only through the Phase 4B generation transaction and keep stale/failed drafts.
- Advance to restricted Derived authoring in Phase 4E after this slice merges;
  Windows native Feature Manager smoke remains a pre-release verification item.

## 2026-07-17 — Train/Admin Phase 4B persistence foundation

### Decision

- Adopt `config/data_definition/manifest.json` as the deterministic bootstrap
  seed for the versioned canonical Definition contract and publish runtime state
  only as immutable generation bundles plus one atomic active pointer.
- Generate Predict, ordered ML, Derived, One-hot, Target/registry, and Mapping
  requirement projections from one validated manifest and retain scoped model-
  compatibility fingerprints distinct from Predict presentation changes.
- Keep `mapping.json`, model artifacts, promotion, and runtime cutover outside the
  Definition transaction. Preserve protected ML/fixed-string Save blockers until
  explicit consumer migration; only a fully generated presentation-compatible
  projection path may replace the legacy parity blocker.
- Compose generation persistence from the production Train root through an
  application repository port. Bind every editable draft to its source
  generation and serialize parent validation with active-pointer replacement so
  stale writers cannot publish over a newer generation.
- Derive bootstrap and candidate identities from the same complete semantic
  manifest hash. Enforce Predict, ordered ML, Derived DAG, One-hot category, and
  Target presentation ordering in projections and whole-contract validation.
- Use native POSIX/Windows process file locks around parent validation through
  pointer replacement, and require callers to choose canonical repository or an
  explicit legacy schema path. Keep active runtime generations in per-user state
  rather than source-controlled config, and validate Predict display order as a
  unique bounded ordering field across active and inactive Features.
- Advance to Phase 4C only after Phase 4B audit and merge.

## 2026-07-17 — Train/Admin Unified Feature Manager phase insertion

### Decision

- Preserve completed Phases 1–3 and PR #16 history, but define the completed
  Phase 3 scope as the table-first Data Definition UX foundation.
- Make Phase 4 the proposed/current Unified Feature Manager workstream for
  complete Predict/ML Feature lifecycle and ordering, Derived/One-hot/Target
  authoring, transaction-safe multi-contract persistence, and live owner refresh.
- Move the unstarted Train/Model and Shell UX design to Phase 5; start it only
  after Phase 4 stabilization and a fresh dynamic Feature/Target contract audit.
- Keep Data Mapping as concrete value owner, Train as explicit training-execution
  owner, and Predict as saved-contract/compatible-model consumer. Exclude
  automatic retraining, automatic model activation, and Predict internal redesign
  from Phase 4.
- Keep current ML-projection-changing Save guards until Phase 4 approves and
  implements a persistence and compatibility migration/rollback boundary.
- Require one immutable persisted contract generation and coordinated consumer
  preflight/cutover; mixed-generation normal operation is forbidden and disk Save
  success remains distinct from runtime activation success.
- Bind every training run/result/artifact to its immutable start-generation
  Feature/Target/preprocessing snapshot. Definition Save does not retroactively
  alter an active run, and stale artifacts are not current-compatible by default.
- Preserve dirty Data Mapping drafts and expose pending requirement updates rather
  than silently reloading them. Separate static, mapping-backed, and external
  One-hot vocabulary owners.
- Keep initial Target CRUD limited to validated existing model-group association
  and target-level policies; new model groups and model-level training policy
  require a separately approved advanced contract.
- Separate run/generation-scoped candidate artifacts from the active model.
  Training completion cannot replace the active model; only validated explicit
  promotion by the artifact/model owner may do so, and failure preserves the
  previous compatible model.
- Limit atomic generation cutover to required owners inside one TrainShell
  process. Standalone Predict and other processes independently detect persisted-
  generation mismatch at startup/execution/reload boundaries and block new work
  when safe reload cannot succeed.

## 2026-07-16 — Train/Admin Phase 4 Train UX direction

### Decision

- Confirm Phase 3 is complete and merged through PR #16; remove the Phase 3 merge
  blocker from active planning.
- Make Phase 4 user-centered around `select training data → train → check
  progress → review results`.
- Run schema, feature, mapping, and compatibility checks automatically inside the
  workflow. Keep normal technical details out of the default surface; show an
  actionable user message first for errors and reserve details for Diagnostics or
  logs.
- Use the existing Train/ML safe defaults for ordinary training; optional or
  technical overrides remain behind Advanced settings and do not become required
  to start a supported default run.
- Separate authoritative training-start blockers from non-blocking warnings and
  post-training artifact/Predict blockers. Existing model, restart, mapping, and
  Predict readiness must not become Start prerequisites without an owner-contract
  basis.
- Center results on overall success, target-level R², optional MAE/RMSE, Optuna
  status and best trial/score when applicable, model-save status, elapsed time,
  and Predict availability.
- Treat the current-state audit and design finalization as the next Phase 4 work;
  preserve existing Data Definition, Data Mapping, Train, Predict, ML,
  persistence, and public-contract owners.

## 2026-07-16 — Train/Admin Data Definition UX Phase 3 closeout

### Decision

- Approve Phase 3 Slices 3A–3F and all audit corrections as one coherent Data
  Definition UX milestone; PR #16 was merged to `main`.
- Close the table-first Definition Inventory, controlled Add/Edit, guarded
  schema-only Save, impact/blocker workflow, saved-only Data Mapping handoff and
  coverage, keyboard/accessibility polish, and bounded native evidence while
  preserving their established owners.
- Keep `config/predict/schema.csv` as the canonical Data Definition write target
  and `config/ml/features.csv` as compatibility/parity-only. Projection-changing
  ML edits remain intentionally blocked without an approved projection writer.
- Accept visible-Cocoa/programmatic native evidence without claiming physical
  interaction; the known unsafe AppKit accessibility table-click path remains
  unused. Deferred Phase 2 native interaction remains separate.
- Keep production mapping completeness, training data, model quality, and
  production readiness company-local. No production config, mapping data,
  training data, protected fixture, or model artifact changed.
- Phase 3 closeout CI passed and the user merge completed; Phase 4 starts only
  from confirmed merged `main` on a separate branch and Draft PR after separate
  instruction.

## 2026-07-15 — Train/Admin Data Mapping UX Phase 2 closeout

### Decision

- Accept Phase 2 Slices 2A–2E and audit corrections at approved head
  `4fe580e1fa76a7af1f51c80e4cef163705ebe648`; PR #15 is the user merge target.
- Close code and repository automation with seven-group editing, spreadsheet
  CRUD/Undo, validation/dirty/Save/Reload, deterministic exchange export,
  exact-header canonical import, semantic row-order no-op, and best-effort
  rollback contracts intact.
- Treat incomplete Slice 2B+2C native interaction and Slice 2D+2E native visual
  evidence as deferred acceptance under the recorded AppKit and locked-desktop
  blockers. No new PNG or physical-interaction claim is made.
- Keep protected mapping data unchanged and do not infer real mapping
  completeness, model quality, or production readiness from fixtures/mock data.
- Mark PR #15 Ready for review after the closeout commit and CI succeed. The
  user performs merge; Phase 3 starts only from confirmed merged `main` on a
  separate branch and Draft PR after a current-state audit.

## 2026-07-14 — Train/Admin Mapping/Data Foundation Phase 1 closeout

### Decision

- Complete Slices 1A–1D and final corrections for repository-automated scope;
  final audit is approved and PR #14 was merged to `main`.
- Use the strict legacy bootstrap projection as a repository-only populated
  mapping fixture; never install it as production `data/mapping.json`.
- Keep Data Definition as dynamic mapping column/type/required owner and Data
  Mapping as value/persistence owner. Dynamic condenser payload attributes do
  not participate in conditional F&T/PFC identity.
- Apply that definition-backed payload contract to Refrigerant and Expansion
  without changing their key-based Predict options. Persist booleans as
  canonical JSON booleans, reject non-finite mapping numbers, and keep
  undeclared raw payload keys hidden from editor schema.
- Preserve undeclared runtime row payload from the current editor row backing
  data across unrelated Save/reload and key rename while overlaying only visible
  definition-backed values. Hidden payload is not review-exported and is
  removed with its row rather than recovered from historical source keys.
- Pair DEV selector metadata with unchanged ML numeric/one-hot training headers
  and fail fast when schema, mapping options/combinations, or resolved mock
  values diverge.
- Treat all fixture and mock success as structural workflow evidence only. Real
  mapping completeness, training data, model quality, and production readiness
  remain company-local validation work.
- Start Phase 2 only from merged `main` on a separate branch after separate
  instruction.

## 2026-07-13 — Active non-AHRI Calculator core refactor closeout

### Decision

- Preserve EN 14825, ISO 16358, and KS C 9306 public facade imports, methods,
  config attributes, routes, results, diagnostics, rounding, exceptions, and
  all official/golden expected values.
- Keep config, point resolution, performance curves, seasonal loops, and result
  assembly in standard-local private owners. ISO and KS CSPF/HSPF engines remain
  separate, and KS does not call the ISO public facade.
- Keep Brazil as capability-owned composite policy and AS/NZS as a disabled
  compatibility path. Resolve profile resources statically without repo-cwd
  dependence, scanning, or plugin discovery.
- Do not commonize cross-standard numeric helpers until formula, units,
  boundary, rounding, and exception semantics are all proven identical.

## 2026-07-12 — AHRI SEER2/HSPF2 core refactor closeout

### Decision

- Preserve `ahri_seer2.py` and `ahri_hspf2.py` as the stable public facades used by Calculator, capability, dispatcher, and ML envelope routes.
- Keep variable-capacity SEER2, variable-capacity HSPF2, and legacy HSPF2 v2 behind separate private owners; future two-stage/triple-capacity formulas must be sibling engines rather than branches added to the current formula bodies.
- Treat the existing user-confirmed expected results as official-calculator golden and the canonical deep-result fingerprints as structural characterization only. No formula, rounding, config, result/diagnostics schema, application scaling, or exception contract changed in this refactor.

## 2026-07-12 — Calculator table-family migration closeout

### Decision

- Completed the active Tk Calculator migration to three explicit table
  families: Editable Matrix, Compact Result Grid, and Scrollable Data Table.
- Shared visual policy and primitives now cover all active single, batch,
  compact-result, and detail tables while existing controllers, profile
  schemas, calculations, status meaning, lifecycle, and export contracts stay
  with their established owners.
- Small fixed results no longer use Treeview; the sole active Treeview remains
  the large `BinTraceTable` detail surface through the shared style adapter.
- EN14825 section hotspots remain unchanged ownership-wise; future new
  responsibilities require a split audit rather than reopening the table-family
  decision.
- Final correction keeps top/nested Notebook tab geometry fixed across
  selection, removes Python class-identity from AHRI/Korea visibility checks,
  and passes the full Tk Calculator suite without the prior order failure.
- Every active Single result surface now exposes Copy and Excel-friendly CSV
  actions while result owners retain their native payloads and detail/Batch
  export paths remain separate. SCOP composes export directly from active
  visible climate surfaces rather than its hidden compatibility text model.
- The user completed final GUI review and approved the feature branch for
  integration to `main`; the Calculator table architecture workstream is
  closed with no remaining merge blocker.

## 2026-07-11 — Clean/hexagonal desktop refactor

### Decision

- Preserve calculator and fixed-artifact ML numeric behavior while removing
  retired calculator code, stale legacy tests, dead Predict split-table UI, and
  the superseded Train Feature Catalog Manager UI.
- Keep `app_train.py` and `app_predict.py` separate and thin. Runtime-neutral
  ports, DTOs, and usecases are assembled in composition roots; PySide runners
  own toolkit/process lifecycle.
- Keep `config/ml/features.csv` and the core ML feature catalog as compatibility
  contracts without adding incomplete ML functionality. Arc 15 Data Definition
  remains the active Train/Admin schema surface.
- Use shared semantic visual tokens and screen-aware window policy, hidden-first
  calculator startup, multi-monitor-safe dialog placement, and two-axis batch
  table scrolling as the conservative desktop UX baseline.

## 2026-07-10 — Agent harness report and memory lifecycle redesign

### Decision

- Ordinary tracked-file changes no longer require result reports.
- Durable compact records are limited to contract/policy/migration/manual
  evidence and non-obvious regression triggers, and are committed with their
  source changes.
- New records use date-based final paths plus `REPORT_INDEX.md`; terminal
  output owns commit hash and push status.
- Memory Review Gate replaces active-count/summary/archive cleanup as the
  memory-update checkpoint.
- Existing archive and summary reports now reside under read-only
  `result_reports/legacy/` while historical bodies remain unchanged.
- Stale generated reference-map/read-budget layers were retired; targeted
  owner/reuse search plus objective structure and staged gates remain.
- `ACTIVE_DOCUMENTS.md` is an owner-route map; child-document completeness
  belongs to local indexes and filesystem search.
- The active design root now contains only current/governing/future-unabsorbed
  decisions; 45 historical records are under an indexed legacy boundary.
- The audited harness branch was merged into `main` after pre-merge corrections.

## 2026-07-06 — Pre-Arc 15 config/mapping source audit decision

### Decision
- Do not proceed directly from Arc 14D-R into Arc 15 real dataset readiness or a
  `Unified Data Definition Manager` direction.
- First run a Pre-Arc 15 audit of `config/ml/features.csv`,
  `config/predict/schema.csv`, the existing legacy mapping fixture
  `tests/fixtures/mapping/mapping_tables_legacy_wide.csv`, and Data Mapping
  Manager output relationships.
- The user clarified that the legacy mapping CSV was already in the repo, while
  real training CSV data is still outside the repo on the user's local PC.
- Do not decide whether the current ML feature contract and Predict schema CSV
  split is final design or duplication debt until that audit is complete.

## 2026-07-03 — Arc 14/15 numbering sync

### Decision
- Renumbered Data Mapping Manager / Mapping Update Execution as Arc 14 because
  `app_train.py` Data Mapping is still a placeholder; moved ML catalog-aligned
  real dataset readiness audit to Arc 15.

## 2026-07-03 — Arc 13.5A feature catalog correction closeout

### Decision
- Completed Arc 13.5A Feature Catalog Manager correction: dropdown UX bugfix,
  user-confirmed GUI smoke, narrowed ML model compatibility fingerprint, and
  active payload dedup are closed out.
- Active report lifecycle cleanup is complete in
  `result_reports/legacy/summaries/673_summary-arc13-5a-feature-catalog-manager-closeout.md`.
- No Arc 13.5A blocker remains; next action is Arc 14 Data Mapping Manager /
  Mapping Update Execution after the Arc 14/15 numbering sync.

## 2026-07-02 — Arc 13.5 feature catalog editor closeout

### Decision
- Completed Arc 13.5 Feature Catalog Editor Bridge for automated scope.
- `app_train.py` now exposes a top-level `Feature Catalog` Train/Admin tab with
  catalog/project consistency validation, read-only review, Excel-safe
  UTF-8-SIG export, whitelisted edit fields, validation-gated save, and
  canonical UTF-8 without BOM safe-write.
- Direct `config/ml/features.csv` editing is no longer the default user
  workflow; it remains an advanced/developer fallback for row add/delete or
  recovery work.
- Arc 14 real dataset readiness audit is the next recommended arc.
- Real desktop GUI manual smoke remains pending; automated Qt validation used
  offscreen mode.

## 2026-07-01 — Calculator Sub-Arc KOREA notebook entry closeout

### Decision
- Completed the bounded KOREA calculator notebook sub-arc before Arc 13.5.
- KOREA is now a top-level calculator tab with CSPF/HSPF single calculation,
  midpoint guide tables, batch table dialogs, and official-result detail views.
- KS C 9306 core formula/config/profile/public result contracts and golden
  expected values were preserved.
- Next near-term action returns to Arc 13.5 Slice 0 Feature Catalog Editor
  Design Gate.

## 2026-07-01 — Arc 13.5 feature catalog editor direction

### Decision
- After Arc 13 closeout, practical review found that opening `features.csv` in
  Excel can display Korean labels incorrectly because Excel may not
  automatically detect UTF-8 CSV encoding.
- The preferred user workflow is not direct CSV editing in Excel or Numbers.
  Arc 13.5 should design the feature catalog workflow around an
  `app_train.py` Feature Catalog viewer/editor surface.
- CSV export remains useful for storage, sharing, and Excel/Numbers review, and
  the implementation design should evaluate an export encoding policy such as
  UTF-8-SIG.
- Arc 14, the real catalog-aligned dataset readiness audit, is deferred until
  after Arc 13.5 viewer/editor/export/save work.
- The Calculator Sub-Arc - KOREA Notebook Entry is the next action before Arc
  13.5 starts.

## 2026-06-30 — Arc 13 feature catalog closeout

### Decision
- Arc 13 is complete for automated scope. `config/ml/features.csv` is the ML
  feature contract; `ml_name` is the raw training header and internal ML name.
- ML feature exports, predictor ML-visible columns, one-hot lists, training
  header runtime guard, inference zero-fill policy, and registry/catalog
  consistency guards now share the catalog contract.
- Arc 13 reports 624-632 are covered by
  `result_reports/legacy/summaries/633_summary-arc13-feature-catalog-closeout.md` and
  archived.
- Next recommended work is an ML catalog-aligned real dataset readiness audit.

## 2026-06-29 — Arc 12 calculator application boundary closeout

### Decision
- Arc 12 Calculator UI/Application Boundary Correction is complete for
  automated scope.
- ISO/ISEER, SASO T3, Hong Kong CSPF/HSPF, EN14825 SEER/SCOP, and AHRI
  SEER2/HSPF2 now route calculation orchestration through
  `apps.calculator.application` / `apps.calculator.adapters` boundaries or thin
  UI shims.
- Matching batch paths reuse application usecases/adapters where applicable,
  and guard tests now prevent completed UI/batch surfaces from importing the
  core dispatcher or mutating calculator config.
- No calculator formulas, config semantics, profile IDs, fixtures/golden
  expected, or public result dict contracts changed.
- Arc 13 ML Pipeline Stabilization is unblocked as the next recommended arc.
