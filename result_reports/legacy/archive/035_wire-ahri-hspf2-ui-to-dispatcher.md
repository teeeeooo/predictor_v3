# 035_wire-ahri-hspf2-ui-to-dispatcher

## Goal
- 보고 034 audit의 추천 next action을 실행한다. `ui/calc_window.py:_load_hspf2_calc()`의 하드코딩된 `data/region_configs/usa_hspf2.json` 경로 + `AHRIHSPF2Calculator(hspf2_path)` 직접 생성 패턴을 `create_calculator_for_profile(profile_id="ahri_usa_hspf2")`로 교체해, UI 한 곳에서 profile dispatcher 사용 패턴을 behavior-preserving하게 검증한다.

## Scope
- `ui/calc_window.py`
  - import 영역에 `from core.calculator_dispatcher import create_calculator_for_profile` 한 줄 추가.
  - `_load_hspf2_calc()` 본문 (3줄)을 dispatcher 호출로 교체. 기존 try/except `self.hspf2_calc = None` fallback은 유지.
- 다른 모든 파일(`core/*`, `data/region_configs/*`, `tests/*`, `docs/*`, workbook)은 수정하지 않았다.

## Non-goals
- AHRI SEER2 dropdown / `AHRICalculator` loading 전환 금지 (filename scan 정책 결정 필요).
- ISO / India / Hong Kong / SASO / KS / EN UI 전환 금지.
- profile manifest 추가 등록 금지.
- dispatcher / calculator core / region config / tests / fixtures / docs / workbook 수정 금지.
- AHRI HSPF2 input schema / `_build_hspf2_v3_input` / `calculate_hspf2_v3` / `calculate_ahri()` result composition 수정 금지.
- 계산식 / public API / result schema 변경 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `result_reports/{active,archive,summaries}` 전체 report 번호 최대값 034를 확인하고 다음 번호 035를 사용했다.
- commit 전 `git status` / `git diff --stat`로 staged 대상이 `ui/calc_window.py` 1개로 한정됨을 확인했다. core / region config JSON / tests / docs / workbook은 staged 대상에 포함되지 않았다.
- `python3 -B -m py_compile ui/calc_window.py core/calculator_dispatcher.py core/calculator_profiles.py core/calculator_ahri_hspf2.py` → compile OK.
- Spot check: `create_calculator_for_profile(profile_id="ahri_usa_hspf2")` 결과의 type이 `AHRIHSPF2Calculator`이고 `isinstance(..., AHRIHSPF2Calculator) == True`임을 확인. 동일 calculator class를 동일 config(`data/region_configs/usa_hspf2.json`)로 인스턴스화하므로 후속 `calculate_hspf2_v3(...)` 호출 결과는 변경 없이 유지된다.
- `python3 -B -m pytest tests/test_calculator_dispatcher.py tests/test_calculator_profiles.py -q` → `21 passed`.
- `python3 -B -m pytest tests -q -k "ahri or hspf2 or dispatcher or profile"` → `54 passed`.
- 전체: `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline (보고 032 직후 main HEAD)과 정확히 동일 통계, 동일 failure set. 신규 회귀 없음.

## Task Results
### task 1 결과
- `ui/calc_window.py:_load_hspf2_calc()` 변경 전 본문:
  - `hspf2_path = os.path.join(self.project_root, "data", "region_configs", "usa_hspf2.json")`
  - `try: self.hspf2_calc = AHRIHSPF2Calculator(hspf2_path) except: self.hspf2_calc = None`
- `core/calculator_profiles.py`에서 `ahri_usa_hspf2` profile record 확인:
  - `profile_id="ahri_usa_hspf2"`, `standard="AHRI_210_240"`, `region="usa"`, `metric="HSPF2"`, `mode="heating"`, `calculator_id="ahri_hspf2"`, `config_path="data/region_configs/usa_hspf2.json"`, `enabled=True`.
- `core/calculator_dispatcher.py`의 `ahri_hspf2` 분기 확인: `AHRIHSPF2Calculator(profile.config_path)`로 동일 calculator class를 동일 경로로 인스턴스화한다.
- 결론: dispatcher 호출과 기존 직접 생성은 calculator class도, config 경로도, calculator 동작도 동일하다. drop-in 안전.

### task 2 결과
- `ui/calc_window.py` import 영역에 `from core.calculator_dispatcher import create_calculator_for_profile` 추가.
- `_load_hspf2_calc()` 본문을 다음으로 교체:
  - `try: self.hspf2_calc = create_calculator_for_profile(profile_id="ahri_usa_hspf2") except: self.hspf2_calc = None`
- 변경된 위치 외에는 `ui/calc_window.py` 전체에서 수정 없음. AHRI SEER2 loading (`on_region_changed_ahri`, `scan_configs`), HSPF2 v3 입력 빌더 (`_build_hspf2_v3_input`), 계산 호출 (`calculate_hspf2_v3`), AHRI 결과 구성 (`calculate_ahri()`)은 그대로다.

### task 3 결과
- `python3 -B -m py_compile ui/calc_window.py core/calculator_dispatcher.py core/calculator_profiles.py core/calculator_ahri_hspf2.py` → 정상 통과.
- `python3 -B -m pytest tests/test_calculator_dispatcher.py tests/test_calculator_profiles.py -q` → `21 passed`.
- `python3 -B -m pytest tests -q -k "ahri or hspf2 or dispatcher or profile"` → `54 passed`.
- 전체: `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline `269 passed, 16 failed, 13 xfailed` 대비 통계와 failure set 완전 동일. 회귀 없음.
- 16개 failures는 모두 pre-existing ISO common HSPF formula 47/50 / pure ISO track A / case 3 Excel BM/BO/CD/Y_MIN_Y_EXTD trace / half-to-full / tiny-bin accumulation / formula50 frost 등으로, 본 wiring과 무관하다.
- tests / fixture / golden expected / xfail-pass / region config / calculator code는 일절 수정하지 않았다.

