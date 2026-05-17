# 043_remove-iso-cspf-ks-intersection-residuals

## Goal
- 042 audit가 dead로 분류한 ISO16358Calculator의 KS CSPF 잔여 분기를 제거한다. 구체적으로 `_ks_intersection_power(...)` wrapper와 `_calculate_cspf_profile(...)` / `calculate_cspf(...)` 두 곳에 있던 `power_interpolation_method == "ks_intersection"` 분기를 삭제하고, `iso_boundary_eer` 분기와 capacity-linear fallback은 그대로 유지한다. `KSC9306Calculator` import / `_ks_calculator()` factory / HSPF delegation block은 HSPF 측 의존이 살아 있으므로 유지한다.

## Scope
- `core/calculator_iso16358.py`
  - `_ks_intersection_power(self, tj, L_c_ref, resolved_points, lower_type, upper_type)` 메서드 정의 블록(이전 line 282-298, 약 17줄) 전체 삭제.
  - `_calculate_cspf_profile(...)` 내부 (이전 line 2087-2090) `if self.power_interpolation_method == "ks_intersection": P_tj = self._ks_intersection_power(...)` 분기 삭제. `elif self.power_interpolation_method == "iso_boundary_eer":` → `if self.power_interpolation_method == "iso_boundary_eer":`로 정리. capacity-linear fallback (`if P_tj is None:` 블록)은 그대로.
  - `calculate_cspf(...)` non-profile path (이전 line 2265-2286) `ks_power = None` + `if ks_intersection: ks_power = ...` + `if ks_power is not None: P_tj = ks_power` 분기 삭제. 나머지 `iso_boundary_eer` 처리 / `c2 == c1` / 선형 보간 분기는 그대로 유지.
  - `from core.calculator_ks_c9306 import KSC9306Calculator` (line 7) 유지. `_ks_calculator(self)` factory (line 635-636) 유지. HSPF delegation block (`_ks_hspf_*` wrappers, 24+개) 일절 무수정.
- 다른 모든 파일(`core/calculator_ks_c9306.py`, profile/dispatcher, UI, tests, fixtures, region config, docs, workbook)은 무수정.

## Non-goals
- `core/calculator_ks_c9306.py` 수정 금지 (KS standalone body 그대로, KS module 내 `ks_intersection` 분기 그대로).
- `_iso_boundary_eer_power(...)` / `_iso_boundary_eer(...)` / `_iso_boundary_eer_t3_piecewise(...)` 수정 금지.
- `power_interpolation_method` config attribute 자체 제거 금지 (`iso_boundary_eer` 등 다른 값에 필요).
- ISO HSPF delegation 정리 / `calculate_hspf(...)` / `_ks_hspf_*` wrapper 수정 금지.
- `KSC9306Calculator` import 제거 금지, `_ks_calculator()` factory 제거 금지.
- `data/region_configs/korea.json` 수정 금지, `tests/test_region_config_integrity.py` 수정 금지.
- profile resolver / dispatcher / UI / fixtures / golden expected / tolerance / xfail-pass / docs 수정 금지.
- 새 테스트 추가 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업.
- `result_reports/{active,archive,summaries}` 최대 번호 042 확인 후 다음 번호 043 사용.
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py` → 통과.
- KS CSPF spot check (`KSC9306Calculator.from_config_path("data/region_configs/korea.json").calculate_cspf({35_full: cap=6035.8/pow=1641.4, 35_half: cap=3420.4/pow=679.4, 29_min: cap=1759.6/pow=201.7}, declared_capacity=6000)`) → `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852` (기존 기준값).
- `python3 -B -m pytest tests -q -k "cspf or profile or dispatcher or korea or c9306"` → `100 passed`.
- `python3 -B -m pytest tests/test_iso16358_hspf_ks_oracle.py -q` → `2 passed`. HSPF delegation 회귀 없음.
- 전체 `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 완전 동일, 신규 회귀 0.
- `git diff --stat` source 변경이 `core/calculator_iso16358.py` 1개 파일 (2 insertions, 29 deletions)로 한정됨을 확인.
- grep 검증:
  - `grep -Rn "_ks_intersection_power" core tests ui` → 0건.
  - `grep -n "ks_intersection" core/calculator_iso16358.py` → 0건.
  - `grep -Rn "ks_intersection" core tests ui data/region_configs` → 4건 잔존 (모두 의도된 위치: `core/calculator_ks_c9306.py:57` 주석, `core/calculator_ks_c9306.py:441` KS standalone 분기, `tests/test_region_config_integrity.py:16` allowed set, `data/region_configs/korea.json:12` KS 설정값). ISO 모듈에는 0건.

