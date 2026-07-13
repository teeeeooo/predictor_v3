# Work Plan

## Purpose

- Own the current slice, one next action, blockers, constraints, and deferred work.
- Keep phase, milestone, and Standard Calculation direction in `project_brief.md`.
- Keep milestone decisions and durable lessons in the log; keep conditional
  evidence in records and structural triggers in `docs/REFACTOR_PLAN.md`.

## Update Rule

- This file is a near-term execution board, not a roadmap or task log.
- Update it only when the current slice, next action, blocker, constraint, or
  hold state changes.
- Do not append report lists, terminal output, or completed-action history.
- Add a Session Handoff only when the user explicitly requests one.

## Current Slice

Production ML Readiness is the active workstream. The Calculator UI workstream is
closed after stabilizing initial ISO/KS result surfaces and selected-child sizing
for EN/AHRI nested notebooks without changing calculator formulas, schemas, or
packaging behavior.

## Next Action

Start the catalog-aligned real dataset readiness audit from the ML/Predictor owner
documents, then define the first bounded implementation slice from available
dataset and trained-model evidence.

## Active Blockers

None.

## Active Constraints

- Preserve the feature catalog and runtime mapping contracts.
- Keep Cooling and Heating models independent, including monotone constraints.
- Do not infer production readiness from mock smoke or absent model/data evidence.

## Deferred / Hold

- ML validation gap: `model/model.pkl` is absent and training CSV is external;
  mock smoke cannot validate accuracy, trends, importance, or model quality.

## Minimal Anchors

- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
