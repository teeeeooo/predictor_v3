# Design Gate Summary

> **Harness V2 note (2026-09-07):** AHRI documentation/owner corrections in this plan remain useful evidence. Instructions to create correction Result Records, update REPORT_INDEX, or perform `memory_review` are superseded by Agent Harness V2; use current owner docs plus selective decision/failure memory instead.

## Goal

최근 AHRI Appendix M 변경(`f7adcac7..HEAD`)이 predictor_v3의 문서 규칙과
현재 owner 경계를 따르도록 문서 자산을 동기화한다. 대상은 Appendix M과
Appendix M1의 구분, 표준 문서의 SSOT, Tkinter table adapter의 현재 구현명,
최근 UI/batch 변경의 Result Record 추적성이다.

## Confirmed Decisions

- 이번 수정 범위는 문서와 문서 lifecycle 자산으로 한정한다. Calculator
  formula, config, public API, UI source, test behavior는 변경하지 않는다.
- AHRI 표준의 장기 재사용 문서는 `docs/ahri210240/`의 notes/dev/design/
  glossary 4종이 소유한다. `docs/designs/`의 AHRI audit spec은 현재
  decision evidence와 설계 gate로 유지하되 표준 문서의 대체물로 취급하지
  않는다.
- Appendix M은 AHRI 210/240-2017 with Addendum 1의 variable-speed,
  non-ducted single-split, Region IV SEER/HSPF 경로로 명시하고, Appendix M1
  의 2026 SEER2/HSPF2 경로와 formula/config/profile/UI owner를 분리한다.
- 기존 Result Record는 append-only이므로 수정하지 않는다. `324235d1`의
  table/batch decision evidence는 독립 추적성이 필요하다고 판정했으므로 같은
  날짜의 새 correction record와 index row를 추가하고 `memory_review:
  no-change`를 명시한다.
- 공용 table contract는 이미 interaction baseline을 소유하므로 중복 설명을
  늘리지 않는다. 현재 구현명과 dynamic `refresh()` binding 책임은 Tkinter
  adapter와 AHRI active design evidence에 맞춰 정리한다.

## Core vs Handler Boundary

| Boundary | Owner | Planned responsibility |
| --- | --- | --- |
| Standard reference and calculation meaning | `docs/ahri210240/` | M/M1 scope, inputs/outputs, formula references, config ownership, golden and implementation caveats |
| Product/design interpretation | `ahri210240_design_notes.md` | M/M1이 제품 성능·설계 해석에 주는 의미; code filename/function/variable은 기재하지 않음 |
| UI interaction contract | `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` and Tkinter adapter | 공통 table baseline과 현재 `TkTableController` 구현 연결; M 고유 field/label은 AHRI design doc에 둠 |
| Active decision evidence | `docs/designs/2026-09-01-ahri-210-240-m-seer-hspf-audit-design-spec.md` | superseded no-batch 문구, M/M1 owner split, M table controller/refresh decision |
| Historical change evidence | `result_reports/records/` | 기존 기록 보존; 필요한 경우 correction record만 추가 |
| Fast recall | `result_reports/memory/project_memory_seed.md` | 장기 invariant가 실제로 변할 때만 갱신; 이번 문서 동기화만으로는 기본 no-change |

## Data Shape / API Boundary

- 표준 문서는 canonical domain keys와 UI display labels를 구분한다. 예를
  들어 `H2V`/`H1N`와 `H2v`/`H1N(STD)`, 그리고 `EV`와 `Ev`를 혼용하지
  않는다.
- M result display names(`CSTL`, `CSEC`, `Heating Load`, `Compressor
  Input`, `Auxiliary Input`)는 UI presentation 설명으로 기록하고, 기존
  result key나 public JSON/API contract를 변경하는 것으로 해석하지 않는다.
- M HSPF의 optional H12/H22, demand-defrost timing, read-only calculated
  credit, H42 제외 범위는 M standard/dev notes와 glossary에 각각 필요한
  수준으로 연결한다. M1의 HSPF2 input schema를 M에 복사하지 않는다.
- UI table의 physical selection은 table별로 독립적이며 cross-table
  selection/paste를 새 contract로 만들지 않는다.

## Required Tests

문서만 바꾸는 단계에서는 source behavior test를 수정하지 않는다. 구현 후
다음 검증을 수행한다.

- `rg`로 active AHRI docs에서 M/M1 scope, `usa_m_seer.json`,
  `usa_m_hspf.json`, M golden, H42 boundary가 모두 discoverable한지 확인한다.
- `rg`로 active UI docs의 현재 controller 명칭을 검사하고,
  `ExcelLikeTableController`가 current implementation으로 남아 있지 않은지
  확인한다. 역사 문맥으로 남길 경우 retired/migration임을 명시한다.
