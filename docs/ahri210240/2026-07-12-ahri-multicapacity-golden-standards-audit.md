# AHRI Multi-capacity Golden Standards Audit

**Status:** Audit complete — implementation not started  
**Target standard:** AHRI Standard 210/240-2026 (I-P)  
**External oracle reviewed:** AHRI Analytics Appendix M / Appendix M1 calculation app  
**Fixture branch reviewed:** `codex/ahri-multicapacity-golden-20260712` at `b32acd70b04172333a5fce5d81c6d3851ca39044`  
**Recommended repo location:** `docs/ahri210240/2026-07-12-multicapacity-golden-standards-audit.md`

---

## 1. Audit question

The repository now contains official AHRI Analytics raw evidence for:

1. Dual-stage SEER
2. Dual-stage HSPF
3. Triple-stage northern heat-pump HSPF

The fixtures preserve Appendix M and Appendix M1 outputs separately. This audit determines which Appendix M1 values can be used directly as AHRI 210/240-2026 SEER2/HSPF2 golden values and which values require correction or replacement.

This audit does not modify production formulas, fixture raw evidence, public APIs, capability routing, application code, or UI.

---

## 2. Source hierarchy

### Normative target

- AHRI Standard 210/240-2026 (I-P)
- Relevant sections:
  - Table 7 and Table 8
  - Section 6.1.2
  - Section 6.1.3.1 and Section 6.1.3.2
  - Section 11.2.1.2
  - Section 11.2.2.1 and Section 11.2.2.2
  - Section 11.2.2.6
  - Table 15 and Table 16

### Official external evidence

- AHRI Analytics SEER/HSPF calculation app
- The app labels its two result paths as Appendix M and Appendix M1.
- The downloaded raw fields are prefixed `M.*` and `M1.*`.

### Regulatory boundary

The eCFR Appendix M note requires representations made on or after January 1, 2023 to use Appendix M1. Appendix M is the legacy SEER/HSPF path. Consequently:

- `M1.SEER` is the relevant external comparator for SEER2.
- `M1.HSPF` is the relevant external comparator for HSPF2.
- `M.SEER` and `M.HSPF` remain useful raw legacy evidence but are not 2026 SEER2/HSPF2 goldens.

---

## 3. Executive verdict

| Fixture result | 2026 status | Permitted use |
|---|---|---|
| Dual-stage SEER2 `M1` | **Direct 2026 golden candidate for covered branches** | Exact raw metric, bin loads, capacities, power, and covered case calculations |
| Dual-stage HSPF2 base `M1` | **Derived 2026 golden candidate** | Inputs, curves, loads, compressor energy and branch evidence are reusable; resistance energy and final raw HSPF2 must be recalculated with 3.412 |
| Dual-stage HSPF2 cut-out `M1` | **Derived 2026 golden candidate** | Availability branch evidence is reusable; resistance energy and final raw HSPF2 must be recalculated with 3.412 |
| Triple-capacity northern HSPF2 `M1` | **Partial oracle only** | Inputs, active-case evidence, building load, boost curve and active compressor-energy path; not the complete 2026 trace or direct final golden |
| Any `M` result | **Legacy only** | Provenance and legacy comparison; never the expected value for a 2026 SEER2/HSPF2 engine |

The current fixture collection is valid and should remain immutable as official raw evidence. A separate 2026 expected overlay should hold corrected or hand-derived values.

---

## 4. Dual-stage SEER2 audit

### 4.1 Test-point mapping

The fixture maps directly to the 2026 two-stage cooling points:

| Fixture field | 2026 point |
|---|---|
| `coolCapacity95full`, corresponding power | AFull |
| `coolCapacity82full`, corresponding power | BFull |
| `coolCapacity82min`, corresponding power | BLow |
| `coolCapacity67min`, corresponding power | FLow |

These are the required steady-state inputs used by Section 11.2.1.2.

### 4.2 Independent calculation

