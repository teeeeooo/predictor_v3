# All Active Calculator Standards Core Refactor Design

**Status:** R0 inventory and contract lock complete; R1-R6 implementation pending

**Base main:** `1d8eca3df9d36d7fbc65cd9f057c22d1917a6595`

**Branch:** `codex/all-standards-core-refactor`

**Reference:** `2026-07-12-ahri-seer2-hspf2-core-refactor-design.md`

## 1. Goal

`app_calculator.py`에서 실제 도달 가능한 non-AHRI standard 계산 core를
behavior-preserving 방식으로 분해한다. 외부 import, constructor, method,
profile/capability route, config 의미, result/diagnostics schema, 예외, rounding,
golden 값은 유지한다.

AHRI는 stable facade와 private owner package의 reference implementation으로만
사용한다. 이번 workstream에서 AHRI core 구조와 공식 golden은 변경하지 않는다.

## 2. Runtime Inventory

Audit 기준 호출 흐름은 다음과 같다.

```text
app_calculator.py
  -> apps.calculator.app
  -> apps.calculator.ui.calculator_app
  -> application adapter/usecase
  -> core.calculators.capability
  -> profile resolver / dispatcher
  -> stable standard facade
  -> private standard owners
```

| Runtime target | Profile / capability | Current owner | Classification | R0 decision |
| --- | --- | --- | --- | --- |
| EN 14825 SEER | `en14825_seer` / `en14825.seer` | `en14825.py` | `active_standard_engine` | R1 refactor |
| EN 14825 SCOP | `en14825_scop` / `en14825.scop` | `en14825.py` | `active_standard_engine` | R1 refactor |
| ISO T1 default CSPF | `iso_t1_default_2point_cspf` / `iso16358.cspf` | `iso16358.py` | `active_standard_engine` | R2 refactor |
| India ISEER | `india_iseer_cspf` / `iso16358.cspf` | `iso16358.py` | `active_standard_engine` | R2 refactor |
| Hong Kong CSPF | `hong_kong_cspf` / `iso16358.cspf` | `iso16358.py` | `active_standard_engine` | R2 refactor |
| Hong Kong HSPF | `hong_kong_hspf` / `iso16358.hspf` | `iso16358.py` | `active_standard_engine` | R2 refactor |
| SASO T3 CSPF | `saso_t3_cspf` / `iso16358.cspf` | `iso16358.py` | `active_standard_engine` | R2 refactor |
| KS C 9306 CSPF | `ks_c9306_cspf` / `ks_c9306.cspf` | `ks_c9306.py` | `active_standard_engine` | R3 refactor |
| KS C 9306 HSPF | `ks_c9306_hspf` / `ks_c9306.hspf` | `ks_c9306.py` | `active_standard_engine` | R3 refactor |
| Brazil CSPF compliance | `brazil_cspf_compliance` / `brazil.cspf_compliance` | `capability/brazil.py` + ISO facade | `already_compliant_no_change` | R4 verification only |
| AHRI SEER2/HSPF2 | AHRI enabled profiles/capabilities | stable facades + `_ahri/` | `already_compliant_no_change` | reference/excluded |
| AS/NZS Excel HSPF | disabled profile, no capability/UI route | `asnzs_hspf_excel.py` | `legacy_or_retired` | retain inactive compatibility evidence; no refactor |

No additional enabled profile, built-in capability, or Calculator tab formula
route was found. Brazil is visible inside the ISO tab but executes its own
composite capability. AS/NZS remains `enabled=False`; the enabled-profile
resolver cannot select it and the built-in capability registry does not expose
it.

## 3. Confirmed Decisions

