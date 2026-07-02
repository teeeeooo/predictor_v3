# EN14825 용어집

이 문서는 EN14825 SEER/SCOP 문서에서 사용하는 도메인 용어, 수식 기호, 코드 변수명 정의의 단일 용어 사전이다. 설계 엔지니어가 보는 물리적 의미와 Coding Agent 및 SW 엔지니어가 확인해야 하는 변수/스키마 정보를 분리하여 관리한다.

## 1. HVAC 설계 엔지니어용

| 용어 및 기호 | 한글명 | 근거 | 정의 및 설계상 의미 |
| --- | --- | --- | --- |
| SEER | 계절 냉방 효율 | EN14825:2012 Clause 6.1 | 연간 냉방 수요를 냉방 운전 에너지와 보조전력 에너지 합으로 나눈 지표다. 냉방 부분부하 효율과 비활성 모드 전력 관리가 함께 반영된다. |
| SEERon | 활성 냉방 계절 효율 | EN14825:2012 Clause 6.3 | 냉방 활성 운전 중 외기온 bin별 부분부하 효율만 반영한 지표다. 중간 외기온에서 안정적으로 높은 효율을 유지하는 능력이 중요하다. |
| SCOP | 계절 난방 효율 | EN14825:2012 Clause 7.1 | 기준 연간 난방 수요를 난방 운전 에너지와 보조전력 에너지 합으로 나눈 지표다. 저온 용량, 부분부하 효율, 보조 전기열 사용량이 함께 반영된다. |
| SCOPon | 활성 난방 계절 효율 | EN14825:2012 Clause 7.3, Equation 9 | 난방 활성 운전 중 bin별 난방 부하, 히트펌프 담당 열량, 보조 전기열을 반영한 지표다. 저온에서 용량 부족이 발생하면 빠르게 낮아진다. |
| Pdesignc | 설계 냉방 부하 | EN14825:2012 Clause 6.2 | 기준 연간 냉방 수요를 산출하는 대표 냉방 용량이다. 냉방 부하선과 A/B/C/D 조건의 상대 위치를 결정한다. |
| Pdesignh | 설계 난방 부하 | EN14825:2012 Clause 7.2 | 기준 연간 난방 수요를 산출하는 대표 난방 용량이다. 외기온별 난방 부하선과 보조열 발생 여부를 좌우한다. |
| Tdesignc | 냉방 설계온도 | EN14825:2012 Table 2, Clause 6.4 | 냉방 부하선의 상단 기준 온도다. 공기 대 공기 장비의 대표 A 조건은 35 °C다. |
| Tdesignh | 난방 설계온도 | EN14825:2012 Table 37, Clause 7.2 | 기후별 난방 부하선의 저온 기준이다. warmer, average, colder 기후에 따라 부하선 기울기가 달라진다. |
| TOL | 운전 한계 온도 | EN14825:2012 Clause 5.2, Clause 7.4 | Operation limit temperature의 약어다. 이 온도 아래에서는 히트펌프 난방 용량을 0으로 보고 보조 전기열이 부하를 담당한다. |
| Tbiv | 이원점 온도 | EN14825:2012 Clause 5.2, Clause 7.4 | Bivalent temperature의 약어다. 히트펌프 용량과 난방 부하가 만나는 기준 온도이며, 보조열 개입 구간 판단에 중요하다. |
| Tj | bin 외기온 | EN14825:2012 Table 36, Table 37 | 계절 계산에서 사용하는 외기온 대표값이다. 각 온도는 bin hour와 결합되어 계절 부하와 에너지 합산에 들어간다. |
| hj | bin 시간 | EN14825:2012 Table 36, Table 37 | 특정 외기온 bin이 계절 중 지속되는 시간이다. 빈 시간이 큰 구간의 효율 개선은 계절 지표에 더 크게 반영된다. |
| Pc(Tj) | bin별 냉방 부하 | EN14825:2012 Clause 6.4, Table 36 | 외기온 Tj에서 요구되는 냉방 부하다. 냉방 부분부하 효율 보간과 SEERon 계산의 기준이 된다. |
| Ph(Tj) | bin별 난방 부하 | EN14825:2012 Clause 7.2, Table 37 | 외기온 Tj에서 요구되는 난방 부하다. 히트펌프 용량선보다 커지면 부족분이 보조 전기열로 넘어간다. |
| EERDC | 선언 냉방 효율 | EN14825:2012 Clause 6.4 | declared capacity와 declared power로 계산되는 냉방 시험점 효율이다. 부분부하 보정 전 기준값이다. |
| EERPL | 부분부하 냉방 효율 | EN14825:2012 Clause 6.3, Clause 6.4 | 냉방 부분부하 조건에 적용되는 효율이다. cycling 보정 또는 용량 제어 단계 보간의 결과로 계절 합산에 사용된다. |
| COPDC | 선언 난방 성능계수 | EN14825:2012 Clause 7.4 | declared capacity와 declared power로 계산되는 난방 시험점 성능계수다. 부분부하 보정 전 기준값이다. |
| COPPL | 부분부하 난방 성능계수 | EN14825:2012 Clause 7.3, Clause 7.4 | 난방 부분부하 조건에 적용되는 성능계수다. SCOPon denominator를 직접 결정한다. |
| Cd | 성능 저하 계수 | EN14825:2012 Clause 6.4.2.1, Clause 7.4.2.1 | Degradation coefficient의 약어다. 장비 용량이 요구 부하보다 커서 cycling이 생길 때 효율을 낮추는 계수이며 기본값은 0.25다. |
| CR | 용량비 | EN14825:2012 Clause 6.4.2.1, Clause 7.4.2.1 | Capacity ratio의 약어다. 요구 부하를 선언 용량으로 나눈 값이며 cycling 손실 계산에 사용된다. |
| elbu(Tj) | 보조 전기 히터 부하 | EN14825:2012 Equation 9 | 난방 부하 중 히트펌프가 담당하지 못한 열량이다. 전기 저항열처럼 작용하므로 SCOP를 크게 낮출 수 있다. |
| Pto | thermostat-off 전력 | EN14825:2012 Annex D Table D.1, Table D.2 | 온도조절기가 운전을 요구하지 않는 상태의 전력이다. 긴 시간과 곱해져 계절 에너지에 누적된다. |
| Psb | standby 전력 | EN14825:2012 Annex D Table D.1, Table D.2 | 대기 모드 전력이다. 작은 값이어도 계절 시간 가중치 때문에 최종 지표에 영향을 준다. |
| Pck | crankcase heater 전력 | EN14825:2012 Annex D Table D.3, Table D.4 | 크랭크케이스 히터 전력이다. 냉매 보호 목적과 계절 에너지 손실 사이의 균형이 필요하다. |
| Poff | off-mode 전력 | EN14825:2012 Annex D Table D.1, Table D.2 | 꺼짐 모드 전력이다. 장비 유형과 계절 운전 시간에 따라 최종 지표에 반영된다. |
| Hce | 등가 냉방 활성 시간 | EN14825:2012 Annex D Table D.1 | 기준 연간 냉방 수요를 계산하는 시간이다. 공기 대 공기 12 kW 이하 장비의 현재 기준은 350 h다. |
| Hhe | 등가 난방 활성 시간 | EN14825:2012 Annex D Table D.2 | 기준 연간 난방 수요를 계산하는 시간이다. 기후 조건에 따라 값이 달라진다. |

