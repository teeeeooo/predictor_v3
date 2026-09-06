# Agent Change Gates

## Role

Own staged objective checks and warning-first structure evidence. This is a mechanical repository guard, not a documentation or memory workflow.

## Applicability

The cached checker inspects staged source, test, tool, and region-config changes. Docs-only wording/status work normally needs no gate beyond diff/link inspection.

## Hard checks

The staged checker fails on:

- staged whitespace errors;
- Python syntax errors in checked source;
- Phase 1 UI presentation literals that bypass token owners without an explicitly approved local exemption; and
- staged paths outside an explicitly supplied local task manifest.

No Result Record, memory review, report index update, or memory-seed update is required by this checker.

## Warning-first structure checks

The checker warns, but does not fail solely, when:

- a new production source is over 250 LOC;
- a new production source exceeds 350 LOC;
- a new source has many top-level classes;
- an existing hotspot grows by 40 net LOC or more;
- structural source ownership/reuse deserves review; or
- a Phase 2 UI presentation literal may deserve an existing token/helper.

LOC and class-count signals are responsibility smells. Split only when ownership becomes clearer or behavior is genuinely reusable; do not extract code merely to satisfy a number.

## Local Task Manifest

The optional local manifest is resolved through:

```bash
git rev-parse --git-path agent_task_manifest.yml
```

Supported shape:

```yaml
allowed_paths:
  - literal/staged/path.py
ui_literal_exemption: none | approved-for-slice
```

`allowed_paths` limits the staged scope to literal paths. `ui_literal_exemption` is optional and defaults to `none`; use `approved-for-slice` only when the current user-approved task intentionally keeps a Phase 1 presentation literal local.

The manifest lives under the Git directory. It is local staging control, not durable project history, and is never required for an ordinary change.

## UI Literal Policy

Phase 1 rejects new staged production UI literals for known table/window/color policy surfaces. Token-owner modules and grandfathered lines remain outside the check.

Phase 2 warns on likely repeated `width`, `height`, `padx`, `pady`, or named-color literals. Prefer an existing token/helper when it owns the same behavior; a deliberately local value does not require a durable report.

Domain/regulation values are not UI presentation literals.

## Hook Policy

`.githooks/pre-commit` runs:

```bash
git diff --cached --check
python3 -B tools/check_agent_change_gate.py --cached
```

Hooks are active only when the checkout config points `core.hooksPath` at `.githooks`. Run `scripts/install_git_hooks.sh` once per checkout to install that repository-local setting.

## Validation

When this policy or checker changes, run focused agent-change-gate tests, focused UI literal tests when that surface changes, and Git hook tests when hook behavior changes. Use `tools/check_code_structure.py` for structure-impacting source changes when it adds useful evidence.

Do not run full pytest solely because harness policy changed.
