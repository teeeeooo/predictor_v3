# Arc 13.5R Predict Schema v2 Field Spec Confirmation

## Goal

Arc 13.5R-1 inventory를 바탕으로 Predict Schema Catalog v2의 field/spec contract를 확정하고, Arc 13.5R-3 read-only schema draft/projection parity prototype 범위를 선명하게 만든다.

## Modified Files

| Path | Change |
| --- | --- |
| `docs/designs/2026-07-03-arc13-5r-predict-schema-v2-field-spec-confirmation.md` | 신규 v2 field/spec confirmation design record 작성. |
| `docs/designs/README.md` | 신규 design record index row 추가. |
| `docs/WORK_PLAN.md` | Current Slice / Next Actions를 Arc 13.5R-3로 compact하게 갱신. |
| `result_reports/active/678_arc13-5r-predict-schema-v2-field-spec-confirmation.md` | Compact result report. |

## Key Decisions

- v2 field set을 `display_order`, `column_key`, `label`, `role`, `editor`, `data_type`, `visible`, `required`, `readonly`, `value_source`, `mapping_entity`, `mapping_attribute`, `trigger_column`, `rule_id`, `model_input_enabled`, `ml_name`, `one_hot_group`, `active`, `notes`로 확정했다.
- `template_id`, `slot_id`, `cascade_role`는 optional preset/group helper로만 둔다.
- `source`와 `mapping_entity`를 같은 의미로 취급하지 않고, `column_key == mapping_entity` 가정도 금지했다.
- One-hot selector는 cascade primitive가 아니라 ML input projection concern으로 분리했다.
- `lookup`, `filter`, `clear`, `composite_lookup` primitive의 초기 spec과 out-of-scope를 문서화했다.
- Schema/column/rule 변경은 초기 restart-required 정책으로 확정했다.

## Verification

- `git diff --check`: OK.
- `python3 -B tools/check_code_structure.py`: NG, pre-existing unchanged source guard failure in `apps/calculator/ui/calculator_app.py` for a raw hex color literal; this docs-only task did not modify source files.
- `git status --short`: expected docs/report changes only.
- Skipped pytest: docs/spec confirmation only; source/test logic was not changed.
- Skipped GUI smoke: no UI implementation change.

## Excluded Scope

- Source code, `config/ml/features.csv`, fixtures, tests, runtime behavior, mapping converter, Data Mapping Manager UI, cascade engine, ML training/model artifacts 변경 없음.
- `config/predict/schema.csv` 생성 없음.
- Report lifecycle movement 없음.
- Follow-up commit/push performed after the initial docs-only closeout.

## Next Action

Arc 13.5R-3 read-only `schema.csv` draft/projection parity prototype.

## Commit / Push

- Commit: `f615254` (`docs: confirm predict schema v2 field spec`).
- Push: OK; remote `main` matched `f615254` after push.