## Task Results
### task 1 결과
- `core/calculator_iso16358.py` 잔여물 위치 (수정 전):
  - `:7` `from core.calculator_ks_c9306 import KSC9306Calculator` — HSPF delegation 필요. 유지.
  - `:39` `self.power_interpolation_method = self.config.get(...)` — 일반 attribute. 유지.
  - `:282-298` `_ks_intersection_power(...)` wrapper. **CSPF 잔여물 제거 대상**.
  - `:653-654` `_ks_calculator()` factory — HSPF delegation 24+개에서 호출. 유지.
  - `:2037-` `_calculate_cspf_profile(...)` cspf_test_profile 경로.
  - `:2088-2089` `_calculate_cspf_profile` 내부 ks_intersection 분기. **CSPF 잔여물 제거 대상**.
  - `:2148-` `calculate_cspf(...)` non-profile path.
  - `:2266-2271` non-profile path 내부 ks_intersection 분기. **CSPF 잔여물 제거 대상**.
- `_ks_intersection_power(...)` 호출처 grep: 같은 파일 내 `_calculate_cspf_profile`(:2089), `calculate_cspf`(:2267) 두 곳뿐. 외부 호출 0건 (KS module / tests / ui 모두 0). 안전 삭제 가능.
- KSC9306Calculator import / `_ks_calculator()` factory의 HSPF 의존 재확인: `_ks_hspf_*` wrapper 약 24개가 `self._ks_calculator()._ks_hspf_*(...)` 패턴으로 호출. 본 작업에서 보존 필요.

### task 2 결과
- `_ks_intersection_power(...)` 메서드 정의 블록 (이전 line 282-298, docstring 포함 17줄) 전체 삭제. 위치는 `interpolate(...)`와 `_iso_boundary_temperature(...)` 사이.
- `_calculate_cspf_profile(...)` 내부 (이전 line 2087-2090):
  - 변경 전: `P_tj = None` → `if self.power_interpolation_method == "ks_intersection": P_tj = self._ks_intersection_power(...)` → `elif self.power_interpolation_method == "iso_boundary_eer": try: ...`.
  - 변경 후: `P_tj = None` → `if self.power_interpolation_method == "iso_boundary_eer": try: ...`. ks_intersection 분기 2줄 삭제, `elif` → `if`로 정리. capacity-linear fallback (`if P_tj is None:` 블록)은 그대로.
- `calculate_cspf(...)` non-profile path 내부 (이전 line 2265-2286):
  - 변경 전: `ks_power = None` → `if self.power_interpolation_method == "ks_intersection": ks_power = self._ks_intersection_power(...)` → `if ks_power is not None: P_tj = ks_power` → `elif self.power_interpolation_method == "iso_boundary_eer": ...` → `elif c2 == c1:` → `else:`.
  - 변경 후: `ks_power` 변수 자체 제거. `if self.power_interpolation_method == "iso_boundary_eer": ...` → `elif c2 == c1:` → `else:`. 동일 fallback chain 유지. ks_intersection 5줄 + ks_power=None 1줄 + `if ks_power is not None: P_tj = ks_power` 2줄 = 약 8줄 감소.
- KSC9306Calculator import / `_ks_calculator()` factory / HSPF delegation block (line 627-783, line 번호는 삭제 후 기준으로 일부 이동) 모두 무수정.

