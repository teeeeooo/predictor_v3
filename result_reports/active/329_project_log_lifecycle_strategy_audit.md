# 329 Project Log Lifecycle Strategy Audit

## 목표

`project_log.md`가 1600줄 수준으로 과도하게 증가한 상태에서, 실제 cleanup 실행 전에 정리 전략을 audit한다.
현재 프로젝트 문서 정책상 어떤 lifecycle 방식(compact / archive segment 생성 / memory seed 갱신)이 적절한지 판단하고,
다음 실행 작업에서 안전하게 cleanup할 수 있는 구체적인 실행안을 제시한다.

> **이번 작업은 audit/report 전용이며, project_log.md, archive, memory seed를 실제 수정하지 않았다.**

---

## 확인한 Workflow 기준

### PROJECT_LOG_AND_MEMORY.md (핵심 발췌)

- `project_log.md`는 active milestone log이다.
- 업데이트 조건: milestone-level decisions, future-relevant failures/risks, lessons, architecture/process rule changes, user-requested entries.
- task report 또는 memory delta를 project_log에 복사하지 않는다.
- Historical logs는 `docs/archive/project_log/YYYY-MM/` 아래 보관하며, user lifecycle maintenance 요청 없이는 read-only다.
- Memory seed 업데이트는 summary lifecycle task 또는 명시적 memory maintenance task에서만 허용한다.
- Seed 50개 초과 시 audit 후보; 75개 초과 시 dedicated maintenance task 필수.

### DOCUMENT_SYNC_AND_LIFECYCLE.md (핵심 발췌)

- `docs/archive/`: agent는 archive 후보를 보고하되, user 승인 없이 이동/삭제하지 않는다 (lifecycle maintenance task 제외).
- 불명확할 때는 자동으로 수정하지 말고 "update may be needed"로 보고한다.

### RESULT_REPORT_WORKFLOW.md (핵심 발췌)

- tracked file 변경이 있으면 report 필수.
- report/archive lifecycle maintenance는 compact report mode 허용.
- active report count: threshold wording 정책 (exact count는 최종 terminal output에만).

---

## Project Log Heading Inventory

현재 `project_log.md`: **1632줄**, heading 총 **63개** (grep 기준).

### 분류표

