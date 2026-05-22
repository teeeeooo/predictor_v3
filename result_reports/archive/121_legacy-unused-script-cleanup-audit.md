# 121 — Legacy / Unused Script Cleanup Audit

## Goal

predictor_v3에 누적된 legacy / unused / spike / debug / one-off
script 후보를 read-only로 inventory하고, 안전한 후속 cleanup slice를
나눈다. **본 작업에서는 파일 삭제 / 이동 / rename / 코드 수정 / import
수정을 하지 않는다.**

## Scope

- task 1: 후보 파일 inventory + 분류 (read-only).
- task 2: 참조 관계 audit (runtime/import vs docs/historical).
- task 3: 후속 cleanup slice 후보 정의 + 추천 first action.
- task 4: 119 New Code Quality Gate 관점 재발 방지 점검 + 추가 guard
  improvement 후보.
- task 5: WORK_PLAN 짧은 갱신 + 본 report.

## Non-goals

- 파일 삭제 / 이동 / rename.
- 코드 수정 / import 수정.
- legacy cleanup 실행.
- code structure guard / AGENTS / ROUTER / architecture / project_log /
  ACTIVE_DOCUMENTS 수정.
- result report lifecycle maintenance / active·archive·summaries
  이동.
- Tkinter 기능 추가 / PyQt UI 재개·삭제.
- PyInstaller 실행.
- unit adapter / ML / inverse-search / calculator logic / expected /
  fixture / xfail / profile / dispatcher 수정.
- AGENTS_FULL.md 열람.

## Verification

- `python3 -B tools/check_code_structure.py` →
  `code structure guard: OK (no findings)`, exit 0.
- `python3 -B -m pytest tests/test_code_structure_guard.py
  tests/test_ui_tk_profile_resolver.py
  tests/test_ui_tk_calculator_foundation.py
  tests/test_calculator_schema_boundaries.py
  tests/test_calculator_profiles.py
  tests/test_calculator_dispatcher.py -q` → **78 passed**.
- 전체 (위 4 PyQt 환경 의존 crash 파일 제외) → **568 passed, 1 skipped,
  23 xfailed**. 120 baseline과 동일 (본 작업 audit only).

## Task Results

### task 1 — Inventory

#### Inventory 범위

`git ls-files` / `find` / `ls`로 다음 영역의 모든 파일을 조사:

- repo root `app_*.py` (4개)
- `tools/` (1 module + `__init__.py`)
- `scripts/` (1 module)
- `ui_tk/` (118 reset 결과 + 신규 modules)
- `ui/` (PyQt UI 9 modules)
- `core/_legacy/` (1 module)
- `tests/_legacy/` (5 module + `__init__.py`)
- `docs/guides/` (2 docs)
- `docs/designs/` (10 docs)
- `docs/archive/` (subfolders 포함)
- `reference_files/` (tracked vs ignored 분리)
- `result_reports/active/` (현 6건 = 115~120)

#### 분류 결과

**범주 1 — Active entrypoint / production candidate (NEVER cleanup):**

| 파일 | 비고 |
| --- | --- |
| `app_predict.py` (29 LOC) | PyQt 예측 앱 진입 |
| `app_train.py` (26 LOC) | PyQt 학습 앱 진입 |
| `app_calculator.py` (12 LOC) | PyQt calculator 진입, hold 상태이지만 reference로 유지 |
| `app_calculator_tk.py` (16 LOC) | Tkinter MVP 진입, 활성 |
| `tools/check_code_structure.py` | 119 추가, 활성 |
| `tools/__init__.py` | package marker |
| `scripts/update_mapping.py` (129 LOC) | **`ui/train_window.py` line 11에서 import 중** (`from scripts.update_mapping import select_excel_file, update_mapping_to_json`) — 활성 production code. 절대 cleanup 대상 아님. |
| `ui_tk/*` (118 reset 결과 — 8 module + 3 `__init__.py`) | 활성 Tkinter MVP foundation. |
| `core/calculator_*.py` (non-legacy) | 활성 calculator core. |
| `ui/predict_window.py`, `ui/train_window.py`, `ui/base_model.py`, `ui/base_view.py` | 활성 Predict/Train UI. |

**범주 2 — Reference / hold but valuable (preserve):**

