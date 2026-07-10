# 097 ISO16358-2 HSPF boundary COP alignment

## Goal
ISO16358-2 HSPF common path의 Formula 44/45/47/48/49/50 boundary COP 보간 흐름을 ISO 원문 표현과 명시적으로 정렬하고, focused test로 alignment를 보호한다.

## Scope / Non-goals
- Scope: `_iso_hspf_boundary_cop`, `_iso_hspf_min_half_power_by_formula_44_48`, `_iso_hspf_half_full_power_by_formula_45_49`, `_iso_hspf_formula47_full_extended_non_frost_power`, `_iso_hspf_formula50_full_extended_frost_power`의 주석/변수 정렬, Formula 50 trace에 boundary COP endpoint 노출, boundary helper 추가, focused tests.
- Non-goals: branch/case naming, expected/fixture/xfail 수정, Excel-like table UI, AHRI/EN/UI, adapter/unit conversion, ML, lifecycle maintenance.

## task 1 결과
- 확인 함수: `_iso_hspf_boundary_cop`, `_iso_hspf_intersection_temp`, `_iso_hspf_min_half_power_by_formula_44_48`, `_iso_hspf_half_full_power_by_formula_45_49`, `_iso_hspf_formula47_full_extended_non_frost_power`, `_iso_hspf_formula50_full_extended_frost_power`, `_iso_hspf_extended_frost_intersection_temp`, `_iso_hspf_extended_frost_curve`, `_iso_hspf_calculate_common_branch_power` (Formula 호출 site).
- 원문식 ↔ 구현식 차이:
  - Formula 44/45/47/48/49/50 모두 두 endpoint COP 사이의 1차 선형 보간이다. 원문은 첫 endpoint를 기준으로 표현하고, 구현은 두 번째 endpoint를 기준으로 같은 직선을 표현한다.
  - 대수적으로 동일하다는 점은 다음 항등식으로 확인:  
    `cop_full + (cop_ext - cop_full) * (tj - tg)/(tf - tg)`  
    `= cop_ext + (cop_full - cop_ext) * (tj - tf)/(tg - tf)`
  - 따라서 변수 이름/주석을 원문과 일치시키는 것만으로도 numeric 결과는 변하지 않는다.
- numeric 차이를 만들 수 있는 지점은 보간 방향이 아니라 (a) capacity/power curve resolution, (b) extended frost 기본 endpoint factor (0.734 / 0.877), (c) frost boundary 5.5 ↔ 5 등이며, 본 작업 범위 밖이다.

## task 2 결과
- `core/calculator_iso16358.py`에 `_iso_hspf_boundary_point()` helper 추가.
  - 반환: `{temp, stage, frost, capacity, power, load_at_boundary, cop}`.
  - capacity는 stage capacity curve, power는 stage power curve에서 동일 frost 모드로 계산. `load_at_boundary`는 load line이 boundary 온도에서 갖는 값이고, intersection 정의상 capacity와 동일해야 한다.
- `_iso_hspf_boundary_cop`에 ISO 원문 의미를 설명하는 주석 추가.
- 기존 hspf result / bin_details schema는 그대로 유지. trace에는 Formula 50 한정으로 endpoint COP 두 개 (`cop_ful_f_tg`, `cop_ext_f_tf`) 만 추가 노출.

## task 3 결과
- Formula 44/48 (`_iso_hspf_min_half_power_by_formula_44_48`): ISO 원문 보간식과 algebraic equivalence를 주석에 명시. 계산식 자체는 그대로.
- Formula 45/49 (`_iso_hspf_half_full_power_by_formula_45_49`): 마찬가지로 ISO 원문 보간식과 동일성 주석 추가. 계산식 변경 없음.
- Formula 47 (`_iso_hspf_formula47_full_extended_non_frost_power`): ISO 원문 보간식 주석 정렬. ext_temp 주석을 "extended non-frost stage curve의 load-line intersection 온도"로 명확화. 계산식 변경 없음.
- Formula 50 (`_iso_hspf_formula50_full_extended_frost_power`): ISO 원문 보간식 (cop_ext_f(tf) 기반) 을 주석에 그대로 적고, 구현은 algebraically equivalent한 cop_ful_f(tg) 기반 rewrite임을 명시. 변수 이름을 `cop_full_f_tg` → `cop_ful_f_tg` (`ful` = full, 원문 표기 `COP_ful,f`와 일치) 로 정렬. trace에 `cop_ful_f_tg` / `cop_ext_f_tf` 노출.
- 계산 결과: numeric 값은 모든 micro test / validation / official exact diagnostic에서 변경 없음 (아래 task 5 참고). 즉 ISO 원문 표현 정렬은 rewrite-only.

