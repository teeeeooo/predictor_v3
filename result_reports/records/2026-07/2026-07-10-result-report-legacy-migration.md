# Result Report Legacy Migration

record:
  date: 2026-07-10
  topic: result-report-legacy-migration
  tags: agent-harness, legacy, report-history
  memory_review: updated
  memory_reason: record the completed physical legacy paths and preserved historical-literal boundary

## Change Reason

Pre-cutover reports and summaries needed a physical legacy boundary so their
historical role would not depend on a removable policy sentence.

## Contract / Behavior Changed

- 720 archived reports now reside under `result_reports/legacy/archive/`.
- 53 summary reports now reside under `result_reports/legacy/summaries/`.
- Active source pointers were remapped to the new paths.
- Legacy report/summary bodies and four approved historical-literal documents
  retain their original text.

## Evidence And Verification

- Pre/post aggregate SHA-256 manifests matched for all 773 moved Markdown
  bodies.
- Active approved documents contain no old archive/summary prefix.
- The remaining 107 old-prefix occurrences are confined to the four approved
  historical-literal files outside legacy.
- Rename, path, link, diff, and staged-gate checks are required before commit.

## Changed Files

- Physical legacy archive/summary paths.
- Active source pointers, report control docs, discovery index, project memory,
  project log, and design implementation status.

## Known Risks

- Legacy bodies intentionally contain old historical paths and commands.
- `project_brief.md` and `docs/WORK_PLAN.md` may still need a separate state
  freshness cleanup unrelated to this path migration.
