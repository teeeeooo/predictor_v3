# AHRI SEER2 / HSPF2 Core Refactor Design

**Status:** Proposed - audit complete, implementation not started
**Scope:** AHRI 210/240 variable-capacity SEER2 and HSPF2 core structure
**Primary implementation sequence:** Contract lock -> HSPF2 extraction -> SEER2 extraction -> minimal commonization -> closeout
**Proposed canonical location:** `docs/designs/2026-07-12-ahri-seer2-hspf2-core-refactor-design.md`

---

## 1. Purpose

이 문서는 AHRI 210/240 multi-capacity 확장 전에 수행할 SEER2/HSPF2 core 리팩터링의 owner boundary, compatibility contract, 구현 slice, 검증 목적을 확정한다.

현재 계산기는 Calculator와 향후 ML/Predict 흐름에서 함께 사용되는 canonical standard calculation owner다. 이 재사용성은 모든 계산식이 한 Python 파일에 있기 때문에 생기는 것이 아니라, 호출자가 하나의 안정된 public facade와 capability contract를 사용하기 때문에 성립한다.

따라서 이번 작업의 목표는 다음과 같다.

1. AHRI SEER2/HSPF2를 계속 하나의 canonical core로 유지한다.
2. 기존 public facade와 Calculator/ML 호출 계약은 바꾸지 않는다.
3. 한 파일에 혼합된 config, point resolution, seasonal engine, result assembly, legacy 책임을 내부 owner별로 분리한다.
4. 공식 계산기로 검증된 기존 variable-capacity golden을 정확성 oracle로 고정한다.
5. 리팩터링이 끝난 뒤 two-stage와 triple-capacity engine을 기존 variable engine의 sibling으로 추가할 수 있는 구조를 만든다.

이번 설계는 계산식 수정 설계가 아니다. 기존 계산 결과를 변경할 수 있는 해석 수정, 규격 보정, config migration은 별도 workstream으로 남긴다.

---

## 2. Confirmed Decisions

| Decision | 확정 내용 |
| --- | --- |
| Refactor priority | AHRI multi-capacity 구현보다 SEER2/HSPF2 core 리팩터링을 먼저 수행한다. |
| Engine scope | HSPF2뿐 아니라 SEER2도 같은 refactor workstream에서 정리한다. |
| Golden authority | 현재 테스트에 포함된 AHRI variable-capacity 입력 데이터와 expected 결과는 사용자가 공식 계산기로 검증한 golden이다. |
| Golden change policy | 기존 variable-capacity golden과 expected 결과는 리팩터링을 맞추기 위해 변경하지 않는다. 결과 불일치는 새 구현의 실패로 판단한다. |
| Canonical owner | Calculator와 ML이 재사용하는 standard calculation core는 하나로 유지한다. |
| Physical layout | canonical core가 여러 내부 module로 분리되는 것은 허용하며 권장한다. 단일 source owner와 안정된 facade가 유지되면 된다. |
| Public facade | 현재 `ahri_seer2.py`, `ahri_hspf2.py`의 import path와 public class/method contract를 유지한다. |
| Multi-capacity | product type, two-stage, triple-capacity 계산식과 UI는 refactor closeout 후 별도 구현한다. |
| AHRI external API | 공식 formula API 또는 Directory API 조사는 별도로 진행하며, 이번 리팩터링의 blocker가 아니다. |
| Behavior policy | 이번 workstream은 no-behavior-change refactor다. formula, rounding, fallback, diagnostics, exception boundary를 의도적으로 바꾸지 않는다. |

### 2.1 Golden provenance

프로젝트 결정:

> 현재 repo 테스트에 포함된 AHRI variable-capacity 데이터와 expected 결과는 공식 계산기로 검증된 golden 데이터다.

이 결정은 단순 regression snapshot보다 높은 우선순위를 가진다.

- 공식 golden: 계산 정확성 oracle
- characterization snapshot: refactor 전후 diagnostics/result shape 보존용
- smoke/validation: route, branch, error boundary 보존용

Characterization fixture를 새로 생성하더라도 이를 공식 golden이라고 표기하지 않는다. 공식 계산기로 검증됐다고 사용자가 확인한 기존 데이터만 공식 golden으로 취급한다.

---

## 3. Evidence and Standard Boundary

### 3.1 Standard references

현재 variable-capacity 경로의 주요 규격 경계는 다음과 같다.

| Metric | Current product path | Primary reference |
| --- | --- | --- |
| SEER2 | Variable Capacity System | AHRI 210/240-2026 Section 11.2.1.3, Table 15 |
| HSPF2 | Variable Capacity Heat Pump | AHRI 210/240-2026 Section 11.2.2.4, Table 16 |
| Test points | Cooling/heating test conditions | AHRI 210/240-2026 Table 7 and Table 8 |
| Future two-stage SEER2 | Two-stage system and variable-capacity certified two-capacity system | Section 11.2.1.2 |
| Future two-stage HSPF2 | Two-stage heat pump | Section 11.2.2.2 |
| Future triple-capacity HSPF2 | Triple-capacity compressor additional steps | Section 11.2.2.6 |

