# Predict Schema / Mapping Foundation Docs

## Goal

Arc 13.5R / Arc 14 재설계 결정을 다음 agent가 문서만 읽어도 이해할 수 있도록 보존하고, root 임시 mapping CSV를 future import compatibility fixture 위치로 이동한다.

## Scope

- Arc 13.5R Predict Schema Catalog v2, Mapping Master Data, Runtime Cascade foundation design record 작성.
- Design index, WORK_PLAN, project_brief의 Arc 13.5R/14/15 map compact sync.
- Root `mapping tables.csv`를 fixture로 이동.

## Changed Files

| Path | Change |
| --- | --- |
| `tests/fixtures/mapping/mapping_tables_legacy_wide.csv` | Root dummy CSV를 legacy wide CSV import compatibility fixture로 이동. |
| `docs/designs/2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md` | 신규 design record 추가. |
| `docs/designs/README.md` | Design record index에 신규 row 추가. |
| `docs/WORK_PLAN.md` | Near-term order를 Arc 13.5R, Arc 14A/B/C, Arc 15 순서로 갱신. |
| `project_brief.md` | Current phase와 Arc 14/15 map 최소 sync. |
| `result_reports/active/675_predict-schema-mapping-foundation-docs.md` | Compact result report. |

## Fixture Move

`mapping tables.csv`는 runtime `data/`로 옮기지 않았고 `mapping.json`도 생성하지 않았다. 새 위치의 fixture는 canonical manager export format이 아니라 legacy wide CSV import compatibility fixture로만 문서화했다.

## Key Decisions

- Feature Catalog Manager는 장기적으로 Predict Schema Manager로 확장/승격한다.
- Data Mapping Manager는 Predict column 정의가 아니라 mapping master data CRUD/import/export/validation/save/reload를 맡는다.
- 새 option/spec 추가와 새 column/group/template 추가는 분리한다.
- IDU와 Evap은 직접 종속이 아니라 IDU Size를 통해 연결된다.
- IDU-Evap / ODU-Cond는 slot template-aware cascade로 다룬다.
- Mapping data 변경은 live reload 가능 방향, schema/column 변경은 초기 restart-required 방향으로 둔다.
- ML feature activation은 Arc 15 readiness audit 대상으로 유지한다.

## Verification

- `git show HEAD:'mapping tables.csv' | cmp - tests/fixtures/mapping/mapping_tables_legacy_wide.csv`: OK, fixture content matches the uploaded root CSV.
- `git diff --check`: OK.
- `git status --short`: expected docs changes, root CSV deletion, new fixture, and this report only.
- `python3 -B tools/check_code_structure.py`: NG, pre-existing unchanged source guard failure in `apps/calculator/ui/calculator_app.py` for a raw hex color literal; this docs/fixture task did not modify source files.
- Skipped pytest: docs/fixture relocation only; code/test logic was not changed.
- Skipped GUI smoke: no UI implementation change.

## Excluded Scope

- 계산 로직, Predict UI code, Feature Catalog code, Mapping converter code 수정 없음.
- Data Mapping Manager UI 구현 없음.
- Runtime cascade 구현 없음.
- Fixture/golden expected 변경 없음.
- Report lifecycle 이동 없음.

## Known Risks

- Predict Schema Catalog v2 storage format, slot template field set, Data Mapping Manager canonical CSV v2 format은 아직 Arc 13.5R/14A에서 확정해야 한다.
- Optional structure guard is currently weaker-verified because of an unrelated pre-existing source warning/error outside this task scope.

## Next Action

Arc 13.5R Predict Schema Catalog v2 design/audit을 실행해 current hard-coded UI-only dropdown columns, Feature Catalog projection, mapping adapter, and cascade/template boundaries를 정리한다.

## Commit / Push

Final commit and push result will be reported in terminal output to avoid a self-referential report update loop.
