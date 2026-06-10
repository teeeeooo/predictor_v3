# 331 Memory Seed Maintenance Audit

## 목표

`result_reports/memory/project_memory_seed.md`가 59 entries로 50-entry audit threshold를 초과한 상태이므로, 실제 수정 전에 maintenance audit을 수행한다. 기존 entry의 stale/superseded/중복 상태를 점검하고, 329/330에서 식별된 신규 후보 2개의 seed 적합성을 판단한다. 다음 실행 작업에서 안전하게 seed cleanup 또는 update를 수행할 수 있는 구체적인 실행안을 제시한다.

> **이번 작업은 audit/report 전용이며, memory seed를 실제 수정하지 않았다.**

---

## 확인한 Workflow 기준

### PROJECT_LOG_AND_MEMORY.md (핵심)

- Memory seed 업데이트는 summary lifecycle task 또는 명시적 memory maintenance task에서만 허용.
- 50-entry 초과: maintenance audit 후보. 75-entry 초과: dedicated maintenance task 필수.
- seed recall: topic/keyword 검색 우선, read-only evidence.
- project_log는 active milestone log, memory seed는 backend-neutral long-term memory staging. 둘은 역할이 다르며 서로를 복사하지 않음.

### RESULT_REPORT_WORKFLOW.md (핵심)

- tracked file 변경이 있으면 report 필수.
- audit/report-only 작업(코드 변경 없음)은 compact report mode 허용.
- active report count: threshold wording 정책.

---

## Memory Seed Inventory 요약

- **총 줄 수:** 763줄
- **총 entries:** 59개 (`  - type:` 기준)
- **Source summaries:** 26개 summary (reports 001~314 커버)

### Type 분포

| type | 개수 |
|---|---|
| decision | 38 |
| procedure | 6 |
| open_question | 9 |
| error | 2 |
| fact | 2 |
| **합계** | **59** |

### Status 분포

| assertionStatus | 개수 |
|---|---|
| verified | 52 |
| observed | 6 |
| resolved | 1 (open_question L535) |
| superseded | 3 (L609, L642, L656) |

**이미 superseded로 표시된 entries:** 3개 (open_question 2개 + decision 1개):
- L600 `common dynamic content refit owner` — assertionStatus: superseded
- L634 `Tk visible content measurement adapter extraction` — assertionStatus: superseded, resolutionStatus: resolved
- L647 `batch two-row matrix layout preflight boundary` — assertionStatus: superseded

---

## 신규 후보 2개 중복 여부 확인

### 후보 1: BatchDialogShell + profiles thin adapter 구조

**검색 결과:** seed에서 `BatchDialogShell`, `profiles/ thin`, `thin adapter` 키워드 없음.

관련 기존 entries:
- L660 `batch two-row matrix path completed and Hong Kong CSPF migration stabilized` (reports 237-248 커버) — 이 entry는 BatchMatrixTable + HongKongCspfMatrixController 패턴을 다루나, `BatchDialogShell`/`profiles/` thin adapter 구조(reports 319-327)는 미포함.
- L674 `main notebook legacy vs batch newer stable path and BatchMatrixTable LOC containment` — batch path 일반론, shell/profiles 구조 미포함.

**판단:** ❌ 미포함 — **신규 후보로 유효**. `BatchDialogShell + profiles/` composition 패턴은 reports 319-327에서 확정된 아키텍처 결정으로, 현재 seed 커버리지(보고서 최대 314까지) 밖에 있다.

---

### 후보 2: Codex 프롬프트에 수동 GUI smoke 세부 항목을 넣지 않는 운영 정책

**검색 결과:** seed에서 `manual GUI smoke`, `manual smoke`, `수동 GUI`, `GUI smoke`, `prompt` 키워드 없음.

관련 기존 entries:
- L736 `durable wording policy for active report count` — report count wording 정책으로, 수동 smoke prompt 운영 정책과는 다른 내용.
- L48 `predictor_v3 result report lifecycle` — report 작성 방식 일반론, smoke prompt 정책 미포함.

**판단:** ❌ 미포함 — **신규 후보로 유효**. 이 운영 정책은 reports 324-325에서 수립되었으며, 현재 seed 커버리지 밖에 있다.

---

## Stale/Supersession 후보 식별

### 즉시 정리 후보 (supersede_candidate / stale_candidate)

| 줄 | topic | 현재 status | 분류 | 이유 |
|---|---|---|---|---|
| L600 | common dynamic content refit owner | superseded | **supersede_candidate** | 이미 superseded 표시됨. supersededBy 필드 없음 — 추가하거나 삭제 후보 |
| L634 | Tk visible content measurement adapter extraction | superseded + resolved | **retire_candidate** | resolutionStatus: resolved + supersededBy 존재. 정보가 중복. 삭제 또는 retired 표시 가능 |
| L647 | batch two-row matrix layout preflight boundary | superseded | **supersede_candidate** | supersededBy 존재하나 내용이 이미 L660 entry로 대체됨. 삭제 또는 supersede 마무리 후보 |

### update candidate (내용이 부분적으로 outdated)

