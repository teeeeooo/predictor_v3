# 700 Summary - Arc 14B Runtime Data Mapping / CRUD Design Closeout

## Goal

Summarize the Arc 14B runtime Data Mapping follow-up work after the foundation
closeout, then archive the completed active reports.

Covered reports:

- `688_active-report-lifecycle-cleanup-arc13-5r-arc14b.md`
- `689_pyside6-macos-computer-use-click-crash-spike.md`
- `690_data-mapping-ax-crash-isolation-and-model-guard.md`
- `691_data-mapping-panel-composition-slice-isolation.md`
- `692_arc14b-runtime-mapping-repository-read-adapter.md`
- `693_arc14b-runtime-source-visibility-and-row-identity.md`
- `694_ui-computer-use-smoke-token-discipline.md`
- `695_smoke-loop-mode-computer-use-bound.md`
- `696_data-mapping-user-facing-copy-simplification.md`
- `697_arc14b4-legacy-mapping-csv-to-json-rule-reconstruction-audit.md`
- `698_arc14b5-data-mapping-ui-crud-workflow-design.md`
- `699_arc14b5-ref-exp-mapping-ssot-design-correction.md`

## Major Decisions

- Data Mapping Manager now reads runtime `mapping.json` through the existing
  repository path and adapts it into `MappingEntityCatalog`; the foundation
  sample provider is explicit test/fallback injection only.
- Missing or empty runtime mapping data is a visible load error, not a silent
  sample fallback.
- Read-only row identity display uses `Row Key` as the visible identity column;
  the entity `key_attribute` remains metadata for future edit/export contracts.
- Main-screen copy is user-facing: short action labels, concise status text,
  `File: <path>` source display, and no raw runtime/repository terminology on
  the primary screen.
- Legacy single-wide CSV to `mapping.json` reconstruction is not recoverable
  enough to implement as a recovered legacy flow.
- Data Mapping editable work should proceed as UI CRUD over user-facing Predict
  mapping groups, not as raw JSON editing, generic entity editing, or
  export-edit-reimport.
- `mapping.json` is the SSOT for Refrigerant and Expansion options:
  `ref_type` and `exp_type` are required mapping sections, and hard-coded
  Predict dropdown fallbacks are legacy behavior to remove during
  implementation.

## Runtime And UI Behavior

- `DataMappingService()` defaults to the runtime mapping provider.
- Controller/UI states preserve runtime source/path when load fails and surface
  a `load_failed` issue row.
- ODU Cond Specs is the user-facing table that generates internal
  `odu_cascade`, `cond_specs`, `fin_type`, `pi`, and `row` sections.
- Export remains a read-only review snapshot concept. XLSX is the human-review
  candidate and pretty JSON is the exact fallback/debug candidate.
- Import is excluded until an explicit compatibility-parser design exists.
- Save/Reload/dirty-state work remains below the UI raw JSON boundary and is
  split into later implementation slices.

## Accessibility And Smoke Lessons

- The Computer Use crash was narrowed away from PySide6/macOS in general,
  Python version, simple `QTableView`, and the generic table model alone.
- The smallest observed failing Data Mapping path was a populated entity table
  with an initial `selectRow()` during `_bind_entity_selection()`.
- Removing the initial programmatic entity selection stabilized the full
  standalone panel for Computer Use state, keyboard substitute, and click
  checks.
- Future UI / Computer Use smoke should run focused automated owner tests
  first, then one bounded state read and the minimum keyboard/click action
  needed for acceptance evidence.

## Excluded Scope

- No editable CRUD implementation.
- No save/reload/export/import implementation.
- No runtime cascade integration.
- No ML training/retraining/model artifact changes.
- No Predict Schema Catalog or Feature Catalog owner changes.
- No broad code-map regeneration.

## Validation

- Source reports recorded focused service/controller/UI model, runtime adapter,
  py_compile, structure guard, and bounded GUI/Computer Use smoke checks where
  applicable.
- Documentation-only design/audit reports recorded `git diff --check` and
  structure guard status where applicable.
- Lifecycle cleanup validation:
  - `git diff --check`: OK.
  - Active report count is expected to be below lifecycle threshold after
    archive movement.
  - Memory seed summary registration and compact durable entries were updated.
- Known weaker verification:
  - This lifecycle cleanup did not rerun source/test suites from archived
    source reports.
  - Future implementation still needs its own focused tests and GUI validation.

## Lifecycle

- Covered active reports are archived under `result_reports/archive/`.
- This summary is registered in `result_reports/memory/project_memory_seed.md`.
- Memory seed gained compact durable entries for runtime Data Mapping state,
  import/export direction, and UI CRUD workflow boundaries.

## Project Memory Seed Sync Judgment

- Registered under Source Coverage because this is a summary lifecycle task.
- Added summary-level durable entries because later Data Mapping CRUD and
  Predict dropdown work depends on the runtime source, import/export, user-facing
  group, and ref/exp SSOT decisions.

## Next Action

Arc 14B-5B - implement editor draft projection from runtime `mapping.json` to
the seven user-facing groups in read-only mode, including `ref_type` /
`exp_type` mapping ownership and Predict dropdown fallback removal.
