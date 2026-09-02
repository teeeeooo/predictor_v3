# predictor_v3 — AHRI 210/240 M SEER/HSPF Audit & One-Pass Implementation Design Specification

**Repository:** `teeeeooo/predictor_v3`
**Audit baseline:** `main @ ab9363dac7e9a01947fa3eccd1e9c1bd5042e217`
**Target:** Calculator에 AHRI 210/240 Appendix M 기반 `SEER` / `HSPF`를 추가하고, 기존 Appendix M1 기반 `SEER2` / `HSPF2`와 UI·domain owner를 명확히 분리한다.
**Primary implementation scope:** non-ducted, single-split, variable-speed compressor, air-to-air unit; HSPF는 Region IV / minimum DHR published rating.

---

## 1. 목적

현재 `predictor_v3` Calculator는 AHRI 계열에서 Appendix M1 기반 `SEER2` / `HSPF2`만 제공한다.

이번 작업의 최종 상태는 다음과 같다.

```text
Seasonal Efficiency Calculator
├─ ISO 16358
├─ EN14825
├─ AHRI 210/240 M
│  ├─ SEER
│  └─ HSPF
├─ AHRI 210/240 M1
│  ├─ SEER2
│  └─ HSPF2
└─ KS C 9306
```

기존 top-level `AHRI 210/240` 표시명은 `AHRI 210/240 M1`으로 변경한다.

새 top-level `AHRI 210/240 M`을 추가하고 하위 metric tab으로 `SEER`, `HSPF`를 제공한다.

이 작업은 단순한 UI label 추가가 아니다. Appendix M과 Appendix M1은 같은 시험점 이름을 일부 공유하지만 seasonal load, interpolation, DHR, bin aggregation 및 published rating semantics가 다르다. 따라서 M 계산을 M1 결과에 환산계수를 적용하거나 M1 seasonal engine의 mode flag로 구현해서는 안 된다.

## 1.1 2026-09-02 implementation resolution

구현 직전 formula/golden 재검증에서 HSPF 기준을 다음과 같이 확정했다.

- Appendix M HSPF production contract는 **AHRI Standard 210/240-2017 with Addendum 1**의 variable-speed Region IV 계산 경로를 따른다.
- Case II는 각 bin에서 minimum/intermediate/full COP를 capacity 기준으로 보간하는 2017 식을 사용한다. 과거 검토 중 관찰된 quadratic HSPF 경로와 `10.70` 결과는 이 feature의 production golden이 아니다.
- authoritative HSPF acceptance fixture는 `H01=3300/130`, `H11=2200/140`, `H1N=14000/1100`, `H2V=4900/360`, `H32=8200/890`, measured `H12=14000/1100`, `CDh=0.25`, `T_off=0°F`, `T_on=5°F`, non-demand-defrost `F_def=1.0`이다.
- 해당 fixture의 accepted aggregates는 heating load `4605.5625`, compressor input `359.486444...`, resistance input `80.695625...`, raw HSPF `10.462858...`, published HSPF `10.45`다.
- SEER acceptance fixture는 A2/B2/EV/B1/F1 입력에 대해 seasonal cooling numerator `5349.664336...`, energy denominator `296.402065...`, raw SEER `18.048674...`, published SEER `18.05`다.
- H42는 initial M production scope에서 제외한다. 현재 supported 2017 Region IV acceptance path에 필요하다는 충분한 근거 없이 M1 H42 behavior를 복제하지 않는다.
- Demand-defrost credit은 직접 rating override를 받지 않고 2017 Eq. 11.129–11.132의 `T_test`/`T_max`에서 M domain이 계산한다. demand-defrost가 아니면 `F_def=1.0`이다.

이 resolution은 아래 audit 단계의 open checkpoint 또는 더 넓은 current-regulation exploration보다 이번 implementation/acceptance에 우선한다.

## 1.2 2026-09-02 UI / batch follow-up

최초 implementation 확인 후 사용자 검토에서 다음 UI contract를 추가 확정했다.

- M HSPF의 canonical domain key는 그대로 유지하되 user-visible point header는 M1과 동일하게 `H2v`, `H1N(STD)`를 사용한다.
- M SEER result의 seasonal aggregate 표시는 `CSTL [Btu/h]`, `CSEC [W]`로 통일한다. 내부 result key와 계산 의미는 변경하지 않는다.
- 초기 설계의 **M-specific batch 제외**는 이 follow-up에서 supersede한다. M SEER와 HSPF 모두 기존 공용 `BatchMatrixTable` / `BatchDialogShell` / `BatchDialogHandle` lifecycle을 재사용하고, M 전용 matrix spec/row handler를 통해 기존 M application adapter/capability를 호출한다. M1 seasonal engine 또는 M1 product policy를 batch 계산 owner로 재사용하지 않는다.
- HSPF `Defrost Credit`은 editable override가 아니다. `Demand Defrost`가 꺼져 있으면 `F_def=1.0`, 켜져 있으면 `Defrost Test` / `Defrost Max` 입력을 M domain의 2017 식으로 계산하고 UI에는 계산된 값을 read-only로 표시한다.
- H12/H22 optional pair semantics는 batch에서도 single surface와 동일하게 `둘 다 blank=fallback`, `둘 다 populated=measured`, `half-filled=invalid`를 유지한다.

따라서 아래 본문의 초기 no-batch 범위 문구는 최초 audit 시점의 경계로 보존하되, production implementation과 acceptance에는 이 follow-up이 우선한다.

---

# 2. Audit 결론

## 2.1 `app_calculator.py`는 구현 owner가 아니다

현재 root `app_calculator.py`는 `apps.calculator.app:main`으로 위임하는 thin entrypoint다.

따라서 다음을 금지한다.

- `app_calculator.py`에 SEER/HSPF formula 추가
- `app_calculator.py`에 widget composition 추가
- `app_calculator.py`에 profile/dispatcher 선택 로직 추가

M 기능은 기존 calculator dependency direction 안에서 구현한다.

```text
Tk View
  ↓
Calculator Application Adapter
  ↓
Standard Calculation Capability
  ↓
Profile / Dispatcher
  ↓
Appendix M Domain Calculator
```

---

## 2.2 현재 architecture에서 보존해야 하는 dependency direction

Repository architecture owner가 정의하는 방향은 다음과 같다.

```text
Shell / Adapter / View
→ Controller / Application Service
→ Model / Domain
```

이번 기능에서는 이를 다음처럼 구체화한다.

### Domain / Model owner

담당:

- Appendix M SEER/HSPF 수식
- test-point domain validation
- bin calculation
- DHR selection
- raw metric 산출
- published metric rounding
- calculation trace/result data

금지:

- Tkinter import
- UI text parsing
- widget state
- CSV/file dialog
- clipboard
- UI-specific labels

### Capability / Dispatcher owner

담당:

- stable profile → calculator construction
- typed request → calculator method call
- capability/profile compatibility validation

금지:

- formula
- widget formatting
- application text validation

### Application adapter owner

담당:

- UI string → typed numeric request
- incomplete input handling
- field error mapping
- core result → UI summary model

금지:

- Appendix M formula
- DHR 계산
- seasonal bin calculation

### View owner

담당:

- widget construction
- user input
- auto calculation trigger
- result/detail rendering
- existing lifecycle owner 호출

금지:

- core formula 직접 실행
- DHR/load line 계산
- result schema 정책 정의
- 독자적인 window sizing/refit/measurement policy

---

# 3. 현재 M1 구현에서 반드시 보존할 contract

이번 작업은 M 추가 작업이지 M1 재설계 작업이 아니다.

다음 existing behavior는 유지한다.

## 3.1 Existing profile IDs

다음 ID를 rename하지 않는다.

```text
ahri_usa_seer2
ahri_usa_hspf2
```

## 3.2 Existing capability IDs

다음 ID를 rename하지 않는다.

```text
ahri210240.seer2
ahri210240.hspf2
```

