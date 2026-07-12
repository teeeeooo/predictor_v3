# AHRI 210/240-2026 Multi-capacity Core + Calculator GUI Implementation Design

**Status:** Ready for implementation  
**Goal:** Complete the AHRI multi-capacity calculation core and finish the Tkinter Calculator GUI connection in one implementation workstream  
**Implementation scope:** Dual-stage SEER2, Dual-stage HSPF2, Triple-capacity Northern HSPF2  
**Canonical document location:** `docs/designs/2026-07-12-ahri-multicapacity-core-calculator-gui-design.md`

---

## 1. Purpose

This document is both the implementation design and the execution brief for extending the existing AHRI 210/240 calculator from the current variable-capacity-only behavior to the following product paths:

1. Dual-stage SEER2
2. Dual-stage HSPF2
3. Triple-capacity Northern HSPF2

The completed state is not merely a formula library. The target is an end-to-end Calculator capability:

```text
Tkinter Calculator GUI
    -> Calculator application adapter
    -> standard calculation capability
    -> stable AHRI facade
    -> product-specific multi-capacity engine
    -> result/diagnostic contract
    -> Calculator result panel and bin detail
```

Additional AHRI Analytics fixture collection is not part of this work. Existing official raw evidence, the completed standards audit, the AHRI 210/240-2026 PDF, and deterministic equation-level tests are the approved evidence set.

---

## 2. Mandatory implementation references

Before changing code, the agent must inspect and use the following sources.

### 2.1 Repository standards audit

Locate the repository document by exact filename:

```text
2026-07-12-ahri-multicapacity-golden-standards-audit.md
```

Its expected canonical location is under the AHRI documentation area, but the exact path must be confirmed in the current branch.

This document defines:

- where AHRI Analytics Appendix M1 can be used directly;
- where a 2026 correction must be applied;
- accepted Dual-stage expected values;
- the Triple Northern partial-oracle boundary;
- the `3.412` resistance conversion;
- published-rating rounding;
- the missing official-fixture coverage that must instead be proven through equation-level tests.

### 2.2 Normative PDF

Read the local normative source:

```text
~/Downloads/AHRI Standard 210.240-2026 I-P.3.20.pdf
```

The implementation must be mapped back to the normative PDF, especially:

- Table 7
- Table 8
- Table 15
- Table 16
- Section 6.1.2
- Section 6.1.3.1
- Section 6.1.3.2
- Section 11.2.1.2
- Section 11.2.2.1
- Section 11.2.2.2
- Section 11.2.2.6

Equation numbers and fallback conditions must be confirmed from the PDF before implementation. The standards-audit document is an implementation guide, not a replacement for checking the normative text.

### 2.3 Existing repository owners

Audit the current sibling owners before selecting exact files or class names:

- stable AHRI facades;
- internal `_ahri` owners created by the completed refactor;
- capability request and gateway;
- Calculator application AHRI adapters;
- Calculator AHRI tab and SEER2/HSPF2 sections;
- product-specific batch profiles;
- result and bin-detail schema owners;
- existing variable-capacity official goldens and contract-lock tests.

The existing call direction must remain:

```text
UI
    -> application adapter
    -> capability request
    -> capability gateway/profile/dispatcher
    -> stable standard facade
    -> internal engine
```

The UI must not import a standard engine directly.

---

## 3. Confirmed decisions

| Topic | Decision |
|---|---|
| Overall goal | Finish the calculation core and Calculator GUI in the same workstream. |
| Product scope | Dual-stage SEER2, Dual-stage HSPF2, Triple-capacity Northern HSPF2. |
| Variable-capacity path | Preserve current behavior, public method signatures, golden outputs, diagnostics, and existing GUI behavior. |
| Additional official fixtures | Do not collect more. |
| Missing official branches | Validate with deterministic equation-level synthetic tests derived from the 2026 PDF. |
| Official raw fixture policy | Do not rewrite input/result CSVs, checksums, or provenance. |
| SEER2 direct oracle | Use the existing Dual-stage M1 fixture where the audit approved direct parity. |
| HSPF2 oracle | Use standards-derived 2026 expected values rather than direct equality to raw M1 HSPF. |
| Triple Northern oracle | Use current M1 evidence only for approved partial fields and cases; verify the full implementation from the PDF. |
| Resistance conversion | New 2026 multi-capacity HSPF2 paths use `3.412`. |
| Published rating | New multi-capacity published SEER2/HSPF2 uses nearest `0.05`; raw metric remains separately available. |
| Current 0.025 behavior | Do not change the protected existing variable-capacity HSPF2 rounding behavior. |
| Engine structure | Add product-specific sibling engines behind the stable facades. |
| UI structure | Keep the current AHRI tab and SEER2/HSPF2 metric navigation; add product-aware surfaces inside each metric section. |
| Batch | Extend product-aware batch behavior after the main single-case surface works. |
| Unsupported combinations | Reject explicitly rather than silently coercing to another product path. |

---

## 4. Current state and constraints

### 4.1 Existing Calculator composition

The current Calculator AHRI tab already owns:

- a scrollable content surface;
- an inner notebook with `SEER2` and `HSPF2`;
- an SEER2 section;
- an HSPF2 section;
- lifecycle-aware refitting when metric tabs or detail panels change.

This shell should remain. Multi-capacity support belongs inside the existing metric sections rather than in a new top-level AHRI tab.

### 4.2 Existing SEER2 surface

The current SEER2 section owns:

