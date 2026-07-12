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
- one of the six active records changes its current role.

Ordinary implementation or wording changes do not update this index.
