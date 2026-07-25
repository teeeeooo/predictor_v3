# Train/Admin UI/UX Overhaul — Design Document Set

Status: active design set; Phase 4–5C complete; Phase 5D first audit FAIL repaired and awaits exact-head re-audit
Date: 2026-07-26

## Purpose

This document set records the governing direction, accepted Phase 1–4 work,
the authoritative Phase 5 Train/Model lifecycle and experiment design, the
supporting Phase 5 Train/Model UI/UX direction, and the later Predict boundary.
The Phase 5B lifecycle foundation and Phase 5C Training Result & Analysis are
independently audited, merged, and complete. Phase 5D connects those persisted
contracts to the Train/Model Candidate/Active review and explicit promotion UI
on a dedicated Draft PR branch. The first independent L4 audit returned `FAIL`
at `c163da7027cdfdcc1bc8f831c17f6e1285b0d6db`; its five UI state/projection
blockers are repaired on the same branch, whose new exact head awaits
independent re-audit. Phase 5E and later scope has not started.

## Documents

1. `2026-07-14-train-admin-ui-ux-overhaul-governing-design.md`
2. `2026-07-14-train-admin-phase-1-mapping-data-foundation.md`
3. `2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md`
4. `2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md`
5. `2026-07-17-train-admin-phase-4-unified-feature-manager.md`
6. `2026-07-17-train-admin-phase-4a-current-state-contract-audit-closeout.md`
7. `2026-07-22-train-model-lifecycle-agent-assisted-experiment-design.md`
8. `2026-07-14-train-admin-phase-5-train-model-shell-ux-overhaul.md`
9. `2026-07-14-future-predict-ui-ux-overhaul-boundary.md`

## Intended Repository Location

Place these records under:

```text
docs/designs/
```

Register active records in `docs/designs/README.md`. Reflect only the current
phase and next action in `docs/WORK_PLAN.md`; Phase 1–3 entries retain their
historical design content while their completion state is maintained here and in
the current owner documents.

## Reading Order

For Phase 5B and later work, read the 2026-07-22 authoritative Phase 5 design
first. Use the 2026-07-14 Phase 5 document as supporting Train/Model and shell
UI/UX detail; it does not override lifecycle, CLI, campaign, agent-loop,
migration, or implementation-order decisions. Predict redesign remains later.
