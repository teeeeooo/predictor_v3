```yaml
record:
  date: 2026-07-14
  topic: train-admin-phase2-slice2a-native-audit-correction
  tags: train-admin, mapping, phase-2, slice-2a, draft-preservation, native-macos, computer-use
  memory_review: updated
  memory_reason: Preserve the draft/source availability separation and the bounded native evidence contract before Slice 2B.
```

# Change Reason

Slice 2A audit found that source loss hid a valid dirty draft, Refresh had been
removed, empty-message exceptions could fail while building error state, and
the layout had only offscreen evidence.

# Contract / Behavior Changed

- A service-owned cached draft remains visible and dirty when its source becomes
  missing; resource availability is reported independently.
- Refresh reprojects current draft/validation/UI state without provider reload,
  while Reload reads the provider and preserves the cached draft on failure.
- Initial load and Reload convert empty-message exceptions to stable summaries.
- Status/workspace presentation helpers moved out of the panel. Before Slice 2B,
  toolbar/selection/model binding and controller presentation projection are the
  concrete split triggers; no spreadsheet framework was introduced.
- Qt editor commits update their current model before a deferred non-destructive
  refresh, avoiding synchronous model replacement during delegate commit.

# Evidence And Verification

- Impacted automated regression: 208 passed offscreen, including controller,
  service, UI models, shell, dynamic requirements, persistence, validation,
  export, runtime adapter, and condenser policy.
- Native macOS onscreen validation used Computer Use after display wake, with
  populated, dynamic, empty, missing, load-error, dirty-source-missing, compact,
  and collapsed-detail captures.
- Native Refresh and Reload were clicked; Reload confirmation was operated by
  keyboard and a restored temporary source reloaded successfully.
- The capture manifest records the bounded Qt delegate text-entry limitation.
- Protected fixture and `data/mapping.json` diffs are empty.

# Changed Files

- Data Mapping service/controller draft and resource state projection
- Data Mapping toolbar, presentation helpers, and safe editor refresh path
- Focused controller/service/UI regression tests
- Phase 2/current-work state and native PNG evidence manifest

# Known Risks

The panel and controller remain above the 400 LOC soft limit. Slice 2B must not
add spreadsheet interaction until the recorded owner split is performed. Native
Computer Use did not reliably replace Qt delegate text, so direct editor typing
is guarded automatically rather than claimed as native proof. PR #15 remains
Draft/Open and Slice 2B+ is not started.
