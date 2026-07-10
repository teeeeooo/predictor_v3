# 118 — Tkinter Calculator Clean Foundation Reset

## Goal

116 Tkinter feasibility prototype을 그대로 확장하지 않고,
production-candidate clean module foundation으로 재정리한다. 117
audit에서 식별한 단일 파일 비대화 위험을 해소하면서 기존 동작
(ISO 16358 탭 + Hong Kong region + CSPF/HSPF 같은 화면 + CSPF =
4.939 / HSPF = 3.643 smoke + PyQt5 미import + `profile_id`/
`calculator_id`/`config_path` 비노출) 을 유지한다.

## Scope

- task 1: 116 prototype에서 이식할 동작과 폐기할 spike 구조 분리.
- task 2: clean module foundation 구축.
- task 3: import boundary와 public interface 테스트로 보호.
- task 4: WORK_PLAN을 reset 결과에 맞게 짧게 수정. legacy cleanup은
  future phase로 명시.
- task 5: 검증 + 본 report 작성.

## Non-goals

- 새 standard tab / region / metric 추가.
- EN / AHRI / KS Tkinter 구현.
- PyInstaller 실행 / size 추정.
- PyQt calculator UI 재개 / 삭제 / 수정.
- `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`,
  `ui/spreadsheet_table.py`, `ui/calculator_errors.py`, `ui/theme.py`
  수정.
- PyQt tests 수정.
- Train/Predict 리팩토링, unit adapter, ML / inverse-search 구현.
- calculator core / profile / dispatcher / region config / expected /
  fixture / xfail 수정.
- legacy cleanup 실행 (별도 phase로 미룸).
- result report lifecycle maintenance, active/archive/summaries 이동.
- `ACTIVE_DOCUMENTS.md` / `project_log.md` / architecture doc 수정.
- AGENTS_FULL.md 열람.

## Verification

- `python3 -B -m py_compile app_calculator_tk.py ui_tk/__init__.py
  ui_tk/calculator_app.py ui_tk/profile_resolver.py
  ui_tk/result_panel.py ui_tk/input_widgets.py ui_tk/tabs/__init__.py
  ui_tk/tabs/iso16358_tab.py ui_tk/sections/__init__.py
  ui_tk/sections/iso_cspf_section.py
  ui_tk/sections/iso_hspf_section.py` → OK.