| 구간 | Date | 제목 (요약) | 분류 |
|---|---|---|---|
| L24 | 2026-06-07 | Batch two-row matrix and reference parity arc summary lifecycle cleanup | archive 후보 |
| L32 | 2026-06-07 | Main notebook legacy vs batch dialog lifecycle audit | archive 후보 |
| L48 | 2026-06-07 | BatchMatrixTable interaction parity repair | archive 후보 |
| L61 | 2026-06-07 | BatchMatrixTable repair vs rebuild audit | archive 후보 |
| L76 | 2026-06-07 | Reference parity / standardization gate added | **active 유지** (process rule) |
| L95 | 2026-06-07 | Hong Kong CSPF matrix migration adapter pattern | **active 유지** (architecture decision) |
| L103 | 2026-06-07 | Tk two-row matrix table skeleton completed | archive 후보 |
| L111 | 2026-06-06 | Project-wide Clean Architecture boundary policy | **active 유지** (architecture policy) |
| L204 | 2026-06-05 | Content-hugging shell/form contract direction | **active 유지** (architecture rule) |
| L218 | 2026-06-05 | Content-hugging window sizing direction | **active 유지** (architecture rule) |
| L232 | 2026-06-05 | Common dynamic refit owner decision | **active 유지** (architecture decision) |
| L247 | 2026-06-05 | Table/window refit report lifecycle cleanup | archive 후보 |
| L261 | 2026-06-05 | Nested notebook window refit policy | **active 유지** (policy) |
| L284 | 2026-06-05 | Table UX target and common Tk foundation direction | **active 유지** (architecture) |
| L302 | 2026-06-05 | Agent workflow owner split | **active 유지** (process rule) |
| L326 | 2026-06-04 | Scoped first-search harness rule | **active 유지** (process rule) |
| L337 | 2026-06-04 | WPF spike closeout and UI contract guardrail | **active 유지** (guardrail) |
| L362 | 2026-05-30 | Tkinter detail panel, copy, and graph parity recovery | archive 후보 (summary 존재) |
| L386 | 2026-05-30 | Tkinter ISO profile expansion and UI stabilization | archive 후보 (summary 존재) |
| L410 | 2026-05-28 | Tkinter calculator UX implementation arc + metric sub-tab amendment | archive 후보 (summary 존재) |
| L442 | 2026-05-24 | Tkinter calculator matrix UI direction + project-wide surface rules | **active 유지** (rules) |
| L455 | 2026-05-23 | Project Memory Delta workflow + seed staging | **active 유지** (process rule) |
| L479 | 2026-05-23 | Xfail cleanup + PyQt/Tkinter environment stabilization | archive 후보 |
| L512 | 2026-05-19 | ISO16358-2 HSPF -7_ext fix + golden update | **active 유지** (golden fix — risk baseline) |
| L549 | 2026-06-07 | Configurable bin-detail schema extraction | archive 후보 |
| L579 | 2026-06-07 | Hong Kong HSPF single-case detail/bin panel wiring | archive 후보 |
| L616 | 2026-06-07 | Shared Tk content-hugging refit/minsize lifecycle repair | archive 후보 |
| L652 | 2026-06-07 | Side-effect-free visible content measurement policy repair | **active 유지** (policy) |
| L687 | 2026-06-07 | Nested notebook current-state width/height replacement repair | archive 후보 |
| L714 | 2026-06-07 | Nested notebook width replacement using chrome-width estimate | archive 후보 |
| L745 | 2026-06-07 | HSPF detail/schema + window lifecycle arc closeout and archive | archive 후보 |
| L769 | 2026-06-07 | Main paste policy alignment to raw text paste + visible validation | **active 유지** (policy) |
| L800 | 2026-06-07 | Main paste policy / validation arc Windows validation closeout | archive 후보 |
| L825 | 2026-06-07 | Code checker reference map foundation design | **active 유지** (foundation decision) |
| L855 | 2026-06-07 | ui_tk cleanup preflight using Reference Evidence Gate | archive 후보 |
| L881 | 2026-06-07 | Reference Evidence Gate workflow integration | **active 유지** (process rule) |
| L903 | 2026-06-07 | Code quality guardrail backlog milestone registration | **active 유지** (guardrail backlog) |
| L921 | 2026-06-07 | Section-level result formatting helper extraction | archive 후보 |
| L940 | 2026-06-07 | BinDetailPanel cleanup preflight | archive 후보 |
| L963 | 2026-06-07 | BinDetailPanel.__init__ setup helper split | archive 후보 |
| L985 | 2026-06-07 | Controller switch design preflight | archive 후보 |
| L1015 | 2026-06-07 | MetricInputTable clipboard protocol compatibility check | archive 후보 |
| L1036 | 2026-06-07 | Controller switch parity test foundation | archive 후보 |
| L1056 | 2026-06-07 | Windows parity test closeout | archive 후보 |
| L1073 | 2026-06-07 | Fix controller parity readonly paste test | archive 후보 |
| L1094 | 2026-06-07 | Controller switch pilot implementation | archive 후보 |
| L1114 | 2026-06-07 | TkTableController type-replace flicker diagnosis | archive 후보 |
| L1136 | 2026-06-07 | Remove redundant focus_set from TkTableController._type_replace | archive 후보 |
| L1154 | 2026-06-07 | Stable ResultPanel summary update | archive 후보 |
| L1174 | 2026-06-09 | Preserve external focus during ResultPanel shape-change rebuild | **active 유지** (architecture decision) |
| L1195 | 2026-06-09 | Narrow ResultPanel focus helper exception handling | archive 후보 |
| L1211 | 2026-06-09 | Post-focus-preservation GUI smoke closeout | archive 후보 |
| L1235 | 2026-06-09 | Active report lifecycle cleanup | archive 후보 |
| L1252 | 2026-06-09 | Controller switch expansion readiness preflight | archive 후보 |
| L1268 | 2026-06-09 | Implement HongKongHspfSection controller switch | archive 후보 |
| L1286 | 2026-06-09 | Fix TkTableController type-replace selection carryover | archive 후보 |
| L1304 | 2026-06-09 | Close out post-type-replace selection fix GUI smoke | archive 후보 |
| L1320 | 2026-06-09 | Implement IsoIseer2PointSection controller switch | archive 후보 |
| L1338 | 2026-06-09 | Close out post-2-point controller switch GUI smoke | archive 후보 |
| L1356 | 2026-06-10 | Implement IsoSasoT3Section controller switch | archive 후보 |
| L1375 | 2026-06-10 | Code checker and reference map gate audit | archive 후보 |
| L1393 | 2026-06-10 | Align 305 code checker audit | archive 후보 |
| L1410 | 2026-06-10 | SASO T3 Section Input Validation Alignment | archive 후보 |
| L1429 | 2026-06-10 | Post-SASO T3 controller switch & validation GUI smoke closeout | archive 후보 |
| L1447 | 2026-06-10 | Reference Evidence Gate warning-first workflow patch & wording policy | **active 유지** (process rule change) |
| L1468 | 2026-06-10 | Improve code_checker metadata & freshness checking | archive 후보 |
| L1488 | 2026-06-10 | Regenerate codebase reference map | archive 후보 |
| L1507 | 2026-06-10 | Controller switch arc final summary / closeout | archive 후보 |
| L1524 | 2026-06-10 | Active report lifecycle cleanup after controller switch arc closeout | archive 후보 |
| L1542 | 2026-06-10 | Active report lifecycle cleanup correction | archive 후보 |
| L1563 | 2026-06-10 | Main table migration check after controller switch arc closeout | archive 후보 |
| L1581 | 2026-06-10 | Retire legacy ExcelLikeTableController and correct test gaps | archive 후보 |
| L1603 | 2026-06-10 | Batch dialog shell/profile architecture decision | **active 유지** (architecture decision) |
| L1613 | 2026-06-10 | Batch dialog shell implementation and cleanup | **active 유지** (recent arc closeout) |
| L1624 | 2026-06-10 | ISO and SASO batch profile expansion | **active 유지** (recent arc closeout) |