| 파일 | 비고 |
| --- | --- |
| `ui/calc_window.py` (834 LOC) | PyQt calculator UI, WORK_PLAN 4c~4g hold. allowlist. |
| `ui/calculators_2point.py` (1629 LOC) | ISO 2-point widget, PyQt calculator path. allowlist. |
| `ui/spreadsheet_table.py` (746 LOC) | PyQt spreadsheet model/view. allowlist. |
| `ui/calculator_errors.py` (114 LOC) | 115에서 추출한 helper. |
| `ui/theme.py` (104 LOC) | 108 design token foundation. |
| `core/_legacy/calculator_iso16358_legacy.py` (2293 LOC) | `docs/REFACTOR_PLAN.md` §1과 `docs/designs/2026-05-17-iso-remaining-work-completion.md`이 명시적으로 reference로 보존. `tests/_legacy/` 5개 file이 이 모듈을 import. allowlist. |
| `docs/designs/*.md` (10개) | 모두 active 또는 history-of-decision. 본 audit 범위 밖. |
| `docs/guides/lightweight_calculator_packaging_check.md` (116) | 활성, Windows 측정 절차. |
| `docs/guides/lightweight_calculator_tk_manual_smoke.md` (120) | 활성, macOS manual smoke. |

**범주 3 — Feasibility spike / temporary prototype 후보:**

- 없음. 116 spike의 단일 파일 누적은 118 clean foundation reset으로
  이미 해소됨. 현재 `ui_tk/` 8 module 모두 한 책임만 담는 production-
  candidate 구조.

**범주 4 — One-off diagnostic / debug script 후보:**

| 파일 | LOC | 상태 |
| --- | --- | --- |
| `tests/_legacy/test_iso16358_cspf_iso_t1_default_diagnostics.py` | 209 | 활성 수집, ISO 16358 CSPF "diagnostics" 명칭. |
| `tests/_legacy/test_iso16358_cspf_profile_calculation.py` | 129 | 활성 수집. |
| `tests/_legacy/test_iso16358_cspf_profile_resolver.py` | 103 | 활성 수집. |
| `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py` | 1775 | 활성 수집, 17 xfail 포함. |
| `tests/_legacy/test_iso16358_hspf_h8_trace.py` | 180 | 활성 수집, "trace audit". |

`pytest tests/_legacy --collect-only -q` 결과 **52 tests collected**.
실행 시 **35 passed, 17 xfailed**. 폴더 이름은 `_legacy`이지만
실제로는 active diagnostic / regression-pinning 테스트. **이름과
실제 상태가 불일치**가 가장 큰 위험. 즉시 삭제 대상이 아니라
**이름/위치/owner 명확화 audit 후보**.

**범주 5 — Legacy compatibility 후보:**

- `core/_legacy/calculator_iso16358_legacy.py` (2293 LOC).
  REFACTOR_PLAN §1 / design doc / project_log / WORK_PLAN /
  architecture doc / allowlist에 모두 명시적으로 "reference로 보존"
  으로 등록. `tests/_legacy/*` 5개가 import 중. **즉시 삭제 금지.**
  decommission은 별도 design-gated 작업이며 본 audit 범위 밖.

**범주 6 — docs/report historical record (cleanup 대상 아님):**

- `result_reports/archive/*.md` (108개) — historical record.
- `result_reports/summaries/*.md` (8개) — 누적 요약.
- `reference_files/audit_*.md` (4 tracked file) — `ACTIVE_DOCUMENTS.md`
  policy로 inventory 제외.
- `docs/archive/AGENTS_FULL.md`, `docs/archive/AGENTS_md_slimming_plan.
  md`, `docs/archive/refactoring_original_log_2026-05-04.md.md`,
  `docs/archive/skills_v2_patterns.md`, `docs/archive/standards_legacy/
  *.md` — `ACTIVE_DOCUMENTS.md` policy에 따라 historical / excluded.

**범주 7 — 정체 확인 필요:**

