# 041_cleanup-ks-c9306-cspf-legacy-iso-delegate

## Goal
- 040 audit가 분류한 두 가지 KS CSPF legacy 항목을 한 번에 정리한다.
  1. `KSC9306Calculator._calculate_cspf_via_iso_delegate(...)` dead method 정의 블록 삭제 (Removal Candidate A).
  2. `test_korea_cspf_regression_unchanged_by_diagnostics`의 calculator caller를 `ISO16358Calculator("data/region_configs/korea.json")` 직접 호출에서 `KSC9306Calculator.from_config_path("data/region_configs/korea.json")` standalone 경로로 전환 (Removal Candidate C).
- 이번 작업은 `core/calculator_iso16358.py`를 일절 수정하지 않는다. ISO 측 `ks_intersection` 분기 / `_ks_intersection_power` wrapper / KS HSPF delegation block 모두 그대로 유지하며, 다음 audit/구현 사이클의 선행 조건만 정돈한다.

## Scope
- `core/calculator_ks_c9306.py`
  - `KSC9306Calculator._calculate_cspf_via_iso_delegate(...)` method 정의 블록 (이전 line 493-525, 34 lines) 전체 삭제.
  - `calculate_cspf(...)`, `_calculate_ks_c9306_cspf(...)`, `_resolve_ks_cspf_points(...)`, `_interpolate_ks_cspf(...)`, `_ks_cspf_intersection_power(...)`, `_ks_cspf_performance_line(...)`, KS HSPF 관련 method 모두 무수정.
- `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py`
  - top-level import에 `from core.calculator_ks_c9306 import KSC9306Calculator` 한 줄 추가.
  - `test_korea_cspf_regression_unchanged_by_diagnostics` → `test_korea_cspf_regression_matches_ks_c9306_calculator`로 rename. 호출 calculator만 `KSC9306Calculator.from_config_path(...)`로 교체. 입력 dict, declared_capacity, expected assert (`cspf=6.504`, `annual_cooling_kwh=1943.798`, `annual_power_kwh=298.852`) 동일.
  - 동일 파일 내 다른 테스트(`ISO16358Calculator` 직접 사용 포함) 무수정.

## Non-goals
- `core/calculator_iso16358.py` 수정 금지 (ISO `calculate_cspf`, `_ks_intersection_power` wrapper, `_ks_calculator` 팩토리, `KSC9306Calculator` import, KS HSPF delegation block 모두 유지).
- ISO `ks_intersection` 분기 / `_iso_boundary_eer_power` 수정 금지.
- KS CSPF standalone body (`_calculate_ks_c9306_cspf`)와 보조 helper 수정 금지.
- KS HSPF body 수정 금지.
- profile resolver / dispatcher / UI / region config JSON / docs / fixtures / golden expected / tolerance / xfail/pass 수정 금지.
- 새 테스트 추가 금지. ISO direct path와의 비교 테스트 추가 금지.
- 다른 테스트의 caller 전환 금지 (`test_iso16358_hspf_ks_oracle.py`, `test_iso16358_hspf_golden.py` 등 HSPF 측 ISO16358Calculator(korea.json) 호출은 그대로 유지).