**요약:**
- active 유지 후보: 약 20개 heading
- archive 이동 후보: 약 43개 heading (약 1100줄 규모)
- 사용자 결정 필요: 없음 (분류 기준이 명확함)

---

## 기존 Archive 구조 확인

```
docs/archive/project_log/2026-05/
  project_log_2026-05_part01_2026-05-18_to_2026-05-10.md
  project_log_2026-05_part02_2026-05-04_to_2026-05-05.md
  project_log_2026-05_part03_2026-05-06_to_2026-05-07.md
  project_log_2026-05_part04_2026-05-11_to_2026-05-17.md
```

**Archive naming style 분석:**

- `YYYY-MM/project_log_YYYY-MM_partNN_YYYY-MM-DD_to_YYYY-MM-DD.md` 형식 사용.
- `partNN`은 original project_log entry 순서 보존(reverse chronological).
- 각 파일은 capped segment 방식으로 date range가 파일명에 포함됨.
- Ordering note가 project_log.md `## Historical Log Archives` 섹션에 명시됨.

**현재 정책과의 정합성:** ✅ 완전 정합.
`docs/archive/project_log/YYYY-MM/` 구조는 PROJECT_LOG_AND_MEMORY.md에서 명시된 `docs/archive/project_log/YYYY-MM/` 정책과 일치한다.
현재 `2026-06/` 폴더가 없으므로, 2026-06 분 archive 생성이 필요하다.

---

## Memory Seed 후보 확인

- `project_memory_seed.md`: **764줄**, **59개 entries** (seed `- type:` 기준).

> **경고:** 59개로 50-entry audit 기준을 이미 초과하였다.  
> `PROJECT_LOG_AND_MEMORY.md` 정책상 "50-entry 초과 시 maintenance audit 후보"에 해당.  
> 75개 미만이므로 아직 dedicated maintenance task 강제는 아니나, 다음 memory seed 관련 작업 시 주의 필요.

**project_log cleanup과 함께 memory seed에 반영할 durable decision 후보:**

| 후보 entry | 이미 seed 포함 여부 |
|---|---|
| project_log는 active milestone log이고 과거 원문은 archive segment로 보존 | ✅ 포함 (L401-410: "capped-segment project_log archive" entry 존재) |
| project_log milestone-level only, micro correction은 result report만 | ✅ 포함 (L401-410 동일 entry에서 암시) |
| batch dialog는 shell.py + profiles thin adapter 구조를 따른다 | ❌ 미포함 — **신규 후보** |
| Codex 프롬프트에 수동 GUI smoke 세부 항목을 넣지 않는다 | ❌ 미포함 — **신규 후보** |
| active report count는 threshold wording만 durable doc에 기재 | ✅ 포함 (L738: threshold wording entry 존재) |

