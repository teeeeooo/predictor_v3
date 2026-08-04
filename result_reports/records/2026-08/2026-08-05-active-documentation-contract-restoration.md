record:
  date: 2026-08-05
  topic: active-documentation-contract-restoration
  tags: agent-harness, documentation, authority, routing, result-record, owner-restoration
  memory_review: no-change
  memory_reason: Existing memory already records the current package owners, MODEL_REGISTRY compatibility role, standard separation, and conditional report policy.

# Active Documentation Contract Restoration

## Change Reason

Active inbound documentation still named retired source paths, treated completed
migration/slice plans as current authority, and let repository-local Result
Record/terminal wording compete with Engineering Workflow role reporting.

## Contract / Behavior Changed

- Separate Engineering Workflow generic role/lane/Build-Gate-Close/reporting
  authority from predictor_v3 project/domain/mechanical ownership.
- Return `AGENT_TASK_ROUTER.md` to task-to-owner navigation while preserving all
  material routes and repository-specific owner gates.
- Restore root ML/Predict/Calculator UI authority to current package owners and
  make Data Definition/immutable registry authority explicit over compatibility
  `COLUMNS` and `MODEL_REGISTRY` projections.
- Demote the completed package-restructuring plan and original PySide foundation
  slices from current implementation authority without deleting historical evidence.
- Keep UI parity evidence mandatory while making compact Result Record creation
  conditional on the repository trigger.
- Restore current EN14825 unified config, KS private standard owner, Calculator UI
  layout owner, and ML feature/Target policy references.

No production source, tests, runtime behavior, formula/golden/config value,
mechanical gate implementation, or Engineering Workflow Skill changed.

## Evidence And Verification

- `git diff --check` — PASS.
- Documentation-only changed-path guard — PASS; all pre-record task changes are
  Markdown documents.
- Active-authority assertions — PASS: retired root/current-owner paths are absent
  from current inbound owners, restored owner paths exist, and all ten material
  router routes remain discoverable.
- Historical-demotion assertions — PASS for restructuring/PySide current owners.
- `python3 -B -m pytest -q tests/test_tools_check_agent_change_gate.py` —
  PASS, 14 tests.
- `python3 -B tools/check_agent_change_gate.py --cached` — PASS (`agent change gate: OK`).

## Changed Files

- Root/routing/report lifecycle: `AGENTS.md`, `AGENT_TASK_ROUTER.md`,
  `docs/agent_workflows/{RESULT_REPORT_WORKFLOW,DOCUMENT_SYNC_AND_LIFECYCLE,ML_PREDICTOR_WORKFLOW}.md`.
- Architecture/navigation: `docs/architecture/{project_architecture,project_wide_architecture_restructuring_plan,pyside6_train_predict_architecture}.md`.
- Domain/current owner corrections: `docs/PACKAGING.md`, EN14825 dev/glossary,
  KS C 9306 dev notes, and `docs/knowledge/hvac_ml_feature_engineering.md`.
- UI owner/evidence corrections: `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`,
  `03_SPREADSHEET_TABLE_UX_CONTRACT.md`, and `adapters/TKINTER_TABLE_ADAPTER.md`.
- This Result Record and `result_reports/REPORT_INDEX.md` complete the required
  conditional-record lifecycle.

## Known Risks

Historical design/archive bodies intentionally retain old paths and retired API
names as evidence. `ACTIVE_DOCUMENTS.md`, `docs/WORK_PLAN.md`, project memory,
Clean Architecture, and broader UI/standard bodies remain unchanged because no
top-level owner/current slice/new durable memory or their unique acceptance
responsibilities changed. Fresh Lane C Auditor exact-head review remains required.
