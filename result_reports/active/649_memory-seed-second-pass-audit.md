# Memory Seed Second-Pass Audit

## Goal

Apply the active seed `Next Maintenance Rule` and reduce `result_reports/memory/project_memory_seed.md` from a detailed decision database into a compact first-read decision index.

## Scope

- Reviewed the active seed structure and `Next Maintenance Rule`.
- Rewrote active seed entries into consolidated owner-boundary entries.
- Preserved removed/replaced source entries in the July retired memory archive with `retiredReason` and `consolidatedBy` metadata.
- Did not modify code, tests, config, runtime behavior, `project_log.md`, `ACTIVE_DOCUMENTS.md`, `WORK_PLAN.md`, `project_brief.md`, source summaries, or existing archived report bodies.

## Changed Files

- `result_reports/memory/project_memory_seed.md`
- `result_reports/memory/archive/project_memory_seed_retired_2026-07.md`
- `result_reports/active/649_memory-seed-second-pass-audit.md`

## Maintenance Rule Check

- This was an explicit memory maintenance task, so seed modification was in scope.
- The active seed exceeded the audit threshold before this pass.
- No new durable rule/error/open_question was added beyond the consolidation itself.
- Source traces were not deleted; entries removed from active recall were archived.
- Individual reports and summaries were not retroactively modified.

## Compaction Decision

- `keep`: current project state and unresolved external-reference items that need direct recall.
- `consolidate`: related owner-boundary, workflow, UI, calculator, and Train/Predict entries where one compact policy entry is more useful than multiple slice-level entries.
- `mark stale`: not used in the active seed; stale/superseded states remain in the archive, not active recall.
- `archive`: detailed slice history, closeout-derived intermediate decisions, and entries replaced by consolidated active topics.
- Active seed entry count is below the maintenance target threshold.

## Archived / Consolidated Areas

- Agent workflow, report lifecycle, project log, and memory lifecycle.
- Architecture, source owner, change gate, and code checker evidence policy.
- UI/UX SSOT and table interaction contracts.
- Window/viewport, result-detail, BatchMatrix, and lifecycle policies.
- Calculator standard/config/profile/public result ownership.
- Calculator envelope and ML/ranking boundary.
- ISO HSPF fixture/minus7 trap.
- Calculator application/UI boundary.
- Train/Predict PySide6 and execution boundaries.
- Arc 13 feature catalog and Arc 13.5 editor direction remain active.
- KOREA calculator notebook closeout remains active in compact form.
- AS/NZS case3 parity remains active as an unresolved open question.

## Verification

- Active seed entry count checked and is below the target threshold.
- Active seed line count checked.
- Active seed forbidden active-rule string scan checked clean.
- Active seed `assertionStatus: superseded` / `assertionStatus: stale` scan checked clean.
- `git diff --check` will be run before commit.
- `git status --short` reviewed for allowed file scope.
- `pytest`, `py_compile`, and structure guard were intentionally not run because this is a docs/lifecycle-only cleanup.
- `rg` is unavailable in this environment, so equivalent `grep` checks were used for the requested pattern scans.

## Known Risks

- The active seed is now intentionally compact; detailed historical recall requires consulting the retired archive or source summaries.
- Archive growth is expected because source traces are preserved instead of deleted.

## Commit / Push

- Commit after validation with message `Compact project memory seed index`.
- Push after commit and verify local HEAD matches `origin/main`.
