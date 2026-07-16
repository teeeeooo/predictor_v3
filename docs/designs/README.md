# Design Records

## Role

`docs/designs/` keeps only current governing, actively referenced, or future
unabsorbed design decisions. Design records are evidence, not active rule
owners; repeated rules belong in their architecture, workflow, UI, standard,
or current-state owner.

## Read Rule

Do not read every record. Start from the matching current owner, then select one
design by keyword only when prior decision context is necessary. Historical
design discovery starts at `docs/designs/legacy/README.md`.

## Active Records

| Record | Current role | Read when |
| --- | --- | --- |
| `2026-07-14-train-admin-ui-ux-overhaul-document-set.md` | Navigation index for the Train/Admin overhaul governing design, four implementation phases, and deferred Predict boundary. | Locating the correct Train/Admin phase design before implementation. |
| `2026-07-14-train-admin-ui-ux-overhaul-governing-design.md` | Governing product direction, owner boundaries, fixture/mock policy, mapping exchange contract, and delivery model for the Train/Admin overhaul. | Planning or reviewing any Train/Admin overhaul phase. |
| `2026-07-14-train-admin-phase-1-mapping-data-foundation.md` | Phase 1 design; repository-automated implementation, final audit, and merge complete. | Historical or boundary review for Train/Admin Phase 1. |
| `2026-07-14-train-admin-phase-2-data-mapping-ux-overhaul.md` | Phase 2 design; implementation and merge complete, with deferred native evidence tracked separately. | Historical or boundary review for Data Mapping UX and exchange. |
| `2026-07-14-train-admin-phase-3-data-definition-ux-overhaul.md` | Phase 3 design; implementation, final audit, and PR #16 merge complete. | Historical or boundary review for Data Definition UX. |
| `2026-07-14-train-admin-phase-4-train-model-shell-ux-overhaul.md` | Phase 4 design for training-data selection, automatic internal validation, training/progress, result and Predict availability, and user-centered shell/Diagnostics separation. | Current-state audit and design finalization before Train/Model implementation. |
| `2026-07-14-future-predict-ui-ux-overhaul-boundary.md` | Deferred boundary and prerequisites for the later Predict UI/UX overhaul. | Planning Predict UX after Train/Admin Phase 4. |
| `2026-07-13-all-standards-core-refactor-design.md` | Implemented governing inventory, contract, and private-owner design for active non-AHRI Calculator standard cores. | Refactoring or reviewing EN 14825, ISO 16358, KS C 9306, Brazil, or remaining active Calculator core routes. |
| `2026-07-12-ahri-seer2-hspf2-core-refactor-design.md` | Implemented governing design for the stable AHRI facades and private variable/legacy engines. | Reviewing or extending AHRI SEER2/HSPF2 core ownership, including future multi-capacity sibling engines. |
| `2026-07-12-calculator-table-architecture-design.md` | Implemented governing design for the three active Calculator table families. | Reviewing or changing Calculator table-family architecture. |
| `2026-07-11-calculator-ui-ux-unification-slice-0.md` | Active Calculator surface audit, target table policy, and migration Slice design. | Reviewing or implementing Calculator UI/UX unification. |
| `TEMPLATE_DESIGN_GATE.md` | Template for a new Design Gate record. | Creating a new design record. |
| `2026-07-10-agent-harness-report-lifecycle-redesign.md` | Current harness report/memory lifecycle redesign evidence. | Reviewing the conditional-record or Memory Review redesign. |
| `2026-06-27-pyside6-train-predict-rewrite-design-gate.md` | Governing Train/Predict PySide6 rewrite design gate. | Planning or reviewing the active Train/Predict architecture. |
| `2026-05-17-calculator-result-envelope-ml-adapter.md` | Unabsorbed calculator-result/ML-adapter boundary decision. | Implementing the future adapter or result-envelope boundary. |
| `2026-07-06-arc15-unified-data-definition-manager-foundation.md` | Current Data Definition foundation and owner-switch decision. | Changing schema/feature-definition ownership or its projections. |

## Legacy Records

Forty-five absorbed, deferred-resume, superseded, or completed records are
indexed under `docs/designs/legacy/README.md`. Their bodies preserve historical
paths and wording; use the legacy index and current physical path for discovery.

## Update Triggers

Update this index when:

- a new active design record is created at the root;
- an active record is absorbed by an owner or moved to legacy;
- a legacy record is explicitly re-promoted;
- an active record changes its current role.

Ordinary implementation or wording changes do not update this index.
