# 647 Memory Seed Maintenance

## Goal

Reduce `result_reports/memory/project_memory_seed.md` into a current/future
work active seed while preserving retired entries with traceable sources.

## Scope

- Rebuilt the active seed around explicitly retained workflow, UI/UX,
  calculator, and ML/Predict/Train topics.
- Rewrote selected stateful entries into compact current-policy entries.
- Moved retired, stale, superseded, resolved, and intermediate-slice entries to
  `result_reports/memory/archive/project_memory_seed_retired_2026-07.md`.
- Added the Arc 13.5 feature catalog editor direction as an active seed entry.
- Updated `ACTIVE_DOCUMENTS.md` to describe `result_reports/memory/archive/`
  as non-active retired memory entry storage.

## Changed Files

- `result_reports/memory/project_memory_seed.md`
- `result_reports/memory/archive/project_memory_seed_retired_2026-07.md`
- `ACTIVE_DOCUMENTS.md`
- `result_reports/active/647_memory-seed-maintenance.md`

## Active / Rewritten / Retired Seed Decision Summary

- Active seed now keeps the explicitly listed durable workflow, UI/UX,
  calculator, and ML/Predict/Train topics.
- Compact rewrites were applied to stateful entries for active agent rule
  ownership, window/viewport policy, BatchMatrix lifecycle boundaries,
  Tkinter/PySide6 calculator direction, Arc 9.5 case table acceptance, and Arc
  10 prediction worker boundaries.
- Retired entries were archived rather than deleted, with original source
  traces preserved.
- Source Summaries were compacted to coverage wording through the KOREA
  calculator sub-arc summary; retired entry source traces remain in the archive.

## Verification

- `rg -n "assertionStatus: superseded|assertionStatus: stale|resolutionStatus:" result_reports/memory/project_memory_seed.md`:
  OK, no matches.
- `git diff --check`: OK.
- `git status --short`: reviewed before commit.
- `pytest`, `py_compile`, and structure guard were not run because this is a
  docs/lifecycle-only memory maintenance slice.

## Known Risks

- The active seed remains above the lightweight maintenance-audit threshold
  because the prompt explicitly retained a broad current/future topic set.
- No source summaries were broadly reread; seed body and scoped source pointers
  were used as the maintenance evidence.

## Commit / Push

- Commit: performed after Slice 1 verification; final hash is reported in the
  terminal response.
- Push: deferred until Slice 2 is complete.
