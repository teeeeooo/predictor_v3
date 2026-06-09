# Report 313: Controller Switch Arc Final Summary / Closeout

## Goal

- `ui_tk` 패키지의 table controller migration arc (legacy `ExcelLikeTableController`에서 `TkTableController` + `interaction_core.py` 공통 기반으로 전환)를 최종적으로 요약 및 closeout한다.
- 최근 2-point 및 SASO T3의 controller switch, SASO validation alignment, 그리고 codebase reference map 재생성까지 완료된 마일스톤 상태를 정리하고 다음 작업인 active report lifecycle cleanup을 준비한다.

## Scope

### Closeout Targets (대상 범위)

1. **Hong Kong HSPF & CSPF Controller Switch**: `MetricInputTable` 기반의 TkTableController 전환 및 paste, undo, clear 기능 복원 완료.
2. **ISO/ISEER 2-Point Controller Switch (302, 303)**: `IsoIseer2PointSection` 마이그레이션 및 6개 focused test 보강, iMac GUI smoke 테스트 통과.
3. **SASO T3 Controller Switch & Validation Alignment (304, 307, 308)**: `IsoSasoT3Section` 마이그레이션, required/optional `35 Min` input의 MetricInputTable visual marking 표준 API 정렬 완료, focused test 추가, iMac GUI smoke 테스트 완료 및 blocker 해결.
4. **Codebase Reference Map Regeneration (310, 311, 312)**: code_checker의 Git metadata comment 지원 및 task number decoupling 적용 후 `CODEBASE_REFERENCE_MAP.md` 재생성 및 freshness check 검증 완료.

### Excluded Scope

- Python 소스코드 수정 금지.
- `tools/code_checker` 및 `tools/check_code_structure.py` 기능/룰 변경 금지.
- calculator core, ML/predictor 로직 수정 금지.
- 이번 슬라이스에서의 실제 active report lifecycle cleanup (파일 이동/아카이빙) 수행 보류.

## MVC / SoC (Separation of Concerns) 최종 판단

- **View (MetricInputTable)**: 오직 UI 렌더링, cell rendering, focus-out parsing, invalid visual marking(빨간색 하이라이팅)의 presentation 관심사만 전담함.
- **Controller (TkTableController)**: interaction_core와 연동되어 paste, undo stack, cell value sync, type-replace selection clear 등의 grid control 관심사를 전담함.
- **Model / Section (IsoSasoT3Section 등)**: required/optional 그룹 분류, positivity 도메인 정책, calculator dispatcher 연계 등 domain / business logic 관심사를 명확히 소유함으로써 깔끔한 MVC/SoC 정렬이 완료됨.

## Verification

- `python3 -B tools/check_code_structure.py` (warnings: 4 pre-existing, 0 new) 통과.
- `git diff --check` 및 `git status --short` 확인 완료.
- active report count 검증 완료 (exact count는 final terminal output으로만 출력).

## Known Limitations / Risks

- **Dirty Tree Metadata warning**: 커밋 후 git HEAD의 short hash가 바뀌기 때문에, 커밋 이후 `--check`를 실행하면 stale로 판정되는 것은 정상 동작임. 추가 재생성-재커밋 무한 루프를 만들지 않고 다음 migration 작업 시작 전 sync할 것을 권장함.

## Active Report Count

- active report count exceeds lifecycle threshold; cleanup pending.

## Lifecycle Maintenance Note

- **Pending**: 현재 완료된 active report가 임계치(10)를 대폭 초과하였으나 이번 closeout 작업에서는 cleanup을 수행하지 않으며, 다음 Next Action으로 예정된 active report lifecycle cleanup 작업에서 전체적인 요약 및 아카이빙을 진행할 예정임.

## Next Suggested Action

1. **Active report lifecycle cleanup**
   - Archive active reports to summary files once all controller switch steps are completed.
2. **Main table migration check**
   - Assess how existing table surfaces can converge on the common table foundation and define a safe migration slice.
3. **ui_tk folder cleanup**
   - Review compatibility wrappers, root table file sprawl, owner locations, and duplicate helpers after window/table foundations stabilize.
4. **EN14825 / AHRI 210/240 / KS profile expansion**