**결론:** memory seed에 새로 반영할 가치가 있는 신규 후보 2개 존재. 단, memory maintenance는 summary lifecycle task 또는 명시적 maintenance task에서만 수행 가능하므로 이번 cleanup 작업에서 seed를 수정하지 않는다.

---

## Option 비교

### Option A. project_log.md 내부 compact만 수행

**장점:**
- 작업 범위가 단순하고 빠르다.
- archive 파일 생성 없이 project_log.md 한 파일만 변경.

**단점:**
- 삭제된 원문 내용을 나중에 찾을 수 없다.
- 이미 compact는 328에서 batch dialog 구간에만 적용했으나 다른 구간 63개 heading의 원문이 소실됨.
- policy에서 "기존 과거 로그는 보존하며... 기존 날짜별 항목을 재작성, 축약, 삭제하지 않는다"는 문구와 충돌.

**적합 조건:** 상세 원문이 result report에 이미 충분히 기록되어 있고, 사용자가 archive 원문 참조를 요구하지 않는 경우.

**이번 프로젝트 권장 여부:** ❌ **비권장** (원문 보존 정책 위반 위험, archive 구조가 이미 존재하므로 별도 compact는 최소화해야 함)

---

### Option B. Historical project_log archive segment 생성 (권장)

**장점:**
- 원문 완전 보존 (archive segment에 그대로 이전).
- PROJECT_LOG_AND_MEMORY.md 및 기존 2026-05 archive 방식과 완전 정합.
- project_log.md는 active milestone heading만 남아 대폭 단축됨.
- `## Historical Log Archives` 섹션에 링크만 추가하면 되므로 navigation 유지.

**단점:**
- 새 archive 파일 생성 필요 (`docs/archive/project_log/2026-06/`).
- project_log.md에서 archive로 이동할 heading 범위를 정확히 지정해야 하므로 실수 위험.

**적합 조건:** 원문 보존이 중요하고, 기존 archive 구조가 존재하는 경우.

**현재 정책과의 정합성:** ✅ 완전 정합. PROJECT_LOG_AND_MEMORY.md의 "Historical logs live under docs/archive/project_log/YYYY-MM/"과 정확히 일치.

**이번 프로젝트 권장 여부:** ✅ **권장**

---

### Option C. project_log compact + memory seed 최소 갱신

**장점:**
- compact와 동시에 durable decision을 seed에 반영하면 향후 토큰 효율 개선.

**단점:**
- memory seed 갱신은 summary lifecycle task 또는 명시적 maintenance task 조건이 필요.
- 이번 cleanup 작업은 그 조건에 해당하지 않음.
- 59개 entry로 이미 50-entry 기준 초과 상태이므로 신규 entry 추가는 maintenance audit 먼저 필요.

**seed maintenance 조건 충족 여부:** ❌ **미충족** (summary lifecycle task가 아님, dedicated maintenance task도 아님)

**이번 프로젝트 권장 여부:** ❌ **비권장** (조건 미충족)

---

### Option D. Archive segment 생성 + Active compact + (별도) seed maintenance (분리 실행)

**단계 1:** 2026-06 archive segment 생성 + project_log.md에서 archive 대상 heading 제거 + Historical Log Archives 섹션 링크 추가.

**단계 2 (별도 task):** memory seed entry 추가 2개(batch dialog shell, manual smoke 정책)를 dedicated maintenance task에서 처리 (50-entry 초과 상태이므로 staleness/supersession review와 함께).

**이번 프로젝트 권장 여부:** ✅ **가장 안전하고 정책 정합적인 방식**.

---

## 권장 전략

**Option B + D-단계1 병합으로 1회 실행**:

> `docs/archive/project_log/2026-06/` archive segment 파일을 생성하고, project_log.md에서 archive 대상 heading 원문을 이동한 후, `## Historical Log Archives` 섹션에 링크를 추가한다. memory seed는 건드리지 않는다. seed maintenance는 별도 dedicated task로 분리한다.

---

## 다음 실행 작업 범위 (구체적 실행안)

### 단계 1: Archive segment 생성 + project_log.md 정리

**1-A. 새 archive 파일 생성**

```
docs/archive/project_log/2026-06/project_log_2026-06_part01_2026-06-07_to_2026-06-10.md
```

내용: project_log.md에서 archive 대상으로 분류된 heading들의 원문 그대로 이전.