| 파일 | LOC | 발견 |
| --- | --- | --- |
| `docs/archive/iso16358_initial_reverse_engineering/cspf_calculator.py` | 116 | 외부 import 0건. `project_log.md` / `docs/iso16358/iso16358_dev_notes.md`에서만 mention. |
| `docs/archive/iso16358_initial_reverse_engineering/dump_bin_inputs.py` | 17 | 동일 (mention only). |
| `docs/archive/iso16358_initial_reverse_engineering/dump_bins.py` | 17 | 동일. |
| `docs/archive/iso16358_initial_reverse_engineering/extract_formulas.py` | 18 | 동일. |
| `docs/archive/iso16358_initial_reverse_engineering/find_cspf.py` | 27 | 동일. |
| `docs/archive/iso16358_initial_reverse_engineering/formula_list.txt` | n/a | 동일. |
| `docs/archive/iso16358_initial_reverse_engineering/README.md` | n/a | archive README, 폴더 정체 설명. |

이 폴더는 ISO 16358 reverse-engineering 초기 작업 산출물 (snapshot).
runtime import는 없고 historical 참조만 있다. **이미 `docs/archive/`
아래에 있으므로 cleanup이라기보다 "위치 + README 정합성" 확인 후보**.
`__pycache__/` 가 존재한다는 점은 한때 import / 실행 흔적이며 현재는
사용되지 않는다 (현 코드 / 테스트에서 import 0).

#### 즉시 삭제 금지 / 보존 후보 요약

- **모든** `ui_tk/`, `tools/`, `scripts/`, `app_*.py`, `ui/`, `core/`
  (legacy 포함), `tests/_legacy/`, `result_reports/`, `docs/`,
  `reference_files/` 항목은 **본 audit에서 삭제 / 이동 / rename
  제안하지 않는다**.
- 후속 cleanup 후보는 task 3에서 slice로 분리.

### task 2 — 참조 관계 audit

#### Runtime / import 참조

| 파일 / 디렉터리 | runtime import 출처 | 결론 |
| --- | --- | --- |
| `scripts/update_mapping.py` | `ui/train_window.py:11` (`from scripts.update_mapping import select_excel_file, update_mapping_to_json`) | **활성**. cleanup 대상 아님. |
| `core/_legacy/calculator_iso16358_legacy.py` | `tests/_legacy/{5 files}`에서 모두 `from core._legacy.calculator_iso16358_legacy import ISO16358Calculator` | **legacy reference**. tests/_legacy 운영 동안 보존. |
| `tests/_legacy/*` | pytest auto-collection (52 tests, 35 passed + 17 xfailed) | **수집되어 실행 중**. 폴더 이름이 실제 상태와 불일치 (`_legacy` 명칭이지만 활성). |
| `docs/archive/iso16358_initial_reverse_engineering/*.py` | runtime import 0건 | **historical only**. 위치는 이미 archive 아래. |
| `ui_tk/*` | `app_calculator_tk.py` + 자체 cross-import | **활성** (118 reset 결과). |
| `ui/calc_window.py` 등 PyQt calculator path | `app_calculator.py` + `tests/test_app_calculator_ui_smoke.py` | **hold이지만 reference 유지**. |

#### Docs / report 참조

- `app_calculator.py` → `README.md`, `project_brief.md`,
  `project_log.md`, `docs/WORK_PLAN.md`, `docs/guides/*`,
  `docs/designs/*`, 다수 `result_reports/*` (active + archive).
  **historical 참조와 active 참조가 섞여 있다**. active 참조 (README /
  project_brief / WORK_PLAN / guides) 만으로도 보존 근거 충분.
- `core/_legacy/calculator_iso16358_legacy.py` → `tools/check_code_
  structure.py`, `tests/test_code_structure_guard.py` (allowlist
  reference), `docs/REFACTOR_PLAN.md`, `docs/architecture/project_
  architecture.md`, `docs/designs/2026-05-17-iso-remaining-work-
  completion.md`, `project_log.md`, 다수 `result_reports/archive/*`.
  active 보존 근거는 REFACTOR_PLAN §1 + architecture doc + tests/_
  legacy import.
- `tests/_legacy/*` → `docs/WORK_PLAN.md`, `docs/iso16358/*notes.md`,
  `docs/designs/2026-05-10-iso16358-2-hspf-h8-routing-resolver-design
  .md`, `project_log.md`, 다수 `result_reports/archive/*`. 진단/회귀
  보호 역할로 명시.

