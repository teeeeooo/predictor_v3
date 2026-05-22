# 119 — Project-wide New Code Quality Gate

## Goal

Predictor_v3 전체 코드베이스에서 새 script / module / feature를 작성할
때 캡슐화, 모듈 경계, 하드코딩 격리, helper 재사용, interface
boundary를 먼저 고려하도록 문서 규칙과 conservative 자동 guard를
도입한다. 기존 코드 전체 리팩토링이 아니라 "새 코드 작성 사고 방지"
가 목적이다.

## Scope

- task 1: project-wide New Code Quality Gate 원칙을 `AGENTS.md`,
  `AGENT_TASK_ROUTER.md`, `docs/architecture/project_architecture.md`
  에 추가.
- task 2: `tools/check_code_structure.py` conservative 자동 guard
  추가.
- task 3: `tests/test_code_structure_guard.py` guard 단위 + CLI smoke
  테스트.
- task 4: `docs/WORK_PLAN.md` / `AGENT_TASK_ROUTER.md` 연결.
- task 5: `project_log.md` follow-up + 본 report.

## Non-goals

- 기존 코드 리팩토링 / 큰 파일 분리.
- magic string 전체 정리.
- legacy cleanup 실행.
- Tkinter 기능 추가 / PyQt calculator UI 재개·삭제.
- PyInstaller 실행 / size 측정.
- unit adapter 수정 / ML / inverse-search 구현.
- calculator logic / expected / fixture / xfail / profile / dispatcher
  수정.
- CI / GitHub Actions / pre-commit hook / devcontainer 추가.
- result report lifecycle maintenance, active/archive/summaries 이동.
- `ACTIVE_DOCUMENTS.md` 수정.
- AGENTS_FULL.md 열람.

## Verification

- `python3 -B -m py_compile tools/__init__.py
  tools/check_code_structure.py tests/test_code_structure_guard.py`
  → OK.
- `python3 -B tools/check_code_structure.py` →
  `code structure guard: OK (no findings)`, exit 0.
- `python3 -B -m pytest tests/test_code_structure_guard.py
  tests/test_ui_tk_profile_resolver.py
  tests/test_ui_tk_calculator_foundation.py
  tests/test_calculator_schema_boundaries.py
  tests/test_calculator_profiles.py
  tests/test_calculator_dispatcher.py -q` → **78 passed**.
- 전체 (118 / 116 시점 동일 4 PyQt 환경 의존 crash 파일 제외)
  → **568 passed, 1 skipped, 23 xfailed**. 118 baseline 548 + 신규
  20 guard tests = 568. 기존 test 회귀 없음.

## Task Results

### task 1 — 문서 규칙

#### `AGENTS.md`

새 섹션 **New Code Quality Gate** 추가 (Non-Negotiable Boundaries
와 Document Triggers 사이). 적용 범위는 UI 전용이 아니라 `core/`,
`ui/`, `ui_tk/`, `scripts/`, `tools/`, ML adapter, packaging probe
등 모든 새 script / module / feature.

추가한 project-wide 원칙:

- `app_*.py` entrypoint thin (class 정의 금지, module-level 함수 3개
  이하, 80 LOC 이하).
- shell / orchestration / business logic / data transform / formatting
  / I/O를 한 파일에 섞지 않음.
- 구현 전에 module boundary와 public interface를 먼저 정함.
- hard-coded region / profile / metric / result key / default 값은
  SSOT, config, constants, resolver, token module로 격리.
- 같은 literal / mapping / formatting이 2곳 이상 반복되면 helper 또는
  registry 후보로 봄.
- `core/`는 `ui`, `ui_tk`, `PyQt5`, `tkinter`를 import하지 않음.
- UI / CLI / script layer는 core public 진입점 (dispatcher / adapter /
  resolver) 만 사용.
- `ui_tk/`는 `PyQt5` 또는 PyQt `ui` 패키지를 import하지 않음.
- feasibility spike도 예외 없음 (116 단일 파일 spike → 118 reset
  교훈).

