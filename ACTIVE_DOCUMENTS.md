# Active Documents

이 문서는 archive/report 원본을 제외한 active 운영 문서 목록과 주요 inbound/outbound 관계를 관리한다.
문서 업데이트 요청이 들어오면 먼저 이 파일에서 owner 문서와 영향 범위를 확인한다.

## Scope

- Included: root Markdown, `docs/**/*.md`, `data/region_configs/REGION_CONFIG_RULES.md`, `result_reports/memory/*.md`.
- Excluded: `docs/archive/**`, `reference_files/*.md`, `result_reports/archive/**`, `result_reports/summaries/**`, `result_reports/active/**`.
- `result_reports/active/**`, `result_reports/summaries/**`, `result_reports/archive/**`는 lifecycle artifact이므로 active owner inventory에서 제외한다.
- `result_reports/memory/*.md`는 lifecycle artifact의 예외로, backend-neutral active memory staging 문서로 관리한다.

## Maintenance Rule

1. 새 active 문서를 추가하거나 archive로 이동하면 이 파일을 갱신한다.
2. 문서의 owner 역할, primary inbound, primary outbound가 바뀌면 이 파일을 갱신한다.
3. 문서 업데이트 작업을 요청받으면 `AGENT_TASK_ROUTER.md`의 Documentation Sync gate에서 이 파일을 먼저 확인한다.
4. `docs/designs/*.md` 추가, lifecycle status 변경, owner-doc mapping 변경은 `docs/designs/README.md`를 갱신한다.
5. 대규모 report lifecycle 정리는 이 파일이 아니라 `result_reports/summaries/`와 `project_log.md`에 기록한다.

## Entrypoints

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `AGENTS.md` | Lite agent entrypoint | user/session start, `README.md` | `AGENT_TASK_ROUTER.md`, docs guardrails |
| `AGENT_TASK_ROUTER.md` | Task routing index and gate map | `AGENTS.md`, agent workflow | task-specific docs, agent workflow owner docs |
| `README.md` | Repository public entrypoint | repo root | `project_brief.md`, `project_log.md`, `ACTIVE_DOCUMENTS.md`, docs map |
| `ACTIVE_DOCUMENTS.md` | Active document inventory | `README.md`, `AGENT_TASK_ROUTER.md` | all active docs by owner relationship |
| `project_brief.md` | Current state handoff | `README.md`, new sessions | `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, `project_log.md` |
| `project_log.md` | Decision/history log | task reports, lifecycle summaries | project docs, historical decisions |
| `PROJECT_CHARTER.md` | Long-term project charter | planning tasks | `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md` |

## Agent Workflow Docs

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md` | Result report creation, numbering, terminal output, and commit/push workflow owner | `AGENT_TASK_ROUTER.md`, report-backed tasks | `result_reports/active/`, `result_reports/summaries/`, `result_reports/archive/`, `result_reports/memory/` |
| `docs/agent_workflows/DIFF_READ_BUDGET.md` | Read-budget and diff-inspection discipline owner | `AGENT_TASK_ROUTER.md`, large docs/diff/code inspection tasks | targeted source/docs ranges, terminal output discipline |
| `docs/agent_workflows/AGENT_CHANGE_GATES.md` | Pre-write boundary, Read Ledger, staged report association, and future hook/CI gate policy owner | `AGENTS.md`, `AGENT_TASK_ROUTER.md`, structure-impacting source work | active reports, future change-gate tools and hooks |
| `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md` | Project log update judgment and memory seed workflow owner | `AGENT_TASK_ROUTER.md`, lifecycle/memory/log tasks | `project_log.md`, `result_reports/memory/project_memory_seed.md`, project log archive |
| `docs/agent_workflows/SMOKE_LOOP_MODE.md` | Manual UI smoke-loop micro-fix workflow owner | `AGENT_TASK_ROUTER.md`, user smoke-loop instructions | focused UI fixes, stable checkpoint follow-up |
| `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md` | Documentation sync and active-doc lifecycle workflow owner | `AGENT_TASK_ROUTER.md`, docs/lifecycle/commit tasks | `ACTIVE_DOCUMENTS.md`, work plan/refactor/brief/log sync judgments |
| `docs/agent_workflows/UI_SURFACE_WORKFLOW.md` | UI surface workflow owner for table, window/dialog, dynamic profile/page, and result/export surface gates | `AGENT_TASK_ROUTER.md`, UI tasks | `docs/ui_ux/`, toolkit adapters, focused UI validation |
| `docs/agent_workflows/CALCULATOR_WORKFLOW.md` | Calculator, region, golden, smoke/validation, and Excel COM workflow owner | `AGENT_TASK_ROUTER.md`, calculator tasks | calculator core, region configs, standard notes, Excel COM protocol |
| `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md` | ML/Predictor workflow owner | `AGENT_TASK_ROUTER.md`, ML/Predictor tasks | ML code, feature schema, knowledge docs, model constraints |
| `docs/agent_workflows/PACKAGING_WORKFLOW.md` | Packaging and deployment-build workflow owner | `AGENT_TASK_ROUTER.md`, packaging tasks | `docs/PACKAGING.md`, packaging commands/artifacts, deployment verification |

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
| `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` | Codebase-wide Clean Architecture / MVC boundary owner | `AGENTS.md`, `AGENT_TASK_ROUTER.md`, architecture-sensitive tasks | Model/Controller/Shell/View/Policy responsibility triage across interfaces, domain logic, model operations, batch, file I/O, and adapters |
| `docs/ui_ux/00_UI_UX_SYSTEM.md` | UI/UX SSOT root | UI/UX tasks, `AGENTS.md`, `AGENT_TASK_ROUTER.md`, architecture doc | toolkit policy, design tokens, table UX contract, visual architecture, input matrix/result surface rules, portable adoption guide, adapters |
| `docs/ui_ux/01_TOOLKIT_SELECTION_POLICY.md` | Toolkit selection policy | UI/UX root, toolkit decisions | adapter docs |
| `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` | Design tokens and layout rules | UI/UX root, layout tasks | UI component implementations |
| `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` | Global spreadsheet-like table UX contract | UI/UX root, table UI tasks, `AGENTS.md`, `AGENT_TASK_ROUTER.md`, calculator design doc | every table surface (calculator, train/predict, helpers, fixtures) via PyQt/Tkinter adapters |
| `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` | Portable visual design architecture owner | UI/UX root, visual design tasks, project binding/adoption tasks | semantic visual-role adoption across interface implementations |
| `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` | Portable repeated-input matrix and result-surface owner | UI/UX root, visual architecture, table UI and result-surface tasks | repeated input/result surface shaping before toolkit adapters |
| `docs/ui_ux/06_PORTABLE_UI_UX_ADOPTION_GUIDE.md` | Portable UI/UX architecture adoption kit owner | UI/UX root, design tokens/layout, toolkit adapters, cross-project adoption tasks | project binding docs, token owners, reusable components, ownership guard configuration |
| `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` | Portable window geometry, viewport, and auto-fit policy owner | UI/UX root, layout/window geometry tasks, nested notebook/detail refit tasks | interface adapters, app shell/window geometry helpers, future shell geometry implementations |
| `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md` | PyQt table implementation adapter | table UX contract, PyQt table tasks | PyQt table surfaces |
| `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md` | Tkinter table adapter | table UX contract, Tkinter table tasks | Tkinter table surfaces (when applicable) |
| `docs/ui_ux/_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` | Legacy PyQt table contract source (history) | UI/UX `_source/` reference only | none — superseded by `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` |
| `data/region_configs/REGION_CONFIG_RULES.md` | Region config edit rules | region config tasks | region config guardrails |
| `docs/guides/lightweight_calculator_packaging_check.md` | Calculator-only packaging measurement guide | Tkinter feasibility / Windows packaging tasks | PyInstaller size measurement protocol, `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md` |
| `docs/guides/lightweight_calculator_tk_manual_smoke.md` | Tkinter calculator manual smoke checklist | Tkinter MVP validation tasks | manual checklist, expected Hong Kong CSPF/HSPF values, PyQt environment separation |
| `docs/guides/pyqt_test_support_matrix.md` | PyQt widget test support/skip matrix | PyQt env audit / skip patch tasks, PyQt host validation | known-bad macOS Python 3.14 skip rationale, Python 3.12/3.11 and Windows validation pending |

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
| `docs/designs/README.md` | Design record index and lifecycle owner | design-gate/reference tasks, `AGENT_TASK_ROUTER.md` update trigger | individual `docs/designs/*.md` records, owner-doc mapping |