프로젝트 해석:

- 이번 작업은 Section 11.2.1.3과 Section 11.2.2.4의 현재 구현을 재해석하지 않는다.
- 표준 원문은 owner 경계와 future engine 분리 필요성을 확인하는 근거로 사용한다.
- 공식 계산기 golden이 현재 variable-capacity 결과의 정확성 기준이다.
- 신규 two-stage/triple-capacity 계산식은 이번 refactor에 포함하지 않는다.

### 3.2 Repository evidence

현재 active owner와 호출 경로는 다음 범위에 있다.

- standard facades:
  - `core/calculators/standards/ahri_seer2.py`
  - `core/calculators/standards/ahri_hspf2.py`
- profile and construction:
  - `core/calculators/profiles.py`
  - `core/calculators/dispatcher.py`
- capability:
  - `core/calculators/capability/requests.py`
  - `core/calculators/capability/gateway.py`
- Calculator application adapters:
  - `apps/calculator/application/ahri/seer2_adapter.py`
  - `apps/calculator/application/ahri/hspf2_adapter.py`
- ML/calculator envelope foundation:
  - `core/calculators/adapters/input_adapter.py`
  - prediction/result/ranking adapters and envelope-chain tests
- configs:
  - `data/region_configs/usa.json`
  - `data/region_configs/usa_hspf2.json`
- AHRI owner documents:
  - `docs/ahri210240/ahri210240_notes.md`
  - `docs/ahri210240/ahri210240_dev_notes.md`

---

## 4. Current Call Flow

### 4.1 Calculator production flow

```text
Tkinter Calculator UI
    -> apps.calculator.application.ahri adapter
    -> execute_standard_calculation(...)
    -> capability handler
    -> calculator profile resolver / dispatcher
    -> AHRI facade class
    -> current seasonal calculation implementation
```

Production application/UI code is already prevented from importing standard engines directly. This boundary must remain unchanged.

### 4.2 ML / Predictor reuse flow

The approved direction is:

```text
ML / Predictor output
    -> predicted-points envelope
    -> calculator-input envelope
    -> standard calculation capability
    -> AHRI facade
    -> result envelope
```

A current end-to-end SEER2 envelope smoke still constructs the facade through the dispatcher and calls `calculate_seer2()` directly. That observable route must continue to work during the refactor even if later production callers are consolidated behind capability execution.

### 4.3 Why internal splitting is safe

The dispatcher and capability layer depend on:

- facade import path,
- public constructor,
- `calculate_seer2()` or `calculate_hspf2()` method,
- existing request and result contract.

They do not depend on how interpolation, point resolution, bin cases, or diagnostics are physically organized inside the facade module. Internal modules can therefore be extracted without creating separate Calculator and ML engines.

---

## 5. Current Implementation Audit

## 5.1 HSPF2 audit

The current HSPF2 implementation is an approximately 900-line class with about 30 methods. It combines multiple generations and responsibilities.

### Mixed responsibilities

| Responsibility | Current examples |
| --- | --- |
| File/config I/O | JSON loading, config default mutation |
| Region table access | Region IV canonical bin table validation |
| Schema inspection | test-point schema and alias access |
| Legacy compatibility | legacy-to-canonical and canonical-to-v2 mapping |
| Legacy calculation | `calculate_hspf2_v2()` |
| Production calculation | `calculate_hspf2_v3()` and AHRI variable-capacity path |
| Point validation | required and positive point checks |
| Optional-point resolution | H12, H22, H42 handling and source metadata |
| Performance curves | Low, Intermediate, Full capacity/power by temperature |
| Availability/defrost | cut-out factor, demand-defrost inputs and metadata |
| Seasonal loop | building load, Case I/II/III, auxiliary heat, totals |
| Result assembly | duplicated top-level totals, nested summary, diagnostics, bin details |
| Rounding | nearest 0.025 half-up |
| Historical helpers | v2-only bin/load interpolation and currently unused compatibility helpers |

### Structural problems

1. **Legacy and production engines share one mutable object**

   `calculate_hspf2_v2()` and the production v3 path use the same class state even though they use different bin tables, point naming, load models, output keys, and seasonal logic.

2. **Config shape and calculation generation are mixed**

   The file exposes both legacy `bin_data` and canonical Region IV tables, plus defaults injected during construction. The facade therefore owns file I/O, schema compatibility, and formula execution at once.

3. **The production method is a long orchestration and formula block**

   Point resolution, context construction, bin loop, case calculation, result totals, and diagnostics are assembled in one method.

4. **Result contract construction is embedded in the formula loop owner**

   The engine writes:
   - canonical result values,
   - duplicate compatibility keys,
   - summary metadata,
   - defrost trace,
   - heating-load trace,
   - bin diagnostics.

   This makes formula extraction risky because result schema and calculation logic cannot be changed independently.

