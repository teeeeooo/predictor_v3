# 037_separate-ks-c9306-measured-input-prep

## Goal
- 보고 036 audit의 추천 next action을 실행한다. `KSC9306Calculator.calculate_cspf(...)`에서 measured input preparation 책임만 KS module 내부로 분리하는 첫 단계 behavior-preserving refactor를 수행한다. ISO common CSPF engine으로의 thin delegate는 유지하되, KS 측에서 `_round_test_value` / `_prepare_measured_inputs` helper를 도입해 `calculate_cspf` 진입점에서 먼저 선전처리한 뒤 delegate에 넘긴다.

## Scope
- `core/calculator_ks_c9306.py`
  - 상단 import에 `from decimal import Decimal, InvalidOperation, ROUND_HALF_UP` 추가.
  - `KSC9306Calculator`에 KS 측 `_round_test_value(value)` 추가 (ISO 동명 helper와 동일 ROUND_HALF_UP 방식).
  - `KSC9306Calculator`에 KS 측 `_prepare_measured_inputs(measured_inputs)` 추가 (capacity/power만 정수화, 새 dict 반환, unknown field 보존, 입력 dict mutate 금지).
  - `KSC9306Calculator.calculate_cspf(...)` 진입점에서 `_prepare_measured_inputs` 호출 + `declared_capacity` 선정수화 후 기존 ISO delegate 분기(`_iso_calculator_ref` 우선, 없으면 lazy import + `ISO16358Calculator(self._config_path)`)로 넘긴다. 기존 fail-fast 메시지는 유지.

## Non-goals
- `core/calculator_iso16358.py` 수정 금지 (helper 이동/삭제, `ks_intersection` 분기 제거, ISO `_prepare_measured_inputs`/`_round_test_value` 변경 모두 금지).
- KS CSPF full bin loop / regime selection / accumulation / result dict composition KS module 복제 금지.
- `_ks_intersection_power` wrapper 제거 금지.
- KS HSPF body (`calculate_hspf`, `_ks_hspf_*`, `_calculate_ks_c9306_hspf`) 수정 금지.
- profile resolver / dispatcher / UI / region config JSON / tests / fixtures / docs / workbook 수정 금지.
- 새 테스트 추가 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `result_reports/{active,archive,summaries}` 전 디렉터리 최대 번호 036 확인 후 다음 번호 037 사용.
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py` → 통과.
- KS CSPF spot check (`KSC9306Calculator.from_config_path("data/region_configs/korea.json").calculate_cspf({35_full: cap=6035.8/pow=1641.4, 35_half: cap=3420.4/pow=679.4, 29_min: cap=1759.6/pow=201.7}, declared_capacity=6000)`) → `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852` (기존 기준값 동일).
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- 전체 `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 통계 / failure set 완전 동일, 회귀 없음.
- `git diff --stat`으로 source 변경이 `core/calculator_ks_c9306.py` 1개 (46 insertions, 0 deletions)로 한정됨을 확인.

## Task Results
### task 1 결과
- `core/calculator_iso16358.py`
  - `_round_test_value` (line 48): `int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))`.
  - `_prepare_measured_inputs` (line 65): `round_test_values=False`이면 원본 그대로, true이면 새 dict에 capacity/power만 `_round_test_value`로 정수화, 예외 시 원값 유지, unknown field는 그대로.
  - `calculate_cspf` (line 2160): 첫 줄에서 `_prepare_measured_inputs(...)` 호출 후 declared_capacity는 `round_test_values`일 때 `_round_test_value` 정수화.
  - 동일한 round/prepare 로직이 line 1935 (HSPF 경로)에도 적용됨.
- `core/calculator_ks_c9306.py`
  - `calculate_cspf` (line 63 기준 이전): KS 측 선전처리 없이 곧장 `_iso_calculator_ref.calculate_cspf(...)` 또는 lazy import 후 `ISO16358Calculator(self._config_path).calculate_cspf(...)`로 thin delegate.
  - `from_config_path`는 `_config_path` 설정, `from_iso_calculator`는 `_iso_calculator_ref` 설정. 둘 다 KS module에서 ISO config/state를 직접 갖고 있어 `self.config.get("round_test_values", False)` 호출이 KS 측에서도 valid.
