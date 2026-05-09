# Design Gate Summary

## Goal

ISO16358-2 HSPF common path와 AS/NZS / Energy Rating SEER calculator Excel exact-match path의 compatibility boundary를 코드 구현 전에 고정한다. 이번 결정은 문서화 전용이며 코드, 테스트, fixture expected를 변경하지 않는다.

## Context

- Windows Excel COM original workbook 기준 case 3 baseline은 `H12 = 1126.120 kWh`, `H13 = 4.33824`, `CH48 = 1126120.47 Wh`이다.
- 현재 predictor_v3 common ISO path는 같은 case에서 대략 `HSEC = 1134087.8405 Wh`, `HSPF = 4.308`을 낸다.
- Excel workbook의 `BN` / `BP` / `BY` / `CA` / `CC` COP helper columns는 boundary COP를 temperature axis로 선형 보간하고 `BA / COP_helper(tj)` 형태로 component power를 산출한다.
- 이 workbook helper convention은 ISO16358-2 Formula 47/49/50의 common production implementation과 동일한 수학적 계약으로 보지 않는다.

## Confirmed Decisions

- ISO16358 common HSPF path는 ISO 원문 기준의 bin temperature `tj`, capacity/power curve, load ratio `X_j`, Formula 47/49/50-style power calculation을 유지한다.
- `4.33824` / `1126.120 kWh` / `1126120.47 Wh`는 AS/NZS Excel compatibility reference이며 ISO common expected가 아니다.
- AS/NZS Excel exact matching은 common ISO calculator path에 섞지 않고 별도 compatibility calculator/profile로 분리한다.
- `calculator_iso16358.py` common path에는 AS/NZS workbook helper cell convention을 직접 추가하지 않는다.
- `BE5` / `BK5` / `BQ5`, `BE6` / `BK6` / `BQ6`, `BN` / `BP` / `BY` / `CA` / `CC` 같은 workbook helper cells/anchors를 common production code에 복제하지 않는다.

## Boundary Decision

| Item | Common/Core | Specialized/Compatibility Profile | Reason |
|---|---|---|---|
| ISO16358-2 HSPF expected | ISO standard common behavior | N/A | common path는 external workbook exact-match를 golden으로 삼지 않는다. |
| AS/NZS Excel case 3 `4.33824` / `1126.120 kWh` | N/A | AS/NZS Excel compatibility reference | 원본 workbook 계산값은 보존하되 reference type을 분리한다. |
| COP helper columns | 사용하지 않음 | workbook compatibility convention으로만 재현 가능 | helper columns는 common Formula 47/49/50 implementation 계약이 아니다. |
| Workbook anchor cells | production code에 복제하지 않음 | compatibility module 내부에서만 필요한 경우 해석 | common core가 Excel sheet layout에 결합되는 것을 막는다. |
| Calculator/profile selection | resolver manifest contract | `asnzs_excel_hspf_compat` 같은 explicit profile | selector ambiguity와 hidden coupling을 방지한다. |

## Data Shape / API Boundary

- Candidate profile record:
  - `profile_id=asnzs_excel_hspf_compat`
  - `standard=ASNZS`
  - `region=au_nz`
  - `metric=HSPF`
  - `mode=heating`
  - `calculator_id=asnzs_excel_hspf`
  - `config_path=data/region_configs/asnzs_excel_hspf.json`
  - `enabled=false` until implemented and validated
- Candidate module: `core/calculator_asnzs_hspf_excel.py`
- Public API impact: none in this documentation phase.
- Backward compatibility: current ISO common HSPF output, xfail policy, fixtures, and tests remain unchanged.

## Dual-track Architecture Contract

Track A — ISO16358-2 common HSPF path:

- Keep the ISO text-oriented Formula 47/49/50-style calculation flow in `calculator_iso16358.py`.
- Do not use AS/NZS Excel final HSPF or CHSE values as common ISO golden expected values.
- Because final-result coverage is not yet sufficient for broad Track A validation, prioritize smaller invariants over a single large final assertion:
  - formula micro golden
  - branch routing invariant
  - cycling PLF edge case
  - accumulation invariant
  - auxiliary energy invariant
- Candidate micro/edge cases:
  - load equals half capacity -> `P_j = P_half`
  - load equals full capacity -> `P_j = P_full`
  - load equals `0.5 * min capacity` -> `X = 0.5`, `PLF = 1 - Cd * (1 - X)`, `P_j = X * P_min / PLF`
  - load between full and extended -> Formula 50 branch
  - load greater than extended -> auxiliary energy included

Track A validation phases:

- Phase H-1: ISO HSPF formula micro golden tests.
- Phase H-2: KS shared-formula oracle consistency gate.
- Phase H-3: AS/NZS Excel compatibility guard/design.
- Phase H-4: compatibility module skeleton.

