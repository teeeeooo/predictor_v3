# Packaging Workflow

## Role

This document owns packaging and deployment-build workflow details.
`AGENT_TASK_ROUTER.md` only routes here.

## Applies To

- local or deployment packaging requests;
- PyInstaller, `.spec`, onefile/onedir, binary dependency, and crash logging
  work;
- packaging failure reproduction;
- packaging artifact verification;
- deployment environment cleanup.

## Owner Documents

- Packaging owner: `docs/PACKAGING.md`
- Existing packaging failure or milestone decisions: search `project_log.md`
  by keyword only.

## Flow

1. Confirm target platform, output shape, packaging purpose, and verification
   method.
2. If no build command or `.spec` is already accepted, do not invent a
   canonical command.
3. Keep deployment environment separate from development environment
   (`venv_deploy` or equivalent).
4. Do not mix packaging work with calculator, ML, or UI logic changes.
5. Check binary dependencies, resource paths, and crash logging only from actual
   packaging evidence or explicit failure logs.
6. If packaging workflow, failure cause, or deployment decision is confirmed,
   judge whether `project_log.md` needs a compact entry.
7. Final report should separate build commands run, artifact checks, skipped
   verification, and residual risk.

## Do Not Read

- unrelated standard notes/dev_notes;
- broad calculator, ML, or UI code;
- unrelated archived reports.

## Forbidden

- recording speculative build commands as canonical docs or README guidance;
- unrelated logic/UI/ML refactors during packaging.
