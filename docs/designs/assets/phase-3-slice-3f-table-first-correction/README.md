# Phase 3 Slice 3F table-first correction evidence

## Status

The affected-state safe Cocoa rerun succeeded for the final-audit correction.
It replaced `05-saved-mapping-next-step.png` with a single-requirement state;
the other five unaffected correction PNGs remain valid. The manifest records
the audited implementation commit and `native_onscreen: true`. State
transitions were programmatic through Qt public panel/controller APIs; no
Computer Use, physical interaction, or known AppKit Qt table accessibility path
was used.

The earlier files under `../phase-3-slice-3f/` remain preserved as superseded
historical evidence for the previous Summary-led composition.

## Capture contract

Run `tools/dev/native_acceptance/run_phase3f_native_scenarios.py` against the
visible Cocoa environment after manual unlock. The runner writes
`native_manifest.json` with the commit SHA, native onscreen status, capture
source, logical/pixel sizes, synthetic provider, interaction classification,
protected/runtime fixture checks, accessibility-path use, and the historical
evidence supersession note.

Required correction states:

| File | Logical size | State |
| --- | --- | --- |
| `01-clean-table-first-normal.png` | 1280x820 | Clean normal table-first workspace |
| `02-details-modal-technical-expanded.png` | dialog below 1280x820 | On-demand read-only Details modal |
| `03-dirty-saveable-banner.png` | 1280x820 | Dirty saveable conditional surface |
| `04-blocked-save-banner.png` | 1280x820 | Blocked conditional surface |
| `05-saved-mapping-next-step.png` | 1280x820 | Single saved requirement: direct Data Mapping next step, no selector |
| `06-clean-table-first-compact.png` | 900x640 | Clean compact table-first workspace |

The current `native_manifest.json` and six PNGs are the authoritative native
status evidence for the amended composition. Capture `05` proves the direct
single-requirement presentation without a disabled or empty selector area; the
previous Slice 3F screenshots remain historical and are not acceptance evidence
for the amended composition.
