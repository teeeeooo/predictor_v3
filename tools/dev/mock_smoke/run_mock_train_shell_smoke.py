"""Run offscreen DEV-only Train shell/status smoke using a mock bundle."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QAbstractButton, QLabel, QPushButton  # noqa: E402

from apps.predict.ui.workspace import PredictWorkspace  # noqa: E402
from apps.train.app import create_shell  # noqa: E402
from apps.train.ui.data_definition_panel import DataDefinitionPanel  # noqa: E402
from apps.train.ui.data_mapping_panel import DataMappingPanel  # noqa: E402
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
    definition_state = output_dir / "definition-state"
    lifecycle_state = output_dir / "lifecycle-state"
    shell = create_shell(
        generation_root=definition_state,
        lifecycle_root=lifecycle_state,
    )
    app.processEvents()
    tabs = [shell.tabs.tabText(index) for index in range(shell.tabs.count())]
    expected = ["Predict", "Train / Model", "Data Definition", "Data Mapping"]
    if tabs != expected:
        raise RuntimeError(f"unexpected Train tabs: {tabs}")
    if not isinstance(shell.tabs.widget(0), PredictWorkspace):
        raise RuntimeError("Predict tab is not an embedded PredictWorkspace")
    if shell.tabs.widget(0).title_label is not None:
        raise RuntimeError("embedded Predict workspace title is visible")
    if not isinstance(shell.tabs.widget(2), DataDefinitionPanel):
        raise RuntimeError("Data Definition tab is not the current manager surface")
    if not isinstance(shell.tabs.widget(3), DataMappingPanel):
        raise RuntimeError("Data Mapping tab is not the current manager surface")
    status_text = "\n".join(label.text() for label in shell.findChildren(QLabel))
    for expected_text in (
        "현재 사용 모델 있음",
        "학습 데이터: 확인됨",
        "데이터 매핑: 로드됨",
    ):
        if expected_text not in status_text:
            raise RuntimeError(f"Train status strip missing: {expected_text}")
    train_buttons = {
        button.text(): button
        for button in shell.tabs.widget(1).findChildren(QPushButton)
    }
    for text in ("학습 데이터 선택", "학습 실행"):
        if not train_buttons[text].isEnabled():
            raise RuntimeError(f"Train control is disabled: {text}")
    if train_buttons["중지"].isEnabled():
        raise RuntimeError("Train stop control should be disabled while idle")
    expected_train_controls = {
        "학습 데이터 선택",
        "학습 실행",
        "중지",
        "새로고침",
        "고급 정보 보기",
        "이 모델 사용",
    }
    if set(train_buttons) != expected_train_controls:
        raise RuntimeError(f"unexpected Train controls: {sorted(train_buttons)}")
    mapping_buttons = {
        button.text(): button
        for button in shell.tabs.widget(3).findChildren(QAbstractButton)
    }
    for text in ("Refresh", "Add", "Export", "Import", "Reload"):
        if not mapping_buttons[text].isEnabled():
            raise RuntimeError(f"Data Mapping control is disabled: {text}")
    print("train shell smoke: tabs/status/active controls OK")
    print("trainer execution: production adapter composed")
    shell.close()
    shell.deleteLater()
    app.processEvents()
    if args.cleanup:
        removed = cleanup_from_manifest(
            paths["manifest"],
            remove_local_model=True,
            remove_local_mapping=True,
            remove_local_train_data=True,
        )
        for path in removed:
            print(f"removed: {path}")
        shutil.rmtree(definition_state, ignore_errors=True)
        shutil.rmtree(lifecycle_state, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
