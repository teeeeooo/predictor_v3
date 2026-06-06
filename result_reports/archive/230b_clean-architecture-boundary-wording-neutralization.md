# 230B — Clean Architecture Boundary Wording Neutralization

## Goal

Refine the 230A Clean Architecture / MVC boundary policy so it reads as a
codebase-wide design rule, not as a policy tied to one project, GUI toolkit, or
external integration.

## Specificity Audit

The 230A owner document had the right direction but used many concrete names in
principle sections:

- project name;
- GUI framework names;
- specific external-system names;
- a specific calculator/profile/window sizing issue.

Those names risked reading as scope boundaries instead of examples. The
architecture owner should define neutral responsibility boundaries first, then
use concrete names only as evidence.

## Architecture Owner Neutralization

Updated `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`:

- `predictor_v3` wording was changed to active project / codebase wording.
- GUI framework names were replaced in principle text with interface framework
  / interface shell wording.
- Specific external integration names were generalized to spreadsheet
  automation, protected-file environments, file system, database, network API,
  and external document integration.
- Profile/toolkit repetition wording was generalized to domain variants,
  standards, screens, and interface frameworks.
- The window sizing lesson became an `Observed Example / Evidence` section.
- Added the rule that example names are evidence, not scope boundaries.

Specific names were not erased completely; they are now limited to the evidence
section where they clarify the historical example.

## Router Gate Reinforcement

Updated `AGENT_TASK_ROUTER.md` Architecture Triage:

- if any boundary question is Yes, the agent must not jump straight to
  implementation;
- it must first leave an owner-boundary decision;
- when needed, it should split implementation behind a design/report slice;
- the existing principle that not every coding task needs a large preflight
  remains unchanged.

## AGENTS / ACTIVE_DOCUMENTS

Updated `AGENTS.md` minimally:

- replaced `profile/toolkit/surface` wording with
  `domain/interface/code surface` wording.

Updated `ACTIVE_DOCUMENTS.md` minimally:

- changed the owner role to codebase-wide;
- generalized outbound wording from UI/calculator/ML specifics to interfaces,
  domain logic, model operations, batch, file I/O, and adapters.

## WORK_PLAN / project_log

Updated `docs/WORK_PLAN.md`:

- recorded that 230B neutralized the architecture policy wording.
- next action remains `extract Tk visible content measurement adapter`.

Updated `project_log.md`:

- merged a short 230B note into the existing 2026-06-06 Clean Architecture
  entry instead of adding a duplicate section.

## Excluded Scope

- No code changes.
- No tests changed.
- No Tkinter sizing implementation.
- No UI/UX policy docs changed.
- No core, ML, backend, or table architecture changes.
- No docs/designs changes.
- No report lifecycle/archive work.

## Validation

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing soft warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git status --short`: only expected documentation/report files changed before
  commit.
- `pytest`: not run; documentation/agent-rule refinement task.
- GUI smoke: not run; no UI code changes.

## Next Action

Extract Tk visible content measurement adapter.
