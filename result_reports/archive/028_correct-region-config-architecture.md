# 028_correct-region-config-architecture

## Goal
- 직전 architecture reset 문서들에 들어간 잘못된 표현 “region config는 ISO16358 계열에만 붙여 쓴다 / region config를 사용하는 유일한 계열”을 바로잡는다. `data/region_configs/`는 ISO16358 전용이 아니라 여러 calculator(ISO16358 / KS C 9306 / AHRI 등)가 공유하는 정적 standard/region config 저장소이며, 각 JSON을 어느 calculator가 직접 해석하는지가 진짜 boundary임을 architecture 문서와 region config rules에 반영한다.

## Scope
- `docs/architecture/project_architecture.md`
  - `Region config vs HW candidate input` 섹션 상단에 region_configs가 ISO16358 전용 저장소가 아니라 여러 calculator가 공유하는 정적 standard/region config 저장소임을 명시.
  - `Calculator module boundary (ISO / KS / ASNZS)` 섹션에서 “region config를 사용하는 유일한 계열이다” 표현을 제거하고, ISO16358은 ISO 기반 regional profile JSON을 해석하는 대표 사례, KS는 `korea.json`을 KSC9306Calculator가 직접 해석한다는 표현으로 정정. AHRI special calculator의 `usa.json` / `usa_hspf2.json` 사용에 대한 동일 원칙 paragraph 추가.
- `data/region_configs/REGION_CONFIG_RULES.md`
  - 상단 원칙에 region_configs가 공통 정적 config 저장소이며 각 JSON을 한 calculator가 직접 해석한다는 boundary 3줄 추가 (ISO16358 regional profile / KS C 9306 korea.json / AHRI usa*.json / AS/NZS opt-in compatibility).
- `docs/WORK_PLAN.md`
  - Near-term execution order 2번 항목의 괄호 표현 “region config는 이 계열에서만 사용”을 “ISO 기반 regional profile JSON 해석을 ISO calculator에 한정”으로 정정.
- `docs/REFACTOR_PLAN.md`
  - Active refactor candidate 1번 모듈 boundary 표현 정정, region config 저장소 정책 1줄 추가, next work order 2번 표현 정정, KS C 9306 helper separation 항목의 “ISO16358 region config common path에 합치지 않는다” 문구를 “ISO16358 common path가 korea.json 같은 KS region config를 해석하지 않도록 boundary를 유지” 표현으로 정정.
- `project_log.md`
  - 2026-05-17 “Calculator architecture reset: ISO / KS / ASNZS boundary” 로그의 “region config는 ISO16358 계열에만 붙여 쓴다” 문구를 region_configs 공유 저장소 / KS는 KSC9306Calculator가 해석 / AHRI 등 다른 special calculator도 동일 원칙 / AS/NZS opt-in compatibility 분리 취지로 교체.

## Non-goals
- code / tests / fixture / workbook / reference_files / UI / profile resolver / `core/calculator_profiles.py` 수정하지 않는다.
- `data/region_configs/*.json` 값 변경 금지.
- 새 규격 수식 설명, AS/NZS 구현 계획, UI redesign 계획 추가 금지.
- 과거 project_log 전체 재작성 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `result_reports/{active,archive,summaries}` 전체 report 번호 최대값 027을 확인하고 다음 번호 028을 사용했다.
- commit 전 `git status` / `git diff --stat`로 staged 대상이 docs/architecture/project_architecture.md, data/region_configs/REGION_CONFIG_RULES.md, docs/WORK_PLAN.md, docs/REFACTOR_PLAN.md, project_log.md 5개로 한정됨을 확인했다. code / tests / fixture / region config JSON / profile resolver code / UI는 staged 대상에 포함되지 않았다.
- 전체 docs grep으로 “region config를 사용하는 유일한 계열”, “region config는 이 계열에서만 사용”, “region config는 ISO16358 계열에만 붙여 쓴다” 문구가 더 이상 active 문서에 남아 있지 않음을 확인했다 (변경 후 grep으로 검색해 잔존 없음 확인).

## Task Results
### task 1 결과
- `docs/architecture/project_architecture.md`의 `Region config vs HW candidate input` 섹션 상단에 region_configs가 ISO16358 전용 저장소가 아니라 여러 calculator가 공유하는 정적 standard/region config 저장소임을 1단락으로 명시했다.
- `Calculator module boundary (ISO / KS / ASNZS)` 섹션에서 ISO 계열 bullet의 “region config를 사용하는 유일한 계열이다” 문구를 제거하고, “Hong Kong / India / SASO / ISO T1 default 등 ISO 16358 기반 regional profile을 region config로 구현하는 대표 사례” 표현으로 교체했다.
- KS bullet에 “`data/region_configs/korea.json`을 사용할 수 있으나, 해당 config는 ISO common path가 아니라 `KSC9306Calculator`가 직접 해석해야 한다”는 boundary를 추가했다.
- AHRI special calculator의 `usa.json` / `usa_hspf2.json` 사용 원칙 1단락을 boundary 섹션 하단에 추가했다.
- ML / UI / COLUMNS 섹션은 수정하지 않았다.