**historical 참조와 active 참조 구분**: `result_reports/archive/*`
와 `result_reports/summaries/*`의 참조는 *history*. `README.md`,
`docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, `project_brief.md`,
`AGENTS.md`, `AGENT_TASK_ROUTER.md`, `docs/architecture/*`,
`docs/designs/*` (active), `docs/guides/*` (active), `tools/*`,
`tests/*`는 *active*. 본 audit에서는 "active 참조가 있으면 보존",
"historical-only 참조면 cleanup 후보 가능"으로 판정한다.

#### `tools/check_code_structure.py` allowlist 표시

LOC allowlist (9 file):

- `core/_legacy/calculator_iso16358_legacy.py`
- `core/calculator_iso16358.py`
- `core/calculator_ks_c9306.py`
- `core/calculator_ahri_hspf2.py`
- `core/calculator_en14825.py`
- `core/calculator_asnzs_hspf_excel.py`
- `ui/calc_window.py`
- `ui/calculators_2point.py`
- `ui/spreadsheet_table.py`

CLASS allowlist (4 file):

- `core/_legacy/calculator_iso16358_legacy.py`
- `ui/calculators_2point.py`
- `ui/spreadsheet_table.py`
- `ui/calc_window.py`

**allowlist 등록 ≠ cleanup 대상**. 단지 119 structure guard의 LOC /
class soft limit 예외 처리일 뿐. 본 audit에서는 allowlist 파일에 대해
삭제 / 이동 / rename 제안을 하지 않는다.

### task 3 — 후속 cleanup slice 후보

각 slice는 별도 작업으로 분리하고, 이번 작업에서는 실행하지 않는다.

#### Slice C1 — Documentation / guide 위치 확인 (audit only)

- **목적**: `docs/guides/*`, `docs/designs/*`가 active SSOT (`docs/
  ui_ux/`, `AGENTS.md`, `WORK_PLAN`) 와 정합하는지 cross-link 검토.
- **대상 파일 후보**: `docs/guides/lightweight_calculator_packaging_
  check.md`, `docs/guides/lightweight_calculator_tk_manual_smoke.md`,
  `docs/designs/2026-05-22-calculator-action-model-alignment.md`,
  `docs/designs/2026-05-22-calculator-ui-module-boundary.md`,
  `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`.
- **포함**: 문구 cross-link / 의미 변화 표시 / docs 사이 모순 점검.
- **제외**: 파일 삭제 / 이동, 설계 doc 본문 rewrite.
- **선행 조건**: 없음.
- **검증**: `rg`로 cross-link 일관성 + `python3 -B tools/check_code
  _structure.py`.
- **위험**: 낮음 (docs only).

#### Slice C2 — `docs/archive/iso16358_initial_reverse_engineering/` 정리

- **목적**: 5개 reverse-engineering script와 `formula_list.txt`,
  `README.md`가 archive 위치에 적절히 있는지 확인하고, README가
  "이것은 historical snapshot이며 runtime import 없음"을 명시하는지
  검토. 필요하면 README만 보강.
- **대상 파일 후보**: `docs/archive/iso16358_initial_reverse_
  engineering/README.md` (수정 후보), 그 외 `.py`는 그대로 둔다.
- **포함**: README의 status 한 줄 보강. `__pycache__/` 디렉터리 .gitignore
  여부 확인 (Git에 tracked되어 있다면 별도 cleanup).
- **제외**: `.py` 삭제, 폴더 이동, runtime import 추가.
- **선행 조건**: `git ls-files docs/archive/iso16358_initial_reverse_
  engineering/`로 tracked file만 추출 (`__pycache__`는 ignored).
- **검증**: `python3 -B tools/check_code_structure.py` 변경 없음
  확인.
- **위험**: 최저 (docs only).

#### Slice C3 — `tests/_legacy/` 명명 / owner audit

- **목적**: `tests/_legacy/`가 실제로는 활성 diagnostic / regression
  test 폴더라는 점을 명확히 한다. 폴더 이름 (`_legacy`) 이 misleading
  하여, 새로 합류하는 작업자가 "보존 의무 없음"으로 오해할 수 있다.
- **대상 파일 후보**:
  - `tests/_legacy/__init__.py` (docstring 보강 후보)
  - `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py` (1775 LOC,
    17 xfail) — 회귀 보호용 명시 후보
  - `tests/_legacy/test_iso16358_hspf_h8_trace.py` (180 LOC, "trace
    audit") — diagnostic 명시 후보
  - 나머지 3개 — owner / 보존 이유 명시 후보
- **포함**: `__init__.py` docstring 또는 `tests/_legacy/README.md`
  추가 (현재 없음). 폴더 명칭 변경은 import path를 깨므로 본 slice
  범위 밖.
- **제외**: 폴더 rename (`_legacy` → `_diagnostic`) — 5개 file의
  import path가 모두 영향받으므로 별도 design-gated 작업.
  test 본문 수정. xfail 변경.
- **선행 조건**: `core/_legacy/calculator_iso16358_legacy.py`
  decommission 의도 없음을 REFACTOR_PLAN §1 / project_log에서 재확인.
- **검증**: `python3 -B -m pytest tests/_legacy -q` 결과 동일 (35
  passed, 17 xfailed) 확인.
- **위험**: 낮음 (docs only).

#### Slice C4 — `core/_legacy/calculator_iso16358_legacy.py` 보존 confirmation

- **목적**: 본 모듈이 reference로 유지된다는 점을 한 자리에서
  확인하고, decommission 조건을 design-gate에 적어 두는 audit.
- **대상 파일 후보**: 신규 audit report 또는 `docs/REFACTOR_PLAN.md`
  §1의 한 두 문장 보강.
- **포함**: decommission 가능 조건 정의 (예: `tests/_legacy/*` 폐기
  + AS/NZS workbook oracle 작업 종료). cleanup 실행은 아님.
- **제외**: 파일 삭제 / 이동 / rename. test 수정. allowlist 변경.
- **선행 조건**: Slice C3 완료 후 진행하는 것이 안전.
- **검증**: `python3 -B -m pytest tests/_legacy -q` + guard 통과.
- **위험**: 낮음 (read-only + 문서 1~2줄).

#### Slice C5 — Code structure guard allowlist 재검토

- **목적**: 119에서 등록한 9 LOC allowlist / 4 CLASS allowlist
  파일이 여전히 정당한지 재확인. 새 파일이 부당하게 allowlist에
  추가되지 않도록 review checklist를 명문화.
- **대상 파일 후보**: `tools/check_code_structure.py` (코드 수정은
  하지 않고 audit만), `tests/test_code_structure_guard.py` (수정 없음),
  `docs/architecture/project_architecture.md` §6 (필요 시 한 줄 추가).
- **포함**: 각 allowlist 항목이 (a) 현재도 large인지, (b) 분리/축소
  대상인지, (c) reference-only로 동결인지 분류 표.
- **제외**: 실제 allowlist 변경 / 파일 분리.
- **선행 조건**: 없음.
- **검증**: `python3 -B tools/check_code_structure.py` 결과 변화
  없음 확인 + `tests/test_code_structure_guard.py` 통과.
- **위험**: 낮음 (audit only).

#### 추천 first cleanup action

**Slice C2 — `docs/archive/iso16358_initial_reverse_engineering/`
정리** 를 첫 번째 cleanup으로 추천한다.

기준:

- 위험 최저 (docs only, runtime import 0).
- README 한 줄 보강으로 "historical snapshot, runtime import 없음"
  명시 가능 → 미래 cleanup 판단 비용 절감.
- guard / test / runtime에 0 영향.
- 다음 단계 (C3 tests/_legacy 명명 audit)로 자연스럽게 연결.

대안 (사용자 선호에 따라):

- **Slice C3 (tests/_legacy 명명 audit)** — 더 큰 효과 (작업자
  오해 방지). 단 docs 작업이 1 파일 (`README.md` 또는 `__init__.py`
  docstring)에 한정되므로 효과 / 위험 trade-off는 C2와 비슷.

기각:

- 즉시 파일 삭제 / 이동 / rename / 폴더 이동 — 본 audit의 어떤
  후보도 zero-risk가 아니라 분리 작업 필요.

**삭제가 아니라 archive/rename이 더 나은 경우**:

- `tests/_legacy/` 폴더 자체 rename은 import path 5개 파일 영향 →
  rename 대신 README/docstring 명시화가 우선.
- `core/_legacy/calculator_iso16358_legacy.py`는 이미 `_legacy/`
  하위 → 위치 적절. rename 불필요.
- `docs/archive/iso16358_initial_reverse_engineering/*.py`는 이미
  `docs/archive/` 하위 → 위치 적절. README 보강만 필요.

### task 4 — Code Quality Gate 관점 재발 방지

#### 119 guard와의 관계

현재 `tools/check_code_structure.py` 가 막는 것:

- `core/` 의 `ui`/`ui_tk`/`PyQt5`/`tkinter` import.
- `ui_tk/` 의 `PyQt5` 또는 `ui` import.
- `app_*.py` 의 비-thin entrypoint (class / func count / LOC).
- `ui_tk/` 의 multi-책임 anti-pattern.
- 새 파일 LOC > 400 / class > 5 (warning, soft).

본 cleanup audit가 발견한 위험은 119 guard가 직접 막지 못한다:

1. **명칭 misleading** — `tests/_legacy/` 가 실제로는 활성 diagnostic
   인데 이름이 "legacy". guard는 명칭 검사 안 함.
2. **historical archive 의도 표시 부재** — `docs/archive/...
   _initial_reverse_engineering/*.py` 같은 historical snapshot에
   "import 금지" / "runtime 미사용" status header가 없다. guard는
   archive 폴더 status header 검사 안 함.
3. **one-off helper script의 owner / purpose 부재** —
   `scripts/update_mapping.py` 는 다행히 `ui/train_window.py` 가
   import하고 있지만, header에 "active production helper" 같은
   상태가 명시되어 있지 않다. 미래 audit에서 다시 "사용 여부"를
   조사해야 한다.
4. **spike file lifecycle marker 부재** — 새 spike가 들어올 때
   "spike, 30일 내 reset 또는 promote 필요" 같은 lifecycle marker가
   없다.
5. **stale script audit 자동화 부재** — "어떤 .py 가 outside import
   0건이고, 어떤 test도 참조하지 않으며, doc만 mention하는지"를 한
   command로 확인할 수 없다.

#### 후속 guard improvement 후보 (별도 작업)

다음은 본 작업에서 **구현하지 않는다**. 별도 design slice로 둔다.

- **G1**: `docs/archive/**/*.py` 안의 모든 `.py`에 "archived
  snapshot, no runtime import" header 필수화. guard가 header 부재 시
  warning.
- **G2**: `tests/_legacy/__init__.py` 또는 `tests/_legacy/README.md`
  필수화. guard가 부재 시 warning ("이 폴더의 활성 상태를 명시
  하라").
- **G3**: `tools/` / `scripts/` 의 module-level docstring 첫 줄에
  `owner:` / `purpose:` / `status:` field 권장 (필수까지는 안 가도
  됨). guard가 missing field 시 warning.
- **G4**: spike lifecycle marker — 파일 docstring에 `STATUS: spike,
  expires YYYY-MM-DD` 형태 마커가 있는지 검사. 만료 후 warning.
- **G5**: stale script audit subcommand — `python3 -B tools/check_
  code_structure.py --orphans` 같은 모드로, AST import edge가 0인
  `.py` 파일을 나열. 본 작업에서 구현하지 않음.

#### 이번 작업에서 guard를 수정하지 않은 이유

- 작업 지시상 `tools/check_code_structure.py`, `tests/test_code_
  structure_guard.py`, `AGENTS.md`, `AGENT_TASK_ROUTER.md`,
  `docs/architecture/project_architecture.md` 수정 금지.
- 본 작업은 audit-only. cleanup 실행이나 guard 강화는 별도 design-
  gated 작업.
- 위 G1~G5는 *제안 목록* 으로만 본 report에 남긴다.

### task 5 — WORK_PLAN / report

#### `docs/WORK_PLAN.md` 수정 내용

4x (120 manual smoke checklist) 아래에 **4w — Legacy / unused script
cleanup audit (121 참고)** 한 문단 추가:

- audit 범위 (app_*.py, tools/, scripts/, ui_tk/, ui/, core/_legacy,
  docs/guides, docs/designs, docs/archive, reference_files,
  tests/_legacy, result_reports/active).
- 즉시 삭제 / 이동 / rename 후보 없음 — 모든 후보는 후속 slice
  (C1~C5) 로 분리.
- 추천 first cleanup = **Slice C2** (`docs/archive/iso16358_initial_
  reverse_engineering/README.md` 보강).
- guard improvement 후보 G1~G5는 별도 design slice 로 보류.

다른 항목 (4y, 4z, 4c~4g, 5번 hold) 은 그대로 유지.

#### lifecycle maintenance 제외 이유

- 현 active 누적: 115 + 116 + 117 + 118 + 119 + 120 + 121 = **7건**.
  summary trigger 8~12개 미만이며 아직 trigger 부근 아님.
- 본 작업은 audit only. summary / archive / `project_log.md` /
  `ACTIVE_DOCUMENTS.md` 작업과 섞지 않는다.
- `result_reports/archive/` / `result_reports/summaries/` 미수정.

## Next Suggested Action

**Slice C2 — `docs/archive/iso16358_initial_reverse_engineering/
README.md` status header 보강** (추천 first cleanup action).

또는 사용자 우선순위에 따라:

- **Slice C3** (tests/_legacy 명명 audit + README/docstring 보강).
- **Slice C5** (allowlist 재검토 audit-only).
- **Windows host 확보 시** Slice T6 (PyInstaller size 실측, 120 우선
  순위).

PyQt calculator UI hold (4c~4g) / Hong Kong HSPF PyQt UI surface (5)
/ Tkinter MVP 기능 추가 / unit adapter / ML / inverse-search 는 본
audit가 변경하지 않는다.

## Scope Compliance

- 파일 삭제 / 이동 / rename / 코드 수정 / import 수정 없음.
- legacy cleanup 미실행.
- Tkinter 기능 추가 / PyQt UI 재개·삭제 없음.
- PyInstaller 실행 없음.
- unit adapter / ML / inverse-search / calculator logic / expected /
  fixture / xfail / profile / dispatcher 미수정.
- `tools/check_code_structure.py`, `tests/test_code_structure_guard
  .py`, `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `docs/architecture/
  project_architecture.md` 미수정.
