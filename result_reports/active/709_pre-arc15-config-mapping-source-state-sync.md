# Pre-Arc 15 Config Mapping Source State Sync

## Goal

Record the current project-state ambiguity before Arc 15 so the next session
does not proceed directly into a real dataset readiness audit or a `Unified Data
Definition Manager` direction without first checking the relationship between
config CSVs, legacy mapping evidence, and Data Mapping Manager outputs.

## Modified Files

- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/709_pre-arc15-config-mapping-source-state-sync.md`

## Checked Files And Paths

- `config/ml/features.csv`
- `config/predict/schema.csv`
- `tests/fixtures/mapping/mapping_tables_legacy_wide.csv`
- `docs/designs/2026-07-05-arc14b4-legacy-mapping-csv-to-json-rule-reconstruction-audit.md`
- `docs/designs/2026-07-03-arc14a-mapping-entity-master-data-foundation.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`

## Legacy Mapping CSV Result

`mapping_tables_legacy_wide.csv` is found in the current checkout:

- `tests/fixtures/mapping/mapping_tables_legacy_wide.csv`

The file header is a legacy wide mapping layout with grouped columns such as
Compressor, Evap Index, IDU, ODU, ODU Cond Index/Specs, Ref type, and Exp type.
Existing Arc 14A / Arc 14B-4 design notes classify it as legacy
import-compatibility evidence, not a canonical manager export format. This task
does not re-decide that classification; it records that the file is present and
must be included in the Pre-Arc 15 relationship audit.

## Config CSV Status

Current conservative reading:

- `config/ml/features.csv` has columns including `ml_name`, `role`, `ui_key`,
  `source`, `mapping_key`, `one_hot_group`, `zero_fill_policy`, and `active`.
  It currently reads as the ML training/inference feature contract.
- `config/predict/schema.csv` has columns including `column_key`, `role`,
  `editor`, `value_source`, `mapping_entity`, `mapping_attribute`,
  `trigger_column`, `rule_id`, `model_input_enabled`, `ml_name`, and
  `one_hot_group`. It currently reads as the Predict UI/runtime column schema
  contract.
- The split between those two CSVs may be intentional final design, or it may
  be accumulated duplication debt from Arc progression. This task does not
  decide that question.
- Real training CSV data is not in this repo; the user clarified that real
  training data remains on the user's local PC.

## Documentation Updates

- `docs/WORK_PLAN.md`: changed Next Actions to:
  1. Pre-Arc 15 Audit - Config CSV / Legacy Mapping Source / Manager Output
     Relationship Audit.
  2. Arc 15 direction decision after the audit.
- `docs/WORK_PLAN.md`: added blockers/open decisions for the legacy mapping CSV
  path, missing real training CSV in repo, current config CSV split, and the
  need to avoid locking in `Unified Data Definition Manager` before audit.
- `project_brief.md`: updated the current phase and Arc 15 status to reflect
  that Arc 15 is pending direction decision after the Pre-Arc 15 audit.
- `project_log.md`: added a short milestone decision entry for the Pre-Arc 15
  config/mapping source audit decision.

## Excluded Scope

- No code changes.
- No CSV, JSON, fixture, or data file changes.
- No new design record.
- No Arc 15 detailed design decision.
- No `Unified Data Definition Manager` direction commitment.
- No training, prediction, smoke test, or data conversion execution.
- No report lifecycle cleanup.

## Validation

- `git ls-files | rg "mapping_tables_legacy_wide|mapping.*legacy|legacy.*mapping"`:
  OK; found `tests/fixtures/mapping/mapping_tables_legacy_wide.csv` plus
  existing design/report references.
- `rg -n "mapping_tables_legacy_wide|legacy wide|legacy mapping CSV|config/ml/features.csv|config/predict/schema.csv" .`:
  OK; references reviewed only as needed.
- Header/sample checks for `config/ml/features.csv`, `config/predict/schema.csv`,
  and `tests/fixtures/mapping/mapping_tables_legacy_wide.csv`: OK.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  LOC/class soft warnings unrelated to this docs-only task.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK,
  freshness `FRESH`; commit/dirty-worktree notes were informational.
- `git diff --check`: OK.
- `git diff --stat`: OK; tracked doc diff only before adding this report.
- `git status --short`: expected modified docs plus new report before commit.

## Next Action

Pre-Arc 15 Audit - Config CSV / Legacy Mapping Source / Manager Output
Relationship Audit.
