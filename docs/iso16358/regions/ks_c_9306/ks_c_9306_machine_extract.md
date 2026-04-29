# KS C 9306 Machine-Readable Extract Notes

## Source

This note records the 2026-04-30 extraction pass from the Korean Standards machine-readable endpoint.

| Item | Value |
| --- | --- |
| Standard | KSC9306 |
| reformNo | 19 |
| formType | STD |
| Initial URL | `https://standard.go.kr/KSCI/api/std/viewMachine.do?reformNo=19&tmprKsNo=KSC9306&formType=STD` |
| JSON endpoint | `https://standard.go.kr/KSCI/api/std/viewMachineNextPage.do?format=json` |
| POST fields used | `tmprKsNo=KSC9306`, `reformNo=19`, `formType=STD` |
| Temporary working folder | `.tmp_ks_machine/` |

The endpoint content includes generated recommendation blocks mixed into the body text. For implementation, use the clause numbers, tables, and formula images as source anchors; do not copy the mixed text directly into calculation logic.

## Extracted Sections

| Section | Text file | Formula/image assets |
| --- | --- | --- |
| E.2 | `.tmp_ks_machine/E_2.txt` | none extracted |
| E.3.2 | `.tmp_ks_machine/E_3_2.txt` | 9 images |
| E.3.2.1 | `.tmp_ks_machine/E_3_2_1.txt` | 6 images |
| E.3.2.2 | `.tmp_ks_machine/E_3_2_2.txt` | 15 images |
| E.3.2.3 | `.tmp_ks_machine/E_3_2_3.txt` | 14 images |
| E.3.2.4 | `.tmp_ks_machine/E_3_2_4.txt` | 13 images |
| E.3.2.5 | `.tmp_ks_machine/E_3_2_5.txt` | 21 images |

Embedded formula images were extracted from SVG wrappers into `.tmp_ks_machine/png/`. The formula PNGs are much more reliable than OCR for symbols and subscripts.

## HSPF Formula Image Map

The variable-capacity HSPF formula images in `E.3.2.3` map as follows:

| Image | Equation | Role |
| --- | --- | --- |
| `E_3_2_3_001.png` | E.2.20 | minimum heating capacity, non-frost region |
| `E_3_2_3_002.png` | E.2.21 | minimum heating capacity, frost region |
| `E_3_2_3_003.png` | E.2.22 | rated heating capacity, non-frost region |
| `E_3_2_3_004.png` | E.2.23 | rated heating capacity, frost region |
| `E_3_2_3_005.png` | E.2.24 | intermediate heating capacity, non-frost region |
| `E_3_2_3_006.png` | E.2.25 | intermediate heating capacity, frost region |
| `E_3_2_3_007.png` | E.2.26 | maximum heating capacity |
| `E_3_2_3_008.png` | E.2.27 | minimum heating power, non-frost region |
| `E_3_2_3_009.png` | E.2.28 | minimum heating power, frost region |
| `E_3_2_3_010.png` | E.2.29 | rated heating power, non-frost region |
| `E_3_2_3_011.png` | E.2.30 | rated heating power, frost region |
| `E_3_2_3_012.png` | E.2.31 | intermediate heating power, non-frost region |
| `E_3_2_3_013.png` | E.2.32 | intermediate heating power, frost region |
| `E_3_2_3_014.png` | E.2.33 | maximum heating power |

The operating-selection formulas in `E.3.2.5` cover E.2.36 through E.2.40. Equation E.2.36 was manually confirmed from the source image and user-provided transcription:

```text
P_h(t_j) = P_h23(t_j) = P_h3(t_g) + (P_h2(t_b) - P_h3(t_g)) * (t_j - t_g) / (t_b - t_g)
```

where `P_h2(t_b)` is Equation E.2.30 evaluated at `t_b`, and `P_h3(t_g)` is Equation E.2.33 evaluated at `t_g`.

## Table E.5 Extract

The machine-readable HTML table under E.3.2.1 exposes the HSPF correction factors needed for implementation.

