# 157 — Tkinter Calculator Final UX Contract Alignment Audit

## Goal

Confirm that the current Tkinter MVP (`app_calculator_tk.py` / `ui_tk/`) is a
feasibility foundation, not the final calculator-only UX, and define the final
UX contract, implementation order, and PyQt retirement dependency without
modifying code, tests, or sources.

## Scope

- Read-only gap analysis between the current Tkinter MVP and the intended
calculator-only UX.
- Write the final UX contract design doc.
- Update `docs/WORK_PLAN.md` and the feasibility doc status note.
- Record the audit result.

## Non-goals

- No code modification, UI implementation, test change, source retirement, or
  packaging work.
- No `project_log.md`, `ACTIVE_DOCUMENTS.md`, `project_memory_seed.md`, or
  result-report lifecycle maintenance.

---

## Project Memory Recall Gate

Keyword-limited search of `result_reports/memory/project_memory_seed.md`
(grep) found the following relevant evidence:

- **calculator action model** (line 264–270): Calculator UI action alignment
  selected **auto-calc unified Option A**, with implementation ordered through
  recompute wiring, result/status surface unification, and error feedback
  alignment.
- **PyQt calculator-only packaging hold / Tkinter evaluation** (line 298–301):
  PyQt calculator-only packaging direction is on hold while a lightweight
  Tkinter calculator direction is evaluated.
- **PyQt and Tkinter calculator direction** (line 352–360): PyQt Predict/Train
  applications remain retention candidates, while PyQt calculator-only assets
  are candidates for retirement audit; the Tkinter calculator direction proceeds
  from the clean foundation and pure ISO helper split.

These entries were treated as **evidence only**. The current prompt constraints,
`AGENTS.md`, `AGENT_TASK_ROUTER.md`, and the source/design references governed
the audit. The memory seed was not modified.

---

## Task 1 — Current Tkinter MVP vs Final UX Gap

### Current MVP UX (confirmed from source)

- `app_calculator_tk.py`: thin entrypoint (16 LOC), no PyQt5 import.
- `ui_tk/sections/iso_cspf_section.py`: `NumericEntryRow` widgets
  (`Entry` + label) for declared capacity, 35_full capacity/power, 35_half
  capacity/power; a `ttk.Button("CSPF 계산")` triggers `_on_calculate()`.
- `ui_tk/sections/iso_hspf_section.py`: same pattern for rated heating
  capacity, 7_full capacity/power, 7_half capacity/power; `ttk.Button("HSPF
  계산")` triggers `_on_calculate()`.
- Result is emitted as plain text through a `result_callback` into a shared
  read-only text panel.
- **Manual calculation only**; no auto-recompute.

### Final UX target (from project direction)

- **Table/grid input** (rows = measure points, columns = numeric fields)
  matching the PyQt calculator's spreadsheet-like interaction.
- **Auto-calc** on every valid input change, debounced, with no calculate
  button.
- **Per-section result panel** that updates automatically.
- **Keyboard-first workflow** (Tab, Enter, arrow navigation inside the grid).
- **Numeric validation**, inline error/status, no stack traces to the user.
- **PyQt UX philosophy without PyQt runtime**: the user-visible behavior from
  the PyQt calculator is the reference, but the implementation uses Tkinter
  widgets and event patterns.

### Gap summary

| Dimension | MVP | Final UX |
|---|---|---|
| Input widget | Single `Entry` per field (`NumericEntryRow`) | Editable table/grid |
| Trigger | Explicit button per section | Auto-calc on `values_changed` |
| Result | Plain text callback | Per-section auto-updating panel |
| Keyboard nav | Tab between `Entry` widgets | Spreadsheet-like cell navigation |
| Copy/paste | Not supported | Candidate for later slice |
| Undo/redo | Not supported | Candidate for later slice |
| Table UX contract | Out of scope (feasibility doc §Non-goals) | Follows `03_SPREADSHEET_TABLE_UX_CONTRACT.md` via Tkinter adapter |

### Design/SSOT references confirming the gap

- `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md` §MVP scope
  explicitly states: *"Input form: small Entry/grid … Calculate button per
  section (no auto-recompute in MVP)"* and *"Re-implementing
  SpreadsheetTableModel … inside Tkinter. The MVP intentionally uses simpler
  Entry/grid input."*
- `docs/designs/2026-05-22-calculator-action-model-alignment.md` §Decision:
  **Option A — Auto-calc unified** was selected for the calculator UI. The MVP
  uses the opposite pattern (explicit button), confirming it is not the final
  UX.
- `docs/ui_ux/00_UI_UX_SYSTEM.md` §3: *"Reduce required clicks for the primary
  task."* The MVP requires a click per section; the final UX does not.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` §1: tables must behave like a
  small Excel sheet. The MVP does not use a table-shaped surface.

---

## Task 2 — Final UX Contract Document

Created: `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`

### Key decisions recorded in the contract

1. **Current `app_calculator_tk.py` / `ui_tk/` is a feasibility MVP foundation.**
   The Entry row + calculate button pattern is spike/MVP-only.
2. **Final UX is table/grid input + auto-calc.** This aligns with the PyQt
   action model Option A decision.
3. **PyQt calculator source retirement is on hold** until the Tkinter final UX
   vertical slice (slice 3) is verified.
4. **PyQt calculator remains the reference UX/source** until that gate is
   cleared.
5. **Tkinter inherits PyQt table UX philosophy and UI/UX SSOT principles**
   without importing PyQt5.
6. **Internal identifiers (`profile_id`, `config_path`, `calculator_id`) stay
   hidden** from the UI.
7. **Standard tab + region selector + metric sections in the same screen**
   remains the information architecture.