## 3.3 Existing calculator public surface

현재 M1 facade와 public method signature를 변경하지 않는다.

대표적으로:

```text
AHRICalculator.calculate_seer2(...)
AHRIHSPF2Calculator.calculate_hspf2(...)
```

M 구현을 위해 M1 method에 Appendix M switch를 추가하지 않는다.

## 3.4 Existing M1 formula/result behavior

다음은 모두 regression-preserved behavior다.

- SEER2 variable-capacity building load
- M1 HP cooling `v_factor`
- existing SEER2 intermediate calculation
- HSPF2 Region IV context
- HSPF2 load line
- HSPF2 defrost behavior
- existing result dict keys
- existing application summary behavior
- existing batch behavior
- existing SEER2/HSPF2 product classifications

UI에서 바뀌는 M1 관련 user-visible contract는 top-level tab label 하나다.

```text
AHRI 210/240
→ AHRI 210/240 M1
```

하위 `SEER2`, `HSPF2` surface는 그대로 유지한다.

---

# 4. 표준 근거와 구현 authority

## 4.1 Primary external references

### DOE Appendix M

10 CFR Part 430 Subpart B Appendix M:

https://www.law.cornell.edu/cfr/text/10/appendix-M_to_subpart_B_of_part_430

Audit 단계의 broad primary reference다. 다만 **이번 production HSPF 계산 contract는 §1.1 implementation resolution에 따라 AHRI 210/240-2017 with Addendum 1이 우선**하며, DOE/current-Appendix-M 탐색 결과를 섞어 2017 HSPF 식을 변경하지 않는다. SEER 및 공통 Appendix M cross-check에는 계속 사용한다.

주요 범위:

- §3.6.4 — variable-speed compressor heating tests
- §3.9.2 — demand defrost credit
- §4.1.4 — variable-speed compressor SEER
- §4.2 — HSPF common aggregation
- §4.2.4 — variable-speed compressor HSPF
- Table 19 — cooling fractional bin hours
- Table 20 — heating regional bin data
- Table 21 — standardized DHR
- §4.4 — SEER/HSPF reporting rounding pointer

### AHRI SEER/HSPF Calculation App

https://seerhspf2.ahrianalytics.org/app_direct/seer2hspf2/

용도:

- Appendix M / M1 input topology cross-check
- supported variable-speed path 확인
- final SEER/HSPF golden parity
- optional point/flag behavior 확인

이 도구는 validation evidence이며 source formula authority를 대체하지 않는다.

### AHRI 210/240-2017

https://www.ahrinet.org/system/files/2023-06/AHRI_Standard_210-240_2017.pdf

특히 HSPF published rating의 DHR selection 확인에 사용한다.

표준 rating은 Region IV의 `DHR_min`에 해당하는 rating으로 취급한다.

### 10 CFR §429.16

https://www.law.cornell.edu/cfr/text/10/429.16

represented efficiency rounding context를 확인한다.

---

# 5. Scope

## 5.1 포함

### SEER

- Appendix M
- variable-speed compressor
- non-ducted
- single-split
- cooling seasonal calculation
- A2/B2/B1/EV/F1 test-point path
- cooling degradation coefficient
- Appendix M Table 19 bin calculation
- Appendix M variable-speed intermediate EER calculation
- raw SEER
- published SEER
- bin trace

### HSPF

- Appendix M
- variable-speed compressor heat pump
- non-ducted
- single-split
- Region IV
- DHR_min standard rating
- H01/H11/H1N/H2V/H32
- optional H12/H22
- optional low-temperature H42 support only if the exact Appendix M/AHRI-app path is confirmed during implementation
- CDh
- compressor cut-out/on behavior
- resistive supplementary heating
- demand-defrost credit
- raw HSPF
- published HSPF
- DHR trace
- bin trace

### Integration

- calculator profile
- dispatcher
- typed capability
- application adapter
- Tk calculator
- result/detail surface
- focused tests
- official-calculator golden evidence
- relevant AHRI owner documentation

---

## 5.2 제외

이번 구현에서 다음을 추가하지 않는다.

- single-speed compressor
- two-stage / dual-capacity compressor
- triple-capacity northern heat pump
- multi-split / multi-head / VRF
- multi-blower special paths
- ducted external-static-pressure correction
- coil-only adjustment
- mobile-home / space-constrained adjustment
- single-package product
- heat comfort controller
- HSPF Region I/II/III/V/VI
- M-specific batch calculator
- M → M1 또는 M1 → M 변환계수
- SEER2/HSPF2 formula refactor
- ML/Predictor integration
- root `app_calculator.py` 기능 확장
- 기존 M1 public ID rename
- unrelated AHRI cleanup

지원하지 않는 product/region을 UI placeholder로 노출하지 않는다.

---

# 6. UI design contract

## 6.1 Top-level navigation

최종 top-level notebook 순서는 다음을 목표로 한다.

```text
ISO 16358
EN14825
AHRI 210/240 M
AHRI 210/240 M1
KS C 9306
```

기존 M1 tab object의 내부 compatibility를 위해 현재 class/file의 무의미한 rename은 요구하지 않는다.

즉 기존 `Ahri210240Tab`을 대규모 rename하는 것보다:

- existing surface는 그대로 M1 기능을 소유
- `calculator_app`에서 표시 label만 `AHRI 210/240 M1`
- M은 sibling feature surface로 새 owner를 둔다

를 우선한다.

## 6.2 M top-level tab

`AHRI 210/240 M` 아래에 nested notebook:

```text
SEER
HSPF
```

를 둔다.

기존 M1 tab과 동일한 user-facing lifecycle 특성을 유지한다.

- `ScrollableFrame`
- nested notebook lifecycle
- visible-content measurement/refit
- nested tab change refit
- detail open/close refit
- scroll reset/containment

하지만 lifecycle logic을 복사하지 않는다.

기존 `apps/calculator/ui/lifecycle/` owner를 사용한다.

## 6.3 M feature package

M은 여러 책임을 갖기 때문에 새 UI 파일을 broad directory에 산발적으로 추가하지 않는다.

권장 owner boundary:

```text
apps/calculator/ui/ahri_m/
```

이 package 내부에 필요에 따라:

- top-level M tab
- SEER section/surface
- HSPF section/surface
- detail formatting/schema
- M-specific view model

을 둔다.

정확한 파일 분할은 sibling audit 후 최소 구조를 택하되, `tabs/`, `sections/`, `apps/calculator/ui/` root에 M 관련 flat files를 여러 개 추가하지 않는다.

---

# 7. Appendix M SEER domain specification

## 7.1 Initial supported product

```text
Variable-speed compressor
Non-ducted
Single-split
```

M SEER 계산 자체에 product-type branch가 필요하지 않은데 단지 M1 sibling에 존재한다는 이유로 `HP/AC` selector를 복제하지 않는다.

AHRI validation app의 `Is Variable-Speed HP`는 M1 cooling building load에 영향을 주는 항목임을 명시하고 있다. Appendix M M calculation에 실제로 필요하지 않으면 M UI에는 노출하지 않는다.

---

## 7.2 Required test points

| Canonical UI point | Condition | Compressor operation | Required |
|---|---:|---|---|
| A2 | 95°F ODB | full | Yes |
| B2 | 82°F ODB | full | Yes |
| B1 | 82°F ODB | minimum | Yes |
| EV | 87°F ODB | intermediate | Yes |
| F1 | 67°F ODB | minimum | Yes |

각 point 입력:

```text
Capacity [Btu/h]
Power [W]
```

모든 required capacity/power:

```text
finite
> 0
```

이어야 한다.

---

## 7.3 Cooling fractional bin table

Appendix M Table 19:

| Tj [°F] | nj/N |
|---:|---:|
| 67 | 0.214 |
| 72 | 0.231 |
| 77 | 0.216 |
| 82 | 0.161 |
| 87 | 0.104 |
| 92 | 0.052 |
| 97 | 0.018 |
| 102 | 0.004 |

