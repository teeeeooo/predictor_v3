# ISO16358 CSPF Region Config Phase 1 Report

## Scope

This phase freezes comparison notes, draft fixture shape, and production region
config integrity checks before changing any CSPF calculation logic or production
country JSON.

No production region config values were changed in this phase.

## Source Availability

The raw `golden_data.txt` file referenced by the task was not present under the
workspace or nearby Desktop paths during this pass. The fixture draft therefore
uses only the values explicitly provided in the task prompt. Row-level bin-hour
tables that were not fully present in the prompt are marked source-pending.

## Thailand Config Snapshot

`data/region_configs/thailand.json` currently has:

| Item | Current value |
| --- | --- |
| standard | ISO16358-1 / EGAT No.5 |
| t_100_load | 35.0 |
| reference_point | 35_full |
| t_0_load | 20.0 |
| Cd | 0.25 |
| building_load_source | measured |
| points | 35_full measure, 35_half measure, 29_full default, 29_half default |
| derived_rules | 29_full from 35_full, 29_half from 35_half |
| capacity_factor | 1.077 |
| power_factor | 0.914 |
| bin temperature range | 21 C to 39 C |
| bin row count | 19 |
| total bin hours | 2397 |

Current Thailand bin rows:

| tj | nj |
| --- | --- |
| 21 | 243 |
| 22 | 247 |
| 23 | 257 |
| 24 | 251 |
| 25 | 226 |
| 26 | 220 |
| 27 | 196 |
| 28 | 153 |
| 29 | 135 |
| 30 | 120 |
| 31 | 90 |
| 32 | 67 |
| 33 | 56 |
| 34 | 47 |
| 35 | 35 |
| 36 | 25 |
| 37 | 15 |
| 38 | 9 |
| 39 | 5 |

## Southeast Asia ISO Basic Golden Summary

The task prompt identifies the ISO16358-1 basic Southeast Asia golden as:

| Item | Golden summary |
| --- | --- |
| target regions | Thailand, Vietnam, Malaysia, Philippines, Indonesia |
| 35_full | 2691.334 W / 889.5 W |
| 35_half | 1249.055 W / 303.2 W |
| expected CSPF | 4.665 |
| total bin hours | 1817 |

The prompt did not include the row-level `tj` and `nj` values, so each bin row
cannot yet be compared against `thailand.json`.

## Comparison

| Item | thailand.json | SEA ISO basic golden | Status |
| --- | --- | --- | --- |
| bin temperature range | 21 C to 39 C | source-pending | cannot confirm |
| row-level nj | listed above | source-pending | cannot compare |
| total hours | 2397 | 1817 | mismatch |
| points | 35_full, 35_half measured; 29_full, 29_half default | two 35 C points in prompt summary | likely compatible but not complete |
| derived_rules | 29 C defaults from 35 C points | not specified in prompt summary | source-pending |
| Cd | 0.25 | not specified in prompt summary | source-pending |
| t_0_load | 20.0 | not specified in prompt summary | source-pending |
| building_load_source | measured | not specified in prompt summary | source-pending |

## Judgment

B안이 타당하다.

`thailand.json` already carries an EGAT-specific standard label and a comment
that the bin hours may need replacement after EGAT confirmation. Its current
total bin hours, 2397, do not match the provided Southeast Asia ISO basic
golden total of 1817. Without the raw row-level golden bin table, replacing
Thailand immediately would risk losing a Thailand/EGAT candidate config while
still not producing a verified ISO basic base config.

Next production step should create a separate base config named
`iso_t1_default_2point.json` only after the raw ISO basic `tj`/`nj` rows and
config semantics are confirmed. Thailand can then either inherit from or be
manually aligned with that base after EGAT-specific evidence is reviewed.

## Fixture Draft

Draft fixtures were added under
`tests/fixtures/iso16358_cspf_golden_fixtures.json` with four named samples:

| Fixture | Status |
| --- | --- |
| southeast_asia_iso_basic_cspf_4_665 | source-pending bin rows |
| india_iseer_5_00 | source-pending point values and bin rows |
| saso_cspf_4_95 | source-pending point values and bin rows; 50 C blank bin unresolved |
| hong_kong_cspf_4_83 | source-pending bin rows |

These are intentionally not enabled as regression tests yet.

## Next Turn Plan

