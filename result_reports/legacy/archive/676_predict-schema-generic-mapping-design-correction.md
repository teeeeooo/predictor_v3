# Predict Schema Generic Mapping Design Correction

## Goal

Arc 13.5R / Arc 14 foundation 문서에서 IDU-Evap / ODU-Cond examples가 core schema boundary처럼 읽히는 문제를 보정하고, Predict Schema Catalog v2를 generic mapping entity / attribute / rule contract 중심으로 재정의한다.

## Scope

- Existing design record의 Purpose, Decisions, Target Architecture, Manager Responsibilities, Runtime Apply Policy, Open Questions, Next Action 보정.
- WORK_PLAN near-term board의 Arc 13.5R/14 표현 보정.
- project_brief Arc map/current phase 최소 sync.

## Changed Files

| Path | Change |
| --- | --- |
| `docs/designs/2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md` | IDU/ODU preset 중심 표현을 generic mapping entity / attribute / rule 중심으로 보정. |
| `docs/WORK_PLAN.md` | Arc 13.5R/14 execution board를 generic schema contract audit 방향으로 보정. |
| `project_brief.md` | Current phase와 Arc 14 map의 boundary 표현을 compact하게 sync. |
| `result_reports/active/676_predict-schema-generic-mapping-design-correction.md` | Compact result report. |

## Key Corrections

- IDU-Evap / ODU-Cond는 representative examples 또는 default presets이며, core schema boundary가 아니라고 명시했다.
- Predict Schema Catalog v2의 핵심 후보를 `column_key`, `value_source`, `mapping_entity`, `mapping_attribute`, `trigger_column`, `rule_id`, `model_input_enabled`, `ml_name` 등 generic fields로 정리했다.
- `template_id`, `slot_id`, `cascade_role`는 optional preset/group helper로 격하했다.
- Data Mapping Manager를 fixed table manager가 아니라 Mapping Entity Manager로 설명했다.
- Cascade/autofill primitive를 `lookup`, `filter`, `clear`, `composite_lookup`로 정리했다.
- Extension cases로 Evap Index attribute 추가, new `fan_motor` entity, tube dependent dropdown 관계를 추가했다.

## Verification

- `git diff --check`: OK.
- `git status --short`: expected docs/report changes only.
- `python3 -B tools/check_code_structure.py`: NG, pre-existing unchanged source guard failure in `apps/calculator/ui/calculator_app.py` for a raw hex color literal; this docs-only task did not modify source files.
- Skipped pytest: docs-only correction; code/test logic was not changed.
- Skipped GUI smoke: no UI implementation change.

## Excluded Scope

- Source code, Feature Catalog code, Predict runtime, mapping converter, Data Mapping Manager UI implementation 변경 없음.
- `config/ml/features.csv`, fixture/golden expected, `tests/fixtures/mapping/mapping_tables_legacy_wide.csv` 변경 없음.
- Report lifecycle 이동 없음.

## Next Action

Arc 13.5R design/audit에서 current schema projection, UI-only dropdown columns, mapping autofill owner, and generic rule primitive scope를 확인한 뒤 Predict Schema Catalog v2 owner contract를 확정한다.

## Commit / Push

Final commit and push result will be reported in terminal output to avoid a self-referential report update loop.