정적 standard data로 config/domain policy가 소유한다.

UI에 하드코딩하지 않는다.

---

## 7.4 Cooling building load

Appendix M building cooling load:

\[
BL(T_j)
=
\frac{T_j - 65}{95 - 65}
\cdot
\frac{Q_{A2}(95)}{1.1}
\]

M SEER에는 M1 variable-capacity HP cooling load의 `V=0.93` factor를 적용하지 않는다.

즉 다음 구현은 금지한다.

```python
seer = calculate_seer2(...) / some_factor
```

또는:

```python
building_load = m1_building_load(..., v_factor=1.0)
```

처럼 M1 seasonal policy owner를 재사용하는 것도 동일 formula임이 충분히 증명되지 않으면 피한다.

Appendix M formula를 M domain owner가 명시적으로 소유한다.

---

## 7.5 Minimum-speed capacity and power line

B1(82°F)와 F1(67°F)를 이용하여 Appendix M 4.1.4 minimum-speed capacity/power line을 계산한다.

개념적으로:

\[
Q_{min}(T)
=
Q_{F1}
+
\frac{Q_{B1}-Q_{F1}}{82-67}(T-67)
\]

\[
P_{min}(T)
=
P_{F1}
+
\frac{P_{B1}-P_{F1}}{82-67}(T-67)
\]

표준 notation/equation order를 코드 및 formula tests에 trace 가능하게 남긴다.

---

## 7.6 Full-speed capacity and power line

B2(82°F)와 A2(95°F)를 이용한다.

\[
Q_{full}(T)
=
Q_{B2}
+
\frac{Q_{A2}-Q_{B2}}{95-82}(T-82)
\]

\[
P_{full}(T)
=
P_{B2}
+
\frac{P_{A2}-P_{B2}}{95-82}(T-82)
\]

---

## 7.7 EV intermediate curve

EV(87°F) point를 기준으로 Appendix M §4.1.4이 정의하는 intermediate capacity/power slope를 계산한다.

현재 M1 SEER2 engine의 `_compute_intermediate_slopes`를 이름이 비슷하다는 이유만으로 호출하지 않는다.

M formula를 직접 대조하여 algebraically identical임이 확인된 작은 pure numeric primitive만 공통화할 수 있다.

---

## 7.8 SEER operating cases

### Case 1 — minimum speed cycling

조건:

\[
BL(T_j) \le Q_{min}(T_j)
\]

Load factor:

\[
X(T_j)=\frac{BL(T_j)}{Q_{min}(T_j)}
\]

Part-load factor:

\[
PLF_j = 1 - C_D^c(1-X)
\]

기본 cooling degradation coefficient:

```text
CDc = 0.25
```

variable-speed path에서 tested CDc를 입력할 경우 Appendix M/AHRI app의 allowed range/rounding을 따른다.

### Case 2 — intermediate speed matching

조건:

\[
Q_{min}(T_j) < BL(T_j) < Q_{full}(T_j)
\]

여기가 현재 M1 SEER2 implementation과 특히 구분되어야 한다.

Appendix M §4.1.4.2는 intermediate operation EER을 outdoor temperature에 대한 quadratic으로 정의한다.

\[
EER_i(T) = A + B T + C T^2
\]

세 anchor temperature:

- `T1`: `Q_min(T1) = BL(T1)`
- `Tv`: `Q_v(Tv) = BL(Tv)`
- `T2`: `Q_full(T2) = BL(T2)`

각 anchor에서:

- minimum-speed EER
- EV-derived intermediate EER
- full-speed EER

를 계산한다.

그 세 점을 정확히 지나는 quadratic coefficient `A/B/C`를 구한다.

구현 방법은 선형대수 library를 도입하지 않고 pure Python closed-form 또는 3-point Lagrange-equivalent formulation을 사용한다.

이 repo calculator는 `numpy` 사용 금지다.

각 Case 2 bin에서는:

\[
Q_i(T_j)=BL(T_j)
\]

\[
P_i(T_j)=\frac{BL(T_j)}{EER_i(T_j)}
\]

로 seasonal numerator/denominator contribution을 구한다.

**현재 M1 SEER2의 `low→intermediate`, `intermediate→full` capacity-based EER piecewise interpolation을 그대로 호출하면 안 된다.**

### Case 3 — full speed continuously

조건:

\[
BL(T_j) \ge Q_{full}(T_j)
\]

Appendix M full-speed continuous contribution을 적용한다.

건물이 요구하는 load가 full capacity보다 커도 delivered cooling numerator를 임의로 BL까지 늘리지 않는다.

---

## 7.9 SEER aggregation

각 bin에서 Appendix M Eq. 4.1-1에 대응하는 cooling and electrical contribution을 fractional bin hours로 합산한다.

최종 raw:

\[
SEER_{raw}
=
\frac{\sum_j q_c(T_j)/N}
{\sum_j e_c(T_j)/N}
\]

absolute season hours를 임의로 도입하지 않는다.

UI에서 numerator/denominator를 보여줄 경우 실제 물리 단위를 과장하지 않는다.

권장 trace field:

```text
seasonal_cooling_numerator
seasonal_energy_denominator
```

필요하면 unit/normalization metadata를 같이 제공한다.

---

## 7.10 SEER published rounding

domain result는 raw와 published를 구분한다.

```text
raw_seer
published_seer
```

published rating은 applicable Appendix M reporting rule에 따라 nearest `0.05 Btu/Wh`로 처리한다.

Python built-in binary `round()`의 tie behavior에 의존하지 말고 project/standard requirement에 맞는 decimal half-up helper를 사용한다.

rounding 자체에 focused boundary tests를 둔다.

---

# 8. Appendix M HSPF domain specification

## 8.1 Initial supported product

```text
Variable-speed compressor heat pump
Non-ducted
Single-split
Region IV
Published rating = standardized DHRmin
```

single-package 지원은 이번 scope에 넣지 않는다.

따라서 UI에서 `Split / Single Package` selector를 추가하지 않는다.

split-specific CSF는 config/domain policy가 소유한다.

---

## 8.2 HSPF required and optional points

### Required

| Point | ODB | Operation |
|---|---:|---|
| H01 | 62°F | minimum |
| H11 | 47°F | minimum |
| H1N | 47°F | nominal |
| H2V | 35°F | intermediate |
| H32 | 17°F | full |

각 point:

```text
Capacity [Btu/h]
Power [W]
```

### Optional

| Point | Condition |
|---|---|
| H12 | 47°F full test performed |
| H22 | 35°F full frost accumulation test performed |

H12/H22가 없다는 이유로 calculation을 `incomplete`로 만들지 않는다.

표준 fallback path를 사용해야 한다.

### H42 audit checkpoint

현재 Appendix M §3.6.4(d)는 H4²(5°F)를 언급하지만 동일 section의 Table 14에 H42 row가 나타나지 않는 editorial inconsistency가 있다. AHRI validation app은 `H42 Tested`를 optional field로 노출한다.

따라서 worker는 구현 시 다음을 수행한다.

1. 현재 applicable Appendix M text에서 H42가 variable-speed Region IV supported path에 실제로 소비되는 정확한 equation path를 확인한다.
2. AHRI app의 M HSPF variable-speed path에서 H42 on/off가 결과에 미치는 동작을 확인한다.
3. 공식 경로가 확인되면 optional H42를 domain/config/UI에 추가한다.
4. 확인되지 않으면 H42를 임의로 required input으로 만들거나 M1 H42 behavior를 복사하지 않는다.
5. H42 여부는 Result Record에 근거와 함께 명시한다.

이 checkpoint는 전체 구현을 막기 위한 것이 아니라 M1 동작을 추측 복제하지 않기 위한 정확성 gate다.

---

# 9. Region IV contract

Appendix M Table 20:

```text
Region IV
HLH = 2250
TOD = 5°F
C = 0.77
```

Fractional bin table:

| Tj [°F] | nj/N |
|---:|---:|
| 62 | 0.132 |
| 57 | 0.111 |
| 52 | 0.103 |
| 47 | 0.093 |
| 42 | 0.100 |
| 37 | 0.109 |
| 32 | 0.126 |
| 27 | 0.087 |
| 22 | 0.055 |
| 17 | 0.036 |
| 12 | 0.026 |
| 7 | 0.013 |
| 2 | 0.006 |
| -3 | 0.002 |
| -8 | 0.001 |

M HSPF에서 다음 M1 Region IV parameters를 사용하면 안 된다.

```text
HLH = 1701
zero load = 55°F
Cvc = 1.07
A2 cooling capacity based heating building load
```

Appendix M HSPF는 DHR 기반이다.

---

# 10. DHR contract

## 10.1 Raw DHR

Appendix M에서 Regions I/II/III/IV/VI:

\[
DHR_{min}
=
Q_h^k(47)
\cdot
\frac{65-T_{OD}}{60}
\]

\[
DHR_{max}
=
2 Q_h^k(47)
\cdot
\frac{65-T_{OD}}{60}
\]

variable-speed path의 47°F reference는 applicable Appendix M rule에 따라 nominal `H1N` capacity를 사용한다.

Region IV:

```text
TOD = 5°F
(65 - 5) / 60 = 1
```

따라서 Region IV raw DHR은:

\[
DHR_{min,raw}=Q_{H1N}
\]

\[
DHR_{max,raw}=2Q_{H1N}
\]

이 관계는 test로 직접 고정한다.

---

## 10.2 Standardized DHR

Appendix M Table 21:

```text
5,000
10,000
15,000
20,000
25,000
30,000
35,000
40,000
50,000
60,000
70,000
80,000
90,000
100,000
110,000
130,000 Btu/h
```

raw DHRmin/DHRmax를 nearest standardized DHR로 매핑한다.

tie behavior를 명시적으로 deterministic하게 구현한다.

published standard HSPF는 Region IV standardized `DHR_min` rating이다.

`DHR_max` 결과는 trace/diagnostic로 계산할 수 있지만 M HSPF UI의 primary published metric은 DHRmin이다.

---

# 11. HSPF building load

Appendix M:

\[
BL(T_j)
=
\frac{65-T_j}{65-T_{OD}}
\cdot
C
\cdot
DHR
\]

Region IV:

```text
TOD = 5°F
C = 0.77
DHR = standardized DHRmin
```

M1처럼 cooling A2를 heating load anchor로 사용하지 않는다.

---

# 12. HSPF full-speed fallback contract

## 12.1 47°F full point

우선순위:

### Path A — H12 tested

H12가 있으면 H12 measured capacity/power를 full-speed 47°F 값으로 사용한다.

### Path B — H1N same speed as H32

H12가 없고 H1N compressor speed가 H32 full-speed와 동일하면 H1N measured values를 사용한다.

UI/domain option 예:

```text
h1n_same_speed_as_h32
```

### Path C — calculated full 47°F

둘 다 아니면 H32로부터 계산한다.

Split-system:

\[
CSF=0.0204/^\circ F
\]

\[
PSF=0.00455/^\circ F
\]

\[
Q_{full,47}
=
Q_{H32}
(1 + 30 \cdot CSF)
\]

\[
P_{full,47}
=
P_{H32}
(1 + 30 \cdot PSF)
\]

이번 scope는 single-split이므로 single-package `CSF=0.0262/°F`를 UI option으로 노출하지 않는다.

config에는 scope와 source를 명확히 기록한다.

---

## 12.2 35°F full fallback

H22가 있으면 measured H22를 사용한다.

H22가 없으면 Appendix M §3.6.4(c)의 fallback을 정확히 구현한다.

현재 regulation의 equation value를 source에서 직접 transcription하여 test로 고정한다.

핵심 형태는 H32와 calculated/tested full 47°F line에서 35°F reference를 만들고 Appendix M frost adjustment factor를 적용하는 경로다.

worker는 이 부분을 current M1 H22 fallback helper에서 복사하지 말고 Appendix M equation text와 1:1 대조해야 한다.

결과 metadata에:

```text
h12_source
h22_source
```

또는 동등한 trace를 남겨 measured/fallback 경로를 구분한다.

---

# 13. HSPF minimum-speed curve

Appendix M §4.2.4 minimum-speed capacity/power는 H01(62°F), H11(47°F) 기반이다.

35°F minimum reference는 Appendix M formula에 따라 산출한다.

M1 minimum-speed-limiting policy를 이번 M scope에 가져오지 않는다.

AHRI app의 `Does Comp Limit Min-Spd` 설명 자체가 M1-specific임을 명시하고 있으므로 M UI에는 M formula가 실제로 요구하지 않는 한 노출하지 않는다.

---

# 14. H2V intermediate performance

H2V는 35°F intermediate test point다.

Appendix M §4.2.4:

\[
N_Q
=
\frac{Q_{H2V}-Q_{min}(35)}
{Q_{full}(35)-Q_{min}(35)}
\]

\[
N_E
=
\frac{P_{H2V}-P_{min}(35)}
{P_{full}(35)-P_{min}(35)}
\]

Intermediate capacity slope:

\[
M_Q
=
\left(
\frac{Q_{min}(62)-Q_{min}(47)}
{62-47}
\right)(1-N_Q)
+
N_Q
\left(
\frac{Q_{full}(35)-Q_{full}(17)}
{35-17}
\right)
\]

Power slope도 동일 구조로 `N_E`를 사용한다.

domain validation은 physically invalid envelope를 silent clamp하지 않는다.

최소한:

```text
0 <= N_Q <= 1
0 <= N_E <= 1
```

가 아니면 명확한 domain error를 발생시킨다.

---

# 15. HSPF operating cases

## 15.1 Case I — minimum speed cycling

조건:

\[
Q_{min}(T_j) \ge BL(T_j)
\]

\[
X=\frac{BL}{Q_{min}}
\]

\[
PLF=1-C_D^h(1-X)
\]

default:

```text
CDh = 0.25
```

compressor low-temperature cut-out factor는 Appendix M의 `δ(Tj)` / referenced cut-out equation을 그대로 적용한다.

M1 implementation의 cut-out/COP 조건을 이름이 비슷하다는 이유로 복사하지 않는다.

---

## 15.2 Case II — intermediate speed

조건:

\[
Q_{min}(T_j)
<
BL(T_j)
<
Q_{full}(T_j)
\]

heat pump는 building load에 맞는 intermediate compressor speed로 동작한다.

Appendix M §4.2.4.2의 COP interpolation:

### min ↔ H2V-derived intermediate

\[
COP_i
=
COP_{min}
+
\frac{COP_v-COP_{min}}
{Q_v-Q_{min}}
(BL-Q_{min})
\]

### H2V-derived intermediate ↔ full

\[
COP_i
=
COP_v
+
\frac{COP_{full}-COP_v}
{Q_{full}-Q_v}
(BL-Q_v)
\]

그 후 compressor electrical contribution을 Appendix M equation에 따라 산출한다.

cut-out factor도 Appendix M path를 적용한다.

---

## 15.3 Case III — full speed + resistance

조건:

\[
BL(T_j) \ge Q_{full}(T_j)
\]

compressor는 full-speed로 동작하고 부족한 building load는 resistive supplementary heat가 담당한다.

resistance conversion은 Appendix M notation에 맞춰:

```text
3.413 Btu/h per W
```

를 사용한다.

M1 `aux_cop` generalization을 이번 M profile에 임의로 도입하지 않는다.

이번 scope의 supplementary heat는 electric resistance semantics다.

---

# 16. Low-temperature compressor cut-out

Appendix M에서 `T_off`, `T_on`이 주어질 수 있다.

worker는 Appendix M이 정의하는 cut-out factor `δ(Tj)`를 exact port한다.

요구사항:

