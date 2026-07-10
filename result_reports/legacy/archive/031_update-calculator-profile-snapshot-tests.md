# 031_update-calculator-profile-snapshot-tests

## Goal
- 보고 030의 KS C 9306 profile 등록 이후 발생한 `tests/test_calculator_profiles.py::test_list_calculator_profiles_returns_enabled_profiles_only` snapshot mismatch 1건을 해소한다. enabled profile snapshot에 `ks_c9306_cspf`, `ks_c9306_hspf`를 포함하도록 갱신하고, KS profile resolver lookup을 검증하는 최소 테스트를 추가한다. calculator code / config는 수정하지 않는다.

## Scope
- `tests/test_calculator_profiles.py`
  - `test_list_calculator_profiles_returns_enabled_profiles_only`의 expected `profile_id` set을 AHRI 2개 + KS 2개 (`ahri_usa_seer2`, `ahri_usa_hspf2`, `ks_c9306_cspf`, `ks_c9306_hspf`)로 갱신. `all(profile.enabled for profile in profiles)` invariant assertion은 그대로 유지.
  - KS resolver lookup guard 테스트 4건 추가.
    - `test_resolve_ks_c9306_cspf_by_profile_id_returns_korea_json`
    - `test_resolve_ks_c9306_hspf_by_profile_id_returns_korea_json`
    - `test_resolve_ks_c9306_cspf_by_selector`
    - `test_resolve_ks_c9306_hspf_by_selector`
  - 각 테스트는 030에서 등록한 profile record의 `profile_id` / `calculator_id` / `config_path` / `metric` / `mode`를 검증하거나 selector 4-tuple로 정확히 한 건만 매치되는지 확인한다.

## Non-goals
- `core/calculator_profiles.py` / `core/calculator_iso16358.py` / `core/calculator_ks_c9306.py` 수정 금지.
- `data/region_configs/*.json` 수정 금지.
- dispatch helper / Calculator UI selector 연결 / `ui/` 수정 금지.
- 계산식 / fixture / golden expected / xfail/pass 수정 금지.
- 기존 AHRI 관련 테스트 본문 수정 금지.
- docs 수정 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업했다.
- `result_reports/{active,archive,summaries}` 전체 report 번호 최대값 030을 확인하고 다음 번호 031을 사용했다.
- commit 전 `git status` / `git diff --stat`로 staged 대상이 `tests/test_calculator_profiles.py` 1개로 한정됨을 확인했다. calculator code / region config JSON / docs / UI는 staged 대상에 포함되지 않았다.
- `python3 -B -m py_compile core/calculator_profiles.py` → 정상 통과.
- `python3 -B -m pytest tests/test_calculator_profiles.py -q` → `14 passed` (기존 10개 + 새 4개; snapshot test 통과).
- `python3 -B -m pytest tests -q -k "profile or resolver or calculator_profiles"` → `32 passed` (이전 27 passed → 32 passed; 추가된 4개 + snapshot 복구 1개).
- 전체: `python3 -B -m pytest tests -q` → `262 passed, 16 failed, 13 xfailed`.
- Baseline 비교: 030 직후 전체 `257 passed, 17 failed, 13 xfailed` → 본 작업 직후 `262 passed, 16 failed, 13 xfailed`. snapshot 실패 1건이 해소되어 baseline (029 직후 main HEAD)의 `258 passed, 16 failed, 13 xfailed`와 동일 failure set으로 복구되었고, KS lookup 테스트 4건이 추가되어 passed 카운트가 +4 증가했다.

## Task Results
### task 1 결과
- `tests/test_calculator_profiles.py`를 읽고 `test_list_calculator_profiles_returns_enabled_profiles_only`의 expected set이 `{"ahri_usa_seer2", "ahri_usa_hspf2"}` 두 개로만 하드코딩되어 있음을 확인했다.
- 030에서 등록한 KS profile `ks_c9306_cspf`, `ks_c9306_hspf` (둘 다 `enabled=True`)가 manifest에 추가되어 있어 enabled set이 4개가 되었지만 테스트의 expected set은 2개로 고정되어 있어 snapshot mismatch가 발생했음을 확인했다.
- `all(profile.enabled for profile in profiles)` invariant 부분은 추가된 profile들도 `enabled=True`이므로 그대로 유지하면 됨을 확인했다.

