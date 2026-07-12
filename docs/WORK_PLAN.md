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

PR #11 audit corrections are complete on
`chatgpt/ahri-multicapacity-core-gui`. In addition to the earlier formula,
seasonal-total, validation, and overlay corrections, Dual-stage and Triple
Northern H3Low requiredness now follows the AHRI Table 7 footnote 7 boundary:
H3Low is required only when the Low stage operates at or below 37°F. Inactive
Low-stage curves are not evaluated, fabricated H3Low/H2Low metadata is not
exposed, and Single/Batch active schemas use the same requiredness rule.
Compressor-availability detail now follows the stage selected by each case.

## Next Action

Perform the final merge audit for PR #11. Perform the requested bounded native
Windows/macOS five-path Tkinter smoke outside the GitHub connector before main
integration when that manual evidence is required. Merge only after explicit
user approval.

## Active Blockers

- Native Windows/macOS five-path GUI smoke cannot be executed through the GitHub
  connector and remains pending manual evidence.
- Main merge remains blocked until final merge-audit approval.

## Active Constraints

- Preserve existing variable-capacity numeric results, fixtures, and goldens.
- Keep stable capability IDs and facade method names.
- Keep raw official AHRI Analytics evidence immutable; use the separate 2026
  expected overlay for corrected or derived values.
- Multi-capacity published ratings use nearest 0.05 without changing the current
  variable-capacity 0.025 HSPF2 behavior.
- Keep normalized fractional-bin aggregates separate from actual seasonal totals.
- Use the inclusive 37°F boundary for conditional H3Low requiredness in core,
  application, Single, and Batch contracts.
- Do not merge the implementation branch without explicit approval.

## Deferred / Hold

- Production ML Readiness resumes after the standard-calculation sequence.
- ML validation gap: `model/model.pkl` is absent and training CSV is external;
  mock smoke cannot validate accuracy, trends, importance, or model quality.

## Minimal Anchors

- Phase and milestone direction: `project_brief.md`
- Durable milestone history: `project_log.md`
- Active memory: `result_reports/memory/project_memory_seed.md`
- Structural candidates: `docs/REFACTOR_PLAN.md`