- `python3 -B -m py_compile` 신규 test 2개 → OK.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py
  tests/test_ui_tk_calculator_foundation.py tests/test_calculator_
  schema_boundaries.py tests/test_calculator_profiles.py
  tests/test_calculator_dispatcher.py -q` → **58 passed**.
- 전체 (제외 4개 PyQt fatal-abort 파일은 116 Known Failures와 동일)
  `python3 -B -m pytest -q --ignore=tests/test_iso16358_result_table_
  copy_tsv.py --ignore=tests/test_iso16358_table_excel_like_behavior
  .py --ignore=tests/test_app_calculator_ui_smoke.py
  --ignore=tests/test_spreadsheet_table_view.py` → **548 passed, 1
  skipped, 23 xfailed**. 117 시점 533 + 신규 15 (profile_resolver 11
  + foundation 4) = 548.

## Task Results

### task 1 — 이식 대상 / 폐기 대상 식별

이식 대상 (116 `ui_tk/calculator_app.py` 안):

- `CalculatorTkApp` → 새 `ui_tk/calculator_app.py` shell로 이동
  (Notebook + ISO tab 등록만 담당).
- `_Iso16358Tab` → `ui_tk/tabs/iso16358_tab.py::Iso16358Tab`.
- `_CspfSection` → `ui_tk/sections/iso_cspf_section.py::IsoCspfSection`.
- `_HspfSection` → `ui_tk/sections/iso_hspf_section.py::IsoHspfSection`.
- `_ResultPanel` → `ui_tk/result_panel.py::ResultPanel` (public API
  확장: `append`/`set_text`/`clear`/`copy`).
- `_NumericEntryRow` → `ui_tk/input_widgets.py::NumericEntryRow`.
- `REGION_BY_LABEL` / `METRIC_SECTIONS_BY_REGION` /
  `resolve_profile_id` → `ui_tk/profile_resolver.py` (Tkinter / PyQt
  import 없는 pure Python module).

유지된 기존 동작 값 (smoke 보존을 위해 변경 금지):

| 항목 | 값 |
| --- | --- |
| Region 표시 label | `"Hong Kong"` |
| Region internal key | `"hong_kong"` |
| Hong Kong metric sections | `("CSPF", "HSPF")` |
| (Hong Kong, CSPF) → profile_id | `"hong_kong_cspf"` |
| (Hong Kong, HSPF) → profile_id | `"hong_kong_hspf"` |
| CSPF default 정격 능력 [W] | `3500` |
| CSPF default 35_full 능력/전력 [W] | `3600` / `900` |
| CSPF default 35_half 능력/전력 [W] | `1700` / `380` |
| HSPF default 정격 난방 능력 [W] | `6300` |
| HSPF default 7_full 능력/전력 [W] | `6300` / `1500` |
| HSPF default 7_half 능력/전력 [W] | `3200` / `800` |
| Result text — CSPF 본문 | `[CSPF]\n  CSPF = ...\n  CSTL = ...\n  CSEC = ...` |
| Result text — HSPF 본문 | `[HSPF]\n  HSPF = ...\n  HSTL_Wh = ...\n  HSEC_Wh = ...` |
| Window title | `"Calculator (Tkinter)"` (116의 `"Calculator (Tkinter spike)"`에서 변경 — production-candidate shell이라 "spike" suffix 제거) |
| Hong Kong CSPF smoke | `4.939` (`measure_1` fixture와 일치) |
| Hong Kong HSPF smoke | `3.643` (Hong Kong golden case 1) |

폐기 대상:

- `_CspfSection` / `_HspfSection` 내부의 region label hardcode
  (`"Hong Kong"`)를 section 생성자 인자로 이동. `IsoCspfSection(parent,
  region_label, result_callback)` / 동일하게 HSPF.
- `_Iso16358Tab`의 sections-renderer 안에 박혀 있던
  `if metric == "CSPF": _CspfSection(...) elif metric == "HSPF":
  _HspfSection(...)` if/elif 분기 → `_SECTION_FACTORIES` dict.
- top-level 함수 형태의 단일 `resolve_profile_id` if/elif 분기 →
  `_PROFILE_BY_REGION_METRIC` dict + 작은 lookup 함수.

새 legacy copy (`*_legacy`, `*_spike`, `*_old`)는 만들지 않았다.
116 prototype 파일들은 in-place로 새 구조에 맞춰 축소했다.

### task 2 — Clean module foundation

#### 신규 / 수정 module 목록 + LOC

| 파일 | 상태 | LOC | 책임 |
| --- | --- | --- | --- |
| `app_calculator_tk.py` | M (no diff in body) | 16 | thin entrypoint |
| `ui_tk/__init__.py` | M (주석 갱신) | 8 | package marker |
| `ui_tk/calculator_app.py` | M (345 → 54) | 54 | `CalculatorTkApp` shell + Notebook + ISO tab 등록 |
| `ui_tk/profile_resolver.py` | A | 60 | pure Python region/metric → profile_id resolver |
| `ui_tk/result_panel.py` | A | 51 | `ResultPanel` (append / set_text / clear / copy) |
| `ui_tk/input_widgets.py` | A | 50 | `NumericEntryRow` |
| `ui_tk/tabs/__init__.py` | A | 1 | package marker |
| `ui_tk/tabs/iso16358_tab.py` | A | 76 | `Iso16358Tab` region selector + section factory |
| `ui_tk/sections/__init__.py` | A | 1 | package marker |
| `ui_tk/sections/iso_cspf_section.py` | A | 89 | `IsoCspfSection` |
| `ui_tk/sections/iso_hspf_section.py` | A | 84 | `IsoHspfSection` |
| `tests/test_ui_tk_profile_resolver.py` | A | 76 | pure-Python resolver tests |
| `tests/test_ui_tk_calculator_foundation.py` | A | 80 | smoke + Tk widget tree |

ui_tk 총합: ~488 LOC (이전 345 LOC 단일 파일 대비 약 +143 LOC).
증가분은 module boundary / public API 헤더 / docstring / Tab+section
재구성 비용이고, 각 파일은 100 LOC 이하로 한 책임만 담는다.

#### Public interface 요약

```python
# ui_tk/profile_resolver.py  (pure Python)
REGION_BY_LABEL: Mapping[str, str]
METRIC_SECTIONS_BY_REGION: Mapping[str, Tuple[str, ...]]