### task 2 결과
- `test_list_calculator_profiles_returns_enabled_profiles_only`의 expected set에 `ks_c9306_cspf`와 `ks_c9306_hspf`를 추가했다. AHRI 두 profile은 그대로 보존했다.
- enabled invariant assertion `all(profile.enabled for profile in profiles)`는 그대로 유지했다.
- count-only 약화 방식은 사용하지 않았고, 정확한 profile_id set 동등성 검증을 유지했다.

### task 3 결과
- KS resolver lookup guard 4건을 추가했다.
  - `test_resolve_ks_c9306_cspf_by_profile_id_returns_korea_json`: `profile_id`, `calculator_id`, `config_path`, `metric`, `mode` 모두 검증.
  - `test_resolve_ks_c9306_hspf_by_profile_id_returns_korea_json`: 동일하게 HSPF/heating에 대해 검증.
  - `test_resolve_ks_c9306_cspf_by_selector`: `standard="KS_C_9306"`, `region="korea"`, `metric="CSPF"`, `mode="cooling"` selector 일치 검증.
  - `test_resolve_ks_c9306_hspf_by_selector`: HSPF/heating selector 일치 검증.
- 기존 AHRI 테스트 함수와 동일한 style을 따랐다.
- dispatch 실행 / KSC9306Calculator 호출 / 계산 결과 검증은 추가하지 않았다.

### task 4 결과
- `python3 -B -m py_compile core/calculator_profiles.py` → 정상 통과.
- `python3 -B -m pytest tests/test_calculator_profiles.py -q` → `14 passed`.
- `python3 -B -m pytest tests -q -k "profile or resolver or calculator_profiles"` → `32 passed`.
- 전체: `python3 -B -m pytest tests -q` → `262 passed, 16 failed, 13 xfailed`.
- 030 직후 baseline `257 passed, 17 failed, 13 xfailed`와 비교 시 snapshot 실패 1건이 해소되었다. 029 직후 main HEAD baseline `258 passed, 16 failed, 13 xfailed`의 16 failure set과 정확히 동일한 실패 set으로 돌아왔고, KS lookup 테스트 4건이 추가되어 passed 카운트가 +4 증가했다.
- calculator code / region config / fixture / golden expected는 일절 수정하지 않았다.

### task 5 결과
- 갱신한 snapshot expected: `{ahri_usa_seer2, ahri_usa_hspf2, ks_c9306_cspf, ks_c9306_hspf}`.
- 추가한 KS resolver lookup tests: `test_resolve_ks_c9306_cspf_by_profile_id_returns_korea_json`, `test_resolve_ks_c9306_hspf_by_profile_id_returns_korea_json`, `test_resolve_ks_c9306_cspf_by_selector`, `test_resolve_ks_c9306_hspf_by_selector`.
- 기존 AHRI 테스트 영향 여부: 영향 없음 (`test_resolve_ahri_seer2_by_profile_id_returns_usa_json`, `test_resolve_ahri_hspf2_by_profile_id_returns_usa_hspf2_json`, `test_resolve_ahri_seer2_by_selector`, `test_resolve_ahri_hspf2_by_selector`, `test_invalid_ahri_metric_mode_combinations_fail_fast`, `test_ahri_seer2_never_resolves_to_hspf2_config`, `test_ahri_hspf2_never_resolves_to_seer2_config`, `test_resolved_config_paths_exist`이 모두 그대로 통과).
- profile resolver dispatch 구현 여부: 본 작업 범위 밖. resolver는 여전히 순수 manifest/selector 상태이며 dispatch helper는 추가하지 않았다.
- UI 영향 여부: 없음. UI는 수정하지 않았고 KS profile lookup 결과를 사용하는 UI 코드는 본 작업에 포함되지 않는다.
- 전체 테스트 baseline 복구 여부: 16 failed로 복구됨 (029 직후 main HEAD와 동일한 known-failure set).
- 후속 작업 필요 여부:
  - `calculator_id` 기반 thin dispatch helper: profile resolver lookup 결과를 받아 KSC9306Calculator / ISO16358Calculator / AHRI calculator로 라우팅하는 helper 설계.
  - Calculator UI selector 연결: profile_id를 UI에 노출하고 KS profile을 선택할 수 있게 하는 작업.
  - ISO `calculate_cspf` 내부의 `power_interpolation_method == "ks_intersection"` 분기 정리: KS dispatch가 KSC9306Calculator로 완전히 라우팅된 이후에 검토.

