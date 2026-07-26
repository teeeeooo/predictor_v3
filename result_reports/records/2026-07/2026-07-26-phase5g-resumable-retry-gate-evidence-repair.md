record:
  date: 2026-07-26
  topic: phase5g-resumable-retry-gate-evidence-repair
  tags: train-admin, phase-5g, audit-repair, retry-scope, pre-start-failure, hard-gate
  memory_review: updated
  memory_reason: The first Phase 5G audit failure and its durable retry-scope and fail-closed evidence rules are required for exact-head re-audit and future lifecycle work.
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

# Change Reason

The first independent Phase 5G audit failed because a pre-start failure removed
the pending proposal and allowed proposal identity to reset attempt allowance,
while configured guardrail or instability requirements could pass without
resolved evidence. Historical validation run `30199916760` succeeded at that
failed-audit head but is not acceptance evidence.

# Contract / Behavior Changed

- Preserve accepted proposal identity, resolved before/delta/after evidence,
  policy acceptance, stable training-meaning execution key, attempt history,
  configured total attempts, remaining attempts, and diagnostics after a
  pre-start failure.
- Resume `failed_resumable` from the persisted proposal and next attempt number
  without resubmission. Duplicate ID/metadata cannot reset allowance, and a
  different proposal cannot silently replace a pending execution.
- Distinguish configured gate evidence as `not_configured`, `passed`,
  `violated`, or `unresolved`. Configured unresolved guardrail or instability
  evidence records dedicated blockers and excludes the Candidate from
  production incumbent and recommendation while preserving history and
  exploratory evidence.
- Keep Phase 5F Core-start accounting, writer lock, Candidate/Active lifecycle,
  operator-only iteration extension, production authority boundaries, and
  Phase 5H exclusion unchanged.

# Evidence And Verification

Focused owner and representative lifecycle regression passed 92 tests covering
restart/resume at attempt 2, exhausted duplicate and replacement rejection,
configured missing/resolved/violated/unconfigured gate evidence, deterministic
incumbent/recommendation exclusion, Phase 5F retry and writer lock, headless
projection, Candidate/Active management, immutable deployment export, and
Predict reload preservation. The repair remains pending independent exact-head
re-audit; this record does not declare audit PASS.

# Changed Files

Existing Phase 5G campaign lifecycle, proposal persistence, hard-gate,
leaderboard, recommendation, focused tests, and their workflow/current-state
owners.

# Known Risks

- The stable execution key is application-owned deterministic identity, not an
  authorization token or external agent API.
- Production data/model quality, Phase 5H snapshot/final confirmation,
  migration, retention, deletion, and proposal abandonment/override remain
  outside this repair.
- PR #34 must remain open, Draft, unmerged, and independently re-audited at the
  new exact head.