| 줄 | topic | 분류 | 이유 |
|---|---|---|---|
| L367 | PyQt and Tkinter calculator direction | **update candidate** | "PyQt calculator-only assets are candidates for a read-only retirement audit"로 기술되어 있으나, 현재는 Tkinter calculator가 production 수준으로 안정화됨. 318 reports에서 ExcelLikeTableController 퇴출까지 완료. PyQt retirement audit이 여전히 "pending"인지 재검토 필요. 사용자 판단 필요. |
| L438 | Tkinter calculator matrix UI and PyQt retirement gate | **update candidate** | "PyQt calculator-only source retirement remains held pending"으로 기술. 현재 Tkinter calculator가 완전히 구현된 상태. 330에서 controller switch arc closeout까지 완료. "held pending" 상태가 여전히 유효한지 사용자 판단 필요. |
| L378 | deployment and PyQt validation follow-up | **stale candidate** | "Windows PyInstaller size measurement and Python 3.12/3.11 or Windows PyQt smoke validation remain pending". 현재 Tkinter 방향으로 전환 완료. PyQt deployment validation이 현재 next action과 무관. stale 표시 후보. |

### open_question 재검토 후보

| 줄 | topic | 분류 | 이유 |
|---|---|---|---|
| L125 | predictor_v3 ISO profile dispatcher coverage | **needs user decision** | "observed" 상태. 현재 ISO/SASO T3 controller switch 완료 이후 커버리지가 크게 변경됨. 해결됐는지 사용자 확인 필요. |
| L147 | ASNZS case3 full-dump parity | **keep** | 아직 명시적으로 해결되지 않은 외부 참조 의존성 open_question. 유지. |
| L202 | calculator envelope profile expansion | **keep** | 미해결 open_question. 유지. |
| L257 | ISO table and unit adapter follow-up | **keep** | 미해결 open_question. 유지. |
| L301 | Train and Predict UI deferred refactor | **keep** | 명시적으로 deferred. 유지. |
| L535 | Tkinter calculator multi-monitor geometry clipping | **keep** | assertionStatus: resolved로 이미 표시됨. 그러나 resolutionStatus 필드 없음 — 추가 정리 후보이나 삭제 대상은 아님. |

### keep (명확히 유효한 entries)

- L48~L122: procedure entries (result report lifecycle, agent rule ownership, lifecycle check modes) — 모두 verified, 여전히 유효.
- L92~L212: calculator standard/routing/envelope decisions — core architecture, verified, 유효.
- L213~L290: table UX, profile-native unit, HSPF fix, UI SSOT — 모두 verified, 유효.
- L612~L632: Clean Architecture boundary, portable UI/UX rule set — 현재 프로젝트 전 영역에 유효.
- L660~L744: batch path, schema-driven bin detail, visible content measurement, MVC separation, code_checker policy, durable wording policy — 모두 최근 확인된 verified decisions.

---

## Option 비교

### Option A. 신규 후보 2개만 추가

**장점:**
- 작업 범위가 좁고 실수 위험이 낮음.
- 즉시 coverage gap을 보완.

**단점:**
- superseded 3개, stale/update candidate 3개가 그대로 남아 entry 수가 61개로 증가.
- 50-entry threshold 초과 상태가 개선되지 않고 악화됨.

**권장 여부:** ❌ 비권장. entry 수가 증가하므로 threshold 개선에 역행.

---

### Option B. stale/superseded 후보 정리 후 신규 후보 추가 (권장)

**단계 1:** superseded 3개(L600, L634, L647) 처리 + stale 1개(L378) stale 표시 + update candidate 2개(L367, L438) 내용 보정 또는 보류 = 최소 3개 entry 줄 수 감소.
**단계 2:** 신규 후보 2개 추가 = 최종 예상 entry 수 약 58~59개 유지 (net 변화 ≈ 0 ~ -1).

**장점:**
- superseded/stale entries를 정리하여 seed 품질 향상.
- 신규 coverage gap(reports 319-327)을 보완.
- 정책 준수: seed maintenance task + add 1-2 entries per update.

**단점:**
- update candidate 2개(PyQt/Tkinter direction)는 사용자 판단이 필요해 작업이 일부 지연될 수 있음.
- 단계 분리 시 2개의 task/commit이 필요.

**권장 여부:** ✅ **권장**. 현재 entry 수와 품질 모두 개선.

---

### Option C. 이번에는 seed 미수정, Batch foundation foldering audit으로 복귀

**장점:**
- 즉시 다음 기술 작업으로 복귀 가능.
- 위험 없음.

**단점:**
- 59 entries로 threshold 초과 상태가 계속됨.
- reports 319-327에서 확정된 아키텍처 결정(batch dialog shell+profiles)이 seed에 미반영 상태로 유지됨.
- 이후 작업에서 seed가 더 stale해질 위험.

**권장 여부:** ❌ 비권장 (단, 즉각 기술 작업이 우선이면 수용 가능).

---

## 권장 전략

**Option B (2단계 실행):**