| Type | Item | Capacity relation | Power relation |
| --- | --- | --- | --- |
| fixed capacity | low-temperature heating | `Phi_hr(-7.0) = 0.601 * Phi_hr` | `P_h(-7.0) = 0.801 * P_h` |
| 2-stage variable | low-temperature minimum | `Phi_hr1(-7.0) = 0.601 * Phi_hr1` | `P_h1(-7.0) = 0.801 * P_h1` |
| 2-stage variable | low-temperature rated | `Phi_hr2(-7.0) = 0.601 * Phi_hr2` | `P_h2(-7.0) = 0.801 * P_h2` |
| variable capacity | defrost no-frost | `Phi_nof = 1.12 * Phi_def` | `P_nof = 1.06 * P_def` |
| variable capacity | low-temperature minimum | `Phi_hr1(-7.0) = 0.601 * Phi_hr1` | `P_h1(-7.0) = 0.801 * P_h1` |
| variable capacity | low-temperature intermediate | `Phi_hrm(-7.0) = 0.601 * Phi_hrm` | `P_hm(-7.0) = 0.801 * P_hm` |
| variable capacity | low-temperature rated | `Phi_hr2(-7.0) = 0.601 * Phi_hr2` | `P_h2(-7.0) = 0.801 * P_h2` |
| variable capacity | low-temperature maximum | measured `Phi_hr3(-7.0)` | measured `P_h3(-7.0)` |
| all listed heating types | degradation coefficient | `C_D = 0.25` | `C_D = 0.25` |

## Implementation Implications

- Production HSPF is now feasible from the machine-readable source plus formula images.
- E.2.20 through E.2.33 still need exact manual transcription from PNG before replacing the current simplified variable-capacity HSPF path.
- Table E.5 removes the previous blocker around derived low-temperature and no-frost values.
- The current golden sample has only high, half, and minimum measured points; production schema should keep stage-specific standard, defrost, no-frost, low-temperature, and maximum points distinct.
- If a temporary golden adapter remains necessary, it should be explicitly marked as non-production fallback.

## Remaining Verification Before Core Changes

1. Manually transcribe E.2.20 through E.2.33 from `E_3_2_3_001.png` through `E_3_2_3_014.png`.
2. Manually transcribe E.2.37 through E.2.40 from the `E.3.2.5` images.
3. Reconcile the existing `calculate_hspf()` input schema with the full KS stage-specific inputs.
4. Keep `calc_heating_building_load` unchanged unless a separate golden HSTL regression proves it is wrong.
5. Run HSPF golden, HSPF smoke, and CSPF golden/regression tests after implementation.


## HSPF formula

1. 난방 능력 (Heating Capacity) 수식
가변 용량형 에어컨의 온도 조건별 난방 능력 $\Phi_{hr}$ 수식입니다.
E.2.20 (최소 운전, 무착상):
$$\Phi_{hr}(t_j) = \Phi_{hr1}(t_j) = \Phi_{hr1(-7.0)} + \frac{\Phi_{hr1} - \Phi_{hr1(-7.0)}}{7 - (-7.0)} (t_j - (-7.0))$$
E.2.21 (최소 운전, 착상 - 반영 완료):
$$\Phi_{hr}(t_j) = \Phi_{def1}(t_j) = \Phi_{hr1(-7.0)} + \frac{\Phi_{hr1(2)} \cdot (\frac{\Phi_{def}}{\Phi_{nof}}) - \Phi_{hr1(-7.0)}}{2 - (-7.0)} (t_j - (-7.0))$$
E.2.22 (정격 운전, 무착상):
$$\Phi_{hr}(t_j) = \Phi_{hr2}(t_j) = \Phi_{hr2(-7.0)} + \frac{\Phi_{hr2} - \Phi_{hr2(-7.0)}}{7 - (-7.0)} (t_j - (-7.0))$$
E.2.23 (정격 운전, 착상 - 패턴 정규화):
$$\Phi_{hr}(t_j) = \Phi_{def2}(t_j) = \Phi_{hr2(-7.0)} + \frac{\Phi_{hr2(2)} \cdot (\frac{\Phi_{def}}{\Phi_{nof}}) - \Phi_{hr2(-7.0)}}{2 - (-7.0)} (t_j - (-7.0))$$
E.2.24 (중간 운전, 무착상):
$$\Phi_{hr}(t_j) = \Phi_{hrm}(t_j) = \Phi_{hrm(-7.0)} + \frac{\Phi_{hrm} - \Phi_{hrm(-7.0)}}{7 - (-7.0)} (t_j - (-7.0))$$
E.2.25 (중간 운전, 착상 - 패턴 정규화):
$$\Phi_{hr}(t_j) = \Phi_{defm}(t_j) = \Phi_{hrm(-7.0)} + \frac{\Phi_{hrm(2)} \cdot (\frac{\Phi_{def}}{\Phi_{nof}}) - \Phi_{hrm(-7.0)}}{2 - (-7.0)} (t_j - (-7.0))$$
E.2.26 (최대 운전):
$$\Phi_{hr}(t_j) = \Phi_{hr3}(t_j) = \Phi_{hr3(-7.0)} + \frac{\Phi_{def} - \Phi_{hr3(-7.0)}}{2 - (-7.0)} (t_j - (-7.0))$$

