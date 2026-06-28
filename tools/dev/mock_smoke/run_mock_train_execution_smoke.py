"""Run offscreen DEV-only Train execution smoke using a mock bundle."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from apps.train.controllers.train_controller import TrainController  # noqa: E402
from apps.train.services.training_service import TrainingService  # noqa: E402
from apps.train.state.training_run_state import TrainingRequest  # noqa: E402
from apps.train.ui.shell import TrainShell  # noqa: E402
from core.ml.artifacts import MODEL_FILE  # noqa: E402
from core.ml.inference import load_model  # noqa: E402
from tools.dev.mock_smoke.dev_training_backend import DevFastTrainingBackend  # noqa: E402
from tools.dev.mock_smoke.generators import (  # noqa: E402
    CASE_INPUT_NAME,
    cleanup_from_manifest,
    generate_mock_smoke_bundle,
    resolve_output_dir,
    update_mock_smoke_manifest,
)
from tools.dev.mock_smoke.run_mock_predict_smoke import _run_workspace  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Mock output directory. Defaults outside the repo.")
    parser.add_argument("--rows", type=int, default=12)
    parser.add_argument("--predict-delay-ms", type=int, default=0)
    parser.add_argument("--with-real-core-training", action="store_true")
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


def _run_train_ui_smoke(rows: int, predict_delay_ms: int) -> TrainShell:
    app = QApplication.instance() or QApplication([])
    shell = TrainShell()
    backend = DevFastTrainingBackend(rows=rows, predict_delay_ms=predict_delay_ms)
    controller = TrainController(service=TrainingService(backend=backend))
    panel = shell.train_model_panel
    panel.training_controller = controller
    panel._update_control_state()
    app.processEvents()
    if not panel.run_button.isEnabled():
        raise RuntimeError("Train run button is not enabled for mock training data.")

    panel.run_button.click()
    if not _wait_until(
        app,
        lambda: controller.last_result is not None
        and not controller.is_running
        and controller._thread is None,
    ):
        raise RuntimeError("Train execution smoke did not finish before timeout.")
    result = controller.last_result
    if result is None or result.status != "complete":
        raise RuntimeError(f"Train execution smoke failed: {result}")
    log_text = panel.log.toPlainText()
    if "DEV fast training" not in log_text:
        raise RuntimeError("Train log did not include DEV fast backend output.")
    if panel.progress_bar.value() != 100:
        raise RuntimeError("Train progress did not reach terminal complete state.")
    summary_model = panel.summary_table.model()
    if summary_model.data(summary_model.index(0, 2)) != "완료":
        raise RuntimeError("Train summary did not show complete state.")
    if not Path(MODEL_FILE).exists():
        raise RuntimeError("Train execution did not create model/model.pkl.")
    load_model(MODEL_FILE)
    return shell


def _run_optional_real_core_training(data_path: Path) -> None:
    print("optional real core training smoke: running; metrics are meaningless")
    service = TrainingService()
    result = service.train(
        TrainingRequest(
            run_id="real-core-training-smoke",
            data_path=str(data_path),
            model_output_path=MODEL_FILE,
        )
    )
    if result.status != "complete":
        raise RuntimeError(f"real core training smoke failed: {result.message}")


def main() -> int:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir)
    if Path(MODEL_FILE).exists() and not args.force:
        raise FileExistsError(
            f"{MODEL_FILE} already exists. Use --force only for DEV smoke replacement."
        )
    paths = generate_mock_smoke_bundle(
        output_dir,
        rows=args.rows,
        predict_delay_ms=args.predict_delay_ms,
        write_manifest=True,
        install_mapping=True,
        install_train_data=True,
        force=args.force,
    )
    if args.with_real_core_training:
        _run_optional_real_core_training(paths["training_data"])
    else:
        print("optional real core training smoke: skipped")

    _run_train_ui_smoke(args.rows, args.predict_delay_ms)
    update_mock_smoke_manifest(
        output_dir,
        "prediction_artifact",
        paths["prediction_artifact"],
        rows=max(args.rows, 5),
        predict_delay_ms=args.predict_delay_ms,
        purpose="train execution produced local model smoke",
        installed_path=MODEL_FILE,
    )
    case_tsv = (output_dir / CASE_INPUT_NAME).read_text(encoding="utf-8")
    workspace = _run_workspace(args.rows, case_tsv, cancel=False)
    app = QApplication.instance() or QApplication([])
    _wait_until(app, lambda: workspace.prediction_controller._thread is None, timeout_ms=1000)
    print(f"train execution smoke complete model: {MODEL_FILE}")
    print(f"predict after train rows: {workspace.session.summary_counts()['completed']}")
    if args.cleanup:
        removed = cleanup_from_manifest(
            paths["manifest"],
            remove_local_model=True,
            remove_local_mapping=True,
            remove_local_train_data=True,
        )
        for path in removed:
            print(f"removed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