def region_labels() -> Tuple[str, ...]: ...
def supported_metrics_for(region: str) -> Tuple[str, ...]: ...
def resolve_profile_id(region: str, metric: str) -> str: ...
```

```python
# ui_tk/result_panel.py
class ResultPanel:
    def __init__(self, parent: tk.Widget, *, title: str = "결과") -> None: ...
    def pack(self, **kwargs) -> None: ...
    def append(self, text: str) -> None: ...
    def set_text(self, text: str) -> None: ...
    def clear(self) -> None: ...
    def copy(self) -> None: ...
```

```python
# ui_tk/input_widgets.py
class NumericEntryRow:
    def __init__(self, parent, label, *, width=12, label_width=22) -> None: ...
    def grid(self, **kwargs) -> None: ...
    def pack(self, **kwargs) -> None: ...
    def get_value(self, *, allow_empty=False) -> float | None: ...
    def set_value(self, text: str) -> None: ...
```

```python
# ui_tk/tabs/iso16358_tab.py
class Iso16358Tab(ttk.Frame):
    result_panel: ResultPanel
    def __init__(self, parent: tk.Widget) -> None: ...
```

```python
# ui_tk/sections/iso_cspf_section.py / iso_hspf_section.py
class IsoCspfSection:
    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        result_callback: Callable[[str], None],
    ) -> None: ...
    def pack(self, **kwargs) -> None: ...

class IsoHspfSection:
    # same signature pattern
    ...
```

```python
# ui_tk/calculator_app.py
class CalculatorTkApp:
    root: tk.Tk
    iso_tab: Iso16358Tab
    def __init__(self, root: tk.Tk | None = None) -> None: ...
    def run(self) -> None: ...

def main() -> None: ...
```

#### 의존 방향 (실제 import 그래프)

```
app_calculator_tk.py
        │
        ▼
ui_tk.calculator_app
        │
        ├─→ ui_tk.tabs.iso16358_tab
        │           │
        │           ├─→ ui_tk.profile_resolver  (pure Python)
        │           ├─→ ui_tk.result_panel       (tk only)
        │           ├─→ ui_tk.sections.iso_cspf_section
        │           │           │
        │           │           ├─→ ui_tk.input_widgets       (tk only)
        │           │           ├─→ ui_tk.profile_resolver
        │           │           └─→ core.calculator_dispatcher
        │           │
        │           └─→ ui_tk.sections.iso_hspf_section
        │                       └─→ (동일)
        │
        (ui_tk.calculator_app도 ui_tk.tabs.iso16358_tab 외에는
         core를 직접 import하지 않는다)
