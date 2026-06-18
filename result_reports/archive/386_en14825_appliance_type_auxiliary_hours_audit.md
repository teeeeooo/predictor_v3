# 386 EN14825 Appliance Type Auxiliary Hours Audit

## Goal

Audit whether EN14825 appliance type should affect auxiliary operating hours in
predictor_v3, and define the implementation boundary without changing
calculation/UI code.

## Scope

- Official basis: EU air-conditioner labelling / ecodesign calculation
  documents for SEER/SCOP operating hours.
- Current behavior: `core/calculator_en14825.py`, EN14825 UI adapters/sections,
  current SCOP operational-hours config, and focused tests.
- Non-goals: no source, test, fixture, golden, schema, or UI behavior changes.

## Official Basis

Primary public basis used for this audit:

- Commission Delegated Regulation (EU) No 626/2011, Annex VII, Table 4:
  `https://www.energy-community.org/dam/jcr%3A01efda2e-96c2-4546-bdc5-7c6955f85dc9/Regulation_626_2011_EE.pdf`
- Commission Communication 2012/C 172/01, Table 8 and equations 1-3 / 20:
  `https://www.afec.es/documentos/english/communication-2012-172.pdf`

For air conditioners except single/double ducts, official hours distinguish
mode/function and appliance offering:

| Function / appliance offering | HCE/HHE | HTO | HSB | HOFF | HCK |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cooling, cooling-only | 350 | 221 | 2142 | 5088 | 7760 |
| Cooling, reversible | 350 | 221 | 2142 | 0 | 2672 |
| Heating, reversible, average | 1400 | 179 | 0 | 0 | 179 |
| Heating, reversible, warmer | 1400 | 755 | 0 | 0 | 755 |
| Heating, reversible, colder | 2100 | 131 | 0 | 0 | 131 |
| Heating-only, average | 1400 | 179 | 0 | 3672 | 3851 |
| Heating-only, warmer | 1400 | 755 | 0 | 4345 | 4476 |
| Heating-only, colder | 2100 | 131 | 0 | 2189 | 2944 |

Interpretation:

- Active equivalent hours (`HCE`, `HHE`) do not differ by appliance type within
  the same function/climate; `HHE` differs by climate.
- Auxiliary hours do differ by appliance type, especially `HOFF` and `HCK`.
- SEER uses `QCE = QC / SEERon + HTO*PTO + HCK*PCK + HOFF*POFF + HSB*PSB`.
- SCOP uses the same auxiliary structure for heating via `QHE`.

## Current Behavior

### SEER

- `calculate_seer()` has no `appliance_type` parameter.
- Cooling hours are hard-coded as reversible cooling constants:
  `H_CE=350`, `H_TO=221`, `H_SB=2142`, `H_CK=2672`, `H_OFF=0`.
- Therefore `p_off` has no SEER effect today because `H_OFF=0`.
- A cooling-only SEER case would need `H_OFF=5088` and `H_CK=7760`; current
  behavior undercounts auxiliary energy when `Poff` or `Pck` is nonzero.

### SCOP

- `calculate_scop()` accepts `appliance_type`, defaults to `reversible`, and
  selects `operational_hours` from `data/region_configs/en14825_scop.json`.
- Current JSON supports `reversible` and `heating_only`.
- SCOP correctly changes heating auxiliary hours for `heating_only`.
- A quick read-only check using existing golden inputs showed that nonzero
  `Poff/Pck` changes the result through `standby_kwh`, as expected:
  - average: reversible `standby_kwh=1.181`, heating_only `5.588`;
  - warmer: reversible `4.983`, heating_only `10.197`;
  - colder: reversible `0.865`, heating_only `3.491`.

### UI / Adapter

- `En14825Tab` exposes common appliance values `("reversible",
  "heating_only")`.
- SEER receives the same common numeric powers but ignores `appliance_type`.
- SCOP reads `appliance_type` from the common provider and forwards it through
  `ScopAdapter` to core.
- There is no `cooling_only` UI value, so cooling-only SEER cannot be selected.

## Gap

- Active bin hours: no gap for appliance type. Cooling active equivalent hours
  are the same for reversible and cooling-only; heating active equivalent hours
  are climate-dependent, not reversible-vs-heating-only dependent.
- Auxiliary hours: gap exists.
  - SEER lacks cooling-only auxiliary hours.
  - SCOP already has reversible/heating-only auxiliary hours.
- `Poff/Pck` impact:
  - For SEER cooling-only, nonzero `Poff` or `Pck` should materially lower
    SEER compared with reversible because `HOFF` and `HCK` are larger.
  - For SCOP heating-only, this is already reflected when `appliance_type` is
    `heating_only`.
- UI gap:
  - Current `reversible/heating_only` list is sufficient for SCOP but not for
    SEER.
  - Adding `cooling_only` to the shared dropdown without additional handling
    would create an invalid SCOP selection path, because SCOP currently expects
    only `reversible` or `heating_only`.

## Recommendation

Do not implement directly in the next code slice without a small
implementation preflight, because the clean solution touches public input
contract and the shared SEER/SCOP UI owner.

Recommended implementation boundary:

- Core owner: `core/calculator_en14825.py`
  - Add a backward-compatible optional SEER `appliance_type` parameter with
    default `reversible`.
  - Move cooling operational hours into a small resolver/constant mapping for
    `reversible` and `cooling_only`.
  - Preserve current default results for `calculate_seer()`.
- Config owner:
  - Keep SCOP heating hours in `data/region_configs/en14825_scop.json`.
  - Consider a separate cooling-hours constant/config owner only if multiple
    standards or regions will need it; otherwise a core-local mapping is enough.
- UI owner: `apps/calculator/ui/tabs/en14825_tab.py`
  - Avoid one shared unconstrained dropdown if it lets users select
    `cooling_only` while viewing SCOP.
  - Candidate designs:
    1. mode-aware appliance selector values per SEER/SCOP page; or
    2. separate cooling/heating appliance-type selectors; or
    3. shared selector plus SCOP-side validation/disable behavior for
       `cooling_only`.
- Adapter/tests:
  - Add SEER adapter propagation tests for `appliance_type`.
  - Add core tests showing default reversible SEER unchanged.
  - Add cooling-only SEER auxiliary-hour test where nonzero `Poff/Pck` lowers
    SEER using official hours.
  - Keep SCOP reversible/heating-only regression tests.

## Next Action

Run an implementation preflight for EN14825 appliance-type auxiliary hours:

- choose UI contract for cooling-only vs heating-only selections;
- decide whether cooling hours stay core-local or move to config;
- define backward-compatible `calculate_seer()` API change and focused tests;
- only then implement.

## Memory Seed

- Not updated. This audit confirms a gap and recommends a preflight, but does
  not finalize a durable implementation decision.
- Candidate: if the preflight chooses the UI contract and SEER API shape, record
  that decision in memory seed.

## Verification

- `python3 -B tools/check_code_structure.py`
- `git diff --check`
- `git status --short`

## Commit / Push

- Final commit hash and push status are reported in terminal output.
