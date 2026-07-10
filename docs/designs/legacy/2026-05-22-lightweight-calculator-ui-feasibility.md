# Design Gate — Lightweight Calculator UI Feasibility

> **Scope note.** This is a **feasibility spike**, not a redesign or
> replacement of the PyQt calculator UI. The existing PyQt calculator
> stack (`app_calculator.py`, `ui/calc_window.py`,
> `ui/calculators_2point.py`, `ui/spreadsheet_table.py`,
> `ui/theme.py`, `ui/calculator_errors.py`) stays in place as the
> reference implementation. This doc decides whether a Tkinter-based
> calculator-only deployment is small enough and adequate enough to
> ship as a separate distribution target.
>
> This doc does **not** redefine calculator core, profile dispatcher,
> region config, unit adapter, ML, table UX contract, the
> Calculator UI module boundary
> (`docs/designs/2026-05-22-calculator-ui-module-boundary.md`), or
> the action-model decision
> (`docs/designs/2026-05-22-calculator-action-model-alignment.md`).
> The PyQt calculator UI advancement workstream (Slice ζ → η → β →
> γ → δ + Hong Kong HSPF UI surface) is **held** pending the result of
> this spike; if the Tkinter direction does not pan out, the PyQt
> workstream resumes from Slice ζ.

## Background

`app_calculator.py` is a thin legacy Qt binding entrypoint over
`ui/calc_window.py` (~834 LOC of `CalculatorWindow` shell + AHRI / EN
tabs + helper plumbing). It already shares core calculator logic
through:

- `core/calculators/profiles.py` — profile manifest
  (`hong_kong_cspf`, `hong_kong_hspf`, `iso_t1_default_2point_cspf`,
  `ks_c9306_*`, `en14825_*`, `ahri_usa_seer2`, `ahri_usa_hspf2`,
  `saso_t3_cspf`, …).
- `core.calculators.dispatcher.create_calculator_for_profile()` —
  thin profile → calculator-instance dispatch.
- `core.calculators.standards.iso16358.ISO16358Calculator` — common engine for
  ISO 16358-1 CSPF and ISO 16358-2 HSPF (Hong Kong CSPF / HSPF share
  the same `data/region_configs/hong_kong.json`).
- `core/calculators/adapters/unit_adapter.py` — ML-W ↔ AHRI Btu/h boundary.

Calculator core (`core/calculators/standards/*.py`) is pure Python with no
`numpy` / `pandas` (AGENTS rule). Heavy weight in the deployed
`app_calculator.exe` is the **GUI shell**, not the engine.

A PyInstaller build of `app_calculator.py` carries legacy Qt binding + Qt
runtime + Qt plugins. Hands-on estimates for similar legacy Qt binding console
apps land in the **~100–150 MB** range for either one-folder dist or
one-file exe (this is an order-of-magnitude estimate, not a measured
value — see `docs/guides/lightweight_calculator_packaging_check.md`
for the measurement plan). For a general-user calculator-only
distribution, this size is plausibly higher than necessary.

Tkinter ships with CPython (Tcl/Tk are part of the standard library
bundle on Windows / macOS / Linux Python installs). A PyInstaller
build of a Tkinter app pulls in `tcl86.dll` / `tk86.dll` and the Tcl
script library, but **does not** pull in Qt, Qt plugins,
`QtWebEngine`, or platform-style assets. Field reports for small
Tkinter calculator-shaped apps frequently land below the legacy Qt binding
baseline by a noticeable margin, but the actual delta depends on
included DLLs and must be measured locally before any decision is
locked in.

## Problem statement

Decide whether a **calculator-only** deployment target can be shipped
on a lightweight Tkinter UI shell while:

1. Reusing the existing pure-Python calculator core and
   profile / dispatcher / region-config / unit-adapter assets
   unchanged.
2. Producing a PyInstaller bundle that is measurably smaller than the
   legacy Qt binding `app_calculator` bundle on the same host.
3. Preserving the user-visible calculation semantics (numbers, keys,
   region selection) of the PyQt calculator UI for the profile(s) the
   MVP supports.
4. Not blocking the PyQt calculator UI workstream — if the Tkinter
   direction does not produce a meaningful size delta or hits a
   usability cliff, the PyQt UI workstream resumes from Slice ζ
   without rework.

## Non-goals

