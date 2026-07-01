# Calculator Sub-Arc — KOREA Notebook Entry & KS C 9306 UI Completion Specification

작성일: 2026-07-01  
대상 repo: `https://github.com/teeeeooo/predictor_v3`  
기준 branch: `main`  
용도: Codex/agent가 이 문서를 먼저 읽고, Sub-Arc를 slice 단위로 구현하기 위한 작업명세서

---

## 1. Sub-Arc 목표

KOREA를 calculator의 top-level notebook tab으로 추가하고, KS C 9306 CSPF/HSPF 계산 UI를 완성한다.

이번 Sub-Arc는 단순 tab 추가가 아니라, 사용자가 KOREA tab에서 다음 작업을 끝까지 수행할 수 있는 상태를 목표로 한다.

- KS C 9306 CSPF 단일 계산
- KS C 9306 HSPF 단일 계산
- CSPF/HSPF batch table 계산
- CSPF/HSPF 상세보기
- CSPF/HSPF 입력값 기반 midpoint guide table 표시
- 기존 calculator core, formula, config, profile contract 보존

---

## 2. 현재 상태 요약

### 2.1 현재 calculator shell

현재 calculator root entrypoint는 `app_calculator.py`이고, 실제 실행은 `apps.calculator.app:main`으로 위임된다.

현재 Tk calculator shell은 `apps/calculator/ui/calculator_app.py`가 소유한다. 이 shell은 Tk root window와 top-level `ttk.Notebook`을 구성하고, 현재 다음 tab만 등록한다.

- ISO 16358
- EN14825
- AHRI 210/240

따라서 KOREA는 아직 top-level tab으로 등록되어 있지 않다.

### 2.2 기존 참고 구조

KOREA top-level tab은 AHRI 210/240 tab 구조를 1순위 reference로 삼는다.

AHRI 구조:

- `apps/calculator/ui/tabs/ahri210240_tab.py`
- top-level tab 내부에 nested metric notebook
- SEER2 frame / HSPF2 frame
- 각 frame에 metric section을 붙임
- `ProfileVisibleContentLifecycleController`로 nested tab refit과 visible content lifecycle 처리

EN14825 구조는 2순위 reference다.

EN14825 구조:

- `apps/calculator/ui/tabs/en14825_tab.py`
- top-level tab 내부 nested standard notebook
- SEER / SCOP section 조립
- common input panel 동기화와 lifecycle controller 사용

KOREA는 EN14825의 common input sync까지 그대로 복제하지 않는다. metric navigation과 lifecycle/refit 조립 방식만 참고한다.

### 2.3 기존 KS C 9306 core/profile

`core/calculators/profiles.py`에는 이미 다음 profile이 존재한다.

- `ks_c9306_cspf`
- `ks_c9306_hspf`

따라서 이번 Sub-Arc는 core formula나 profile ID를 새로 만드는 작업이 아니다. 이미 존재하는 KS C 9306 profile을 UI에서 안전하게 노출하는 작업이다.

---

## 3. 핵심 설계도

### 3.1 목표 UI 구조

KOREA는 calculator의 top-level tab으로 추가한다.

구조:

- `CalculatorTkApp`
  - ISO 16358
  - EN14825
  - AHRI 210/240
  - KOREA
    - nested notebook
      - CSPF
        - single input area
        - midpoint guide table
        - result panel
        - detail view button/surface
        - batch button/dialog
      - HSPF
        - single input area
        - midpoint guide table
        - result panel
        - detail view button/surface
        - batch button/dialog

권장 파일 구조:

- `apps/calculator/ui/tabs/korea_tab.py`
- `apps/calculator/ui/sections/korea_cspf_section.py`
- `apps/calculator/ui/sections/korea_hspf_section.py`
- `apps/calculator/application/korea/`
  - `__init__.py`
  - `midpoint_guide.py`
  - `cspf_usecase.py` 또는 기존 usecase/adapter 패턴에 맞는 이름
  - `hspf_usecase.py` 또는 기존 usecase/adapter 패턴에 맞는 이름