2. 난방 소비 전력 (Heating Power Input) 수식
온도 조건별 난방 소비 전력 $P_h$ 수식입니다.
E.2.27 (최소 운전, 무착상):
$$P_h(t_j) = P_{h1}(t_j) = P_{h1(-7.0)} + \frac{P_{h1} - P_{h1(-7.0)}}{7 - (-7.0)} (t_j - (-7.0))$$
E.2.28 (최소 운전, 착상 - 패턴 정규화):
$$P_h(t_j) = P_{def1}(t_j) = P_{h1(-7.0)} + \frac{P_{h1(2)} \cdot (\frac{P_{def}}{P_{nof}}) - P_{h1(-7.0)}}{2 - (-7.0)} (t_j - (-7.0))$$
E.2.29 (정격 운전, 무착상):
$$P_h(t_j) = P_{h2}(t_j) = P_{h2(-7.0)} + \frac{P_{h2} - P_{h2(-7.0)}}{7 - (-7.0)} (t_j - (-7.0))$$
E.2.30 (정격 운전, 착상 - 반영 완료):
$$P_h(t_j) = P_{def2}(t_j) = P_{h2(-7.0)} + \frac{P_{h2(2)} \cdot (\frac{P_{def}}{P_{nof}}) - P_{h2(-7.0)}}{2 - (-7.0)} (t_j - (-7.0))$$
E.2.31 (중간 운전, 무착상):
$$P_h(t_j) = P_{hm}(t_j) = P_{hm(-7.0)} + \frac{P_{hm} - P_{hm(-7.0)}}{7 - (-7.0)} (t_j - (-7.0))$$
E.2.32 (중간 운전, 착상 - 패턴 정규화):
$$P_h(t_j) = P_{defm}(t_j) = P_{hm(-7.0)} + \frac{P_{hm(2)} \cdot (\frac{P_{def}}{P_{nof}}) - P_{hm(-7.0)}}{2 - (-7.0)} (t_j - (-7.0))$$
E.2.33 (최대 운전, 착상 - 반영 완료):
$$P_h(t_j) = P_{defm}(t_j) = P_{hm(-7.0)} + \frac{P_{hm(2)} \cdot (\frac{P_{def}}{P_{nof}}) - P_{hm(-7.0)}}{2 - (-7.0)} (t_j - (-7.0))$$
참고: 작성해주신 E.2.33 수식은 '중간 운전(m)'의 변수를 사용하고 있습니다. 파이썬 로직 구현 시, 규격상 최대 운전 하드코딩 변수는 $P_{h3}$ 및 $P_{def}$를 주로 사용하므로 (예: $P_{h3(-7.0)}$ ), 실제 변수 맵핑 시 최대 운전 인덱스(3)와 중간 운전 인덱스(m)가 섞이지 않도록 한 번만 확인해 주시면 완벽할 것 같습니다.

3. 3점식 적용 시 난방 소비 전력 수식 (건물 부하 교차 구간)

E.2.37 (무착상, 최소 운전 능력 < 건물 부하 $\le$ 중간 운전 능력):
$$P_h(t_j) = P_{hm}(t_c) + \frac{P_{h1}(t_c) - P_{hm}(t_c)}{t_c - t_{e}} (t_j - t_c)$$
E.2.38 (무착상, 중간 운전 능력 < 건물 부하 $\le$ 정격 운전 능력):
$$P_h(t_j) = P_{h2}(t_a) + \frac{P_{hm}(t_c) - P_{h2}(t_a)}{t_c - t_a} (t_j - t_a)$$
E.2.39 (착상, 최소 운전 능력 < 건물 부하 $\le$ 중간 운전 능력):
$$P_h(t_j) = P_{hm}(t_f) + \frac{P_{h1}(t_d) - P_{hm}(t_f)}{t_d - t_f} (t_j - t_f)$$
E.2.40 (착상, 중간 운전 능력 < 건물 부하 $\le$ 정격 운전 능력):
$$P_h(t_j) = P_{h2}(t_b) + \frac{P_{hm}(t_f) - P_{h2}(t_b)}{t_f - t_b} (t_j - t_b)$$