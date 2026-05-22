# 117 — Tkinter Calculator MVP Structure Audit

## Goal

116에서 추가한 Tkinter calculator-only MVP prototype의 구조가 장기
확장에 안전한지 audit하고, 다음 구현 slice를 작게 나눈다. 코드 구현
확장, profile 추가, UI 기능 추가, PyInstaller 실측은 본 작업 범위
밖이다.

## Scope

- task 1: Tkinter prototype inventory.
- task 2: 사용자 정보구조 (규격 탭 + 지역 선택 + multi-metric
  section) 준수 audit.
- task 3: module boundary / 확장 위험 audit.
- task 4: target module structure 제안 (실제 분리는 미수행).
- task 5: 다음 구현 slice 4~6개 분할 + 추천.
- task 6: WORK_PLAN / design doc / report 갱신.

## Non-goals

- Tkinter 기능 구현 확장.
- Tkinter module 실제 분리.
- PyInstaller 실행 / size 추정값 확정.
- PyQt calculator UI 재개 / 삭제 / 수정.
- `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`,
  PyQt EN/AHRI/ISO tab 수정.
- Hong Kong HSPF PyQt UI surface.
- Train/Predict 리팩토링, unit adapter, ML / inverse-search 구현.
- calculator core / profile / dispatcher / region config / expected /
  fixture / xfail 수정.
- result report lifecycle maintenance, active/archive/summaries 이동.
- `ACTIVE_DOCUMENTS.md` / `project_log.md` 수정.
- AGENTS_FULL.md 열람.

## Verification