The 2026 calculation was independently reproduced using:

- Table 15 temperatures and fractional bin hours
- Equation 11.69 building load
- Equation 11.71 through Equation 11.74 stage curves
- Case 1, Case 2 and Case 4 formulas
- Section 6.1.3.1.4 cooling degradation rule

The input low-stage cooling degradation coefficient is `0.24`. The 2026 two-capacity maximum/default is `0.20`; the effective coefficient is therefore `0.20`.

### 4.3 Numerical result

| Quantity | Independent 2026 | AHRI Analytics M1 |
|---|---:|---:|
| Seasonal cooling aggregate | 17117.202797202794 | 17117.2027972028 |
| Seasonal energy aggregate | 1374.4302560987994 | 1374.4302560988 |
| Raw SEER2 | 12.454035205677503 | 12.4540352056775 |
| Difference | 3.6e-15 | — |

The values match to floating-point precision.

### 4.4 Covered cases

| 2026 case | Coverage |
|---|---|
| Case 1 — low stage cycles with off | Covered: bins 1–4 |
| Case 2 — alternates low/full | Covered: bins 5–7 |
| Case 3 — full stage cycles with off due to low-stage lockout | **Not covered** |
| Case 4 — continuous full stage | Covered: bin 8 |

### 4.5 Verdict

`M1.SEER = 12.4540352056775` is accepted as a direct 2026 golden candidate for this fixture’s test-point and branch scope.

It must not be treated as proof of Case 3. A separate low-capacity-lockout cooling fixture is required before the two-stage SEER2 engine is considered branch-complete.

---

## 5. Dual-stage HSPF2 audit

### 5.1 Test-point mapping

The base and cut-out fixtures map to:

| Fixture field | 2026 point |
|---|---|
| 62°F minimum | H0Low |
| 47°F full / minimum | H1Full / H1Low |
| 35°F full / minimum | H2Full / H2Low |
| 17°F full / minimum | H3Full / H3Low |
| 5°F full when enabled | H4Full |

The base fixture does not use H4Full. The cut-out fixture enables H4Full.

### 5.2 Confirmed equivalence

The following M1 values match the 2026 equations:

- Region IV building load from Equation 11.106
- Table 16 fractional bin hours
- Low-stage interpolation from Equation 11.149 through Equation 11.154
- Full-stage interpolation with and without H4Full
- Case 1, Case 2 and Case 4 compressor-energy paths
- Low/full degradation coefficients supplied by the fixture
- Cut-out states `1`, `0.5`, and `0`

### 5.3 Confirmed incompatibility: 3.413 versus 3.412

AHRI Analytics Appendix M1 resistance-energy output uses a Btu/Wh divisor of **3.413**. AHRI 210/240-2026 equations use **3.412**, including Equation 11.156, Equation 11.171 and the equivalent resistance-heat formulas.

This was not inferred from display rounding. Solving each non-zero M1 resistance bin reproduces an exact divisor of 3.413.

Therefore:

```text
RH_2026 = RH_M1 × 3.413 / 3.412
```

The raw M1 resistance values and final M1 HSPF cannot be copied unchanged into strict 2026 formula tests.

### 5.4 Base fixture result

Inputs include `Fdef = 1.03`.

| Quantity | AHRI Analytics M1 | Recalculated 2026 |
|---|---:|---:|
| Seasonal load aggregate | 10398.99 | 10398.99 |
| Compressor energy | 934.5634003919118 | 934.5634003919118 |
| Resistance energy | 315.32604095452024 | 315.41845773088437 |
| Raw HSPF2 | 8.5695257081792 | **8.56889212463095** |

Formula used:

```text
HSPF2_2026 =
    10398.99
    / (934.5634003919118 + 315.41845773088437)
    × 1.03
```

### 5.5 Cut-out fixture result

The fixture has `T_off = 35°F`, `T_on = 45°F`, no demand-defrost multiplier, and exact availability coverage:

- available: 4 bins
- fractional: 2 bins
- unavailable: 12 bins

| Quantity | AHRI Analytics M1 | Recalculated 2026 |
|---|---:|---:|
| Seasonal load aggregate | 10398.99 | 10398.99 |
| Compressor energy | 167.7699938393656 | 167.7699938393656 |
| Resistance energy | 2504.2572516847345 | 2504.9912075029306 |
| Raw HSPF2 | 3.89179789143965 | **3.890729181034762** |

The fixture is strong evidence for the cut-out availability states after the cut-in and cut-out temperatures are known. It does not validate the upstream Appendix J procedure that determines those temperatures or its significant-digit requirements.

### 5.6 Covered cases

| 2026 case | Base | Cut-out |
|---|---|---|
| Case 1 — low stage cycles with off | Covered | Covered, including fractional availability |
| Case 2 — alternates low/full | Covered | Load relation present |
| Case 3 — full stage cycles with off because low stage is locked out | **Not covered** | **Not covered**; `lockOutLowCapacityOps` is false |
| Case 4 — full stage plus supplemental heat | Covered | Covered with unavailable compressor bins |

### 5.7 Verdict

Both dual-stage HSPF2 fixtures are accepted as **derived** 2026 golden candidates.

Use:

- the official raw input and compressor-side evidence unchanged;
- 2026-recalculated resistance energy;
- the 2026-recalculated raw HSPF2 shown above.

Do not assert direct equality to `M1.HSPF`.

A separate fixture with low-stage lockout enabled is required to cover Case 3.

---

## 6. Triple-capacity northern HSPF2 audit

### 6.1 Required 2026 boundary

AHRI 210/240-2026 explicitly lists a technical correction for the triple-capacity northern heat pump. Section 11.2.2.6 defines:

- Low, Full and Boost stage performance
- manufacturer stage-operating temperature ranges
- Case 1 through Case 8
- H2Boost fallback
- H3Boost and H4Boost interpolation
- triple-capacity-specific treatment of H2Low
- substitution of H4Boost for H4Full in the low-temperature Full-stage curve

The Appendix M1 raw output must therefore be compared equation by equation rather than accepted based only on the final displayed HSPF.

### 6.2 Parts that match the active 2026 path

For the current synthetic stage ranges:

- Low: 40°F to 65°F
- Full: 20°F to 50°F
- Boost: -20°F to 30°F

the active M1 path is:

| Temperature bins | Raw case |
|---|---|
| 62°F through 42°F | Case 1 |
| 37°F through 22°F | Case 2 |
| 17°F | Case 3 |
| 12°F through -18°F | Case 8 |
| -23°F | raw `0`; Region IV fractional hours are zero |

The independent 2026 reconstruction matches:

- Region IV building load
- active Low-stage curves at 42°F and above
- active Full-stage curves from 37°F through 22°F
- Boost-stage interpolation at 17°F and below
- Case 1, Case 2, Case 3 and Case 8 compressor energy
- effective low/full degradation handling
- the raw case sequence for the active fixture

The M1 compressor-energy aggregate matches exactly:

```text
975.3371449127085
```

### 6.3 Technical-correction mismatch: H2Low treatment

The fixture provides:

```text
H1Low = 21000 Btu/h, 1300 W
H2Low input = 18500 Btu/h, 1550 W
H3Low = 14500 Btu/h, 1750 W
H3Low tested = true
```

Section 11.2.2.6 Equation 11.253 and Equation 11.254 instead produce:

```text
H2Low capacity = 16560 Btu/h
H2Low power    = 1457.8 W
```

AHRI Analytics M1 uses the supplied 35°F Low value directly. As a result, its Low-stage diagnostic curve at 37°F, 32°F, 27°F and 22°F differs from the 2026 curve.

These bins do not affect the current fixture’s final HSPF because Low stage is not permitted below 40°F. They still make the complete raw curve trace unsuitable as a direct 2026 golden.

