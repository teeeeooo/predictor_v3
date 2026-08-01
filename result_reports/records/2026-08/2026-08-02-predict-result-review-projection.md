record:
  date: 2026-08-02
  topic: predict-result-review-projection
  tags: predict, result-review, projection, clipboard, provenance, presentation
  memory_review: no-change
  memory_reason: The active design, architecture, Work Plan, and indexed record are sufficient until independent audit and merge closeout.
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: local-with-reason

# Change Reason

Predict needed a review surface without restoring split result storage or
combining edited current capacity with historical accepted outputs. The existing
unified-table rectangular copy helper also could not own header-bearing full-row
copy with hidden typed evidence and execution provenance.

# Contract / Behavior Changed

One Qt-free Result Review package now projects the current canonical session
order on demand. It obtains status/freshness/issues from `ResultRow`, executed
capacity from pinned context evidence, EER/COP from `DerivedMetricOutcome`, and
frequency/refrigerant values from stable-identity `TargetOutcome` values. A row
without executed evidence may show current case capacity. Four specification
groups resolve values by stable Feature identity and use current generation
labels/keys without truncating their canonical text.

The shared PySide table seam is read-only, renders unavailable values as `—`,
formats EER/COP to two decimals without changing raw values, visually elides the
single-line summary, and exposes the full text by tooltip. Full-row copy writes
header-bearing TSV in canonical order with the visible ten fields first, then
raw cooling/heating power, freshness, stable case identity, execution and model
provenance, typed power source metadata, and issue detail. The application
document retains the richer typed rows behind the flat clipboard encoding.

# Evidence And Verification

Focused projection, status, stale replacement, summary, clipboard, immutable
state, and offscreen Qt model/view tests cover the Slice 4 behavior. Targeted
canonical result, Slice 3 enrichment, freshness, generation migration,
standalone/embedded composition, and schema compatibility suites plus changed
Python compilation, structure, staged change, and diff checks are the Worker
validation boundary. A fresh independent exact-head Auditor remains required.

# Changed Files

The change adds Qt-free Result Review contracts/projection/presentation/clipboard
owners, a shared PySide read-only table model/view, composition wiring, focused
tests, and source-completing architecture/design/current-state documentation.

# Known Risks

Slice 5 still owns Layout B composition, workspace navigation, and narrow
embedded viewport pinning. CSV/XLSX file export, export dialogs/preferences,
bulk paste, persistent detail/Full Context, graph/Advanced, partial-target Active
expansion, Target/unit authoring, seasonal metrics, Calculate orchestration,
training/model changes, and Calculator formula changes remain excluded. No
production data, model, generation, lifecycle artifact, or user session is
mutated by this projection.