> **단계 1:** superseded 3개를 정리(삭제 또는 retired 마무리)하고, stale 1개(L378)에 stale 표시 추가, update candidate 2개(L367, L438)에 대한 사용자 판단을 먼저 구한 후 결정.  
> **단계 2:** 신규 후보 2개 추가 — (1) `BatchDialogShell + profiles/` thin adapter 구조, (2) Codex 프롬프트 수동 GUI smoke 운영 정책.

---

## 다음 실행 작업 범위 (구체적 실행안)

### 실행 단계 1: superseded/stale 정리

**처리 대상:**

| 줄 | topic | 처리 방안 |
|---|---|---|
| L600 | common dynamic content refit owner | supersededBy 추가 후 retired 표시 (예: `supersededBy: summaries/231 and 236`) |
| L634 | Tk visible content measurement adapter extraction | 이미 resolutionStatus: resolved + supersededBy 있음 — retired 표시 추가 후 삭제 후보 |
| L647 | batch two-row matrix layout preflight boundary | supersededBy 있음 — retired 표시 후 삭제 후보 |
| L378 | deployment and PyQt validation follow-up | stale 표시 추가 (PyQt deployment follow-up은 현재 next action과 무관) |

**사용자 판단이 필요한 항목:**

| 줄 | topic | 질문 |
|---|---|---|
| L367 | PyQt and Tkinter calculator direction | "PyQt calculator-only assets are candidates for a read-only retirement audit"가 아직 유효한 pending 작업인가, 아니면 retired로 처리할 수 있는가? |
| L438 | Tkinter calculator matrix UI and PyQt retirement gate | "PyQt calculator-only source retirement remains held pending"이 여전히 유효한가? |

### 실행 단계 2: 신규 후보 추가

**추가할 entry 1:**
```yaml
- type: decision
  topic: batch dialog shell and profiles thin adapter structure
  content: ui_tk/batch_dialogs/ uses BatchDialogShell (shell.py) as the single owner of Toplevel lifecycle, focus, close callback, hidden-first geometry settle, and snapshot handoff; profile-specific files (profiles/*.py) are thin adapters owning only matrix table layout and controller wiring. Composition over inheritance is the pattern. Established in reports 319-327.
  keywords:
    - BatchDialogShell
    - profiles thin adapter
    - batch dialog
    - composition
    - snapshot handoff
  assertionStatus: verified
  source: result_reports/active/330_project_log_2026_06_archive_segment_cleanup.md (batch dialog arc summary, reports 319-327)
```

**추가할 entry 2:**
```yaml
- type: procedure
  topic: manual GUI smoke prompt policy
  content: Codex agent prompts must not include detailed manual GUI smoke checklists. Users perform manual smoke verification independently and report only the pass/fail outcome; the closeout entry reflects the outcome, not the step-by-step list.
  keywords:
    - manual GUI smoke
    - prompt policy
    - closeout
    - agent workflow
  assertionStatus: verified
  source: result_reports/active/325_iso_iseer_2point_batch_dialog_report_closeout_correction.md
```

**금지 범위:**
- source/test/ui_tk/core/calculator 수정 금지
- project_log.md 수정 금지 (이미 완료)
- docs/WORK_PLAN.md 수정 금지
- result_reports/active 기존 report 수정 금지
- result_reports/archive, summaries 이동/생성 금지

**project_log 수정 필요 여부:** 불필요 (이번 seed 수정은 memory maintenance이므로 project_log milestone update 대상 아님).

**WORK_PLAN 수정 필요 여부:** 불필요.

**예상 최종 entry 수:**
- 현재 59 → 정리 후 ~56 → 신규 2개 추가 후 ~58. 50-entry threshold는 초과 상태이나 악화되지 않음. 75-entry mandatory threshold에는 충분한 여유.

---

## 제외 범위

- result_reports/memory/project_memory_seed.md 실제 수정: 이번 audit에서 수행하지 않음.
- project_log.md 수정: 수행하지 않음.
- docs/archive/project_log 수정: 수행하지 않음.
- result_reports/summaries, archive 수정: 수행하지 않음.
- source/test/ui_tk/core/calculator: 수행하지 않음.

---

## 검증 결과

- `git status --short`: clean — 새 report 파일 외 diff 없음.
- `wc -l result_reports/memory/project_memory_seed.md`: 763줄, 변경 없음.
- `grep -n "^  - type:" result_reports/memory/project_memory_seed.md`: 59 entries 확인.
- `grep "BatchDialogShell|batch dialog|..." result_reports/memory/project_memory_seed.md`: BatchDialogShell 없음, `batch dialog` 3개 기존 entries 확인 (L636, L662, L676) — 모두 2024-06-07 arc 범위, 319-327 arc 미반영 확인.
- `python3 -B tools/check_code_structure.py`: warnings 4개 (pre-existing LOC/class soft limit) — 신규 위반 없음.
- `git diff --check`: clean.
- active report count: threshold 기준 확인 (exact count는 최종 terminal output에만).

---

## Next Action

**Option B 단계 1:** L367, L438 PyQt/Tkinter direction entries에 대한 사용자 판단 수렴 후 superseded/stale 정리 및 신규 2개 추가 실행.

또는: **Batch foundation foldering audit** (이번 seed maintenance를 연기하고 기술 작업 우선).
