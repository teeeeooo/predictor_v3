# 01. Toolkit Selection Policy

## Role and scope

- This document is the **toolkit choice policy** shared by every
  desktop project in this organization.
- It tells the agent and the reviewer which UI toolkit to use for a
  given screen and when a toolkit change must go through a design
  gate.
- It does **not** describe visual design (see
  `02_DESIGN_TOKENS_AND_LAYOUT.md`) or table behavior (see
  `03_SPREADSHEET_TABLE_UX_CONTRACT.md`).

## 1. Default policy

- **New** desktop UI with editable, table-heavy screens uses
  **PyQt5** as the default toolkit.
- **Existing** Tkinter apps stay on Tkinter and follow
  `adapters/TKINTER_TABLE_ADAPTER.md` for table-shaped surfaces.
- Within a single application, do **not** mix Tkinter and PyQt5
  widgets. Pick one toolkit per app.
- Switching an existing app from one toolkit to another is an
  architectural change that requires its own design gate and
  migration plan (§4). It is not a routine UI polish task.

## 2. Choose PyQt5 when

PyQt5 is the right default if **any** of the following apply to the
new app or new screen:

- The screen is dominated by an editable, spreadsheet-like table
  (multi-row, multi-column, with copy / paste / undo / navigation).
- Cells need per-column behavior: dropdown editors, validators,
  read-only states, custom paint (error border, invalid background).
- The app needs Ctrl+C / Ctrl+V TSV interop with Excel or Google
  Sheets out of the box.
- Validation coloring, error highlighting, or rich cell rendering is
  central to the UX.
- The app benefits from a model / view / delegate separation (large
  data, sortable / filterable, multiple views of the same data).
- The app is starting fresh and there is no installed Tkinter user
  base to disrupt.

When the answer is yes to any of these, use PyQt5 and follow
`adapters/PYQT_TABLE_IMPLEMENTATION.md` for table-shaped surfaces.

## 3. Keep or choose Tkinter when

Tkinter remains acceptable if **all** of the following apply:

- The project already ships in Tkinter and has a user base.
- The change is maintenance, polish, or feature work that fits inside
  the existing Tkinter shell.
- The table surfaces in the app can satisfy the
  `03_SPREADSHEET_TABLE_UX_CONTRACT.md` baseline through the Tkinter
  adapter.
- There is no strong product reason (Excel-like UX, rich validation,
  complex delegates) to introduce a second toolkit.

In this case follow `adapters/TKINTER_TABLE_ADAPTER.md` for any
table-shaped surface.

## 4. Toolkit-change design gate

Switching an existing app from Tkinter to PyQt5 (or vice versa) is
**not** an ordinary UI task. Before any code is moved, the change
requires:

- A short design note that states:
  - Why the current toolkit is no longer sufficient.
  - The scope of the migration (which screens, which order).
  - The plan for keeping the app shippable during the migration.
  - The rollback path if the migration stalls.
- Explicit user approval of that design note.
- A migration plan that does not require running Tkinter and PyQt5
  side-by-side inside the same process.

Polish, theming, or wanting "a more modern look" is **not** a
sufficient reason to switch toolkits. The trigger must be a real
constraint (table UX limits, validation needs, paint requirements)
that the current toolkit cannot meet through its adapter.

## 5. Forbidden patterns

- "All projects must use PyQt5." This document does **not** say
  that. Existing Tkinter apps are not forced to migrate.
- "Tkinter is banned." This document does **not** say that. Tkinter
  remains the supported toolkit for existing Tkinter apps under the
  adapter.
- Mixing Tkinter and PyQt5 widgets in the same process to "try out"
  the other toolkit. Pick one.
- Using PyQt5 just because the developer prefers it, when the
  existing Tkinter app already satisfies the user requirements.
- Migrating an app's toolkit as a side effect of a feature or bug-fix
  task. The migration must be the explicit task.

## 6. Related documents

- `00_UI_UX_SYSTEM.md` — common UX principles.
- `02_DESIGN_TOKENS_AND_LAYOUT.md` — visual tokens and layout.
- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` — common table UX.
- `adapters/PYQT_TABLE_IMPLEMENTATION.md` — PyQt5 table rules.
- `adapters/TKINTER_TABLE_ADAPTER.md` — Tkinter table adapter rules.
