# Train/Admin Phase 4F Audit Correction

```yaml
record:
  date: 2026-07-22
  topic: train-admin-phase4f-audit-correction
  tags: train-admin, phase-4f, one-hot, audit-correction, selector-lifecycle, source-binding, provider-validation
  memory_review: updated
  memory_reason: Selector takeover restoration and canonical runtime vocabulary ownership are durable Phase 4F invariants for authoring, publication, and Predict.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

Inactive group Add/Duplicate immediately converted an ordinary Feature into an
inactive One-hot selector and detach guessed a partial manual shape. Predict also
read Mapping-backed selector options from column metadata instead of the group's
canonical source binding, while an unknown External provider identity could reach
an internal `None.value` dereference.

## Contract / Behavior Changed

- Ordinary Feature takeover uses a canonical group-local restoration relation
  containing the complete persisted Feature shape. Add/Duplicate only reserve the
  selector while inactive; activation validates dependencies and atomically applies
  selector shape, emitted activation, ML order, runtime projection, and model impact.
- Disable or detach restores the exact shape and Predict order. Missing, ambiguous,
  or stale restoration evidence rejects the command. Existing native One-hot
  selectors without an ordinary predecessor remain dedicated and cannot be guessed
  back into an ordinary Feature.
- One core policy projects reservation eligibility, takeover state, blocker code,
  actionable reason, and affected owners. IDU/ODU/Mapping/cascade dependencies may
  be reserved harmlessly but block activation until explicitly migrated.
- Mapping-backed dropdowns resolve options from `OneHotRuntimeGroup.source_binding`;
  the encoder continues to consume category rules from the same immutable group
  snapshot. Ordinary non-One-hot dropdown ownership is unchanged, and a missing
  Mapping section is exposed as an actionable Mapping resource state.
- External source changes validate snapshot availability, exact preserved-category
  coverage, unknown/duplicate provider identities, non-empty unique values, and
  prepared snapshot revision before dereference or draft mutation. Every failure is
  a structured atomic command rejection.
- Contract v3 whole-candidate validation rejects dangling/stale restore relations,
  inactive selector mutation, and active Mapping selector projection mismatch.
  Existing dedicated groups omit null restore metadata from semantic hashing, so
  bootstrap identity, v2 migration, rollback, and representation parity remain stable.

## Evidence And Verification

- Focused lifecycle/source/runtime/UI/bootstrap coverage passes with `63 passed`.
  It proves inactive IDU metadata preservation across Save/reload, Add→Detach clean
  baseline equality, activation dependency blockers, dependency-free
  activation→disable exact restore, stale prepared rejection, and dedicated-selector
  detach protection.
- Mapping parity coverage uses selector column `idu` with source binding `ref_type`:
  dropdown options come from `ref_type`, exclude IDU values, accept `R32`, and the
  encoder emits `R32=1.0`. Existing Static, External, and ordinary dropdown paths pass.
- External coverage proves unknown, duplicate, incomplete, unavailable, and stale
  provider relations reject without replacing the original draft; a valid overlay
  succeeds.
- Persisted Mapping source tests retain byte-identical `mapping.json` across command
  and inactive Save. Repository publication/rollback, Derived-One-hot dependencies,
  Predict row input, Train header/preprocessing, and Phase 4B–4E regressions pass in
  the full repository suite: `2385 passed, 2 xfailed`.

## Changed Files

- existing contract v3 One-hot DTO/codec/fingerprint/relation validation owners
- existing One-hot group/category command, policy, impact, and vocabulary owners
- existing Data Definition prepared command/controller/projection/View owners
- existing Predict dropdown adapter and focused lifecycle/source/runtime tests
- active work-plan, project-log, memory, and result-record discovery owners

## Known Risks

- Phase 4H remains the process-wide live generation cutover owner.
- No production External provider is registered; immutable fake snapshots verify the
  bounded provider relation contract without adding discovery infrastructure.
- Windows native UI smoke was not run and remains a pre-release verification item;
  automated macOS/offscreen coverage is not equivalent evidence.