추가한 soft limits:

- 새 파일 > 250 LOC 예상 시 분리 계획 먼저 보고.
- 새 파일 > class 3개 예상 시 분리 계획 먼저 보고.
- 새 함수 > 60~80 LOC 예상 시 helper 분리 검토.
- 한 작업에서 신규 책임 영역 3개 이상이면 skeleton/interface 작업과
  구현 작업 분리.

feasibility spike rule:

- spike는 runtime smoke / import smoke / core call smoke / shell
  skeleton까지만 작게 유지.
- spike에서 shell + input + result + resolver + core call + formatting
  을 한 파일에 모두 구현하지 않음.
- 자동 guard `python3 -B tools/check_code_structure.py`를 코드 구조에
  영향을 주는 작업의 검증에 포함 (전체 강제 실행은 아님).

#### `AGENT_TASK_ROUTER.md`

Shared Guardrails / 공통 코드 경계 끝에 한 줄 추가:

> 새 script / module / feature 작성에는 `AGENTS.md`의 New Code Quality
> Gate를 따른다 (thin entrypoint, layer boundary, hard-coded value
> 격리, helper 재사용, soft LOC/class limit, spike도 한 파일에 모든
> 책임 담지 않음). 코드 구조에 영향을 주는 작업은 검증에 `python3 -B
> tools/check_code_structure.py`를 포함하고, 결과를 최종 보고에 짧게
> 남긴다.

이 위치 한 곳만 추가했다 — 기존 ML / 계산기 / 문서 / UI / Packaging /
Logic / Coding work route 각각 안에 중복 기재하지 않는다. 모든 route
가 Shared Guardrails를 함께 적용하기 때문이다.

#### `docs/architecture/project_architecture.md`

`## 6. New module / script boundary` 섹션을 문서 끝에 추가. UI 전용이
아니라 `core/`, `ui/`, `ui_tk/`, `scripts/`, `tools/`, ML adapter,
packaging probe 등 새 module/script/feature 전반에 적용되는 boundary
원칙을 아키텍처 관점에서 요약했다. `AGENTS.md`가 owner이고 본
섹션은 architecture-perspective 요약이라고 명시했다.

기존 architecture 문서의 다른 섹션 (§1~§5) 은 수정하지 않았다.
PyQt / Tkinter 설계 문서 (`docs/designs/...`) 도 수정하지 않았다.

### task 2 — 자동 guard

#### 경로

`tools/check_code_structure.py` (신규, ~280 LOC). `tools/__init__.py`
(빈 package marker).

#### 구현한 checks

1. **core/ banned imports** — `core/`의 모든 `.py` 파일에 대해 ast로
   import 모듈을 모아 `("ui", "ui_tk", "PyQt5", "tkinter")` 중
   하나라도 import하면 error.
2. **ui_tk/ banned imports** — `ui_tk/`의 모든 `.py` 파일에 대해
   `("PyQt5", "ui")` 중 하나라도 import하면 error.
3. **app_*.py thin entrypoint** — 저장소 root의 `app_*.py` 파일에
   대해:
   - class 정의가 1개라도 있으면 error.
   - module-level `def`가 3개 초과면 error.
   - LOC > 80이면 error.
4. **ui_tk multi-책임 anti-pattern** — `ui_tk/` 안의 단일 파일이 ast
   level에서 다음 5종 책임 중 3개 이상을 *정의*하면 error:
   - tab (`ClassDef`, name endswith `"Tab"`)
   - section (`ClassDef`, name endswith `"Section"`)
   - result_panel (`ClassDef`, name endswith `"ResultPanel"`)
   - input_widget (`ClassDef`, name endswith `"EntryRow"`)
   - shell (`ClassDef`, name endswith `"App"` / `"TkApp"`)
   - resolver (`FunctionDef` name `resolve_profile_id` 또는 module
     level `REGION_BY_LABEL` 할당)
   116 spike의 단일 파일 누적을 잡는다. 단순히 `import`만으로는 trip
   하지 않는다 (118 reset의 dedicated 모듈들은 통과).
