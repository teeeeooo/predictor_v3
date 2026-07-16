# Phase 3 Slice 3F table-first correction evidence

## Status

The correction evidence folder is reserved for the six-state native rerun. The
safe Cocoa scenario was prepared, but Computer Use reported that macOS was
locked and automatic unlock was unavailable. No native PNG is claimed from that
attempt, and the known AppKit Qt table accessibility path was not used.

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
| `05-saved-mapping-next-step.png` | 1280x820 | Saved-only Data Mapping next step |
| `06-clean-table-first-compact.png` | 900x640 | Clean compact table-first workspace |

Until the locked-desktop rerun completes, this README and the correction record
are the authoritative status evidence; the previous Slice 3F screenshots are
not acceptance evidence for the amended composition.