### task 4 결과
- `_load_hspf2_calc()` 변경 전: `usa_hspf2.json` 경로 하드코딩 + `AHRIHSPF2Calculator(hspf2_path)` 직접 생성.
- `_load_hspf2_calc()` 변경 후: `create_calculator_for_profile(profile_id="ahri_usa_hspf2")` 호출. dispatcher가 manifest의 `config_path`로 동일 calculator class를 생성한다.
- 사용한 profile_id: `ahri_usa_hspf2`.
- dispatcher 사용 여부: 예. UI 코드에서 처음으로 `core/calculator_dispatcher.py`를 사용한다.
- AHRI HSPF2 input schema 변경 여부: 없음. `_build_hspf2_v3_input`, `calculate_hspf2_v3` 호출 시그니처와 결과 dict 그대로.
- AHRI SEER2 path 영향 여부: 없음 (`on_region_changed_ahri`, `scan_configs`, `AHRICalculator` 직접 생성 모두 그대로).
- ISO / KS / EN path 영향 여부: 없음 (해당 코드 경로 수정 없음).
- manual UI smoke 필요 여부: 자동 검증으로 dispatcher 결과 calculator class 동일성과 전체 테스트 baseline 동일성을 확인했으나, Calculator UI를 실제로 띄워 AHRI HSPF2 입력 → 계산 결과 dialog가 기존과 동일한지 spot 검사를 수행하는 것이 권장된다 (UI 환경 의존성 때문에 본 turn에서는 수행하지 않음).
- 후속 작업 후보 1개: **AHRI SEER2 dropdown filename scan 정책 audit**. 현재 `scan_configs()`가 `data/region_configs/*.json` 전체를 dropdown에 노출하므로 `usa_hspf2.json` / `korea.json` 등 SEER2 용도가 아닌 파일도 사용자에게 보일 수 있다. dispatcher 전환 전 SEER2 only filter / single profile lock / filename→profile_id 매핑 중 어느 정책을 쓸지 결정하는 audit-only turn이 필요하다.