## Root Result Docs

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| none | Root result docs have been moved to `reference_files/` as reference snapshots. | n/a | n/a |

## Memory Staging Docs

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `result_reports/memory/project_memory_seed.md` | Backend-neutral `Project Memory Delta` seed/staging document; preserves traceable source summaries/reports rather than replacing original report text | `AGENT_TASK_ROUTER.md`, `result_reports/summaries/*.md`, `Project Memory Delta` workflow | future local index, memory backend import, agent session recall |

## Historical Archive Docs

| Document | Role | Primary inbound | Primary outbound |
| --- | --- | --- | --- |
| `docs/archive/project_log/YYYY-MM/*.md` | Capped segment archive of exact moved historical `project_log.md` dated entries; not an active operational log | `project_log.md` archive split tasks | none — historical read-only |

- Active operational log는 `project_log.md`이고, historical body는 `docs/archive/project_log/YYYY-MM/*.md` capped segment archive이다.
- Archive 문서는 기본 read 대상이 아니며, 필요 시 `rg -n "^## YYYY-MM-DD"` heading 검색 후 해당 segment 파일의 필요한 범위만 확인한다.

## Reference Snapshots

`reference_files/*.md` contains user/audit/result snapshots and is excluded from the active owner inventory. If a reference snapshot becomes an active owner document again, move it out of `reference_files/` and add it to the relevant section above.

## Watchlist

| Document | Reason |
| --- | --- |
| `docs/designs/2026-05-06-iso16358-2-hspf-core-boundary.md` | No explicit active inbound reference found; keep because it is a design record. |
| `docs/designs/2026-05-10-iso16358-2-hspf-h8-routing-resolver-design.md` | No broad index inbound found; keep because it is a design record and has outbound references. |
| `docs/iso16358/regions/southeast_asia/cspf_region_config_phase1_report.md` | No explicit inbound found; keep if still used as regional CSPF evidence, otherwise archive candidate. |