- no shut-off case 지원
- `T_on >= T_off` validation
- transition bin의 fractional availability semantics 보존
- compressor unavailable 시 unmet load를 resistance heating으로 처리
- M1 helper가 identical한지 증명되지 않으면 직접 reuse 금지

formula trace에 cut-out case를 남긴다.

---

# 17. Demand-defrost credit

default:

\[
F_{def}=1
\]

qualifying demand-defrost system은 Appendix M §3.9.2 equation을 사용한다.

개념적으로:

\[
F_{def}
=
1
+
0.03
\left[
1-
\frac{\Delta\tau_{def}-1.5}
{\Delta\tau_{max}-1.5}
\right]
\]

constraints:

```text
Δτdef = max(measured interval, 1.5 h)
6 h limit reached without completed defrost → Δτdef = 6
Δτmax = min(control maximum, 12 h)
```

variable-speed heat pump에서는 required intermediate-speed frost accumulation test에 해당하는 interval을 사용한다.

UI는 가능하면 raw defrost interval inputs보다 current product workflow에 맞는 최소 입력만 노출한다.

단, domain에서는 formula inputs/trace를 충분히 보존한다.

M HSPF aggregate에서 `F_def`의 위치는 Appendix M Eq. 4.2-1 그대로 구현한다.

M1 `fdef_override` policy를 복사하지 않는다.

---

# 18. HSPF aggregation

각 Region IV bin에 대해:

- building load
- compressor heat contribution
- compressor electrical contribution
- resistance heat contribution
- resistance electrical contribution
- cut-out factor
- part-load factor
- operating case

를 계산한다.

Appendix M Eq. 4.2-1에 따라 HSPF를 계산하고 demand-defrost credit을 적용한다.

domain output은 최소 다음을 구분한다.

```text
raw_hspf
published_hspf
dhr_min_raw
dhr_min_standardized
dhr_max_raw
dhr_max_standardized
f_def
bin_details
```

DHRmax는 trace이며 primary user rating은 Region IV DHRmin이다.

---

# 19. HSPF published rounding

SEER와 동일하게 raw/published를 분리한다.

published HSPF는 nearest `0.05 Btu/Wh`.

decimal-based deterministic rounding을 사용하고 boundary tests를 둔다.

---

# 20. Config ownership

현재:

```text
M1 SEER2  → data/region_configs/usa.json
M1 HSPF2  → data/region_configs/usa_hspf2.json
```

M config를 이 두 schema에 억지로 병합하지 않는다.

권장:

```text
data/region_configs/usa_m_seer.json
data/region_configs/usa_m_hspf.json
```

또는 repo audit 후 동일 의미의 명확한 M-specific name.

M SEER config 예시 responsibility:

```text
standard identity
Table 19 bins
test point temperatures
sizing factor 1.1
zero-load cooling temperature 65°F
CDc default / allowed constraints
published rounding step
```

M HSPF config responsibility:

```text
standard identity
Region IV Table 20 bins
TOD
C = 0.77
HLH metadata
Table 21 standardized DHR values
split CSF
PSF
CDh default
resistance conversion
published rounding step
```

config에는 production standard data만 둔다.

official calculator sample input/output을 config에 넣지 않는다.

---

# 21. Profile design

기존 M1 profiles는 그대로 둔다.

신규 M profiles는 explicit하게 M identity를 드러내는 ID를 권장한다.

```text
ahri_usa_m_seer
ahri_usa_m_hspf
```

예상 semantic contract:

### SEER

```text
standard      = AHRI_210_240
region        = usa
metric        = SEER
mode          = cooling
calculator_id = ahri_seer
```

### HSPF

```text
standard      = AHRI_210_240
region        = usa
metric        = HSPF
mode          = heating
calculator_id = ahri_hspf
```

기존 M1 IDs를 `*_m1_*`로 rename하지 않는다.

M/M1 구분은:

- existing metric: SEER2/HSPF2
- new metric: SEER/HSPF
- M-specific new profile ID
- UI label

로 충분히 명확하게 만든다.

---

# 22. Standard facade / domain package design

M은 별도 domain owner를 갖는다.

권장 public facade:

```text
core/calculators/standards/ahri_seer.py
core/calculators/standards/ahri_hspf.py
```

여러 internal responsibility가 생기므로 새 internal package를 권장한다.

```text
core/calculators/standards/_ahri_m/
```

예시 responsibility split:

```text
SEER seasonal engine
SEER performance/intermediate math
HSPF context / DHR
HSPF performance
HSPF seasonal engine
result assembly
pure numeric helpers
```

단, 이 파일 이름을 그대로 강제하지 않는다.

worker는 existing M1 `_ahri/` sibling을 audit한 뒤:

- public facade는 얇게 유지하고
- formula owners가 한 파일에 과도하게 모이지 않으며
- source file owner boundary policy를 만족하는

최소 구조를 선택한다.

---

# 23. M과 M1 사이 code reuse 규칙

재사용 판단의 원칙:

> 이름이 같거나 시험점이 비슷해서가 아니라, equation semantics가 동일할 때만 공유한다.

공유 후보:

- `safe_div`
- generic linear interpolation
- decimal step rounding primitive

조건부 공유 후보:

- H2V slope math
- simple point interpolation

공유 금지 기본값:

- SEER/SEER2 seasonal case dispatch
- SEER intermediate EER policy
- HSPF/HSPF2 building load
- HSPF/HSPF2 Region IV context
- DHR
- defrost application policy
- M1 minimum-speed-limiting logic
- M1 H42 low-temperature policy

M 전용 logic을 기존 M1 `_ahri` files에 `if appendix_m:` 분기로 누적하지 않는다.

---

# 24. Dispatcher / capability design

## 24.1 Dispatcher

신규 calculator IDs를 lazy construction mapping에 연결한다.

```text
ahri_seer
ahri_hspf
```

기존 mappings는 수정 의미를 최소화한다.

## 24.2 New capability IDs

권장 stable public capability IDs:

```text
ahri210240.seer
ahri210240.hspf
```

기존:

```text
ahri210240.seer2
ahri210240.hspf2
```

는 그대로 유지한다.

## 24.3 Typed request

신규 M-specific typed request를 둔다.

개념:

```text
AhriSeerRequest
AhriHspfRequest
```

M1 request class를 metric discriminator로 재사용하지 않는다.

SEER request는:

- measured points
- CDc / supported options
- profile ID

HSPF request는:

- measured points
- H12/H22 presence
- H1N/H32 speed relation
- CDh
- cut-out inputs
- demand-defrost inputs
- profile ID

를 domain-neutral typed values로 전달한다.

---

# 25. Application adapter design

M UI는 core calculator를 직접 호출하지 않는다.

예상 flow:

```text
Tk input
→ M application adapter
→ AhriSeerRequest / AhriHspfRequest
→ execute_standard_calculation(...)
→ domain result
→ typed UI summary
→ View
```

Application adapter가 담당할 validation:

```text
blank cell
non-numeric
non-finite
<= 0 capacity/power
option text conversion
```

Domain adapter가 숨기면 안 되는 error:

```text
invalid standard envelope
invalid DHR/config
invalid H2V interpolation envelope
invalid T_off/T_on
invalid defrost parameters
```

UI는 field error와 calculation error를 current sibling UX에 맞게 표시한다.

---

# 26. SEER UI surface

## 26.1 Input

표 형태:

```text
Point | ODB [°C] | Capacity [Btu/h] | Power [W] | EER
A2    | 35.0     | ...              | ...       | ...
B2    | 27.8     | ...              | ...       | ...
B1    | 27.8     | ...              | ...       | ...
EV    | 30.6     | ...              | ...       | ...
F1    | 19.4     | ...              | ...       | ...
```

표준 I-P condition을 primary source로 하되 current calculator UX의 °C display convention과 일관성을 유지한다.

내부 formula는 °F canonical 값으로 계산해도 된다.

Product selector는 두지 않는다.

M1용 dual-stage option을 가져오지 않는다.

## 26.2 Options

최소:

```text
Cooling degradation coefficient CDc
```

default:

```text
0.25
```

tested coefficient 정책을 지원하면 Appendix M/AHRI app constraints와 rounding을 적용한다.

## 26.3 Result

권장 summary:

```text
SEER Raw
SEER Published
```

보조:

```text
Seasonal Cooling Numerator
Seasonal Energy Denominator
```

## 26.4 Detail

최소 columns:

```text
Tj
fraction
BL
Q_min
Q_v
Q_full
EER_min
EER_v
EER_full
EER_match
case
cooling contribution
energy contribution
```

---

# 27. HSPF UI surface

## 27.1 Input

required rows:

```text
H01
H11
H1N
H2V
H32
```

optional rows:

```text
H12
H22
```

confirmed if applicable:

```text
H42
```

optional point의 Capacity/Power 둘 중 하나만 입력된 상태는 field error다.

둘 다 blank면 “not tested”로 취급한다.

## 27.2 Options

최소 candidate:

```text
H1N speed = H32 speed
Heating degradation coefficient CDh
Compressor shut-off temperature
Compressor turn-on temperature
Demand defrost enabled
Defrost interval
Control maximum defrost interval
```

현재 supported scope가 split unit으로 고정되어 있으므로:

```text
Unit type
Region
```

selectors는 추가하지 않는다.

UI에 변경 불가능한 선택지를 늘리지 않는다.

## 27.3 Result

Primary:

```text
HSPF Raw
HSPF Published
```

trace:

```text
Region IV
DHRmin Raw
DHRmin Standardized
DHRmax Raw
DHRmax Standardized
Fdef
```

가능하면:

```text
Compressor seasonal energy contribution
Resistance seasonal energy contribution
```

## 27.4 Detail

최소:

```text
Tj
fraction
BL
Q_min
Q_v
Q_full
COP_min
COP_v
COP_full
COP_match
case
delta
PLF
compressor heat
compressor energy
resistance heat
resistance energy
```

---

# 28. Existing shared UI owners to reuse

M surface는 다음 repository capabilities를 새로 재구현하지 않는다.

- `ScrollableFrame`
- `ProfileVisibleContentLifecycleController`
- `DebouncedAutoCalc`
- standard input table/controller primitives when compatible
- `ResultPanel`
- `BinDetailPanel`
- detail visibility owner
- existing result copy/export actions

M-specific field maps, labels, formula trace schema는 M package에서 소유한다.

공통 widget behavior만 shared owner를 사용한다.

---

# 29. M batch behavior

첫 implementation에서는 M-specific batch dialog를 만들지 않는다.

이유:

- formula + profile + capability + UI가 이미 cross-owner change다.
- M1 batch는 product-specific state/session owner를 포함한다.
- M에 이를 그대로 복사하면 지원하지 않는 product policy와 state responsibility가 같이 유입될 수 있다.

따라서 M main metric surfaces를 먼저 complete 상태로 만들고, batch는 별도 요청이 있을 때 추가한다.

UI에 disabled batch button이나 placeholder도 두지 않는다.

---

# 30. Public result schema

M1 result schema를 수정하지 않는다.

신규 M schema를 독립적으로 정의한다.

## 30.1 SEER recommended contract

```python
{
    "SEER": ...,
    "raw_seer": ...,
    "published_seer": ...,
    "seasonal_cooling_numerator": ...,
    "seasonal_energy_denominator": ...,
    "bin_details": [...],
    "summary": {
        "metadata": {
            "standard_method": "appendix_m",
            "compressor_type": "variable_speed",
            ...
        }
    }
}
```

`SEER` top-level 의미는 project convention에 맞춰 하나로 고정한다.

권장:

```text
SEER = published_seer
```

그리고 raw는 항상 `raw_seer`로 별도 제공한다.

다른 existing standards가 raw metric을 top-level로 쓰는 convention이 있으면 worker는 capability/result owner를 audit하여 일관된 선택을 하고 tests/docs로 고정한다.

## 30.2 HSPF recommended contract

```python
{
    "HSPF": ...,
    "raw_hspf": ...,
    "published_hspf": ...,
    "region": "IV",
    "dhr_min_raw": ...,
    "dhr_min_standardized": ...,
    "dhr_max_raw": ...,
    "dhr_max_standardized": ...,
    "f_def": ...,
    "bin_details": [...],
    "summary": {
        "metadata": {
            "standard_method": "appendix_m",
            "compressor_type": "variable_speed",
            "rating_dhr": "minimum",
            ...
        }
    }
}
```

M1 diagnostics/result keys를 rename하거나 억지로 공통 schema로 통합하지 않는다.

---

# 31. Validation plan

## 31.1 Formula unit tests — SEER

반드시 증명할 것:

1. Table 19 exact bins
2. fractional bin sum
3. M building-load equation
4. M load에 M1 HP `V=0.93`가 적용되지 않음
5. minimum Q/P line
6. full Q/P line
7. EV intermediate Q/P slope
8. `T1`, `Tv`, `T2` crossing calculation
9. 3-point quadratic EER interpolation
10. Case 1 cycling
11. Case 2 intermediate matching
12. Case 3 full continuous
13. aggregate raw SEER
14. nearest 0.05 published rounding
15. invalid/nonphysical intermediate path fail-fast

특히 characterization test 하나는 동일 test points에서 M과 M1의 intermediate seasonal path가 같은 implementation으로 합쳐지지 않았음을 보여야 한다.

---

## 31.2 Formula unit tests — HSPF

반드시 증명할 것:

1. Region IV Table 20 exact bins
2. HLH = 2250 metadata
3. TOD = 5°F
4. C = 0.77
5. raw DHRmin = H1N capacity for Region IV
6. raw DHRmax = 2 × H1N capacity
7. Table 21 nearest standardized DHR
8. building load
9. H12 tested full-47 path
10. H1N same-speed full-47 path
11. CSF/PSF calculated full-47 path
12. H22 measured path
13. H22 fallback path
14. H2V NQ/NE
15. H2V slope
16. invalid H2V envelope rejection
17. Case I min cycling
18. Case II min↔intermediate interpolation
19. Case II intermediate↔full interpolation
20. Case III full + resistance
21. low-temperature cut-out behavior
22. no-cutout behavior
23. demand-defrost default Fdef=1
24. qualifying demand-defrost Fdef
25. aggregate Region IV DHRmin raw HSPF
26. nearest 0.05 published HSPF
27. DHRmax not substituted for primary published HSPF

H42가 supported되면:

28. H42 absent path
29. H42 present path
30. official-app parity difference

를 추가한다.

---

# 32. Integration tests

## 32.1 Profile

검증:

```text
ahri_usa_m_seer
ahri_usa_m_hspf
```

가 각각 정확히 하나의 enabled profile로 resolve된다.

기존:

```text
ahri_usa_seer2
ahri_usa_hspf2
```

도 이전과 동일하게 resolve된다.

## 32.2 Dispatcher

new calculator IDs가 new M facade를 반환한다.

기존 M1 route는 이전 class를 반환한다.

## 32.3 Capability

검증:

```text
ahri210240.seer + AhriSeerRequest
ahri210240.hspf + AhriHspfRequest
```

wrong request type은 fail-fast.

M request를 M1 capability에 전달하거나 그 반대도 fail-fast.

## 32.4 Application adapter

검증:

- blank required input → `None`/input wait semantics
- optional H12/H22 blank → fallback calculation 가능
- half-filled optional point → field error
- invalid numeric
- zero/negative
- summary conversion
- core domain errors preserve calculation-error boundary

---

# 33. UI tests

## 33.1 Top-level labels

정확히 검증:

```text
AHRI 210/240 M
AHRI 210/240 M1
```

기존 generic `AHRI 210/240` label이 남아 있지 않아야 한다.

## 33.2 Nested metric labels

M:

```text
SEER
HSPF
```

M1:

```text
SEER2
HSPF2
```

## 33.3 Lifecycle