### task 3 결과
- `grep -Rn "_ks_intersection_power" core tests ui` → 0건.
- `grep -n "ks_intersection" core/calculator_iso16358.py` → 0건.
- `grep -Rn "ks_intersection" core tests ui data/region_configs` 잔존:
  - `core/calculator_ks_c9306.py:57` (KS module 주석에 "power_interpolation_method=ks_intersection" 언급, 의도된 문서화).
  - `core/calculator_ks_c9306.py:441` (KS standalone body의 ks_intersection 분기 — KS-자체 책임, 본 작업 무관).
  - `tests/test_region_config_integrity.py:16` ("ks_intersection"이 valid set에 있음 — korea.json이 여전히 사용하므로 유지 필요).
  - `data/region_configs/korea.json:12` (`"power_interpolation_method": "ks_intersection"` — KS standalone body가 사용).
- ISO 모듈 내 잔존 0건. KS module / config / integrity test의 4건은 모두 의도된 활성 사용처.
- `KSC9306Calculator` import (`:7`) 유지 확인. `_ks_calculator(self)` factory (`:635-636`) 유지 확인. 그 아래 HSPF delegation wrappers(`_has_ks_c9306_hspf_input` 외 다수)도 무수정.

### task 4 결과
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py` → 통과.
- KS CSPF spot check: `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852`. 기존 기준값과 완전 동일.
- `python3 -B -m pytest tests -q -k "cspf or profile or dispatcher or korea or c9306"` → `100 passed`.
- `python3 -B -m pytest tests/test_iso16358_hspf_ks_oracle.py -q` → `2 passed`. HSPF delegation 회귀 없음.
- 전체 `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline `269 passed, 16 failed, 13 xfailed`와 통계/failure set 완전 동일.
- 16 failures는 모두 pre-existing ISO HSPF (case3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundary 등)로 본 변경과 무관.

### task 5 결과
- 삭제한 wrapper: `ISO16358Calculator._ks_intersection_power(...)`.
- 삭제한 CSPF 분기 2곳:
  - `_calculate_cspf_profile(...)` 내부 `if self.power_interpolation_method == "ks_intersection": ...`.
  - `calculate_cspf(...)` non-profile path 내부 `ks_power = None`/`if self.power_interpolation_method == "ks_intersection": ks_power = ...`/`if ks_power is not None: P_tj = ks_power`.
- `KSC9306Calculator` import 보존 여부: 예 (line 7).
- `_ks_calculator()` 보존 여부: 예 (line 635-636).
- HSPF delegation block 보존 여부: 예 (`_has_ks_c9306_hspf_input` 외 24+개 wrapper 무수정).
- `korea.json` / integrity test valid set 보존 여부: 예 (둘 다 무수정).
- KS CSPF spot check 결과: `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852` 통과.
- ISO/Hong Kong/India/SASO CSPF 영향 여부: 없음 (4개 region 모두 `iso_boundary_eer`만 사용. ks_intersection 분기를 트리거한 적 없으므로 결과 동치).
- KS HSPF 영향 여부: 없음 (HSPF delegation block 무수정).
- public API/result schema 변화 여부: 없음 (ISO `calculate_cspf` 시그니처와 반환 dict 동일).
- 후속 작업 후보 1개: **`korea.json`의 `power_interpolation_method` 정책 정리 audit**. 현재 ISO 모듈에서 `ks_intersection`이 사라졌으므로 ISO16358Calculator(korea.json).calculate_cspf(...)가 호출되면 capacity-linear fallback으로 계산된다 (활성 caller는 없음). KS standalone은 여전히 `ks_intersection`을 직접 처리. (1) korea.json의 해당 키를 그대로 둘지, (2) KS-only 의미를 명시하는 새 키(`ks_power_interpolation_method` 등)로 분리할지, (3) ISO 호환 caller가 사라진 상태이므로 그대로 유지해도 무방한지를 audit-only로 정리하는 turn을 다음 단위로 권장. 구현은 그 audit 이후 별도 turn.