5. **LOC / class-count soft limits** (warning, not error) — `core/`,
   `ui/`, `ui_tk/`, `scripts/` 의 production 파일에 대해 LOC > 400 /
   top-level class > 5면 warning. allowlist 파일은 제외.

#### Allowlist 기준

`LOC_ALLOWLIST` / `CLASS_ALLOWLIST` 는 script 상단 상수로 정의. 현재
이미 large인 known-large historical 파일만 등록. 새 파일은 allowlist
대상이 아니다. 등록 파일:

- `core/_legacy/calculator_iso16358_legacy.py`
- `core/calculator_iso16358.py`
- `core/calculator_ks_c9306.py`
- `core/calculator_ahri_hspf2.py`
- `core/calculator_en14825.py`
- `core/calculator_asnzs_hspf_excel.py`
- `ui/calc_window.py`
- `ui/calculators_2point.py`
- `ui/spreadsheet_table.py`

CLASS_ALLOWLIST: 위 중 class가 많은 `core/_legacy/...`,
`ui/calculators_2point.py`, `ui/spreadsheet_table.py`, `ui/calc_window
.py`.

#### Output / exit

- 사람이 읽는 텍스트 출력 (`[E]` / `[W]` prefix).
- 모든 finding이 0이면 `code structure guard: OK (no findings)`.
- error가 1개라도 있으면 exit code 1.
- warning만 있을 때는 exit code 0 (warning은 conservative first
  version의 정책).
- `--verbose` flag: error 와 함께 warning 도 출력 (default는 error
  있을 때 warning 요약만).
- `--repo-root` flag: 다른 경로의 repo도 검사 가능 (테스트 fixture
  용도).

#### 외부 의존성

stdlib only (`ast`, `argparse`, `pathlib`, `sys`, `typing`). 외부
라이브러리 의존 없음. PyQt / Tkinter / Excel COM / numpy / pandas
import 없음.

#### 현재 repo 실행 결과

```
$ python3 -B tools/check_code_structure.py
code structure guard: OK (no findings)
$ echo $?
0
```

`--verbose`도 동일 출력. 현재 repo는 본 guard의 모든 error / warning
기준을 통과한다.

### task 3 — Guard tests

`tests/test_code_structure_guard.py` 신규 (~180 LOC, 20 test case).

#### 검증한 violation / pass cases

Banned-import boundary (8 case):

- `core/` 가 `ui_tk`, `PyQt5`, `tkinter` import 시 error (각 1 case).
- `core/` 가 pure Python import만 사용 시 pass.
- `ui_tk/` 가 `PyQt5`, `ui` import 시 error (각 1 case).
- `ui_tk/` 가 `tkinter` + `core.calculator_dispatcher` import 시 pass.

App entrypoint thin (4 case):

- class 정의 1개 → error.
- module-level 함수 5개 (limit + 2) → error.
- LOC 85 (limit + 5) → error.
- 4 LOC thin entrypoint (`from ui_tk... import main; if __name__ ==
  '__main__': main()`) → pass.

ui_tk anti-pattern (3 case):

- 한 파일에 `CalculatorTkApp` + `Iso16358Tab` + `IsoCspfSection` +
  `ResultPanel` + `resolve_profile_id` + `REGION_BY_LABEL` 동시 정의
  → error.
- `Iso16358Tab` class만 정의 + 다른 모듈 import → pass (118 reset의
  실제 형태).
- 같은 multi-responsibility 코드라도 path가 `ui/...`이면 pass (ui_tk
  전용 rule).

Soft limit + allowlist (4 case):

- LOC > 400 → warning (severity `warning`).
- allowlist 적용 시 LOC warning 미발생.
- class > 5 → warning.
- allowlist 적용 시 class warning 미발생.

Repo-wide pass (2 case):

