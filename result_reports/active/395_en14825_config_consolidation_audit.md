# 395 EN14825 config consolidation audit

## Goal

Audit current EN14825 config ownership before any code or config migration.

## Scope

- Checked active references to `eu.json`, `en14825_scop.json`,
  `en14825.json`, EN14825 profiles, and calculator config loading.
- Reviewed focused memory/summary/archive evidence for EN14825 defaults and
  config decisions.
- Updated `docs/WORK_PLAN.md` next action.
- Did not edit source, config, tests, archive, summary, memory, or project log
  files.

## Current Config References

- `core/calculator_profiles.py` registers both `en14825_scop` and
  `en14825_seer` with `config_path="data/region_configs/en14825_scop.json"`.
- `core/calculator_dispatcher.py` passes the profile `config_path` into
  `EN14825Calculator(config_path)`, so both EN14825 profiles instantiate the
  same calculator with the same SCOP-named JSON.
- `EN14825Calculator.__init__()` defaults to
  `data/region_configs/en14825_scop.json` and always loads it into
  `self.scop_config`.
- SEER currently uses hard-coded module constants for Table 36 cooling bins,
  cooling design/test temperatures, default Cd, and SEER operational hours.
  `calculate_seer()` only touches the loaded JSON indirectly through
  construction; it does not read SCOP config keys during SEER math.
- SCOP actively uses `self.scop_config` for climate data, heating test point
  schema, climate/appliance operational hours, defaults, and source metadata.
- `data/region_configs/eu.json` exists and contains SEER/cooling config-like
  data, but active non-archive search found no runtime or test owner consuming
  it.
- No active `data/region_configs/en14825.json` reference or file was found.

## Memory And Summary Findings

- Memory seed only preserves the EN14825 GUI prefill defaults hierarchy: UI
  prefill defaults are user-editable and separate from config validation limits.
- Summary 364 records the same defaults hierarchy decision and SEER model/adapter
  foundation; it does not record a completed single-config consolidation.
- Archive 357 used both `en14825_scop.json` and `eu.json` as design references.
  Archive 359 corrected the misconception that config validation limits should
  become UI prefill defaults, and explicitly left config files unchanged.
- Archive 360 built SEER model/adapter foundation while leaving
  `core/calculator_en14825.py` and `data/region_configs` unchanged.
- Summary 385 closes the EN14825 UI correction lifecycle and recommends further
  audit/design slices before expanding appliance-type behavior; it does not
  settle config ownership.
- Report 386 recommended keeping SCOP heating hours in
  `en14825_scop.json` and considering a cooling-hours owner later. Report 387
  subsequently added SEER cooling-only behavior without SCOP config changes.

## Decision

- The current split is an implementation-history artifact, not an intentional
  final architecture:
  - SCOP has a real JSON owner because climate data and Annex D heating hours
    were implemented config-first.
  - SEER has legacy `eu.json` data but the active calculator uses core-local
    constants instead.
  - `en14825_seer` points to `en14825_scop.json` because the shared constructor
    requires a path, while SEER does not consume SCOP-specific keys. This is an
    intermediate compatibility state, not evidence that the SCOP file is the
    correct long-term EN14825 common owner.
- Long-term direction should be a single EN14825 config owner, most likely
  `data/region_configs/en14825.json`, with explicit SEER and SCOP sections.
- `eu.json` is an unused/stale candidate. Do not delete or rename it before the
  consolidation design defines migration, compatibility, and reference-doc
  handling.
- `en14825_scop.json` is a rename/migration candidate, but it should remain
  untouched until a design fixes the schema and transition path.
- SEER hard-coded constants should be evaluated for config migration with a
  compatibility-preserving resolver. The migration should not change golden
  results or public API behavior.
- SCOP Warmer A inactive point correction should be designed with the new config
  schema before implementation. If implemented before consolidation, it risks
  encoding a temporary SCOP-only schema that must be migrated again.
- EN14825 batch integration preflight should wait until config ownership is
  designed, because batch schemas need stable defaults, validation limits,
  appliance-hour ownership, and correction metadata.

## Next Action

Run an EN14825 config consolidation design slice:

- choose the final config path/name and section schema;
- define backward-compatible handling for existing `en14825_scop.json` and
  unused `eu.json`;
- decide which SEER constants move into config;
- include the SCOP Warmer A inactive point correction contract in the target
  schema;
- list focused migration tests, but do not implement migration in the design
  slice.

## Verification

- `git diff --check` OK.
- `git status --short` reviewed before commit.

## code_map_check

- skipped - audit/report only, no structural source edit

## Project Memory Delta

- Candidate: EN14825 config ownership should be consolidated through a design
  slice before batch integration or SCOP Warmer A inactive correction.