| Decision | Contract |
| --- | --- |
| Behavior policy | Formula correction is forbidden; existing behavior is the oracle. |
| Facades | `en14825.py`, `iso16358.py`, and `ks_c9306.py` remain stable import paths. |
| Internal layout | Each standard receives its own private package; no cross-standard base engine or DSL. |
| Context | Config is loaded once and passed to internal owners. |
| Point ownership | Validation, measured/default/derived resolution, and provenance are outside seasonal loops. |
| Curve ownership | Capacity/power/COP/EER interpolation and boundary equations are separate from bin aggregation. |
| Seasonal ownership | SEER/SCOP, CSPF/HSPF, and KS-specific loops remain distinct engines. |
| Result ownership | Result key order, details, diagnostics, and rounding are assembled by explicit standard-local owners. |
| KS boundary | KS facade calls only KS owners; it does not call the ISO public facade. |
| Brazil | Existing capability-owned composite policy is already on the correct core boundary. |
| AS/NZS | Disabled compatibility code and tests remain intact; no active route is created. |
| Resource paths | Profile resources use static, packageable resolution; no scanning or dynamic plugin discovery. |
| Baseline failure | Any failure on the clean latest-main Calculator collection stops implementation. R0 baseline passed. |

## 4. Before / Target Owner Map

### 4.1 EN 14825

| Before | Target owner |
| --- | --- |
| JSON loading and SEER/SCOP section split in facade | private EN context |
| A/B/C/D validation and EERPL construction in facade | SEER point/performance owners |
| cooling bin loop in facade | SEER seasonal engine |
| climate/point-contract resolution in facade | SCOP point resolver |
| COP/capacity curves and backup behavior in facade | SCOP performance owner |
| heating bin loop in facade | SCOP seasonal engine |
| result dicts assembled inline | EN result assembler |

The application currently reads `seer_config`, `scop_config`, and the facade's
SCOP point-contract resolver for UI-neutral availability/default projection.
Those compatibility surfaces remain callable; application code must not import
the new private package.

### 4.2 ISO 16358

| Before | Target owner |
| --- | --- |
| config flags, point schema, bins, rounding state in one class | private ISO context |
| CSPF measured/default/profile-derived resolution | CSPF point resolver |
| load grouping, interpolation, ISO boundary EER | CSPF performance owner |
| CSPF bin aggregation | CSPF seasonal engine |
| common/legacy heating point resolution | HSPF point resolver |
| heating curves, frost/default, boundary/intersection equations | HSPF performance owners |
| legacy HSPF bins and ISO common bins in one class | separate legacy/common HSPF engines |
| CSPF/HSPF result mappings inline | ISO result assemblers |

Hong Kong HSPF is the only enabled ISO HSPF profile, while the sixteen official
exact cases remain the strongest common-engine branch oracle. T1/T3 and optional
minimum-test variation remain profile data, not standard-name conditionals.

### 4.3 KS C 9306

| Before | Target owner |
| --- | --- |
| config loading and mutable compatibility state in facade | private KS context |
| ROUND_HALF_UP, KS measured/derived points | KS point resolvers |
| KS interpolation and load-line intersections | KS performance owners |
| CSPF bin loop and rounding inline | KS CSPF seasonal/result owners |
| HSPF validation/fallback/curve/intersection/bin logic inline | KS HSPF point/performance/seasonal owners |
| HSPF result mapping inline | KS result assembler |

The current KS CSPF formula is already implemented locally rather than through
the ISO facade. R3 preserves that direction and removes stale comments that
describe a retired ISO delegation without changing code behavior.

### 4.4 Brazil and AS/NZS

Brazil's domain formula consists of exact three-point/two-point ISO result
comparison and two compliance rules. It already lives in
`core.calculators.capability.brazil`, while application code owns parsing and
presentation projection only. It is therefore verified, not rewritten.

AS/NZS is a disabled workbook compatibility adapter with its own calculator ID,
fixture namespace, and exact-match tests. Because there is no enabled profile,
capability, or UI inbound, R4 records exclusion and does not revive it.

## 5. Data Shape / API Boundary

Protected surfaces include:

- constructor and public method signatures, parameter defaults, positional and
  keyword meaning;
- facade import paths and caller-visible config attributes;
- profile IDs, capability IDs, calculator IDs, dispatcher routing;
- result key names and order, raw/rounded values, detail/bin/diagnostic shape;
- measured/default/derived/fallback source meaning;
- exception type, relied-upon message text, and fail-fast order;
- default config route and explicit config path override;
- application summary, batch/export, and UI schemas.

