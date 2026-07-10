# 332 Memory Seed Maintenance Execution

## 목표

331 memory seed maintenance audit 이후 사용자 확정 판단을 반영하여 `result_reports/memory/project_memory_seed.md`를 실제 보정한다. 신규 후보 중 repo memory에 넣지 말아야 할 항목을 제외하고, superseded/stale seed 후보를 정리하며, PyQt/Tkinter/PySide6 방향 seed를 최신 결정에 맞게 보정한다.

---

## 확인한 Workflow 기준

- `docs/agent_workflows/PROJECT_LOG_AND_MEMORY.md`
  - Memory seed 업데이트는 summary lifecycle task 또는 명시적 memory maintenance task에서만 허용.
  - 50-entry 초과: maintenance audit 후보. 75-entry 초과: dedicated maintenance task 필수.
  - seed는 evidence이며, 삭제 대신 `superseded`/`stale`/`resolutionStatus`/`supersededBy` 방식으로 정리.
- `AGENT_TASK_ROUTER.md` Result Report Workflow
  - tracked file 변경이 있으면 report 필수.
  - active report 수 관련 문구는 exact count 대신 threshold wording.

---

## 사용자 확정 판단 반영 내용

1. **BatchDialogShell + profiles thin adapter 구조**
   - batch dialog에만 국한되는 결정이 아니며, codebase-wide Clean Architecture boundary 원칙의 적용 사례임.
   - `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`와 기존 memory seed의 `codebase-wide Clean Architecture boundary owner` entry가 상위 원칙을 이미 소유.
   - 별도 BatchDialogShell 전용 seed는 추가하지 않음.

2. **manual GUI smoke prompt policy**
   - repo memory seed에 넣지 않음.
   - 이는 프롬프트 작성자 운영 규칙이지, 코드베이스에 남길 durable project memory가 아님.

3. **PyQt calculator 방향**
   - PyQt calculator-only path는 Tkinter calculator 도입의 read-only reference.
   - EN14825 및 AHRI 210/240 작성에 참고가 필요하면 read-only reference로 유지.
   - 참고 필요가 없어지면 retired 처리 가능.
   - app_calculator.py / app_calculator_tk.py entrypoint handover는 별도 후속 작업.

4. **Predict/Train PyQt 방향**
   - Predict/Train PyQt는 calculator와 별개로 유지.
   - 해당 코드는 shell 구조와 MVC 정책 도입 전에 작성된 코드이므로, 향후 PySide6 기반으로 신규 작성하는 방향이 적절.
   - 기존 Predict/Train PyQt를 현재 작업에서 수정하거나 삭제하지 않음.

---

## Superseded / Stale 정리 내용

기존 entry를 삭제하지 않고, `assertionStatus`/`resolutionStatus`/`supersededBy` 보강으로 정리.

| topic | 이전 상태 | 처리 |
|---|---|---|
| common dynamic content refit owner | superseded, supersededBy 없음 | `resolutionStatus: retired` 추가, `supersededBy` 추가 |
| Tk visible content measurement adapter extraction | superseded, resolutionStatus: resolved | `resolutionStatus: retired`로 변경 |
| batch two-row matrix layout preflight boundary | superseded, supersededBy 있음 | `resolutionStatus: retired` 추가 |
| deployment and PyQt validation follow-up | observed | `assertionStatus: stale`, `resolutionStatus: stale` 변경 |

---

## PyQt / Tkinter / PySide6 방향 Seed 보정 내용

- **PyQt and Tkinter calculator direction** (기존 entry)
  - `assertionStatus: superseded`, `resolutionStatus: superseded`, `supersededBy` 추가.
- **Tkinter calculator matrix UI and PyQt retirement gate** (기존 entry)
  - `assertionStatus: superseded`, `resolutionStatus: superseded`, `supersededBy` 추가.
- **신규 통합 entry 추가**
  - topic: `Tkinter calculator active direction and PyQt/PySide6 UI transition`
  - 의미:
    - PyQt calculator-only path는 Tkinter 전환 중 read-only reference.
    - EN14825 / AHRI 210/240 구현에 참고 필요가 있을 때만 유지.
    - 참고 필요 종료 시 PyQt calculator-only path는 retired 가능.
    - Predict/Train PyQt는 calculator와 별개로 유지.
    - 향후 Predict/Train UI 재작성은 PySide6 대상, shell/MVC boundary 정책 준수.
    - app_calculator_tk.py → app_calculator.py handover는 별도 future task.
  - keywords: PyQt calculator, Tkinter calculator, PySide6, Predict Train UI, entrypoint handover, EN14825, AHRI 210/240, MVC boundary.

---

## 추가하지 않은 후보와 이유

| 후보 | 제외 이유 |
|---|---|
| BatchDialogShell + profiles thin adapter structure | 기존 `codebase-wide Clean Architecture boundary owner` seed와 `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`가 상위 원칙을 이미 소유하며, BatchDialogShell은 해당 원칙의 적용 사례에 불과함. |
| manual GUI smoke prompt policy | repo memory seed가 아닌 ChatGPT 프롬프트 작성 운영 규칙으로 유지. 코드베이스 durable memory 성격이 아님. |

---

## 최종 Seed Entry Count 방향

- 수정 전: 59 entries
- 수정 후: 60 entries
- 변화: +1 (신규 통합 entry 1개 추가, superseded/stale 4개는 보강/상태 변경만, 삭제 없음)
- 50-entry threshold 초과 상태가 유지되며, 75-entry mandatory threshold에는 도달하지 않음.
- stale/superseded 정리로 seed 품질이 개선되었음.

---

## 검증 결과

- `git status --short`: `result_reports/memory/project_memory_seed.md`만 수정됨.
- `wc -l result_reports/memory/project_memory_seed.md`: 787줄.
- `grep -c "^  - type:" result_reports/memory/project_memory_seed.md`: 60 entries.
- `grep` BatchDialogShell / manual GUI smoke: memory seed에 없음.
- `python3 -B tools/check_code_structure.py`: warnings 7개 (pre-existing, 신규 위반 없음).
- `git diff --check`: clean.
- `project_log.md`: diff 없음.
- `docs/WORK_PLAN.md`: diff 없음.
- `docs/archive/project_log`: diff 없음.
- `result_reports/summaries`, `archive`: diff 없음.
- production source/test/ui_tk/core/calculator: diff 없음.
- active report count: threshold wording만 사용, exact count는 본문에 기록하지 않음.

---

## 제외 범위

- `project_log.md` 수정: 수행하지 않음.
- `docs/archive/project_log` 수정: 수행하지 않음.
- `result_reports/summaries`, `archive` 생성/이동: 수행하지 않음.
- production source/test/ui_tk/core/calculator: 수행하지 않음.
- `docs/WORK_PLAN.md` 수정: 수행하지 않음.
- batch foundation foldering audit: 수행하지 않음.
- `app_calculator.py` / `app_calculator_tk.py` rename: 수행하지 않음.

---

## Next Action

Batch foundation foldering audit으로 복귀.
