# 030_register-ks-c9306-profiles

## Goal
- `core/calculator_profiles.py`에 KS C 9306 CSPF/HSPF profile record 두 개를 등록하여 기존 `resolve_calculator_profile(...)` API로 `calculator_id=ks_c9306` profile을 lookup할 수 있게 만든다. UI/dispatch 연결은 본 작업 범위 밖이다.

## Scope
- `core/calculator_profiles.py`
  - `_CALCULATOR_PROFILES` 튜플 끝에 두 record 추가.
    - `ks_c9306_cspf`: standard=`KS_C_9306`, region=`korea`, metric=`CSPF`, mode=`cooling`, calculator_id=`ks_c9306`, config_path=`data/region_configs/korea.json`, enabled=`True`.
    - `ks_c9306_hspf`: standard=`KS_C_9306`, region=`korea`, metric=`HSPF`, mode=`heating`, calculator_id=`ks_c9306`, config_path=`data/region_configs/korea.json`, enabled=`True`.
  - 기존 dataclass `CalculatorProfile`, `_same`, `list_calculator_profiles`, `resolve_calculator_profile` 본문은 수정하지 않았다.

## Non-goals
- `core/calculator_iso16358.py` 수정 금지.
- `core/calculator_ks_c9306.py` 수정 금지.
- `data/region_configs/*.json` 수정 금지.
- 신규 dispatch helper / Calculator UI selector 연결 / `ui/` 수정 금지.
- tests / fixture / xfail / golden / docs 수정 금지.
- 새 테스트 추가 금지.
- ISO `calculate_cspf` 내부 KS-aware 분기 정리 금지 (별도 작업).

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `python3 -B -m py_compile core/calculator_profiles.py core/calculator_ks_c9306.py` → compile OK.
- Resolver lookup spot check:
  - `resolve_calculator_profile(profile_id="ks_c9306_cspf")` → `profile_id="ks_c9306_cspf"`, `calculator_id="ks_c9306"`, `config_path="data/region_configs/korea.json"`, `enabled=True`.
  - `resolve_calculator_profile(profile_id="ks_c9306_hspf")` → `profile_id="ks_c9306_hspf"`, `calculator_id="ks_c9306"`, `config_path="data/region_configs/korea.json"`, `enabled=True`.
  - `resolve_calculator_profile(standard="KS_C_9306", region="korea", metric="HSPF", mode="heating")` → `profile_id="ks_c9306_hspf"` (selector-based 일치 1건).
  - `list_calculator_profiles(enabled_only=True)` 길이 = 4 (AHRI 2 + KS 2).
- 기존 AHRI/ISO/ASNZS 식별 동작 변화 없음 (기존 lookup 4개 테스트 통과: `test_resolve_ahri_seer2_by_profile_id_returns_usa_json`, `test_resolve_ahri_hspf2_by_profile_id_returns_usa_hspf2_json`, `test_resolve_ahri_seer2_by_selector`, `test_resolve_ahri_hspf2_by_selector`).
- `test_resolved_config_paths_exist` 통과: `data/region_configs/korea.json` 파일 존재.

## Task Results
### task 1 결과
- `core/calculator_profiles.py` 전체 87 lines를 확인했다. schema는 `@dataclass(frozen=True) class CalculatorProfile` 하나로 모든 profile을 표현하며 필드는 `profile_id`, `standard`, `region`, `metric`, `mode`, `calculator_id`, `config_path`, `enabled`(default `True`)이다.
- 현재 등록된 profile은 AHRI 두 개뿐 (`ahri_usa_seer2`, `ahri_usa_hspf2`). ISO/Hong Kong/India/SASO는 manifest에 아직 등록되어 있지 않다.
- resolver API:
  - `list_calculator_profiles(enabled_only=True)` — enabled profile만 반환.
  - `resolve_calculator_profile(profile_id=..., standard=..., region=..., metric=..., mode=...)` — profile_id 단일 매치 또는 standard+region+metric+mode 조합으로 정확히 1건 매치를 요구하고 그 외에는 `ValueError` fail-fast.
- profile manifest는 dispatch logic을 포함하지 않는 순수 selector이다. 따라서 dispatch map 변경은 필요 없고, KS profile record를 manifest에 추가하기만 하면 lookup이 가능하다.
- `calculator_id=ks_c9306` 등록은 기존 schema 안에서 side effect 없이 가능하다고 판단했다.

