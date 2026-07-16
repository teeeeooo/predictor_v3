```yaml
record:
  date: 2026-07-15
  topic: train-admin-phase3-slice3d-audit-correction
  tags: train-admin, data-definition, data-mapping, phase-3, slice-3d, audit-correction, reconciliation, row-occurrence
  memory_review: updated
  memory_reason: The durable Slice 3D contract now distinguishes requirement-owned presentation metadata from mapping-owned backing values and resolves validation cells by exact row occurrence.
change_gate:
  new_source: small
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

The initial Slice 3D projection added the latest Mapping Requirement metadata to
already-projected groups without removing superseded metadata. Coverage also
matched issue rows by row key or row index, so one invalid duplicate-key
occurrence could contaminate another occurrence.

# Contract / Behavior Changed

- Qt-free editor-group provenance now retains the Data Mapping base columns,
  notes, data types, and required columns separately from the current Data
  Definition requirement columns. Every refresh rebuilds the effective group
  from that base plus the latest saved requirements.
- Required/optional classification, type, dynamic visibility, group note,
  coverage, and required-missing validation now replace prior requirement-owned
  metadata. The same projection is idempotent across draft, baseline, and every
  undo snapshot and does not create a user command.
- Removing a requirement hides its column and removes its coverage/validation
  applicability while retaining row backing payload. Re-adding the requirement
  restores the prior concrete value; only explicit mapping Save writes JSON.
- Coverage and validation targets now carry group, attribute, row key,
  occurrence, and a current local-index hint. A valid issue row index is exact
  authority; index-less duplicate keys require an exact occurrence and otherwise
  remain unscoped.
- Issue and coverage navigation re-resolve stable occurrence identity against
  the latest state. A removed occurrence fails without clamping or moving to an
  unrelated row.

# Evidence And Verification

- Focused Qt-free tests cover required to optional, optional to required,
  removal/re-add, backing-value restoration, latest type replacement, multiple
  requirement replacement/order, repeated projection, note cleanup, baseline,
  undo history, no automatic write, and explicit hidden-payload Save.
- Duplicate-row tests cover second/first invalid occurrence, attribute isolation,
  valid-index authority, index-less occurrence fallback, ambiguous unscoped
  issues, index shifts, disappeared targets, and issue/coverage target alignment.
- Offscreen Train workflows cover saved Add/Open, optional Save/Open,
  deactivation/removal, stale-handoff rejection, re-add restoration, F&T/PFC
  backing values, exact duplicate coverage focus, and exact issue focus.
- Final impacted regression passed 551 tests across Data Definition, Data Mapping
  application/service/core/UI/import/export, condenser policy, Predict adapters,
  ML catalog parity, and Train shell.
- Compile, diff, protected-path review, structure guard, and staged agent change
  gate passed. Structure findings remain warning-only existing hotspots. Native
  Computer Use was not run, as required by this correction scope.

# Changed Files

- mapping editor provenance and latest requirement reprojection
- stable Data Mapping target contracts, occurrence resolver, coverage matching,
  presentation targeting, and Qt focus adapter
- focused Qt-free, service/session, persistence, and offscreen workflow tests
- current work plan, memory seed, result-record index, and this correction record

# Known Risks

- Duplicate identity remains the accepted row-key plus occurrence contract; this
  correction does not introduce a new persistent row identifier or change import
  merge semantics.
- Existing Data Mapping service/panel hotspots remain unchanged. The new stable
  resolver is isolated under the existing application package, and no Slice 3E
  editing/native responsibility was added.
- Predict remains restart-required after schema Save.
