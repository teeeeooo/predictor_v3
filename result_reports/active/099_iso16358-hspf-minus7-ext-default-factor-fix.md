# 099 ISO16358-2 HSPF -7_ext default factor fix

## Goal
ISO 16358-2 HSPF common path의 `_iso_hspf_extended_minus7_default()`가 `-7_ext` measured 부재 시 적용하는 default factor를 원문 audit 결과에 맞게 정정한다. 0.734 (capacity) / 0.877 (power)는 2°C **non-frost** → -7°C 변환 factor이므로 2°C **frost** measured (`2_ext`)에 직접 곱하면 안 된다. 2-step (frost → non-frost → -7°C) 으로 수정한다.

## Scope / Non-goals
- Scope: `core/calculator_iso16358.py::_iso_hspf_extended_minus7_default()` 본체. helper-level focused test 추가.
- Non-goals: official exact expected / fixture / xfail 수정, Formula 44/45/47/48/49/50 식 수정, branch selection / case naming 변경, ISO table UI, AHRI/EN/UI, adapter/unit conversion, ML, result_reports lifecycle maintenance.

## task 1 결과
- 수정 파일: `core/calculator_iso16358.py`
- `-7_ext` measured가 있으면 measured 값을 그대로 반환 (기존 동작 유지).
- `-7_ext` measured가 없는 경우, 2-step 변환을 적용:
  - `ext_2_nonfrost_capacity = ext_2_frost.capacity * 1.12`
  - `ext_2_nonfrost_power = ext_2_frost.power * 1.06`
  - `minus7_ext_capacity = ext_2_nonfrost_capacity * 0.734`
  - `minus7_ext_power = ext_2_nonfrost_power * 0.877`
- 출처 주석 명시:
  - `1.12 / 1.06`: 2°C frost → 2°C non-frost equivalent.
  - `0.734 / 0.877`: 2°C non-frost → -7°C, ISO Table 1 derived.
- Formula 44/45/47/48/49/50 식, branch selection, case naming 모두 미변경.

## task 2 결과
- 신규 파일: `tests/test_iso16358_hspf_extended_default.py`
- `test_minus7_ext_measured_passthrough`: `-7_ext` measured 가 그대로 반환됨을 확인.
- `test_minus7_ext_default_uses_two_step_factor`: `2_ext` only일 때 (cap=4200, pow=1700) 2-step factor가 적용되어
  - capacity = 4200 × 1.12 × 0.734 ≈ 3452.7
  - power = 1700 × 1.06 × 0.877 ≈ 1580.4 임을 확인 (`abs=1.0` / `abs=2.0` tolerance).
- `test_minus7_ext_default_differs_from_direct_factor`: 과거 direct factor (`2_ext × 0.734` / `2_ext × 0.877`) 와 새 결과가 명확히 다름을 보장 (regression guard).
- 결과: 3 passed.

