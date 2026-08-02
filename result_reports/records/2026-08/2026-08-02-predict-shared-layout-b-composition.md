record:
  date: 2026-08-02
  topic: predict-shared-layout-b-composition
  tags: predict, layout-b, workspace-state, result-review, qt, generation
  memory_review: no-change
  memory_reason: The approved design, architecture, Work Plan, and Slice 4 record remain the current owner set; this record completes the Slice 5 source boundary for audit.
change_gate:
  new_source: split
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Standalone and Train-embedded Predict needed one full-area Input/Result switch
without duplicating navigation policy, result storage, or shell-specific state
machines. Runtime composition replacement also needed to rebind both surfaces
while preserving the user's current surface and stable selected case.

# Contract / Behavior Changed

One Qt-free `PredictWorkspaceState` now owns current surface, selected stable
`case_id`, run-start surface, run-local explicit user choice, and the one terminal
auto-reveal decision. Input is initial. Manual switching remains available while
running. Progressive rows refresh the existing Slice 4 projection without
navigating. Complete or partial terminal evidence reveals Result unless an
explicit Input choice suppresses it; validation-only returns to Input and
error/invalid/cancel-only terminal evidence does not force Result. Every new run
resets prior run-local choice state.

`PredictWorkspace` composes two cached full-area pages over one canonical
session. A stable-identity bridge transfers only current case identity; each
table retains local selection, focus, and independent horizontal scroll state.
Deleted identities reconcile without dangling state. Authoring commands are
disabled on Result. Copy retains selected-cell behavior on Input and uses the
Slice 4 provenance-preserving full-row TSV on Result.

Runtime generation preparation carries the same workspace-state owner into the
destination composition. Commit/rebind and rollback replace both Input and
Result presentation models while retaining the canonical session, current
surface, surviving selected identity, and independent scroll positions. No
frozen/pinned table or synchronized auxiliary view is introduced.

# Evidence And Verification

Focused Qt-free state and offscreen Layout B tests cover initial/manual
navigation, stable-case reconciliation, local table interaction, progressive and
terminal lifecycle behavior, command routing, clipboard preservation, and
runtime rebinding. Targeted Result Review, canonical Predict workspace,
generation migration/replacement, standalone/embedded shell, and schema suites
plus changed Python compilation, structure, staged change, and diff checks form
the Worker validation boundary. A fresh independent exact-head Auditor remains
required before merge or Slice 5 close.

Worker evidence: 184 focused/targeted projection, workspace, generation,
standalone/embedded, and schema tests plus 41 prediction worker/execution tests
passed. Changed Predict/test Python compilation passed. The structure guard
passed with its 34 existing soft warnings, and `git diff --check` passed. The
staged change gate is recorded at commit preparation. Interactive manual smoke
is not claimed; equivalent surface behavior is covered by offscreen Qt tests.

# Changed Files

The change adds the Qt-free workspace-state package; cached Layout B, stable-case
selection, coordinated model notification, table setup, and status UI helpers;
wires the state owner through Predict composition/runtime replacement; extends
the read-only Result Review model's notification seam; adds focused tests; and
updates source-completing architecture/current-state documentation.

# Known Risks And Exclusions

No persistent process-restart workspace state, pinned/frozen columns, bulk-paste
transaction, CSV/XLSX export, export preferences, detail/Full Context surface,
graph/Advanced, partial-target Active expansion, seasonal metrics,
Predict-to-Calculate orchestration, training/model behavior, public/generated
schema, persisted Feature Definition shape, or Calculator formula is changed.
Slice 6 bulk paste and later file export retain separate ownership.
