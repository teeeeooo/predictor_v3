---
name: packaging
description: Use for predictor_v3 local/deployment packaging, PyInstaller, spec files, binary dependencies, packaging failures, artifact verification, and deployment-environment cleanup. Do not use for application logic changes.
---

# Packaging

Use this skill only for predictor_v3 packaging and deployment-build work. The user's explicit task takes precedence over this skill.

## Scope and owners

- Packaging policy: `docs/PACKAGING.md`.
- Dependency policy: `docs/development/dependencies.md`.
- Calculator packaging measurement only: `docs/guides/lightweight_calculator_packaging_check.md`.
- Historical failure context: search `project_log.md` by a specific keyword only when needed.

## Boundaries

- Confirm target platform, output shape, packaging purpose, and verification method from the task or existing repository evidence.
- If no build command or `.spec` is already accepted, do not invent one as canonical guidance.
- Keep deployment and development environments separate.
- Do not mix packaging work with calculator, ML, or UI behavior changes.
- Use app-scoped requirements as deployment dependency evidence: `requirements/train.txt`, `requirements/predict.txt`, and `requirements/calculator.txt`; include `requirements/excel.txt` when that surface reads or writes Excel.
- Do not treat `requirements/dev.txt` as the deployment dependency source unless the task explicitly calls for a development bundle.

## Execution and verification

1. Reproduce the actual packaging path or failure before changing guidance.
2. Check binary dependencies, resource paths, crash logging, and output shape from actual build evidence rather than speculation.
3. Verify the produced artifact at the level required by the task: build success alone does not prove startup/runtime behavior.
4. Record skipped platform/runtime verification as unverified rather than assuming success.

Run only the packaging checks and focused app/runtime checks needed to prove the changed packaging behavior. Broaden validation only after a later change, failure, or unresolved packaging risk invalidates the earlier evidence.