5. **Tests directly call private helpers**

   Existing tests call private interpolation/performance methods. These tests are useful, but they currently couple verification to facade internals.

6. **Public-looking compatibility methods have no current repo callers**

   Methods such as schema access and canonical/internal mapping are not used outside the facade in current repo search, but they are non-underscore methods. They must remain callable during the initial no-behavior-change refactor unless separately approved for retirement.

7. **Historical/dead branch language remains in tests and code**

   Some conservation helpers contain handling for labels such as `Case S`, `Cut-out`, or `Fractional`, while the current production bin loop emits Case 0/I/II/III with fractional availability represented through `delta_j`. This mismatch must not be “cleaned up” casually during extraction; it needs a later behavior/test audit.

8. **Documentation and metadata inconsistencies exist**

   Config metadata contains 2023/2024/2026 references and scaffold comments. These may be stale metadata or real capability gaps. They are outside the no-behavior-change refactor.

### HSPF2 audit verdict

The current file is a genuine hotspot. Adding two-stage and triple-capacity branches directly to it would increase coupling and make official-golden regression diagnosis substantially harder.

HSPF2 requires responsibility extraction before new formulas are added.

---

## 5.2 SEER2 audit

The current SEER2 implementation is much smaller, but it still combines several responsibilities in one class.

### Mixed responsibilities

| Responsibility | Current examples |
| --- | --- |
| Default config factory | `get_default_ahri_seer2_config()` |
| Config loading | bin table, point temperatures, scale and v-factor |
| Input unpacking | A/B/E/F point tuple extraction |
| Intermediate curve resolution | N/M values for capacity and power |
| Per-bin performance | Low, Intermediate, Full values |
| Case logic | low cycling, two interpolation ranges, full operation |
| Seasonal aggregation | cooling and energy sums |
| Result assembly | metric, point EERs, totals, system type, bin details |

### Structural and compatibility concerns

1. **Facade name and direct-call contract are already used**

   `AHRICalculator` and `calculate_seer2()` are referenced by dispatcher, tests, and the ML/calculator envelope chain.

2. **Core and application own different seasonal scaling steps**

   The core returns fractional-bin cooling/energy sums. The Calculator application adapter multiplies them by `cooling_season_hours`. This boundary must not move during refactor.

3. **Accepted parameters include currently unused behavior**

   `p_w_off` is accepted by the public method but currently does not affect the returned result. The refactor must preserve this behavior rather than silently implementing off-mode energy.

4. **Config includes unused or partially used fields**

   The default config includes `cd_default_full`, while the current engine primarily consumes the low-speed degradation coefficient. Config cleanup is not part of this refactor.

5. **Intermediate-envelope clamping is observable behavior**

   Capacity/power interpolation ratios are clamped before slopes are calculated. The refactor must preserve this behavior even if a later standards audit questions it.

6. **Standard-version metadata is inconsistent**

   The default/external config says 2023 while implementation documentation refers to 2026. Metadata correction is separate from structural extraction.

### SEER2 audit verdict

SEER2 does not need the same degree of decomposition as HSPF2, but extracting the variable-capacity engine now prevents a second monolith when two-stage cooling is added.

---

## 5.3 Cross-boundary audit

### Stable boundaries already present

- Profiles identify AHRI SEER2/HSPF2 calculator owners.
- Dispatcher lazily constructs the exact facade classes.
- Capability IDs are stable:
  - `ahri210240.seer2`
  - `ahri210240.hspf2`
- Application adapters create typed requests and consume raw result mappings.
- UI depends on application adapters, not core engine modules.
- ML/calculator envelopes are separate from calculator result schema.

### Implication

The refactor should remain entirely inside `core/calculators/standards` plus focused tests and owner documentation. Application/UI, capability requests, profiles, and envelope schemas do not need to change.

---

## 6. Compatibility Contract Lock

## 6.1 HSPF2 facade contract

The following observable contract must remain stable.

### Import and construction

```python
from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator

calculator = AHRIHSPF2Calculator(config_path)
```

### Public methods

- `calculate_hspf2(test_points, **kwargs)`
- `calculate_hspf2_v3(test_points, **kwargs)`
- `calculate_hspf2_v2(test_points, **kwargs)`
- `get_test_point_schema(mode=None)`
- `legacy_to_canonical(test_points)`
- `canonical_to_internal_usage(test_points)`

The initial refactor must preserve these methods and signatures. Retirement or rename of compatibility methods is a separate API change.

### Constructor-visible state

Existing facade attributes should remain readable with equivalent values during this workstream:

- `config`
- `bin_temps`
- `bin_hours`
- `canonical_hspf2_bin_tables`
- `test_point_schema`
- `test_point_aliases`
- `test_point_temps`
- `constants`
- `defaults`

Internal owners may hold the canonical state, but facade compatibility properties/attributes must remain.

### Production input behavior

Preserve:

- canonical and legacy aliases,
- case-insensitive point matching,
- conflicting alias detection,
- required v3 points,
- optional H12/H22/H42 behavior,
- explicit defrost input requirement,
- default/fallback kwargs,
- minimum-speed alias kwargs,
- split/single-package fallback behavior,
- positive point validation.

