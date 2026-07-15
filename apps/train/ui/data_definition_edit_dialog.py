"""Controlled metadata Edit dialog for Data Definition."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from core.data_definition import (
    EditDefinitionIntent,
    MAPPING_LOOKUP_TEMPLATES,
    mapping_template,
    mapping_template_for_relation,
)
from core.data_definition.command_contract import (
    controlled_data_type_options,
    controlled_editor_options,
    controlled_value_source_options,
)

EditApplyCallback = Callable[[EditDefinitionIntent], tuple[bool, str]]


class DataDefinitionEditDialog(QDialog):
    """Edit schema metadata without exposing identity, order, or role."""

    def __init__(
        self,
        identity: tuple[str, str],
        values: dict[str, str],
        on_apply: EditApplyCallback,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._identity = identity
        self._initial = dict(values)
        self._role = self._initial.get("role", "")
        self._has_mapping_metadata = any(
            self._initial.get(field_name, "")
            for field_name in (
                "mapping_entity",
                "mapping_attribute",
                "trigger_column",
                "rule_id",
            )
        )
        self._on_apply = on_apply
        self.setWindowTitle("Edit Definition")
        self.setAccessibleName("Edit Data Definition")
        self.setModal(True)
        self._build()
        self._prefill()
        self._update_contract_fields()

    def intent(self) -> EditDefinitionIntent:
        """Return every controlled form value as one atomic Edit command."""
        source = str(self.value_source_combo.currentData())
        template = mapping_template(str(self.mapping_combo.currentData()))
        updates: list[tuple[str, object]] = [
            ("label", self.label_input.text()),
            ("editor", self.editor_combo.currentData()),
            ("data_type", self.data_type_combo.currentData()),
            ("visible", self.visible_checkbox.isChecked()),
            ("required", self.required_checkbox.isChecked()),
            ("readonly", self.readonly_checkbox.isChecked()),
            ("value_source", source),
            ("model_input_enabled", self.model_input_checkbox.isChecked()),
            ("ml_name", self.ml_name_input.text()),
            ("one_hot_group", self.one_hot_input.text()),
            ("active", self.active_checkbox.isChecked()),
            ("notes", self.notes_input.text()),
        ]
        if source == "mapping_lookup" and template is not None:
            updates.extend((
                ("mapping_entity", template.mapping_entity),
                ("mapping_attribute", self.attribute_input.text()),
                ("trigger_column", template.trigger_column),
                ("rule_id", template.rule_id),
            ))
        elif self._initial.get("value_source") == "mapping_lookup":
            updates.extend((
                ("mapping_entity", ""),
                ("mapping_attribute", ""),
                ("trigger_column", ""),
                ("rule_id", ""),
            ))
        return EditDefinitionIntent(self._identity, tuple(updates))

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.outer")] * 4))
        layout.setSpacing(style.spacing("space.sm"))
        heading = QLabel("Edit Definition Metadata")
        heading.setObjectName("PanelTitle")
        heading.setFont(style.qfont("font.window_title"))
        layout.addWidget(heading)
        identity = QLabel(f"Internal key: {self._identity[1]}")
        identity.setAccessibleName("Read-only definition identity")
        layout.addWidget(identity)

        form = QFormLayout()
        form.setSpacing(style.spacing("space.sm"))
        self.label_input = QLineEdit()
        source = self._initial.get("value_source", "")
        editor = self._initial.get("editor", "")
        self.editor_combo = _combo(
            "Definition editor",
            controlled_editor_options(
                self._role,
                source,
                editor,
                self._has_mapping_metadata,
            ),
        )
        self.data_type_combo = _combo(
            "Definition data type",
            controlled_data_type_options(self._role, source, editor),
        )
        self.value_source_combo = _combo(
            "Definition value source",
            controlled_value_source_options(self._role, source),
        )
        self.value_source_combo.currentIndexChanged.connect(self._update_contract_fields)
        self.editor_combo.currentIndexChanged.connect(self._update_contract_fields)
        self.visible_checkbox = QCheckBox("Visible in Predict")
        self.required_checkbox = QCheckBox("Required")
        self.readonly_checkbox = QCheckBox("Read only")
        self.model_input_checkbox = QCheckBox("Model input enabled")
        self.active_checkbox = QCheckBox("Active")
        form.addRow("Label", self.label_input)
        form.addRow("Editor", self.editor_combo)
        form.addRow("Data type", self.data_type_combo)
        form.addRow("Value source", self.value_source_combo)
        form.addRow("Visibility", self.visible_checkbox)
        form.addRow("Requirement", self.required_checkbox)
        form.addRow("Editability", self.readonly_checkbox)

        self.mapping_combo = QComboBox()
        self.mapping_combo.setAccessibleName("Mapping group and lookup template")
        for template in MAPPING_LOOKUP_TEMPLATES:
            self.mapping_combo.addItem(template.label, template.key)
        self.attribute_input = QLineEdit()
        self.attribute_input.setAccessibleName("Mapping attribute")
        self.mapping_label = QLabel("Mapping group")
        self.attribute_label = QLabel("Mapping attribute")
        form.addRow(self.mapping_label, self.mapping_combo)
        form.addRow(self.attribute_label, self.attribute_input)
        self.ml_name_input = QLineEdit()
        self.one_hot_input = QLineEdit()
        self.notes_input = QLineEdit()
        form.addRow("Model input", self.model_input_checkbox)
        form.addRow("ML name", self.ml_name_input)
        form.addRow("One-hot group", self.one_hot_input)
        form.addRow("Lifecycle", self.active_checkbox)
        form.addRow("Notes", self.notes_input)
        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setAccessibleName("Edit Definition validation feedback")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)
        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.setAccessibleName("Cancel Edit Definition")
        cancel.clicked.connect(self.reject)
        apply_button = QPushButton("Apply to Draft")
        apply_button.setAccessibleName("Apply Edit Definition to Draft")
        apply_button.setDefault(True)
        apply_button.clicked.connect(self._apply)
        actions.addWidget(cancel)
        actions.addWidget(apply_button)
        layout.addLayout(actions)

    def _prefill(self) -> None:
        self.label_input.setText(self._initial.get("label", ""))
        _select(self.editor_combo, self._initial.get("editor", ""))
        _select(self.data_type_combo, self._initial.get("data_type", ""))
        _select(self.value_source_combo, self._initial.get("value_source", ""))
        for field, checkbox in (
            ("visible", self.visible_checkbox),
            ("required", self.required_checkbox),
            ("readonly", self.readonly_checkbox),
            ("model_input_enabled", self.model_input_checkbox),
            ("active", self.active_checkbox),
        ):
            checkbox.setChecked(self._initial.get(field, "false").casefold() == "true")
        relation = mapping_template_for_relation(
            self._initial.get("mapping_entity", ""),
            self._initial.get("trigger_column", ""),
            self._initial.get("rule_id", ""),
        )
        if relation is not None:
            _select(self.mapping_combo, relation.key)
        self.attribute_input.setText(self._initial.get("mapping_attribute", ""))
        self.ml_name_input.setText(self._initial.get("ml_name", ""))
        self.one_hot_input.setText(self._initial.get("one_hot_group", ""))
        self.notes_input.setText(self._initial.get("notes", ""))

    def _update_contract_fields(self) -> None:
        source = str(self.value_source_combo.currentData() or "")
        editor = str(self.editor_combo.currentData() or "")
        editor_options = controlled_editor_options(
            self._role,
            source,
            self._initial.get("editor", ""),
            self._has_mapping_metadata and source == self._initial.get("value_source"),
        )
        _replace_options(self.editor_combo, editor_options, editor)
        editor = str(self.editor_combo.currentData() or "")
        _replace_options(
            self.data_type_combo,
            controlled_data_type_options(self._role, source, editor),
            str(self.data_type_combo.currentData() or ""),
        )

        visible = source == "mapping_lookup"
        for widget in (
            self.mapping_label,
            self.mapping_combo,
            self.attribute_label,
            self.attribute_input,
        ):
            widget.setVisible(visible)

        input_role = self._role == "input"
        self.readonly_checkbox.setChecked(not input_role)
        self.readonly_checkbox.setEnabled(False)
        if self._role in {"helper", "one_hot_feature"}:
            self.visible_checkbox.setChecked(False)
            self.visible_checkbox.setEnabled(False)

        fixed_model_input = {
            "helper": False,
            "result": False,
            "status": False,
            "one_hot_feature": True,
        }
        if input_role and source in {"one_hot", "rule_options"}:
            fixed_model_input["input"] = source == "one_hot"
        if self._role in fixed_model_input:
            self.model_input_checkbox.setChecked(fixed_model_input[self._role])
            self.model_input_checkbox.setEnabled(False)
        else:
            self.model_input_checkbox.setEnabled(True)

        direct_ml_name = (
            self._role == "auto"
            or (input_role and source == "manual")
            or (self._role == "result" and source == "result")
            or self._role == "one_hot_feature"
        )
        self.ml_name_input.setEnabled(direct_ml_name)
        self.one_hot_input.setEnabled(
            self._role == "one_hot_feature" or (input_role and source == "one_hot")
        )

    def _apply(self) -> None:
        accepted, message = self._on_apply(self.intent())
        self.error_label.setText("" if accepted else message)
        if accepted:
            self.accept()


def _combo(accessible_name: str, values: tuple[str, ...]) -> QComboBox:
    combo = QComboBox()
    combo.setAccessibleName(accessible_name)
    for value in sorted(values):
        combo.addItem(value.replace("_", " ").title(), value)
    return combo


def _select(combo: QComboBox, value: str) -> None:
    index = combo.findData(value)
    if index >= 0:
        combo.setCurrentIndex(index)


def _replace_options(
    combo: QComboBox,
    values: tuple[str, ...],
    selected: str,
) -> None:
    with QSignalBlocker(combo):
        combo.clear()
        for value in values:
            combo.addItem(value.replace("_", " ").title(), value)
        index = combo.findData(selected)
        combo.setCurrentIndex(index if index >= 0 else 0)