- `project_log.md`, `ACTIVE_DOCUMENTS.md` 미수정.
- result report lifecycle maintenance 미수행. `result_reports/
  archive` / `result_reports/summaries` 미수정.
- AGENTS_FULL.md 미열람.

## Changed Files

- M `docs/WORK_PLAN.md` (4w 항목 신규 추가)
- A `result_reports/active/121_legacy-unused-script-cleanup-audit.md`

## Known Failures / Risks

- 본 작업은 read-only audit. 실제 cleanup 위험은 후속 slice에서
  평가한다.
- `tests/_legacy/` 폴더 이름이 실제 상태와 불일치 (`_legacy` 명칭
  이지만 활성 diagnostic + 회귀 보호 52 tests). Slice C3가 이 위험을
  해소한다.
- `scripts/update_mapping.py` 가 활성 production helper임을 본 audit
  로 확인 — `ui/train_window.py:11`이 import 중. 무심코 삭제하면
  Train UI 깨진다. (Slice C5 / guard G3로 명시 후보.)
- `core/_legacy/calculator_iso16358_legacy.py` 와 `tests/_legacy/*`는
  강하게 결합 (5 import). decommission은 두 영역을 동시에 다뤄야
  하므로 design-gated 작업 (Slice C4 + 후속) 으로 분리.