### task 2 결과
- `_CALCULATOR_PROFILES` 튜플 끝에 위 Scope 섹션의 두 record를 추가했다. 기존 두 AHRI record는 그대로 보존했다.
- 표준 이름은 AHRI naming pattern (`AHRI_210_240`)을 따라 `KS_C_9306`으로 통일했다.
- `enabled=True`로 설정한 이유: AHRI 두 profile이 모두 `enabled=True`이고, KS C 9306 calculator는 보고 025/026/027에서 `KSC9306Calculator.calculate_cspf(...)` 및 `.calculate_hspf(...)` public entry가 마련된 상태이므로 "구현이 끝났으면 enabled=True"라는 AHRI 정책과 일치한다. AS/NZS Excel compatibility처럼 미구현 상태에서 `enabled=False`로 두는 경우와는 다르다.
- config JSON, UI, calculator code 모듈은 수정하지 않았다.

### task 3 결과
- 위 Verification 섹션의 resolver lookup spot check가 두 profile 모두에서 성공함을 확인했다.
- profile 매니페스트는 dispatch map을 포함하지 않는 순수 selector이므로 추가 dispatch 코드 작성은 필요하지 않았고 작성하지도 않았다.
- 신규 large dispatcher / UI 연결 / `core/calculator_iso16358.py` 수정은 수행하지 않았다.

### task 4 결과
- `python3 -B -m py_compile core/calculator_profiles.py` → 정상 통과.
- `python3 -B -m py_compile core/calculator_ks_c9306.py` → 정상 통과.
- profile/resolver 테스트: `python3 -B -m pytest tests -q -k "profile or resolver or calculator_profiles"` → `27 passed, 1 failed`. 실패 1건은 `tests/test_calculator_profiles.py::test_list_calculator_profiles_returns_enabled_profiles_only`로, 본 등록으로 인한 snapshot mismatch이다 (아래 Known Failures 참조).
- KS smoke: `python3 -B -m pytest tests -q -k "ks or c9306 or korea"` → `40 passed`. 기존 KS 동작 회귀 없음.
- 전체: `python3 -B -m pytest tests -q` → `257 passed, 17 failed, 13 xfailed`.
- Baseline (보고 029 직후 main HEAD) → `258 passed, 16 failed, 13 xfailed`.
- 차이: +1 failed, –1 passed. 추가된 실패 1건은 `test_list_calculator_profiles_returns_enabled_profiles_only` 한 개. 나머지 16 failures는 모두 pre-existing known failures와 동일 set이다. 본 작업으로 인해 새로 발생한 회귀는 snapshot 테스트 한 건뿐이며 ISO/AHRI/KS 계산 동작 회귀는 없다.
- 테스트, fixture, expected, tolerance, xfail/pass, 새 테스트 추가는 일절 수행하지 않았다.

### task 5 결과
- 추가한 KS profile_id: `ks_c9306_cspf`, `ks_c9306_hspf`.
- 각 profile의 `calculator_id`: 둘 다 `ks_c9306`.
- 각 profile의 `config_path`: 둘 다 `data/region_configs/korea.json`.
- `enabled` 설정값: 둘 다 `True`. 이유: AHRI 정책 일치 + KSC9306Calculator의 CSPF/HSPF public entry가 이미 구현되어 있어 lookup 가능 상태로 노출하는 것이 적절. AS/NZS compat과 달리 구현 대기 상태가 아님.
- resolver lookup 가능 여부: `profile_id` 및 `standard+region+metric+mode` 두 경로 모두 lookup 성공함을 spot check로 확인.
- dispatch map 변경 여부: 현재 manifest는 dispatch map을 포함하지 않으므로 변경 없음.
- 기존 ISO/AHRI profile 영향 여부: AHRI selector/profile_id lookup 동작 그대로. ISO 관련 manifest entry는 원래 없었으므로 영향 없음.
- UI 영향 여부: UI는 수정하지 않았고, 현재 UI가 `core/calculator_profiles.py` resolver를 통해 KS profile을 사용하지도 않는다. UI 연결은 후속 작업.
- 후속 작업 필요 여부:
  - `tests/test_calculator_profiles.py::test_list_calculator_profiles_returns_enabled_profiles_only`의 hard-coded snapshot set을 manifest 추가에 맞춰 갱신하는 testing-task가 별도로 필요하다 (이번 작업 범위 밖).
  - dispatch helper / 호출 라우팅: profile resolver로 받은 `calculator_id`/`config_path`를 KSC9306Calculator나 ISO16358Calculator로 라우팅하는 helper. 본 작업은 manifest registration만 다룬다.
  - Calculator UI selector / dropdown 연결: profile_id를 UI에 노출하고 KS profile을 선택할 수 있게 하는 작업.
  - ISO `calculate_cspf` 내부의 `power_interpolation_method == "ks_intersection"` 분기 정리: KS dispatch가 KSC9306Calculator로 완전히 라우팅된 이후에 검토.

