```yaml
record:
  date: 2026-07-12
  topic: calculator-table-semantic-policy-correction
  tags: calculator, tkinter, semantic-tone, scop, korea, treeview, correction
  memory_review: no-change
  memory_reason: Existing table-family memory already assigns profile status meaning locally and all three families to the shared Tk visual policy owner.
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

The Slices 3–6 audit found three presentation-boundary leaks: SCOP tones were
assigned by row, Korea midpoint status text was treated as calculated output,
and the Treeview adapter rebound visual tokens instead of consuming the shared
Tk table policy.

# Contract / Behavior Changed

SCOP Declared/Tested identity cells remain default, actual values are
calculated, unavailable values are pending, and status code meaning is resolved
inside the SCOP presentation owner. Status containers and labels now update the
same semantic background and metadata while stale values still clear on error.

Korea midpoint normal values and status rendering use separate presenter paths.
CSPF and HSPF sections explicitly pass pending, invalid, or warning meaning;
row keys, order, and address-based reads remain unchanged.

The detail Treeview adapter now accepts an optional `TkTableVisualPolicy` and
resolves body, header, font, padding, divider, selection, row-height, and
outer-edge bindings through it. The default concrete visuals remain unchanged.

# Evidence And Verification

- 62 focused SCOP, Korea, Treeview policy, detail-schema, and integration tests passed.
- The full Tk Calculator UI selection reached 653 passed with two unrelated AHRI refit order-dependent failures; the isolated AHRI refit file passed 3/3 immediately afterward.
- Python compilation and whitespace checks passed.
- Structure guard completed with only pre-existing hotspot/class-count warnings.

# Changed Files

- SCOP compact result surface and section status wiring
- Korea midpoint guide presenter plus CSPF/HSPF status wiring
- shared Tk visual policy and Treeview style adapter
- focused semantic/policy and existing integration tests

# Known Risks

No manual GUI visual smoke was performed. Automated Tk style lookup, concrete
default values, tone metadata/background agreement, behavior, and lifecycle
tests passed; manual platform GUI smoke remains a separate merge gate. The two
AHRI refit failures appear suite-order dependent and outside this change, as the
unchanged focused file passed in isolation.