Phase H-1 test design:

- Purpose: validate the ISO16358-2 common HSPF path with hand-calculated micro fixtures and invariants, not with AS/NZS Excel final values.
- Do not use AS/NZS Excel `4.33824`, `1126.120 kWh`, or `1126120.47 Wh` as H-1 expected values.
- Do not use KS C 9306 path results as H-1 expected values; KS consistency belongs to Phase H-2.
- Recommended test file: `tests/test_iso16358_hspf_formula_micro.py`.
- Alternate name if the suite grows around behavioral properties: `tests/test_iso16358_hspf_invariants.py`.
- Keep all micro fixture data under the test namespace. Do not add H-1 micro values to production `data/region_configs`.

Candidate H-1 tests:

- `test_hspf_power_at_half_load_equals_half_power`
- `test_hspf_power_at_full_load_equals_full_power`
- `test_hspf_cycling_below_min_uses_plf`
- `test_hspf_half_to_full_interpolation_matches_hand_calculation`
- `test_hspf_full_to_extended_branch_uses_formula_50`
- `test_hspf_above_extended_adds_auxiliary_energy`
- `test_hspf_bin_accumulation_matches_hand_calculation`

Assertion strategy:

- Prefer bin-level diagnostics over final HSPF alone.
- Public ISO common result currently exposes `bin_details` with `tj`, `nj`, `bl_h`, `pi_j`, `P_j`, `case`, `heat_pump_energy`, `auxiliary_energy`, and `E_j`, plus top-level `hstl_wh`, `hsec_wh`, `heat_pump_energy_wh`, and `auxiliary_energy_wh`.
- Use public `calculate_hspf()` / `calculate_hspf_iso16358_common()` result diagnostics first.
- Private helpers may be used only for narrow formula micro checks when public diagnostics are insufficient, for example `_iso_hspf_capacity_curve`, `_iso_hspf_power_curve`, `_iso_hspf_min_half_power_by_formula_44_48`, and `_iso_hspf_formula50_full_extended_frost_power`.
- Do not change production API in Phase H-1. If diagnostics are insufficient, design minimal diagnostics exposure as a separate phase.

Candidate micro fixtures:

- Half boundary identity: set load equal to half capacity. Expect `P_j = P_half`, no auxiliary energy, and boundary/interpolation behavior consistent with the selected branch.
- Full boundary identity: set load equal to full capacity. Expect `P_j = P_full` and no auxiliary energy.
- Below minimum cycling PLF: set load to `0.5 * min_capacity` with explicit `Cd`. Expect `X = 0.5`, `PLF = 1 - Cd * (1 - X)`, `P_j = X * P_min / PLF`, `E_j = P_j * bin_hours`, and no auxiliary energy.
- Half-to-full interpolation: set `half_capacity < load < full_capacity`. Expect half-full interpolation and hand-calculated `P_j`.
- Full-to-extended Formula 50: set frost-bin `full_capacity < load <= extended_capacity`. Expect `formula50_full_extended_frost`, hand-calculated `P_j`, and no auxiliary energy.
- Above extended auxiliary: implementation check required before locking expected values. Current common path enters `saturated` when Formula 50 is unavailable or `load > extended_capacity`, uses full-stage power, and computes auxiliary from `load - full_capacity`; if the intended ISO contract is extended-capacity saturation, that should be resolved before H-1 expected values are frozen.
- Accumulation invariant: use a tiny 2-3 bin fixture. Expect `hstl_wh = sum(load_j * hours_j)`, `hsec_wh = sum(E_j)`, and `hspf = hstl_wh / hsec_wh` before final rounding.

KS shared-formula oracle consistency gate:

- Use the implemented KS C 9306 HSPF path as a surrogate oracle / cross-path consistency gate only.
- Do not promote KS path results to common ISO expected values.
- Purpose is shared-formula consistency plus accumulation and branch sanity checking.
- In test fixture scope, apply ISO16358-2 bin hours to the KS path as well.
- Align the load-line basis with the ISO common path.
- Declare stage mapping explicitly:
  - KS rated <-> ISO full
  - KS intermediate <-> ISO half
  - KS min <-> ISO min
  - KS max <-> ISO extended
- Control KS-specific correction factors and policy knobs:
  - defrost correction
  - -7°C fallback / capacity / power factor
  - `Cd`
  - `aux_cop`
  - Korean-only correction
- Compare bin-level diagnostics before final HSPF:
  - branch
  - load
  - capacity boundary
  - `P_j`
  - `E_j`
  - auxiliary energy
  - HSTL / HSEC accumulation