### task 6 결과
- `git status` / `git diff --stat`로 source 변경 범위 = `core/calculator_iso16358.py` (2 insertions, 29 deletions) 단일 파일로 한정됨을 확인.
- source commit: `refactor: remove ISO CSPF KS intersection residuals` (hash `6c64ac8`).
- 본 report 파일을 `result_reports/active/043_remove-iso-cspf-ks-intersection-residuals.md`로 생성.
- report commit: `report: record ISO CSPF KS intersection cleanup` (push 직후 hash 확정).
- push: `origin/main`.

## Test Results
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_ks_c9306.py` → 통과.
- KS CSPF spot check (`korea.json`, declared_capacity=6000) → `cspf=6.504, annual_cooling_kwh=1943.798, annual_power_kwh=298.852`.
- `python3 -B -m pytest tests -q -k "cspf or profile or dispatcher or korea or c9306"` → `100 passed`.
- `python3 -B -m pytest tests/test_iso16358_hspf_ks_oracle.py -q` → `2 passed`.
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`. baseline 동일.

## Changed Files
- `core/calculator_iso16358.py`
- `result_reports/active/043_remove-iso-cspf-ks-intersection-residuals.md`

## Known Failures / Risks
- 16개 pre-existing ISO HSPF failures (case3 cycling simulation diagnostics, formula 44/48 pure ISO track A, frost boundary 등)는 본 변경과 무관.
- 외부 ad-hoc 스크립트(노트북, ML 파이프라인 등)가 `ISO16358Calculator("data/region_configs/korea.json").calculate_cspf(...)`를 호출하고 ks_intersection 결과를 기대하고 있었다면, 본 변경 후 capacity-linear fallback 결과로 silent drift 발생. testsuite/UI grep 기준으로는 활성 caller 0건이지만, 외부 사용자에게는 명시적 공지가 권장된다.
- `data/region_configs/korea.json:12`의 `power_interpolation_method="ks_intersection"`은 KS standalone body가 직접 사용하므로 그대로 유지. ISO 모듈에서는 이 키가 더 이상 의미를 가지지 않으므로 정책 일관성 audit이 후속 작업으로 권장.
- `tests/test_region_config_integrity.py:16`의 valid set에 `"ks_intersection"`이 남아 있다. korea.json이 사용 중이라 유지가 옳지만, ISO 모듈에서 해당 분기가 사라진 사실과 의미 불일치가 있을 수 있어 후속 audit에서 명확히 정리하는 것이 안전.
- ISO HSPF delegation block(`_ks_hspf_*` 24+ wrappers, `_ks_calculator()`, `KSC9306Calculator` import)은 본 작업에서 유지된다. HSPF 측 ISO→KS delegation 정리는 별도 audit/구현 사이클이 필요.

## Next Suggested Action
- **`data/region_configs/korea.json`의 `power_interpolation_method` 정책 정리 audit**: 본 cleanup으로 ISO 모듈은 `ks_intersection` 분기를 더 이상 갖지 않으나 korea.json은 여전히 그 값을 명시한다. (1) 그대로 유지 (KS standalone만 의미 보유) (2) KS-only 키(`ks_power_interpolation_method` 등)로 rename (3) ISO 측 의미가 사라졌으므로 일반 키에서 KS-namespaced 키로 이동 — 세 옵션의 영향 범위(KS standalone body, integrity test allowed set, 다른 region config naming 정합성)를 audit-only로 정리하는 별도 turn을 권장. 그 audit 이후 별도 구현 turn에서 정책 적용.

## Scope Compliance
- ISO16358 calculator: 수정함 (`core/calculator_iso16358.py`에서 `_ks_intersection_power` wrapper + CSPF 두 분기 제거).
- KS C 9306 calculator: 수정하지 않음 (`core/calculator_ks_c9306.py` 그대로).
- KS HSPF delegation: 수정하지 않음 (`_ks_hspf_*` wrappers, `_ks_calculator()`, `KSC9306Calculator` import 모두 유지).
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
- source commit: `6c64ac8 refactor: remove ISO CSPF KS intersection residuals`
- report commit: `report: record ISO CSPF KS intersection cleanup`
- pushed branch: `origin/main`