- HP/AC selector;
- fixed five-point variable-capacity matrix;
- automatic calculation;
- result panel;
- batch dialog;
- bin-detail panel;
- Copy and CSV result actions.

The existing five-point matrix is the variable-capacity surface and must remain unchanged when that product is selected.

### 4.3 Existing HSPF2 surface

The current HSPF2 section owns:

- Region IV selector;
- measured optional-point flags;
- variable-capacity-specific flags;
- numeric option table;
- A2 cooling-capacity anchor;
- variable-capacity heating-point matrix;
- automatic calculation;
- result panel;
- batch access;
- bin-detail panel.

The current option names and point matrix describe the variable-capacity path. They must not be stretched into a misleading union of Variable, Dual-stage, and Triple Northern fields.

### 4.4 Application boundary

Current Calculator adapters:

- parse UI text;
- validate required and optional fields;
- create typed AHRI capability requests;
- call `execute_standard_calculation`;
- translate core result mappings into UI summary models.

This remains the application owner. Product classification and product-specific input normalization must be introduced here or immediately below this boundary, not in Tk widget code and not by bypassing capability execution.

---

## 5. Target architecture

### 5.1 High-level composition

```text
AHRI SEER2 facade
    -> product selector
        -> existing Variable-capacity SEER2 engine
        -> Dual-stage SEER2 engine

AHRI HSPF2 facade
    -> product selector
        -> existing Variable-capacity HSPF2 engine
        -> Dual-stage HSPF2 engine
        -> Triple-capacity Northern HSPF2 engine
```

The stable facade import paths and public methods remain the canonical entrypoints.

A caller that does not provide product classification must continue to receive the current variable-capacity behavior.

### 5.2 Product classification

Support the following semantic product classifications:

```text
variable_capacity
dual_stage
triple_capacity_northern
```

Supported combinations:

| Metric | Product classification |
|---|---|
| SEER2 | `variable_capacity`, `dual_stage` |
| HSPF2 | `variable_capacity`, `dual_stage`, `triple_capacity_northern` |

Do not infer classification solely from which point keys happen to be present. Classification must be explicit at the application/capability boundary.

The exact enum, literal, or validated string owner should follow the current repository convention after audit. Do not introduce a broad registry or generic standards taxonomy solely for this feature.

### 5.3 Dependency direction

Approved dependency direction:

```text
Tk widgets
    -> Calculator application models/adapters
    -> capability request/gateway
    -> AHRI facade
    -> product-specific resolver/context/engine/result owner
```

Forbidden direction:

```text
Tk widget
    -> internal _ahri engine
```

The Calculator UI may depend on UI-only point schemas and labels. It may not own AHRI interpolation, case classification, fallback, or seasonal equations.

### 5.4 Internal owner boundaries

Use the completed refactor seams. The exact physical files should be chosen after inspecting sibling owners, but responsibilities must remain distinct:

1. **Product selection**
   - validate supported metric/product combination;
   - route to the correct engine;
   - preserve variable default behavior.

2. **Point contract and resolution**
   - normalize product-specific point names;
   - validate required points and positive values;
   - resolve tested, optional, calculated, and fallback points;
   - preserve source metadata.

3. **Seasonal context**
   - region/bin table;
   - building-load parameters;
   - degradation coefficients;
   - stage operating temperature ranges;
   - low-stage lockout;
   - compressor cut-in/cut-out;
   - defrost inputs;
   - DHR selection or resolved design load.

4. **Performance curves**
   - Low, Full, and where applicable Boost capacity/power by temperature;
   - only share interpolation primitives proven to be identical.

5. **Seasonal engine**
   - determine permitted stages;
   - determine compressor availability;
   - select the standard case;
   - compute delivered load and energy;
   - aggregate seasonal totals.

6. **Result assembly**
   - raw metric;
   - published rating;
   - seasonal totals;
   - point/fallback metadata;
   - bin diagnostics;
   - formula-path metadata.

Avoid:

- one giant generic AHRI engine;
- a large product-type conditional inside the existing variable engine;
- one class per equation;
- a new generic standards DSL;
- sharing product-specific case formulas merely because names look similar.

---

## 6. Public and capability contracts

### 6.1 Stable facade methods

Preserve the current public entrypoints:

```text
calculate_seer2(...)
calculate_hspf2(...)
```

The exact compatible extension should be chosen after inspecting existing calls. Preferred direction:

- add explicit product classification as a backward-compatible keyword or request parameter;
- keep omitted classification mapped to `variable_capacity`;
- do not add separate public methods for every product unless an existing repository convention requires it.

The existing direct-call tests and capability path must continue to work.

### 6.2 Capability request extension

Extend the AHRI request contracts minimally.

Conceptual requirement:

```text
AhriSeer2Request
    test_points
    system_type
    product_classification = variable_capacity
    parameters/options

AhriHspf2Request
    test_points
    product_classification = variable_capacity
    parameters/options
```

Requirements:

- old request construction remains valid;
- product classification is validated before facade execution;
- unsupported SEER2 Triple Northern fails explicitly;
- product-specific options are carried as a mapping or typed nested model consistent with repository practice;
- UI-only labels must not leak into the core point contract.

### 6.3 Profile and dispatcher

Do not create a separate calculator profile for every product unless the profile owner clearly requires product-level separation.

Preferred direction:

```text
existing AHRI SEER2 profile
    -> same facade
    -> product classification selects variable or dual-stage

existing AHRI HSPF2 profile
    -> same facade
    -> product classification selects variable, dual-stage, or triple northern
```

Preserve existing capability IDs:

```text
ahri210240.seer2
ahri210240.hspf2
```

The feature is a product-path extension of the same standard capability, not a new top-level capability family.

---

## 7. Core formula requirements

### 7.1 Dual-stage SEER2

Implement the AHRI 210/240-2026 two-stage cooling path defined by the normative PDF.

#### 7.1.1 Required point semantics

Primary point contract:

| Semantic point | Meaning |
|---|---|
| AFull | Full-stage cooling at A condition |
| BFull | Full-stage cooling at B condition |
| BLow | Low-stage cooling at B condition |
| FLow | Low-stage cooling at F condition |

Optional or conditional points should only be added when the audited standard path actually consumes them.

The UI and application adapter may use product-friendly display labels, but the core must receive stable semantic point identifiers.

#### 7.1.2 Seasonal cases

Support all two-stage cooling cases.

**Case 1 — Low stage cycles**

Condition:

```text
building load <= permitted Low-stage capacity
```

Behavior:

- Low stage cycles;
- apply Low-stage cycling degradation;
- no unnecessary Full-stage interpolation.

**Case 2 — Low and Full alternation**

Condition:

```text
Low capacity < building load < Full capacity
```

Behavior:

- interpolate/alternate between Low and Full according to the standard;
- calculate delivered cooling and energy from the specified case equations.

**Case 3 — Full stage cycles because Low is locked out**

Condition includes:

```text
Low stage not permitted
building load < Full capacity
```

Behavior:

- Full stage cycles;
- apply Full-stage degradation;
- do not misclassify as Case 2 or Case 4.

**Case 4 — Full stage continuous**

Condition:

```text
building load >= Full capacity
```

Behavior:

- Full stage operates continuously;
- delivered cooling is limited by available Full capacity where required by the standard.

#### 7.1.3 Seasonal result

Provide:

- Table 15 bin trace;
- building load;
- Low/Full capacity and power;
- stage-permission state;
- selected case;
- cycling/load factors;
- bin cooling;
- bin energy;
- seasonal cooling;
- seasonal energy;
- raw SEER2;
- published SEER2 rounded to nearest 0.05.

#### 7.1.4 Accepted official comparison

The existing Dual-stage SEER2 fixture has accepted direct 2026 parity:

```text
raw SEER2 = 12.4540352056775
```

The implementation must reproduce this value within the repository’s approved numerical tolerance.

The existing fixture covers Cases 1, 2, and 4. Case 3 must be proven with a deterministic PDF-derived test.

---

### 7.2 Dual-stage HSPF2

Implement the AHRI 210/240-2026 two-stage heating path.

#### 7.2.1 Required point semantics

Primary point contract:

| Semantic point | Meaning |
|---|---|
| H0Low | Low-stage heating at H0 |
| H1Low | Low-stage heating at H1 |
| H1Full | Full-stage heating at H1 |
| H2Low | Low-stage heating at H2 when tested/applicable |
| H2Full | Full-stage heating at H2 |
| H3Low | Low-stage heating at H3 when tested/applicable |
| H3Full | Full-stage heating at H3 |
| H4Full | Full-stage low-temperature point when tested/applicable |

Optional/tested flags and fallback rules must come from Table 8 and the relevant 2026 clauses.

#### 7.2.2 Seasonal cases

Support all two-stage heating cases.

**Case 1 — Low stage cycles**

- Low stage is permitted;
- building load is below Low-stage capacity;
- apply Low-stage cycling degradation;
- compressor availability may be available, fractional, or unavailable.

**Case 2 — Low and Full alternation**

- both stages are permitted;
- building load lies between Low and Full;
- interpolate/alternate according to the standard.

**Case 3 — Full stage cycles because Low is locked out**

- Low stage is not permitted by the low-stage operating limit;
- Full stage is permitted;
- building load is below Full capacity;
- apply Full-stage cycling degradation.

This is distinct from total compressor cut-out.

**Case 4 — Full stage continuous with supplemental heat as required**

- Full stage operates continuously;
- supplemental resistance heat supplies the unmet building load;
- compressor availability and total cut-out remain separate state dimensions.

#### 7.2.3 Availability and supplemental heat

Keep these concepts separate:

```text
load-capacity relationship
low-stage permission
full-stage permission
compressor availability
supplemental resistance heat
selected standard case
```

Compressor availability states:

```text
available
fractional
unavailable
```

Resistance heat must use the 2026 conversion constant:

```text
3.412 Btu/Wh
```

Do not copy the Appendix M1 `3.413` resistance result into the 2026 engine.

#### 7.2.4 Defrost

The core must support the 2026 defrost boundary without guessing missing inputs.

Approved behavior:

- retain the existing variable-capacity defrost contract unchanged;
- introduce the minimum product-specific input needed for the new multi-capacity path;
- support an explicit no-credit/factor-1 path;
- support an explicit validated factor override if that is consistent with current repository ownership;
- implement timing-derived demand-defrost credit only when the PDF inputs are present and mapped.

Diagnostics must state whether the factor was:

```text
none
explicit_override
calculated_from_timing
```

Do not hide an assumed demand-defrost default.

#### 7.2.5 Accepted 2026 expected values

Base Dual-stage fixture:

```text
raw HSPF2 = 8.56889212463095
```

Cut-out fixture:

```text
raw HSPF2 = 3.890729181034762
```

These are standards-derived 2026 values. Exact equality to the raw Appendix M1 HSPF is not expected because the 2026 engine uses `3.412`.

The test must show that the difference is explained by the resistance conversion rather than by unrelated formula drift.

---

### 7.3 Triple-capacity Northern HSPF2

Implement the AHRI 210/240-2026 Triple-capacity Northern path, including the 2026 technical correction.

#### 7.3.1 Stage model

The engine owns three distinct heating stages:

```text
Low
Full
Boost
```

Each stage has:

- capacity curve;
- power curve;
- lower operating-temperature bound;
- upper operating-temperature bound;
- tested/calculated/fallback point provenance.

Stage permission is determined before case selection.

#### 7.3.2 Required point semantics

Primary contract:

| Semantic point | Meaning |
|---|---|
| H0Low | Low at H0 |
| H1Low | Low at H1 |
| H1Full | Full at H1 |
| H2Low | Low at H2, tested or calculated per 2026 |
| H2Full | Full at H2 |
| H2Boost | Boost at H2, tested or fallback per 2026 |
| H3Low | Low at H3 where applicable |
| H3Full | Full at H3 |
| H3Boost | Boost at H3 |
| H4Boost | Boost at H4 |

The exact required/optional combinations must follow Table 8 and Section 11.2.2.6.

#### 7.3.3 Cases 1 through 8

Implement all eight standard cases.

**Case 1 — Low cycles with off**

- Low permitted;
- load below Low capacity.

**Case 2 — Full cycles with off**

- Low unavailable/not permitted for the applicable path;
- Full permitted;
- load below Full capacity.

**Case 3 — Boost cycles with off**

- lower stages unavailable/not permitted for the applicable path;
- Boost permitted;
- load below Boost capacity.

**Case 4 — Low and Full alternation**

- Low and Full permitted;
- load between Low and Full capacities.

**Case 5 — Full and Boost alternation**

- Full and Boost permitted;
- load between Full and Boost capacities.

**Case 6 — Continuous Low plus resistance heat**

- only Low is the active permitted compressor stage for the case;
- load exceeds Low capacity;
- resistance supplies the remainder.

**Case 7 — Continuous Full plus resistance heat**

- Full is the active permitted compressor stage for the case;
- load exceeds Full capacity;
- resistance supplies the remainder.

**Case 8 — Continuous Boost or resistance-only**

- Boost operates continuously when available;
- resistance supplies unmet load;
- if compressor is unavailable, resistance-only behavior is explicit.

Case ordering and boundary equality must be confirmed against the PDF. Do not derive precedence merely from the numbering above.

#### 7.3.4 Mandatory 2026 corrections

**H2Low correction**

Implement the 2026 H2Low rule from Section 11.2.2.6.

Requirements:

- do not blindly use an Appendix M1 input H2Low when the 2026 rule requires a calculated value;
- preserve whether H2Low was tested, calculated, or inapplicable;
- expose source anchors and calculated value in diagnostics;
- equation-level tests must prove the corrected curve.

**H2Boost fallback**

When H2Boost is not tested:

- calculate it from the 2026 fallback equations;
- preserve source points and fallback reason;
- use the calculated point in the active Boost curve;
- test the fallback independently from seasonal aggregation.

**H4Boost substitution**

Where the 2026 Full-stage low-temperature curve requires H4Boost substitution:

- use H4Boost rather than reproducing the Appendix M1 H1Full–H3Full extrapolation;
- expose the substituted anchor in diagnostics;
- test a temperature where the corrected Full curve differs from the Appendix M1 trace.

**Resistance heat**

All new Triple Northern resistance energy uses `3.412`.

**Defrost**

Implement the same explicit defrost-source contract described for Dual-stage HSPF2.

#### 7.3.5 Existing official fixture boundary

The current official Triple Northern fixture is an approved partial oracle.

It may directly validate:

- input normalization;
- Region IV building load;
- active Case 1, 2, 3, and 8 labels for the covered fixture;
- active compressor-energy path where the standards audit found parity;
- approved Low/Full/Boost curve segments.

It may not be used as a direct oracle for:

- final raw HSPF2;
- complete curve traces;
- corrected H2Low;
- H2Boost fallback;
- H4Boost substitution;
- resistance-energy exact values;
- Cases 4, 5, 6, and 7;
- unresolved defrost intermediate behavior.

Those paths require PDF-derived equation tests.

---

## 8. Common numerical and result rules

### 8.1 Numerical primitives

Share only proven-identical primitives such as:

- safe division;
- linear interpolation;
- explicit decimal rounding helpers.

Do not share:

- product-specific stage permission;
- product-specific case selection;
- product-specific fallback rules;
- product-specific building-load equations unless the PDF and existing owners prove identity.

### 8.2 Non-negativity and conservation

For each bin:

```text
delivered load >= 0
compressor energy >= 0
resistance energy >= 0
total energy = compressor energy + resistance energy
```

For heating:

```text
delivered heating = compressor heating + resistance heating
```

within the approved numerical tolerance.

Seasonal totals must equal the sum of bin contributions.

### 8.3 Raw and published values

New multi-capacity result contracts distinguish:

```text
raw_metric
presentation_value
published_rating
```

Published rating uses nearest `0.05` with an explicit half-up rule consistent with Section 6.1.2.

Examples from the completed standards audit:

| Raw value | Published rating |
|---:|---:|
| 12.4540352056775 | 12.45 |
| 8.56889212463095 | 8.55 |
| 3.890729181034762 | 3.90 |

Do not route new multi-capacity HSPF2 through the existing protected variable-capacity nearest-0.025 helper.

---

## 9. Core result contract

### 9.1 Backward compatibility

Existing variable-capacity result mappings remain unchanged.

New keys may be added only to new multi-capacity paths unless the existing result contract explicitly permits additive metadata without breaking characterization tests.

### 9.2 Multi-capacity top-level result

The new product paths must expose enough information for both GUI and future non-GUI callers:

```text
raw metric
published rating
seasonal delivered load
seasonal compressor energy
seasonal resistance energy
seasonal total energy
bin details
point/fallback metadata
formula path
product classification
```

Suggested semantic fields:

```text
raw_seer2 / raw_hspf2
published_seer2 / published_hspf2
total_cooling_btu / total_heating_btu
total_compressor_energy_wh
total_resistance_energy_wh
total_energy_wh
bin_details
summary.metadata
```

Exact key names must be selected after auditing existing result owners and compatibility tests.

### 9.3 Bin diagnostics

Cooling detail should support:

- bin number;
- temperature;
- fractional hours;
- building load;
- Low/Full capacity and power;
- stage permission;
- selected Case 1–4;
- load/cycling factors;
- delivered cooling;
- electrical energy.

Heating detail should support:

- bin number;
- temperature;
- fractional hours;
- building load;
- Low/Full/Boost capacity and power as applicable;
- stage permission;
- compressor availability;
- selected case;
- HLF/PLF or equivalent factors;
- compressor heating/energy;
- resistance heating/energy;
- total heating/energy;
- point/fallback formula metadata.

Do not make GUI formatting parse free-form debug strings. The core should provide typed/structured fields.

---

## 10. Calculator application design

### 10.1 Product-aware UI models

The application layer should own product-specific UI contracts, for example:

```text
SEER2 product options
HSPF2 product options
product-specific required point list
product-specific optional/tested state
product-specific summary mapping
```

The exact model names are not prescribed. The key constraint is that Tk widget classes do not assemble core point aliases or formula kwargs ad hoc.

### 10.2 Adapter behavior

Each metric adapter must:

1. receive explicit product classification;
2. select the active application point schema;
3. parse only active surface values;
4. reject malformed active values;
5. ignore hidden values from inactive products;
6. create the capability request;
7. translate the core result to a UI summary and detail rows.

The current variable-capacity parsing behavior must remain unchanged.

### 10.3 Summary models

Extend summary models only as needed for the new GUI.

For new multi-capacity paths, the UI needs:

- raw metric;
- published rating;
- total seasonal load;
- compressor energy;
- resistance energy for heating;
- total energy;
- product classification;
- bin details.

Existing variable-capacity summary fields and display remain intact.

---

## 11. Calculator GUI design

### 11.1 Overall navigation

Keep the current AHRI tab:

```text
AHRI 210/240
    ├── SEER2
    └── HSPF2
```

Do not add separate top-level tabs for each product.

Each metric surface gains a product selector at the top.

**SEER2 product selector**

```text
Variable Capacity
Dual Stage
```

Default remains Variable Capacity.

**HSPF2 product selector**

```text
Variable Capacity
Dual Stage
Triple Stage Northern
```

Default remains Variable Capacity.

### 11.2 Product-surface composition

Do not create one giant union table containing every Variable, Dual, and Triple point.

Preferred behavior:

```text
Metric section shell
    -> product selector
    -> active product input surface
    -> shared result/action/detail area
```

The active product surface may be implemented through stacked frames, replaceable child composition, or another existing repository pattern.

Requirements:

- only active product fields are visible and submitted;
- switching product does not leave hidden stale values in the request;
- each product may retain an in-memory draft snapshot for user convenience;
- results and detail are cleared immediately on product change;
- automatic calculation resumes only when the new surface is complete;
- lifecycle/window refit is requested after the new surface settles.

Avoid destroying existing variable behavior merely to force all products through the same table definition.

### 11.3 SEER2 GUI

#### 11.3.1 Shared controls

Top control area:

- Product
- System Type: HP / AC

Variable Capacity continues to show the existing five-point matrix and existing behavior.

#### 11.3.2 Dual-stage options

Expose only inputs used by the implemented 2026 path:

- Low-stage lockout enabled;
- low-stage lockout outdoor temperature;
- Low-stage degradation coefficient;
- Full-stage degradation coefficient;
- off-mode power only if the standard path and existing facade contract actually consume it.

Defaults must come from the standard/config owner, not the Tk widget.

#### 11.3.3 Dual-stage point matrix

Recommended compact matrix:

| Row | AFull | BFull | BLow | FLow |
|---|---:|---:|---:|---:|
| Condition / Temp | static | static | static | static |
| Capacity [Btu/h] | input | input | input | input |
| Power [W] | input | input | input | input |
| EER2 | calculated | calculated | calculated | calculated |

Do not display the variable-only EInt column for Dual-stage.

Optional points should be added only if consumed by the audited implementation.

#### 11.3.4 Dual-stage result panel

Display:

```text
SEER2 Raw
SEER2 Published
Total Cooling [kBtu]
Total Energy [kWh]
```

Presentation precision should remain readable while CSV/detail retains raw precision.

### 11.4 HSPF2 GUI

#### 11.4.1 Shared controls

Shared control area:

- Product
- Region, currently IV
- DHR selection or the existing approved design-load input path
- compressor cut-out temperature
- compressor cut-in temperature
- defrost mode/source
- defrost factor or timing inputs according to active mode

Variable Capacity continues to use its current options and point layout.

Do not reinterpret current variable flags as Dual/Triple options.

#### 11.4.2 Dual-stage options

Expose:

- H4Full tested;
- H2Low tested when applicable;
- other tested/optional flags required by Table 8;
- Low-stage lockout enabled;
- Low-stage lockout temperature;
- Low degradation coefficient;
- Full degradation coefficient;
- cut-in/cut-out;
- defrost mode and associated inputs.

When a tested flag is false:

- corresponding input cells become read-only/blank;
- calculated fallback source is shown in result metadata/detail;
- hidden previous values are not submitted.

#### 11.4.3 Dual-stage point layout

A single compact matrix is acceptable because the number of points remains manageable.

Recommended semantic order:

```text
H0Low
H1Low
H1Full
H2Low
H2Full
H3Low
H3Full
H4Full
```

Rows:

```text
Condition / Temp
Capacity [Btu/h]
Power [W]
COP
```

Labels should make stage identity explicit; do not rely on ambiguous numeric suffixes alone.

#### 11.4.4 Triple Northern options

Expose:

- tested/optional states required for H2Low, H2Boost, H3Low, and other applicable points;
- Low stage lower/upper operating temperatures;
- Full stage lower/upper operating temperatures;
- Boost stage lower/upper operating temperatures;
- degradation coefficients for Low, Full, Boost where required;
- cut-in/cut-out;
- defrost mode;
- DHR/Region controls.

Validate stage ranges in the application layer:

```text
lower <= upper
finite values
required stage ranges present
```

Do not silently reorder invalid bounds.

#### 11.4.5 Triple Northern point layout

Avoid a ten-column mega-table that makes the Calculator unnecessarily wide.

Preferred layout is three vertically stacked stage tables.

**Low stage**

| Row | H0Low | H1Low | H2Low | H3Low |
|---|---:|---:|---:|---:|
| Condition / Temp | static | static | static | static |
| Capacity [Btu/h] | input | input | conditional | conditional |
| Power [W] | input | input | conditional | conditional |
| COP | calculated | calculated | calculated | calculated |

**Full stage**

| Row | H1Full | H2Full | H3Full |
|---|---:|---:|---:|
| Condition / Temp | static | static | static |
| Capacity [Btu/h] | input | input | input |
| Power [W] | input | input | input |
| COP | calculated | calculated | calculated |

**Boost stage**

| Row | H2Boost | H3Boost | H4Boost |
|---|---:|---:|---:|
| Condition / Temp | static | static | static |
| Capacity [Btu/h] | conditional | input | input |
| Power [W] | conditional | input | input |
| COP | calculated | calculated | calculated |

This keeps stage meaning visible and fits the existing scrollable AHRI surface.

If the current table owner supports grouped column headers without increasing coupling, a grouped matrix is acceptable. The final design must prioritize readability and existing table behavior over visual novelty.

#### 11.4.6 HSPF2 result panel

For new Dual/Triple products display:

```text
HSPF2 Raw
HSPF2 Published
Total Heating [kBtu]
Compressor Energy [kWh]
Resistance Energy [kWh]
Total Energy [kWh]
```

Variable Capacity keeps its current result display unless an additive field is proven safe by existing UI tests.

### 11.5 Detail panel

The existing shared detail panel remains the user entrypoint.

Use product-specific detail schemas selected by active product.

**Dual-stage SEER2 columns**

```text
Bin
Outdoor Temp
Fractional Hours
Building Load
Low Capacity
Full Capacity
Low Power
Full Power
Low Permitted
Case
Cycling/Load Factor
Cooling
Energy
```

**Dual-stage HSPF2 columns**

```text
Bin
Outdoor Temp
Fractional Hours
Building Load
Low Capacity
Full Capacity
Low Power
Full Power
Low Permitted
Full Permitted
Compressor Availability
Case
HLF/PLF
Compressor Heating
Resistance Heating
Compressor Energy
Resistance Energy
Total Energy
```

**Triple Northern columns**

```text
Bin
Outdoor Temp
Fractional Hours
Building Load
Low/Full/Boost Capacity
Low/Full/Boost Power
Low/Full/Boost Permission
Compressor Availability
Case 1–8
Cycling/Alternation Factor
Compressor Heating
Resistance Heating
Compressor Energy
Resistance Energy
Total Energy
```

Keep CSV export column order deterministic per product.

Do not display fields that are meaningless for the selected product merely to preserve one universal table.

### 11.6 Validation and stale-state behavior

On every relevant edit:

- clear stale detail rows;
- schedule debounced recalculation;
- highlight invalid active fields;
- leave inactive product fields unvalidated and unsubmitted.

On product switch:

1. save the current product draft if the current UI pattern supports snapshots;
2. activate/rebuild the new product surface;
3. apply tested/optional read-only state;
4. clear result and detail;
5. request lifecycle refit;
6. recalculate only after required inputs are complete.

A value entered in Triple Boost must never affect a later Dual-stage calculation while hidden.

---

## 12. Batch GUI design

### 12.1 Product-aware batch entry

The existing SEER2 and HSPF2 batch entrypoints remain.

Each batch dialog gains a Product selector and uses a product-specific matrix specification.

Do not create one union batch table containing every possible point.