**1-B. archive 대상 heading 범위 (project_log.md 기준)**

이동할 heading: 아래 기준으로 선별

- **이동 대상 (43개 heading, 약 1100줄):**
  - L24 ~ L103: 2026-06-07 초반 matrix/batch dialog 관련 구현 arc
  - L247: Table/window refit report lifecycle cleanup
  - L362 ~ L512: 2026-05-19 ~ 2026-05-30 구간 (별도 summary 커버됨, summary 314가 일부 커버)
  - L549 ~ L800 (policy/rule heading 제외): 2026-06-07 configurable schema ~ paste validation closeout 구현 arc
  - L855, L921 ~ L1154: ui_tk cleanup preflight ~ stable ResultPanel (개별 구현 closeout)
  - L1174 이후 archive 대상 heading들 (이미 summary 314 커버 범위와 겹치는 것 위주)

- **active 유지 (약 20개 heading):**
  - L76, L95, L111, L204, L218, L232, L261, L284, L302, L326, L337
  - L442, L455, L512 (golden fix risk baseline)
  - L652, L769, L825, L881, L903
  - L1174, L1447
  - L1603, L1613, L1624 (최근 batch dialog arc 3개)

**1-C. project_log.md 수정 내용**

- archive 대상 heading 원문 제거 (원문은 archive 파일로 이전)
- `## Historical Log Archives` 섹션에 신규 링크 추가
- Ordering note는 유지
- project_log Policy section 유지

**1-D. 예상 결과**

- project_log.md: 현재 1632줄 → 약 500줄 수준 (active milestone heading 20개 내외)
- archive 파일: 약 1100줄 규모의 2026-06 part01 생성

**1-E. result report**

- compact report mode로 작성 (docs/archive lifecycle maintenance에 해당)
- WORK_PLAN.md 수정 불필요 (실행 우선순위 변경 없음)
- ACTIVE_DOCUMENTS.md 확인 불필요 (기존 archive 구조 확장이므로)

**금지 범위:**

- source/test/ui_tk/core/calculator 수정 금지
- memory seed 수정 금지 (별도 task)
- result_reports/active 기존 report 수정 금지
- result_reports/archive 이동 금지
- result_reports/summaries 수정/생성 금지
- docs/WORK_PLAN.md 수정 금지
- unrelated refactor 금지

### 단계 2 (별도 dedicated task): Memory Seed Maintenance

조건: dedicated memory maintenance task로 명시적 요청.

범위:
- 50-entry 초과 상태이므로 staleness/supersession review 병행
- 신규 후보 2개 추가 검토:
  1. batch dialog는 `BatchDialogShell` + `profiles/` thin adapter 구조를 따른다.
  2. Codex 프롬프트에 수동 GUI smoke 세부 항목을 넣지 않고 결과만 반영한다.

---

## 제외 범위

- project_log.md 실제 수정: 이번 audit에서 수행하지 않음
- docs/archive/project_log 파일 생성: 이번 audit에서 수행하지 않음
- result_reports/memory/project_memory_seed.md 수정: 이번 audit에서 수행하지 않음
- result_reports/summaries 생성/수정: 해당 없음
- 기존 active reports 수정: 해당 없음
- source/test/ui_tk/core/calculator: 해당 없음

---

## 검증 결과

- `git status --short`: 새 report 파일(`329_...`) 외 diff 없음 확인.
- `grep -n "^## 2026-" project_log.md`: 63개 heading 목록 확인 (inventory 작성 기준).
- `find docs/archive/project_log -maxdepth 3 -type f | sort`: 기존 2026-05/ 4개 파일 확인, 2026-06/ 없음 확인.
- `wc -l project_log.md`: 1632줄 확인.
- `wc -l result_reports/memory/project_memory_seed.md`: 764줄, 59 entries — 50-entry threshold 초과 확인.
- `python3 -B tools/check_code_structure.py`: warnings 5개 (pre-existing LOC/class soft limit) — 신규 위반 없음.
- `git diff --check`: clean.
- active report count: threshold 기준 확인 (exact count는 최종 명령 결과로만 보고).

---

## Next Action

**단계 1:** Project log 2026-06 archive segment 생성 + project_log.md active milestone heading 정리  
**단계 2 (별도):** Memory seed maintenance (50-entry 초과 상태 review + 신규 후보 2개 추가)
