---
name: ui-surface
description: Use for predictor_v3 user-facing UI surface changes including tables, windows/dialogs, dynamic pages, input/result/detail/export surfaces, visual polish, and GUI interaction validation. Do not use for core-only changes.
---

# UI Surface

Use this skill only for predictor_v3 UI work. The user's explicit task takes precedence over this skill.

## Classify the changed surface

Choose the smallest matching UI class before editing:

- table-shaped surface;
- window, dialog, viewport, or content-hugging shell;
- dynamic profile/page/screen lifecycle;
- input/result/detail/export surface;
- visual-only polish;
- UI change that also alters schema, calculator, ML, config, or public-result behavior.

## Owner routing

- UI/UX root: `docs/ui_ux/00_UI_UX_SYSTEM.md`.
- Local index: `docs/ui_ux/README.md`.
- Toolkit policy: `docs/ui_ux/01_TOOLKIT_SELECTION_POLICY.md`.
- Design tokens/layout: `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`.
- Table interactions: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Input/result/error/export: `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.
- Window/dialog/viewport lifecycle: `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`.
- Toolkit-specific table adapters live under `docs/ui_ux/adapters/`.

## Reuse and structure gate

Before adding lifecycle, mapping, formatting, sizing, clipboard/export, validation, or presentation policy, inspect the changed owner and a materially similar sibling surface. Reuse an existing helper/adapter when it owns the same behavior; keep profile-specific labels, field maps, precision, and schema local.

For structure-impacting UI work, use `tools/check_code_structure.py` as a warning-first guard. A soft LOC warning is a responsibility-triage signal, not an automatic extraction requirement. Split only when ownership becomes clearer or the responsibility is repeated/cross-surface.

## Surface acceptance

- Table work follows the shared spreadsheet contract for selection, copy/paste, scrolling, viewport containment, and toolkit parity.
- Window/dialog work follows the geometry/viewport owner rather than inventing local settle/refit loops.
- Stateful input/batch surfaces preserve their documented state owner across close/reopen unless an explicit reset action exists.
- Input/result/detail/export work keeps domain result schemas separate from UI table/export schemas and reuses established copy/export owners when they fit.
- Visual-only changes do not justify calculator, ML, schema, or persistence changes.

## Boundary trigger

If a UI request also changes calculator inputs/results, profile selection, region config, ML features, persisted state, schema, or public result keys, inspect `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` and the matching domain owner before implementation. Do not solve a domain/schema issue as a UI convenience patch.

## Verification

Use the narrowest automated evidence that proves the changed behavior: controller/helper tests for interaction semantics, fake/provider/scheduler tests for lifecycle behavior, and focused UI import/programmatic checks for the changed surface.

Use manual GUI or native-platform smoke only when the behavior cannot be adequately proven automatically. Keep Computer Use/accessibility-tree interaction bounded, especially on known fragile macOS Data Mapping paths. When manual smoke exposes a source defect, add or update the focused automated guard when practical before one bounded rerun.

Do not repeat a passing UI suite or broaden to full pytest merely because the task is UI-related. Re-run only evidence invalidated by a later source change, a failure, or an unresolved acceptance concern.