Preferred structure:

```text
Batch dialog shell
    -> shared product/common options
    -> active product batch matrix spec
    -> automatic row calculation
    -> product-specific export
```

### 12.2 Snapshot behavior

Batch snapshots must include product classification.

Snapshots from different products must not be restored into incompatible table specs.

An acceptable approach is to retain a separate snapshot per product within the dialog lifecycle.

### 12.3 Batch result columns

SEER2 new-product rows:

```text
Raw SEER2
Published SEER2
Total Cooling
Total Energy
Status/Error
```

HSPF2 new-product rows:

```text
Raw HSPF2
Published HSPF2
Total Heating
Compressor Energy
Resistance Energy
Total Energy
Status/Error
```

Exports must include:

- product classification;
- common options;
- active point inputs;
- tested flags;
- stage ranges;
- raw result;
- published rating.

Existing variable batch column order and behavior should remain unchanged unless the batch owner already supports a compatible additive migration.

---

## 13. Testing strategy

### 13.1 Contract protection

Before formula implementation, lock:

- facade signatures;
- default variable classification;
- current variable request construction;
- current variable result keys;
- current official variable goldens;
- current Calculator variable SEER2/HSPF2 behavior;
- current batch/export behavior.

Any variable-capacity result change is a regression unless explicitly justified outside this workstream.

### 13.2 Dual-stage SEER2 tests

Required:

1. Existing official M1 direct golden:
   ```text
   12.4540352056775
   ```
2. Case 1 equation test.
3. Case 2 equation test.
4. Case 3 deterministic synthetic test:
   - Low locked out;
   - Full capacity above building load;
   - Full cycles;
   - Full degradation applied.
5. Case 4 equation test.
6. Low-stage lockout boundary.
7. equality boundaries between cases.
8. nearest-0.05 published rating.
9. seasonal sum equals bin sum.
10. UI product switch and dynamic point matrix.
11. batch Dual-stage row and export.

### 13.3 Dual-stage HSPF2 tests

Required:

1. Base standards-derived golden:
   ```text
   8.56889212463095
   ```
2. Cut-out standards-derived golden:
   ```text
   3.890729181034762
   ```
3. explicit proof of `3.412`.
4. availability:
   - available;
   - fractional;
   - unavailable.
5. Case 1.
6. Case 2.
7. Case 3 with Low-stage lockout.
8. Case 4 with resistance.
9. H4Full tested and fallback.
10. defrost none/override/calculated boundary as implemented.
11. nearest-0.05 published rating.
12. seasonal conservation.
13. UI tested-point read-only behavior.
14. UI stale-state isolation.
15. batch product schema and export.

### 13.4 Triple Northern tests

Use two evidence categories.

**Partial official parity**

Verify only fields approved by the standards audit:

- input normalization;
- Region IV building load;
- active Case 1/2/3/8 sequence;
- approved compressor-energy path;
- approved curve segments.

Do not assert final HSPF parity.

**PDF-derived equation tests**

Required:

1. Case 1.
2. Case 2.
3. Case 3.
4. Case 4.
5. Case 5.
6. Case 6.
7. Case 7.
8. Case 8.
9. H2Low correction.
10. H2Boost fallback.
11. H4Boost substitution.
12. Low/Full/Boost stage-range boundaries.
13. compressor available/fractional/unavailable.
14. resistance-only path.
15. defrost source behavior.
16. seasonal conservation.
17. nearest-0.05 published rating.
18. UI stage tables and tested toggles.
19. UI product switching.
20. batch Triple row and export.

Each equation-level test must record:

- input;
- expected case;
- clause/table/equation reference;
- hand-derived or independently derived intermediate values;
- expected bin contribution;
- expected seasonal contribution where applicable.

A snapshot copied from the implementation under test is not an independent expected value.

### 13.5 GUI regression

Protect:

- AHRI tab metric navigation;
- current visible-content lifecycle and window refit;
- detail-panel toggle;
- automatic calculation;
- Copy;
- result CSV;
- detail CSV;
- batch open/focus/snapshot lifecycle;
- invalid-cell highlighting;
- optional-point blank/read-only state;
- no stale output after product change.

Manual GUI verification must cover all five visible paths:

```text
SEER2 Variable
SEER2 Dual Stage
HSPF2 Variable
HSPF2 Dual Stage
HSPF2 Triple Stage Northern
```

---

## 14. Implementation sequence

Perform one workstream on one branch, but use staged internal slices and commits.

### M0 — Audit and contract lock

- locate and read the standards-audit document;
- read the PDF sections;
- audit current facade, capability, application, UI, batch, and detail owners;
- lock existing variable behavior;
- write the final product/input/result mapping before formulas.

Proof:

- characterization/contract tests pass before structural changes;
- no formula implementation yet.

### M1 — Product classification and request contracts

- add backward-compatible product classification;
- validate supported metric/product combinations;
- preserve default variable path;
- update capability invocation without new capability IDs.

Proof:

- old requests unchanged;
- explicit product requests route to test doubles/skeleton owners;
- unsupported combinations fail clearly.

### M2 — Dual-stage SEER2 core

- point resolver;
- context/options;
- Case 1–4 seasonal engine;
- raw/published result;
- official and equation tests.

Proof:

- direct official golden passes;
- Case 3 synthetic passes;
- variable SEER2 remains unchanged.

### M3 — Dual-stage HSPF2 core

