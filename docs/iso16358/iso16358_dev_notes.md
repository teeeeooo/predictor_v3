# ISO16358 Dev Notes

## 1. Purpose

이 문서는 ISO 16358 기반 CSPF 공통 엔진을 수정하거나 검증할 때 구현자가 따라야 할 순서, 실수 방지 규칙, 디버깅 방법, 테스트 전략을 정리한다. 용어 본문은 이 문서에 중복 작성하지 않으며, 상세 용어는 [iso16358_glossary.md](./iso16358_glossary.md)를 참조한다.

## 2. Top Implementation Pitfalls

| Pitfall | Symptom | Cause | Prevention | Reference |
| --- | --- | --- | --- | --- |
| building load 기준 혼동 | CSPF가 region별로 크게 달라진다. | measured reference와 declared capacity를 같은 방식으로 처리한다. | `building_load_source`를 먼저 확인하고 분기한다. | ISO 16358-1:2013 Chapter 6 |
| 시험점 누락 | `ValueError` 또는 비어 있는 interpolation 결과가 발생한다. | configuration의 `measure` point가 입력에 없다. | `points`에서 `measure` 항목을 검증한다. | ISO 16358-1:2013 Clause 6.4~6.7 |
| 파생점 순서 오류 | default point가 unresolved 상태로 남는다. | derived rule source가 아직 만들어지지 않았다. | default point는 반복 pass로 해석하고 unresolved 목록을 에러로 노출한다. | Project implementation |
| 온도 보간과 부하 보간 혼동 | 중간 부하 소비전력이 과소/과대 계산된다. | temperature interpolation과 capacity-range interpolation을 같은 단계로 취급한다. | 먼저 온도별 load type 성능선을 만들고, 이후 Lc 위치에 따라 power를 정한다. | ISO 16358-1:2013 Chapter 6 |
| PLF 0 또는 음수 | 저부하 bin에서 전력값이 비정상적으로 커진다. | Cd가 크거나 X가 낮아 PLF가 0에 접근한다. | PLF 최소 방어값을 유지하고 Cd 변경 시 경계 테스트를 수행한다. | ISO 16358-1:2013 Chapter 6 |
| zero load temperature 오류 | division by zero가 발생한다. | `t_100_load`와 `t_0_load`가 같다. | configuration load temperature를 로딩 후 검증한다. | Project implementation |

## 3. Correct Calculation Order

1. region configuration을 로드한다.
2. metadata key를 계산 대상에서 제거한다.
3. `measure` point가 모두 입력되었는지 검증한다.
4. `default` point를 derived rule로 생성한다.
5. `building_load_source`에 따라 L_c_ref를 결정한다.
6. `t_100_load - t_0_load`가 0인지 확인한다.
7. bin-hour를 순회하며 `nj <= 0`인 bin을 제외한다.
8. 각 bin에서 BL(tj)를 계산한다.
9. 각 load type의 capacity/power를 outdoor temperature 기준으로 보간 또는 외삽한다.
10. Lc가 최저 용량 이하인지, 최고 용량 초과인지, 중간 용량 범위인지 판단한다.
11. 각 bin의 cooling output과 power에 `nj`를 곱해 누적한다.
12. total power가 0 이하이면 0 결과를 반환하고, 아니면 CSPF를 산정한다.

## 4. Data Model Notes

| Key | Meaning | Implementation note |
| --- | --- | --- |
| `t_100_load` | 100% cooling load 기준 온도 | BL(tj) 직선의 상단 기준이다. |
| `t_0_load` | 0% cooling load 기준 온도 | BL(tj) 직선의 하단 기준이다. |
| `Cd` | degradation coefficient | PLF 보정에만 사용한다. |
| `building_load_source` | 기준 부하 출처 | `measured` 또는 `declared`를 구분한다. |
| `reference_point` | measured 기준 부하 point | `building_load_source = measured`일 때 사용한다. |
| `round_test_values` | 시험값 반올림 여부 | region-specific 규칙이므로 공통 기본값은 false이다. |
| `power_interpolation_method` | 중간 용량 범위 power 계산법 | 기본값은 capacity-linear이며 지역 확장에서 바꿀 수 있다. |
| `points` | point별 measured/default 지정 | point 이름은 temperature와 load type을 포함한다. |
| `derived_rules` | default point 생성 규칙 | source, capacity factor, power factor를 사용한다. |
| `bin_hours` | outdoor temperature와 hour | seasonal accumulation의 시간 가중치이다. |

