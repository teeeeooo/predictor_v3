# 244 Reference Parity And Standardization Gate

## Goal

Add a broad reference parity / standardization gate to common process documents
so that new UI surfaces, scripts, helpers, adapters, workflow paths, and
reusable components first check existing stable implementations before repeating
already-solved behavior bugs, lifecycle handling, and interaction patterns.

## Scope

- Add a short, implementation-agnostic reference parity gate to existing owner
documents.
- Connect the gate into the agent work flow (AGENTS, router, report workflow).
- Do not create new active documents.
- Do not lock in specific implementation patterns or class names.

## Documentation Flow Audit

- `AGENTS.md` New Code Quality Gate already applies to all new scripts/modules/features
(UI/core/tools/scripts/ML). Best place for a one-line parity reminder.
- `AGENT_TASK_ROUTER.md` Architecture Triage is the natural route hook for
boundary decisions. Best place for a short route addition.
- `PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` already owns codebase-wide Clean
Architecture / MVC boundary rules and stop conditions. Best place for a dedicated
"Reference Parity / Standardization Gate" section.
- `RESULT_REPORT_WORKFLOW.md` already owns report structure. Best place for a
conditional reference parity evidence section in full report defaults.
- `UI_SURFACE_WORKFLOW.md` already owns table-specific parity checklist. Best
place for a one-line connection to the broader gate.
- `ACTIVE_DOCUMENTS.md` owner roles did not change; no update needed.
- `WORK_PLAN.md` next action did not change; no update needed.

## Changed Docs

### AGENTS.md
- Added one bullet to New Code Quality Gate:
  "기존에 안정화된 구현이나 workflow가 있으면 reference parity를 확인하고,
  reuse/adapt 불가 시 그 이유를 남긴다."

### AGENT_TASK_ROUTER.md
- Added one paragraph to Architecture Triage:
  "새 UI surface, script, helper, adapter, workflow path, 또는 reusable component를
  만들기 전에 기존 안정화 구현이나 workflow가 있는지 확인하고,
  재사용/변형/비재사용 판단과 근거를 남긴다."

### docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md
- Added "Reference Parity / Standardization Gate" section after "How To Apply".
- Covers every layer (Model, Controller, Shell, View, Policy), not only UI.
- Includes: check existing stable implementation, prefer reuse/adapt, record why
  not reused, leave parity evidence, record unresolved gaps as risks.

### docs/agent_workflows/RESULT_REPORT_WORKFLOW.md
- Added conditional guidance to full report default sections:
  "When a new UI surface, script, helper, adapter, workflow path, or reusable
  component is created or an existing stable path is replaced/extended, include
  a short reference parity section..."

### docs/agent_workflows/UI_SURFACE_WORKFLOW.md
- Added one bullet to Table Surface Gate connecting the broad parity gate to
table-specific work:
  "broad reference parity gate: before creating a new table-shaped surface,
  confirm whether an existing stable implementation already covers the same
  interaction, lifecycle, or cleanup concerns, and record why it was or was not
  reused;"

### project_log.md
- Added 2026-06-07 log entry documenting the new gate and its trigger (242
  migration reproduced already-solved interaction issues).

## Reference Parity Gate Summary

The gate is intentionally lightweight and implementation-agnostic:
- It does not force code reuse.
- It does not mandate specific classes, functions, or algorithms.
- It applies to every layer, not only UI.
- It requires evidence (why reused / why not / what gaps remain), not compliance.

## Implementation Lock-in Avoidance

- No specific paste handler, undo stack, StringVar lifecycle, restore method,
  or widget class is mandated.
- The gate asks for "parity evidence," not "use the same implementation."
- Report guidance is conditional ("when creating or replacing..."), not universal.

## Verification

- `git diff --check`: clean
- `git status --short`: 6 files modified, no untracked files

## Known Risks

- The gate is only as effective as the discipline to follow it. Automated
enforcement is limited to check_code_structure.py style checks.
- If reference implementations are themselves unstable, the gate may propagate
bugs. The gate encourages recording "why not reused," which can surface this.

## Next Suggested Action

- When creating the next new UI surface, script, helper, adapter, or workflow
path, apply the gate and record parity evidence in the result report.

## Project Memory Delta

- `reference_parity_gate` is now a documented process rule across
  `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`,
  `RESULT_REPORT_WORKFLOW.md`, and `UI_SURFACE_WORKFLOW.md`.
- The gate is triggered by the observation that 242-243 matrix migration
reproduced paste tiling, repeated undo, and restore flicker issues already solved
in the existing row-per-case table surface.