### task 2 결과
- `data/region_configs/REGION_CONFIG_RULES.md` 상단 원칙 직전에 3줄 boundary 설명을 추가했다.
  - region_configs가 ISO16358 전용 저장소가 아니라 여러 calculator가 공유하는 정적 standard/region config 저장소임.
  - 각 JSON은 한 calculator가 직접 해석한다 (ISO16358은 ISO 기반 regional profile JSON, KS는 `korea.json`, AHRI는 `usa.json` / `usa_hspf2.json`).
  - AS/NZS workbook oracle compatibility는 ISO common path에 섞지 않고 별도 opt-in compatibility calculator/profile로 다룬다.
- 기존 production-only / golden 금지 / load line 등 규정은 보존했고, `## ISO 16358-2 / HSPF Load Line Rule` 섹션의 Korea 예시는 수식 재논쟁 없이 그대로 두었다.

### task 3 결과
- `docs/WORK_PLAN.md`: near-term execution order 2번 항목 괄호의 “region config는 이 계열에서만 사용”을 “ISO 기반 regional profile JSON 해석을 ISO calculator에 한정”으로 정정.
- `docs/REFACTOR_PLAN.md`: active refactor candidate 1번 ISO bullet 표현 정정, region config 저장소 정책 1줄 추가, next work order 2번 정정, KS C 9306 helper separation 항목의 “ISO16358 region config common path에 합치지 않는다” 표현을 boundary 표현으로 정정.
- 잘못된 표현이 남아 있던 두 곳을 모두 정정했고, plan 전체 구조와 실행 순서는 그대로 유지했다.

### task 4 결과
- `project_log.md` 2026-05-17 Calculator architecture reset 로그에서 ISO 모듈 설명 줄과 “region config는 ISO16358 계열에만 붙여 쓴다” 줄을 정정했다.
- 정정 후 표현:
  - ISO16358은 Hong Kong / India / SASO / ISO T1 default 등 regional profile JSON을 해석하는 대표 calculator.
  - KS C 9306 calculator는 `data/region_configs/korea.json`을 직접 해석.
  - region_configs는 여러 calculator가 공유하는 저장소이며 AHRI 등 다른 special calculator도 동일 원칙.
  - AS/NZS workbook oracle은 별도 compatibility calculator/profile로 분리.
- 이전 로그 본문, 다른 날짜 로그는 수정하지 않았다.

### task 5 결과
- `result_reports/active/028_correct-region-config-architecture.md`를 생성하고 두 단계 commit + push를 수행했다.

## Changed Files
- `docs/architecture/project_architecture.md`
- `data/region_configs/REGION_CONFIG_RULES.md`
- `docs/WORK_PLAN.md`
- `docs/REFACTOR_PLAN.md`
- `project_log.md`
- `result_reports/active/028_correct-region-config-architecture.md`

## Known Failures / Risks
- 이번 작업은 docs-only 문서 정정이며 calculator 코드 동작은 변하지 않는다.
- 현재 `core/calculator_iso16358.py`에는 여전히 KS C 9306 HSPF/CSPF에 대한 thin delegating wrapper가 남아 있고, KS region config (`data/region_configs/korea.json`)는 사용자가 `ISO16358Calculator(config_path).calculate_cspf/.calculate_hspf(...)` 형태로 호출했을 때 ISO 모듈을 거쳐 KS calculator의 해석 helper로 위임된다. 위 문서들은 “KS config는 KSC9306Calculator가 직접 해석해야 한다”는 boundary를 명시했지만, 코드 상태가 그 boundary와 100% 일치하려면 profile resolver/UI가 KS dispatch를 KSC9306Calculator로 직접 라우팅하는 후속 작업이 필요하다. 그 정렬 이전까지 문서 contract와 코드 상태가 일시적으로 불일치한다.

## Next Suggested Action
- `core/calculator_profiles.py`에 `calculator_id=ks_c9306` profile record를 추가하고, KS dispatch가 `KSC9306Calculator.from_config_path(...).calculate_cspf/.calculate_hspf(...)`로 직접 라우팅되도록 연결하는 후속 단계. 그 다음에 ISO 측 KS thin wrappers와 ISO `calculate_cspf` 내부의 `ks_intersection` 분기 정리 검토.

## Scope Compliance
- code: 수정하지 않았음
- tests: 수정하지 않았음
- fixtures: 수정하지 않았음
- workbook/reference_files: 수정하지 않았음
- UI: 수정하지 않았음
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 그대로)
- configs: `data/region_configs/*.json` 수정 없음. `REGION_CONFIG_RULES.md`만 boundary 설명 3줄 추가.
- git pull/merge/rebase: 수행하지 않았음

## Commit / Push
- source/docs commit: `76fa746 docs: correct region config architecture`
- report commit: `report: record region config architecture correction`
- pushed branch: `origin/main`
