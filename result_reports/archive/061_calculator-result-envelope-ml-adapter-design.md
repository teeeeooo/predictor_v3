# 061 Calculator Result Envelope ML Adapter Design

## Goal

Define and record the calculator result envelope / ML adapter boundary before any ML or inverse-search implementation resumes.

## Scope

- `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`
- `docs/architecture/project_architecture.md`
- `docs/WORK_PLAN.md`
- `docs/REFACTOR_PLAN.md`
- `docs/README.md`
- `ACTIVE_DOCUMENTS.md`
- `project_brief.md`
- `project_log.md`

## Non-goals

- No ML / inverse-search implementation.
- No calculator public API or return schema change.
- No region config schema or semantics change.
- No AGENTS/router workflow rule change.

## Changed Files

- `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`
- `docs/architecture/project_architecture.md`
- `docs/WORK_PLAN.md`
- `docs/REFACTOR_PLAN.md`
- `docs/README.md`
- `ACTIVE_DOCUMENTS.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/061_calculator-result-envelope-ml-adapter-design.md`

## Verification

- `git diff --check`
  - passed before source commit
- `rg -n "calculator-result-envelope-ml-adapter|PredictedPointsEnvelope|CalculatorResultEnvelope|AHRI SEER2 selector|audit_2 immediate" ACTIVE_DOCUMENTS.md docs project_brief.md project_log.md`
  - confirmed the new design record and managed-doc links

## Task Results

- Added a Design Gate Summary defining:
  - `PredictedPointsEnvelope`
  - `CalculatorInputEnvelope`
  - `CalculatorResultEnvelope`
  - `RankingCandidateEnvelope`
- Updated architecture docs to make the adapter/envelope flow the source boundary for ML / inverse-search restart.
- Updated work/refactor plans so completed UI audit and AHRI selector cleanup are no longer listed as pending next work.
- Updated `project_brief.md`, `ACTIVE_DOCUMENTS.md`, `docs/README.md`, and `project_log.md` to preserve handoff and document ownership.
- Left `AGENTS.md` and `AGENT_TASK_ROUTER.md` unchanged because this task did not introduce a new agent workflow rule.

## Known Risks

- The design intentionally does not implement the adapter. The next code slice must still add unit tests and schema-coupling guards.
- The current Calculator UI still lacks a discovered calculate button/result display connection; that remains a separate UI follow-up.

## Commit / Push

- Source commit: `cadc65c` (`docs: define calculator result envelope boundary`).
- Report commit: this commit (`report: record calculator envelope adapter design`).
- Push: deferred until final objective push.