- Replacing `ui/calc_window.py` or `app_calculator.py`.
- Porting the entire PyQt calculator UI to Tkinter.
- Re-implementing `SpreadsheetTableModel` / `SpreadsheetTableView`
  semantics (TSV copy/paste, undo, paste-route normalization) inside
  Tkinter. The MVP intentionally uses simpler Entry/grid input.
- Touching calculator core, profile dispatcher, region config,
  result envelope, ML adapter, unit adapter, or fixture / expected
  values.
- Setting up a parallel design system, theme tokens, or table UX
  contract for Tkinter. (If we proceed past the spike, a separate
  Tkinter UX contract / adapter doc gets a Design Gate of its own.)
- Locking in packaging optimization (UPX, exclude-modules, custom
  hooks). The spike measures the **default** PyInstaller bundle so
  we have an honest baseline.
- Replacing the action-model decision (Option A — auto-calc unified)
  or the calculator UI module boundary plan; those continue to govern
  the PyQt UI direction if it resumes.

## Candidate UI direction

Plain **Tkinter** (CPython stdlib). Optional `ttk` widgets for
slightly nicer default styling on Windows. No external GUI
dependency. No `numpy`, no `pandas`. No legacy Qt binding import anywhere in the
Tkinter shell.

Why Tkinter over alternatives, for an MVP only:

- **Tkinter**: stdlib, no extra wheel, no runtime install. PyInstaller
  pulls in Tcl/Tk DLLs but not Qt. Layout primitives (`pack` / `grid`)
  are sufficient for entry + label + button MVP.
- **CLI / argparse**: smallest possible binary, but loses the
  "general-user calculator" UX target this spike is meant to test.
  Kept as a fallback if Tkinter packaging does not shrink enough.
- **HTML / local web (Flask + browser)**: avoids the GUI question
  entirely but introduces a server process + browser dependency,
  which is a different deployment shape than "double-click and use".
  Kept as a second fallback.
- **PySide / PyQt-lite**: still pulls Qt; doesn't address the
  motivating size concern.

The first three rows above are the **possible** outcomes of this
spike — Tkinter is the *primary* candidate, CLI / HTML are
*fallbacks* if Tkinter does not produce a meaningful size delta.

## Information architecture — standard tab + region selection

User-facing structure is intentionally minimal. The user **does
not** see `profile_id`, `calculator_id`, or `config_path`. The UI
resolves the calculator profile internally from (standard tab, region
selection, metric section).

- Top-level: **standard tabs**. MVP candidates listed in
  *MVP scope* below.
- Inside a standard tab: a **region selector**
  (`ttk.Combobox` / radios). The selector shows only regions that the
  tab's standard supports.
- Region selection drives which **metric sections** are visible in
  the same screen. Examples:
  - ISO 16358 / **Hong Kong** → CSPF section + HSPF section visible
    together.
  - EN 14825 → SEER section + SCOP section together.
  - AHRI 210/240 → SEER2 section + HSPF2 section together.
- Internal resolution maps `(region, metric_section)` →
  `profile_id` for `create_calculator_for_profile(profile_id=...)`:
  - Hong Kong + CSPF → `hong_kong_cspf`
  - Hong Kong + HSPF → `hong_kong_hspf`
  - EN + SEER → `en14825_seer`
  - EN + SCOP → `en14825_scop`
  - AHRI + SEER2 → `ahri_usa_seer2`
  - AHRI + HSPF2 → `ahri_usa_hspf2`