- `apps/calculator/ui/batch_dialogs/profiles/korea_cspf.py`
- `apps/calculator/ui/batch_dialogs/profiles/korea_hspf.py`

주의:

- 실제 파일명은 기존 package naming convention을 먼저 확인한 뒤 맞춘다.
- 새 feature가 여러 책임으로 확장되므로 `apps/calculator/application/korea/`처럼 feature package를 사용하는 것을 우선한다.
- broad folder에 flat helper를 추가하지 않는다.

---

## 4. Architecture Boundary

### 4.1 Core boundary

이번 Sub-Arc에서 기존 core는 수정하지 않는다.

수정 금지:

- `core/calculators/standards/ks_c9306.py`
- `core/calculators/profiles.py`의 기존 profile ID/semantics
- `data/region_configs/korea.json`
- calculator formula
- public result dict contract
- fixture/golden expected 값

예외:

- 명백한 import path 또는 registration 누락이 발견되어도, core 수정이 필요하면 해당 slice를 중단하고 보고한다.
- core 계산 결과의 새 key를 기대하는 방식으로 UI를 설계하지 않는다.

### 4.2 UI / Application / Adapter boundary

KOREA UI는 raw formula나 core internals를 직접 계산하지 않는다.

책임 분리:

| Layer | 책임 |
| --- | --- |
| View / Section | widget 구성, 사용자 입력 수집, event forwarding |
| Controller / Usecase | 입력 DTO 구성, profile dispatch 호출, result envelope 해석 |
| Application helper | midpoint guide 계산, UI-neutral result formatting |
| Core calculator | 기존 KS C 9306 CSPF/HSPF 계산 |
| Batch profile | batch table column/row contract, row input 변환, result projection |

### 4.3 Midpoint guide boundary

Midpoint guide는 공식 KS C 9306 결과가 아니라 설계 보조값이다.

따라서:

- 기존 calculator result dict에 섞지 않는다.
- `result_panel`의 공식 metric 출력과 구분한다.
- KOREA section 내부의 별도 read-only table로 표시한다.
- helper/usecase output은 UI 표시용 DTO로 둔다.
- guide 계산 실패는 공식 계산 실패와 분리해 표시한다.

---

## 5. Midpoint Guide 설계

### 5.1 표시 항목

CSPF/HSPF 모두 동일한 형태의 small read-only table을 표시한다.

| 항목 | 값 |
| --- | --- |
| 현재 tc | `<value> °C` |
| 권장 tc | `<value> °C` |
| 권장 Mid capacity | `<value> W` |

표시하지 않는 항목:

- 현재 Mid point가 높음/낮음
- pass/fail
- 개선 필요 문구
- 자동 judgement
- 전역 최적화 해석

### 5.2 Engineering basis

`docs/iso16358/regions/ks_c_9306/ks_c_9306_design_notes.md`의 `### 6.1 Midpoint Placement of tc and Energy Minimization`을 기준으로 한다.

핵심 해석:

- KS C 9306의 3점식 전력 보간 구조에서는 energy curve가 `ta -> tc -> tb` 두 직선 구간으로 구성된다.
- `tc`는 계절 누적 소비전력에 영향을 주는 설계 판단점이다.
- engineering heuristic으로 `tc ≈ (ta + tb) / 2`를 사용한다.
- 이 관계는 전역 최적 해가 아니라 전력 분포를 균형화하는 설계 참고값이다.

### 5.3 계산 개념

CSPF/HSPF 공통 개념:

- 현재 tc: 현재 입력된 Mid/Half capacity가 building load line과 만나는 온도
- 권장 tc: `(ta + tb) / 2`
- 권장 Mid capacity: 권장 tc에서의 building load capacity

정확한 formula는 기존 KS C 9306 notes/dev_notes/glossary와 기존 core helper naming을 확인해 구현한다.

중요:

- 기존 core 내부 계산식을 복사/수정하지 않는다.
- 공식 calculation path에서 이미 산출되는 ta/tb/tc가 public result나 trace/detail에 있으면 그것을 usecase/adapter에서 읽어 사용한다.
- public result에 없으면 UI application helper에서 입력값만으로 guide를 계산한다.
- 이 helper는 pure Python이어야 하며 Tkinter를 import하지 않는다.
- helper에 fixture/golden expected를 바꾸는 의존성을 만들지 않는다.