### Production result contract

Preserve exact key names, casing, types, units, rounding, and nested locations.

Top-level keys include:

- `raw_hspf2`
- `raw_hspf2_base`
- `rounded_hspf2`
- `HSPF2`
- `total_load`
- `total_energy`
- `total_heating_btu`
- `total_energy_wh`
- `h42_source`
- `bin_table`
- `summary`
- `bin_details`

Preserve current duplicate compatibility totals rather than normalizing them in this refactor.

Preserve nested diagnostics including:

- formula path,
- Region IV metadata,
- H12/H22 source fields,
- minimum-speed fields,
- defrost trace,
- heating-load-line trace,
- bin-level `debug_info`.

### Legacy v2 contract

Preserve:

- v2 public method,
- legacy input keys,
- legacy bin behavior,
- legacy result key casing,
- legacy sanity warning behavior,
- existing v2 expected results.

The v2 implementation may move to a separate internal owner, but it must not be rewritten to use the v3 algorithm.

---

## 6.2 SEER2 facade contract

### Import and construction

```python
from core.calculators.standards.ahri_seer2 import (
    AHRICalculator,
    get_default_ahri_seer2_config,
)

calculator = AHRICalculator(config_path)
```

### Public method

```python
calculate_seer2(
    test_points,
    system_type="HP",
    p_w_off=0.0,
    cd_low=None,
)
```

Preserve:

- parameter names and defaults,
- HP/AC handling,
- current `p_w_off` no-effect behavior,
- default config helper,
- readable `config` attribute,
- current point-key contract.

### Result contract

Preserve exact values and shape for:

- `SEER2`
- `EER2_A_Full`
- `EER2_B_Low`
- `total_cooling_Btu`
- `total_energy_Wh`
- `system_type`
- `bin_details`

Preserve bin order, case labels, rounded detail fields, and current interpolation/clamping behavior.

---

## 6.3 Capability, profile, application, and UI contract

Do not change during this workstream:

- capability IDs,
- request dataclasses,
- profile IDs,
- calculator IDs,
- dispatcher selection,
- application adapter signatures,
- application summary dataclasses,
- UI input schema,
- Batch schema,
- Copy/CSV/detail behavior,
- ML/calculator envelope schema,
- result/ranking envelope schema.

---

## 6.4 Exception contract

No-behavior-change includes error boundaries.

Preserve:

- exception type,
- fail-fast order where tests or callers depend on it,
- meaningful message content,
- missing-point behavior,
- invalid config behavior,
- invalid system type behavior,
- invalid interpolation envelope behavior,
- total-energy/total-load sanity checks.

Exact message text only needs byte preservation where a current test asserts it, but messages must not become generic or lose diagnostic context.

---

## 7. Target Architecture

## 7.1 Design principles

1. **Stable public facade, private internal engines**
2. **One canonical AHRI core, not separate Calculator and ML implementations**
3. **Variable-capacity and legacy calculations have separate owners**
4. **Formula owners do not perform UI/application translation**
5. **Result contract assembly is explicit**
6. **No speculative universal AHRI engine**
7. **Commonization happens only after both engines are independently extracted**
8. **New multi-capacity engines will be siblings, not branches inside the variable engine**

## 7.2 Required conceptual owners

The exact internal filenames and class names should follow existing repo conventions after implementation audit. The following owner boundaries are required.

### HSPF2 facade owner

Owns:

- existing public class and methods,
- compatibility attributes,
- delegation,
- minimal constructor wiring.

Does not own:

- seasonal bin loop,
- point fallback equations,
- legacy-v2 formula body,
- result-dict construction details.

### HSPF2 config/context owner

Owns:

- loaded config access,
- canonical Region IV table validation,
- immutable calculation context construction,
- defaults needed by the selected engine.

Does not own:

- test-point fallback,
- bin case calculation,
- result schema.

### HSPF2 point owner

Owns:

- alias normalization,
- case-insensitive matching,
- positive-point validation,
- required/optional point resolution,
- H12/H22/H42 source metadata,
- resolved Low/Intermediate/Full anchors.

Does not own:

- seasonal bin iteration,
- UI optional controls,
- result formatting.

### HSPF2 variable-capacity engine

Owns:

- AHRI 210/240-2026 variable-capacity heating path,
- building load,
- Low/Intermediate/Full performance by bin,
- Case I/II/III,
- cut-out availability,
- compressor/auxiliary totals,
- raw and rounded HSPF2 calculation.

Does not own:

- file I/O,
- legacy aliases,
- public facade compatibility,
- Calculator presentation.

### HSPF2 result/diagnostics owner

Owns:

- current raw result mapping,
- duplicate compatibility keys,
- summary metadata,
- bin diagnostics shape.

This may be a small dedicated assembler or a bounded part of the variable engine. It must be explicit and testable; it must not remain an incidental dictionary assembled throughout the facade.