- standard docs가 `DOCS_GUIDELINES.md`의 4-file 역할 분리, 근거 표기,
  glossary SSOT, design_notes의 code-free 규칙을 지키는지 수동 점검한다.
- Result Record를 추가할 때 `python3 -B tools/check_agent_change_gate.py
  --cached`로 path/index/memory metadata를 검증한다.
- 문서 변경의 형식은 `git diff --check`로 확인한다. source 변경이 없으므로
  `check_code_structure.py`는 필수 검증 대상이 아니며, 기존 source behavior가
  오염되지 않았는지는 `git diff --name-only`로 확인한다.
- 문서 동기화 후 회귀 확인이 필요하면 기존 baseline으로
  `PYTHONPATH=. pytest -q -k ahri`와 최신 M UI/table focused tests를
  재실행한다. 공식 calculator 재검증이나 manual GUI smoke는 이번 문서
  계획의 acceptance에 포함하지 않는다.

## Migration / Refactor Path

1. 현재 AHRI standard docs와 README의 owner 범위를 inventory하고, 기존
   HSPF2/SEER2 문장을 보존할 부분과 M/M1 공통 family 설명을 추가할 부분을
   분리한다.
2. `ahri210240_notes.md`에 M/M1 scope, input/output schema, formula/code
   mapping, config와 accepted golden을 추가한다.
3. `ahri210240_dev_notes.md`에 M 전용 구현 주의점, M1 재사용 금지 경계,
   batch/UI adapter와 focused test pointer를 추가한다.
4. `ahri210240_design_notes.md`에는 code reference 없이 M/M1의 제품 설계
   영향과 SEER/HSPF 결과 해석을 추가하고, `ahri210240_glossary.md`에는
   M 전용 표준 용어와 schema/display alias를 단일 출처로 추가한다.
5. `docs/ahri210240/README.md`에 active AHRI Appendix M design/spec와
   표준 문서의 현재 역할을 연결한다.
6. `TKINTER_TABLE_ADAPTER.md`의 current controller 표기를
   `TkTableController`로 교정하고, `ExcelLikeTableController`는 필요한
   경우 retired migration history로만 표시한다.
7. `324235d1`의 독립 decision evidence가 필요하므로 기존 record를 고치지
   않고 `2026-09-02-ahri-m-documentation-sync.md` correction record와 index
   row를 추가한다.
8. 문서 index와 검증 결과를 확인하고, source/test 변경 없이 문서 작업으로
   close한다.

## Risks

- 기존 AHRI notes는 2026 HSPF2/SEER2 기준이고 M은 2017 Addendum 1
  경로이므로, 공통 family 설명을 추가하면서 standard edition을 섞지
  않아야 한다.
- `docs/designs/`의 긴 active spec을 표준 notes에 그대로 복사하면 SSOT가
  중복된다. 표준 문서에는 재사용 가능한 현재 상태만 요약하고 spec 링크를
  둔다.
- controller 이름을 일괄 치환할 때 legacy design/archive 문서까지 수정하면
  append-only/historical boundary를 침범할 수 있다. active 문서만 대상에
  둔다.
- correction record를 추가할지 여부는 commit 단위가 아니라 decision slice
  단위로 판단해야 하며, 불필요한 report 증가를 피한다.

## Non-goals

- AHRI M/M1 계산식, region config, fixture/golden 값의 변경
- Calculator public API, capability, profile, JSON key의 변경
- Tkinter controller 구현, table interaction behavior, UI label의 변경
- 기존 Result Record/project log/memory seed의 소급 수정
- 공식 AHRI calculator 또는 수동 GUI acceptance 재실행
- legacy 문서 archive 정리나 대규모 문서 트리 refactor

## Next Codex Implementation Prompt

`docs/designs/2026-09-02-ahri-documentation-sync-plan.md`를 기준으로 문서
동기화를 구현하라. 먼저 Goal / Scope / Non-goals / Verification을 확인하고,
`docs/ahri210240/`의 4개 standard owner 문서와 README, active Tkinter
adapter만 수정하라. 기존 Result Record는 수정하지 말고, `324235d1`의
decision evidence가 별도 correction record를 요구하는지 먼저 판정하라.
M/M1 formula/config/API/UI source는 변경하지 않는다. 문서 근거와
code-free design_notes 규칙을 지키고, 마지막에 `git diff --check`, active
문서 검색, 필요한 change gate와 focused regression 결과를 보고하라.

## Execution Result

이 계획은 2026-09-02에 실행되었다. AHRI M/M1 owner 문서 4종과 README,
Tkinter adapter, active design index 및 append-only correction record를
동기화했고, staged 변경에는 `docs/`와 `result_reports/` 경로만 포함했다.
`agent change gate`와 `git diff --check`를 통과했으며,
`PYTHONPATH=. pytest -q -k ahri`는 `208 passed`였다. Calculator source와
test source는 변경하지 않았다.