### 5.4 CSPF midpoint guide

CSPF 입력 개념:

- STD / Full point: 35°C full
- Mid / Half point: 35°C half
- Min point: 29°C minimum

Guide:

- 현재 tc: current half capacity가 cooling building load line과 만나는 온도
- 권장 tc: `(ta + tb) / 2`
- 권장 Mid capacity: 권장 tc에서의 cooling building load

### 5.5 HSPF midpoint guide

HSPF 입력 개념:

- STD / Full point: 7°C full
- Mid / Half point: 7°C half
- Min point: 7°C minimum
- 기존 HSPF 계산에 필요한 2°C defrost, -7°C maximum 입력은 그대로 유지

Guide:

- 7°C full/half/min 기반 중온 난방 운전선의 설계 참고값
- 현재 tc: current half capacity가 heating building load line과 만나는 온도
- 권장 tc: `(ta + tb) / 2`
- 권장 Mid capacity: 권장 tc에서의 heating building load

주의:

- 2°C defrost와 -7°C maximum은 HSPF 공식 계산에는 필요하지만, midpoint guide의 기본 3점 설계 table에 억지로 섞지 않는다.
- HSPF guide 계산에서 defrost/maximum이 반드시 필요하다고 판단되면 구현을 중단하고 설계 확인을 요청한다.

---

## 6. Batch / Detail 완료 기준

### 6.1 Batch table

KOREA CSPF/HSPF는 batch table까지 완료한다.

기준:

- 기존 `apps/calculator/ui/batch/` 및 `apps/calculator/ui/batch_dialogs/profiles/` 패턴을 재사용한다.
- Hong Kong CSPF/HSPF 또는 AHRI SEER2/HSPF2 batch dialog profile을 먼저 확인한다.
- batch input columns는 single section 입력 contract와 동일한 의미를 가져야 한다.
- batch output은 공식 metric 결과와 주요 summary만 포함한다.
- midpoint guide 값은 batch output에 기본 포함하지 않는다. 사용자가 명시적으로 원하지 않았고, guide는 single UI 보조 table 성격이다.
- batch에서 guide 값을 넣고 싶다면 별도 slice로 분리한다.

### 6.2 상세보기

KOREA CSPF/HSPF는 상세보기까지 완료한다.

기준:

- 기존 EN14825/AHRI detail view 구현을 reference로 사용한다.
- 공식 result dict에서 이미 제공되는 detail/bin/trace 정보만 표시한다.
- public result dict에 없는 값을 detail view를 위해 core에 추가하지 않는다.
- detail surface는 공식 계산 상세와 midpoint guide를 섞지 않는다.
- midpoint guide는 single input 주변의 별도 guide table로 유지한다.

---

## 7. Slice Plan

### Slice 0 — Sub-Arc Design Spec & Readiness Audit

목표:

- 이 작업명세서를 repo에 추가한다.
- KOREA top-level tab 구현 전 기존 owner, reference file, tests, batch/detail patterns를 확인한다.
- 구현 세부 경계를 확정한다.

수정 허용:

- `docs/designs/2026-07-01-korea-notebook-entry-subarc-spec.md`
- `docs/WORK_PLAN.md`의 current slice/next action 최소 업데이트
- `project_log.md`는 milestone decision이 필요할 때만

금지:

- source code 수정 금지
- test expected 수정 금지
- formula/config 수정 금지

검증:

- `git diff --check`
- 문서 링크/파일명 확인
- `git status --short`

결과 보고:

- report 작성
- commit 수행
- push 금지

### Slice 1 — KOREA Top-level Tab Skeleton

목표:

- `CalculatorTkApp`에 KOREA top-level tab을 추가한다.
- KOREA tab 내부에 CSPF/HSPF nested notebook skeleton을 만든다.
- 아직 full calculation UI를 모두 완성하지 않아도 된다.
- skeleton은 import/compile 및 minimal widget construction smoke를 통과해야 한다.