Private owner classes and internal dataclasses are not public contracts. Existing
tests that call old private helpers are redirected to semantic owner tests only
when the facade no longer needs the helper as a caller compatibility surface.

## 6. Commonization Boundary

No generic seasonal engine, universal resolver, base standard class, registry by
standard name, or formula DSL will be introduced. A helper may move to a shared
location only after two standards prove identical formula, units, boundary,
rounding point, and exception behavior. R5 may therefore legitimately make no
source change.

Initially identical-looking ISO and KS interpolation remains duplicated because
KS applies ROUND_HALF_UP, different derived-point semantics, KS intersections,
and different result rounding. EN interpolation remains EN-local.

## 7. Contract Lock

R0 adds ordered deep-result fingerprints and signature/attribute guards for:

- EN SEER detail for reversible/cooling-only and SCOP average/warmer/colder;
- ISO T1 default, India, Hong Kong CSPF, SASO T3, and Hong Kong HSPF;
- KS official CSPF and HSPF;
- Brazil composite capability;
- all three non-AHRI facade constructors and public calculation methods.

These fingerprints are characterization evidence, not new official fixtures.
Existing golden/formula/validation tests remain authoritative and expected values
must not be edited to accommodate the refactor.

## 8. Required Verification

Each slice must pass its contract lock, focused standard golden/formula/detail
tests, capability/dispatcher tests, and application adapter tests before commit.
R6 additionally runs:

- the complete import-derived Calculator pytest collection;
- all official/golden fixtures and existing xfail expectations;
- default resources from a temporary non-repo working directory;
- explicit config path overrides;
- `app_calculator.py` import plus one capability smoke per enabled non-AHRI route;
- `py_compile` for changed owners;
- `tools/check_code_structure.py`;
- cached staged change gate and whitespace check.

## 9. Migration / Refactor Path

1. R0: inventory, architecture decision, ordered contract fingerprints.
2. R1: EN context, SEER owners, SCOP owners, facade delegation.
3. R2: ISO context, CSPF owners, legacy/common HSPF owners, facade delegation.
4. R3: KS context, CSPF/HSPF owners, facade delegation.
5. R4: Brazil/no-change verification, AS/NZS exclusion, remaining-route audit.
6. R5: commonize only proven-identical primitives, otherwise document retained duplication.
7. R6: resource-path smoke, full regression, gates, closeout record and owner-map update.

Each implementation slice is independently committed and no slice begins with a
known regression from the previous slice.

## 10. Risks

| Risk | Mitigation |
| --- | --- |
| Floating-point drift from reordered expressions | Move formulas verbatim; ordered deep fingerprints and official golden tests. |
| Mutable config copied inconsistently across owners | One context object; facade and engines share the same config mapping. |
| Tests coupled to facade private helpers | Keep required compatibility delegates; move implementation-only assertions to owner tests. |
| New private source hotspot | Responsibility packages and structure gate; no new production file above hard LOC limit. |
| Relative profile paths fail outside repo cwd | Static resource resolution at dispatcher boundary while preserving facade contracts. |
| Formula discrepancy found during extraction | Preserve current behavior and list it as a correction candidate in closeout. |
| Accidental AS/NZS activation | Keep profile disabled and capability registry unchanged. |

## 11. Non-goals

- formula, standard interpretation, rounding, golden, fixture, config-schema, or
  public result changes;
- AHRI core changes;
- GUI layout/features, batch UX, user-facing error wording;
- new standard/profile or AS/NZS activation;
- actual one-exe build or packaging-spec edits;
- unrelated ML/Predict/Arc 15 work.

## 12. Next Codex Implementation Prompt

```text
Implement R1 EN 14825 behind the stable facade. Move config, point resolution,
performance curves, seasonal loops, and result assembly to EN-private owners;
preserve every signature, config attribute, result/detail value and exception;
then run EN contract/golden/detail/capability/application regression before commit.
```
