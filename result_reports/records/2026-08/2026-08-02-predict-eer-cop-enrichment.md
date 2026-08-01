record:
  date: 2026-08-02
  topic: predict-eer-cop-enrichment
  tags: predict, eer, cop, enrichment, execution-input, typed-result
  memory_review: no-change
  memory_reason: Active design, architecture, Work Plan, and this indexed Draft record provide sufficient recall until independent audit and merge closeout.
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

Predict needed one Qt-free application contract for execution-specific EER/COP.
Reading capacity from the current mutable case after prediction could combine a
new numerator with an old accepted power outcome, while treating EER/COP as ML
Targets or copying Calculator formulas would create a second semantic owner.

# Contract / Behavior Changed

The validated prediction request now captures cooling and heating capacity
evidence by the approved stable Feature identities. The immutable execution
context pins the current generation key/ML name, Predict-owned W interpretation,
and raw numeric input actually sent for that execution. The result adapter derives
EER and COP independently from those pinned numerators and the accepted raw W
cooling/heating power `TargetOutcome` denominators.

Each derived metric carries its source identities, W/W semantics, exact raw
precision, and either a finite numeric value or a bounded deterministic
unavailable reason. Missing, non-numeric, non-finite, non-positive, failed, or
metadata-incompatible evidence never becomes NaN, Infinity, zero, or a placeholder
number. Metric availability does not alter the Target-owned aggregate result
status.

Canonical result validation recomputes the attachment from the pinned request and
typed outcomes, rejecting caller-fabricated or mismatched evidence. Same-case
edits, model reload, generation migration, and rollback retain the accepted metric
and source evidence while applying the existing current/stale lifecycle; they do
not consult the current case. Direct non-executed state cannot install metric
evidence.

# Evidence And Verification

Focused regressions cover exact EER/COP precision, independent partial success,
all bounded unavailable classes, identity/unit/source mismatch, non-finite
protection, aggregate-status isolation, edit and row isolation, reload,
presentation-only versus semantic migration, rollback, stable-identity rename
compatibility, forged execution input, fabricated attachment, and direct setter
rejection. The related Predict execution/session, model lifecycle, generation
migration/rollback, standalone/embedded composition, and schema compatibility
suite is the Build evidence for the Draft PR; a fresh independent exact-head
Auditor remains required.

# Changed Files

The change adds one Predict application enrichment module and focused tests;
extends request/context/result canonical state and the existing input/result
adapters with immutable evidence; preserves metrics through migration/freshness
transforms; and completes the active architecture, approved design, Work Plan,
record index, and this correction record.

# Known Risks

The capacity W interpretation remains a closed Predict application contract for
the two approved stable identities because persisted Feature Definition does not
author units. Cross-process serialization of execution evidence is not added.
Display rounding, Result Review, `사양 요약`, Layout B, partial-target Active
models, Target/unit authoring, CSPF/HSPF2, Predict-to-Calculate orchestration,
bulk/export, training, packaging, and deployment remain excluded. Slice 3 is not
merged or closed and Slice 4 is not started.