- Idempotency 판단
  - ISO `_round_test_value`는 `Decimal(str(value)).quantize(Decimal("1"), ROUND_HALF_UP)` 기반이며, 정수 입력에 대해 같은 정수를 돌려준다 (`Decimal(str(6036)).quantize(Decimal("1"), ROUND_HALF_UP) == Decimal("6036")`).
  - 따라서 KS 측에서 capacity/power/declared_capacity를 정수화한 뒤 ISO delegate가 동일 로직을 한 번 더 적용해도 결과는 동일하며, 후속 bin loop / regime selection 등의 입력값은 변하지 않는다.
  - `round_test_values=False` 케이스에서는 KS 측 helper가 원본 dict를 그대로 반환하므로 기존 동작과 동치.

### task 2 결과
- import 추가: `from decimal import Decimal, InvalidOperation, ROUND_HALF_UP` (line 5).
- `_round_test_value(self, value)` 추가: ISO 동명 helper와 동일하게 `int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))`. 한국어 docstring으로 KS 정수 반올림 용도임을 명시.
- `_prepare_measured_inputs(self, measured_inputs)` 추가:
  - `self.config.get("round_test_values", False)`가 false이면 원본 dict 그대로 반환.
  - true이면 새 dict `prepared` 생성. point_data가 dict가 아닌 경우 그대로 보존, dict이면 capacity/power만 `_round_test_value`로 정수화 (예외 시 원값 유지), 그 외 키는 보존.
  - 원본 dict는 mutate하지 않는다.
- 기존 public API (`from_config_path`, `from_iso_calculator`, `calculate_cspf`, `calculate_hspf`, `_ks_cspf_*` 등)는 변경하지 않았다.

### task 3 결과
- `calculate_cspf` 시그니처 (`measured_inputs, declared_capacity=None`) 그대로.
- 진입점 첫 줄에서 `measured_inputs = self._prepare_measured_inputs(measured_inputs)`.
- `declared_capacity is not None and round_test_values is true`이면 `self._round_test_value(declared_capacity)`로 정수화 시도, 예외는 무시하고 원값 유지.
- 이후 분기 그대로:
  - `_iso_calculator_ref`가 있으면 그 인스턴스의 `calculate_cspf(measured_inputs, declared_capacity=...)` 호출.
  - 없으면 lazy import 후 `ISO16358Calculator(self._config_path).calculate_cspf(...)`.
  - `_config_path`도 없으면 기존 `ValueError` 메시지 유지.
- `calculate_hspf`는 일절 손대지 않았다.

### task 4 결과
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py` → 통과.
- KS CSPF spot check: `cspf=6.504`, `annual_cooling_kwh=1943.798`, `annual_power_kwh=298.852` — 기존 기준과 완전 동일.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- 전체 `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline `269 passed, 16 failed, 13 xfailed`와 통계/failure set 완전 동일.
- 16개 failures는 모두 pre-existing ISO HSPF (case 3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundaries) 등으로 본 변경과 무관.

### task 5 결과
- 추가 helper: `KSC9306Calculator._round_test_value`, `KSC9306Calculator._prepare_measured_inputs`.
- `_round_test_value` 구현: `int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))` — ISO와 동일.
- `calculate_cspf` 선전처리 위치: KS `calculate_cspf` 진입점 첫 줄 (measured_inputs) 및 두 번째 블록 (declared_capacity).
- declared_capacity 선정수화: 예 (`round_test_values=True`일 때만).
- ISO delegate 유지 여부: 예 (`_iso_calculator_ref` 또는 lazy-imported `ISO16358Calculator(self._config_path)`로 delegate).
- ISO `ks_intersection` 분기 유지 여부: 예 (`calculator_iso16358.py` 무수정).
- KS HSPF 영향 여부: 없음 (`calculate_hspf` / `_ks_hspf_*` 무수정).
- public API 변화 여부: 없음.
- result schema 변화 여부: 없음 (spot check로 동일 dict 키/값 확인).
- spot check 결과: 통과 (`cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852`).
- 후속 작업 후보 1개: **KS CSPF point resolution을 `KSC9306Calculator`로 분리**. `_resolve_cspf_profile_points` (ISO line 109)는 현재 ISO module에서 climate=T1 / T3 분기로 KS-식 derived point (29_full, 29_half, 29_min, 46_half 등)를 만들어 낸다. 이 책임을 `KSC9306Calculator`에 KS-only entry로 옮기고 ISO delegate에 resolved dict를 넘기는 단계가 다음 가장 작은 안전 단위. behavior-preserving이며 ISO common engine은 그대로 둘 수 있다.

