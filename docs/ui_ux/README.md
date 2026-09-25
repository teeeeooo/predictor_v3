# UI / UX Documentation Index

This folder owns the UI/UX contracts adopted by predictor_v3. Other projects
may reuse relevant guidance through explicit adoption; this copy does not
automatically govern them. Generic table/window workflows remain in the global
`desktop-table-ui` and `desktop-window-lifecycle` Skills; this folder owns the
project adoption, surface obligations, and toolkit bindings.

`00_UI_UX_SYSTEM.md` is the root SSOT. This README is only a navigation and
adoption guide; it does not replace any owner document.

## Temporary behavior baseline

During the 2026-09-25 policy-only consolidation, existing UI behavior is
temporarily fixed as the baseline. This is not a claim that every current
behavior passes the generic contract, and it is not a permanent UX decision.
Policy cleanup must not change product behavior. A later explicitly scoped
behavior change may revise this baseline with its owning design and checks.
See [the table bindings](03_SPREADSHEET_TABLE_UX_CONTRACT.md#temporary-surface-bindings)
for the observed differences and [toolkit policy](01_TOOLKIT_SELECTION_POLICY.md)
for the retained toolkit choices.

## Document Roles

- `00_UI_UX_SYSTEM.md`: root common UI/UX principles.
- `01_TOOLKIT_SELECTION_POLICY.md`: interface toolkit choice policy.
- `02_DESIGN_TOKENS_AND_LAYOUT.md`: semantic token and layout contract.
- `03_SPREADSHEET_TABLE_UX_CONTRACT.md`: adopted table obligations and current surface bindings.
- `04_VISUAL_DESIGN_ARCHITECTURE.md`: adopted visual roles and design direction.
- `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`: adopted repeated-input and
  result-surface shaping rules.
- `06_PORTABLE_UI_UX_ADOPTION_GUIDE.md`: how to bind the common rules into a
  concrete project.
- `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`: Predictor geometry/viewport adoption,
  implementation owners, and acceptance; reusable refit procedure is in the
  global `desktop-window-lifecycle` Skill.
- `adapters/`: interface-framework-specific implementation adapters.
- `_source/`: historical or evidence source material, not active contracts.

## Portability Rule

Specific project, library, screen, or standard names may appear as examples,
evidence, or adoption notes. Reusability does not extend this repository's
policy authority: another project selects its own binding. Read only the
adapter for the selected toolkit; legacy PyQt guidance is not a PySide6 default.

Adapter documents are allowed to keep specific toolkit names because their job
is to map portable contracts to a concrete implementation framework.

Project-specific harvest and design references live under `docs/designs/`.

When adopting this folder into another project, use `06_PORTABLE_UI_UX_ADOPTION_GUIDE.md`
to create the project binding, token owner, adapter decisions, and verification
guard needed to make the portable rules enforceable.