### task 5 결과
- `git status` / `git diff --stat`으로 변경 범위가 `ui/calc_window.py` 1개 파일 (2 insertions, 2 deletions)로 한정됨을 확인했다.
- `py_compile`과 dispatcher/profile tests 통과 후 source commit: `refactor: wire AHRI HSPF2 UI through dispatcher` (hash `dfecc0b`).
- 본 report 파일을 `result_reports/active/035_wire-ahri-hspf2-ui-to-dispatcher.md`로 생성.
- report commit: `report: record AHRI HSPF2 UI dispatcher wiring` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m pytest tests/test_calculator_dispatcher.py tests/test_calculator_profiles.py -q` → `21 passed`.
- `python3 -B -m pytest tests -q -k "ahri or hspf2 or dispatcher or profile"` → `54 passed`.
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`.
- Baseline (보고 032 직후 / 034 audit 직후) `269 passed, 16 failed, 13 xfailed` 통계와 failure set 완전 일치. 본 wiring으로 인한 신규 회귀 없음.

## Changed Files
- `ui/calc_window.py`
- `result_reports/active/035_wire-ahri-hspf2-ui-to-dispatcher.md`

## Known Failures / Risks
- 16개 pre-existing failures는 main HEAD에도 동일하게 존재하며 본 변경과 무관하다.
- 자동 테스트로 dispatcher가 동일 calculator class를 동일 config로 인스턴스화함은 확인되었지만, Calculator UI를 실제로 띄워 AHRI HSPF2 입력 입력 → 결과 dialog까지 도달하는 manual smoke는 본 turn에서 수행하지 않았다. 가능한 환경에서 다음 turn 또는 사용자 측에서 확인하는 것이 권장된다.
- AHRI SEER2 UI는 여전히 filename scan dropdown + 직접 `AHRICalculator(path)` 패턴을 사용한다. dispatcher 전환은 다음 audit 이후 별도 turn으로 분리.
- ISO / India / Hong Kong / SASO / KS / EN UI 경로는 본 wiring으로 인한 영향 없음. 각각의 dispatcher 전환은 manifest 등록 / 입력 schema 정렬 / SASO override 처리 / 새 selector 등 선행 작업이 필요하다.
- 본 변경은 try/except로 dispatcher 호출 실패 시 `self.hspf2_calc = None`으로 떨어지는 fallback을 유지한다. 만약 manifest에서 `ahri_usa_hspf2`가 사라지면 (예: profile 비활성화) HSPF2 탭 동작은 기존과 마찬가지로 사일런트하게 비활성화된다. 동일 동작 보존이지만 향후 명시적 사용자 알림이 필요하면 별도 작업으로 분리.

## Next Suggested Action
- **AHRI SEER2 dropdown filename scan 정책 audit**: `ui/calc_window.py:scan_configs()`가 `data/region_configs/*.json` 전체를 SEER2 dropdown에 노출하는 현 동작을 점검하고, SEER2-only filter / single `ahri_usa_seer2` profile lock / filename→profile_id 매핑 중 어느 정책으로 dispatcher 전환할지 결정하는 audit-only turn (별도 result report).

## Scope Compliance
- UI: `ui/calc_window.py`의 import 1줄 추가 + `_load_hspf2_calc()` 본문 3→2줄 교체 (`+2 / -2`).
- calculator dispatcher: 수정 없음 (`core/calculator_dispatcher.py` 그대로).
- profile resolver: 수정 없음 (`core/calculator_profiles.py` 그대로).
- calculator core: 수정 없음 (`core/calculator_ahri_hspf2.py`, `core/calculator_ahri_seer2.py`, `core/calculator_iso16358.py`, `core/calculator_ks_c9306.py` 그대로).
- tests: 수정 없음.
- fixtures/golden expected: 수정 없음.
- docs: 수정 없음.
- region config JSON: 수정 없음 (`data/region_configs/*.json` 그대로, `usa_hspf2.json` 포함).
- workbook/reference_files: 수정 없음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- source commit: `dfecc0b refactor: wire AHRI HSPF2 UI through dispatcher`
- report commit: `report: record AHRI HSPF2 UI dispatcher wiring`
- pushed branch: `origin/main`