- macOS + Python 3.14 + PyQt5 환경의 4 PyQt clipboard / table fatal-
  abort 4건은 본 작업과 무관 (audit만 수행).
- 119 New Code Quality Gate가 직접 막지 못하는 위험 5종 (G1~G5)을
  task 4에서 후속 guard improvement 후보로 기록.

## Test Results

- `python3 -B tools/check_code_structure.py` →
  `code structure guard: OK (no findings)`, exit 0.
- `python3 -B -m pytest tests/test_code_structure_guard.py
  tests/test_ui_tk_profile_resolver.py
  tests/test_ui_tk_calculator_foundation.py
  tests/test_calculator_schema_boundaries.py
  tests/test_calculator_profiles.py
  tests/test_calculator_dispatcher.py -q` → 78 passed.
- 전체 (위 4 PyQt 환경 의존 crash 파일 제외) → 568 passed, 1 skipped,
  23 xfailed. 120 baseline과 동일.
- 참조: `tests/_legacy -q` → 35 passed, 17 xfailed (52 tests
  collected). audit 정보용; 본 작업이 이 결과를 변경하지 않는다.

## Commit / Push

- 소스/문서 변경 (`docs/WORK_PLAN.md`) 과 본 report를 두 개 commit
  으로 분리해 stage / commit / push.
- 소스/문서 commit message: `audit: inventory legacy and unused
  scripts`.
- report commit message: `report: 121 legacy unused script cleanup
  audit`.
- push branch: `work/ui-ux-ssot-adoption`.