- `guard.run_checks(REPO_ROOT)` 실행 시 `error` finding 0건.
- CLI subprocess (`python3 -B tools/check_code_structure.py`) exit
  code 0 + `code structure guard` 문자열 출력.

#### CLI smoke 결과

`subprocess.run([sys.executable, "-B", "tools/check_code_structure
.py"], cwd=REPO_ROOT)` → returncode 0, stdout `code structure guard:
OK (no findings)`. 외부 binary 의존 없음.

테스트는 PyQt5 / Tkinter import를 요구하지 않으며, 임시 디렉터리도
사용하지 않는다 (in-memory source string + 라이브 repo CLI smoke 만).
macOS PyQt fatal-abort 4 파일과 무관.

### task 4 — Workflow 연결

#### `docs/WORK_PLAN.md`

4y 항목 신규 추가 (4z `Calculator deployment UI feasibility pivot`
앞):

- 119 project-wide new code quality gate 도입.
- 신규 문서 / guard / tests 경로 명시.
- 현재 repo guard 결과 (`OK (no findings)`).
- 코드 구조에 영향을 주는 작업에서 `python3 -B tools/check_code_
  structure.py` 실행을 최종 보고에 포함.
- CI / pre-commit hook 미추가 명시.

기존 4z (Tkinter feasibility pivot), 4c~4g (PyQt UI hold), 5번
(Hong Kong HSPF PyQt UI surface hold) 항목은 그대로 유지.

#### `AGENT_TASK_ROUTER.md`

Shared Guardrails / 공통 코드 경계 한 줄로 충분 (task 1에서 추가).
별도 새 route 정의나 기존 route 안의 중복 기재는 하지 않았다.

#### 사용 방식

- 코드 구조에 영향을 주는 작업: 새 module / 새 script / 큰 리팩토링
  → 검증에 guard 실행 + 결과 보고.
- 문서 only / fixture / xfail / config 값만 바뀌는 작업 → guard 실행
  의무 없음 (코드 구조 변화 없으므로).
- guard error 발견 시 그 자리에서 분리 / 격리 / boundary 정리. 무조건
  allowlist에 추가하지 않는다.
- macOS PyQt fatal-abort 4 파일과 guard는 무관 (guard는 PyQt / Tk
  import / 실행이 필요 없는 정적 분석).

### task 5 — Project log / report

#### `project_log.md`

`### Follow-up — Project-wide new code quality gate` 섹션을 한 번
append. 116 단일-파일 spike → 118 reset 패턴 인식, project-wide gate
+ conservative guard + 20 guard tests 도입, CI/pre-commit 미포함을
명시.

#### lifecycle maintenance 제외 사유

- 114 summary cycle 이후 active 누적: 115 + 116 + 117 + 118 + 119 =
  5건. summary trigger 8~12개의 절반 수준.
- 본 작업은 audit/doc/guard 추가이지 workstream wrap이 아니다.
  lifecycle maintenance와 섞지 않는다.
- `ACTIVE_DOCUMENTS.md` / `result_reports/archive` / `result_reports
  /summaries` 미수정.

## Next Suggested Action

코드 구조에 영향을 주는 다음 작업에서 본 guard를 실제로 사용해
보고, false positive / 누락된 boundary check를 발견하면 119 후속
slice로 정리한다. 우선 후보:

- **macOS Tkinter manual smoke checklist** (118 next suggested
  action 그대로 유지) — docs only, 코드 구조 영향 없음. guard 실행
  의무 없음.
- 또는 ISO section input dict / result formatter pure helper 분리 —
  코드 구조 영향 있음. guard 실행 후 보고.

추천: **macOS Tkinter manual smoke checklist** (118 추천 그대로).
119는 인프라 정비이고, 다음 단계 우선순위는 Tkinter MVP 동작 검증
체크리스트가 자연스러운 연결이다.

## Scope Compliance

- 기존 코드 리팩토링 / 큰 파일 분리 없음.
- magic string 정리 없음. legacy cleanup 실행 없음.
- Tkinter 기능 추가 / PyQt calculator UI 재개·삭제 없음.
- `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`
  미수정.
