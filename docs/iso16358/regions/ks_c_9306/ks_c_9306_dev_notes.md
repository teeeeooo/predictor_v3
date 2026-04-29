# KS C 9306 Dev Notes

## 1. Purpose

이 문서는 KS C 9306 region 구현을 수정하거나 검증할 때 필요한 구현 노하우, 실수 방지 규칙, 디버깅 방법, 테스트 전략을 정리한다. 공통 ISO 용어는 [../../iso16358_glossary.md](../../iso16358_glossary.md)를 참조하고, KS 고유 용어는 [ks_c_9306_glossary.md](./ks_c_9306_glossary.md)를 참조한다. 이 문서에는 glossary 본문을 중복 작성하지 않는다.

## 2. Top Implementation Pitfalls

| Pitfall | Symptom | Cause | Prevention |
| --- | --- | --- | --- |
| ROUND_HALF_UP 누락 | golden sample의 CSPF와 annual power가 어긋난다. | raw float 시험값을 그대로 사용한다. | `round_test_values` 적용 위치를 먼저 확인한다. |
| Python `round()` 사용 | .5 경계에서 인증 계산과 다른 정수가 나온다. | bankers rounding이 적용된다. | Decimal 기반 HALF_UP helper를 사용한다. |
| declared capacity 누락 | ValueError가 발생하거나 BL(tj)가 잘못 잡힌다. | 한국은 measured reference가 아니라 declared source이다. | `building_load_source = declared`를 유지한다. |
| `ks_intersection` 미적용 | 중간 용량 범위 power가 golden과 달라진다. | 기본 capacity-linear interpolation으로 fallback된다. | `power_interpolation_method`를 확인한다. |
| 외삽 과신 | 고온/저온 bin에서 비현실적인 capacity/power가 나온다. | 시험점 두 개로 선형 외삽한다. | 외삽 bin과 BL > max_cap branch를 함께 점검한다. |
| BL > max_cap 처리 변경 | cooling output이 과대 계산된다. | 요구 부하를 항상 처리한다고 가정한다. | 최고 용량 초과 시 output cap을 유지한다. |

## 3. `round_test_values` Application

| Target | Applied | Reason |
| --- | --- | --- |
| measured `capacity` | Yes | KS 시험값은 계산 전 정수 반올림한다. |
| measured `power` | Yes | KS 시험값은 계산 전 정수 반올림한다. |
| derived `capacity` | Yes | 파생 factor 적용 후 정수 반올림한다. |
| derived `power` | Yes | 파생 factor 적용 후 정수 반올림한다. |
| `declared_capacity` | Yes | BL(tj)의 기준값도 정수화된 declared capacity를 사용한다. |
| non-numeric metadata | No | 계산 대상이 아니다. |

## 4. `power_interpolation_method` Separation

`power_interpolation_method = ks_intersection`은 KS C 9306 region 전용 동작이다. ISO 공통 기본 동작인 capacity-linear interpolation과 분리되어야 한다.

| Method | Use case | Risk if mixed |
| --- | --- | --- |
| `capacity_linear` | ISO 공통 기본 보간 | KS golden sample 불일치 |
| `ks_intersection` | KS C 9306 중간 부하 전력 산정 | 타 region에 적용하면 국가별 특례가 누출됨 |

구현 판단: KS method가 실패해 `None`을 반환할 때만 공통 capacity-linear fallback을 허용한다. 이 fallback은 방어 로직이지 KS 주 계산 경로가 아니다.

## 5. Extrapolation Handling

| Condition | Behavior | Debug check |
| --- | --- | --- |
| tj below measured temperature range | 가장 낮은 두 시험온도로 외삽한다. | 24°C bin에서 29°C/35°C 시험선 외삽 결과를 확인한다. |
| tj above measured temperature range | 가장 높은 두 시험온도로 외삽한다. | 36~37°C bin에서 capacity와 power가 의도 범위인지 확인한다. |
| `nj = 0` | 누적에서 제외한다. | 38°C bin은 계산 결과에 영향을 주지 않아야 한다. |
| extrapolated capacity below load | BL > max_cap branch로 넘어갈 수 있다. | cooling output cap과 annual cooling 결과를 확인한다. |

## 6. BL > max_cap Handling

BL(tj)가 해당 온도의 최고 capacity보다 크면 장비가 요구 부하를 모두 처리한다고 가정하지 않는다. 이 경우 cooling output은 highest capacity로 제한되고, power는 highest power를 사용한다.

검증 포인트:

| Check | Expected |
| --- | --- |
| cooling output | Lc가 아니라 highest capacity |
| power | highest power |
| annual cooling | 요구 부하 전체 합보다 작아질 수 있음 |
| CSPF | 출력 cap과 power cap이 함께 반영됨 |

## 7. `recommend_35_half_capacity` Structure

이 helper는 CSPF 본계산에 사용하지 않는 독립 추천 계산이다. 목적은 35°C half capacity 목표값을 설계 검토용으로 산정하는 것이다.

| Step | Meaning |
| --- | --- |
| 1 | 29°C minimum capacity를 35°C minimum capacity로 환산한다. |
| 2 | minimum capacity line과 building load line의 교점 온도 `T_min`을 구한다. |
| 3 | `T_min`과 35°C 사이의 중간 온도 `T_mid`를 구한다. |
| 4 | `T_mid`의 building load를 구한다. |
| 5 | 29↔35°C capacity factor를 반영해 35°C half target을 산정한다. |

실수 방지: 이 helper의 반환값을 CSPF 계산 입력으로 자동 대체하면 안 된다. 시험값과 설계 추천값의 역할을 분리해야 한다.

## 8. Test Strategy

| Test | Input | Expected |
| --- | --- | --- |
| golden sample | declared 6000 W, 35_full 6035.8/1641.4, 35_half 3420.4/679.4, 29_min 1759.6/201.7 | CSPF 6.504 |
| rounding test | .5 경계 capacity/power | ROUND_HALF_UP 결과 |
| missing declared capacity | `declared_capacity = None` | ValueError |
| method separation | `power_interpolation_method` changed | golden mismatch should be detected |
| BL cap branch | artificially low max capacity | cooling output capped |
| recommendation helper | positive full/min capacity | returns T_min, T_mid, target half capacity |

## 9. Prompt Snippets for Agent

Agent 재사용 프롬프트:

> AGENTS.md와 docs/DOCS_GUIDELINES.md를 먼저 읽는다. KS C 9306 계산을 수정하기 전에 docs/iso16358/iso16358_dev_notes.md와 docs/iso16358/regions/ks_c_9306/ks_c_9306_dev_notes.md를 확인한다. ISO 공통 문서에는 KS 전용 내용을 추가하지 않는다. KS 변경 후 golden sample에서 CSPF 6.504, annual cooling 1943.798 kWh, annual power 298.852 kWh가 유지되는지 확인한다.

## 10. References

| Source | Usage |
| --- | --- |
| [ks_c_9306_notes.md](./ks_c_9306_notes.md) | KS 계산 구조와 golden sample |
| [ks_c_9306_glossary.md](./ks_c_9306_glossary.md) | KS 고유 용어와 데이터 위치 |
| [../../iso16358_dev_notes.md](../../iso16358_dev_notes.md) | 공통 엔진 구현 지침 |
| `data/region_configs/korea.json` | KS region configuration |
| `core/calculator_iso16358.py` | 구현 동작 확인 |