Rejected alternatives (kept here so future readers don't relitigate):

- **Per-region tabs** (one tab per `region`): rejected. Tab count
  grows with `region` list (`hong_kong`, `india`, `saudi_arabia`,
  `usa`, `eu`, `korea`, `generic_t1`, …) and the user usually thinks
  *standard first, region second*.
- **Nested tabs** (outer standard, inner region): rejected. The
  nested tab pattern is hard to read in Tkinter and increases click
  depth.
- **KS C 9306 merged into the ISO 16358 tab as a "Korea" option**:
  rejected. `core/calculators/standards/ks_c9306.py` is a separate calculator
  (not the ISO common engine); silently merging would blur the
  calculator boundary. KS C 9306 stays in its **own tab** if/when
  added.

The MVP only implements the first standard tab (see
*MVP scope*); other tabs are listed in this section for future
slices, not built in the spike.

## MVP scope

Deliberately small. Anything not listed here is out of scope for
the spike.

- Runnable Tkinter app (`python3 -m app_calculator_tk`).
- No legacy Qt binding import anywhere in the Tkinter shell.
- Single standard tab in the MVP: **ISO 16358**.
- Region selector inside the ISO 16358 tab. MVP wires only one
  region: **Hong Kong**.
- Hong Kong region screen shows **both** CSPF and HSPF metric
  sections in the same view (matches the IA above).
- Input form: small `Entry`/grid for the minimum points each metric
  needs. CSPF takes 35_full / 35_half capacity + power
  (the same `measure` points `data/region_configs/hong_kong.json`
  declares). HSPF takes the H1 / H2 / H3 points the existing PyQt
  AHRI/EN tabs already mirror.
- Calculate button per section (no auto-recompute in MVP — that's an
  optional follow-up only if the spike survives the decision
  criteria).
- Result rendered as text (read-only `tk.Text` widget) showing
  CSPF / HSPF and a small set of intermediate values from the
  calculator result dict.
- Copy-result affordance: either a "Copy result" button that copies
  the text widget contents to the clipboard via `clipboard_clear` /
  `clipboard_append`, **or** the text widget's native selection +
  Ctrl+C path. TSV copy/paste of input cells is intentionally **not**
  in MVP.

What MVP intentionally does **not** include:

- AHRI tab. AHRI / HSPF2 v3 input shape and unit conversion stay in
  the PyQt UI until the spike is decided.
- EN 14825 tab. SCOP multi-climate selection stays in the PyQt UI
  until the spike is decided.
- KS C 9306 tab.
- Hong Kong HSPF heating-point auxiliary form polish — MVP uses the
  same raw `temp / capacity / power` entries the core calculator
  already accepts (`_heating_points`).
- ML / inverse-search integration.
- TSV copy/paste of input cells; undo/redo; invalid-cell tinting.
- Theme tokens / design-system parity with `ui/theme.py`. (Spike
  uses Tk defaults.)

## Profiles to test

- **Primary**: `hong_kong_cspf` (region `hong_kong`, metric `CSPF`,
  mode `cooling`, `calculator_id=iso16358`,
  config `data/region_configs/hong_kong.json`).
- **Primary, second metric section in the same Hong Kong screen**:
  `hong_kong_hspf` (region `hong_kong`, metric `HSPF`, mode
  `heating`, `calculator_id=iso16358`, same config). Hong Kong CSPF +
  HSPF share one region config, so this exercises the IA decision
  inside one screen.

Both profiles are already enabled in
`core/calculators/profiles.py` and are reachable via
`create_calculator_for_profile(profile_id=...)`.

Out of scope for the spike's profile list:
- `iso_t1_default_2point_cspf` — listed as a possible *future*
  region under the same ISO 16358 tab (not wired in MVP).
- `en14825_*` — defer until ISO tab is decided.
- `ahri_usa_seer2` / `ahri_usa_hspf2` — defer until ISO tab is
  decided.
- `ks_c9306_*` — separate tab if/when added.

## Packaging measurement plan

Detailed commands live in
`docs/guides/lightweight_calculator_packaging_check.md`. Summary of
what gets measured:

- PyInstaller one-folder dist size for `app_calculator.py` (legacy Qt binding
  baseline) on Windows (target deployment platform).
- PyInstaller one-folder dist size for `app_calculator_tk.py`
  (Tkinter MVP) on the same Windows host with the same Python
  interpreter version.
- One-file `.exe` sizes for both, with the same measurement protocol.
- Windows `calculator_tk` packaged size was measured at approximately
  11 MB and is acceptable for the current deployment candidate. Keep PyQt
  baseline comparison as a later retirement-gate input if needed.

## Reuse boundaries

What the Tkinter MVP **reuses unchanged**:

- `core/calculators/profiles.py` — profile manifest and
  `resolve_calculator_profile()`.
- `core.calculators.dispatcher.create_calculator_for_profile()`.
- `core.calculators.standards.iso16358.ISO16358Calculator` (CSPF + HSPF paths).
- `data/region_configs/hong_kong.json`.
- `core/calculators/adapters/unit_adapter.py` (not wired in MVP, but available
  if a future slice needs it).
- All calculator fixtures, expected values, and xfail constants.

What the Tkinter MVP **does not touch**:

- `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`,
  `ui/spreadsheet_table.py`, `ui/calculator_errors.py`, `ui/theme.py`.
- `tests/test_app_calculator_ui_smoke.py`.
- Any calculator core file.
- Any region config file.

What the Tkinter MVP **adds (in its own directory)**:

- `app_calculator_tk.py` entrypoint.
- `ui_tk/` package: `ui_tk/__init__.py`, `ui_tk/calculator_app.py`,
  and (only if the spike survives the decision criteria) future
  per-tab / per-metric modules.

The `ui_tk/` path keeps Tkinter code physically separated from
`ui/` PyQt code so there's no risk of cross-import or accidental
shared base class.

## Decision criteria

Trigger to **continue Tkinter direction** (all must hold):

1. Measured Tkinter one-folder dist on Windows is **at least 40 %
   smaller** than the legacy Qt binding baseline on the same host with the same
   Python build (i.e. ≥ 40 MB absolute reduction if the PyQt baseline
   lands near 100 MB).
2. Hong Kong CSPF + HSPF calculation results from the Tkinter MVP
   match the PyQt calculator UI numerically for the same input
   points.
3. No required calculator-core change to make Tkinter work (i.e. the
   spike confirms core reuse without modification).

Trigger to **pause and re-evaluate** (any one is enough):

1. Tkinter packaging shrinks by < 20 % on the same host. (Tk DLLs
   and Tcl script library may be heavier than expected.)
2. MVP requires duplicating non-trivial input parsing /
   normalization logic that already lives inside `ui/` PyQt helpers
   — i.e. the Tkinter port pulls in too much logic that should stay
   shared.
3. Decision criterion (1) holds but Tkinter MVP UX is materially
   worse than CLI for the same set of inputs.

Trigger to **fall back** (any one is enough):

1. Tkinter packaging does not shrink meaningfully on the target
   platform.
2. Tcl/Tk runtime adds a hard dependency on a system Tk install on
   the target machine (i.e. PyInstaller's bundled Tcl/Tk does not
   load on a clean Windows host).

Fallback options, in order:
- CLI / `argparse` entrypoint over the same dispatcher.
- Local HTML / browser-driven UI (Flask + browser).
- Stay on legacy Qt binding and resume the Calculator UI module boundary
  workstream from Slice ζ.

## Next implementation slice

After this design doc lands:

1. **Spike step 1** — add a minimal Tkinter prototype skeleton
   (`app_calculator_tk.py` + `ui_tk/calculator_app.py` +
   `ui_tk/__init__.py`) that runs and at least reaches the dispatcher
   call boundary for `hong_kong_cspf`. If input plumbing blocks the
   core call in the spike, record the blocker in the slice's report
   and stop there.
2. **Spike step 2** — Windows `calculator_tk` packaged size measured at
   approximately 11 MB and acceptable for the current deployment candidate.
3. **Decision point** — apply the *Decision criteria* section to the
   measured data. The decision lands in a follow-up report; this
   design doc is not edited to record the decision.
4. **If continue** — open a follow-up design slice for the Tkinter
   UX contract (Tk equivalents for keyboard nav and numeric input
   validation), then bring up CSPF + HSPF inputs to parity with the
   PyQt Hong Kong screen.
5. **If pause / fallback** — the PyQt calculator UI workstream
   resumes from Slice ζ (`ui/calculator_en_tab.py` extraction) as
   originally planned in the calculator UI module boundary design.

## Status

- Decision: **spike**. PyQt calculator UI advancement workstream
  (Slice ζ → η → β → γ → δ + Hong Kong HSPF UI surface) is held
  pending the result.
- MVP profile: `hong_kong_cspf` + `hong_kong_hspf` on a single ISO
  16358 tab.
- IA decision: standard tab + region selector + multi-metric sections
  in the same screen (not per-region tabs, not nested tabs, not KS C
  9306 merged into ISO).
- Packaging result: Windows `calculator_tk` packaged size measured at
  approximately 11 MB and acceptable for the current deployment candidate.
- **Note:** This doc defined the feasibility MVP, not the final UX. The MVP
  intentionally used `Entry` rows + calculate buttons to validate core reuse
  and packaging size. The final calculator-only UX contract (table/grid input
  + auto-calc) now lives in
  `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`.