## task 3 결과
- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` → `5 failed (XPASS strict)` 11 → 6 xfailed.
- 자연 pass 전환된 case (XPASS strict로 표시): **3, 4, 9, 10, 11**.
- 여전히 mismatch (xfail 유지) case: **8, 12, 13, 14, 15, 16**.
- 사용자 지시에 따라 `XFAIL_CASE_IDS` / fixture / expected 모두 미변경. XPASS strict 실패는 다음 작업(official exact expected/golden update)에서 처리.
- per-case 실측 vs expected (HSEC kWh / HSPF):

| case | actual HSEC | expected HSEC | actual HSPF | expected HSPF | match |
|------|-------------|---------------|-------------|---------------|-------|
| 1    | 1079.3      | 1079.3        | 4.527       | 4.527         | ✓ |
| 2    | 1061.4      | 1061.4        | 4.603       | 4.603         | ✓ |
| 3    | 1079.0      | 1079.0        | 4.528       | 4.528         | ✓ new |
| 4    | 1061.1      | 1061.1        | 4.604       | 4.604         | ✓ new |
| 5    | 1079.3      | 1079.3        | 4.527       | 4.527         | ✓ |
| 6    | 1077.2      | 1077.2        | 4.535       | 4.535         | ✓ |
| 7    | 1080.7      | 1080.7        | 4.520       | 4.520         | ✓ |
| 8    | 1078.5      | 1077.2        | 4.530       | 4.535         | ✗ +1.3 |
| 9    | 1058.0      | 1058.0        | 4.617       | 4.617         | ✓ new |
| 10   | 1064.4      | 1064.4        | 4.590       | 4.590         | ✓ new |
| 11   | 1061.1      | 1061.1        | 4.604       | 4.604         | ✓ new |
| 12   | 1108.6      | 1079.0        | 4.407       | 4.528         | ✗ +29.6 |
| 13   | 1077.2      | 1079.0        | 4.535       | 4.528         | ✗ -1.8 |
| 14   | 1077.2      | 1079.0        | 4.535       | 4.528         | ✗ -1.8 |
| 15   | 1112.8      | 1079.0        | 4.390       | 4.528         | ✗ +33.8 |
| 16   | 1111.2      | 1066.3        | 4.396       | 4.582         | ✗ +44.9 |

- 잔여 mismatch는 `2_full` / `2_half` measured 가 frost curve endpoint로 사용되는 별도 경로 (Cluster C / B / D, 098 분석) 에 기인. 본 패치 범위 밖.

## task 4 결과
- `docs/WORK_PLAN.md`의 "Repo 다음 순서" 갱신:
  1. official exact expected/golden update (XPASS strict 5건 처리 및 `XFAIL_CASE_IDS` 축소).
  2. ISO table Excel-like behavior patch.
  3. ISO result/read-only table copy TSV.
  4. unit adapter 확장: ISO / KS / EN.
- 099 진행 결과 (extended -7 default factor 적용 대상 정정, 5 case 자연 pass) 요약.
- result report lifecycle maintenance 제외 이유: 본 작업은 single helper 함수 정정에 한정되어 있고, active/archive/summaries 이동을 섞으면 commit scope가 커지고 회귀 위험이 증가하기 때문. lifecycle maintenance는 별도 작업으로 분리.

## Verification
- `python3 -B -m py_compile core/calculator_iso16358.py` → OK
- `python3 -B -m pytest tests/test_iso16358_hspf_extended_default.py -q` → 3 passed
- `python3 -B -m pytest tests/test_iso16358_hspf_frost_trace.py -q` → 8 passed
- `python3 -B -m pytest tests/test_iso16358_hspf_boundary_cop_alignment.py -q` → 6 passed, 1 skipped
- `python3 -B -m pytest tests/test_iso16358_hspf_formula_micro.py -q` → all pass
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py -q` → all pass
- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` → 5 failed (XPASS strict for case 3/4/9/10/11), 6 xfailed (case 8/12/13/14/15/16) — 의도된 상태, 다음 작업에서 `XFAIL_CASE_IDS` 갱신 예정.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → pass
- `python3 -B -m pytest -q` → 5 failed, 414 passed, 4 skipped, 29 xfailed (XPASS strict 5건은 본 보고 task 3 항목과 동일).

## Known Risks
- `XFAIL_CASE_IDS` 미갱신으로 official exact golden suite가 strict XPASS 5건으로 실패한다. 다음 작업 "official exact expected/golden update"에서 case 3/4/9/10/11을 `XFAIL_CASE_IDS`에서 제거해 정상 pass로 전환해야 한다.
- 잔여 mismatch (case 8/12/13/14/15/16) 는 `2_full` / `2_half` measured → frost curve endpoint 경로의 별개 이슈로, 098 audit의 Cluster B/C/D 대상. 본 작업과 분리해야 한다.
- result report lifecycle maintenance pending (active 폴더에 099까지 누적). 별도 정리 작업으로 분리.