## Verification
- `git branch --show-current` → `main`.
- `result_reports/{active,archive,summaries}` 최대 번호 040 확인 후 다음 번호 041 사용.
- `grep -Rn "_calculate_cspf_via_iso_delegate" core tests ui` 삭제 전: KS module 자기 정의 + 자기 ValueError 메시지 2건. 삭제 후: 0건.
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py tests/test_iso16358_cspf_iso_t1_default_diagnostics.py` → 통과.
- `python3 -B -m pytest tests/test_iso16358_cspf_iso_t1_default_diagnostics.py -q -k "korea_cspf"` → `1 passed`. rename된 테스트가 KS standalone 경로로 동일 expected 값을 통과.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed` (test count 변화 없음 — rename은 같은 1개 테스트로 count됨).
- 전체 `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 통계 / failure set 완전 동일. 회귀 없음.
- `git diff --stat`: `core/calculator_ks_c9306.py` (-34), `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py` (+2/-1) 2개 파일로 한정. ISO/profile/dispatcher/UI/region config/docs 무변경.

## Task Results
### task 1 결과
- `grep -Rn "_calculate_cspf_via_iso_delegate" core tests ui` 결과 (수정 전):
  - `core/calculator_ks_c9306.py:493` (method 정의)
  - `core/calculator_ks_c9306.py:521` (자체 ValueError 메시지 문자열)
  - 외부 호출처 0건.
- `grep -Rn "korea.json\|test_korea_cspf_regression_unchanged_by_diagnostics" tests/test_iso16358_cspf_iso_t1_default_diagnostics.py` 결과:
  - `:168 def test_korea_cspf_regression_unchanged_by_diagnostics():`
  - `:169     calculator = ISO16358Calculator("data/region_configs/korea.json")`
  - 활성 ISO direct caller임을 재확인.
- `KSC9306Calculator.calculate_cspf` (line 527-528): 단 한 줄 `_calculate_ks_c9306_cspf(...)` 호출. ISO delegate 의존 없음.
- `_calculate_ks_c9306_cspf` (line 320~) 본문도 KS 내부 helper만 사용 (`_prepare_measured_inputs`, `_round_test_value`, `_resolve_ks_cspf_points`, `_interpolate_ks_cspf`, `_ks_cspf_intersection_power`).
- 결론: dead delegate 안전 삭제 가능, ISO direct test caller가 ks_intersection 분기를 잡고 있는 유일한 활성 경로.

### task 2 결과
- `KSC9306Calculator._calculate_cspf_via_iso_delegate(...)` method 정의 블록 (34 lines, 전체 docstring 포함) 삭제.
- 동일 위치의 lazy import `from core.calculator_iso16358 import ISO16358Calculator`는 이 helper 안에서만 사용되었으므로 함께 사라짐 (블록 단위 삭제). KS module에는 top-level ISO import이 없으며, 다른 lazy import도 추가하지 않음.
- `calculate_cspf(...)` (이전 line 527-528, 삭제 후도 동일 동작): 변경 없음. `_calculate_ks_c9306_cspf(measured_inputs, declared_capacity)` 호출 그대로.
- `_calculate_ks_c9306_cspf`, `_resolve_ks_cspf_points`, `_interpolate_ks_cspf`, `_ks_cspf_intersection_power`, `_ks_cspf_performance_line`, KS HSPF block 모두 그대로.
- public API 변경 없음 (private method 삭제이며 호출처 0건).

### task 3 결과
- import 추가: `from core.calculator_ks_c9306 import KSC9306Calculator` 한 줄. 기존 `from core.calculator_iso16358 import ISO16358Calculator` import는 동일 파일 내 다른 테스트(예: `test_e_derived_nearest_integer_manual_rounding_changes_metrics`)가 여전히 ISO16358Calculator를 사용하므로 유지.
- test rename: `test_korea_cspf_regression_unchanged_by_diagnostics` → `test_korea_cspf_regression_matches_ks_c9306_calculator`. 의도가 “ISO direct path 유지”에서 “KS C 9306 standalone CSPF 결과 유지”로 명확화됨.
- caller 교체: `calculator = ISO16358Calculator("data/region_configs/korea.json")` → `calculator = KSC9306Calculator.from_config_path("data/region_configs/korea.json")`.
- 입력 dict (`35_full / 35_half / 29_min`), `declared_capacity=6000`, expected assert 3건 (`6.504 / 1943.798 / 298.852`) 모두 그대로.
- 다른 테스트 / fixture / golden expected / tolerance / xfail/pass / 다른 ISO16358Calculator(korea.json) 호출 (`tests/test_iso16358_hspf_ks_oracle.py`, `tests/test_iso16358_hspf_golden.py`) 무수정.

### task 4 결과
- `grep -Rn "_calculate_cspf_via_iso_delegate" core tests ui` 삭제 후: 0건.
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py tests/test_iso16358_cspf_iso_t1_default_diagnostics.py` → 통과.
- `python3 -B -m pytest tests/test_iso16358_cspf_iso_t1_default_diagnostics.py -q -k "korea_cspf"` → `1 passed, 2 deselected`. 전환된 단일 테스트가 KS standalone 경로로 통과.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`. count 변화 없음 (rename은 같은 1개 테스트로 잡힘).
- 전체 `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline `269 passed, 16 failed, 13 xfailed`와 통계 / failure set 완전 동일. 신규 회귀 없음.
- 16개 pre-existing failures는 ISO HSPF (case3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundary 등)로 본 변경과 무관.

