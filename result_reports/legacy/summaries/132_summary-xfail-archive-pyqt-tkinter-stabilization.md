# 132 — Summary: Xfail Cleanup + PyQt/Tkinter Environment Stabilization

## Summary Scope

Active reports 124–131. Workstream: ISO pure-route obsolete xfail retirement, legacy diagnostic xfail owner/reason cleanup, AS/NZS case3 external-reference compatibility decision, archived ISO16358 reverse-engineering status header, PyQt macOS fatal-abort audit + known-bad environment skip patch, Tkinter ISO section pure helper cleanup, and PyQt test support matrix documentation.

This lifecycle maintenance creates one summary and archives the covered active reports. It does not create a new `result_reports/active/132_*.md` report.

## Covered Reports

- `124_iso-pure-route-obsolete-xfail-retirement.md`
- `125_legacy-diagnostic-xfail-reason-owner-cleanup.md`
- `126_asnzs-case3-external-reference-compatibility-decision.md`
- `127_archive-iso16358-reverse-engineering-status-header.md`
- `128_pyqt-macos-fatal-abort-environment-audit.md`
- `129_pyqt-known-bad-environment-skip-patch.md`
- `130_tkinter-iso-section-pure-helper-cleanup.md`
- `131_pyqt-test-support-matrix-doc.md`

## Key Decisions

- ISO pure-route Formula 45/49/47/50 xfail 4개는 obsolete experiment로 판정되어 `tests/test_iso16358_hspf_pure_iso_track_a.py`에서 제거되었다. 남은 보호는 fixture identity, workbook-reference guard, cycling, Formula 44/48 min-half, saturated auxiliary smoke이다 (124).
- `tests/_legacy` 17개 xfail은 marker/count를 유지하면서 reason/owner를 legacy workbook-oracle diagnostic/reference로 재명시했다. 삭제 대상이 아니며 현재 production ISO16358-2 HSPF official-exact path와 분리된 historical 비교용이다 (125).
- AS/NZS case3 2개 xfail은 production calculator failure가 아니라 full component row 데이터 미확보로 인한 external reference prerequisite으로 결정되어 Z-phase AS/NZS Excel compatibility 작업까지 deferred로 유지된다 (126).
- `docs/archive/iso16358_initial_reverse_engineering/`는 historical initial reverse-engineering snapshot / non-runtime archive임을 README 상단 status header로 명시했다. 파일 삭제·이동·rename은 없다 (127).
- macOS 15.7.3 arm64 + Python 3.14.4 + PyQt5 5.15.11/Qt 5.15.14 환경에서 일부 `QTableView` subclass 생성 경로가 native SIGABRT로 abort되는 원인이 audit되었다 (128).
- 위 known-bad 환경에서만 4개 PyQt widget test 파일을 사전 skip하는 가드를 `tests/helpers/pyqt_env.py` + `tests/test_pyqt_environment_guard.py`로 도입했다. Windows / Linux / Python 3.12·3.11 / 향후 검증된 host에서는 계속 실행 가능하다 (129).
- Tkinter ISO CSPF/HSPF section의 input dict 구성과 result text formatting은 `ui_tk/sections/iso16358_helpers.py`로 추출되었고 pure tests (`tests/test_ui_tk_iso16358_helpers.py`)로 보호된다. Hong Kong CSPF 4.939 / HSPF 3.643 smoke 유지 (130).
- `docs/guides/pyqt_test_support_matrix.md`로 PyQt widget test 보존 이유, macOS Python 3.14 known-bad skip 정책, Python 3.12/3.11 및 Windows validation pending 상태가 문서화됐다. 이 문서는 "중간 안정화 문서"로 유지된다 (131).

## Completed Work

- ISO pure-route Formula 45/49/47/50 obsolete xfail 4개 제거 완료.
- full suite xfail count가 23 → 19로 정리됨.
- `tests/_legacy` 17개 xfail은 legacy workbook-oracle diagnostic/reference로 owner/reason 정리됨 (count/marker 동일).
- AS/NZS case3 2개 xfail은 external reference prerequisite으로 명문화하고 Z-phase deferred 결정.
- `docs/archive/iso16358_initial_reverse_engineering/README.md`에 historical snapshot / non-runtime archive status header 추가.
- PyQt macOS Python 3.14 fatal-abort 원인/환경 audit 완료.
- known-bad macOS Python 3.14 + PyQt5 환경에서 PyQt widget tests 사전 skip patch 완료.
- manual PyQt ignore 없이 full suite 실행 가능 — 130 이후 baseline은 **585 passed, 59 skipped, 19 xfailed**.
- Tkinter ISO section input dict / result formatting이 pure helper로 분리됨.
- PyQt support matrix doc (`docs/guides/pyqt_test_support_matrix.md`) 추가됨.

## Remaining Work