## 2. Coding Agent 및 SW 엔지니어용

| 코드 변수명 또는 키 | 데이터 타입 | 위치 | 정의 및 구현상 주의 |
| --- | --- | --- | --- |
| `calculate_seer()` | function | `core/calculators/standards/en14825.py` | EN14825 SEER 생산 entry point다. A/B/C/D 선언 운전점, Pdesignc, 보조전력을 받아 SEER와 SEERon을 반환한다. |
| `calculate_scop()` | function | `core/calculators/standards/en14825.py` | EN14825 SCOP 생산 entry point다. A/B/C/D/TOL/Tbiv 선언 운전점, Pdesignh, 기후, 보조전력을 받아 SCOP와 SCOPon을 반환한다. |
| `test_points["A"..."D"]` | dict 또는 tuple | SEER/SCOP input schema | 냉방과 난방의 선언 시험점이다. capacity와 power는 0보다 커야 한다. |
| `test_points["TOL"]` | dict 또는 tuple | SCOP input schema | TOL 선언 운전점이다. `TOL <= Tbiv`와 기후별 TOL 제한을 만족해야 한다. |
| `test_points["Tbiv"]` | dict 또는 tuple | SCOP input schema | Tbiv 선언 운전점이다. 기후별 Tbiv 제한을 만족해야 한다. |
| `capacity` | number | test point dict | 선언 용량 kW다. tuple 입력에서는 첫 번째 값으로 해석된다. |
| `power` | number | test point dict | 선언 소비전력 kW다. tuple 입력에서는 두 번째 값으로 해석된다. |
| `temp_c` | number | SCOP point dict | 선택적 운전점 온도다. 없으면 A/B/C/D는 schema 기본 온도, TOL/Tbiv는 별도 입력 또는 기후별 기본값을 사용한다. |
| `p_design_c` | number | SEER input schema | Pdesignc kW다. 0보다 커야 한다. |
| `t_design_c` | number | SEER input schema | Tdesignc °C다. 기본 35 °C이며 16 °C는 부하선 분모가 0이 되므로 금지된다. |
| `p_design_h` | number | SCOP input schema | Pdesignh kW다. 0보다 커야 한다. |
| `climate` | string | SCOP input schema | `average`, `warmer`, `colder` 중 하나로 정규화된다. 일부 alias는 허용된다. |
| `tbiv_temp_c` | number | SCOP input schema | 선택적 Tbiv 온도 °C다. 없으면 기후별 최대값을 사용한다. |
| `tol_temp_c` | number | SCOP input schema | 선택적 TOL 온도 °C다. 없으면 기후별 최대값을 사용한다. |
| `p_to`, `p_sb`, `p_ck`, `p_off` | number | SEER/SCOP input schema | 보조전력 kW다. W가 아니라 kW로 입력해야 한다. |
| `cd` | number | SEER/SCOP input schema | Cd 값이다. 기본값은 0.25다. |
| `appliance_type` | string | SCOP input schema | Annex D 운전 시간 선택에 사용된다. 현재 기본 경로는 `reversible`이다. |
| `seer` | number | SEER return dict | 최종 계절 냉방 효율이다. |
| `seer_on` | number | SEER return dict | 활성 냉방 계절 효율이다. |
| `qc_kwh` | number | SEER return dict | 기준 연간 냉방 수요다. |
| `scop`, `SCOP` | number | SCOP return dict | 최종 계절 난방 효율이다. 두 키는 현재 반환 호환성을 위해 함께 존재한다. |
| `scop_on` | number | SCOP return dict | 활성 난방 계절 효율이다. |
| `qh_kwh` | number | SCOP return dict | 기준 연간 난방 수요다. |
| `active_kwh` | number | SCOP return dict | 활성 난방 운전 에너지다. |
| `standby_kwh` | number | SCOP return dict | Annex D 보조 운전 모드 에너지다. |
| `total_kwh` | number | SCOP return dict | 활성 난방 에너지와 보조 운전 모드 에너지의 합이다. |
| `bin_details` | list | SCOP return dict | bin별 난방 부하, 용량, COPPL, elbu, denominator 기여량, 운전 케이스를 담는다. |
| `unimplemented_notes` | list 또는 string | SCOP return dict | 현재 구현 제한과 미지원 범위 설명이다. |
| `data/region_configs/en14825_scop.json` | JSON | project data | Table 37 난방 bin, 기후별 Tdesignh, TOL/Tbiv 제한, Annex D 운전 시간을 담는다. 문서 작업에서는 수정하지 않는다. |
