# 004_migrate-ml-training-artifact-guardrails

## Goal
- Move remaining ML/training architecture blockers from `AGENTS_FULL.md` into the active owner document.
- Keep `AGENTS_FULL.md` unchanged in this turn.

## Scope
- Add a concise ML training/model artifact guardrail section to `docs/architecture/project_architecture.md`.
- Use `AGENTS_FULL.md` only as source reference for the remaining blocker rules.
- Do not start the next archive cleanup phase.

## Non-goals
- No `AGENTS_FULL.md` reduction, deletion, archive move, stale migration note cleanup, or obsolete report format cleanup.
- No `AGENTS.md`, `AGENT_TASK_ROUTER.md`, or `docs/knowledge/*` edits.
- No code, tests, model artifact, training run, or test run.

## Verification
- Ran `git diff -- docs/architecture/project_architecture.md`.
- Ran `git diff --name-only` before report creation and confirmed the source change was only `docs/architecture/project_architecture.md`.
- Checked `AGENTS_FULL.md`, `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `docs/knowledge`, `core`, `tests`, and `model` had no source diff.
- Ran `git diff --check -- docs/architecture/project_architecture.md`.
- Did not run tests by request.

## Task Results

### task 1 결과
- 수정 파일: `docs/architecture/project_architecture.md`
- 수정 내용:
  - Added `### ML 학습 및 모델 artifact 가드레일`.
  - Documented `model.pkl` single artifact contract through `MODEL_FILE`.
  - Documented `preprocess_version` or equivalent preprocessing version guard.
  - Documented `core/trainer.py` / `core/predictor.py` train-predict runtime import boundary.
  - Documented independent target-level XGBoost model and independent RFE feature-set guardrail.
  - Linked cooling/heating or target-specific feature boundaries to `MODEL_REGISTRY.target_rules` and train/predict feature alignment.
- 검증 결과: OK. Source diff was limited to `docs/architecture/project_architecture.md`; tests were not run.
- OK/NG: OK

## Test Results
- Not run by request. This was a docs-only architecture guardrail migration.

## Changed Files
- `docs/architecture/project_architecture.md`
- `result_reports/active/004_migrate-ml-training-artifact-guardrails.md`

## Known Failures / Risks
- `AGENTS_FULL.md` still contains the stale migration note and obsolete report format; those were explicitly out of scope.
- This change records architecture guardrails and does not verify runtime implementation behavior.
- `project_log.md` was not updated because this migrated existing `AGENTS_FULL.md` rules into the owner document rather than introducing a new architecture decision, and the requested scope was limited.

## Next Suggested Action
- In a separate user-approved phase, clean up stale `AGENTS_FULL.md` archive notes and obsolete completion-report wording.

## Scope Compliance
- `AGENTS_FULL.md`: not modified, deleted, shrunk, or moved
- `AGENTS.md`: not modified
- `AGENT_TASK_ROUTER.md`: not modified
- `docs/knowledge/*`: not modified
- code: not modified
- tests: not modified or run
- model artifact: not generated or modified
- training: not run
- archive phase: not started
- result report: created as workflow artifact

## Commit / Push
- source/docs commit: `4a77871`
- report commit: committed separately by `report: record ml training guardrail migration`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