### task 6 결과
- `git status` / `git diff --stat`로 source 변경 범위 = `core/calculator_ks_c9306.py` (46 insertions) 단일 파일로 한정됨을 확인.
- source commit: `refactor: separate KS C9306 measured input prep` (hash `2edf1b2`).
- 본 report 파일을 `result_reports/active/037_separate-ks-c9306-measured-input-prep.md`로 생성.
- report commit: `report: record KS C9306 measured input prep separation` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py` → 통과.
- KS CSPF spot check (`korea.json`, declared_capacity=6000) → `cspf=6.504`, `annual_cooling_kwh=1943.798`, `annual_power_kwh=298.852`.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 동일.

## Changed Files
- `core/calculator_ks_c9306.py`
- `result_reports/active/037_separate-ks-c9306-measured-input-prep.md`

## Known Failures / Risks
- 16개 pre-existing ISO HSPF failures (case3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundary config 등)는 본 변경과 무관하다.
- KS `_round_test_value`는 ISO 동명 helper의 단순 복제로, 둘이 분기 동안 서로 다르게 진화하면 idempotency가 깨질 수 있다. 다음 분리 단계에서 ISO 측에서 KS-flagged round/prepare 호출을 제거하거나, KS 측이 ISO delegate를 거치지 않게 될 때 해당 위험은 해소된다.
- ISO delegate는 그대로 유지되므로 ISO common engine의 동작 변경이 여전히 KS CSPF 결과에 영향을 준다. 이번 단계는 책임만 KS 진입점으로 옮긴 첫 신호이며, full 독립화는 후속 작업에서 단계적으로 진행한다.
- 본 변경은 KS CSPF 경로에 한정되며 KS HSPF, AHRI SEER2/HSPF2, ISO T1 default / India / Hong Kong / SASO CSPF 경로에는 영향이 없다.

## Next Suggested Action
- **KS CSPF point resolution을 `KSC9306Calculator`로 분리**: `_resolve_cspf_profile_points`의 climate=T1/T3 derived point 생성 로직을 KS module에 KS-only entry로 옮기고, KS `calculate_cspf`에서 resolved dict를 만들어 ISO delegate에 넘긴다. ISO common engine은 그대로 두고, KS-side 책임을 한 단계 더 분리하는 가장 작은 다음 안전 단위. behavior-preserving이며 spot check + 전체 baseline 비교로 회귀 없음을 확인할 수 있다.

## Scope Compliance
- KS C 9306 calculator: 수정함 (`core/calculator_ks_c9306.py`).
- ISO16358 calculator: 수정하지 않음 (`core/calculator_iso16358.py` 그대로).
- KS HSPF path: 수정하지 않음 (`calculate_hspf`, `_ks_hspf_*`, `_calculate_ks_c9306_hspf` 그대로).
- profile resolver: 수정하지 않음 (`core/calculator_profiles.py` 그대로).
- dispatcher: 수정하지 않음 (`core/calculator_dispatcher.py` 그대로).
- UI: 수정하지 않음 (`ui/*` 그대로).
- tests: 수정하지 않음.
- fixtures/golden expected: 수정하지 않음.
- docs: 수정하지 않음.
- region config JSON: 수정하지 않음 (`data/region_configs/*.json` 그대로, `korea.json` 포함).
- workbook/reference_files: 수정하지 않음.
- git pull/merge/rebase: 수행하지 않음.

## Commit / Push
- source commit: `2edf1b2 refactor: separate KS C9306 measured input prep`
- report commit: `report: record KS C9306 measured input prep separation`
- pushed branch: `origin/main`
