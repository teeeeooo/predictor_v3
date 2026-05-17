# Active Documents

이 문서는 archive/report 원본을 제외한 active 운영 문서 목록과 주요 inbound/outbound 관계를 관리한다.
문서 업데이트 요청이 들어오면 먼저 이 파일에서 owner 문서와 영향 범위를 확인한다.

## Scope

- Included: root Markdown, `docs/**/*.md`, `data/region_configs/REGION_CONFIG_RULES.md`.
- Excluded: `docs/archive/**`, `reference_files/*.md`, `result_reports/archive/**`, `result_reports/summaries/**`, `result_reports/active/**`.
- Result reports는 lifecycle artifact이므로 `result_reports/summaries/`에서 별도 요약한다.

## Maintenance Rule

1. 새 active 문서를 추가하거나 archive로 이동하면 이 파일을 갱신한다.
2. 문서의 owner 역할, primary inbound, primary outbound가 바뀌면 이 파일을 갱신한다.
3. 문서 업데이트 작업을 요청받으면 `AGENT_TASK_ROUTER.md`의 Documentation Sync gate에서 이 파일을 먼저 확인한다.
4. 대규모 report lifecycle 정리는 이 파일이 아니라 `result_reports/summaries/`와 `project_log.md`에 기록한다.

## Entrypoints

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `AGENTS.md` | Lite agent entrypoint | user/session start, `README.md` | `AGENT_TASK_ROUTER.md`, docs guardrails |
| `AGENT_TASK_ROUTER.md` | Task routing and workflow owner | `AGENTS.md`, agent workflow | task-specific docs, result report workflow |
| `README.md` | Repository public entrypoint | repo root | `project_brief.md`, `project_log.md`, `ACTIVE_DOCUMENTS.md`, docs map |
| `ACTIVE_DOCUMENTS.md` | Active document inventory | `README.md`, `AGENT_TASK_ROUTER.md` | all active docs by owner relationship |
| `project_brief.md` | Current state handoff | `README.md`, new sessions | `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, `project_log.md` |
| `project_log.md` | Decision/history log | task reports, lifecycle summaries | project docs, historical decisions |
| `PROJECT_CHARTER.md` | Long-term project charter | planning tasks | `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md` |

## Core Project Docs

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `docs/README.md` | Documentation structure guide | `README.md`, doc tasks | standard doc set, archive policy |
| `docs/DOCS_GUIDELINES.md` | Standard documentation rules | `AGENTS.md`, `docs/README.md` | template, evidence rules |
| `docs/STANDARD_DOC_TEMPLATE.md` | Standard doc template | `docs/README.md`, new standard docs | notes/dev/design/glossary shape |
| `docs/FORMULA_REFERENCE_GUIDE.md` | Formula notation guide | `docs/README.md`, formula doc tasks | formula/variable formatting |
| `docs/WORK_PLAN.md` | Current execution order | `project_brief.md`, planning tasks | `PROJECT_CHARTER.md`, `docs/REFACTOR_PLAN.md` |
| `docs/REFACTOR_PLAN.md` | Refactor candidates and structural guardrails | `project_brief.md`, architecture-sensitive tasks | `docs/WORK_PLAN.md`, `project_log.md` |
| `docs/PACKAGING.md` | Packaging task owner | packaging route | packaging principles and verification |
| `docs/architecture/project_architecture.md` | Architecture boundary owner | architecture-sensitive tasks | calculator/profile/UI/ML boundaries |
| `data/region_configs/REGION_CONFIG_RULES.md` | Region config edit rules | region config tasks | region config guardrails |

## Standard Docs

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `docs/en14825/en14825_notes.md` | EN14825 standard facts | EN14825 tasks | EN14825 dev/design/glossary |
| `docs/en14825/en14825_dev_notes.md` | EN14825 implementation notes | EN14825 coding tasks | EN14825 notes/design/glossary |
| `docs/en14825/en14825_design_notes.md` | EN14825 design notes | EN14825 boundary tasks | EN14825 glossary |
| `docs/en14825/en14825_glossary.md` | EN14825 terms | EN14825 docs | none |
| `docs/ahri210240/ahri210240_notes.md` | AHRI 210/240 standard facts | AHRI tasks | AHRI dev/design/glossary |
| `docs/ahri210240/ahri210240_dev_notes.md` | AHRI implementation notes | AHRI coding tasks | AHRI notes/glossary |
| `docs/ahri210240/ahri210240_design_notes.md` | AHRI design notes | AHRI boundary tasks | none |
| `docs/ahri210240/ahri210240_glossary.md` | AHRI terms | AHRI docs | none |
| `docs/iso16358/iso16358_notes.md` | ISO16358 standard facts | ISO tasks | ISO dev/design/glossary, KS notes |
| `docs/iso16358/iso16358_dev_notes.md` | ISO16358 implementation notes | ISO calculator tasks, router | ISO notes/glossary, refactor plan |
| `docs/iso16358/iso16358_design_notes.md` | ISO16358 design notes | ISO boundary tasks | ISO glossary |
| `docs/iso16358/iso16358_glossary.md` | ISO16358 terms | ISO docs | ISO notes/dev/design, KS glossary |
| `docs/iso16358/excel_com_runner_packet_protocol.md` | Excel COM packet protocol | AS/NZS/workbook packet tasks | runner/chat_packet workflow |

## Region And Extension Docs

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `docs/iso16358/regions/ks_c_9306/ks_c_9306_notes.md` | KS C 9306 standard facts | KS tasks, router | ISO notes |
| `docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md` | KS implementation notes | KS calculator tasks, router | ISO dev/glossary, KS notes/glossary |
| `docs/iso16358/regions/ks_c_9306/ks_c_9306_design_notes.md` | KS design notes | KS boundary tasks | ISO design/glossary, KS glossary |
| `docs/iso16358/regions/ks_c_9306/ks_c_9306_glossary.md` | KS terms | KS docs | ISO glossary, KS notes/dev/design |
| `docs/iso16358/regions/aus/aus_notes.md` | AS/NZS regional notes | AS/NZS tasks | none |
| `docs/iso16358/regions/southeast_asia/cspf_region_config_phase1_report.md` | Southeast Asia CSPF phase report | regional CSPF tasks | none |

## Knowledge Docs

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `docs/knowledge/README.md` | ML knowledge index | ML/doc tasks | ML knowledge docs |
| `docs/knowledge/hvac_ml_data_quality.md` | ML data quality knowledge | ML data tasks | physical constraints |
| `docs/knowledge/hvac_ml_feature_engineering.md` | ML feature engineering knowledge | ML feature tasks | none |
| `docs/knowledge/physical_constraints_for_ml.md` | ML physical sanity constraints | ML validation tasks | none |

## Design Records

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `docs/designs/TEMPLATE_DESIGN_GATE.md` | Design Gate template | Design Gate tasks | none |
| `docs/designs/2026-05-06-iso16358-2-hspf-core-boundary.md` | ISO HSPF core boundary decision | ISO HSPF boundary tasks | none |
| `docs/designs/2026-05-08-asnzs-hspf-excel-compat-boundary.md` | AS/NZS workbook compatibility boundary | AS/NZS tasks, ISO separation plan | none |
| `docs/designs/2026-05-10-iso16358-2-hspf-h8-routing-resolver-design.md` | ISO HSPF H-8 routing design | ISO HSPF tasks | `docs/iso16358/iso16358_dev_notes.md`, `docs/REFACTOR_PLAN.md` |
| `docs/designs/2026-05-17-iso-remaining-work-completion.md` | ISO remaining work completion boundary | ISO separation completion | `iso_separation_result.md` |
| `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md` | Calculator result envelope / ML adapter boundary | ML / inverse-search restart tasks | `docs/architecture/project_architecture.md`, `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md` |

## Root Result Docs

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| none | Root result docs have been moved to `reference_files/` as reference snapshots. | n/a | n/a |

## Reference Snapshots

`reference_files/*.md` contains user/audit/result snapshots and is excluded from the active owner inventory. If a reference snapshot becomes an active owner document again, move it out of `reference_files/` and add it to the relevant section above.

## Watchlist

| Document | Reason |
| --- | --- |
| `docs/designs/2026-05-06-iso16358-2-hspf-core-boundary.md` | No explicit active inbound reference found; keep because it is a design record. |
| `docs/designs/2026-05-10-iso16358-2-hspf-h8-routing-resolver-design.md` | No broad index inbound found; keep because it is a design record and has outbound references. |
| `docs/iso16358/regions/southeast_asia/cspf_region_config_phase1_report.md` | No explicit inbound found; keep if still used as regional CSPF evidence, otherwise archive candidate. |