### task 5 결과
- 삭제한 method: `KSC9306Calculator._calculate_cspf_via_iso_delegate`.
- 삭제 전 호출처 확인 결과: KS module 내부 자기 정의 + 자기 ValueError 메시지 2건 외 0건.
- 삭제 후 grep 결과: 0건.
- 전환한 test 이름: `test_korea_cspf_regression_unchanged_by_diagnostics` → `test_korea_cspf_regression_matches_ks_c9306_calculator`.
- test caller 변경 전: `ISO16358Calculator("data/region_configs/korea.json").calculate_cspf(...)`.
- test caller 변경 후: `KSC9306Calculator.from_config_path("data/region_configs/korea.json").calculate_cspf(...)`.
- expected 값 유지 여부: 예 (`cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852`).
- `calculate_cspf` main path 유지 여부: 예 (`_calculate_ks_c9306_cspf(...)` 단일 호출).
- KS CSPF spot/regression 결과: 통과.
- KS HSPF 영향 여부: 없음 (KS HSPF body / `_ks_hspf_*` 전부 무수정, 관련 테스트도 무수정).
- ISO calculator 영향 여부: 없음 (`core/calculator_iso16358.py` 무수정. ISO direct path는 여전히 동일 분기/helper로 동작 가능하지만, 활성 caller가 사라져 dead branch 가까운 상태로 한 단계 진입).
- public API / result schema 변화 여부: 없음 (`{cspf, annual_cooling_kwh, annual_power_kwh, bin_details}` 그대로).
- 후속 작업 후보 1개: **ISO `calculate_cspf` 안의 `ks_intersection` 분기 및 `_ks_intersection_power` wrapper 제거 audit-only turn**. ks_intersection 활성 caller가 본 cleanup으로 사라졌으므로, (1) ISO `calculate_cspf` non-profile path의 `ks_intersection` 분기, (2) `_calculate_cspf_profile` 안의 `ks_intersection` 분기, (3) `_ks_intersection_power` wrapper, (4) `tests/test_region_config_integrity.py`의 valid value set 영향, (5) HSPF delegation block과의 import 공유 여부를 정확히 확인한 뒤 별도 구현 turn으로 분리.

### task 6 결과
- `git status` / `git diff --stat`로 source/test 변경 범위 = `core/calculator_ks_c9306.py` (-34) + `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py` (+2/-1) 2개 파일로 한정됨을 확인.
- source/test commit: `refactor: clean up KS C9306 CSPF legacy ISO delegate` (hash `7fccedc`).
- 본 report 파일을 `result_reports/active/041_cleanup-ks-c9306-cspf-legacy-iso-delegate.md`로 생성.
- report commit: `report: record KS C9306 CSPF legacy cleanup` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `grep -Rn "_calculate_cspf_via_iso_delegate" core tests ui` → 0건 (삭제 후).
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358.py tests/test_iso16358_cspf_iso_t1_default_diagnostics.py` → 통과.
- `python3 -B -m pytest tests/test_iso16358_cspf_iso_t1_default_diagnostics.py -q -k "korea_cspf"` → `1 passed, 2 deselected`.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea or cspf or profile or dispatcher"` → `104 passed`.
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 동일.

