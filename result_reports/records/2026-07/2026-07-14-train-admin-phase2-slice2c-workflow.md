```yaml
record:
  date: 2026-07-14
  topic: train-admin-phase2-slice2c-workflow
  tags: train-admin, mapping, phase-2, slice-2c, validation, dirty, save, reload
  memory_review: updated
  memory_reason: Preserve baseline-diff dirty semantics and structured issue navigation across future Data Mapping workflow changes.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Data Mapping dirty state previously meant that some command had occurred, so
restoring baseline values could remain dirty. Validation rows also lacked a
stable UI navigation target, and Save/Reload success feedback omitted the
actual destination, backup, or reload completion.

# Contract / Behavior Changed

- The service-owned draft session compares current draft with the last loaded
  or successfully saved baseline. Editing back, Add-then-Delete, and undo to
  baseline become clean without UI-local state.
- Successful Save advances the baseline while a failed Save preserves it;
  successful Reload installs a new draft/baseline and clears command history,
  while failed Reload preserves all current state.
- Mapping validation issues carry an optional structured zero-based row index.
  The presentation owner resolves group/row/field targets and invalid-cell
  roles without parsing message strings.
- A feature-local navigator switches group, focuses, and scrolls to exact issue
  cells. Source/save/reload issues have no cell target.
- Save feedback includes destination and backup when present; Reload success is
  explicit. Existing atomic persistence and confirmation semantics remain.

# Evidence And Verification

- Seven focused workflow tests cover baseline restoration, Save success/failure,
  Reload success/failure, structured navigation, invalid decoration, Refresh
  preservation, source-issue no-navigation, and dynamic/PFC/hidden-payload
  Save-to-Reload round-trip.
- The impacted offscreen regression passed 223 tests across Slice 2B interaction,
  controller/service/UI, Data Definition integration, persistence/export,
  runtime adapters, condenser policy, and Train shell.
- Protected runtime fixture and `data/mapping.json` diffs are empty.

# Changed Files

- Service-owned draft session baseline state
- Validation DTO structured row identifier and editor validation projection
- Controller presentation issue targets and Save/Reload feedback
- Data Mapping invalid-cell model role and issue navigation owner
- Focused workflow and adjusted feedback assertions

# Known Risks

Changed row/cell counts are intentionally not displayed because an accurate
identity-aware count for duplicate/new rows would require a separate diff
contract. Dirty truth itself is exact draft equality. Native proof remains the
bounded post-Slice-2C Batch step; Save failure injection and previous Slice 2A
states remain automated or prior evidence only. Slice 2D is not started.
