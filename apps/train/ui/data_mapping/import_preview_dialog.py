"""Compact modal preview for applying a mapping exchange candidate."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.services.data_mapping_types import DataMappingImportPreview
from apps.train.ui.data_mapping_models import ReadOnlyMappingTableModel


class DataMappingImportPreviewDialog(QDialog):
    """Show change counts and blockers before a full draft replacement."""

    def __init__(
        self,
        preview: DataMappingImportPreview,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._preview = preview
        self.setWindowTitle("Import Mapping Bundle Preview")
        self.setAccessibleName("Mapping Bundle Import Preview")
        self.setModal(True)
        self.setMinimumSize(760, 520)
        self._build_contents()

    def _build_contents(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))

        heading = QLabel("Import Mapping Bundle Preview")
        heading.setObjectName("PanelTitle")
        heading.setFont(style.qfont("font.window_title"))
        layout.addWidget(heading)

        source = QLabel(f"Source: {self._preview.source_path}")
        source.setAccessibleName("Mapping Bundle source")
        source.setWordWrap(True)
        format_text = self._preview.format_version or "Not detected"
        version = QLabel(f"Format: {format_text}")
        version.setAccessibleName("Mapping Bundle format version")
        summary = QLabel(
            f"Affected groups: {self._preview.affected_group_count}  |  "
            "Apply changes to the Unsaved draft only; Save remains explicit."
        )
        summary.setAccessibleName("Mapping Bundle change summary")
        layout.addWidget(source)
        layout.addWidget(version)
        layout.addWidget(summary)

        table = QTableView(self)
        table.setAccessibleName("Mapping Bundle change counts")
        table.setModel(ReadOnlyMappingTableModel(
            ("Group", "Existing", "Added", "Removed", "Changed", "Unchanged"),
            tuple(
                (
                    diff.label,
                    str(diff.existing_rows),
                    str(diff.added_rows),
                    str(diff.removed_rows),
                    str(diff.changed_rows),
                    str(diff.unchanged_rows),
                )
                for diff in self._preview.group_diffs
            ),
        ))
        table.setMinimumHeight(150)
        table.verticalHeader().setVisible(False)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(table, 1)

        issue_frame = QFrame(self)
        issue_frame.setObjectName("Panel")
        issue_layout = QVBoxLayout(issue_frame)
        issue_layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        issue_layout.setSpacing(style.spacing("space.xs"))
        blocker_heading = QLabel("Blockers")
        blocker_heading.setFont(style.qfont("font.panel_title"))
        blocker_text = QLabel(_issue_text(self._preview.blockers))
        blocker_text.setAccessibleName("Mapping Bundle blockers")
        blocker_text.setWordWrap(True)
        warning_heading = QLabel("Warnings")
        warning_heading.setFont(style.qfont("font.panel_title"))
        warning_text = QLabel(_issue_text(self._preview.warnings))
        warning_text.setAccessibleName("Mapping Bundle warnings")
        warning_text.setWordWrap(True)
        issue_layout.addWidget(blocker_heading)
        issue_layout.addWidget(blocker_text)
        issue_layout.addWidget(warning_heading)
        issue_layout.addWidget(warning_text)
        layout.addWidget(issue_frame)

        note = QLabel(
            "Save destination: the existing runtime mapping source. "
            "The import file is not modified."
        )
        note.setAccessibleName("Mapping Bundle save destination notice")
        note.setWordWrap(True)
        layout.addWidget(note)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setAccessibleName("Cancel Mapping Bundle Import")
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button = QPushButton("Apply to Draft")
        self.apply_button.setAccessibleName("Apply Mapping Bundle to Draft")
        self.apply_button.setDefault(True)
        self.apply_button.setEnabled(self._preview.can_apply)
        if not self._preview.can_apply:
            self.apply_button.setToolTip("Resolve import blockers before applying.")
        self.apply_button.clicked.connect(self.accept)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.apply_button)
        layout.addLayout(actions)


def _issue_text(issues) -> str:  # noqa: ANN001
    if not issues:
        return "None"
    return "\n".join(
        f"• {_issue_location(issue)}: {issue.message}"
        for issue in issues
    )


def _issue_location(issue) -> str:  # noqa: ANN001
    parts = [part for part in (issue.entity_key, issue.attribute_key) if part]
    return " / ".join(parts) or "Import"
