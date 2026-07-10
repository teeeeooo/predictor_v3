# Calculator Sample Data Inventory and Empty-State Policy

## Status

Active reference for detail-view sequencing and later sample-removal slices.
This document records policy and inventory only; it does not authorize code or
fixture changes.

## Goal

Separate calculator option/standard defaults that support an empty-state UX
from product performance demo values that should eventually be removed, while
making EN14825/AHRI detail views an explicit prerequisite for removal.

## Audit Boundary and Method

- Production UI scope: profile sections under `apps/calculator/ui/sections/`,
  AHRI mock owner, and EN14825 common-option tab defaults.
- Search targets: `set_values`, Tk variable defaults, `_DEFAULT_VALUES`, and
  explicit DEV/MOCK/SAMPLE owners.
- Read scope: initialization/default ranges and Hong Kong detail-panel ownership
  only; no full-file audit or calculation/core/config interpretation.
- Excluded: test fixtures, golden data, core/config defaults not used as UI
  prefill, restored user snapshots, and user-entered batch cases.

## Classification Policy

### Keep by default

- Standard, calculation-condition, and option defaults needed to select a valid
  mode or express a conventional neutral state.
- Boolean/profile state needed to define which optional inputs are active.
- Neutral ancillary power defaults of zero where zero is the existing explicit
  UI condition rather than a product performance demonstration.

### Remove after prerequisites

- Product-specific capacity, power, EER, COP, declared, or tested values.
- Feasibility/MVP values whose purpose is to make a result appear immediately.
- DEV/mock/sample performance dictionaries used for manual visual smoke.

### Additional decision required

- Values whose meaning is both a standard condition and potentially a product
  declaration must be resolved at the adapter/config/UI owner before removal.
- Restored snapshots are user state, not sample defaults, and remain outside the
  removal policy.

## Profile Inventory

| Profile | Keep | Remove candidate | Current detail state | Judgment |
| --- | --- | --- | --- | --- |
| EN14825 SEER | Tdesignc and Cd from adapter/config defaults; Type; Pto/Psb/Pck/Poff neutral zero | Pdesignc `3000`; A-D declared capacity/EER and tested capacity/power prefill | No `BinDetailPanel`/detail toggle in SEER section | Detail design/implementation must precede sample removal. |
| EN14825 SCOP | Cd; Type; Tbiv/TOL condition defaults; average/warmer/colder activation state; neutral ancillary powers | Per-climate Pdesignh `3000`; declared capacity/COP and tested capacity/power for A/B/C/D/TOL/Tbiv | No `BinDetailPanel`/detail toggle in SCOP section | Detail design/implementation must precede sample removal. Tdesignh remains derived display, not sample input. |
| AHRI SEER2 | Type `HP` | None found in main section | No detail toggle/panel | Already conforms to performance-empty initialization; detail still belongs in the shared EN/AHRI design slice. |
| AHRI HSPF2 | Region IV; H42/H12/H22 enable state; H1N=H32 Hz; MinSpd; Cd; Defrost Credit; Cut Out/In | Isolated `HSPF2_DEV_SAMPLE_VALUES`: A2 and H01/H11/H1N/H2Int/H32/H42/H12/H22 capacity/power | No detail toggle/panel | Remove mock population only after detail implementation and empty-state guards. Delete owner/import in that later slice. |
| ISO/ISEER 2-point | Mode/profile selection outside performance table | Full/half capacity and power prefill | Existing detail toggle and `BinDetailPanel` with selectable sources/CSV | Eligible for a later isolated sample-removal slice; no new detail prerequisite. |
| Hong Kong CSPF | Profile identity | Declared capacity plus full/half capacity/power prefill | Existing detail toggle, trace rows/status, graph/table, CSV | Eligible for isolated removal after empty-state behavior tests. |
| Hong Kong HSPF | Profile identity | Full/half capacity/power prefill | Existing detail toggle, heating detail schema, trace rows/status, CSV | Eligible for isolated removal after empty-state behavior tests. |
| SASO T3 | Optional 35 Min enabled state | `_DEFAULT_VALUES` capacity/power for 46 Full, 35 Full/Half/Min | Existing detail toggle, required/optional trace sources, CSV | Eligible for isolated removal; keep optional-point state independent of blank values. |

## Empty-State Contract

1. A newly opened calculator profile has blank product performance inputs.
2. Standard/mode/option defaults remain selected where an unselected state would
   be invalid or unnecessarily obstructive.
3. Automatic calculation remains enabled, but incomplete blank performance
   input resolves to an input-waiting state rather than a computed demo result.
4. Summary/result cells remain blank or show the established input-waiting
   status; they must not present a sample seasonal metric on launch.
5. Detail panels begin with no trace rows and the established no-detail/input
   waiting status. Detail visibility must not synthesize sample data.
6. Batch matrices remain blank unless restoring an explicit user snapshot.
7. Removing sample data must not change equations, config/schema, optional point
   inclusion, result formatting, or snapshot contracts.

## Detail-View Dependency

### Reference pattern

Hong Kong CSPF/HSPF demonstrate the target ownership pattern:

- section-owned detail toggle and visible/hidden lifecycle;
- reusable `BinDetailPanel` with source description and summary;
- trace rows plus explicit no-data/error status;
- detail table and lightweight graph;
- copy/CSV detail export boundary;
- optional callback so visible-content window fitting can react to detail state.

ISO/ISEER and SASO T3 also reuse this panel for multi-source/scenario traces.
The pattern is evidence, not a requirement to copy Hong Kong schemas into other
standards.

### Missing surfaces

EN14825 SEER/SCOP and AHRI SEER2/HSPF2 currently have no detail toggle,
`BinDetailPanel`, trace-row/status owner, or detail CSV surface. Their adapters
and core returns must be audited in a separate design slice to decide what
detail data exists without changing public result contracts.

### Required sequence

1. Design EN14825/AHRI detail schemas, source labels, adapter boundaries,
   no-data/error states, and export ownership.
2. Implement and verify detail views without changing initial sample values.
3. Remove main-section performance samples profile-by-profile.
4. Add empty-launch, input-waiting result, detail no-data, restored snapshot,
   and manual visual regression coverage.

Sample removal before steps 1-2 is prohibited by this policy because it would
remove the only immediately visible calculation evidence before equivalent
diagnostic/detail surfaces exist.

## Removal Slice Boundaries

- EN14825 and AHRI removal must be separate from detail implementation commits.
- ISO/ISEER, Hong Kong, and SASO removal should be profile-focused slices even
  though their detail prerequisite is already satisfied.
- Keep option defaults in each removal slice; do not convert boolean/profile
  state into blank/tri-state behavior opportunistically.
- Do not move demo values into config, fixtures, or core as a way to keep launch
  prefill.

## Next Action

EN14825/AHRI detail view design.
