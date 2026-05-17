# Active Documents Workflow Audit Result

## Objective

Create one maintainable list of active managed documents, include inbound/outbound relationships where practical, wire that list into the document workflow, summarize active result reports, and update project management docs.

## Deliverables

- Active document inventory: `ACTIVE_DOCUMENTS.md`
- Router inbound: `AGENT_TASK_ROUTER.md`
- README inbound: `README.md`, `docs/README.md`
- Result report lifecycle summary: `result_reports/summaries/054_summary-calculator-ui-iso-separation.md`
- Archived covered reports: `result_reports/archive/034` through `053`
- Project log update: `project_log.md`
- Completion report: this file

## Active Document Inventory

`ACTIVE_DOCUMENTS.md` lists active root/docs documents and separates result reports from active owner docs.

Inventory scope:

- Included: root Markdown, `docs/**/*.md`, `data/region_configs/REGION_CONFIG_RULES.md`
- Excluded: `docs/archive/**`, `result_reports/archive/**`, `result_reports/summaries/**`, `result_reports/active/**`

The file groups documents by role:

- Entrypoints
- Core project docs
- Standard docs
- Region and extension docs
- Knowledge docs
- Design records
- Root result docs
- Watchlist

## Inbound / Outbound Policy

The inventory records primary inbound and outbound relationships, not every incidental mention.

- Primary inbound means the normal route that causes a worker to read or update the document.
- Primary outbound means the document owner or downstream document that should be checked next.
- Watchlist entries identify active docs with weak explicit inbound references.

## Workflow Update

`AGENT_TASK_ROUTER.md` now requires `ACTIVE_DOCUMENTS.md` before broad document updates, docs lifecycle work, or active document create/archive actions.

`README.md` and `docs/README.md` now expose `ACTIVE_DOCUMENTS.md` as the active documentation owner map.

## Result Reports Summary

Created `result_reports/summaries/054_summary-calculator-ui-iso-separation.md`.

Covered reports:

- 034-035: calculator UI / dispatcher
- 036-043: KS C 9306 and ISO CSPF cleanup
- 044-053: ISO separation reset and completion

The covered reports were moved from `result_reports/active/` to `result_reports/archive/` without renaming.

## Verification

- `git diff --check` passed before the first docs commit.
- `ACTIVE_DOCUMENTS.md` inbound references were verified with `rg`.
- Result report active/archive/summary placement was verified with `ls`.

## Remaining Risk

- Inbound/outbound relationship mapping is curated from explicit path references and known workflow ownership. It is not a full semantic graph.
- Watchlist docs should be reviewed later if the team wants every design/report document to have an explicit index inbound.