## 5. Interpolation / Extrapolation Rules

| Rule | Behavior | Debug focus |
| --- | --- | --- |
| 동일 load type에 1개 point만 있을 때 | 해당 capacity/power를 그대로 사용한다. | point 수가 의도된 것인지 확인한다. |
| tj가 최저 시험온도 이하일 때 | 가장 낮은 두 temperature point로 외삽한다. | 외삽된 capacity가 음수로 내려가지 않는지 확인한다. |
| tj가 최고 시험온도 이상일 때 | 가장 높은 두 temperature point로 외삽한다. | 고온 bin에서 최고 용량 초과 처리와 함께 확인한다. |
| tj가 시험온도 사이일 때 | 해당 구간의 두 point로 선형 보간한다. | temperature sorting과 point key parsing을 확인한다. |
| Lc가 capacity 사이일 때 | 기본적으로 capacity 기준 power 선형 보간을 적용한다. | region-specific method가 켜져 있는지 확인한다. |

## 6. Debugging Checklist

| Step | Check | Expected |
| --- | --- | --- |
| 1 | configuration path | 파일이 존재해야 한다. |
| 2 | required measured points | `points`의 `measure` key가 모두 입력되어야 한다. |
| 3 | derived points | 모든 `default` point가 resolved 되어야 한다. |
| 4 | L_c_ref | measured 또는 declared source가 region 의도와 일치해야 한다. |
| 5 | load temperature | `t_100_load`와 `t_0_load`가 달라야 한다. |
| 6 | bin loop | `nj <= 0`인 bin은 누적하지 않아야 한다. |
| 7 | PLF branch | Lc가 lowest capacity 이하일 때만 Cd가 적용되어야 한다. |
| 8 | cap branch | Lc가 highest capacity보다 크면 cooling output이 highest capacity로 제한되어야 한다. |
| 9 | accumulation | Wh 누적 후 kWh로 변환되어야 한다. |

## 7. Test Strategy

| Test type | Purpose | Required cases |
| --- | --- | --- |
| Unit test | point resolution과 interpolation을 독립 검증한다. | missing measured point, chained derived point, temperature extrapolation |
| Golden test | region sample 결과가 고정되는지 확인한다. | KS C 9306 golden sample |
| Boundary test | 분기 경계에서 값이 안정적인지 확인한다. | Lc <= lowest, Lc > highest, csec <= 0 |
| Configuration test | region key 변경이 의도대로 반영되는지 확인한다. | `building_load_source`, `power_interpolation_method`, `round_test_values` |

## 8. Prompt Snippets for Agent

Agent 재사용 프롬프트:

> AGENTS.md와 docs/DOCS_GUIDELINES.md를 먼저 읽는다. ISO16358 공통 엔진을 수정할 때는 docs/iso16358/iso16358_notes.md, docs/iso16358/iso16358_dev_notes.md, docs/iso16358/iso16358_glossary.md를 확인한다. 국가별 특이사항은 ISO 공통 문서에 넣지 말고 docs/iso16358/regions/<region>/ 문서에 분리한다. 계산 변경 후에는 region golden sample과 branch boundary test를 실행한다.

## 9. References

| Source | Usage |
| --- | --- |
| [iso16358_notes.md](./iso16358_notes.md) | 공통 계산 구조와 mapping |
| [iso16358_glossary.md](./iso16358_glossary.md) | 용어와 schema SSOT |
| `core/calculator_iso16358.py` | 구현 동작 확인 |
| `data/region_configs/*.json` | region configuration 확인 |