수정 허용:

- `apps/calculator/ui/calculator_app.py`
- `apps/calculator/ui/tabs/korea_tab.py`
- 필요한 `__init__.py`
- focused tests

Reference:

- `apps/calculator/ui/tabs/ahri210240_tab.py`
- `apps/calculator/ui/tabs/en14825_tab.py`

금지:

- core 수정 금지
- profile ID 변경 금지
- formula/config/golden 변경 금지
- broad UI refactor 금지

검증:

- `python3 -B -m compileall -q apps/calculator tests`
- focused pytest: KOREA tab construction 또는 calculator app tab registration test
- `python3 -B tools/check_code_structure.py`
- `git diff --check`

결과 보고:

- report 작성
- commit 수행
- push 금지

### Slice 2 — KOREA CSPF Single UI + Midpoint Guide

목표:

- KOREA CSPF section을 구현한다.
- 기존 `ks_c9306_cspf` profile을 통해 계산한다.
- 입력 table과 result panel을 연결한다.
- read-only midpoint guide table을 표시한다.
- guide table 표시 항목은 `현재 tc`, `권장 tc`, `권장 Mid capacity`만 둔다.

수정 허용:

- `apps/calculator/ui/sections/korea_cspf_section.py`
- `apps/calculator/application/korea/`
- 필요한 adapter/usecase/helper
- focused tests

Reference:

- `apps/calculator/ui/sections/hong_kong_cspf_section.py`
- `apps/calculator/application/hong_kong_cspf/usecase.py`
- `apps/calculator/ui/sections/iso_iseer_2point_section.py`
- 기존 result panel/detail toggle helper

금지:

- `core/calculators/standards/ks_c9306.py` 수정 금지
- `data/region_configs/korea.json` 수정 금지
- public result dict contract 변경 금지
- expected/golden 변경 금지
- guide 값을 공식 result로 편입 금지

검증:

- `python3 -B -m compileall -q apps/calculator tests`
- focused pytest: KOREA CSPF usecase/helper/section
- existing KS C 9306 focused tests
- `python3 -B tools/check_code_structure.py`
- `git diff --check`

결과 보고:

- report 작성
- commit 수행
- push 금지

### Slice 3 — KOREA HSPF Single UI + Midpoint Guide

목표:

- KOREA HSPF section을 구현한다.
- 기존 `ks_c9306_hspf` profile을 통해 계산한다.
- 입력 table과 result panel을 연결한다.
- read-only midpoint guide table을 표시한다.
- HSPF의 2°C defrost, -7°C maximum 입력은 기존 공식 계산에 맞게 유지한다.
- midpoint guide는 7°C full/half/min 기반 중온 난방 설계 참고값으로 분리한다.

수정 허용:

- `apps/calculator/ui/sections/korea_hspf_section.py`
- `apps/calculator/application/korea/`
- focused tests

Reference:

- `apps/calculator/ui/sections/hong_kong_hspf_section.py`
- `apps/calculator/application/hong_kong_hspf/usecase.py`
- `apps/calculator/ui/sections/ahri_hspf2_section.py`

금지:

- core/formula/config/profile 변경 금지
- HSPF expected/golden 변경 금지
- defrost/maximum을 midpoint guide에 억지로 섞기 금지
- guide 값을 공식 result/detail로 편입 금지

검증:

- `python3 -B -m compileall -q apps/calculator tests`
- focused pytest: KOREA HSPF usecase/helper/section
- existing HSPF/KS focused tests
- `python3 -B tools/check_code_structure.py`
- `git diff --check`

결과 보고:

- report 작성
- commit 수행
- push 금지

### Slice 4 — KOREA Batch Dialogs

목표:

- KOREA CSPF/HSPF batch table을 구현한다.
- 기존 batch shell/profile architecture를 재사용한다.
- single section과 batch input/output 의미가 일치해야 한다.

수정 허용:

- `apps/calculator/ui/batch_dialogs/profiles/korea_cspf.py`
- `apps/calculator/ui/batch_dialogs/profiles/korea_hspf.py`
- section의 batch button wiring
- focused batch tests