1. Copy raw row-level bin tables from `golden_data.txt` into the draft fixtures.
2. Add fixture validation tests that require no `null` point values before a
   fixture can be used for calculation regression.
3. Add a CSPF golden regression test for the ISO basic Southeast Asia fixture.
4. Create `data/region_configs/iso_t1_default_2point.json` as a production base
   config only after the fixture regression is reproducible.
5. Add country production configs by copying the verified base only where the
   country standard actually uses that ISO basic profile.

## ISO T1 Default 2-Point Diagnostic

The completed fixture now gives a reproducible mismatch:

| Item | Value |
| --- | --- |
| fixture expected CSPF | 4.665 |
| current engine CSPF | 4.501 |
| current engine CSTL | 1,973,107 Wh |
| current engine CSEC | 438,400 Wh |
| status | strict xfail 1-sample regression |

Diagnostic variants from
`tests/test_iso16358_cspf_iso_t1_default_diagnostics.py`:

| Variant | CSPF | CSTL Wh | CSEC Wh | Interpretation |
| --- | --- | --- | --- | --- |
| A current, Cd 0.25, power_factor 0.914, t_0 20 | 4.501 | 1,973,107 | 438,400 | Baseline mismatch |
| B Cd 0.0 diagnostic only | 4.677 | 1,973,107 | 421,892 | Closest to 4.665 |
| C power_factor 0.914 | 4.501 | 1,973,107 | 438,400 | Same as baseline |
| C power_factor 0.864 | 4.832 | 1,973,107 | 408,376 | Overshoots; likely Korea coefficient confusion if applied here |
| D t_0 20.0 | 4.501 | 1,973,107 | 438,400 | Baseline |
| D t_0 21.0 | 4.473 | 1,764,746 | 394,498 | Moves farther from golden |
| D t_0 23.0 | 4.392 | 1,319,875 | 300,494 | Moves farther from golden |
| E derived 29 C unrounded | 4.501 | 1,973,107 | 438,400 | Baseline |
| E derived 29 C nearest integer | 4.502 | 1,973,107 | 438,253 | Rounding impact is negligible |

Most likely cause candidate: low-load `Cd` / PLF treatment. Setting `Cd = 0`
as a diagnostic-only variant moves the result from 4.501 to 4.677, which is
near the 4.665 fixture, while keeping CSTL constant and lowering CSEC. This
does not prove that production `Cd` should be changed. It only narrows the
mismatch to how the ISO T1 default 2-point worksheet treats cycling degradation
or low-load power below the half-capacity line.

Secondary candidates:

| Priority | Candidate | Diagnostic result |
| --- | --- | --- |
| 1 | Low-load Cd / PLF treatment | Strong: Cd 0.0 nearly reproduces golden |
| 2 | 35_half 이하 power calculation method | Still open; Cd effect occurs in this region |
| 3 | 29 C derived power factor | Weak: 0.864 overshoots to 4.832 and must not be imported from Korea |
| 4 | building_load_source / t_0_load / reference_point | Weak from tested t_0 variants |
| 5 | derived rounding / unit conversion | Weak: rounding changes CSPF by about 0.001 |

Do not modify `core/calculator_iso16358.py` or create
`iso_t1_default_2point.json` until the ISO16358-1 text or an official
calculation sheet confirms whether the default T1 2-point case applies `Cd`,
uses a different low-load PLF rule, or calculates power below 35_half by a
worksheet-specific method.

## ASEAN Report Table 7 Control Sample

The user-provided ASEAN AC EE Harmonization report summary supports the ISO T1
default 2-point direction:

| Item | Report summary |
| --- | --- |
| standard basis | ISO 16358:2013 |
| ASEAN/ISO default bin | 21 C to 35 C, 15 nonzero bins, 1817 h total |
| variable-speed required points | 35 C full and 35 C half capacity/power |
| 29 C full/half | ISO predetermined equations |
| 29 C capacity factor | 1.077 |
| 29 C power factor | 0.914 |
| minimum capacity | not considered for ASEAN/India/Japan/China <= 7.1 kW |
| CD / FPL context | CD = 0.25 appears as regional metric context and FPL is part of Annex C calculation |

Control fixture added:
`asean_report_table7_variable_speed_cspf_4_76`.

