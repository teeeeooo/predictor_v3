# 032_add-calculator-profile-dispatcher

## Goal
- `core/calculator_profiles.py`의 profile resolver 결과(`CalculatorProfile`)를 받아 `calculator_id`에 따라 실제 calculator 인스턴스를 생성하는 thin dispatch helper 모듈을 추가한다. profile resolver schema와 기존 calculator code는 수정하지 않고, Calculator UI 연결 전 단계의 core-level foundation만 마련한다.

## Scope
- `core/calculator_dispatcher.py` (신규)
  - public 함수 `create_calculator_for_profile(profile_id=None, standard=None, region=None, metric=None, mode=None)` 추가.
  - 내부에서 `resolve_calculator_profile(...)` 호출 후 `profile.calculator_id`에 따라 calculator instance를 생성.
  - 지원하는 calculator_id:
    - `ks_c9306` → `KSC9306Calculator.from_config_path(profile.config_path)`
    - `ahri_seer2` → `AHRICalculator(profile.config_path)`
    - `ahri_hspf2` → `AHRIHSPF2Calculator(profile.config_path)`
  - calculator 모듈 import는 lazy하게 함수 내부에서 수행한다 (불필요한 import 부하 방지 및 boundary 유지).
  - unsupported calculator_id는 `ValueError`로 fail-fast.
  - dispatcher는 instance 생성만 담당하고 seasonal 계산을 실행하지 않는다.
- `tests/test_calculator_dispatcher.py` (신규)
  - KS C 9306 CSPF/HSPF profile_id × selector 각 2건 (총 4건)으로 `KSC9306Calculator` 인스턴스 반환을 검증.
  - AHRI SEER2 / HSPF2 profile_id로 각각 `AHRICalculator` / `AHRIHSPF2Calculator` 인스턴스 반환을 smoke 검증.
  - 알 수 없는 profile_id는 `resolve_calculator_profile`의 fail-fast(`ValueError` "match exactly one enabled profile")로 차단됨을 검증.
  - 총 7 테스트.

## Non-goals
- `core/calculator_profiles.py` 수정 금지 (profile schema/registry는 030 상태 유지).
- `core/calculator_iso16358.py`, `core/calculator_ks_c9306.py`, AHRI calculator 모듈 수정 금지.
- `data/region_configs/*.json` 수정 금지.
- 계산식 / fixture / golden expected / xfail/pass 수정 금지.
- 새 계산 로직 / large registry framework / plugin architecture 도입 금지.
- UI 연결 / `ui/` 수정 금지.
- ISO16358 profile manifest 신규 등록 금지 (이번 범위 밖).

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `result_reports/{active,archive,summaries}` 전체 report 번호 최대값 031을 확인하고 다음 번호 032를 사용했다.
- commit 전 `git status` / `git diff --stat`로 변경 범위가 `core/calculator_dispatcher.py`와 `tests/test_calculator_dispatcher.py` 2개로 한정됨을 확인했다. profile resolver, calculator 모듈, region config JSON, docs, UI는 staged 대상에 포함되지 않았다.
- `python3 -B -m py_compile core/calculator_dispatcher.py core/calculator_profiles.py core/calculator_ks_c9306.py core/calculator_ahri_seer2.py core/calculator_ahri_hspf2.py` → compile OK.
- `python3 -B -m pytest tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q` → `21 passed`.
- `python3 -B -m pytest tests -q -k "profile or resolver or calculator_dispatcher or calculator_profiles"` → `39 passed`.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea"` → `48 passed`.
- 전체: `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`.
- Baseline (보고 031 직후 main HEAD) → `262 passed, 16 failed, 13 xfailed`. 본 작업 후 passed가 +7 증가 (새 dispatcher tests 7건) 했고 failure set은 정확히 동일하다. 신규 회귀 없음.

## Task Results
### task 1 결과
- `core/calculator_profiles.py`: schema는 `CalculatorProfile` frozen dataclass + `resolve_calculator_profile` selector function 그대로. 등록된 calculator_id: `ahri_seer2`, `ahri_hspf2`, `ks_c9306`. ISO16358 profile은 현재 manifest에 없음 (이번 작업 범위 밖).
- `core/calculator_ks_c9306.py`: `KSC9306Calculator` 클래스 + `from_config_path(config_path)` factory 존재. CSPF/HSPF public entry (`calculate_cspf`, `calculate_hspf`) 보유.
- `core/calculator_ahri_seer2.py`: `class AHRICalculator` + `__init__(self, config_path: str)`. 본문은 JSON 로드 + 상수 파싱만 수행 (side effect 없음).
- `core/calculator_ahri_hspf2.py`: `class AHRIHSPF2Calculator` + `__init__(self, config_path: str)`. 본문은 `os.path.exists` 가드 + JSON 로드 + 상수 파싱 + `defaults` 보완만 수행 (side effect 없음).
- 결론: 세 calculator_id 모두 안전하게 instance 생성 가능. AHRI도 dispatcher에서 지원하기로 결정했다 (constructor가 명확하고 side effect 없음).