### task 6 결과
- `git status` / `git diff --stat`으로 변경 범위가 `tests/test_calculator_profiles.py` 1개 파일로 한정됨을 확인했다.
- test commit: `test: update calculator profile snapshot` (hash `c0f717b`).
- 본 report 파일을 `result_reports/active/031_update-calculator-profile-snapshot-tests.md`로 생성.
- report commit: `report: record calculator profile snapshot update` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m pytest tests/test_calculator_profiles.py -q` → `14 passed` (snapshot test 1 + AHRI lookups 7 + config-path 1 + selector negative 2 + KS lookups 4).
- `python3 -B -m pytest tests -q -k "profile or resolver or calculator_profiles"` → `32 passed`.
- `python3 -B -m pytest tests -q` → `262 passed, 16 failed, 13 xfailed`.
- 030 직후 baseline `257 passed, 17 failed, 13 xfailed`와 대비해 snapshot 실패 1건이 해소되었고 KS lookup 테스트 4건이 추가되어 passed +5, failed -1. 16개 pre-existing known failures는 동일하다.

## Changed Files
- `tests/test_calculator_profiles.py`
- `result_reports/active/031_update-calculator-profile-snapshot-tests.md`

## Known Failures / Risks
- 16개의 기존 pre-existing failures는 본 작업과 무관하다 (ISO common HSPF formula 47/50, pure ISO track A min-to-half, case 3 Excel BM/BO/CD/Y_MIN_Y_EXTD trace, half-to-full / tiny-bin accumulation, formula50 frost branch 등).
- profile manifest snapshot test는 계속 brittle한 형태로 유지되므로, 향후 새 profile (예: ISO/Hong Kong/India/SASO/EN14825) 등록 시 또 한 번 갱신이 필요할 수 있다. 본 작업에서는 정책 변경(예: snapshot을 부분 매치로 약화) 없이 set 동등성 검증을 유지했다.
- 본 작업은 lookup 결과만 검증하며 실제 dispatch/계산 동작은 검증하지 않는다. dispatch wiring은 후속 작업이다.

## Next Suggested Action
- profile resolver lookup 결과를 받아 `calculator_id`에 따라 KSC9306Calculator / ISO16358Calculator / AHRI calculator로 라우팅하는 thin dispatch helper 설계 (별도 작업).

## Scope Compliance
- calculator code: 수정 없음 (`core/calculator_iso16358.py`, `core/calculator_ks_c9306.py` 그대로).
- profile resolver code: 수정 없음 (`core/calculator_profiles.py` 그대로).
- tests: `tests/test_calculator_profiles.py`만 갱신 (snapshot expected + KS lookup 4건).
- fixtures/golden expected: 수정 없음.
- docs: 수정 없음.
- UI: 수정 없음.
- region config JSON: 수정 없음 (`data/region_configs/korea.json` 등 그대로).
- workbook/reference_files: 수정 없음.
- git pull/merge/rebase: 수행하지 않았음.

## Commit / Push
- test commit: `c0f717b test: update calculator profile snapshot`
- report commit: `report: record calculator profile snapshot update`
- pushed branch: `origin/main`
