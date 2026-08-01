record:
  date: 2026-08-01
  topic: predict-typed-result-canonical-acceptance-repair
  tags: predict, typed-result, canonical-acceptance, progress, cancellation, infrastructure, correction
  memory_review: no-change
  memory_reason: Active Predict architecture and Work Plan owners plus this correction record are sufficient while PR #44 remains an unmerged Draft.
change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Fresh exact-head audit of PR #44 reproduced three acceptance defects: an
incomplete/unavailable `complete` payload could attach, a rejected row could
still advance transport-derived progress and summary counts, and cancellation
or infrastructure failure could bypass immutable execution provenance.

# Contract / Behavior Corrected

`PredictSession` now pins the result adapter's immutable runtime target
descriptors with each allowed execution and validates exact Target identity,
Feature identity, result key, unit, value source, target status, and aggregate
row status before canonical attachment. Malformed payloads preserve canonical
state and append one bounded diagnostic. Executed results cannot enter through
the legacy direct setter.

Cancellation and row-wide infrastructure errors retain the original execution
context and pass the same session, case, run, input-revision, semantics, model,
and payload gate before run authority is revoked. The Predict controller counts
and reports each accepted terminal disposition once; worker progress/counts are
transport evidence only. A terminal transport event still disposes the runner,
while `unresolved` exposes requested rows without an accepted disposition.

# Evidence And Verification

- Narrow canonical acceptance, typed context, usecase, adapter/worker contract,
  and deterministic controller repair suite: 58 passed.
- Related Predict result adapter, application, execution, session, lifecycle,
  generation, schema compatibility, and shared composition suite: 163 passed.
- Final changed-source compilation, repository structure, diff hygiene, and
  staged change gates are recorded in the Worker handoff.

# Compatibility And Scope

The current five-target `W`/`Hz`/`kg` catalog, raw precision, exact-target model
rule, reload and generation freshness/migration, public generated Predict
schema, and persisted Feature Definition shape are unchanged. No production
model, generation, mapping, or user data is mutated.

Result Review, EER/COP, `사양 요약`, Layout B, bulk paste, copy/export redesign,
partial-target Active models, Target unit authoring, and cross-launch history
remain excluded. PR #44 remains Draft and Slice 2 is not recorded as merged or
closed.
