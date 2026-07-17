record:
  date: 2026-07-17
  topic: train-admin-unified-feature-manager-phase-design
  tags: train-admin, data-definition, feature-manager, phase-4, phase-5, ownership, planning
  memory_review: updated
  memory_reason: The active Train/Admin phase order and cross-tab owner/persistence direction changed and must remain discoverable across later implementation slices.

# Change Reason

The next Train/Admin work is broader Data Definition Feature management rather
than the previously numbered Phase 4 Train/Model UX work. The active design set
needed a new Phase 4 and a non-retroactive move of the unstarted Train/Model
design to Phase 5.

# Contract / Behavior Changed

- Phase 3 remains the completed and merged table-first Data Definition UX
  foundation; its original scope and PR #16 acceptance are unchanged.
- Phase 4 is the proposed/current Unified Feature Manager audit and design
  workstream. It targets Predict/ML Feature lifecycle and ordering, Derived and
  One-hot group authoring, Result/Target registry management, transaction-safe
  multi-contract persistence, and owner-preserving live reload.
- The prior Train/Model and Shell design is now deferred Phase 5 and consumes the
  stable dynamic Feature/Target contract produced by Phase 4.
- Data Mapping retains concrete `mapping.json` values, Train retains explicit
  training execution, and Predict consumes saved contracts and compatible model
  artifacts. Automatic retraining, automatic activation, and Predict internal
  redesign remain excluded.
- Current production persistence guards remain in force until Phase 4 audit and
  design approval establishes the compatibility migration/rollback owner.
- No runtime, public API, schema, config, data, or production behavior changed.

# Evidence And Verification

- The active governing design, design-set index, design README, WORK_PLAN,
  project brief, Arc 15 follow-up, Phase 3/3F follow-ups, Predict boundary, log,
  and memory were reviewed and synchronized against the five-phase structure.
- Repository-wide stale-path and phase-language searches distinguish preserved
  historical Phase 3/project-log wording from active navigation.
- Markdown path existence, docs-only scope, rename detection, and whitespace
  validation are performed before commit.

# Changed Files

- Train/Admin governing, phase, navigation, planning, milestone, history, and
  memory Markdown documents.
- No production source, configuration, data, fixture, or model artifact.

# Known Risks

- Phase 4A must still determine the exact canonical representation, transaction
  primitive, stable identities, reload adapters, protected dependencies, and
  independent ordering contracts before production implementation.
- The design intentionally does not promise that current import-time consumers
  or static registries can reload without bounded adapter/provider changes.