### HSPF2 legacy owner

Owns only:

- v2 legacy point validation,
- legacy load/performance interpolation,
- v2 seasonal loop,
- v2 result mapping.

It may reuse only primitives whose semantics are demonstrably identical.

### SEER2 variable-capacity engine

Owns:

- A/B/E/F point model,
- Low/Intermediate/Full curves,
- current Case 1/2.1/2.2/3 logic,
- fractional-bin seasonal aggregation,
- raw core result mapping and bin details.

### Optional AHRI numeric primitives

May own:

- safe division,
- linear interpolation,
- shared positive finite value helpers.

Create this owner only when extraction proves the semantics are identical. Do not introduce a base engine or generic case framework merely because method names look similar.

---

## 7.3 Recommended physical shape

The exact layout is not mandatory, but the implementation should preserve the two existing facade module paths and place internal owners behind them.

A reasonable shape is:

```text
core/calculators/standards/
  ahri_seer2.py              # stable public facade
  ahri_hspf2.py              # stable public facade
  <private AHRI internals>/
    hspf2_context.*
    hspf2_points.*
    hspf2_variable.*
    hspf2_legacy.*
    seer2_variable.*
    numeric.*                # only if real shared semantics are proven
```

Equivalent private sibling modules are acceptable if a package would add unnecessary ceremony.

The final choice should satisfy:

- facade paths unchanged,
- no circular dependency,
- no new public package contract by accident,
- no production file above the project soft limit without a concrete reason,
- no structure allowlist addition merely to hide a new hotspot.

---

## 7.4 Internal data shape

Raw dictionaries are required at the public facade boundary, but internal formula owners should prefer small immutable values where they reduce ambiguity.

Potential internal concepts include:

- capacity/power pair,
- resolved variable-capacity points,
- Region IV seasonal context,
- per-bin performance state,
- per-bin energy result,
- fallback/source metadata.

These are internal concepts, not approved public schemas. Exact dataclass names and package locations should be selected by the implementing agent after checking sibling calculator patterns.

Do not expose internal dataclasses through capability requests, application adapters, UI, or ML envelopes during this refactor.

---

## 8. HSPF2 Refactor Boundaries

## 8.1 Extraction boundary: config and context

Move the following responsibility out of the formula facade:

- config loading interpretation,
- canonical bin-table lookup and validation,
- Region IV values used by production v3,
- v2 bin data used by legacy calculation,
- effective defaults.

Preserve facade attributes and current default-injection behavior.

Do not merge `usa.json` and `usa_hspf2.json` or create a new nested schema in this workstream.

## 8.2 Extraction boundary: point normalization and fallback

Move:

- legacy/canonical alias handling,
- case-insensitive matching,
- conflict detection,
- required point validation,
- H12 fallback,
- H22 fallback,
- H42 optional source,
- H2Int envelope inputs,
- source metadata.

The resolved point owner should return a coherent variable-capacity point set so the seasonal engine does not repeatedly inspect raw input keys.

## 8.3 Extraction boundary: performance curves

Move and group the current variable-capacity calculations for:

- low-speed performance,
- minimum-speed-limited low path,
- full-speed performance,
- intermediate-speed performance,
- cut-out availability,
- building load.

Keep equation-source metadata available for diagnostics.

## 8.4 Extraction boundary: seasonal bin engine

The bin engine should receive resolved points and seasonal context, then own:

- bin iteration,
- Case 0/I/II/III selection,
- cycling degradation,
- COP interpolation,
- compressor heat/energy,
- auxiliary heat/energy,
- seasonal accumulation.

It must not read UI values or build application summaries.

## 8.5 Extraction boundary: result assembly

Result assembly must preserve current raw dict shape exactly.

Do not use this refactor to:

- remove duplicate total keys,
- rename `HSPF2`,
- normalize v2/v3 key casing,
- move `h42_source`,
- flatten metadata,
- remove debug fields,
- replace strings with enums in public output.

## 8.6 Legacy v2 separation

Move the v2 formula body and v2-only helpers behind a legacy owner.

The facade must continue to expose `calculate_hspf2_v2()`.

The legacy owner must not depend on the variable-capacity production engine. Shared primitive reuse is allowed only for mathematically identical operations.

---

## 9. SEER2 Refactor Boundaries

## 9.1 Facade

Keep:

- `AHRICalculator`,
- `get_default_ahri_seer2_config()`,
- constructor behavior,
- `calculate_seer2()` signature,
- `config` visibility.

The facade should load/wire and delegate.

## 9.2 Variable-capacity point and curve owner

Own:

- A/B/E/F input extraction,
- Low/Full interpolation,
- EInt-based intermediate slopes,
- current N-factor clamping,
- per-bin EER values.

Do not add a product type or two-stage branch in this slice.

## 9.3 Seasonal engine

Own:

- cooling building load,
- Case 1/2.1/2.2/3,
- fractional-bin cooling and energy totals,
- current bin detail values,
- SEER2 calculation.

## 9.4 Application scaling boundary

