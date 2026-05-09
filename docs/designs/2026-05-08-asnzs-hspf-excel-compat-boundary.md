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
| Calculator/profile selection | resolver manifest contract | `asnz_excel_hspf_compat` 같은 explicit profile | selector ambiguity와 hidden coupling을 방지한다. |

## Data Shape / API Boundary

- Candidate profile record:
  - `profile_id=asnz_excel_hspf_compat`
  - `standard=ASNZS`
  - `region=au_nz`
  - `metric=HSPF`
  - `mode=heating`
  - `calculator_id=asnz_excel_hspf`
  - `config_path=data/region_configs/asnz_excel_hspf.json`
  - `enabled=false` until implemented and validated
- Candidate module: `core/calculator_asnzs_hspf_excel.py`
- Public API impact: none in this documentation phase.
- Backward compatibility: current ISO common HSPF output, xfail policy, fixtures, and tests remain unchanged.

## Design Contract Candidate

Calculator/profile identity:

- `profile_id`: `asnz_excel_hspf_compat`
- `calculator_id`: `asnz_excel_hspf`
- `standard`: `ASNZS`
- `region`: `au_nz`
- `metric`: `HSPF`
- `mode`: `heating`
- `reference_type`: `ASNZS_EXCEL_COMPAT`
- candidate module: `core/calculator_asnzs_hspf_excel.py`
- candidate config: `data/region_configs/asnz_excel_hspf.json`

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
- Future resolver tests should verify that `asnz_excel_hspf_compat` is selected only by explicit profile/calculator id.
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
Implement AS/NZS Excel HSPF exact matching only after this design boundary is accepted. Do not modify calculator_iso16358.py common ISO behavior, ISO common expected values, or existing HSPF fixtures. Add a separate compatibility calculator/profile candidate such as core/calculator_asnzs_hspf_excel.py with profile_id=asnz_excel_hspf_compat and calculator_id=asnz_excel_hspf. Treat Windows Excel COM case baselines as REFERENCE_TYPE=ASNZS_EXCEL_COMPAT, not ISO common golden expected.
```