### 6.4 Technical-correction mismatch: H4Boost substitution in Full curve

For a triple-capacity northern heat pump, Section 11.2.2.1.1 instructs the Full-stage low-temperature curve to substitute H4Boost for H4Full.

AHRI Analytics M1 continues the H1Full-to-H3Full line below 17°F. Examples:

| Temperature | M1 Full capacity | 2026 Full capacity |
|---|---:|---:|
| 12°F | 21000 | 23250 |
| 7°F | 20000 | 24500 |
| 2°F | 19000 | 25750 |
| -8°F | 17000 | 28250 |
| -18°F | 15000 | 30750 |

Power differs in the same region.

The Full stage is not permitted below 20°F in this fixture, so the mismatch is inactive for the final metric. It would become material in another stage-range configuration and in Cases 5 or 7.

### 6.5 Resistance conversion mismatch

The M1 resistance aggregate again uses 3.413:

| Quantity | M1 | 2026 conversion |
|---|---:|---:|
| Resistance energy | 89.26457661881034 | 89.29073856975371 |

### 6.6 Demand-defrost ambiguity

The input records:

```text
demandDefrostCredit = 1.028571429
```

The M1 headline implies an internally used factor of approximately:

```text
1.0286
```

AHRI 210/240-2026 Equation 11.107 derives `Fdef` from defrost timing inputs. The fixture does not preserve `Ttest` and `Tmax`, so it cannot prove the exact 2026 intermediate factor or an allowed intermediate rounding rule.

Using the preserved input factor without intermediate rounding gives a candidate:

```text
HSPF2_2026_candidate =
    10398.99
    / (975.3371449127085 + 89.29073856975371)
    × 1.028571429
  = 10.046800549191993
```

Using 1.0286 gives:

```text
10.04707962279874
```

The raw M1 result is:

```text
10.0473265237749
```

### 6.7 Covered cases

| Triple-capacity case | Coverage |
|---|---|
| Case 1 — Low cycles with off | Covered |
| Case 2 — Full cycles with off | Covered |
| Case 3 — Boost cycles with off | Covered |
| Case 4 — alternates Low/Full | **Not covered** |
| Case 5 — alternates Full/Boost | **Not covered** |
| Case 6 — continuous Low plus supplemental heat | **Not covered** |
| Case 7 — continuous Full plus supplemental heat | **Not covered** |
| Case 8 — continuous Boost or resistance-only | Covered |

### 6.8 Verdict

The current Triple Northern M1 fixture is **not** a direct or complete 2026 golden.

It may be used for:

- official raw input provenance;
- Region IV building-load evidence;
- active Case 1/2/3/8 classification;
- active compressor-energy calculations;
- Boost interpolation in the covered range.

It must not be used unchanged for:

- the full curve trace;
- low-stage diagnostics below the permitted Low range;
- resistance-energy exact values;
- final raw HSPF2;
- Cases 4 through 7;
- demand-defrost intermediate behavior.

A 2026 hand-derived expected fixture and additional branch fixtures are required.

---

## 7. Rounding boundary

AHRI 210/240-2026 Section 6.1.2 states that published EER2, SEER2 and HSPF2 values are expressed in increments of the nearest 0.05 Btu/(W·h).

The AHRI Analytics screen values are ordinary two-decimal displays. They are not evidence of the Section 6.1.2 published-rating rounding rule.

Examples:

| Raw 2026 metric | Screen-style 2 decimals | Nearest 0.05 |
|---:|---:|---:|
| Dual-stage SEER2 12.4540352057 | 12.45 | 12.45 |
| Dual-stage HSPF2 8.5688921246 | 8.57 | 8.55 |
| Dual cut-out HSPF2 3.8907291810 | 3.89 | 3.90 |
| Triple candidate 10.0468005492 | 10.05 | 10.05 |

The current variable-capacity HSPF2 production contract rounds to 0.025 increments. That behavior is protected by existing official-calculator golden tests and must not be changed as part of multi-capacity implementation.