The core currently returns fractional-bin totals. The application adapter applies `cooling_season_hours` for displayed seasonal totals.

Keep that boundary unchanged. Do not move the 1000-hour scaling into the core during refactor.

## 9.5 Deferred SEER2 behavior

Do not implement or modify:

- off-mode energy using `p_w_off`,
- full-speed degradation coefficient,
- 2026 metadata correction,
- two-stage input schema,
- test-point naming migration,
- additional standard parity.

---

## 10. Shared Primitive Policy

Commonization is the final refactor slice, not the starting point.

### Approved candidates

Only after HSPF2 and SEER2 extraction, compare:

- safe division,
- linear interpolation,
- capacity/power validation,
- basic immutable capacity/power representation.

### Rejected speculative abstractions

Do not introduce:

- `BaseAHRICalculator`,
- generic seasonal engine,
- universal building-load policy,
- universal Case enum shared by cooling and heating,
- one point schema covering variable, two-stage, and triple-capacity,
- one result model replacing existing raw dicts,
- reflection-based engine discovery.

Cooling and heating cases have different standard semantics even where the control flow appears similar.

---

## 11. Implementation Slices

## Slice R0 - Contract and Golden Lock

### Objective

Create an explicit refactor baseline before moving production logic.

### Required work

- Inventory all current facade callers and public symbols.
- Mark existing AHRI variable-capacity test datasets as official-calculator golden in owner documentation.
- Consolidate duplicated test input data only where it improves provenance without changing expected values.
- Add focused contract tests for currently under-guarded public result and diagnostics shape.
- Add representative deep-equality characterization fixtures for refactor comparison where needed.

### Important distinction

- Existing user-confirmed expected results are official golden.
- Newly generated full-result snapshots are structural characterization evidence only.

### Completion state

The implementation can be moved while a failing test identifies whether the mismatch is:

- official metric/golden,
- public result contract,
- diagnostics contract,
- route/error behavior.

No production formula is changed in this slice.

---

## Slice R1 - HSPF2 Context and Point Owners

### Objective

Separate config/seasonal context and input-point resolution from the formula loop.

### Required behavior

- Facade construction and attributes remain compatible.
- Canonical/legacy aliases produce the same resolved values.
- H12/H22/H42 branches and metadata remain identical.
- Validation order and errors remain compatible.
- No seasonal formula moves unless needed for a narrow dependency seam.

### Completion state

The production v3 formula receives a resolved point/context object rather than repeatedly reading raw config and raw test-point dictionaries.

---

## Slice R2 - HSPF2 Variable-Capacity Engine

### Objective

Move the current Section 11.2.2.4 production path into a dedicated variable-capacity owner.

### Required behavior

- Exact official golden results.
- Exact 0.025 rounding.
- Same bin count/order.
- Same Case labels and branch distribution.
- Same q/p Low/Intermediate/Full values.
- Same compressor/auxiliary totals.
- Same defrost and cut-out handling.
- Same raw result and diagnostics shape.

### Completion state

`AHRIHSPF2Calculator.calculate_hspf2_v3()` is a thin delegate to the variable-capacity engine.

---

## Slice R3 - HSPF2 Legacy Separation and Facade Closeout

### Objective

Move v2 calculation into a separate legacy owner and reduce the facade to compatibility and delegation.

### Required behavior

- Existing v2 input and output contract unchanged.
- Existing v2 smoke/golden unchanged.
- No v2 behavior is rewritten to match v3.
- Non-underscore compatibility methods remain callable.
- Private-helper tests are moved to the new owner or replaced by equivalent behavior tests; the facade is not kept large solely to satisfy private test access.

### Completion state

The HSPF2 facade no longer owns formula bodies for both generations.

---

## Slice R4 - SEER2 Variable-Capacity Extraction

### Objective

Separate the current Section 11.2.1.3 variable-capacity engine while retaining the existing facade.

### Required behavior

- Exact current official golden values.
- Same default-config helper output.
- Same A/B/E/F point contract.
- Same HP/AC v-factor behavior.
- Same N-factor clamping and intermediate slopes.
- Same Case 1/2.1/2.2/3 results.
- Same fractional totals and bin details.
- Same application season-hour scaling boundary.
- Same ML/calculator envelope chain behavior.

### Completion state

`AHRICalculator.calculate_seer2()` delegates to a bounded variable-capacity engine.

---

## Slice R5 - Minimal Commonization and Refactor Closeout

### Objective

Remove only proven low-level duplication and close the workstream.

### Required work

- Compare extracted engines before creating shared primitives.
- Commonize only identical numeric semantics.
- Remove temporary extraction shims that are not part of compatibility contract.
- Update AHRI dev notes with final internal ownership.
- Verify structural warnings and owner boundaries.
- Confirm multi-capacity can be added as sibling engines without modifying current variable formula bodies.

### Completion state

- Public facades remain stable.
- HSPF2 hotspot is removed rather than allowlisted.
- SEER2 is ready for a sibling two-stage engine.
- HSPF2 is ready for sibling two-stage and triple-capacity engines.

