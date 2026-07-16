"""Shared label, validation, and focus conventions for Definition dialogs."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFormLayout, QLabel, QWidget


def add_labeled_row(form: QFormLayout, text: str, field: QWidget) -> QLabel:
    """Add one explicit accessible label/buddy relation to a form."""
    label = QLabel(text)
    label.setBuddy(field)
    form.addRow(label, field)
    if not field.accessibleName():
        field.setAccessibleName(text)
    return label


def configure_validation_summary(label: QLabel, accessible_name: str) -> None:
    """Make validation feedback readable and keyboard focusable on rejection."""
    label.setAccessibleName(accessible_name)
    label.setWordWrap(True)
    label.setFocusPolicy(Qt.StrongFocus)


def show_validation_summary(label: QLabel, message: str) -> None:
    """Keep a rejected form open and move focus to its authoritative feedback."""
    label.setText(message)
    label.setAccessibleDescription(message)
    label.setFocus(Qt.OtherFocusReason)


def schedule_initial_focus(field: QWidget) -> None:
    """Focus the first meaningful field after the modal is shown."""
    QTimer.singleShot(0, lambda: field.setFocus(Qt.OtherFocusReason))
