```yaml
record:
  date: 2026-07-12
  topic: calculator-result-actions-notebook-correction
  tags: calculator, tkinter, result-actions, csv, notebook, geometry, lifecycle, correction
  memory_review: updated
  memory_reason: Single result actions and stable Notebook identity/geometry are durable cross-profile Calculator presentation contracts.
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Final GUI review found inconsistent Single result actions, selection-dependent
Notebook tab size, incomplete initial SCOP status metadata, and an AHRI/Korea
visibility check that failed under Tkinter module class-identity changes.

# Contract / Behavior Changed

AHRI and Korea visibility now recognizes the actual Tk `TNotebook` identity,
preserving hidden/visible settle-cycle behavior independently of Python class
reload order. SCOP initializes status container and Label metadata through the
same pending-status path used by later transitions.

All active non-Brazil Single sections now append visible Copy and Export CSV
actions after existing Batch/detail actions. Dedicated compact results retain
their native headers/rows; `ResultPanel` retains latest summary order and emits
sectioned title/field/value/status CSV. Detail and Batch exports remain separate,
and Brazil's Result/Rule/Final payload is unchanged.

The Calculator theme fixes font and padding for default and top-level Notebook
tabs, clears native selected-padding maps, and keeps selection indication in
the existing foreground/background colors.

# Evidence And Verification

- Full Tk Calculator UI selection passed 661 tests in suite order, including the formerly order-dependent AHRI refit tests.
- Focused result action, SCOP metadata, lifecycle, Brazil regression, and geometry owner selection passed 123 tests before the final status-only fallback; the complete suite passed afterward.
- Notebook geometry focused verification passed after moving literals to the layout-token owner.
- Python compilation, whitespace checks, and structure guard passed; warnings are the two intentional new-package registry notices plus existing hotspots.

# Changed Files

- Calculator theme/layout constants and top-level style binding
- AHRI/Korea tab visibility checks and SCOP status initialization
- `ResultPanel`, shared CSV adapter, and small `result_actions` presentation package
- ten active non-Brazil Single section action rows
- focused lifecycle, result payload, geometry, inventory, and Brazil-preservation tests
- work plan, project log, memory seed, and report index

# Known Risks

The structure guard reports the new bounded `result_actions` package as absent
from its warning-only registry; changing the agent harness was outside this UI
correction. Existing EN14825 section hotspot warnings remain wiring-only for
this change. Automated Tk geometry and action tests passed, but the user should
perform the requested final visible GUI review before merge.
