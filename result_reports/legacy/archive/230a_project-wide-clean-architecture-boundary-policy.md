# 230A — Project-Wide Clean Architecture Boundary Policy

## Goal

Promote the repeated Tkinter window sizing lesson into a project-wide Clean
Architecture / MVC boundary policy. This is a documentation and agent-rule task
only; no code or tests were changed.

## Checked Documents

- `AGENTS.md`
- `AGENT_TASK_ROUTER.md`
- `ACTIVE_DOCUMENTS.md`
- `docs/architecture/project_architecture.md`
- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
- `result_reports/active/229_tk-content-hugging-shell-template.md`
- `docs/WORK_PLAN.md`
- recent `project_log.md` entries

## Current Gap

`AGENTS.md` already had a general code quality gate that warned against mixing
shell, orchestration, business logic, transforms, formatting, and I/O in one
file. `AGENT_TASK_ROUTER.md` also had architecture triage questions.

The gap was that neither document made the Model / Controller(or Service) /
Shell(or Adapter) / View / Policy boundary explicit enough for repeated local
hotfixes. The Hong Kong lower blank/flicker arc showed that a View can gradually
accumulate widget composition, measurement policy, scheduling, geometry apply,
scroll cleanup, and calculation orchestration until a small smoke bug becomes a
boundary problem.

UI/UX documents remain UX contract owners. They are not the project-wide code
architecture owner.

## New Owner Document

Added:

- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`

It defines:

- project-wide purpose;
- dependency direction from Shell/View/Adapter toward Controller/Service and
  Model/Domain;
- responsibility definitions for Model/Domain, Controller/Orchestrator,
  Shell/Adapter/Infrastructure, View/Presentation, and Policy/Contract Owner;
- boundary smells and stop conditions;
- the window sizing lesson as an example, not a source of truth;
- lightweight application rules that do not force large preflights for every
  micro change.

This document applies across UI, calculator core, ML, batch, file I/O, Excel /
DRM adapters, and future Web/PySide/WPF shells.

## AGENTS.md Update

Updated the New Code Quality Gate with a short pointer to the new architecture
owner:

- Model / Controller(or Service) / Shell(or Adapter) / View / Policy boundaries
  follow `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`;
- repeated local hotfixes or rules that may spread across profiles/toolkits
  require owner-boundary judgment first.

Detailed rules were intentionally not copied into `AGENTS.md`.

## Router Update

Updated `AGENT_TASK_ROUTER.md` Architecture Triage for Coding Tasks with
Clean/MVC boundary checks:

- whether a task adds a new Model / Controller / Shell / View / Adapter /
  Policy responsibility;
- whether one file/class gains multiple responsibilities;
- whether View/script code mixes domain calculation, file I/O, schema policy,
  or toolkit-specific measurement;
- whether a local hotfix is really a reusable policy/adapter/helper candidate.

The router remains a gate map and points to the owner document for detail.

## ACTIVE_DOCUMENTS Update

Registered:

- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`

Role:

- project-wide Clean Architecture / MVC boundary owner.

Primary outbound:

- Model/Controller/Shell/View/Policy responsibility triage across UI,
  calculator, ML, batch, file I/O, and adapters.

## WORK_PLAN Update

Updated next action to:

- extract Tk visible content measurement adapter.

Rationale:

- `window_shell.py` is now a shell/template owner;
- `window_refit.py` remains scheduler owner;
- `window_geometry.py` remains primitive owner;
- the next boundary should move `Iso16358Tab`-specific hidden-tab
  width/current-visible-height measurement into an adapter/provider boundary.

## project_log Update

Added a short decision entry:

- repeated Tkinter window-sizing failures are a project-wide responsibility
  boundary lesson;
- the Clean/MVC boundary owner is now
  `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`;
- repeated smoke failures of the same class should trigger owner-boundary
  judgment before more local patches.

## Excluded Scope

- No source code changes.
- No test changes.
- No Tkinter window sizing implementation.
- No `Iso16358Tab` refactor.
- No `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` changes.
- No UI table contract changes.
- No calculator core / ML / backend abstraction changes.
- No docs/designs changes.
- No report lifecycle/archive work.

## Validation

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing soft warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git status --short`: only expected documentation and report files changed
  before commit.
- `pytest`: not run; documentation/agent-rule task.
- GUI smoke: not run; no UI code changes.

## Next Action

Extract Tk visible content measurement adapter.