---

## 12. Validation Strategy

## 12.1 Official golden tests

Treat current AHRI variable-capacity expected data as immutable official-calculator golden.

Validate exact expected values for all existing covered combinations, including where present:

- HSPF2 final rounded value,
- raw HSPF2,
- seasonal heating total,
- seasonal energy total,
- SEER2,
- point EER values,
- cooling/energy totals.

Do not loosen exact expected values into broad tolerances merely to make extraction pass.

## 12.2 HSPF2 branch and diagnostics tests

Preserve coverage for:

- H12 tested and fallback sources,
- H22 tested and fallback source,
- H42 provided/not provided,
- H2Int capacity/power sensitivity,
- minimum-speed-limited and non-limited paths,
- Case I/II/III activation,
- `delta_j` cut-out/fractional behavior,
- Region IV bin table and HLH,
- heat and energy conservation,
- positive/non-negative outputs,
- nested metadata and debug-info keys,
- legacy v2 delta and v2 result.

## 12.3 SEER2 branch tests

Preserve or add focused coverage for:

- HP and AC system type,
- default and explicit `cd_low`,
- Low cycling,
- Low-to-Intermediate interpolation,
- Intermediate-to-Full interpolation,
- Full operation,
- EInt slope and clamping behavior,
- point EER outputs,
- bin ordering and detail schema,
- `p_w_off` accepted with current no-effect behavior.

## 12.4 Deep result comparison

Before moving each engine, create representative baseline comparisons that assert the raw result mapping is deeply equal after extraction, including nested list/dict values.

Use stable representative cases for:

- HSPF2 with all optional points,
- HSPF2 without H12,
- HSPF2 without H22,
- HSPF2 without H42,
- HSPF2 minimum-speed-limited,
- HSPF2 cut-out/fractional availability,
- HSPF2 legacy v2,
- SEER2 HP,
- SEER2 AC.

If full floating-point deep equality is not stable because an existing output intentionally rounds only selected fields, compare the exact observable fields and document any intentionally unrounded internal value. Do not introduce new rounding.

## 12.5 Route and boundary tests

Validate unchanged behavior through:

- dispatcher construction,
- standard calculation capability,
- Calculator application adapters,
- application-without-UI import boundary,
- Single Calculator sections,
- Batch paths,
- SEER2 ML/calculator envelope chain,
- result envelope/ranking boundary.

## 12.6 Structural validation

Required structural outcome:

- no new import-boundary error,
- no new structure warning,
- no new oversized internal file without explicit reason,
- existing HSPF2 core hotspot warning should be eliminated,
- no allowlist entry added merely to suppress the refactor result,
- core remains pure Python without UI toolkit, numpy, or pandas.

---

## 13. Risks and Safeguards

| Risk | Why it matters | Safeguard |
| --- | --- | --- |
| Golden accidentally reclassified as regression data | 공식 계산기 정확성 기준이 약화된다. | User-confirmed variable data는 official golden으로 명시하고 expected 변경 금지 |
| Formula correction mixed into extraction | 결과 변화 원인을 구조/공식 중 구분할 수 없다. | 모든 formula/config correction을 non-goal로 유지 |
| Facade attribute loss | 외부 또는 테스트의 관찰 가능 동작이 깨질 수 있다. | 기존 constructor-visible attributes 유지 |
| Private test coupling | facade를 다시 비대하게 유지할 수 있다. | helper 테스트를 새 owner로 이동하고 public facade compatibility와 분리 |
| Result key normalization | adapter, diagnostics, historical tests가 깨질 수 있다. | v2/v3 casing과 duplicate keys 그대로 유지 |
| Dict assembly order change | CSV/debug snapshot 등 비공식 소비자가 영향을 받을 수 있다. | 가능하면 current insertion order도 보존하고 deep contract test 수행 |
| Rounding drift | HSPF2 0.025 경계에서 golden이 달라진다. | Decimal half-up owner와 호출 시점 보존 |
| Config mutation cleanup | `defaults` 관찰값이 달라질 수 있다. | 이번 단계에서는 effective defaults와 facade state 보존 |
| H12/H22 fallback drift | 최종 HSPF2와 diagnostics가 모두 바뀐다. | source branch별 golden/metadata tests |
| H42 low-temperature drift | 저온 bin 성능과 Case III가 바뀐다. | provided/not-provided bin comparison 유지 |
| H2Int envelope change | Case II COP와 minimum-speed path가 바뀐다. | current envelope validation and sensitivity tests 보존 |
| SEER2 seasonal scaling move | core와 application totals가 1000배 차이 날 수 있다. | cooling-season-hours multiplication은 application에 유지 |
| `p_w_off` opportunistic implementation | SEER2가 의도치 않게 달라진다. | accepted/no-effect behavior characterization test |
| Standard metadata cleanup | behavior change와 문서 변경이 섞인다. | 2023/2024/2026 metadata 정리는 별도 task |
| Premature common base class | cooling/heating 규격 의미가 강제로 합쳐진다. | engines 추출 후 identical primitive만 공통화 |
| Circular facade/internal imports | dispatcher import와 test collection이 실패한다. | internal owners do not import facades |
| New package ceremony | 작은 helper가 과도하게 분리된다. | required owner boundary를 만족하는 최소 파일 수 선택 |
| Legacy branch removal | historical/reference behavior가 사라진다. | `calculate_hspf2_v2()`와 legacy owner 유지 |
| Dead branch cleanup during refactor | 숨은 behavior/test 의도가 사라진다. | unreachable/dead-code removal은 별도 evidence와 승인 필요 |

