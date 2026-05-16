# AHRI 210/240-2026 HSPF2 구현 상세

## 개요
- 파일: core/calculator_ahri_hspf2.py
- 적용 규격: AHRI 210/240-2026
- 대상: non-ducted, single-split, variable-capacity, air-to-air heat pump
- 우선 지역: Region IV

---

## 입력 스키마

### required
- H01: 62°F Low speed (capacity Btu/h, power W)
- H11: 47°F Low speed
- H1N: 47°F Nominal speed
- H2Int: 35°F Intermediate speed
- H32: 17°F Full speed
- A2: 95°F Cooling (건물 부하선 기준)

### optional
- H12: 47°F Full speed
- H22: 35°F Full speed
- H42: 5°F Full speed

### kwargs 주요 항목
- h1n_same_speed_as_h3: bool (default False)
- does_comp_limit_min_spd: bool (default False)
- unit_type: "split" 또는 "single_package" (default "split")
- fdef_override: float (default 1.0)
- defrost_t_test_minutes: float (fdef_override 없을 때 필수)
- defrost_t_max_minutes: float (fdef_override 없을 때 필수)
- t_off: float (default -40.0°F)
- t_on: float (default -40.0°F)
- c_d_heating: float (default 0.25)

---

## H1Full_calc 결정 로직

H12 tested → Eq.11.181~11.182: q_H1Full_calc = q_H1Full (실측값)
H12 없음 + h1n_same_speed=True → Eq.11.183~11.184: q_H1Full_calc = q_H1Nom
H12 없음 + h1n_same_speed=False → Eq.11.185~11.186:
  q_H1Full_calc = q_H3Full × (1 + 30 × CSF)
  P_H1Full_calc = P_H3Full × (1 + 30 × PSF)
  CSF = 0.0204/°F (split), 0.0262/°F (single package)
  PSF = 0.00455/°F (all)

---

## H22(q_H2Full) 결정 로직

H22 tested → 실측값 사용
H22 없음 → Eq.11.44/11.50:
  q_H2Full = 0.90 × {q_H3Full + 0.6 × (q_H1Full_calc - q_H3Full)}
  P_H2Full = 0.985 × {P_H3Full + 0.6 × (P_H1Full_calc - P_H3Full)}

---

## Full Speed bin 용량/전력

tj ≥ 45°F (tOBO): Eq.11.209~11.210
  q_Full = {q_H3Full + (q_H1Full_calc - q_H3Full) × (tj-17)/(47-17)} × (q_H1Nom/q_H1Full_calc)

17 < tj < 45°F: Eq.11.213~11.214
  q_Full = q_H3Full + (q_H2Full - q_H3Full) × (tj-17)/(35-17)

H4Full 없음, tj ≤ 17°F: Eq.11.211~11.212
  q_Full = q_H3Full + (q_H1Full_calc - q_H3Full) × (tj-17)/(47-17)

H4Full 있음, 5 < tj ≤ 17°F: Eq.11.215~11.216
  q_Full = q_H4Full + (q_H3Full - q_H4Full) × (tj-5)/(17-5)

H4Full 있음, tj ≤ 5°F: Eq.11.217~11.218
  q_Full = q_H4Full + (q_H1Full_calc - q_H3Full) × (tj-5)/(47-17)

---

## Low Speed bin 용량/전력

non-minimum-speed-limiting (Eq.11.187~11.188):
  q_Low = q_H1Low + (q_H0Low - q_H1Low) × (tj-47)/(62-47)

minimum-speed-limiting (Eq.11.189~11.194):
  tj ≥ 47: H0Low~H1Low 보간
  35 ≤ tj < 47: H2Int~H1Low 보간
    q_Low = q_H2Int + (q_H1Low - q_H2Int) × (tj-35)/(47-35)
  tj < 35: q_Low = q_H,Int(tj) (intermediate 경로 직통)

---

## Intermediate Speed slope (Eq.11.199~11.204)

q_Int(tj) = q_H2Int + M_Hq × (tj - 35)
P_Int(tj) = P_H2Int + M_HE × (tj - 35)

N_Hq = (q_H2Int - q_Low(35)) / (q_H2Full - q_Low(35))
M_Hq = (q_H0Low - q_H1Low)/(62-47) × (1-N_Hq) + (q_H2Full - q_H3Full)/(35-17) × N_Hq

q_Low(35): Eq.11.187 기준
q_H2Full: H22 tested 또는 Eq.11.44 fallback

---

## Case 분기

Case I: BL ≤ q_Low → Low speed cycling
  PLF = 1 - Cd × (1 - HLF)
  E(tj)/N = P_Low × HLF / PLF × nj/N

Case II: q_Low < BL < q_Full → COP_Int-Bin 보간
  E(tj)/N = BL / (3.412 × COP_Int-Bin) × δ_Int-Bin × nj/N
  COP_Int-Bin: Eq.11.197 또는 Eq.11.198

Case III: BL ≥ q_Full → Full speed + resistance heat
  E(tj)/N = P_Full × nj/N
  RH(tj)/N = (BL - q_Full) / 3.412 × nj/N

---

## Defrost 처리

fdef_override 있음 (default 1.0):
  Fdef = fdef_override, Ttest/Tmax 입력 불필요

fdef_override 없음 + Ttest/Tmax 있음:
  Fdef = 1 + 0.03 × (1 - (Ttest-90)/(Tmax-90))  (Eq.11.107)
  Ttest = max(raw, 90), Tmax = min(raw, 720) clamp 적용

HSPF2 = sum(BL × nj/N) / (sum(E/N) + sum(RH/N)) × Fdef

---

## Golden Case 검증 결과

AHRI 공식 계산기 대비:

Case #1 (H12/H22 없음, Eq.11.185, A2=18120.3):
  우리 raw_hspf2: 9.447720 / AHRI: 9.448025 / diff: -0.0003

Case #2 (H12/H22 없음, Eq.11.185, A2=22420.0):
  우리 raw_hspf2: 8.821297 / AHRI: 8.821440 / diff: -0.0001

H22 tested (H22=44436/4414): rounded 9.52 pass
H12 tested (H12=23000/2308): rounded 9.47 pass
Eq.11.183 (h1n_same_speed=True): rounded 9.438 pass

---

## metadata trace 키 목록

summary["metadata"] 주요 키:
- h12_source: "tested" / "eq_11_183" / "eq_11_185"
- h22_source: "tested" / "eq_11_44_11_50"
- h22_high_anchor_capacity / h22_high_anchor_power
- h22_capacity / h22_power
- minimum_speed_limited: bool
- case_i_low_source: "eq_11_187_188" / "eq_11_189_194"
- t_off_used / t_on_used
- defrost.mode: "override" / "eq_11_107"
- defrost.fdef_used
- defrost.seasonal_defrost_multiplier_applied
