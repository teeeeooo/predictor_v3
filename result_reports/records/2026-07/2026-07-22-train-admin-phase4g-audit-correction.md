# Train/Admin Phase 4G Audit Correction

```yaml
record:
  date: 2026-07-22
  topic: train-admin-phase4g-audit-correction
  tags: train-admin, phase-4g, audit-correction, process-snapshot, policy-pool, model-group-identity, preview-evidence
  memory_review: updated
  memory_reason: Process-generation isolation and the single ordered policy-input pool are durable Phase 4 boundaries.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

## Change Reason

The original Phase 4G composition re-read the active repository generation through
the Train provider at each start, policy validation admitted owners outside the
runtime ML order, validated model groups did not pin their stable identities, and
Target impact evidence omitted Predict visibility.

## Contract / Behavior Changed

- TrainShell selects one active generation during process composition. Embedded
  Predict and the Train registry provider retain that immutable generation after a
  later Definition publication; each TrainingRequest serializes it again. A new
  shell reads the newly active generation. Phase 4H remains the only future owner of
  coordinated process snapshot replacement.
- One pure ordered training-input identity pool now owns policy eligibility, UI
  options, Impact Preview, contract validation, registry projection, preprocessing,
  and actual Train filtering. Eligible entries are active, uniquely projected,
  present in canonical ML order, non-Result, and either model-input-enabled supported
  Basic Features or validated Derived/One-hot owners. Invalid owners and empty final
  policy results fail before publication.
- The three validated model-group catalog entries pin stable identity together with
  registry key, display name, and use_rfe. Raw identity replacement and swaps fail
  even when Target references are changed in the same candidate.
- Target impact shape and the Preview UI show Predict visibility before/after.
  Visibility-only changes affect target presentation evidence but not registry/model
  compatibility, final inputs, or active Target membership.

## Evidence And Verification

- Process A → publish B isolation keeps embedded Predict, Train choices, and a new
  TrainingRequest on A; restarting the shell selects B.
- Existing three-group/five-Target registry membership, use_rfe, iteration order,
  policies, and exact final input columns retain golden parity.
- Correction-focused regression passes with `175 passed`; the final focused rerun
  passes with `45 passed`; full repository regression passes with
  `2400 passed, 2 xfailed`.
- Compile, diff check, structure gate, staged change gate, head equality, and GitHub
  CI are final closeout gates. Structure warnings remain non-blocking existing or
  accepted slice hotspots.
- Windows native UI smoke was not run and remains a pre-release verification item.

## Known Risks

- Phase 4H process-wide prepare/commit/abort coordination and live reload remain out
  of scope. This correction intentionally retains the current process generation.
- Production Mapping values, model artifacts, algorithms, training, promotion, and
  candidate lifecycle are unchanged.