- Treat final HSPF assertion as a secondary signal only.

Track B — AS/NZS Excel HSPF compatibility path:

- Target exact matching against the original Windows Excel COM workbook.
- Allow workbook conventions such as `BN` / `BP` / `BY` / `CA` / `CC`, `BA / COP_helper(tj)`, `CG` / `CH` / `CH48` only inside this compatibility path.
- Keep a separate calculator/profile/test namespace.
- Isolate from Track A through resolver opt-in guards.
- Keep `1126.120 kWh`, `4.33824`, and `1126120.47 Wh` only under the `ASNZS_EXCEL_COMPAT` reference namespace.

## Design Contract Candidate

Calculator/profile identity:

- `profile_id`: `asnzs_excel_hspf_compat`
- `calculator_id`: `asnzs_excel_hspf`
- `standard`: `ASNZS`
- `region`: `au_nz`
- `metric`: `HSPF`
- `mode`: `heating`
- `reference_type`: `ASNZS_EXCEL_COMPAT`
- candidate module: `core/calculator_asnzs_hspf_excel.py`
- candidate config: `data/region_configs/asnzs_excel_hspf.json`

Input contract candidate:

- Reuse common ISO canonical heating test input where possible.
- Keep workbook-specific helper convention inside the compatibility calculator only.
- Do not put candidate values, golden/sample/test-only values, Excel dump values, or ML predictions into production region config.
- Treat Windows Excel COM `full_dump` / `chat_packet` values as reference artifacts or test fixture namespace data only.

Resolver boundary:

- The resolver must select AS/NZS Excel compatibility through explicit `profile_id` / `calculator_id`.
- `region=au_nz` or `standard=ASNZS` alone must not enable compatibility mode.
- ISO common calculator code must not branch internally on `reference_type=ASNZS_EXCEL_COMPAT`.
- The compatibility profile is opt-in only.

Golden/reference namespace:

- `4.33824`, `1126.120 kWh`, and `1126120.47 Wh` are not ISO common golden expected values.
- These values belong only under the `ASNZS_EXCEL_COMPAT` namespace / reference type.
- Common ISO golden tests and AS/NZS Excel compatibility golden tests must be distinguishable by filename, fixture namespace, and assertion message.

## Required Tests

- No tests are changed in this documentation phase.
- Future implementation should add explicit AS/NZS Excel compatibility golden tests separate from ISO common golden tests.
- Future guard tests should prove that ISO common expected values do not silently adopt AS/NZS Excel compatibility baselines.
- Future resolver tests should verify that `asnzs_excel_hspf_compat` is selected only by explicit profile/calculator id.
- Future guard tests should verify that `region=au_nz` / `standard=ASNZS` alone does not activate compatibility mode.
- Future guard tests should verify that Excel helper convention is not imported or replicated in `calculator_iso16358.py`.

## Migration / Refactor Path

1. Keep ISO common HSPF implementation and existing fixtures unchanged.
2. Add an explicit AS/NZS Excel compatibility profile only after the compatibility module contract is approved.
3. Implement Excel exact matching in a separate compatibility calculator/profile, not in `calculator_iso16358.py`.
4. Promote Windows Excel COM baselines only as `REFERENCE_TYPE=ASNZS_EXCEL_COMPAT`, not as ISO common golden expected.

## Non-goals

- No code implementation.
- No test, fixture, expected, or xfail change.
- No production region config change.
- No workbook helper cell replication in common ISO code.
- No claim that the AS/NZS Excel baseline is invalid; only its reference type is reclassified.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Excel compatibility baseline is treated as ISO common expected | common ISO path may be distorted by workbook layout details | require explicit `REFERENCE_TYPE=ASNZS_EXCEL_COMPAT` and separate profile id |
| Workbook helper cells leak into common code | ISO implementation becomes coupled to external sheet conventions | keep helper conventions inside compatibility module/profile only |
| Converted workbook values are used as reference | false golden updates | use original Windows Excel COM as trusted calculation reference only |
| Compatibility profile is exposed before validation | UI/user may see unstable HSPF values | keep candidate profile disabled until implementation and golden tests are complete |

## Next Codex Implementation Prompt

```text
Implement AS/NZS Excel HSPF exact matching only after this design boundary is accepted. Do not modify calculator_iso16358.py common ISO behavior, ISO common expected values, or existing HSPF fixtures. Add a separate compatibility calculator/profile candidate such as core/calculator_asnzs_hspf_excel.py with profile_id=asnzs_excel_hspf_compat and calculator_id=asnzs_excel_hspf. Treat Windows Excel COM case baselines as REFERENCE_TYPE=ASNZS_EXCEL_COMPAT, not ISO common golden expected.
```
