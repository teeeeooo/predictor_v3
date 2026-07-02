"""Run offscreen DEV-only Train shell/status smoke using a mock bundle."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton  # noqa: E402

from apps.predict.ui.workspace import PredictWorkspace  # noqa: E402
from apps.train.ui.shell import TrainShell  # noqa: E402
from tools.dev.mock_smoke.generators import (  # noqa: E402
    cleanup_from_manifest,
    generate_mock_smoke_bundle,
    resolve_output_dir,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Mock output directory. Defaults outside the repo.")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir)
    paths = generate_mock_smoke_bundle(
        output_dir,
        write_manifest=True,
        install_model=True,
        install_mapping=True,
        install_train_data=True,
        force=args.force,
    )
    app = QApplication.instance() or QApplication([])
    shell = TrainShell()
    app.processEvents()
    tabs = [shell.tabs.tabText(index) for index in range(shell.tabs.count())]
    expected = ["Predict", "Train / Model", "Data Mapping", "Feature Catalog"]
    if tabs != expected:
        raise RuntimeError(f"unexpected Train tabs: {tabs}")
    if not isinstance(shell.tabs.widget(0), PredictWorkspace):
        raise RuntimeError("Predict tab is not an embedded PredictWorkspace")
    if shell.tabs.widget(0).title_label is not None:
        raise RuntimeError("embedded Predict workspace title is visible")
    status_text = "\n".join(label.text() for label in shell.findChildren(QLabel))
    for expected_text in ("model.pkl loaded", "학습 데이터: found", "mapping: loaded"):
        if expected_text not in status_text:
            raise RuntimeError(f"Train status strip missing: {expected_text}")
    train_buttons = {
        button.text(): button
        for button in shell.tabs.widget(1).findChildren(QPushButton)
    }
    for text in ("학습 데이터 선택", "학습 실행"):
        if not train_buttons[text].isEnabled():
            raise RuntimeError(f"Train control is disabled: {text}")
    for text in ("중지", "모델 열기", "로그 저장"):
        if train_buttons[text].isEnabled():
            raise RuntimeError(f"Train control should be disabled: {text}")
    for button in shell.tabs.widget(2).findChildren(QPushButton):
        if button.isEnabled():
            raise RuntimeError(f"deferred Data Mapping button is enabled: {button.text()}")
    print("train shell smoke: tabs/status/train controls/data mapping deferred OK")
    print("trainer execution: controller-ready")
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