## Changed Files
- `core/calculator_ks_c9306.py`
- `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py`
- `result_reports/active/041_cleanup-ks-c9306-cspf-legacy-iso-delegate.md`

## Known Failures / Risks
- 16개 pre-existing ISO HSPF failures (case3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundary 등)는 본 변경과 무관.
- 본 cleanup은 ISO `calculate_cspf`의 `ks_intersection` 분기를 제거하지 않았다. ISO direct path를 호출하는 외부 스크립트가 있다면(예: 사용자가 ad-hoc하게 `ISO16358Calculator("korea.json").calculate_cspf(...)`를 호출) 여전히 동일 결과를 돌려준다. 활성 caller가 사라졌을 뿐 분기 자체는 그대로.
- HSPF 측 ISO16358Calculator(korea.json) 직접 호출(`test_iso16358_hspf_ks_oracle.py`, `test_iso16358_hspf_golden.py`)은 그대로 유지된다. 이는 ISO→KS HSPF delegation block과 함께 별도 audit/구현 사이클에서 다뤄야 한다.
- `_calculate_cspf_via_iso_delegate`가 외부에서 reflection / dynamic dispatch로 호출되지 않는다는 가정은 read-only grep 기반이다. 외부 스크립트가 그런 호출을 하고 있었다면 ImportError가 아니라 AttributeError로 깨질 것. 본 작업에서는 신뢰성 있는 외부 사용 흔적을 grep으로 찾지 못했다.
- rename된 test name이 외부 reference(`pytest --collect-only` 출력, 문서 등)에 박혀 있을 가능성. 본 audit/구현 범위 밖이며, 문서 수정 금지 정책에 따라 동기화는 별도 작업으로 분리.

## Next Suggested Action
- **ISO `calculate_cspf` 안의 `ks_intersection` 분기 및 `_ks_intersection_power` wrapper 제거 audit**: 본 cleanup으로 ks_intersection 활성 caller가 사라졌으므로, ISO 측에서 `power_interpolation_method=="ks_intersection"` 분기(non-profile path 1군데 + cspf_test_profile path 1군데), `_ks_intersection_power` wrapper, 관련 KSC9306Calculator import 공유 여부, `tests/test_region_config_integrity.py`의 valid set 정책 영향까지 grep으로 정리하는 audit-only turn을 다음 단위로 진행. 구현은 그 audit 이후 별도 turn에서 분리 수행.

## Scope Compliance
- KS C 9306 calculator: 수정함 (`_calculate_cspf_via_iso_delegate` method 정의 블록 삭제).
- ISO16358 calculator: 수정하지 않음 (`core/calculator_iso16358.py` 그대로).
- KS CSPF tests: 수정함 (`tests/test_iso16358_cspf_iso_t1_default_diagnostics.py`의 단일 테스트 caller/이름만 전환, expected/입력 동일).
- KS HSPF path: 수정하지 않음 (`calculate_hspf`, `_ks_hspf_*`, `_calculate_ks_c9306_hspf` 그대로). HSPF 측 ISO direct test 무수정.
- profile resolver: 수정하지 않음 (`core/calculator_profiles.py` 그대로).
- dispatcher: 수정하지 않음 (`core/calculator_dispatcher.py` 그대로).
- UI: 수정하지 않음 (`ui/*` 그대로).
- fixtures/golden expected: 수정하지 않음.
- docs: 수정하지 않음.
- region config JSON: 수정하지 않음 (`data/region_configs/*.json` 그대로, `korea.json` 포함).
- workbook/reference_files: 수정하지 않음.
- git pull/merge/rebase: 수행하지 않음.

## Commit / Push
- source/test commit: `7fccedc refactor: clean up KS C9306 CSPF legacy ISO delegate`
- report commit: `report: record KS C9306 CSPF legacy cleanup`
- pushed branch: `origin/main`
