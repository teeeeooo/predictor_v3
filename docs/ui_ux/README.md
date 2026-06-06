# UI / UX Documentation Index

This folder is a portable UI/UX rule set. It is intended to be reusable when
starting or adopting another engineering/data application, rather than being
tied to one project, screen, or GUI library.

`00_UI_UX_SYSTEM.md` is the root SSOT. This README is only a navigation and
adoption guide; it does not replace any owner document.

## Document Roles

- `00_UI_UX_SYSTEM.md`: root common UI/UX principles.
- `01_TOOLKIT_SELECTION_POLICY.md`: interface toolkit choice policy.
- `02_DESIGN_TOKENS_AND_LAYOUT.md`: semantic token and layout contract.
- `03_SPREADSHEET_TABLE_UX_CONTRACT.md`: portable table interaction contract.
- `04_VISUAL_DESIGN_ARCHITECTURE.md`: portable visual design architecture.
- `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`: portable repeated-input and
  result-surface shaping rules.
- `06_PORTABLE_UI_UX_ADOPTION_GUIDE.md`: how to bind the common rules into a
  concrete project.
- `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`: portable window/viewport and
  dynamic refit policy.
- `adapters/`: interface-framework-specific implementation adapters.
- `_source/`: historical or evidence source material, not active contracts.

## Portability Rule

Specific project, library, screen, or standard names may appear as examples,
evidence, or adoption notes. They are not principle scope boundaries unless the
owner document explicitly says so.

Adapter documents are allowed to keep specific toolkit names because their job
is to map portable contracts to a concrete implementation framework.

When adopting this folder into another project, use `06_PORTABLE_UI_UX_ADOPTION_GUIDE.md`
to create the project binding, token owner, adapter decisions, and verification
guard needed to make the portable rules enforceable.
