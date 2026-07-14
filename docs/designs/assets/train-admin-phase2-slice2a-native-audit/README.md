# Train/Admin Phase 2 Slice 2A Native macOS Capture Manifest

- Verification commit SHA: `d206d2826c4b627ecc053194ea5d83b9317456f9`
- Platform: native macOS onscreen PySide6 (`QT_QPA_PLATFORM` was not set)
- Computer Use: yes
- Display wake: yes; `F15` was sent and an unlocked Finder desktop was confirmed before launch
- Production entry point checked: `python3 app_train.py`
- Screenshot harness entry point: temporary, untracked `/tmp/predictor_v3_slice2a_native_harness.py`
- Normal Computer Use capture size: 1154 × 768 pixels
- Missing-resource capture size: 2560 × 1640 pixels from the same visible native Qt window's `grab()`; the Computer Use screenshot stream produced black capture artifacts for that state
- Compact capture size: 900 × 632 pixels (900 × 600 Qt client request plus macOS frame)
- Data: synthetic repository fixture `tests/fixtures/mapping/mapping_runtime_equivalent.json` and copies under `/tmp/predictor_v3_slice2a_native/`

## Captures

| File | Evidence |
| --- | --- |
| `01-populated-idu.png` | Seven group rows, selected IDU, 9 rows, complete toolbar, primary table, status/source summary, and secondary details. |
| `02-populated-odu-cond-specs.png` | Selected ODU Cond Specs, 22 rows, conditional identity/payload columns, table scrolling, and primary-table dominance. |
| `03-dynamic-attribute.png` | Definition-backed `Cond Inner Area` header and synthetic value `12.5` without panel-specific column configuration. |
| `04-empty-group.png` | Existing synthetic provider with an empty IDU group, explicit empty copy, and available Add action. |
| `05-missing-resource.png` | Initial source missing with no cached draft, explicit recovery copy, and Refresh/Reload separation. |
| `06-load-error.png` | Existing malformed temporary JSON source, explicit load-error workspace, issue details, and no traceback in the primary workspace. |
| `07-dirty-draft-source-missing.png` | IDU value `99.5`, `Draft: Unsaved`, missing resource warning, preserved rows, and failed Reload feedback after the source was moved. |
| `08-compact-window.png` | Compact shell with all seven toolbar actions visible and navigation/table/details remaining bounded. |
| `09-details-collapsed.png` | Collapsed secondary details and increased primary-table height with the Show details control retained. |

## Table sizing correction evidence

- Sizing correction verification commit: the single Git commit containing this
  manifest update and captures `10`–`12`; its resolved SHA is recorded in PR
  #15 after push because a commit cannot embed its own SHA.
- Verification base: `6a3e22c0f17bc52f38d2ba8b08fb043ca4c7e132`.
- `10-balanced-idu-columns.png`: standard-window IDU; `IDU`, `ID Volume`, and
  `Size` use balanced bounded content widths, while `Group` stretches and
  `Rows` remains compact.
- `11-balanced-dynamic-columns.png`: standard-window ODU Cond Specs with the
  dynamic `Cond Inner Area` header and value `12.5`; every identity/payload
  column follows the same bounded policy and the final dynamic column does not
  stretch.
- `12-balanced-compact-columns.png`: compact 900 × 600 client request; all
  toolbar actions remain visible, `Rows` stays compact, primary columns remain
  bounded, and table-local scrolling remains available.
- Computer Use interaction was limited to confirming the unlocked desktop,
  reading the native ODU Cond Specs/dynamic table state, reading the compact
  native controls, and clicking the Data Mapping tab.
- The earlier populated/empty/missing/load-error/dirty/details evidence remains
  valid and was not rerun for this sizing-only correction.
- `tests/fixtures/mapping/mapping_runtime_equivalent.json` and
  `data/mapping.json` were not modified.

## Native interaction performed

- Launched the real Train/Admin entry point and clicked the Data Mapping top-level tab.
- Used the temporary native harness only to select deterministic synthetic states and avoid exposing a user path or production data in screenshots.
- Selected an IDU table cell onscreen and exercised the Qt edit keyboard path; the Computer Use accessibility bridge did not expose reliable delegate text replacement, so the screenshot's `99.5` edit was seeded through the same controller `edit_cell` boundary. The automated Qt regression covers the direct table-model edit path.
- Moved the temporary runtime source away, clicked Refresh, and confirmed the selected group, rows, `99.5`, and dirty state remained visible with Resource Missing.
- Clicked Reload, moved keyboard focus from No to Yes with Left, confirmed with Return, and verified failed Reload preserved the same draft.
- Restored the temporary source and verified a subsequent Reload returned the source value and cleared the failed-reload issue.
- Toggled secondary details and verified the collapsed compact layout.

## Restoration and limits

- `/tmp/predictor_v3_slice2a_native/runtime_mapping.json` was restored after the missing-source scenarios.
- `data/mapping.json` was neither created nor modified.
- `tests/fixtures/mapping/mapping_runtime_equivalent.json` was not modified.
- The screenshots contain only synthetic fixture data and temporary `/tmp` source labels.
- Native delegate text replacement through the Computer Use accessibility bridge was not counted as proven; controller-seeded dirty state plus native Refresh/Reload interaction and automated direct-edit regression are the bounded evidence used here.
- No Slice 2B/2C interaction, import/export bundle, or advanced spreadsheet behavior was exercised or implemented.