- Python 3.12/3.11 venv 또는 Windows host에서 PyQt smoke 재검증은 미수행.
- Windows host 확보 시 PyInstaller size 측정 (Slice T6) 미수행.
- Tkinter next metric/standard extension design 미착수.
- ML / inverse-search 복귀 준비 미착수.
- PyQt calculator-only UI 자산은 reference 상태로 유지되며 retirement audit이 아직 수행되지 않았다.

## Xfail Status

- Pure ISO HSPF route: pure-route Formula 45/49/47/50 xfail 4개 제거 후 의도적으로 xfail 없음 (fixture identity / workbook reference guard / cycling / Formula 44·48 min-half / saturated auxiliary smoke만 보호로 유지).
- `tests/_legacy`: 17 xfail 유지. 모두 legacy workbook-oracle diagnostic/reference. marker/count/expected/fixture/core 변경 없음.
- AS/NZS case3: 2 xfail 유지. external workbook reference / full component row data prerequisite. Z-phase deferred.
- Full suite remaining xfail count: **19**.
- 124~131 어디에서도 xfail marker, expected, fixture, assertion, core code는 수정되지 않았다.

## PyQt / Tkinter Direction

- PyQt 전체를 삭제하지 않는다. PyQt Predict/Train 앱은 유지 후보로 둔다.
- PyQt calculator-only 경로 (예: `app_calculator.py` / `ui/calc_window.py` 계열 calculator UI 자산)는 retirement audit 후보로 본다. 이번 lifecycle 작업에서 삭제/수정/이동은 수행하지 않았다.
- Tkinter calculator-only direction은 118 clean foundation 위에서 130의 pure helper 분리로 한 단계 더 정돈되었다. Hong Kong CSPF/HSPF smoke 유지.
- `docs/guides/pyqt_test_support_matrix.md`는 현 시점 안정화 문서로 유지하되, PyQt calculator-only UI를 계속 고도화하는 방향은 더 이상 목표가 아니다.

## Active Documents Sync Judgment

- `docs/guides/pyqt_test_support_matrix.md`가 131에서 신규 생성되었고 owner inventory에 추가가 필요하여 `ACTIVE_DOCUMENTS.md`에 한 줄 entry로 반영했다.
- `docs/archive/iso16358_initial_reverse_engineering/README.md`는 archive 문서이므로 active owner inventory에는 추가하지 않는다.
- `tests/_legacy/README.md`는 test directory 내 owner 문서로 `ACTIVE_DOCUMENTS.md` Scope (`docs/**/*.md`, root Markdown)에서 제외되는 위치이므로 추가하지 않는다.
- 그 외 docs는 owner 관계 변경 없음.

## Project Log Sync Judgment

- `project_log.md` 마지막 entry는 2026-05-19이며 122 이후 결정 (obsolete ISO pure-route xfail 제거 / 남은 19개 xfail 성격 정리 / PyQt known-bad skip patch / PyQt calculator-only retirement audit이 다음 방향) 이 아직 기록되어 있지 않다.
- 위 결정들은 단순 docs 문구 수정이 아니므로 `project_log.md`에 짧게 새 entry를 append한다 (report 전문 복사 없이 결정/방향만).

## Archive Candidates

위 Covered Reports 8개 (124~131) 를 본 lifecycle 단계에서 `result_reports/archive/`로 이동한다. 파일명/번호는 그대로 유지한다.

## Active Reports After Maintenance

- `result_reports/active/`는 본 lifecycle 이후 비어 있을 예정이다 (active 폴더에 남길 report 없음).

## Next Suggested Actions

1. PyQt calculator-only retirement audit (PyQt calculator UI 자산 / `app_calculator.py` / `ui/calc_window.py` 계열 read-only inventory + 의존성/사용처 분리). 이번 lifecycle에서는 실행하지 않는다.
2. Windows host 확보 시 PyInstaller size measurement (Slice T6).
3. 필요 시 Python 3.12/3.11 venv PyQt support validation.
4. 필요 시 Tkinter next metric/standard extension design.
5. ML / inverse-search 복귀 준비.

## Verification

- Lifecycle maintenance: docs/report-only. source code / test marker / expected / fixture / core / profile / dispatcher / PyQt UI / Tkinter UI 코드는 본 작업에서 수정하지 않았다.
- 최소 검증:
  - `python3 -B tools/check_code_structure.py`
  - `python3 -B -m pytest tests/test_code_structure_guard.py -q`
  - (가능 시) `python3 -B -m pytest tests/test_pyqt_environment_guard.py tests/test_ui_tk_iso16358_helpers.py -q`
- 본 작업은 새 active report를 생성하지 않으며 summary + archive 이동 + ACTIVE_DOCUMENTS/project_log/WORK_PLAN 최소 갱신만 수행했다.