## task 4 결과
- 신규: `tests/test_iso16358_hspf_boundary_cop_alignment.py`
  - `test_boundary_point_helper_returns_consistent_cop`: `_iso_hspf_boundary_point()`가 `_iso_hspf_boundary_cop()`와 동일한 COP를 돌려주고, intersection에서 capacity ≈ load_at_boundary 임을 확인.
  - `test_formula50_trace_exposes_boundary_cop_endpoints`: tj=0 frost branch에서 tg/tf/cop_fe_f/cop_ful_f_tg/cop_ext_f_tf가 trace에 존재하고, cop_fe_f가 ISO 원문 form (`cop_ext + (cop_full - cop_ext)*(tj-tf)/(tg-tf)`) 와 algebraic equivalence form 양쪽 모두에서 일치함을 검증.
  - `test_formula50_spec_form_matches_implementation_at_problem_bins`: audit에서 P_j gap이 보고된 tj=-1, tj=0 bin에서 구현 cop_fe_f가 ISO 원문 spec form과 일치하고 P_j == bl_h / cop_fe_f 임을 확인 (audit 외부 숫자는 hard-code하지 않음).
  - `test_formula45_half_full_endpoints_match_boundary_helper`: Formula 45 trace의 cop_full/cop_half/cop_hf invariant (cop_hf가 두 endpoint 사이) 및 P_j = bl_h / cop_hf 확인.
  - `test_formula47_full_extended_non_frost_endpoints`: Formula 47 trace key 노출 확인 (해당 branch에 들어가지 않으면 skip).
  - `test_formula44_min_half_non_frost_smoke`: Formula 44 branch P_j > 0 smoke (branch 미진입 시 skip).
- 096 frost trace test (`tests/test_iso16358_hspf_frost_trace.py`) 8 case 그대로 유지/통과.
- HSEC/HSPF expected, official exact xfail list, fixture 모두 변경 없음.

## task 5 결과
- `tests/test_iso16358_hspf_official_exact_golden.py`: 11 xfailed 그대로 (변경 없음).
- 전체 suite 411 passed / 4 skipped / 34 xfailed.
- numeric behavior 변화 없음 (수식 정렬만으로는 P_j 변동 없음). 따라서 case 3/4/12/15/16의 audit-reported mismatch 역시 본 패치로 해소되지 않음 — task 1에서 분석한 대로 boundary 방향이 아니라 capacity/power curve resolution 또는 extended endpoint default 등 별개 원인 후보가 남음.
- xfail / expected 미변경. "모두 맞추기" 시도 없음.

## task 6 결과
- `docs/WORK_PLAN.md` "Repo 다음 순서" 갱신:
  1. ISO table Excel-like behavior patch
  2. ISO result/read-only table copy TSV
  3. unit adapter 확장 (ISO / KS / EN)
  4. ML / inverse-search 복귀 준비
- 097 진행 결과 (boundary COP alignment는 rewrite-only, numeric 변화 없음, mismatch는 별도 원인 추적) 를 짧게 기록.
- result report lifecycle maintenance는 이번 작업 범위가 아니므로 수행하지 않음. 본 작업은 계산 path 정렬에 한정되어 있어 active/archive/summaries 이동을 섞으면 commit scope가 커지고 회귀 위험이 증가하기 때문.

## Verification
- `python3 -B -m py_compile core/calculator_iso16358.py` → OK
- `python3 -B -m pytest tests/test_iso16358_hspf_frost_trace.py -q` → 8 passed
- `python3 -B -m pytest tests/test_iso16358_hspf_formula_micro.py -q` → all pass
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py -q` → all pass
- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` → xfail list unchanged
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → pass
- `python3 -B -m pytest tests/test_iso16358_hspf_boundary_cop_alignment.py -q` → 6 passed, 1 skipped (Formula 47 branch 미진입 시 skip 정책)
- `python3 -B -m pytest -q` → 411 passed, 4 skipped, 34 xfailed

## Known Risks
- Formula 50 등 audit-reported P_j 차이는 boundary 보간 방향과 무관함이 본 작업에서 재확인되었다. 후속 ISO HSPF mismatch 추적은 (a) extended frost 기본 endpoint factor (-7°C 기본값 0.734 / 0.877), (b) 2_full → 2_full_f / 2_half → 2_half_f 매핑 후의 capacity/power 해석, (c) frost upper boundary 5.5 ↔ 5 등 별개 후보를 다뤄야 한다. 본 보고서는 boundary 방향 alignment까지만 다룬다.
- result report lifecycle maintenance pending (active 폴더에 097까지 누적). 별도 정리 작업으로 분리.
