```yaml
record:
  date: 2026-07-14
  topic: train-admin-mapping-data-foundation-persistence-correction
  tags: train-admin, mapping, persistence, hidden-payload, atomic-save, correction
  memory_review: updated
  memory_reason: Preserve the durable distinction between hidden runtime row data and definition-owned visible schema.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
```

# Change Reason

The final Phase 1 re-audit found that editor projection retained undeclared
runtime payload in row backing values, but persistence rebuilt payload from
visible columns only. Any unrelated Save therefore silently deleted hidden
runtime data.

# Contract / Behavior Changed

- Persistence now starts from each current editor row's backing payload,
  removes group key/identity controls, and overlays visible columns using the
  existing canonical value policy.
- Undeclared payload remains hidden from Data Mapping columns, validation, and
  JSON/XLSX review exports, but survives Save/reload and follows its row through
  key rename. Row deletion removes it.
- Visible values remain authoritative, including optional empty values; number
  and boolean overlays retain finite-number and canonical-boolean rules.
- The policy applies uniformly to IDU, Evap Index, ODU, Compressor,
  Refrigerant, Expansion, and ODU Cond Specs without changing option or
  condenser identity.
- Hidden non-finite payload is preserved into the JSON boundary, where
  `allow_nan=False` fails the atomic Save without replacing the existing file.

# Evidence And Verification

- Focused persistence, dynamic requirement, editor command/validation, Predict,
  and DEV mock regression suite: 106 passed.
- Full repository suite: 1974 passed, 2 expected xfailed.
- Tests cover all seven groups, visible overlay type/empty precedence,
  save/reload, JSON/XLSX non-exposure, later requirement restoration,
  rename/delete row association, and hidden NaN failure preservation.
- Protected mapping fixtures and `data/mapping.json` are unchanged.

# Changed Files

- Mapping editor runtime persistence payload assembly
- Focused persistence and Train dynamic requirement integration tests
- Phase 1 design/closeout state, work plan, project log, memory, and report index

# Known Risks

Hidden raw payload has no editor deletion surface by design; explicit unknown
payload management remains outside Phase 1. Repository fixture success does not
prove company mapping completeness, real-data quality, model quality, or
production readiness. PR #14 remains Draft/Open pending final re-audit.
