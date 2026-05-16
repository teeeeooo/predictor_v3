# Audit Doc Workflow Links

## Goal

Audit the active documentation workflow that starts from `AGENTS.md` and routes through `AGENT_TASK_ROUTER.md`, project docs, standard docs, and supporting reference docs. Identify bad inbound/outbound links, archive misuse, and ownerless isolated documents without editing source docs.

## Scope

- Active-doc audit only.
- Excluded `*_design_notes.md` from the audit target set.
- Excluded `docs/archive/**` and `result_reports/**` as workflow nodes; they were checked only for incorrect active-primary usage.
- Excluded generated/cache docs such as `.pytest_cache/README.md`.
- Source docs were not modified.

## Inventory Summary

- Active tracked/document candidates checked: 41.
- Entrypoints: `AGENTS.md`, `README.md`, `docs/README.md`.
- Router/owner docs: `AGENT_TASK_ROUTER.md`, `PROJECT_CHARTER.md`, `project_brief.md`, `project_log.md`, `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`.
- Standard active docs: EN14825, AHRI 210/240, ISO16358, KS C 9306 notes/dev/glossary docs.
- Supporting docs: architecture, knowledge, formula/reference/documentation guides, region config rules, packaging, design records, local skill docs, naming/reference docs.

## Findings

### High

None found.

No active document currently uses `docs/archive/**` or `result_reports/**` as a primary workflow owner. The active references to archived EN14825/AHRI legacy notes are explicitly marked as historical source/evidence.

### Medium

| Finding | Evidence | Why it matters | Suggested fix |
| --- | --- | --- | --- |
| `docs/PACKAGING.md` is an active owner doc with no active inbound path. | `rg` found no active references to `docs/PACKAGING.md`, `PACKAGING.md`, or `PACKAGING` outside the file itself. | Packaging rules were split out of archived agent rules, but agents starting from `AGENTS.md`/router/README will not discover it unless they already know it exists. | Add it to the root `README.md` documentation map and add a packaging route or conditional read in `AGENT_TASK_ROUTER.md`. |
| `docs/iso16358/regions/aus/aus_notes.md` is a region research memo without an owner route. | No active inbound references found. The file itself says it is a regional research memo, not implementation spec. | It sits in an active region path, so future agents may treat it as implementation guidance or miss it entirely. | Either link it from `docs/iso16358/iso16358_notes.md` as deferred AS/NZS research, or move it under `docs/archive/` if it is not active guidance. |
| `docs/iso16358/regions/southeast_asia/cspf_region_config_phase1_report.md` is a phase report inside active docs. | No active inbound references found. The title and content are report-style, not canonical notes/dev/glossary structure. | Report-style evidence in active region docs blurs the boundary between canonical guidance and one-off audit output. | Move to `docs/archive/` or convert the reusable findings into an ISO/region notes section and archive the report body. |
| `skills_devide_plan.md` is a completed root-level migration plan with no owner. | No active inbound references found. Its work is already reflected by `docs/archive/skills_v2_patterns.md`, owner docs, project_log, and report summaries. | Root-level completed plans increase startup/workflow noise and look like active pending work. | Move to `docs/archive/` or delete after confirming all useful content is already preserved. |

### Low

| Finding | Evidence | Why it matters | Suggested fix |
| --- | --- | --- | --- |
| `reference_files/OPTIMO_naming.md` is an ownerless naming reference. | No active inbound references found. It contains product/module naming ideas. | It may be useful, but it is not discoverable from README, docs map, or architecture docs. | Link from `README.md` or `project_brief.md` if naming remains active; otherwise archive it as historical naming exploration. |
| `.agents/skills/grill-me/SKILL.md` has no path-level inbound reference. | No active path reference found, but `AGENTS.md` references the `grill-me` skill by name. | This is acceptable because skill discovery is tool/skill mediated, not path-reference mediated. | No change required unless the project wants path-level discoverability for local skills. |
| `docs/designs/*` records are weakly linked by pattern rather than per-file inbound links. | `README.md`, `project_brief.md`, and `docs/REFACTOR_PLAN.md` reference `docs/designs/*`; individual design files are not all linked. | This is acceptable for append-only design records, but searching by topic remains necessary. | No immediate change required; add per-design links only when a design becomes active guidance for a current task. |

## Healthy Workflow Checks

- `AGENTS.md` correctly delegates detailed task routing to `AGENT_TASK_ROUTER.md`.
- `AGENT_TASK_ROUTER.md` owns task routes, report workflow, lifecycle behavior, and conditional document reads.
- `PROJECT_CHARTER.md`, `project_brief.md`, `project_log.md`, `docs/WORK_PLAN.md`, and `docs/REFACTOR_PLAN.md` have distinct roles and are cross-linked from root/readme/router paths.
- `docs/DOCS_GUIDELINES.md`, `docs/STANDARD_DOC_TEMPLATE.md`, and `docs/FORMULA_REFERENCE_GUIDE.md` are discoverable from document-work routes.
- Region config rules are discoverable from `AGENTS.md` and `AGENT_TASK_ROUTER.md`.
- Knowledge docs are discoverable from `docs/knowledge/README.md` and ML/Predictor router conditions.
- EN14825 and AHRI archive references are historical/evidence references, not primary active owners.

## Suggested Fix Order

1. Decide whether `skills_devide_plan.md` should be archived or deleted.
2. Add a discoverable owner path for `docs/PACKAGING.md`.
3. Decide whether AS/NZS and Southeast Asia region notes are active deferred region docs or archive-only evidence.
4. Decide whether `reference_files/OPTIMO_naming.md` should be linked as active naming/product reference or archived.

## Project Log Sync Judgment

No `project_log.md` update is recommended for this audit-only task.

Reason: this report records findings but does not establish a new workflow decision or modify source docs. Update `project_log.md` only after the user accepts a follow-up cleanup plan or a source-doc fix is implemented.

## Verification

- `find` active inventory excluding `docs/archive/**`, `result_reports/**`, `.pytest_cache`, and `*_design_notes.md`: 41 candidates.
- `rg` path/reference scan for active docs and archive/report primary misuse.
- Targeted inbound checks for `docs/PACKAGING.md`, `skills_devide_plan.md`, `reference_files/OPTIMO_naming.md`, `docs/iso16358/regions/aus/aus_notes.md`, and `docs/iso16358/regions/southeast_asia/cspf_region_config_phase1_report.md`: no active inbound references found.
- Checked top sections of suspected ownerless documents to classify whether they are active guidance, completed plan, report evidence, or expected isolated docs.
- Runtime tests were not run because this was documentation workflow audit only.

## Changed Files

- `result_reports/active/021_audit-doc-workflow-links.md`: this audit report.

## Known Risks

- The audit is path/reference based; implicit human knowledge or external workflow habits are not counted as inbound ownership.
- `*_design_notes.md` files were deliberately excluded by request, so design-note-specific workflow gaps are not covered.
- No source documents were corrected in this task.

## Commit / Push

- Source change: none.
- Report commit: this report is intended to be committed as a report-only change.
- Push: final terminal response records the pushed commit hash.