Reference:

- `apps/calculator/ui/batch_dialogs/profiles/hong_kong_cspf.py`
- `apps/calculator/ui/batch_dialogs/profiles/hong_kong_hspf.py`
- `apps/calculator/ui/batch_dialogs/profiles/ahri_seer2.py`
- `apps/calculator/ui/batch/controller.py`
- `apps/calculator/ui/batch/matrix_table.py`

금지:

- batch framework 재작성 금지
- unrelated profile batch 수정 금지
- guide 값을 batch output에 추가 금지
- fixture/golden expected 변경 금지

검증:

- `python3 -B -m compileall -q apps/calculator tests`
- focused pytest: KOREA batch profile/controller
- related existing batch tests
- `python3 -B tools/check_code_structure.py`
- `git diff --check`

결과 보고:

- report 작성
- commit 수행
- push 금지

### Slice 5 — KOREA Detail View

목표:

- KOREA CSPF/HSPF 상세보기를 구현한다.
- 기존 EN14825/AHRI detail view surface를 reference로 사용한다.
- 공식 calculation detail/bin/trace만 보여준다.
- midpoint guide는 detail view에 넣지 않는다.

수정 허용:

- KOREA section detail wiring
- detail adapter/helper if needed
- focused tests

Reference:

- `docs/designs/2026-06-21-en14825-ahri-detail-view-design.md`
- existing EN14825 SEER/SCOP detail implementation
- existing AHRI SEER2/HSPF2 detail implementation

금지:

- core result dict key 추가 금지
- formula/config 변경 금지
- unrelated detail surface refactor 금지
- midpoint guide와 공식 detail 혼합 금지

검증:

- `python3 -B -m compileall -q apps/calculator tests`
- focused pytest: KOREA detail view/adapter
- existing detail tests if present
- `python3 -B tools/check_code_structure.py`
- `git diff --check`

결과 보고:

- report 작성
- commit 수행
- push 금지

### Slice 6 — KOREA Sub-Arc Closeout / Manual Smoke Prep

목표:

- KOREA CSPF/HSPF single, batch, detail, midpoint guide가 모두 연결되었는지 closeout한다.
- docs/work plan/report lifecycle를 정리한다.
- manual smoke checklist를 작성한다.
- 모든 slice commit 완료 후 push한다.

수정 허용:

- `docs/WORK_PLAN.md`
- `project_brief.md`는 Phase/Arc map 변경이 필요한 경우만
- `project_log.md`는 milestone decision이 필요한 경우만
- result summary/report lifecycle files
- manual smoke guide update if appropriate

검증:

- `python3 -B -m compileall -q apps/calculator core/calculators tests`
- focused pytest for KOREA + related calculator UI/application/batch/detail tests
- `python3 -B tools/check_code_structure.py`
- `git diff --check`
- `git status --short`
- active report count check per report workflow

결과 보고:

- report 작성
- summary/archive 필요 시 lifecycle cleanup
- all slice commits 확인
- push 수행
- final report에 commit hash / push 여부 / manual smoke 필요 항목 보고

---

## 8. Agent Execution Prompt Template

아래 prompt는 각 slice를 실행할 때 사용한다. `{SLICE_NAME}`과 `{SLICE_SCOPE}`만 실제 slice에 맞게 바꾼다.

[PROMPT START]

AGENTS.md는 현재 세션에서 이미 확인했다면 다시 읽지 않는다.  
AGENT_TASK_ROUTER.md는 이번 작업 유형에 필요한 섹션만 확인한다.  
AGENTS_FULL.md는 존재하지 않으므로 언급하지 않는다.

[작업]
Calculator Sub-Arc — KOREA Notebook Entry & KS C 9306 UI Completion
{SLICE_NAME}

[우선 읽기]
1. docs/designs/2026-07-01-korea-notebook-entry-subarc-spec.md
2. docs/WORK_PLAN.md
3. AGENTS.md
4. AGENT_TASK_ROUTER.md의 필요한 섹션만
5. 이번 slice의 Reference 파일만 필요한 범위로 확인

[목적]
{SLICE_SCOPE}

