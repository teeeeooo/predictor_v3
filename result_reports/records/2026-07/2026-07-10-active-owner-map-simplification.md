# Active Owner Map Simplification

record:
  date: 2026-07-10
  topic: active owner map simplification
  tags: agent-harness, document-routing, owner-map
  memory_review: no-change
  memory_reason: existing workflow/lifecycle seed already captures AGENTS/router/owner-document routing and no new project-domain memory is needed

## Reason

The exhaustive active-document inventory duplicated child discovery, became
stale easily, and encouraged broad reads instead of routing to one owner.

## Change

- Replaced the generated-style inventory with a non-exhaustive top-level
  owner-route map, reducing it from 162 lines / 1,920 words to 55 lines / 413
  words.
- Added missing local discovery links to the UI, calculator, ML/Predictor, and
  packaging workflows, and marked the old ML Feature Catalog edit/save flow as
  historical rather than the current schema owner.
- Corrected README, charter, lifecycle, project-log, and work-plan wording so
  ordinary detail belongs to Git history, focused validation, and terminal/final
  output; compact records remain conditional.

## Preserved Discovery

- Preserved routes to agent rules, current direction, architecture, workflow
  owners, result index, design index, memory seed, and historical boundaries.
- Child completeness now belongs to the nearest owner README/index/workflow or
  a filesystem search; no tracked full-file inventory is generated.

## Verification

- All owner-route and newly added workflow-link targets exist.
- Final owner-map count is 55 lines / 413 words.
- Stale inventory/work-history policy phrase scan returned no matches in the
  synchronized policy surfaces.
- `git diff --check` passed.