| Item | Expected / report | Current engine |
| --- | --- | --- |
| CSPF | 4.76 | 4.668 |
| Annual Energy Consumption | 555 kWh | 565.355 kWh |
| Annual cooling | not fixed in prompt summary | 2,639.280 kWh |
| status | published report example/control sample | strict xfail diagnostic |

Direction comparison:

| Sample | Expected CSPF | Current engine CSPF | Delta |
| --- | --- | --- | --- |
| user ISO T1 default fixture | 4.665 | 4.501 | -0.164 |
| ASEAN report Table 7 control | 4.760 | 4.668 | -0.092 |

Both samples are below the expected CSPF with the current engine. This makes a
fixture-specific data entry issue less likely and points toward shared Clause
6.7 / variable-speed CSPF implementation details. Because the ASEAN report also
keeps CD/FPL in scope, adding a production option to turn off `Cd` remains
blocked. The next check should reproduce the Annex C/Table 7 worksheet line by
line before modifying `calculate_cspf`.

## Clause 6.7 Bin Diagnostic

`tests/test_iso16358_cspf_clause67_bin_diagnostics.py` reproduces the current
CSPF bin loop for the ASEAN Table 7 control sample without changing production
code.

Current engine totals:

| Item | Value |
| --- | --- |
| current CSTL | 2,639.280 kWh |
| current CSEC | 565.355 kWh |
| report expected AEC / CSEC | 555.000 kWh |
| current over expected | +10.355 kWh |
| current CSPF | 4.668 |
| report expected CSPF | 4.760 |

Current engine range summary:

| Temperature range | Hours | CSTL kWh | CSEC kWh | Share of current CSEC | Operating case | Suspected mismatch relevance |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 21-23 C | 404 | 209.520 | 43.301 | 7.7% | load below half capacity | FPL/PLF active; low-load sensitivity |
| 24-27 C | 831 | 1,102.560 | 222.734 | 39.4% | load below half capacity | FPL/PLF active; largest low-load contribution |
| 28 C | 181 | 347.520 | 69.219 | 12.2% | load below half capacity | half-capacity boundary; high relevance |
| 29-35 C | 401 | 979.680 | 230.102 | 40.7% | load between half and full | interpolation path, no PLF |

The current engine applies PLF from 21 C through 28 C because `Lc <=
phi_half(tj)` in those bins. That low-load group contributes 335.254 kWh, or
about 59.3% of current CSEC. The official report only gives the total 555 kWh
annual energy in the prompt summary, not per-bin expected CSEC, so the exact
10.355 kWh overage cannot yet be assigned bin-by-bin. However, if the mismatch
is caused by FPL/PLF treatment, the affected bins are concentrated in 21-28 C,
especially 24-28 C where the low-load contribution is largest.

Next implementation candidates to verify against ISO Annex C / Table 7:

| Candidate | Why it matters |
| --- | --- |
| half 이하 구간의 `P(tj)` 산식 | Current low-load bins compute `P_tj = (X * P_half(tj)) / PLF` |
| FPL 적용 대상/분모 | Current `X` uses `Lc / phi_half(tj)` in low-load bins, not `Lc / phi_full(tj)` |
| current engine PLF denominator vs worksheet `P(tj)` definition | The engine divides low-load power by PLF; official worksheet may define equivalent power differently |

No calculator change has been made. Do not modify `calculate_cspf` until the
official Annex C/Table 7 worksheet confirms the exact low-load formula.

## mismatch 원인 판단 기록

KS C 9306과 ISO 16358-1 기본 2점식 CSPF는 계산 경로가 다르다.

| 항목 | KS C 9306 | ISO 16358-1 기본 2점식 |
|---|---|---|
| t_0_load | 23°C | 20°C |
| BLc 기준 | declared 중심 | measured full capacity 기준 |
| 29°C power_factor | KS profile에서는 0.864 계열 사용 | ISO/ASEAN 기본 경로에서는 0.914 |
| minimum capacity | 29_min / 35_min 등 KS profile에 포함 | ASEAN/ISO T1 2점식에서는 not considered |
| low-load / PLF 처리 | 현재 Korea CSPF 6.504로 검증된 경로 | ISO Clause 6.7 원문 경로 확인 필요 |