[수정 허용]
이번 slice에 명시된 파일/패키지만 수정한다.

[금지]
- 기존 core KS C 9306 formula 수정 금지
- config semantics 변경 금지
- profile ID 변경 금지
- fixture/golden expected 변경 금지
- public result dict contract 변경 금지
- unrelated calculator refactor 금지
- unrelated Train/Predict 수정 금지
- unrelated report lifecycle 이동 금지
- push 금지. 단, Slice 6 closeout에서만 push 허용

[구현 원칙]
- AHRI 210/240 tab 구조를 KOREA top-level tab primary reference로 사용한다.
- EN14825 tab은 lifecycle/refit/reference로만 사용한다.
- UI section은 widget 구성과 event forwarding만 소유한다.
- 계산 orchestration, input envelope, midpoint guide 계산은 application/helper 경계에 둔다.
- midpoint guide는 공식 result가 아니라 read-only design helper table이다.
- midpoint guide 항목은 현재 tc, 권장 tc, 권장 Mid capacity만 표시한다.
- batch output에는 midpoint guide 값을 기본 포함하지 않는다.
- detail view에는 midpoint guide를 섞지 않는다.

[검증]
- python3 -B -m compileall -q apps/calculator tests
- 이번 slice focused pytest
- python3 -B tools/check_code_structure.py
- git diff --check
- git status --short

[결과 보고 형식]
task 1: OK/NG - short summary
task 2: OK/NG - short summary
modified: ...
report: ...
commit: ...

[PROMPT END]

---

## 9. Manual Smoke Checklist

모든 slice 완료 후 사용자가 확인할 항목:

1. `python app_calculator.py` 실행
2. top-level notebook에 `KOREA` tab 표시
3. KOREA tab 내부에 `CSPF`, `HSPF` sub-tab 표시
4. CSPF 입력 table에 값 입력 후 계산 결과 표시
5. CSPF midpoint guide table 표시
   - 현재 tc
   - 권장 tc
   - 권장 Mid capacity
6. HSPF 입력 table에 값 입력 후 계산 결과 표시
7. HSPF midpoint guide table 표시
   - 현재 tc
   - 권장 tc
   - 권장 Mid capacity
8. CSPF batch dialog 열림
9. CSPF batch table 입력/계산 가능
10. HSPF batch dialog 열림
11. HSPF batch table 입력/계산 가능
12. CSPF 상세보기 열림
13. HSPF 상세보기 열림
14. tab 전환 후 window refit 이상 없음
15. 기존 ISO/EN14825/AHRI tab 기능 회귀 없음

---

## 10. Open Questions / Stop Conditions

아래 상황이 발생하면 구현을 멈추고 보고한다.

1. 기존 KS C 9306 public result에 ta/tb/tc 또는 midpoint guide 계산에 필요한 값이 없어, core 수정 없이는 정확한 guide 계산이 불가능한 경우
2. HSPF midpoint guide 계산에 defrost/maximum point를 포함해야 하는지 불명확한 경우
3. KOREA batch table을 기존 batch framework로 구현하기 어려워 framework 변경이 필요한 경우
4. 상세보기를 위해 core result dict에 새 key를 추가해야 하는 경우
5. KOREA section이 250 LOC를 크게 넘거나 한 파일에 View/Controller/Adapter/Policy가 섞이는 경우
6. 기존 KS C 9306 golden 또는 fixture expected 변경이 필요해 보이는 경우

---

## 11. Completion Definition

Sub-Arc 완료 조건:

- KOREA top-level tab이 존재한다.
- CSPF/HSPF single UI가 계산 가능하다.
- CSPF/HSPF midpoint guide table이 표시된다.
- CSPF/HSPF batch table이 작동한다.
- CSPF/HSPF 상세보기가 작동한다.
- 기존 core KS C 9306 formula와 public result contract는 변경되지 않는다.
- 기존 profile ID/config semantics/golden expected는 변경되지 않는다.
- focused tests와 structure guard가 통과한다.
- 각 slice는 commit되어 있다.
- Slice 6 closeout에서 전체 push가 완료되어 있다.