- `python3 -B -m py_compile app_calculator_tk.py ui_tk/__init__.py
  ui_tk/calculator_app.py` → OK.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py
  tests/test_calculator_profiles.py tests/test_calculator_dispatcher
  .py -q` → 43 passed.
- `python3 -B -m pytest -q --ignore=tests/test_iso16358_result_table
  _copy_tsv.py --ignore=tests/test_iso16358_table_excel_like_behavior
  .py --ignore=tests/test_app_calculator_ui_smoke.py
  --ignore=tests/test_spreadsheet_table_view.py` → 533 passed, 1
  skipped, 23 xfailed. 제외 4개는 116 Known Failures / Risks와 동일한
  macOS + Python 3.14 + PyQt5 환경 의존 fatal abort. 본 audit는 PyQt
  path 미수정.

## Task Results

### task 1 — Tkinter prototype inventory

#### `app_calculator_tk.py` (16 LOC)

Thin entrypoint. Module docstring이 feasibility spike임을 명시.
실제 로직 없음: `from ui_tk.calculator_app import main` + `if __name__
== "__main__": main()`. PyQt5 import 없음.

**판정**: thin entrypoint OK. 추가 정리 필요 없음.

#### `ui_tk/__init__.py` (5 LOC)

Package marker + spike 주석. design doc 경로 참조 1개. PyQt5 import
없음. 추가 정리 필요 없음.

#### `ui_tk/calculator_app.py` (345 LOC)

class/function inventory (line 기준):

| 책임 범주 | 심볼 | 위치 | 비고 |
| --- | --- | --- | --- |
| profile resolution helper | `resolve_profile_id(region, metric)` | line 39 | label/internal key 모두 입력 가능 |
| 상수 (region/metric mapping) | `REGION_BY_LABEL`, `METRIC_SECTIONS_BY_REGION` | line 28~36 | dict 2개 |
| 입력 widget primitive | `_NumericEntryRow` | line 62~84 | `__init__`/`grid`/`get_value`/`set_value` |
| ISO CSPF input section | `_CspfSection` | line 87~153 | `__init__`/`pack`/`_read_inputs`/`_on_calculate` |
| ISO HSPF input section | `_HspfSection` | line 156~221 | `__init__`/`pack`/`_read_inputs`/`_on_calculate` |
| result panel | `_ResultPanel` | line 224~260 | `__init__`/`pack`/`append`/`clear`/`_copy` |
| ISO 16358 tab | `_Iso16358Tab(ttk.Frame)` | line 263~316 | `__init__`/`_on_region_changed`/`_render_region` |
| top-level app shell + Notebook | `CalculatorTkApp` | line 319~337 | `__init__`/`run` |
| module entrypoint | `main()` | line 340 | `CalculatorTkApp().run()` |

LOC 합계: 345. class 6개 + 모듈 함수 2개. PyQt5 import 없음. PyQt 관련
import 정적 검사: `grep -nE "from PyQt|import PyQt" ui_tk/` → 0건.

핵심 책임이 6개 class에 나뉘어 있지만 **모두 하나의 파일**에 존재.

#### Feasibility spike 표시

- `app_calculator_tk.py` line 1 docstring: "feasibility spike". NOT a
  replacement 명시.
- `ui_tk/__init__.py` line 3: "Feasibility spike — NOT a replacement
  for the PyQt calculator UI in ``ui/``".
- `ui_tk/calculator_app.py` line 1 docstring: "feasibility spike",
  line 320 class docstring: "Top-level Tkinter calculator app
  (spike).", line 328 window title: `"Calculator (Tkinter spike)"`.
- design doc `2026-05-22-lightweight-calculator-ui-feasibility.md`
  scope note에 spike 명시.
- WORK_PLAN.md 4z 항목에서 hold 처리 + spike direction 명시.

**판정**: spike marking은 module / class / window title / design doc /
WORK_PLAN 다섯 군데에 일관되게 적용되어 있다.

### task 2 — 정보 구조 준수 audit

#### 선택 단계가 “규격 탭 + 지역 선택”까지만인가

- top-level: `CalculatorTkApp.__init__`이 `ttk.Notebook`에 `_Iso16358Tab`
  하나만 추가 (`text="ISO 16358"`). 다른 표준 탭은 MVP에 없다.
- 표준 탭 내부: `_Iso16358Tab.__init__`이 region selector
  (`ttk.Combobox`, values = `list(REGION_BY_LABEL.keys())` = `["Hong
  Kong"]`)와 sections_holder 두 영역만 노출.
- 선택지에 `profile_id` / `calculator_id` / `config_path` 라벨/
  combobox/dropdown 없음.

**판정**: 사용자가 보는 선택 단계는 "ISO 16358 탭 + 지역(Hong Kong)"
까지만. 준수.

#### profile_id 비노출 검증

- `grep -nE "profile_id|calculator_id|config_path" ui_tk/` → 본 audit
  시점 검사 결과, `ui_tk/calculator_app.py`에서 `profile_id` 사용처는
  `resolve_profile_id()`의 docstring/내부 mapping 결과와
  `create_calculator_for_profile(profile_id=...)` 호출 인자뿐. 사용자
  대면 widget label/text에는 노출되지 않는다.
- `_CspfSection._on_calculate`와 `_HspfSection._on_calculate` 모두
  내부에서 `resolve_profile_id("Hong Kong", "CSPF")` /
  `resolve_profile_id("Hong Kong", "HSPF")` 호출 후 dispatcher에
  주입.

**판정**: 준수.

#### Hong Kong CSPF/HSPF 같은 화면 배치

- `METRIC_SECTIONS_BY_REGION["hong_kong"] = ("CSPF", "HSPF")`.
- `_Iso16358Tab._render_region` 가 선택된 region에서 metric tuple을
  꺼내 `_CspfSection`과 `_HspfSection`을 `sections_holder` 안에 차례로
  `pack(side=tk.TOP, fill=tk.X, ...)`로 stack.
- result panel은 sections 아래에 단일 `_ResultPanel` 인스턴스로 공유
  (CSPF/HSPF 모두 동일 panel에 `append`).

**판정**: 한 화면 위에서 두 metric section이 위/아래로 동시에 보이고,
result도 공유. 준수.

#### 내부 resolve가 region + metric → profile_id

- `resolve_profile_id(region, metric)` 가 region label 또는 internal
  key 두 형태 모두 받아 casefold 후 `(hong_kong, cspf)` →
  `hong_kong_cspf`, `(hong_kong, hspf)` → `hong_kong_hspf` 매핑. 그 외
  조합은 `ValueError`.

**판정**: 준수. 단, 매핑 dict로 외부화하지 않고 `if/elif`로 hard-code
되어 있다 (task 3에서 확장 시 정리 후보).

#### 방식 B(지역별 탭) / 방식 C(nested tab)로 새고 있는가

- `ttk.Notebook` 인스턴스는 `CalculatorTkApp` top-level 한 개뿐.
- `_Iso16358Tab` 내부에 추가 `Notebook` 없음.

**판정**: 방식 A (standard tab + region selector + multi-metric
section) 한 가지만 사용. nested tab 없음. 준수.

#### KS C 9306 분리 원칙

- design doc `2026-05-22-lightweight-calculator-ui-feasibility.md`
  line 163~166: "KS C 9306 merged into the ISO 16358 tab as a 'Korea'
  option: rejected. ... KS C 9306 stays in its own tab if/when
  added."
- line 208 / 238도 동일 결정 재진술.
- prototype에 KS C 9306 코드 미포함.

**판정**: design doc에 명시. prototype에는 실제 KS C 9306 UI 없음 ;
원칙 위반 없음. follow-up 없음.

### task 3 — module boundary / 확장 위험

#### 단일 파일 비대화 위험

- 현재 345 LOC. PyQt `ui/calc_window.py`가 ~852 LOC 시점부터 boundary
  분리가 trigger되었다 (113 design doc 참고).
- 본 prototype은 ISO 16358 + Hong Kong (CSPF + HSPF) 단일 조합만
  지원. 같은 패턴으로 EN 14825 (SEER + SCOP) 탭과 AHRI 210/240 (SEER2
  + HSPF2) 탭을 추가하면 section / tab class가 4~6개 더 늘어난다.
- AHRI는 horizontal table (`SpreadsheetTableView` 등가물) + system-
  type radios + HSPF2 v3 derivation을 가져 section 한 개의 LOC가 100을
  쉽게 넘는다. EN SCOP는 multi-climate selection 때문에 200 LOC급.
- **추정**: 같은 파일에 그대로 누적 시 ISO + EN + AHRI 다 합치면 LOC가
  PyQt `calc_window.py` 비대화 수준 (800~1000+)으로 다시 도달한다.

**판정**: 단일 파일 유지가 **다음 standard 추가 (EN 또는 AHRI) 1회
까지는 안전**, 두 번째 standard 추가 직전에 분리 필요.

#### Hard-coded region/profile mapping 위험

- `REGION_BY_LABEL`, `METRIC_SECTIONS_BY_REGION`, `resolve_profile_id`
  의 if/elif 분기 모두 `ui_tk/calculator_app.py` 안에 위치.
- 새 region/metric 추가마다 3곳 동시 수정 필요.
- core의 `core/calculator_profiles.py`에 이미 manifest가 있고
  `resolve_calculator_profile(region=..., metric=..., mode=...)` 가
  존재한다 — Tkinter resolver는 manifest를 재참조하지 않고 별도
  hard-code.

**판정**: 단기에는 OK (region 1개). region 1~2개 추가 단계에서
**manifest 재사용 또는 별도 resolver module 분리 후보**. core resolver
재사용이 가능한지 별도 audit slice 필요.

#### Duplicate logic 위험

- `_CspfSection` / `_HspfSection`은 widget 구성 (LabelFrame +
  NumericEntryRow * N + Button) + `_read_inputs` (Entry → dict) +
  `_on_calculate` (resolve → dispatch → format) 패턴이 동일.
- HSPF 추가 시 `_read_inputs` 구조가 region 별로 다르지만 (Hong Kong
  HSPF는 `rated_heating_capacity` + `7_full` / `7_half`, ISO 16358-2
  공식 case는 다른 키), section class 안에 region별 분기를 또
  if/elif로 누적할 위험.

**판정**: 두 section의 구조 유사도가 높아 base class 추출 후보.
지금 당장은 아니지만 **section 4~5개 시점에 base class 필요**.

#### core / UI coupling

- UI section 내부에서 직접 `create_calculator_for_profile(profile_id=
  ...)` 호출하고 결과 dict의 key (`cspf`, `cstl_wh`, `csec_wh`, `hspf`,
  `hstl_wh`, `hsec_wh`)를 hard-code로 format.
- core가 ui_tk를 import하지는 않는다 (`grep -rn "ui_tk" core/` → 0건
  예상; 본 audit에서는 prototype의 boundary 책임으로 미검). UI →
  dispatcher → core 방향 단방향.

**판정**: 의존 방향은 OK. 결과 key hard-code는 PyQt UI도 동일한 형태로
가지고 있어 *현 단계에서는* tolerable. result formatter 분리 시점에
key SSOT 정합도 함께 다룬다.

#### widget 생성 vs input dict 변환 분리

- 현재 `_CspfSection._read_inputs`는 Entry 읽기 + dict 구성을 동시
  수행. core 호출용 input shape이 section class 안에 매장되어 있어
  test 시 widget 없이 input shape만 비교하기는 어렵다.
- 단, prototype 단계에서는 input shape이 core test fixture와 동일하므로
  중복 schema는 아니다.

**판정**: 분리는 next slice의 후보. 지금 강제 분리는 spike 가치보다
overhead가 크다.

#### result text formatting 재사용성

- `_CspfSection`과 `_HspfSection`이 각자 `f"[CSPF]\n  CSPF = ..."`,
  `f"[HSPF]\n  HSPF = ..."`로 동일 패턴 반복. result formatter를
  pure-Python helper로 빼면 단위 테스트 가능.

**판정**: result_panel과 별도로 `format_cspf_result(result_dict) -> str`
같은 pure helper 후보가 있다 (현 시점 분리는 not yet).

#### PyQt `calc_window.py` 비대화 반복 가능성

- 현재 구조를 그대로 두고 EN + AHRI section을 추가하면 PyQt에서 본
  monolith pattern을 그대로 재현할 가능성 **높음**.
- 다만 PyQt `calc_window.py`는 tab init / read helper / calculate /
  result label / validation helper 모두 한 클래스에 매장되어 있던 것이
  문제였고, Tkinter prototype은 이미 section class로 1차 분리됨.
- 따라서 **위험은 존재하지만 PyQt 때보다 출발점이 좋다.**

#### 분리해야 할 것 vs 보류 가능한 것

지금 분리해야 할 것 (다음 standard 추가 전):

- result panel: 어차피 모든 section이 공유하므로 별도 module 후보 (작은
  분리, 의존이 명확).
- profile resolver: hard-code mapping을 별도 module로 빼면 새 region
  추가 시 PR diff가 좁아진다 (계속 한 파일에 두면 region 추가마다
  같은 파일이 grow).

다음 standard 추가 직전까지 보류 가능:

- section base class 추출 (section이 2개일 때는 over-engineering).
- input schema와 widget 분리 (현재 1:1 mapping이 단순함).
- result formatter pure helper 분리 (text format이 매우 짧아 분리 효익
  작음).
- tab module 분리 (`ui_tk/tabs/iso16358_tab.py`) — 표준 탭이 1개일 때는
  shell과 한 파일이어도 가독성 손해가 작음.

### task 4 — target module structure 제안

#### 분리 단계별 target

세 단계로 나눈다. 각 단계는 다음 standard 추가 직전에 trigger한다.

##### Stage 0 (현 상태)

```
app_calculator_tk.py          # thin entrypoint
ui_tk/
├── __init__.py
└── calculator_app.py         # 모든 책임 (~345 LOC)
```

OK 기준: ISO 16358 + Hong Kong 하나만 wiring. 다음 PyInstaller 실측
까지 유지 가능.

##### Stage 1 — result panel + profile resolver 분리 (다음 region 추가 또는 다음 metric/section 추가 전에 1회)

```
app_calculator_tk.py          # thin entrypoint (변경 없음)
ui_tk/
├── __init__.py
├── calculator_app.py         # CalculatorTkApp shell + Notebook
├── result_panel.py           # _ResultPanel → ResultPanel (public)
└── profile_resolver.py       # REGION_BY_LABEL, METRIC_SECTIONS_BY_REGION, resolve_profile_id
```

`calculator_app.py`는 여전히 ISO 16358 탭 + section 두 개를 그대로
가진다. result_panel과 profile_resolver만 외부화.

##### Stage 2 — ISO 탭 / section 모듈 분리 (두 번째 standard 추가 직전)

```
app_calculator_tk.py
ui_tk/
├── __init__.py
├── calculator_app.py         # CalculatorTkApp shell + Notebook 등록
├── result_panel.py
├── profile_resolver.py
├── input_widgets.py          # NumericEntryRow 등 reusable primitive
├── tabs/
│   ├── __init__.py
│   └── iso16358_tab.py       # Iso16358Tab
└── sections/
    ├── __init__.py
    ├── iso_cspf_section.py   # IsoCspfSection
    └── iso_hspf_section.py   # IsoHspfSection
```

이 시점에 section base class (`InputSectionBase` 등)를 도입할지 결정.
section이 4개 이상일 때만 base class trigger.

##### Stage 3 (advisory, EN 또는 AHRI 추가 시)

```
ui_tk/tabs/en14825_tab.py     # En14825Tab
ui_tk/sections/en_seer_section.py
ui_tk/sections/en_scop_section.py
# 또는
ui_tk/tabs/ahri_tab.py
ui_tk/sections/ahri_seer2_section.py
ui_tk/sections/ahri_hspf2_section.py
```

base class / table-input adapter 도입 여부를 EN/AHRI 추가 시점에
재평가. Tkinter table 동등물 (TSV copy/paste/undo)이 필요한지도 이 시점
재평가.

#### Public interface 후보

각 module의 public surface를 spike-final이 아니라 candidate로
정의한다 (실제 분리 시 조정 가능).

```python
# ui_tk/profile_resolver.py
REGION_BY_LABEL: Mapping[str, str]
METRIC_SECTIONS_BY_REGION: Mapping[str, Tuple[str, ...]]

def resolve_profile_id(region: str, metric: str) -> str: ...
def supported_metrics_for(region: str) -> Tuple[str, ...]: ...
def region_labels() -> Tuple[str, ...]: ...
```

```python
# ui_tk/result_panel.py
class ResultPanel:
    def __init__(self, parent: "tk.Widget") -> None: ...
    def pack(self, **kwargs) -> None: ...
    def append(self, text: str) -> None: ...
    def set_text(self, text: str) -> None: ...
    def clear(self) -> None: ...
    def copy(self) -> None: ...
```

```python
# ui_tk/input_widgets.py
class NumericEntryRow:
    def __init__(self, parent, label: str, *, width: int = 12) -> None: ...
    def grid(self, **kwargs) -> None: ...
    def get_value(self, *, allow_empty: bool = False) -> float | None: ...
    def set_value(self, text: str) -> None: ...
```

```python
# ui_tk/tabs/iso16358_tab.py
class Iso16358Tab(ttk.Frame):
    def __init__(self, parent, result_panel: ResultPanel) -> None: ...
    def select_region(self, region_label: str) -> None: ...
```

```python
# ui_tk/sections/iso_cspf_section.py
class IsoCspfSection:
    def __init__(
        self,
        parent,
        region_label: str,
        result_callback: Callable[[str], None],
    ) -> None: ...
    def pack(self, **kwargs) -> None: ...
```

```python
# ui_tk/sections/iso_hspf_section.py
class IsoHspfSection:
    # 같은 시그니처 패턴
    ...
```

#### 의존 방향

```
app_calculator_tk.py
        │
        ▼
ui_tk/calculator_app.py
        │
        ├─→ ui_tk/tabs/iso16358_tab.py
        │           │
        │           ├─→ ui_tk/sections/iso_cspf_section.py
        │           │           │
        │           │           ├─→ ui_tk/input_widgets.py
        │           │           ├─→ ui_tk/profile_resolver.py
        │           │           └─→ core.calculator_dispatcher
        │           │
        │           └─→ ui_tk/sections/iso_hspf_section.py
        │                       └─→ (동일)
        │
        └─→ ui_tk/result_panel.py
```

규칙:

- `core/` 는 절대 `ui_tk/` 를 import하지 않는다.
- `ui_tk/` 는 `core.calculator_dispatcher` / `core.calculator_profiles`
  까지만 import. core internal class (`ISO16358Calculator` 등) 직접
  import 금지. PyQt `ui/` 는 import하지 않는다 (PyQt5 미로드 보장).
- `profile_resolver`는 pure-Python (Tkinter import 없음) — 단위
  테스트 용이성.
- `input_widgets`, `result_panel`, `sections/*`, `tabs/*`는 Tkinter
  specific.
- section 내부에서 calculator 호출과 result 포맷은 분리 가능하지만,
  Stage 2까지 같이 둔다 (over-split 방지).

### task 5 — 다음 구현 slice 후보

#### Packaging 전(現 macOS 환경에서 진행 가능)

1. **Slice T1 — Result panel + profile resolver extraction**
   (Stage 1)
   - 목적: 추가 region/metric 도입 전에 가장 의존이 명확한 두 helper를
     외부화한다.
   - 수정 대상 후보: `ui_tk/result_panel.py` (신규),
     `ui_tk/profile_resolver.py` (신규), `ui_tk/calculator_app.py`
     (import 교체).
   - 포함 범위: `_ResultPanel` 공개화 (`ResultPanel`), region/metric
     mapping과 `resolve_profile_id` 이동.
   - 제외 범위: section 분리, tab 분리, base class 도입.
   - 선행 조건: 현 prototype 그대로 (없음).
   - 검증 방법: `python3 -B -m py_compile ...`, profile resolver 단위
     테스트 (`tests/test_ui_tk_profile_resolver.py` 후보), Tk widget
     구축 smoke.

2. **Slice T2 — ISO section / tab module split + NumericEntryRow
   외부화** (Stage 2)
   - 목적: 두 번째 region 또는 두 번째 standard 추가 직전에 1회 분리.
   - 수정 대상 후보: `ui_tk/input_widgets.py` (신규),
     `ui_tk/tabs/iso16358_tab.py` (신규),
     `ui_tk/sections/iso_cspf_section.py` (신규),
     `ui_tk/sections/iso_hspf_section.py` (신규).
   - 포함 범위: section / tab class 이동 + import 교체.
   - 제외 범위: section base class, EN/AHRI 추가, result formatter
     pure helper 분리.
   - 선행 조건: Slice T1 완료.
   - 검증 방법: py_compile + 기존 Tkinter widget 구축 smoke +
     Hong Kong CSPF 4.939 / HSPF 3.643 dispatcher 호출 smoke.

3. **Slice T3 — ISO CSPF/HSPF section cleanup**
   - 목적: section 내부에서 input dict 구성과 result text formatting을
     pure helper로 분리해 단위 테스트 가능하게 만든다.
   - 수정 대상 후보: `ui_tk/sections/iso_*_section.py`,
     `ui_tk/result_formatters.py` (신규 후보).
   - 포함 범위: `_read_inputs` → 모듈 level `build_iso_cspf_input(...)`
     / `build_iso_hspf_input(...)`, `_on_calculate`의 format 문자열을
     `format_cspf_result(result)` / `format_hspf_result(result)`로 분리.
   - 제외 범위: section base class, EN/AHRI 추가.
   - 선행 조건: Slice T2 완료.
   - 검증 방법: 신규 pure-helper 단위 테스트 (Tkinter 미요구),
     Tk smoke 유지.

4. **Slice T4 — Result panel cleanup**
   - 목적: result panel API를 공개화하고 (`set_text`, `append`,
     `clear`, `copy`) 다중 호출 시 누적/덮어쓰기 모드를 명시한다.
   - 수정 대상 후보: `ui_tk/result_panel.py`,
     `ui_tk/sections/iso_*_section.py`.
   - 포함 범위: API 정리 + section callback signature 통일.
   - 제외 범위: result panel UI 디자인 변경, theme token 도입.
   - 선행 조건: Slice T1 완료 (T2/T3와 독립).
   - 검증 방법: result panel 단위 테스트 (Tkinter root 없이 mock
     widget) + Tk smoke.

5. **Slice T5 — macOS Tkinter manual smoke checklist** (audit/doc
   only)
   - 목적: Windows 부재로 PyInstaller 실측 불가한 동안, macOS에서
     수동으로 확인해야 할 항목을 checklist 형태로 docs/guides에 추가.
   - 수정 대상 후보: `docs/guides/lightweight_calculator_tk_manual_
     smoke.md` (신규) 또는 `docs/guides/lightweight_calculator_
     packaging_check.md`에 섹션 추가.
   - 포함 범위: 앱 실행 / 지역 선택 / CSPF 결과 = 4.939 확인 / HSPF
     결과 = 3.643 확인 / 결과 복사 클립보드 확인 / 결과 지우기 확인 /
     지역 재선택 시 sections 재렌더링 확인.
   - 제외 범위: 자동화 테스트, 스크린샷, PyQt smoke.
   - 선행 조건: 없음.
   - 검증 방법: 체크리스트 문서가 본 audit의 task 1 inventory와
     일치하는지 self-review.

#### Packaging 이후 (Windows 호스트 확보 후)

6. **Slice T6 — Windows PyInstaller size measurement** (HOLD — Windows
   호스트 부재)
   - 목적: PyQt baseline vs Tkinter spike의 PyInstaller dist 크기를
     실측해 decision criteria 평가.
   - 수정 대상 후보: 새 후속 report (예: `118_...`).
   - 포함 범위: `docs/guides/lightweight_calculator_packaging_check.md`
     의 명령 그대로 실행 + 측정 수치 기록.
   - 제외 범위: UPX / spec 파일 / 코드 서명.
   - 선행 조건: Windows 호스트 + 동일 Python 버전 + PyInstaller +
     PyQt5 venv.
   - 검증 방법: dist 폴더 / exe 크기 측정 + Tk DLL 포함 / PyQt5 미포함
     확인.

#### 추천 next action

**Slice T1 (Result panel + profile resolver extraction)**.

추천 기준:

- Windows 부재로 packaging 실측은 불가능. 그동안 코드 완성도를 올려야
  packaging 결정 후 다음 standard (EN/AHRI) 도입 단계에서 PR 폭이
  작아진다.
- Slice T1은 **외부 의존성 없이** 가장 작은 분리. 두 helper 모두 region
  추가/metric 추가 시 가장 먼저 grow하는 hot spot이라 미리 빼는
  효익이 크다.
- profile_resolver를 pure Python으로 빼면 Tkinter 없이 단위 테스트
  추가 가능 → Tkinter / PyQt 어느 쪽 direction에서도 재사용 가능.
- packaging 실측 가능 시점에 prototype size에 거의 영향이 없어
  baseline 비교가 흔들리지 않는다.

기각한 후보:

- Slice T2: section/tab 분리는 두 번째 region 또는 두 번째 standard 추가
  직전 trigger 권장 — 현재 region 1개 시점에 강제 분리는 over-split.
- Slice T3 / T4: T1 → T2 이후 자연스럽게 진행.
- Slice T5: 체크리스트 문서는 가치 있지만 audit 산출물 (본 117 report)
  의 task 5 자체가 부분 대체. 단독 slice로 분리할 만한 효익 작음.
- Slice T6: 환경 부재로 hold.

### task 6 — 문서 / report 갱신

#### `docs/WORK_PLAN.md`

다음 짧은 갱신:

- 4z 항목 끝에 "다음 구현 slice 후보는 117 audit (Tkinter MVP 구조)에
  정리되어 있다. 추천 next action은 Slice T1 — `ui_tk/result_panel.py`
  + `ui_tk/profile_resolver.py` 추출 (Stage 1). Windows PyInstaller
  실측은 환경 확보 후 별도 slice (T6, hold)." 한 문장 추가.

audit 결과가 4c~4g hold와 5번 hold를 바꾸지 않는다 (여전히 PyQt UI
hold 유지, packaging 실측 hold 유지). 따라서 WORK_PLAN의 다른 줄은
수정하지 않는다.

#### `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`

본 audit에서 design doc의 누락/모호 항목을 점검했으나 다음 이유로
**수정하지 않는다**:

- 정보구조 (standard tab + region selector + multi-metric section)와
  KS C 9306 분리 원칙은 line 130~170에 명확히 기술되어 있다.
- MVP scope, profile, packaging, decision criteria, fallback도 명확.
- 본 audit에서 추가로 식별한 항목 (단계별 module 분리 trigger, slice
  목록)은 *구현 plan*에 속해 design doc보다 report (본 117) 또는
  WORK_PLAN에 두는 게 적합.

#### lifecycle maintenance 제외 사유

- 114 summary cycle 직후 active 누적: 115 (이미 존재) + 116 (방금) +
  117 (본 작업) = 3건. trigger 기준 8~12개의 절반 미만.
- 본 작업은 audit/docs only. lifecycle maintenance와 섞지 않는다
  (`AGENT_TASK_ROUTER.md` Lifecycle Check 원칙).
- `ACTIVE_DOCUMENTS.md` / `project_log.md`는 본 작업 범위 밖.

## Next Suggested Action

**Slice T1 — `ui_tk/result_panel.py` + `ui_tk/profile_resolver.py`
extraction (Stage 1)**.

소스: `ui_tk/calculator_app.py`의 `_ResultPanel` 공개화 +
`REGION_BY_LABEL` / `METRIC_SECTIONS_BY_REGION` / `resolve_profile_id`
이동. `calculator_app.py`는 import 교체만 수행. 단위 테스트
(`tests/test_ui_tk_profile_resolver.py` 후보) 추가는 Slice T1 본
작업에서 결정.

## Scope Compliance

- Tkinter prototype 코드 수정 미수행 (inventory만 수행).
- Tkinter module 실제 분리 미수행.
- profile 추가 / region 추가 / UI 기능 추가 미수행.
- PyInstaller 실행 / size 추정 미수행.
- PyQt calculator UI 재개 / 삭제 / 수정 미수행.
- `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`,
  PyQt EN/AHRI/ISO tab 수정 미수행.
- Train/Predict 리팩토링, unit adapter, ML 미수행.
- calculator core / profile / dispatcher / region config / expected /
  fixture / xfail 수정 미수행.
- result report lifecycle maintenance 미수행 (trigger 부근 아님 +
  audit 작업과 섞지 않음).
- `ACTIVE_DOCUMENTS.md`, `project_log.md` 미수정.
- active/archive/summaries 이동 미수행.
- AGENTS_FULL.md 미열람.

## Changed Files

- M `docs/WORK_PLAN.md` (4z 항목에 한 문장 추가, 다음 slice 추천 명시)
- A `result_reports/active/117_tkinter-calculator-mvp-structure-audit
  .md`

## Known Failures / Risks

- 본 macOS + Python 3.14 + PyQt5 환경의 전체 pytest는 4 PyQt
  clipboard / table 테스트에서 fatal abort (`tests/test_iso16358_
  result_table_copy_tsv.py`, `tests/test_iso16358_table_excel_like_
  behavior.py`, `tests/test_app_calculator_ui_smoke.py`,
  `tests/test_spreadsheet_table_view.py`). 116 Known Failures와 동일,
  본 audit는 PyQt path를 수정하지 않는다. CI / 회사 PC (Windows)
  환경에서는 정상 통과 가능.
- Tkinter packaging 크기는 **여전히 not measured**. decision criteria
  적용은 Windows 호스트 확보 후 가능.
- 본 audit는 prototype의 *구조*만 점검했다. Tkinter UI의 키보드
  탐색 / paste path / numeric validation / 단위 표시 / 에러 메시지
  표면은 별도 design slice가 필요하다 (현재 prototype은 기본 `ttk.
  Entry` 동작만 사용).
- Stage 2/3 trigger (다음 standard 추가) 까지의 단일 파일 grow는
  여전히 가능. Slice T1을 미루면 EN/AHRI 추가 시 PR diff가 커진다.

## Test Results

- `python3 -B -m py_compile app_calculator_tk.py ui_tk/__init__.py
  ui_tk/calculator_app.py` → OK.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py
  tests/test_calculator_profiles.py tests/test_calculator_dispatcher
  .py -q` → 43 passed.
- `python3 -B -m pytest -q --ignore=tests/test_iso16358_result_table_
  copy_tsv.py --ignore=tests/test_iso16358_table_excel_like_behavior.
  py --ignore=tests/test_app_calculator_ui_smoke.py
  --ignore=tests/test_spreadsheet_table_view.py` → 533 passed, 1
  skipped, 23 xfailed.

## Commit / Push

- 단일 source/doc commit (`docs/WORK_PLAN.md`) + 별도 report commit
  (`result_reports/active/117_tkinter-calculator-mvp-structure-audit
  .md`).
- source/doc commit message: `audit: assess Tkinter calculator MVP
  structure`.
- report commit message: `report: 117 tkinter calculator MVP
  structure audit`.
- push branch: `work/ui-ux-ssot-adoption`.