### task 6 결과
- `git status` / `git diff --stat`으로 변경 범위가 `core/calculator_profiles.py` 1개 파일로 한정됨을 확인했다.
- `py_compile` 통과 후 source commit: `feat: register KS C9306 calculator profiles` (hash `ab7197b`).
- 본 report 파일을 `result_reports/active/030_register-ks-c9306-profiles.md`로 생성.
- report commit: `report: record KS C9306 profile registration` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m pytest tests -q -k "profile or resolver or calculator_profiles"` → `27 passed, 1 failed`. 실패: `test_list_calculator_profiles_returns_enabled_profiles_only` (snapshot mismatch).
- `python3 -B -m pytest tests -q -k "ks or c9306 or korea"` → `40 passed`.
- `python3 -B -m pytest tests -q` → `257 passed, 17 failed, 13 xfailed`.
- Baseline (보고 029 직후) → `258 passed, 16 failed, 13 xfailed`. 본 작업으로 인한 추가 실패는 1건 (snapshot test)이며 ISO/AHRI/KS 계산 동작에는 회귀가 없다.
- AHRI profile lookup 테스트 4건 (`test_resolve_ahri_seer2_by_profile_id_returns_usa_json`, `test_resolve_ahri_hspf2_by_profile_id_returns_usa_hspf2_json`, `test_resolve_ahri_seer2_by_selector`, `test_resolve_ahri_hspf2_by_selector`) 모두 통과 유지.
- `test_resolved_config_paths_exist` 통과 (`data/region_configs/korea.json` 존재 확인).

## Changed Files
- `core/calculator_profiles.py`
- `result_reports/active/030_register-ks-c9306-profiles.md`

## Known Failures / Risks
- `tests/test_calculator_profiles.py::test_list_calculator_profiles_returns_enabled_profiles_only`: 본 작업 결과로 1건 새로 실패. 테스트 본문은 enabled set이 정확히 `{ahri_usa_seer2, ahri_usa_hspf2}`라고 하드코딩되어 있어, 어떤 새 enabled profile이 추가되어도 깨지는 brittle snapshot이다. 본 작업의 task 지시는 “tests 수정 금지 / expected 수정 금지 / 실패는 등록 원인인지 known인지 분류” 이므로 테스트는 수정하지 않았다. 분류: 본 등록 작업이 의도적으로 만든 snapshot mismatch이며 KS profile 등록이 정상적으로 일어났다는 직접 증거다. follow-up testing-task에서 snapshot을 manifest와 동기화해야 한다.
- 16개의 기존 pre-existing failures는 본 변경과 무관하며 main HEAD에도 동일하게 존재한다 (ISO common HSPF formula 47/50, pure ISO track A, case 3 Excel trace 등).
- profile manifest에 KS가 등록되었지만 실제 호출 경로는 여전히 사용자가 `ISO16358Calculator("data/region_configs/korea.json").calculate_*` 또는 `KSC9306Calculator.from_config_path("data/region_configs/korea.json").calculate_*`를 명시적으로 호출하는 방식이다. profile resolver → calculator dispatch 라우팅이 wiring되기 전까지 manifest와 실제 dispatch가 일시적으로 분리된 상태로 존재한다.

## Next Suggested Action
- `tests/test_calculator_profiles.py::test_list_calculator_profiles_returns_enabled_profiles_only`의 snapshot을 KS profile 두 개 포함으로 갱신하는 testing-task (별도 result report).
- 그 후 profile resolver lookup 결과를 받아 `calculator_id`별로 KSC9306Calculator / ISO16358Calculator / AHRI calculator로 라우팅하는 thin dispatch helper 설계 작업.

## Scope Compliance
- ISO16358 calculator: 수정 없음.
- KS C 9306 calculator: 수정 없음 (`core/calculator_ks_c9306.py` 그대로).
- AS/NZS compatibility: 구현하지 않았음.
- tests/fixtures/expected: 수정하지 않았음.
- docs: 수정하지 않았음.
- UI: 수정하지 않았음.
- region config JSON: 수정하지 않았음 (`data/region_configs/korea.json` 등 그대로).
- workbook/reference_files: 수정하지 않았음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- source commit: `ab7197b feat: register KS C9306 calculator profiles`
- report commit: `report: record KS C9306 profile registration`
- pushed branch: `origin/main`