### task 2 결과
- `core/calculator_dispatcher.py`를 새로 생성하고 위 Scope 섹션의 `create_calculator_for_profile(...)` 함수만 노출했다.
- 입력 방식 두 가지 모두 지원: `profile_id` 단일 매치 또는 `standard / region / metric / mode` selector 조합. 입력 검증은 기존 `resolve_calculator_profile`에 위임한다 (fail-fast 보존).
- calculator import는 lazy하게 함수 내부에서 수행해 모듈 로드 부하를 줄이고 dispatcher → calculator 모듈 간 순환 가능성을 차단했다.
- ks_c9306은 `from_config_path` factory를 사용하고, AHRI 두 종류는 기존 `__init__(config_path)` 생성자를 그대로 사용한다.
- unsupported `calculator_id`는 `ValueError`로 fail-fast.
- dispatcher 자체는 계산을 실행하지 않으며 instance 반환만 담당한다.
- `core/calculator_profiles.py`, calculator 모듈, UI, region config는 수정하지 않았다.

### task 3 결과
- `tests/test_calculator_dispatcher.py`를 새로 생성하고 7건 테스트를 추가했다.
  - `test_dispatcher_returns_ks_calculator_for_ks_cspf_profile_id`
  - `test_dispatcher_returns_ks_calculator_for_ks_hspf_profile_id`
  - `test_dispatcher_returns_ks_calculator_for_ks_cspf_selector`
  - `test_dispatcher_returns_ks_calculator_for_ks_hspf_selector`
  - `test_dispatcher_returns_ahri_seer2_calculator_for_ahri_seer2_profile_id`
  - `test_dispatcher_returns_ahri_hspf2_calculator_for_ahri_hspf2_profile_id`
  - `test_dispatcher_fail_fast_on_unknown_profile_id`
- 모든 테스트는 `isinstance(...)` 또는 `pytest.raises(...)`만 검증한다. 계산 실행 / fixture / golden expected 비교는 추가하지 않았다.
- 기존 `tests/test_calculator_profiles.py`는 수정하지 않았다.

### task 4 결과
- `py_compile`: 5개 모듈 모두 정상.
- `pytest tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q`: `21 passed`.
- 키워드 필터 (`profile or resolver or calculator_dispatcher or calculator_profiles`): `39 passed`.
- KS smoke (`ks or c9306 or korea`): `48 passed`.
- 전체: `269 passed, 16 failed, 13 xfailed`. 031 baseline `262 passed, 16 failed, 13 xfailed` 대비 새 dispatcher tests 7건이 추가되어 passed가 +7 증가했고 failure set은 그대로 유지된다. 신규 회귀는 없다.
- calculator code, region config, fixture, golden expected, UI는 일절 수정하지 않았다.

### task 5 결과
- 추가한 dispatcher public 함수: `create_calculator_for_profile(profile_id=None, standard=None, region=None, metric=None, mode=None)`.
- 지원하는 calculator_id: `ks_c9306`, `ahri_seer2`, `ahri_hspf2`.
- unsupported calculator_id 처리: `ValueError("Unsupported calculator_id for dispatcher: ...")` fail-fast.
- KS C 9306 instance 생성 방식: `KSC9306Calculator.from_config_path(profile.config_path)` (027에서 준비된 public factory).
- AHRI dispatch 구현 여부: 구현함. AHRI SEER2와 HSPF2 모두 `__init__(config_path)`이 명확하고 side effect 없는 JSON 로드만 수행하므로 dispatcher 라우팅에 안전하게 포함했다.
- ISO16358 dispatch 미구현/구현 여부: 미구현. ISO16358은 현재 manifest에 profile이 등록되어 있지 않아 selector lookup이 불가능하므로 dispatcher에도 분기를 추가하지 않았다 (이번 작업의 ISO manifest 등록 금지 원칙 준수). ISO16358 manifest 등록은 별도 작업.
- profile resolver schema 변경 여부: 변경 없음.
- UI 영향 여부: 없음. UI는 수정하지 않았고 dispatcher 호출 코드는 아직 어디에도 wiring되지 않았다.
- 계산 실행 여부: 없음. dispatcher는 instance 생성만 한다.
- 후속 작업 필요 여부:
  - Calculator UI selector에서 `create_calculator_for_profile(...)`을 호출해 KS profile 진입점을 노출하는 작업.
  - ISO16358 profile manifest 등록 + dispatcher 분기 추가 (`iso16358` calculator_id) — 별도 작업.
  - ISO `calculate_cspf` 내부의 `power_interpolation_method == "ks_intersection"` 분기 정리는 KS dispatch가 UI/실 사용 경로에서 `KSC9306Calculator`로 완전히 라우팅된 이후 단계.

