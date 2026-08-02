record:
  date: 2026-08-02
  topic: predict-bulk-paste-transaction
  tags: predict, bulk-paste, transaction, mapping, provenance, undo, qt
  memory_review: no-change
  memory_reason: The approved overhaul design and current Work Plan already preserve Slice 6 as the active audit gate; this Worker record completes its source boundary without closing or merging it.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Predict paste previously iterated visible cells through `setData()`, dropping
overflow rows and exposing intermediate per-cell cascade, revision, refresh, and
undo side effects. Excel-first multi-row authoring requires one canonical
transaction whose result is based on each final pasted row combination.

# Contract / Behavior Changed

One Qt-free Predict application transaction now parses the complete headerless
value-only TSV against generation-ordered editable input identities, stages every
destination row, loads mapping once, and reuses existing mapping/cascade/autofill
policy. Explicitly pasted dependent values survive parent clearing; only stale
non-pasted dependents clear. Final numeric and mapping-combination issues retain
the raw canonical value and stable case/column identity while valid rows commit.

The canonical session state boundary atomically commits required overflow rows
and final input/autofill states. Changed cases receive one input-revision change,
lose old run attachment authority, and stale/reset existing results through the
same fail-closed session rules; unaffected cases/results remain unchanged.
Unexpected commit failure restores exact pre-transaction cases, results, run
authority, revision, and case allocator. One sealed undo removes added rows and
restores prior input/mapping-derived state while incrementing changed input
provenance again and never reviving a historical result as fresh.

The Predict view no longer performs repeated-cell paste. Toolbar and keyboard
paste route to the same workspace handler, mutation gates remain enforced, and
Input/Result Review receive one coordinated model reset plus one aggregate
completion message. Existing single-cell edit/clear behavior retains its owners.
Runtime generation replacement rebinds the generation-specific transaction and
clears obsolete undo context. Standalone and Train-embedded Predict use the same
workspace composition.

# Evidence And Verification

Focused application and offscreen Qt tests cover multi-row TSV, overflow row
creation, final-combination mapping, explicit/non-pasted dependent behavior,
mapping unavailable paths, precise invalid issues with valid-row survival,
affected-only stale state, late-result rejection, injected commit rollback,
compound fail-closed undo, active input identity/order, one reset bracket,
aggregate feedback, toolbar/keyboard parity, and mutation gates.

The targeted Predict session/provenance, mapping, spreadsheet, shared workspace,
generation migration, Layout B, Result Review, and Train embedding suite passed
155 tests. Final Worker validation also includes changed Python compilation,
structure and staged change gates, schema compatibility guards, and diff checks.
A fresh independent exact-head Auditor remains required before merge or Slice 6
close.

# Changed Files

The change adds split bulk-paste contract/staging/orchestration owners and a
canonical input transaction authority; wires them through Predict composition,
generation replacement, model issue projection, view/workspace paste/undo, and
the mapping option adapter; adds focused and compatibility tests; and updates
this architecture owner plus the record index.

# Known Risks

Interactive platform smoke is not claimed; shortcut and selection behavior is
covered by offscreen adapter tests. File export, header recognition, arbitrary
column matching, import UI, redo, Slice 6 audit approval/close/merge, Calculate,
training/model behavior, public/generated schema, persisted Feature Definition,
and Calculator formulas remain excluded.

Structure triage: the new application, staging, state-authority, and Qt adapter
owners are split below the new-source soft limit. `PredictWorkspace` retains
composition/routing only for this feature after the paste UI adapter extraction.
`PredictSession` now exceeds the 400-LOC soft warning at 425 LOC solely through
its typed canonical transaction façade; commit/rollback/undo logic remains in
the separate state authority. Splitting the existing result acceptance/session
facade is not required for this bounded slice and is deferred to a dedicated
owner audit before another substantial session responsibility is added.
