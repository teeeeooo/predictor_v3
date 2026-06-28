"""Run offscreen DEV-only Predict smoke using a mock bundle."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QItemSelectionModel, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from apps.predict.ui.workspace import PredictWorkspace  # noqa: E402
from core.predictor_schema.columns import INPUT_COLS  # noqa: E402
from tools.dev.mock_smoke.generators import (  # noqa: E402
    CASE_INPUT_NAME,
    MANIFEST_NAME,
    cleanup_from_manifest,
    generate_mock_smoke_bundle,
    resolve_output_dir,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Mock output directory. Defaults outside the repo.")
    parser.add_argument("--rows", type=int, default=12)
    parser.add_argument("--predict-delay-ms", type=int, default=0)
    parser.add_argument("--with-cancel", action="store_true")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def _wait_until(app: QApplication, predicate, timeout_ms: int = 8000) -> bool:  # noqa: ANN001
    done = {"value": False}

    def _poll() -> None:
        if predicate():
            done["value"] = True
            app.quit()
            return
        QTimer.singleShot(25, _poll)

    QTimer.singleShot(0, _poll)
    QTimer.singleShot(timeout_ms, app.quit)
    app.exec()
    return done["value"]


def _run_workspace(rows: int, case_tsv: str, *, cancel: bool) -> PredictWorkspace:
    app = QApplication.instance() or QApplication([])
    workspace = PredictWorkspace(initial_empty_rows=rows)
    model = workspace.case_model
    view = workspace.case_table
    view.selectionModel().setCurrentIndex(
        model.index(0, 0),
        QItemSelectionModel.ClearAndSelect,
    )
    changed = view.paste_tsv_at_selection(case_tsv)
    if changed < rows * len(INPUT_COLS):
        raise RuntimeError(f"paste changed too few cells: {changed}")
    workspace._refresh_after_row_change()
    first_case = workspace.session.case_store.get_case_at(0)
    for key in (
        "id_volume",
        "evap_area",
        "evap_volume",
        "od_volume",
        "cond_area",
        "cond_volume",
        "comp_eer",
        "comp_cc",
    ):
        if str(first_case.autofill_values.get(key, "")).strip() == "":
            raise RuntimeError(f"autofill did not populate {key}")

    workspace._run_prediction()
    if cancel:
        QTimer.singleShot(80, workspace._cancel_prediction)
    if not _wait_until(
        app,
        lambda: not workspace.prediction_controller.is_running
        and workspace.prediction_controller._thread is None,
    ):
        raise RuntimeError("prediction worker did not finish before timeout")

    counts = workspace.session.summary_counts()
    if cancel:
        if counts["cancelled"] < 1:
            raise RuntimeError(f"cancel smoke did not cancel rows: {counts}")
    elif counts["completed"] != rows:
        raise RuntimeError(f"prediction smoke did not complete all rows: {counts}")
    if counts["errors"] or counts["invalid"]:
        raise RuntimeError(f"prediction smoke produced errors: {counts}")

    view.selectRow(0)
    copied = view.copy_selection_tsv()
    if not copied:
        raise RuntimeError("copy selection smoke returned empty text")
    return workspace


def main() -> int:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir)
    paths = generate_mock_smoke_bundle(
        output_dir,
        rows=args.rows,
        predict_delay_ms=args.predict_delay_ms,
        write_manifest=True,
        install_model=True,
        install_mapping=True,
        force=args.force,
    )
    case_tsv = (output_dir / CASE_INPUT_NAME).read_text(encoding="utf-8")
    workspace = _run_workspace(args.rows, case_tsv, cancel=False)
    print(f"predict smoke complete rows: {workspace.session.summary_counts()['completed']}")
    if args.with_cancel:
        cancel_workspace = _run_workspace(args.rows, case_tsv, cancel=True)
        print(f"predict cancel rows: {cancel_workspace.session.summary_counts()['cancelled']}")
    if args.cleanup:
        removed = cleanup_from_manifest(
            paths["manifest"],
            remove_local_model=True,
            remove_local_mapping=True,
        )
        for path in removed:
            print(f"removed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
