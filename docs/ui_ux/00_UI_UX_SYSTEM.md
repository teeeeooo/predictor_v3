# 00. UI / UX System (Common SSOT)

## Role and scope

- This document is the **common UI/UX SSOT** shared by every desktop
  project in this organization (SPOT, predictor_v3, and any future
  desktop tool).
- It describes UI/UX principles that are **toolkit-agnostic**. PyQt5
  vs Tkinter implementation details do **not** belong here.
- For toolkit choice, see `01_TOOLKIT_SELECTION_POLICY.md`.
- For visual tokens and layout, see `02_DESIGN_TOKENS_AND_LAYOUT.md`.
- For `predictor_v3` project-wide visual philosophy and semantic visual
  roles, see `04_VISUAL_DESIGN_ARCHITECTURE.md`.
- For table-shaped UI behavior, see
  `03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- For shaping repeated inputs and user-facing results into matrix/summary
  surfaces in `predictor_v3`, see
  `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.
- For carrying this architecture into another project together with
  token/component ownership and a minimal guard, see
  `06_PORTABLE_UI_UX_ADOPTION_GUIDE.md`.
- For framework-specific table rules, see the documents under
  `adapters/`.

This document wins when it conflicts with any single project's local
UI notes. Project-specific deviations must be justified and documented
inside the project, not by editing this file.

## 1. Purpose

- Give every project a single, shared definition of what "good UX"
  means for our desktop apps.
- Let agents and reviewers apply the same standard everywhere.
- Reduce churn by separating principle (here) from implementation
  (adapters).

## 2. Core principles

- The user finishes the task; the UI does not get in the way.
- If something looks like a button, it must be clickable. If something
  is not clickable, it must not look like a button.
- Make frequent actions reachable from the main window. Hide rarely
  used controls in sub-dialogs.
- Any operation that can take longer than ~1 second must show
  progress and must show completion.
- Internal terminology (variable names, IDs, deltas) is for the code,
  not for the user.
- The smallest sufficient layout wins. Do not stretch a single input
  across the screen just to fill space.

## 3. User flow design

- Each window has a clear primary task. Secondary tasks live in
  sub-dialogs or collapsible sections.
- Reduce required clicks for the primary task; tolerate extra clicks
  for rare or destructive tasks.
- Confirmation prompts are reserved for destructive or expensive
  actions. Do not prompt for routine edits.
- A multi-step flow must show the user where they are (step label or
  numbered title) when more than two steps exist.
- Cancel must always be possible from a long-running operation; the
  app must not freeze without a way out.

## 4. Button and action rules

- Buttons must look clickable: filled background or outlined border,
  cursor changes on hover where supported.
- Primary actions are emphasized; secondary actions are de-emphasized;
  destructive actions are visually distinct.
- Non-interactive labels styled as colored chips, pills, or badges
  must **not** look like buttons. Pick a flatter shape or a different
  background.
- Disabled buttons must look disabled. Do not silently no-op a
  fully-styled active button.
- Button labels are verbs that describe the result, not the
  mechanism. Prefer "Run analysis" over "Submit form".

## 5. Dialog and sub-dialog rules

- The main window holds the frequent path. Settings, edge cases, and
  advanced options go into sub-dialogs.
- Sub-dialogs are modal when they gate the next step, modeless when
  they expose a side panel of options.
- Every dialog has a clear title, a clear primary action, and a
  visible way to dismiss.
- Dialogs are centered relative to their parent and do not open
  off-screen.
- Dialogs paint **before** any blocking work begins. A progress
  dialog that appears only after the work is half done is a bug.
- On failure, the progress dialog must close. Stale "please wait..."
  windows after an error are a contract violation.

## 6. Progress, completion, and error feedback

- Any operation expected to take longer than ~1 second shows a
  progress indicator (determinate when possible, indeterminate when
  not).
- The progress UI must be visible **before** the blocking work
  starts. Schedule the work on the event loop after the dialog has
  painted.
- On success, give explicit completion feedback: a final dialog,
  status banner, or unambiguous status text.
- On error, close the progress UI and show an error message in the
  user's language, not a raw stack trace. Stack traces go to a log,
  not to the user.
- Indeterminate progress for an operation longer than a few seconds
  must still produce intermediate status text ("Reading file 3 of
  12...") whenever possible.

## 7. Forms, inputs, and selectors

- Required fields are visually marked; optional fields are not
  cluttered with reminders.
- Numeric inputs accept the formats users actually type (commas,
  decimals, scientific notation where relevant) and normalize on
  commit.
- Drop-downs are used when the option set is closed; free-text is
  used when it is open. Do not abuse drop-downs as a substitute for
  text boxes.
- Validation messages appear near the field, not in a popup, unless
  the failure blocks the whole form.
- Field labels describe the data in user terms. Tooltips can provide
  extra detail but must not be the only place the meaning is shown.
- A single fixed input must not stretch full width just because it is
  alone in the row. See `02_DESIGN_TOKENS_AND_LAYOUT.md` for layout
  policy.

## 8. Numeric display policy

- Use a compact, consistent numeric formatter across the whole app.
- Integers display without a decimal point.
- Meaningful fractional digits are preserved; trailing zeros after the
  significant part are stripped.
- Very long decimals are truncated to a sensible width with the
  appropriate rounding; do not show 12 digits of float noise.
- Units belong on the header, label, or column header — not embedded
  in every cell value.
- Negative numbers use a leading minus, not parentheses, unless the
  domain explicitly requires accounting style.
- Percentages, ratios, and signed deltas use a consistent rule across
  every screen in the same project.

## 9. User-facing terminology policy

- Internal identifiers (`case_id`, `items`, `delta`, `dd_vals`,
  `outputs`) must not appear in the UI.
- Each project maintains a small glossary that maps internal names to
  user-facing labels; the UI uses the labels.
- Acronyms used in the UI must be expanded somewhere visible (label,
  tooltip, or help text) the first time the user encounters them.
- Localization keys stay separate from internal names; do not bind UI
  copy directly to schema field names.

## 10. Forbidden patterns

- Buttons that look like buttons but do nothing.
- Badges or chips styled to look identical to buttons but that are not
  clickable.
- Long-running work on the UI thread without a progress dialog.
- Progress dialogs that paint only after the work has already started.
- Progress dialogs that stay open after a failure.
- Stack traces shown directly to the end user.
- Internal variable names shown directly in labels, dialogs, or
  result tables.
- Full-width single inputs that exist only to fill space.
- Re-using a single component for both clickable and non-clickable
  variants without an obvious visual distinction.

## 11. Related documents

- `01_TOOLKIT_SELECTION_POLICY.md` — when to choose PyQt5 vs Tkinter.
- `02_DESIGN_TOKENS_AND_LAYOUT.md` — color, spacing, typography,
  layout rules.
- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` — common spreadsheet-like
  table behavior.
- `04_VISUAL_DESIGN_ARCHITECTURE.md` — `predictor_v3` project-wide
  visual philosophy and semantic color-role direction.
- `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` — `predictor_v3`
  project-wide repeated-input matrix and result-summary surface rules.
- `06_PORTABLE_UI_UX_ADOPTION_GUIDE.md` — portable adoption kit and
  visual-value ownership boundary.
- `adapters/PYQT_TABLE_IMPLEMENTATION.md` — PyQt5 implementation
  rules.
- `adapters/TKINTER_TABLE_ADAPTER.md` — Tkinter adapter rules for
  existing apps.
- `_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` — historical
  source from a prior PyQt project. Reference only; not the active
  contract.
