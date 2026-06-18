# 391 Memory seed sync lifecycle rule hardening

## Goal

Correct the memory seed Source Summaries omission after summary 364 and harden
the lifecycle workflow so future summary closeouts explicitly check memory seed
sync.

## Scope

- Updated `result_reports/memory/project_memory_seed.md` Source Summaries for
  summary 385.
- Added a compact summary lifecycle memory seed checklist to
  `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md`.
- Added a routing hook in `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`.
- Reviewed active reports 386-390 only for durable candidates; they were not
  added directly to Source Summaries because they are not summary reports.

## Memory Seed Sync

- Source Summaries now include
  `result_reports/summaries/385_summary-en14825-ui-correction-lifecycle-closeout.md`
  for covered reports 365-384.
- No new seed entry was added from summary 385. The summary records lifecycle
  closeout and manual smoke evidence, and its own Memory Seed section states
  that it does not introduce a new durable standard/schema/procedure decision
  beyond covered reports.

## Candidate Durable Entries

These active-report candidates were left for the next lifecycle summary or an
explicit memory maintenance task:

- 386/387: EN14825 SEER now has a cooling_only auxiliary-hours path while SCOP
  keeps reversible/heating_only behavior; the durable seed candidate is the
  final owner/API/UI contract, not the earlier audit alone.
- 388/389: `MetricInputTable` gained content-hug behavior for small tables and
  content-width behavior became the default table/result surface policy, with
  responsive behavior remaining explicit.
- 390: `ResultPanel` summary columns use a uniform grid group while the summary
  card remains bounded to content width.

## Workflow Hardening

- `PROJECT_LOG_AND_MEMORY.md` now owns a summary lifecycle checklist covering
  Source Summaries registration, durable candidate judgment, minimal entry
  addition, and seed-not-updated reason recording.
- `RESULT_REPORT_WORKFLOW.md` now routes summary/archive lifecycle maintenance
  to that memory seed check without duplicating the detailed rule.

## Numbering Note

The prompt referred to active reports 386-391 and a report 392 candidate
section, but this checkout has no `391_*.md` under active/archive/summaries.
Per the report numbering owner, the next report number in the current checkout
is 391.

## Verification

- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Known Risks

- Active reports after summary 385 remain outside Source Summaries until a
  future lifecycle summary or explicit memory maintenance task.
- This task did not create a new summary or move archive files.

## Commit / Push

- Final commit hash and push status are reported in terminal output.