### Contract sections included

- Background
- Feasibility MVP vs Final UX
- Final UX Principles
- Information Architecture
- Table/Grid Input Contract (required vs deferred)
- Auto-calc Contract
- Result Surface Contract
- Non-goals
- Implementation Slices (7 ordered slices)
- Retirement Dependency
- Verification Strategy
- Status

---

## Task 3 — WORK_PLAN and Feasibility Doc Alignment

### Feasibility doc status note added

`docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md` §Status:

> **Note:** This doc defined the feasibility MVP, not the final UX. The MVP
> intentionally used Entry rows + calculate buttons to validate core reuse and
> packaging size. The final calculator-only UX contract now lives in
> `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`.

### WORK_PLAN updates

1. **4z — Calculator deployment UI feasibility pivot** updated:
   - Added 157 final UX contract reference.
   - Clarified that the current MVP is Entry row + button, and final UX is
     table/grid + auto-calc.
   - Replaced the old "next action" list with the 7 ordered implementation
     slices from the final UX contract.

2. **4s, 4r, 4q** each appended:
   - **"PyQt calculator-only source retirement는 Tkinter final UX vertical slice
     (slice 3) 검증 이후로 보류한다."**

No other sections of `WORK_PLAN.md` were modified.

---

## Task 4 — PyQt Retirement Hold Judgment

### Why retirement is deferred

- Reports 154~156 completed the audit, direct-test retirement, and shared
  utility retention decision. The next step in that sequence is **S3 — PyQt
  calculator-only source retirement**.
- The Tkinter direction has only a **feasibility MVP** today. Retiring the PyQt
  reference UX before the Tkinter equivalent is verified would leave the
  project without a confirmed production calculator-only UI.
- The final UX contract now gates S3: slice 3 (Hong Kong CSPF/HSPF table +
  auto-calc vertical slice) must be verified before PyQt source retirement is
  authorized.
- If slice 3 fails or slice 5 (Windows size measurement) shows insufficient
  benefit, the Tkinter direction falls back and the PyQt workstream resumes
  from the held slices (ε → ζ → η → β → γ → δ).

### Retirement dependency chain

```
Slice 1 (grid foundation)
   ↓
Slice 2 (auto-calc helper)
   ↓
Slice 3 (vertical slice verification)  ← GATE
   ↓
Slice 5 (size measurement)  ← GATE
   ↓
Resume 154~156 sequence:
   S1 (mixed test split)
   S3 (source retirement)
   S4 (docs update)
   S5 (support matrix narrowing)
```

---

## Task 5 — Verification

- `python3 -B tools/check_code_structure.py`:
  `code structure guard: OK (no findings)`.
- `python3 -B -m pytest -q -rxXs`:
  `566 passed, 32 skipped, 19 xfailed in 2.06s`.
- Baseline matches the expected post-155 baseline exactly.
- No source/test/marker changes were made, so no baseline delta is observed.

---

## Changed Files

- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md` — new final
  UX contract design doc.
- `docs/WORK_PLAN.md` — updated 4z with new slice order; appended hold
  sentence to 4s, 4r, 4q.
- `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md` — added
  status note linking to the final UX contract.
- `result_reports/active/157_tkinter-final-ux-contract-alignment-audit.md` —
  this report.

## Scope Compliance

- No code, UI, test, source, import, fixture, marker, xfail, expected value,
  core calculator, profile, dispatcher, or packaging change was made.
- No `project_log.md`, `ACTIVE_DOCUMENTS.md`, `project_memory_seed.md`,
  `README.md`, `project_brief.md`, or architecture doc was modified.
- No result-report lifecycle maintenance was performed.

## Project Memory Delta

```yaml
- type: decision
  topic: tkinter-calculator-final-ux
  content: "Tkinter calculator final UX is table/grid input with auto-calc; the current Entry/button MVP is a feasibility foundation, not the final calculator-only UX."
  keywords:
    - Tkinter
    - calculator-only
    - table input
    - auto-calc
    - final UX
  assertionStatus: observed
  source: result_reports/active/157_tkinter-final-ux-contract-alignment-audit.md
- type: decision
  topic: pyqt-calculator-retirement-gate
  content: "PyQt calculator-only source retirement is on hold until the Tkinter final UX vertical slice (slice 3) is verified. PyQt calculator remains the reference UX/source until that gate is cleared."
  keywords:
    - PyQt calculator
    - retirement
    - Tkinter
    - vertical slice
    - hold
  assertionStatus: observed
  source: result_reports/active/157_tkinter-final-ux-contract-alignment-audit.md
- type: decision
  topic: tkinter-ux-ssot-inheritance
  content: "Tkinter calculator inherits PyQt table UX philosophy and UI/UX SSOT principles (00_UI_UX_SYSTEM.md, 03_SPREADSHEET_TABLE_UX_CONTRACT.md) without importing PyQt5 runtime."
  keywords:
    - Tkinter
    - UI/UX SSOT
    - PyQt
    - table UX contract
    - adapter
  assertionStatus: observed
  source: result_reports/active/157_tkinter-final-ux-contract-alignment-audit.md
```

## Next Recommended Actions

Per the final UX contract implementation slices:

1. Tkinter table/grid input foundation (slice 1).
2. Tkinter auto-calc debounce/helper foundation (slice 2).
3. ISO Hong Kong CSPF/HSPF table + auto-calc vertical slice (slice 3).
4. macOS manual UX smoke (slice 4).
5. Windows PyInstaller size measurement (slice 5) — Windows host required.
6. PyQt calculator-only source retirement — resume 154~156 sequence after slice
   3 + slice 5 gates.
7. Tkinter standard/region expansion (slice 7).
