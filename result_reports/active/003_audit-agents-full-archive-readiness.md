# 003_audit-agents-full-archive-readiness

## Goal
- Audit whether `AGENTS_FULL.md` is ready to be archived.
- Identify any rules that still exist only in `AGENTS_FULL.md` and lack an active owner document.
- Keep the audit read-only for source docs and code.

## Scope
- Read and compare `AGENTS_FULL.md` against active owner candidates:
  - `AGENTS.md`
  - `AGENT_TASK_ROUTER.md`
  - `docs/PACKAGING.md`
  - `docs/architecture/project_architecture.md`
  - `docs/knowledge/hvac_ml_feature_engineering.md`
  - `docs/knowledge/hvac_ml_data_quality.md`
  - `docs/knowledge/physical_constraints_for_ml.md`
  - `docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md`
  - `docs/ahri210240/ahri210240_notes.md`
  - `docs/README.md`
  - `README.md`
- Create this result report only.

## Non-goals
- No source document edits.
- No `AGENTS_FULL.md` deletion, shrinking, or archive move.
- No owner document edits.
- No code or test edits.
- No tests.

## Verification
- Confirmed pre-audit git status was clean.
- Confirmed existing result report max number was `002`; this report uses `003`.
- Compared `AGENTS_FULL.md` section content against owner documents using targeted reads and `rg`.
- Did not run tests because this is a read-only documentation audit.

## Task Results

### task 1 결과
- 확인 파일:
  - `AGENTS.md`
  - `AGENTS_FULL.md`
  - `AGENT_TASK_ROUTER.md`
  - `docs/PACKAGING.md`
  - `docs/architecture/project_architecture.md`
  - `docs/knowledge/hvac_ml_feature_engineering.md`
  - `docs/knowledge/hvac_ml_data_quality.md`
  - `docs/knowledge/physical_constraints_for_ml.md`
  - `docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md`
  - `docs/ahri210240/ahri210240_notes.md`
  - `docs/README.md`
  - `README.md`
- archive readiness 판단: **not ready for full archive yet**. Most domain rules now have active owners, but several implementation/agent rules still appear to be exclusive to `AGENTS_FULL.md` or only partially represented elsewhere.
- 남은 blocker:
  - `model.pkl` single-model artifact rule and `preprocess_version` verification guard are present in `AGENTS_FULL.md` but no active owner was found in the audited docs.
  - `core/trainer.py` as `app_train.py`-only and explicit `core/predictor.py` import prohibition for `core/trainer.py` is only partially covered by current Train/Predict separation and `core/predictor.py` learning-library import ban.
  - ML rule for independent XGBoost model plus independent RFE feature set per target is only partially covered. `MultiOutput` ban and target-specific feature boundaries are covered, but RFE-specific ownership was not found.
  - `AGENTS_FULL.md` still contains an obsolete completion report format that conflicts with the current Result Report Workflow. This should be retired or marked historical before archiving.
  - `AGENTS_FULL.md` Migration & Archive Note still says ML/UI/Packaging/AHRI detailed rules are not yet moved. That note is now stale for several areas and should be reconciled before archive.
- 이미 이관 완료된 항목:
  - Packaging: `docs/PACKAGING.md` explicitly states it is the owner for packaging rules from `AGENTS_FULL.md` and covers clean deploy env, `venv_deploy`, DLL/binaries mapping, `.spec` considerations, and crash logging.
  - UI guardrails: `AGENTS.md` and `docs/architecture/project_architecture.md` cover `QTableView + QAbstractTableModel`, `setCellWidget` ban, delegate use, state colors, `blockSignals` try/finally, and calculator boundary.
  - ML feature/data quality: `AGENTS.md`, `docs/knowledge/hvac_ml_feature_engineering.md`, `docs/knowledge/hvac_ml_data_quality.md`, and `docs/knowledge/physical_constraints_for_ml.md` cover DataFrame column-name preservation, MultiOutput ban, target leakage, validated derived feature families, fail-fast vs review flags, vectorized transformation preference, and monotonicity caveats.
  - KS C 9306 safety rules: `AGENTS.md` routes KS edits to KS notes, and `ks_c_9306_dev_notes.md` covers `ROUND_HALF_UP`, declared load source, `ks_intersection`, no common fallback, production config vs fixture split, and KS-only branch isolation.
  - AHRI HSPF2 scope: `docs/ahri210240/ahri210240_notes.md` covers AHRI 210/240 HSPF2 v3 scope, non-ducted single-split variable-capacity Region IV focus, unsupported extensions, fractional vs absolute bin hours, `BL(t_j)` source, and critical implementation notes.
  - General active rules: `AGENTS.md` and `AGENT_TASK_ROUTER.md` now own active read policy, task routing, result report workflow, commit/report behavior, and archive-move approval guardrails.
- 다음 추천 작업:
  - Move or explicitly retire the remaining exclusive `AGENTS_FULL.md` rules before archiving.
  - Best next small docs task: add/confirm owner wording for model artifact/preprocess version, trainer/predictor import boundary, and RFE-specific ML training boundary.
  - Then update `AGENTS_FULL.md` Migration & Archive Note or move `AGENTS_FULL.md` to archive with user approval.
- OK/NG: OK

## Test Results
- Not run by request. This was a read-only audit.

## Changed Files
- `result_reports/active/003_audit-agents-full-archive-readiness.md`

## Known Failures / Risks
- Source docs were not modified, so the identified blockers remain unresolved.
- This audit did not inspect every possible code path; it checked the requested owner docs and closely related documentation maps.

## Next Suggested Action
- Create a small follow-up docs task to assign owners for the remaining exclusive rules, then re-run archive readiness.

## Scope Compliance
- source docs: not modified
- `AGENTS_FULL.md`: not modified, deleted, shrunk, or moved
- owner docs: not modified
- code: not modified
- tests: not modified or run
- archive move: not performed
- unrelated refactor: not performed
- result report: created as required by current workflow

## Commit / Push
- source/docs commit: source change 없음
- report commit: committed separately by `report: record agents full archive audit`; final hash is reported in terminal/final summary because a commit cannot contain its own final hash.
- pushed branch: `main`
