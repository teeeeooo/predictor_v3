"""Qt path selection and feedback for saved-generation Training Contract exports."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from apps.train.adapters.data_definition_training_contract_export import (
    publish_definition_reference,
    publish_training_header_template,
)
from apps.train.controllers.data_definition_controller import DataDefinitionController

logger = logging.getLogger(__name__)
CSV_FILTER = "CSV files (*.csv);;All files (*)"


def export_training_header_template(
    parent: QWidget,
    controller: DataDefinitionController,
) -> None:
    _export(parent, controller, export_kind="headers")


def export_definition_reference(
    parent: QWidget,
    controller: DataDefinitionController,
) -> None:
    _export(parent, controller, export_kind="reference")


def _export(
    parent: QWidget,
    controller: DataDefinitionController,
    *,
    export_kind: str,
) -> None:
    try:
        context = controller.training_contract_export_context()
    except RuntimeError as exc:
        QMessageBox.warning(parent, "Training Contract Export", str(exc))
        return

    document = context.document
    if context.draft_dirty:
        QMessageBox.information(
            parent,
            "Saved Training Contract",
            "This export uses the saved Train generation "
            f"'{document.generation_id}'. Unsaved Data Definition draft changes "
            "are excluded. Save and apply those changes first if Train must use them.",
        )

    title, default_name, publisher = _selection(export_kind, document.generation_id)
    destination, _selected_filter = QFileDialog.getSaveFileName(
        parent, title, default_name, CSV_FILTER,
    )
    if not destination:
        return
    try:
        path = publisher(destination, document)
    except OSError:
        logger.exception("Data Definition Training Contract export failed")
        QMessageBox.warning(
            parent,
            "Training Contract Export",
            "Export failed. Check the destination file location and permissions.",
        )
        return

    QMessageBox.information(
        parent,
        "Training Contract Export",
        f"Saved generation '{document.generation_id}' exported to {Path(path).name}.",
    )


def _selection(export_kind: str, generation_id: str):  # noqa: ANN202
    if export_kind == "headers":
        return (
            "Export Training Header Template",
            f"training_header_template_{generation_id}.csv",
            publish_training_header_template,
        )
    if export_kind == "reference":
        return (
            "Export Definition Reference",
            f"data_definition_reference_{generation_id}.csv",
            publish_definition_reference,
        )
    raise ValueError(f"unsupported Training Contract export kind: {export_kind}")