---

## 14. Non-goals

이번 refactor에서 하지 않는다.

- HSPF2 또는 SEER2 공식 수정
- official golden expected 변경
- AHRI 210/240-2026 parity 보정
- standard year metadata 정리
- Region IV 외 지역 지원
- two-stage SEER2 구현
- two-stage HSPF2 구현
- triple-capacity northern HSPF2 구현
- product-type enum/request/schema 추가
- capability ID 추가 또는 변경
- profile 추가 또는 분리
- Calculator UI 변경
- Batch 입력 schema 변경
- ML feature/schema 변경
- result envelope schema 변경
- HSPF2 result key 정규화
- v2 제거
- off-mode energy 구현
- defrost multiplier 정책 변경
- config JSON schema migration/merge
- AHRI external API 연동
- unrelated calculator commonization
- broad `core/calculators` restructure

---

## 15. Completion Criteria

Refactor workstream은 다음 상태에서 완료된다.

### Architecture

- 기존 SEER2/HSPF2 facade import path가 유지된다.
- 기존 public class/method/signature가 유지된다.
- Calculator와 ML이 같은 facade/capability owner를 재사용한다.
- HSPF2 config/point/variable/legacy 책임이 분리된다.
- SEER2 variable-capacity engine이 facade에서 분리된다.
- 새 multi-capacity engine이 sibling으로 추가 가능한 seam이 존재한다.
- generic base engine이나 universal point/result schema는 도입되지 않는다.

### Behavior

- 모든 기존 AHRI variable-capacity official golden이 정확히 통과한다.
- HSPF2 v2 결과도 변경되지 않는다.
- raw result mapping과 diagnostics가 호환된다.
- aliases, fallbacks, optional points, cut-out, defrost, rounding이 변경되지 않는다.
- SEER2 application seasonal scaling과 ML envelope chain이 변경되지 않는다.

### Structure

- HSPF2 facade는 orchestration/delegation 중심으로 축소된다.
- formula owner 파일은 project soft limit을 초과하지 않거나 불가피성이 명확해야 한다.
- 신규 structure warning이 없다.
- 기존 HSPF2 hotspot을 새 allowlist로 숨기지 않는다.
- core에 UI/ML toolkit dependency가 생기지 않는다.

### Documentation

- AHRI owner 문서에 official-calculator golden provenance가 기록된다.
- 최종 owner map이 dev notes에 반영된다.
- standard formula 설명과 structural refactor 설명을 혼동하지 않는다.

---

## 16. Multi-Capacity Handoff

이 refactor가 완료된 뒤 multi-capacity workstream은 다음 구조를 전제로 시작한다.

```text
AHRI SEER2 facade
  -> variable-capacity engine       # current official golden preserved
  -> future two-stage engine        # triple-capacity product cooling also uses this path

AHRI HSPF2 facade
  -> variable-capacity engine       # current official golden preserved
  -> future two-stage engine
  -> future triple-capacity northern engine
```

Refactor 단계에서는 product-type resolver를 미리 만들지 않는다. Two-stage/triple-capacity 공식 audit에서 실제 request boundary와 필수 시험점 schema가 확정된 후 추가한다.

기존 variable-capacity engine을 수정해서 multi-capacity 조건문을 누적하지 않는다. 신규 engine은 sibling owner로 추가하고, public capability/application boundary에서 명시적 product classification을 전달하는 후속 설계를 사용한다.

---

## 17. Agent Implementation Guidance

이 문서는 구현 경계를 확정한다. 구현 agent는 현재 owner와 sibling 구조를 확인한 뒤 최소하고 일관된 내부 파일 구성을 선택한다.

중요한 판단 순서는 다음과 같다.

1. 공식 golden과 public contract를 먼저 잠근다.
2. 구조만 이동한다.
3. 각 slice에서 deep behavior parity를 증명한다.
4. HSPF2를 먼저 닫은 뒤 SEER2를 분리한다.
5. 두 engine을 본 뒤에만 공통 primitive를 판단한다.
6. formula/config/API 개선 아이디어는 발견 사항으로 남기고 이번 diff에 섞지 않는다.
7. refactor closeout 전에는 multi-capacity 구현을 시작하지 않는다.

구조상 더 좋은 코드가 기존 golden과 다르게 계산되면, 이번 workstream에서는 더 좋은 코드가 아니라 실패한 refactor다.