현재 CSPF 엔진의 핵심 저부하/PLF 처리 방식은 Korea CSPF golden 6.504에 맞춰 검증되어 있으며,
이 regression은 반드시 유지해야 한다.

반면 ISO T1 default 2-point fixture는 다음 두 control sample에서 모두 현재 엔진보다 높은 expected 값을 가진다.

- User ISO T1 default golden: expected CSPF 4.665, current engine CSPF 4.501
- ASEAN Table 7 control sample: expected CSPF 4.760, current engine CSPF 4.668

두 sample 모두 같은 방향으로 mismatch가 발생하므로,
문제는 특정 fixture 입력 오류라기보다 ISO16358-1 Clause 6.7 variable-speed 2-point 계산 경로와
현재 엔진의 저부하/PLF 처리 방식 차이일 가능성이 크다.

그러나 ASEAN 보고서 Annex C는 P(tj), FPL(tj), CSEC(tj)의 정의와 Table 7 결과를 제공하지만,
load < half capacity 구간에서 현재 엔진의 `P_tj = (X * P_half(tj)) / PLF`를
어떤 대체식으로 바꿔야 하는지까지는 명시하지 않는다.

따라서 현재 단계에서는 core/calculator_iso16358.py를 수정하지 않는다.
Cd=0, 임의 PLF 보정 지수, sample-specific 보정계수 등은 hidden factor 성격이므로 사용하지 않는다.

ISO T1 default 2-point 경로는 향후 ISO 16358-1 Clause 6.7 원문 또는 공식 worksheet의 bin별 P(tj)/CSEC(tj)를 확보한 뒤,
기존 KS C 9306 regression에 영향을 주지 않는 별도 profile 또는 명시적 분기로 구현한다.

따라서 다음 항목은 보류한다.

- iso_t1_default_2point.json production config 추가
- thailand.json 삭제
- ISO T1 default golden xfail 해제
- ASEAN Table 7 control sample xfail 해제

## ISO T1 2-Point Control Sample Matrix

ISO T1 default 2-point profile now has four control samples in
`tests/fixtures/iso16358_cspf_golden_fixtures.json`. All four use the same
structure: 35 C full and half points are measured, 29 C full and half points
are default values from the ISO factors, minimum capacity is not considered,
`Cd = 0.25`, and the ISO 1817 h reference bin is used.

Current engine comparison from
`tests/test_iso16358_cspf_iso_t1_2point_control_samples.py`:

| sample id | 35_full W/W | 35_half W/W | expected CSPF | expected CSEC/CSTL | current CSPF | current CSEC/CSTL | delta | status |
| --- | --- | --- | ---: | --- | ---: | --- | ---: | --- |
| southeast_asia_iso_basic_cspf_4_665 | 2691.334 / 889.5 | 1249.055 / 303.2 | 4.665 | n/a | 4.501 | 438.400 / 1973.107 kWh | -0.164 | diagnostic mismatch |
| asean_report_table7_variable_speed_cspf_4_76 | 3600 / 1080 | 1800 / 432 | 4.760 | CSEC 555 kWh | 4.668 | 565.355 / 2639.280 kWh | -0.092 | diagnostic xfail |
| jatl_slide_variable_capacity_cspf_4_86 | 2800 / 800 | 1400 / 330 | 4.860 | n/a | 4.783 | 429.213 / 2052.773 kWh | -0.077 | diagnostic mismatch |
| jatl_tool_required_test_only_cspf_4_93 | 2800 / 700 | 1400 / 330 | 4.930 | CSEC 417 kWh, CSTL 2053 kWh | 4.904 | 418.590 / 2052.773 kWh | -0.026 | diagnostic mismatch |

All four current engine CSPF values are lower than the expected/control values.
That consistent direction makes a single fixture data-entry issue unlikely and
keeps the focus on the shared ISO T1 2-point variable-capacity path,
especially the low-load `P(tj)` / FPL behavior below half capacity.

The JATL tool sample is close in absolute terms, but it still follows the same
direction. Therefore the implementation should not be changed by fitting one
sample. The next step remains obtaining ISO 16358-1 Clause 6.7 or official
worksheet bin-level `P(tj)` / `CSEC(tj)` values and then adding a profile or
explicit branch that does not alter the verified KS C 9306 path.

The following remain blocked:

- `iso_t1_default_2point.json` production config
- ISO T1 default golden xfail release
- ASEAN Table 7 xfail release
- any change that uses `Cd = 0`, an arbitrary PLF exponent, or a sample-specific correction factor

## Official ISO Amd1 calculation tool formula audit

Audit target:
`20181107 ISO16358-1_AMD1 Calculation_tool_FINAL.xlsm`.

Relevant worksheet:
`Variable Capacity unit`, T1 block title `CA1 = "CSPF for Variable unit (at T1)"`.

Key T1 cells:

| Item | Cell / formula |
| --- | --- |
| Full 35 C capacity / power | `H9`, `L9` |
| Half 35 C capacity / power | `H10`, `L10` |
| Minimum 35 C capacity / power | `H11`, `L11` |
| Load reference | `CC3 = H9` |
| CD | `CH5 = data!D14 = 0.25` |
| 29 C capacity factor | `CH6 = data!D15 = 1.077` |
| 29 C power factor | `CH7 = data!D16 = 0.914` |
| t0 / t100 | `CH8 = data!D11 = 20`, `CH9 = data!D12 = 35` |
| CSTL / CSEC / CSPF outputs | `Y13 = CK49/1000`, `Y14 = CZ49/1000`, `Y15 = CF3` |
| internal sums | `CK49 = SUM(CK18:CK48)`, `CZ49 = SUM(CZ18:CZ48)`, `CF3 = CK49/CZ49` |

T1 bin table columns:

| Column | Meaning |
| --- | --- |
| `CC18:CC48` | `tj` |
| `CD18:CD48` | `nj` |
| `CE18:CE48` | `Lc(tj)` |
| `CF18:CF48` | `FPL(tj)` |
| `CG18:CG48` | `X(tj)` |
| `CH18:CH48` | `phi_full(tj)` |
| `CI18:CI48` | `phi_half(tj)` |
| `CJ18:CJ48` | `phi_min(tj)` |
| `CK18:CK48` | `CSTL(tj)` |
| `CL18:CL48` | `P_full(tj)` |
| `CM18:CM48` | `P_half(tj)` |
| `CN18:CN48` | `P_min(tj)` |
| `CV:CZ` | branch power inputs and `CSEC(tj)` |

Step 1 conclusion:
the low-load branch itself is structurally the same as the current engine for
Required-test-only / Minimum Not Measure.

Official low-load formulas:

| Formula | Meaning |
| --- | --- |
| `X = Lc / phi_min(tj)` | low-load ratio |
| `FPL = 1 - CD * (1 - X)` | part-load factor |
| `P(tj) = X * P_min(tj) / FPL` | low-load power input |
| `CSEC(tj) = P(tj) * nj` | bin energy |

For Required-test-only or Minimum Not Measure, `phi_min(tj)` and `P_min(tj)`
are replaced by the half-capacity curve. Therefore the effective low-load
formula is `X = Lc / phi_half(tj)` and `P(tj) = X * P_half(tj) / FPL`, matching
the current engine's low-load branch. The earlier hypothesis that the
low-load `P_half / PLF` branch is directly wrong is therefore on hold.

Step 2 official mirror helper:
`tests/test_iso16358_cspf_official_tool_formula_diagnostics.py` mirrors the
audited T1 xlsm formulas in Python for diagnostic purposes only. It does not
modify or import production calculation logic except to compare current engine
totals.

Official helper results:

| sample id | expected CSPF | official helper CSPF | current engine CSPF | official helper CSEC | current CSEC | status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| southeast_asia_iso_basic_cspf_4_665 | 4.665 | 4.665 | 4.501 | 422.932 kWh | 438.400 kWh | helper reproduces expected |
| asean_report_table7_variable_speed_cspf_4_76 | 4.760 | 4.756 | 4.668 | 554.991 kWh | 565.355 kWh | helper reproduces expected within report rounding |
| jatl_slide_variable_capacity_cspf_4_86 | 4.860 | 4.858 | 4.783 | 422.574 kWh | 429.213 kWh | helper reproduces expected within slide rounding |
| jatl_tool_required_test_only_cspf_4_93 | 4.930 | 4.928 | 4.904 | 416.513 kWh | 418.590 kWh | helper reproduces expected within tool rounding |

JATL Required-test-only sample reproduction:

| Item | Expected | Official helper | Current engine |
| --- | ---: | ---: | ---: |
| CSTL | 2053 kWh | 2052.773 kWh | 2052.773 kWh |
| CSEC | 417 kWh | 416.513 kWh | 418.590 kWh |
| CSPF | 4.93 | 4.928 | 4.904 |

The official helper and current engine first diverge in the 29 C bin. The first
recorded worksheet-field difference is `X`: the official sheet sets `X = 1`
outside the low-load branch, while the current diagnostic mirror can still
compute a non-used `Lc / phi_half` ratio. The first energy-affecting difference
is also at 29 C in `P(tj)`:

| Item | Current engine mirror | Official helper |
| --- | ---: | ---: |
| `tj` | 29 C | 29 C |
| operating branch | load between half and full | load between half and full |
| `P(tj)` | 340.242 W | 337.396 W |

This shifts the main mismatch candidate away from the low-load branch and
toward the full-half interpolation branch. The current engine interpolates
power linearly by capacity between half and full:
`P = P_half + (P_full - P_half) * (Lc - phi_half) / (phi_full - phi_half)`.

The official xlsm instead computes boundary EER values and then uses a
temperature-based EER interpolation for the half-to-full branch:

| Official branch | Formula shape |
| --- | --- |
| half < load <= full | interpolate EER between the half/full boundary EERs by `tj`, then `P(tj) = Lc / EER(tj)` |
| load <= half/min replacement | keep `X * P_half(tj) / FPL` |
| load > full | use full curve power |

Therefore the minimal future calculator change, if approved in a separate
implementation turn, is not a `Cd` change. It is an ISO T1 variable-capacity
2-point branch that uses the official xlsm EER interpolation formula for
`half < Lc <= full`, scoped so that KS C 9306 and other existing profiles keep
their current verified behavior.

No code change to `core/calculator_iso16358.py` has been made in this audit
turn, and no production region config has been added.

## ISO Boundary EER Method Implementation

The mismatch source is now narrowed to the full-half branch, not the low-load
branch. The low-load formula remains the existing `X * P_half(tj) / FPL`
calculation for the ISO T1 Required-test-only / Minimum Not Measure path.

New opt-in method:
`power_interpolation_method = "iso_boundary_eer"`.

Scope:

| Path | Behavior |
| --- | --- |
| default / missing method | unchanged capacity-linear interpolation |
| `ks_intersection` | unchanged KS C 9306 path |
| `iso_boundary_eer` low-load branch | unchanged `X * lowest_pow / PLF` |
| `iso_boundary_eer` half < load <= full | official xlsm boundary-EER interpolation, then `P(tj) = Lc / EER(tj)` |
| HSPF paths | unchanged |

Implemented boundary formula:

```text
tb = (6*ref*t0 + 6*phi_full35*dt + 35*(phi_full29-phi_full35)*dt)
     / (6*ref + (phi_full29-phi_full35)*dt)

tc = (6*ref*t0 + 6*phi_half35*dt + 35*(phi_half29-phi_half35)*dt)
     / (6*ref + (phi_half29-phi_half35)*dt)

EER_tb = phi_full(tb) / P_full(tb)
EER_tc = phi_half(tc) / P_half(tc)
EER(tj) = EER_tc + (EER_tb-EER_tc)/(tb-tc) * (tj-tc)
P(tj) = Lc / EER(tj)
```

Control regression results using `iso_boundary_eer`:

| sample id | expected CSPF | actual CSPF | actual CSTL | actual CSEC | status |
| --- | ---: | ---: | ---: | ---: | --- |
| southeast_asia_iso_basic_cspf_4_665 | 4.665 | 4.665 | 1973.107 kWh | 422.932 kWh | pass, provenance-pending control |
| asean_report_table7_variable_speed_cspf_4_76 | 4.760 | 4.756 | 2639.280 kWh | 554.991 kWh | pass within published rounding |
| jatl_slide_variable_capacity_cspf_4_86 | 4.860 | 4.858 | 2052.773 kWh | 422.574 kWh | pass within slide rounding |
| jatl_tool_required_test_only_cspf_4_93 | 4.930 | 4.928 | 2052.773 kWh | 416.513 kWh | pass within tool rounding |

Korea CSPF remains on the existing KS path and keeps the 6.504 regression.
No production `iso_t1_default_2point.json` config has been added in this turn.