- PyInstaller 실행 없음.
- unit adapter / ML / inverse-search / calculator logic / expected /
  fixture / xfail / profile / dispatcher 수정 없음.
- CI / GitHub Actions / pre-commit hook / devcontainer 추가 없음.
- result report lifecycle maintenance 미수행 (active 누적이 trigger
  부근 아님 + audit/infra 작업과 섞지 않음).
- `ACTIVE_DOCUMENTS.md` / `result_reports/archive` / `result_reports/
  summaries` 미수정.
- AGENTS_FULL.md 미열람.

## Changed Files

- M `AGENTS.md` (New Code Quality Gate 섹션 추가)
- M `AGENT_TASK_ROUTER.md` (Shared Guardrails / 공통 코드 경계 한 줄
  추가)
- M `docs/architecture/project_architecture.md` (§6 New module /
  script boundary 섹션 추가)
- A `tools/__init__.py`
- A `tools/check_code_structure.py`
- A `tests/test_code_structure_guard.py`
- M `docs/WORK_PLAN.md` (4y 항목 추가)
- M `project_log.md` (follow-up 섹션 append)
- A `result_reports/active/119_project-wide-code-quality-gate.md`

## Known Failures / Risks

- macOS + Python 3.14 + PyQt5 환경의 4 PyQt clipboard/table fatal-
  abort 파일 (`tests/test_iso16358_result_table_copy_tsv.py`,
  `tests/test_iso16358_table_excel_like_behavior.py`, `tests/test_app_
  calculator_ui_smoke.py`, `tests/test_spreadsheet_table_view.py`) 은
  본 작업과 무관. guard 자체는 PyQt / Tk import 없이 정적 분석만
  수행하므로 본 환경에서 정상 통과.
- Conservative first version: magic string 전체 탐지 / hard-coded
  default 값 정적 분석 / 함수 LOC 분석은 의도적으로 포함하지 않았다.
  미래에 false positive 적은 범위로 확대할 수 있다.
- LOC/class soft limit allowlist는 historical 파일 위주이며, 새
  파일이 이 list에 무조건 들어가지 않도록 review 단계에서 사람이
  판단해야 한다.
- guard 실행이 모든 작업에서 강제되지는 않는다. 코드 구조에 영향을
  주는 작업의 검증에 포함하도록 router에 명시했다.
- CI / pre-commit hook은 본 작업 범위 밖. 도입 시점은 별도 결정.

## Test Results

- `python3 -B -m py_compile tools/__init__.py
  tools/check_code_structure.py tests/test_code_structure_guard.py`
  → OK.
- `python3 -B tools/check_code_structure.py` →
  `code structure guard: OK (no findings)`, exit 0.
- `python3 -B -m pytest tests/test_code_structure_guard.py -q` →
  20 passed.
- 위 + `tests/test_ui_tk_profile_resolver.py` +
  `tests/test_ui_tk_calculator_foundation.py` +
  `tests/test_calculator_schema_boundaries.py` +
  `tests/test_calculator_profiles.py` +
  `tests/test_calculator_dispatcher.py` → 78 passed.
- 전체 (위 4 PyQt 환경 의존 crash 파일 제외) → 568 passed, 1 skipped,
  23 xfailed (118 시점 548 + 신규 20).

## Commit / Push

- 소스/문서 변경 (`AGENTS.md`, `AGENT_TASK_ROUTER.md`,
  `docs/architecture/project_architecture.md`, `tools/__init__.py`,
  `tools/check_code_structure.py`,
  `tests/test_code_structure_guard.py`, `docs/WORK_PLAN.md`,
  `project_log.md`) 와 본 report를 두 개 commit으로 분리해 stage /
  commit / push.
- 소스/문서 commit message: `guard: add project-wide code structure
  check`.
- report commit message: `report: 119 project-wide code quality
  gate`.
- push branch: `work/ui-ux-ssot-adoption`.