```

- `core/` → `ui_tk/` 방향 import 없음 (검색 결과 0건 — 기존 구조 그대로
  유지).
- `ui_tk/` → PyQt 방향 import 없음 (`grep -rn "from PyQt\|import PyQt"
  ui_tk/` 0건).
- core 호출은 `core.calculator_dispatcher.create_calculator_for_profile
  (profile_id=...)` 한 경로만 사용. core internal class
  (`ISO16358Calculator` 등) 직접 import 없음.
- profile_id는 `ui_tk.profile_resolver` 안에서만 등장. section /
  tab / shell code는 region label + metric 만 사용.

#### `ui_tk/calculator_app.py` 축소 결과

- 이전 345 LOC (class 6 + module function 2) → **54 LOC (class 1 +
  module function 1)**.
- 책임: Tk root + `ttk.Notebook` + `Iso16358Tab` 등록 + `main()`.
- 새 standard tab 추가는 `notebook.add(NewTab(notebook), text="...")`
  한 줄로 끝나도록 구조화.

### task 3 — 테스트

신규 test 파일 2개:

#### `tests/test_ui_tk_profile_resolver.py` (11 case, pure Python)

- `region_labels()`가 `"Hong Kong"`을 포함.
- `supported_metrics_for("Hong Kong") == ("CSPF", "HSPF")`.
- internal key (`"hong_kong"`)도 동일 결과.
- unknown region → 빈 tuple.
- `resolve_profile_id("Hong Kong", "CSPF") == "hong_kong_cspf"`.
- `resolve_profile_id("Hong Kong", "HSPF") == "hong_kong_hspf"`.
- internal key + 소문자 metric도 동일.
- unsupported region/metric → `ValueError`.
- `profile_resolver` re-import 시 `tkinter` / `PyQt5` 가 `sys.modules`
  로 끌려오지 않음.

#### `tests/test_ui_tk_calculator_foundation.py` (4 case)

- `import ui_tk.calculator_app` 후 PyQt5 미import 검증.
- `resolve_profile_id` + `create_calculator_for_profile` 경로로 Hong
  Kong CSPF = 4.939 / HSPF = 3.643 smoke 확인.
- `CalculatorTkApp(root=tk.Tk())` 가 withdrawn root 위에 widget tree
  를 구축하고 `iso_tab`이 `Iso16358Tab` 인스턴스이며 `result_panel`이
  존재. Tk가 사용 불가능한 headless 환경에서는 `pytest.skip`.

기존 PyQt fatal-abort test (116 Known Failures 동일 4개)는 건드리지
않았다. PyInstaller / Windows 전용 / screenshot / pixel-perfect test
없음.

### task 4 — WORK_PLAN / design doc

#### `docs/WORK_PLAN.md`

4z 항목 한 문단을 갱신:

- 116 prototype → 117 audit → 118 clean module foundation reset 완료
  를 기록.
- 신규 module 8개 파일 명시.
- PyQt5 미import / CSPF 4.939 / HSPF 3.643 smoke / `profile_id`
  비노출 유지.
- 다음 작업 후보 3개 (macOS manual smoke checklist / ISO section
  추가 분리 / Windows PyInstaller 실측) + 추천 = macOS manual smoke
  checklist.
- legacy cleanup (spike 잔재 / PyQt hold 파일 group review / 미사용
  helper script)은 별도 future cleanup phase로 미룸. 본 작업에서
  삭제 / 정리 미수행.

기존 4c~4g (Slice ζ → η → β → γ → δ) / 5번 (Hong Kong HSPF UI
surface, PyQt) hold 상태는 유지. PyQt calculator UI 자산은 reference
로 유지.

#### `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`

본 reset은 design doc의 IA / MVP scope / profiles / decision criteria
를 변경하지 않는다. design doc은 *지향*을 기술하고 본 reset은 그
지향을 구현 module로 옮긴 작업이다. 따라서 design doc은 **수정하지
않는다**.

#### `docs/guides/lightweight_calculator_packaging_check.md`

빌드 명령에 `app_calculator_tk.py`가 이미 들어가 있어 본 reset 결과와
호환된다. 새 module 추가로 `--add-data` / hidden-import 가정이 바뀌지
않는다 (모든 새 module은 import 시점에 발견 가능). 따라서 guide도
**수정하지 않는다**.

### task 5 — Report

본 파일 (`result_reports/active/118_tkinter-calculator-clean-
foundation-reset.md`)이 task 5의 산출물.

## Next Suggested Action

**macOS Tkinter manual smoke checklist 작성** (`docs/guides/
lightweight_calculator_tk_manual_smoke.md` 신규 후보).

이유:

- Windows 호스트 부재로 PyInstaller 실측은 진행 불가 — packaging
  baseline 결정 시점이 아직 아니다.
- macOS Tkinter가 정상 동작하는 동안 수동 검증 항목 (앱 실행 / 지역
  선택 / CSPF·HSPF 결과값 / 결과 복사 / 결과 지우기 / 지역 재선택 시
  sections 재렌더링) 을 체크리스트로 고정해두면 Windows 측정 시점에
  비교 기준이 명확해진다.
- 코드 변경 없이 docs only로 진행 가능.

대안:

- ISO section의 input dict 구성과 result text formatting을 pure
  helper로 추가 분리 (Slice T3 후보) — section이 2개일 때 over-split
  위험이 있고, 다음 region/standard 추가 직전이 더 자연스러운 trigger.
- Windows PyInstaller 실측 (Slice T6) — Windows 호스트 확보 후로 hold
  유지.

## Scope Compliance

- 새 standard / region / metric 추가 없음.
- EN / AHRI / KS Tkinter 구현 없음.
- PyInstaller 실행 없음. size 추정값 확정 없음.
- PyQt calculator UI 재개 / 삭제 / 수정 없음.
- `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`,
  PyQt EN/AHRI/ISO tab 미수정.
- PyQt tests 미수정.
- Train/Predict 리팩토링, unit adapter, ML / inverse-search 미수행.
- calculator core / profile / dispatcher / region config / expected /
  fixture / xfail 미수정.
- legacy cleanup 실행 없음 (future phase로 미룸).
- result report lifecycle maintenance 미수행 (active 누적이 trigger
  부근 아님 + reset 작업과 섞지 않음).
- active/archive/summaries 이동 없음.
- `ACTIVE_DOCUMENTS.md` / `project_log.md` / architecture doc 미수정.
- AGENTS_FULL.md 미열람.

## Changed Files

- M `app_calculator_tk.py` (no body change — 동일 파일 entrypoint 유지)
- M `ui_tk/__init__.py` (주석을 "production-candidate foundation"으로
  갱신)
- M `ui_tk/calculator_app.py` (345 → 54 LOC, shell로 축소)
- A `ui_tk/profile_resolver.py`
- A `ui_tk/result_panel.py`
- A `ui_tk/input_widgets.py`
- A `ui_tk/tabs/__init__.py`
- A `ui_tk/tabs/iso16358_tab.py`
- A `ui_tk/sections/__init__.py`
- A `ui_tk/sections/iso_cspf_section.py`
- A `ui_tk/sections/iso_hspf_section.py`
- A `tests/test_ui_tk_profile_resolver.py`
- A `tests/test_ui_tk_calculator_foundation.py`
- M `docs/WORK_PLAN.md` (4z 항목 reset 결과 반영)
- A `result_reports/active/118_tkinter-calculator-clean-foundation-
  reset.md`

## Known Failures / Risks

- macOS + Python 3.14 + PyQt5 환경의 pre-existing fatal abort 4종
  (`tests/test_iso16358_result_table_copy_tsv.py`, `tests/test_iso16358_
  table_excel_like_behavior.py`, `tests/test_app_calculator_ui_smoke
  .py`, `tests/test_spreadsheet_table_view.py`) 은 본 reset과 무관하게
  여전히 존재. CI / Windows 환경에서는 정상 통과 가능.
- Tkinter PyInstaller size는 여전히 not measured (Windows 호스트 부재).
- ISO section의 `_read_inputs` + result text formatting은 아직 section
  내부에 매장. 다음 standard 또는 다음 region 추가 시 pure helper
  분리 trigger.
- legacy cleanup은 본 작업 범위 밖. 미사용 helper script / spike
  잔재가 있더라도 별도 audit 후 phase로 진행.

## Test Results

- `python3 -B -m py_compile <11 module files + 2 new tests>` → OK.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py
  tests/test_ui_tk_calculator_foundation.py tests/test_calculator_
  schema_boundaries.py tests/test_calculator_profiles.py
  tests/test_calculator_dispatcher.py -q` → 58 passed.