### task 6 결과
- `git status` / `git diff --stat`으로 변경 범위가 `core/calculator_dispatcher.py`와 `tests/test_calculator_dispatcher.py` 2개로 한정됨을 확인했다.
- `py_compile`과 dispatcher tests 통과 후 source/test commit: `feat: add calculator profile dispatcher` (hash `24df6f6`).
- 본 report 파일을 `result_reports/active/032_add-calculator-profile-dispatcher.md`로 생성.
- report commit: `report: record calculator profile dispatcher` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m pytest tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q` → `21 passed`.
- `python3 -B -m pytest tests -q -k "profile or resolver or calculator_dispatcher or calculator_profiles"` → `39 passed`.
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea"` → `48 passed`.
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`.
- Baseline (보고 031 직후) `262 passed, 16 failed, 13 xfailed` 대비 passed +7, failed/xfailed 동일. 본 작업으로 인한 신규 회귀 없음.

## Changed Files
- `core/calculator_dispatcher.py`
- `tests/test_calculator_dispatcher.py`
- `result_reports/active/032_add-calculator-profile-dispatcher.md`

## Known Failures / Risks
- 16개의 기존 pre-existing failures는 본 변경과 무관하다 (ISO common HSPF formula 47/50, pure ISO track A, case 3 Excel BM/BO/CD/Y_MIN_Y_EXTD trace, half-to-full / tiny-bin accumulation, formula50 frost 등). main HEAD에도 동일하게 존재.
- dispatcher는 호출 시 매번 새로운 calculator instance를 생성한다 (KS는 `from_config_path`로 JSON 재로딩, AHRI는 `__init__`로 JSON 재로딩). 단일 lookup 후 다회 계산이 필요한 호출자는 dispatcher가 반환한 instance를 캐시해서 재사용해야 한다.
- ISO16358 calculator는 manifest에 profile이 없어 dispatcher에서 라우팅되지 않는다. 현재 ISO16358 호출 경로는 여전히 사용자가 `ISO16358Calculator(config_path)`를 직접 호출하는 방식이며, KS calculator의 ISO common engine 위임도 같은 경로를 통해 이루어진다. profile resolver 기반 ISO16358 dispatch가 마련되기 전까지 dispatcher와 직접 instantiation 경로가 공존한다.
- dispatcher 호출 코드가 아직 어디에도 wiring되지 않았으므로 (UI도, 다른 core 모듈도 사용하지 않음) 본 작업의 효과는 향후 wiring 작업으로 이어졌을 때 드러난다.

## Next Suggested Action
- Calculator UI에서 `create_calculator_for_profile(...)`을 호출해 KS / AHRI profile selector를 실제 사용 경로에 연결하는 작업 (별도 result report).
- ISO16358 profile manifest 등록 + dispatcher에 `iso16358` 분기 추가 (별도 작업, ISO16358 region별 profile 설계 필요).

## Scope Compliance
- calculator profile schema: 수정 없음 (`core/calculator_profiles.py` 그대로).
- calculator formula/code: 수정 없음 (`core/calculator_iso16358.py`, `core/calculator_ks_c9306.py`, AHRI 모듈 그대로).
- dispatcher: `core/calculator_dispatcher.py` 신규 생성.
- tests: `tests/test_calculator_dispatcher.py` 신규 생성. 기존 테스트 수정 없음.
- fixtures/golden expected: 수정 없음.
- docs: 수정 없음.
- UI: 수정 없음.
- region config JSON: 수정 없음 (`data/region_configs/*.json` 그대로).
- workbook/reference_files: 수정 없음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- source/test commit: `24df6f6 feat: add calculator profile dispatcher`
- report commit: `report: record calculator profile dispatcher`
- pushed branch: `origin/main`