- point resolver/fallback;
- stage permission;
- availability;
- Case 1–4;
- resistance with 3.412;
- defrost source boundary;
- raw/published result.

Proof:

- both standards-derived goldens pass;
- Case 3 and cut-out tests pass;
- variable HSPF2 remains unchanged.

### M4 — Triple Northern point and curve resolution

- Low/Full/Boost schemas;
- stage ranges;
- H2Low correction;
- H2Boost fallback;
- H4Boost substitution;
- source diagnostics.

Proof:

- equation-level point and curve tests pass independently of the seasonal loop.

### M5 — Triple Northern seasonal engine

- Case 1–8;
- availability;
- resistance;
- defrost;
- seasonal totals;
- result assembly.

Proof:

- all case tests pass;
- approved partial official parity passes;
- no unsupported direct final-M1 assertion.

### M6 — Application and capability integration

- product-aware adapters;
- summary models;
- detail mapping;
- error translation;
- existing route regression.

Proof:

- capability-driven end-to-end core tests for all product types;
- no UI direct core import.

### M7 — Main Calculator GUI

- product selectors;
- dynamic product surfaces;
- SEER2 Dual matrix;
- HSPF2 Dual matrix;
- Triple stage-grouped tables;
- options/tested/range controls;
- result fields;
- detail schema selection;
- stale-state handling;
- lifecycle refit.

Proof:

- automated UI tests;
- manual five-path verification.

### M8 — Batch and export integration

- product-aware batch specs;
- snapshots;
- row calculation;
- result columns;
- CSV export;
- existing variable batch regression.

Proof:

- product-specific batch tests and manual export inspection.

### M9 — Full closeout

- focused and full Calculator suite;
- formula/golden tests;
- structure/change gates;
- documentation/result record;
- branch push.

No slice may leave a knowingly failing formula, route, or GUI test for a later slice to repair.

---

## 15. Excluded scope

Do not include:

- more AHRI Analytics fixture collection;
- Appendix M legacy product engines;
- changes to current variable-capacity formulas;
- changes to current variable official goldens;
- changes to existing variable 0.025 rounding;
- new DOE Regions beyond the existing approved Region IV scope;
- ducted, packaged, multi-split, or unrelated product expansion;
- a generic AHRI base engine;
- a standards-expression DSL;
- Shiny/API automation;
- a GUI redesign outside the AHRI sections;
- unrelated Calculator refactoring;
- raw official fixture edits;
- formula fallback without a PDF basis.

---

## 16. Completion criteria

The workstream is complete only when all of the following are true.

### Core

1. Dual-stage SEER2 Cases 1–4 are implemented.
2. Dual-stage HSPF2 Cases 1–4 are implemented.
3. Triple Northern Cases 1–8 are implemented.
4. H2Low correction is implemented.
5. H2Boost fallback is implemented.
6. H4Boost substitution is implemented.
7. Stage operating ranges are enforced.
8. Low-stage lockout is distinct from total compressor cut-out.
9. HSPF2 resistance uses 3.412.
10. Defrost source is explicit and traceable.
11. Raw and published ratings are separate.
12. Existing variable results are unchanged.

### Application and capability

13. Explicit product classification flows through the current capability route.
14. Omitted product classification preserves variable behavior.
15. Unsupported combinations fail explicitly.
16. Result metadata identifies formula path, product, cases, and fallback sources.

### Main GUI

17. SEER2 supports Variable and Dual-stage selection.
18. HSPF2 supports Variable, Dual-stage, and Triple Northern selection.
19. Active product points/options are visible and editable as appropriate.
20. Inactive product values cannot leak into calculations.
21. Tested/optional state updates read-only cells correctly.
22. Main result shows raw and published metrics for new products.
23. HSPF2 new products show compressor/resistance/total energy.
24. Detail views expose product-appropriate bin traces.
25. Automatic calculation, error highlighting, Copy, and CSV remain functional.
26. Existing variable GUI behavior is unchanged.

### Batch

27. SEER2 batch supports Variable and Dual-stage.
28. HSPF2 batch supports Variable, Dual-stage, and Triple Northern.
29. Product-specific batch schemas do not mix irrelevant fields.
30. Batch snapshots and CSV exports retain product classification.

### Verification

31. Existing official variable goldens pass.
32. Dual-stage SEER2 direct official golden passes.
33. Dual-stage HSPF2 standards-derived goldens pass.
34. Triple partial official comparisons pass only within the approved boundary.
35. All missing-case/correction paths pass equation-level tests.
36. Focused and full Calculator tests pass.
37. Structure and staged gates pass with no new warning.
38. Manual GUI verification covers all five paths.
39. Main is not merged by the implementation agent.
40. Local and remote branch SHA match after push.

---

## 17. Final implementation report requirements

The final report must include:

- branch and slice commit SHAs;
- product classification contract;
- point/option contract by product;
- facade/capability compatibility result;
- Dual-stage SEER2 official golden result;
- Dual-stage HSPF2 2026 corrected golden results;
- Triple Case 1–8 test matrix;
- H2Low/H2Boost/H4Boost equation references and test evidence;
- resistance and defrost handling;
- raw/published rounding results;
- current variable regression result;
- Calculator GUI five-path verification;
- batch/export verification;
- changed owner summary;
- full validation result;
- remaining uncertainty, if any.

If a normative ambiguity remains after checking the PDF, do not hide it behind an assumed fallback. Record the ambiguity, isolate it from unrelated completed paths, and report whether it blocks the affected product from being marked complete.