M tab이 existing calculator lifecycle owner를 사용하며:

- metric switch refit
- detail toggle refit
- scroll behavior
- top-level selection fit

이 sibling AHRI/EN surfaces와 동등하게 동작하는지 focused test.

## 33.4 SEER/HSPF interaction

- auto calculation
- input error
- result clear
- detail rows
- copy/export behavior
- close/destroy cleanup

M UI에 unsupported product controls가 나타나지 않는지도 test한다.

---

# 34. M1 regression guard

이번 작업의 critical regression suite는 M1이다.

기존 M1 focused tests에서 최소 다음 behavior가 그대로 통과해야 한다.

- SEER2 variable-capacity
- SEER2 supported product routing
- HSPF2 variable-capacity
- HSPF2 other currently supported product routing
- M1 profile
- M1 capability
- M1 application adapters
- M1 Tk sections
- M1 tab lifecycle
- M1 batch paths

expected value를 M 추가를 이유로 변경하지 않는다.

M1 source를 변경할 필요가 생기면 그 변경은 shared primitive extraction에 한정하고 exact behavior characterization을 먼저 둔다.

---

# 35. Official-calculator golden

최소 official parity:

```text
1 × Appendix M SEER variable-speed case
1 × Appendix M HSPF variable-speed Region IV DHRmin case
```

AHRI validation app:

https://seerhspf2.ahrianalytics.org/app_direct/seer2hspf2/

## Golden packet에 남길 내용

- input test points
- optional flags
- CDc/CDh
- H1N/H32 speed relation
- demand-defrost inputs
- T_off/T_on
- H12/H22/H42 state
- AHRI app displayed M SEER/HSPF
- observed date
- expected project raw/published mapping

가능하면 현재 repository가 이미 M1 golden에 사용하는 동일 장비 dataset의 공통 test points를 재사용하되, **M expected result는 AHRI M calculation에서 독립적으로 관찰**해야 한다.

절대 금지:

```text
M result = M1 result × conversion coefficient
```

AHRI app access가 불가능하면 expected official value를 추측 생성하지 않는다.

그 경우:

- formula tests
- synthetic branch characterization
- integration tests

까지 구현하고 official-calculator golden만 weaker/blocked evidence로 명시한다.

공식 parity를 확인하지 못한 상태를 “official golden passed”라고 보고해서는 안 된다.

---

# 36. Documentation update

AHRI active owner docs는 M/M1을 함께 구분할 수 있도록 갱신한다.

문서가 표현해야 할 핵심:

```text
AHRI 210/240 family
├─ Appendix M
│  ├─ SEER
│  └─ HSPF
└─ Appendix M1
   ├─ SEER2
   └─ HSPF2
```

현재 M1 deep implementation 설명을 M이라는 이름 아래로 이동시키거나 의미를 바꾸지 않는다.

M의 formula references, supported product/region, config ownership, golden evidence를 별도 subsection으로 추가한다.

---

# 37. Result Record requirement

이번 변경은:

- calculator formula
- golden
- production config
- profile/capability/public result
- UI/core integration

을 포함하므로 repository의 compact Result Record trigger에 해당한다.

Result Record에는 generic 완료 보고를 반복하는 대신 다음 decision evidence를 중심으로 남긴다.

- M/M1 owner split
- Appendix M formula references
- SEER quadratic intermediate proof
- Region IV DHR semantics
- H42 audit conclusion
- official calculator parity evidence
- M1 regression evidence
- any shared primitive reuse decision

---

# 38. Implementation sequence

worker가 한 작업으로 수행하되 dependency 순서는 다음을 권장한다.

## Slice A — Domain

- M config
- M standard facades
- M internal formula owners
- formula unit tests

먼저 raw formula correctness를 고정한다.

## Slice B — Profile / Dispatcher / Capability

- M profiles
- calculator IDs
- typed requests
- capability IDs
- route tests

## Slice C — Application

- outbound construction
- SEER application adapter
- HSPF application adapter
- parsing/error/summary tests

## Slice D — UI

- M top-level tab
- existing AHRI label → M1
- SEER/HSPF sections
- detail/result/copy/export
- lifecycle reuse
- focused UI tests

## Slice E — Golden / Regression / Docs

- AHRI app parity
- M1 regression
- docs
- Result Record
- repository-defined final validation gates

이 순서는 implementation guidance이며 worker는 repository sibling audit 결과에 따라 파일 분할을 더 최소화할 수 있다.

---

# 39. Stop conditions

다음 상황에서는 임의 해석으로 진행하지 않는다.

## 39.1 Standard formula ambiguity

특히:

- H42 exact supported path
- Appendix M equation transcription이 source rendering 때문에 불명확한 경우
- low-temperature cut-out exact branch
- tested degradation coefficient policy

는 authoritative Appendix M/AHRI app evidence로 확인한다.

## 39.2 Architecture smell

다음 형태가 발생하면 구조를 재검토한다.

```text
View contains DHR formula
application adapter contains bin loop
M engine imports M1 facade and selects mode
M and M1 profile IDs are renamed together
M UI lifecycle is copy/pasted
new M files are scattered through broad folders
```

## 39.3 Golden mismatch

AHRI app과 mismatch가 나면 expected를 바꾸기 전에:

1. point mapping
2. optional test state
3. CD
4. DHR
5. cut-out
6. defrost
7. fallback source
8. rounding
9. M vs M1 selected calculation

을 intermediate trace로 비교한다.

---

# 40. Completion criteria

작업은 다음 상태에서 complete다.

## Domain

- Appendix M SEER variable-speed formula implemented
- Appendix M HSPF variable-speed Region IV / DHRmin formula implemented
- raw/published metrics separated
- M-specific configs own standard data
- no numpy/pandas

## Architecture

- M has separate domain owner from M1
- profile/dispatcher/capability path is canonical
- application adapter owns UI mapping only
- View owns presentation only
- lifecycle owner reused
- no formula in UI/application
- no M branch pollution in M1 seasonal engines

## UI

```text
AHRI 210/240 M
  SEER
  HSPF

AHRI 210/240 M1
  SEER2
  HSPF2
```

exactly exposed.

## Compatibility

- existing M1 profile IDs unchanged
- existing M1 capability IDs unchanged
- existing M1 public methods unchanged
- existing M1 result keys unchanged
- M1 focused regression remains green

## Verification

- formula branch tests green
- profile/dispatcher/capability tests green
- application adapter tests green
- focused Tk tests green
- structure/change gates appropriate to touched owners green or warning-triaged
- official M SEER golden confirmed, or explicitly reported as unavailable
- official M HSPF Region IV DHRmin golden confirmed, or explicitly reported as unavailable
- docs and required Result Record synchronized

---

# 41. Worker 실행용 구현 명세

아래 내용을 작업의 direct implementation brief로 사용한다.

---

## predictor_v3 — AHRI 210/240 Appendix M SEER/HSPF Calculator Worker

### Role and objective

`predictor_v3` Calculator에 Appendix M 기반 `SEER`와 `HSPF`를 production-quality calculator feature로 추가한다.

현재 calculator의 Appendix M1 기반 SEER2/HSPF2는 그대로 유지한다.

사용자에게 보이는 최종 standard navigation은:

```text
AHRI 210/240 M
  ├─ SEER
  └─ HSPF

AHRI 210/240 M1
  ├─ SEER2
  └─ HSPF2
```

여야 한다.

현재 top-level `AHRI 210/240` label은 `AHRI 210/240 M1`으로 변경하고, sibling top-level `AHRI 210/240 M`을 추가한다.

### Required implementation behavior

Appendix M calculation은 Appendix M1 결과의 변환이나 existing M1 seasonal engine의 mode option으로 구현하지 않는다.

M은 별도의 domain owner를 가져야 하며, current architecture의:

```text
View
→ application adapter
→ typed capability
→ profile/dispatcher
→ standard domain calculator
```

dependency direction을 유지한다.

Initial product scope는:

```text
non-ducted
single-split
variable-speed compressor
air-to-air
```

이다.

SEER는 Appendix M §4.1.4 variable-speed path를 구현한다.

필수 cooling points:

```text
A2 95°F full
B2 82°F full
B1 82°F minimum
EV 87°F intermediate
F1 67°F minimum
```

Table 19 bins와 Appendix M building load를 사용한다.

특히 intermediate matching 영역은 M1 SEER2의 capacity-piecewise EER interpolation이 아니라 Appendix M의 `EER_i(T)=A+B*T+C*T²` path를 구현한다. `T1`, `Tv`, `T2` crossing points와 그 EER anchor를 이용하여 quadratic을 구성한다.

HSPF는 Appendix M §3.6.4, §4.2, §4.2.4 variable-speed path를 구현한다.

우선 Region IV만 지원하고 primary published rating은 standardized minimum DHR로 한다.

required points:

```text
H01
H11
H1N
H2V
H32
```

optional:

```text
H12
H22
```

H12/H22가 없으면 Appendix M fallback을 사용한다.

Region IV는 Appendix M Table 20의:

```text
HLH 2250
TOD 5°F
C 0.77
```

및 fractional bin table을 사용한다.

DHRmin/DHRmax를 계산하고 Table 21 standardized DHR로 map한다. Region IV primary calculation은 standardized DHRmin을 사용한다.

HSPF building load는 DHR 기반이며 M1의 A2 cooling-capacity heating load line을 사용하지 않는다.

H2V intermediate performance의 `N_Q`, `N_E`, `M_Q`, `M_E`를 Appendix M equation으로 계산하고 nonphysical envelope는 fail-fast 한다.

Case I minimum cycling, Case II intermediate matching, Case III full + electric resistance를 구현한다.

compressor low-temperature cut-out factor와 demand-defrost credit은 Appendix M exact semantics를 사용한다. M1 defrost override policy를 가져오지 않는다.

Appendix M §3.6.4에서 H42 관련 text와 Table 14 사이의 표현 차이가 있으므로 H42는 현재 Appendix M equation path와 AHRI validation app behavior를 직접 확인한 뒤 optional support 여부를 결정한다. M1 H42 path를 추측 복제하지 않는다.

SEER와 HSPF는 raw와 published를 분리하고 published value는 applicable reporting rule의 nearest 0.05 Btu/Wh rounding으로 제공한다.

### Architecture and compatibility requirements

기존 M1 profiles:

```text
ahri_usa_seer2
ahri_usa_hspf2
```

를 rename하지 않는다.

기존 M1 capability IDs:

```text
ahri210240.seer2
ahri210240.hspf2
```

를 rename하지 않는다.

기존 M1 facade/method/result behavior를 바꾸지 않는다.

새 M profiles는 explicit M identity를 갖도록:

```text
ahri_usa_m_seer
ahri_usa_m_hspf
```

형태를 우선한다.

새 capability IDs는:

```text
ahri210240.seer
ahri210240.hspf
```

로 제공한다.

M domain implementation은 M1 seasonal engines와 분리한다. 동일 equation semantics가 증명된 작은 pure numeric primitive만 공유한다.

M UI는 기존 lifecycle, result/detail, copy/export, input-table primitives를 적합한 범위에서 재사용한다.

M UI가 여러 source responsibility를 필요로 하므로 관련 code를 broad UI folders에 flat하게 흩뿌리지 말고 coherent M feature package 안에 둔다.

이번 scope에서는 M-specific batch calculator를 추가하지 않는다.

### UI requirements

M SEER는 A2/B2/B1/EV/F1 Capacity/Power를 입력받고 result로:

```text
SEER Raw
SEER Published
```

를 제공한다.

필요한 bin details를 제공한다.

M HSPF는 required H points와 optional H12/H22를 입력받고:

```text
HSPF Raw
HSPF Published
Region IV
DHRmin Raw
DHRmin Standardized
DHRmax Raw
DHRmax Standardized
Fdef
```

를 보여줄 수 있어야 한다.

지원하는 product가 하나뿐이므로 M surface에 M1 Product selector를 복제하지 않는다.

현재 scope가 Region IV / split으로 고정되어 있으므로 불필요한 Region 또는 Unit Type selector도 추가하지 않는다.

### Validation objective

수식 테스트는 단순 final metric만 확인하지 말고 Appendix M과 Appendix M1의 차이가 손실되지 않았음을 intermediate values로 증명해야 한다.

SEER에서는 최소:

```text
Table 19
BL
min/full curves
EV intermediate slopes
T1/Tv/T2
quadratic EER
Cases 1/2/3
raw/published rounding
```

을 고정한다.

HSPF에서는 최소:

```text
Region IV table
DHR raw/standardized
BL
H12/H1N/CSF-PSF full-47 paths
H22 measured/fallback
H2V N/M terms
Cases I/II/III
cut-out
resistance
demand defrost
raw/published rounding
```

을 고정한다.

M1 focused tests는 expected change 없이 통과해야 한다.

최종 official parity는 AHRI SEER/HSPF Calculation App의 Appendix M output에 대해 최소 SEER 1 case, HSPF Region IV DHRmin 1 case를 확인한다.

공식 계산기 evidence를 얻을 수 없는 환경이라면 expected를 만들어내지 말고 formula/integration validation까지 완료한 뒤 official golden 부분만 명확히 weaker/blocked로 보고한다.

### Final state

완료 후 사용자는 Calculator에서:

```text
AHRI 210/240 M → SEER/HSPF
AHRI 210/240 M1 → SEER2/HSPF2
```

를 독립적으로 사용할 수 있어야 한다.

두 procedure는 서로 다른 formula owner를 사용하며, 기존 M1 behavior/public contract에는 regression이 없어야 한다.

---

# 42. Audit reference map

## Repository owners reviewed

```text
AGENTS.md
AGENT_TASK_ROUTER.md
docs/agent_workflows/CALCULATOR_WORKFLOW.md
docs/agent_workflows/UI_SURFACE_WORKFLOW.md
docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md
data/region_configs/REGION_CONFIG_RULES.md

app_calculator.py
apps/calculator/app.py
apps/calculator/ui/calculator_app.py
apps/calculator/ui/tabs/ahri210240_tab.py
apps/calculator/ui/sections/ahri_seer2_section.py
apps/calculator/ui/ahri/
apps/calculator/application/ahri/seer2_adapter.py
apps/calculator/adapters/ahri_calculator_factory.py

core/calculators/profiles.py
core/calculators/dispatcher.py
core/calculators/capability/requests.py
core/calculators/capability/gateway.py
core/calculators/standards/ahri_seer2.py
core/calculators/standards/ahri_hspf2.py
core/calculators/standards/_ahri/seer2_variable.py
core/calculators/standards/_ahri/hspf2_context.py
core/calculators/standards/_ahri/hspf2_performance.py
core/calculators/standards/_ahri/hspf2_variable.py
```

## External references reviewed

```text
DOE Appendix M
https://www.law.cornell.edu/cfr/text/10/appendix-M_to_subpart_B_of_part_430

AHRI SEER/HSPF Calculation App
https://seerhspf2.ahrianalytics.org/app_direct/seer2hspf2/

AHRI 210/240-2017
https://www.ahrinet.org/system/files/2023-06/AHRI_Standard_210-240_2017.pdf

10 CFR §429.16
https://www.law.cornell.edu/cfr/text/10/429.16
```

---

# 43. Final design decision

이 기능의 architecture 핵심은 다음 한 문장으로 고정한다.

> **AHRI 210/240 M의 SEER/HSPF는 M1의 SEER2/HSPF2와 같은 calculator family에 속하지만 서로 다른 seasonal calculation policy를 가진 독립 domain capability이며, UI에서는 M과 M1을 top-level standard surfaces로 분리하고 core에서는 기존 profile/dispatcher/capability architecture를 통해 각각의 formula owner로 route한다.**