For new multi-capacity engines, the result contract must explicitly distinguish:

- raw formula metric;
- presentation value, if needed;
- 2026 published-rating value rounded to the nearest 0.05.

Do not silently reuse the current 0.025 helper for the new product types.

---

## 8. Golden acceptance policy

### 8.1 Keep raw official evidence immutable

Do not rewrite:

- `input.csv`
- `result_m.csv`
- `result_m1.csv`
- checksums
- provenance of what the official application returned

### 8.2 Add a separate 2026 expected layer

A future implementation slice should add a small, explicit standards-derived overlay rather than changing the official fixture:

```text
official raw evidence
    +
2026 applicability/expected overlay
    =
engine golden contract
```

The overlay should identify each expected field as one of:

- `direct_m1`
- `recalculated_2026`
- `partial_evidence_only`
- `not_applicable_to_2026`
- `unresolved`

### 8.3 Accepted exact metrics

| Fixture | Accepted 2026 raw metric |
|---|---:|
| Dual-stage SEER2 synthetic 01 | 12.4540352056775 |
| Dual-stage HSPF2 synthetic 01 | 8.56889212463095 |
| Dual-stage HSPF2 cut-out synthetic 01 | 3.890729181034762 |
| Triple Northern synthetic 01 | **Not accepted yet** |

---

## 9. Additional evidence required before implementation closeout

### Dual-stage SEER2

Add one fixture that activates:

- Case 3
- low-capacity lockout
- Full-stage cycling degradation

### Dual-stage HSPF2

Add one fixture that activates:

- low-stage lockout;
- Case 3, off ↔ Full;
- Full-stage degradation under that path.

The existing cut-out fixture tests total compressor availability but does not set `lockOutLowCapacityOps`.

### Triple-capacity northern HSPF2

At least the following evidence is still required:

1. A no-demand-defrost or `Fdef = 1` case to isolate the 2026 formula.
2. A Case 4 Low ↔ Full case.
3. A Case 5 Full ↔ Boost case.
4. A Case 6 Low continuous plus resistance case.
5. A Case 7 Full continuous plus resistance case.
6. H2Boost not tested, exercising Equation 11.259 and Equation 11.260.
7. A stage-range configuration where the corrected H4Boost substitution becomes active.
8. A controlled H3Low/H2Low configuration that verifies Equation 11.253 and Equation 11.254.

The AHRI Analytics M1 output remains valuable evidence for these cases, but corrected triple-capacity fields must be derived from the 2026 equations rather than copied automatically.

---

## 10. Implementation gates

Before adding multi-capacity engines:

1. Preserve the current variable-capacity official goldens and public contract.
2. Add a fixture applicability/2026 expected layer.
3. Implement Dual-stage SEER2 against its accepted direct golden and a new Case 3 fixture.
4. Implement Dual-stage HSPF2 against recalculated 2026 goldens and a new low-stage-lockout fixture.
5. Implement Triple Northern only after the missing Case 4–7 and correction-focused evidence is available.
6. Keep product-specific point resolution and formula engines as siblings of the existing variable-capacity engine.
7. Keep raw, presentation, and published-rating rounding explicit.

---

## 11. Final audit decision

### Approved now

- Existing fixture collection and provenance
- Dual-stage SEER2 M1 as a direct golden for the covered scope
- Dual-stage HSPF2 inputs, curves, compressor calculations and branch evidence
- Derived 2026 Dual-stage HSPF2 expected values
- Triple Northern M1 as partial official evidence

### Not approved yet

- Direct use of `M1.HSPF` for Dual-stage 2026 HSPF2
- Direct use of any Triple Northern M1 final or complete trace as a 2026 golden
- Multi-capacity implementation closeout with the current branch coverage
- Reuse of screen two-decimal values as standard published ratings
- Automatic reuse of the current 0.025 HSPF2 rounding helper for new engines