- 전체 (위 4 PyQt 환경 의존 crash 파일 제외) → 548 passed, 1 skipped,
  23 xfailed. 117 시점 baseline 533 + 신규 15 (profile_resolver 11 +
  foundation 4) = 548. 본 reset이 기존 test 회귀 없음.

## Commit / Push

- 소스/문서 변경 (`app_calculator_tk.py`, `ui_tk/__init__.py`,
  `ui_tk/calculator_app.py`, `ui_tk/profile_resolver.py`,
  `ui_tk/result_panel.py`, `ui_tk/input_widgets.py`,
  `ui_tk/tabs/__init__.py`, `ui_tk/tabs/iso16358_tab.py`,
  `ui_tk/sections/__init__.py`, `ui_tk/sections/iso_cspf_section.py`,
  `ui_tk/sections/iso_hspf_section.py`,
  `tests/test_ui_tk_profile_resolver.py`,
  `tests/test_ui_tk_calculator_foundation.py`, `docs/WORK_PLAN.md`)
  와 본 report를 두 개 commit으로 분리해 stage / commit / push.
- 소스/문서 commit message: `refactor: reset Tkinter calculator
  foundation`.
- report commit message: `report: 118 tkinter calculator clean
  foundation reset`.
- push branch: `work/ui-ux-ssot-adoption`.
