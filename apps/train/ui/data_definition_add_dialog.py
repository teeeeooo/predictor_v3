"""Constrained Add intent dialog for Data Definition."""

from __future__ import annotations

from collections.abc import Callable

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
    AddDefinitionIntent,
    MAPPING_LOOKUP_TEMPLATES,
    mapping_template,
)

AddApplyCallback = Callable[[AddDefinitionIntent], tuple[bool, str]]


class DataDefinitionAddDialog(QDialog):
    """Collect only fields owned by one supported Add intent."""

    def __init__(
        self,
        on_apply: AddApplyCallback,
        *,
        standalone_mapping_attribute: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_apply = on_apply
        self._standalone = standalone_mapping_attribute
        self.setWindowTitle(
            "Add Mapping Attribute" if standalone_mapping_attribute else "Add Definition"
        )
        self.setAccessibleName(self.windowTitle())
        self.setModal(True)
        self._build()
        self._update_intent_fields()

    def intent(self) -> AddDefinitionIntent:
        """Return current constrained form values as application intent."""
        kind = (
            "mapping_attribute"
            if self._standalone
            else str(self.intent_combo.currentData())
        )
        template = mapping_template(str(self.mapping_combo.currentData()))
        mapping = kind != "manual_predict" and template is not None
        return AddDefinitionIntent(
            kind=kind,  # type: ignore[arg-type]
            label=self.label_input.text(),
            column_key=self.key_input.text(),
            data_type=str(self.data_type_combo.currentData()),
            visible=self.visible_checkbox.isChecked(),
            required=self.required_checkbox.isChecked(),
            mapping_entity=template.mapping_entity if mapping else "",
            mapping_attribute=self.attribute_input.text() if mapping else "",
            trigger_column=template.trigger_column if mapping else "",
            rule_id=template.rule_id if mapping else "",
            notes=self.notes_input.text(),
        )

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.outer")] * 4))
        layout.setSpacing(style.spacing("space.sm"))
        heading = QLabel(self.windowTitle())
        heading.setObjectName("PanelTitle")
        heading.setFont(style.qfont("font.window_title"))
        layout.addWidget(heading)

        self.form = QFormLayout()
        self.form.setSpacing(style.spacing("space.sm"))
        self.intent_combo = QComboBox()
        self.intent_combo.setAccessibleName("Definition intent")
        self.intent_combo.addItem("Manual Predict Input", "manual_predict")
        self.intent_combo.addItem("Mapping-backed Predict Column", "mapping_predict")
        self.intent_combo.currentIndexChanged.connect(self._update_intent_fields)
        if not self._standalone:
            self.form.addRow("Intent", self.intent_combo)

        self.label_input = QLineEdit()
        self.label_input.setAccessibleName("Definition label")
        self.key_input = QLineEdit()
        self.key_input.setAccessibleName("Definition internal key")
        self.key_input.setPlaceholderText("snake_case_key")
        self.data_type_combo = QComboBox()
        self.data_type_combo.setAccessibleName("Definition data type")
        self.data_type_combo.addItem("Number", "number")
        self.data_type_combo.addItem("String", "string")
        self.visible_checkbox = QCheckBox("Visible in Predict")
        self.visible_checkbox.setAccessibleName("Predict visible")
        self.visible_checkbox.setChecked(not self._standalone)
        self.required_checkbox = QCheckBox("Required")
        self.required_checkbox.setAccessibleName("Definition required")
        self.form.addRow("Label", self.label_input)
        self.form.addRow("Internal key", self.key_input)
        self.form.addRow("Data type", self.data_type_combo)
        self.visible_label = QLabel("Visibility")
        self.form.addRow(self.visible_label, self.visible_checkbox)
        self.form.addRow("Requirement", self.required_checkbox)

        self.mapping_combo = QComboBox()
        self.mapping_combo.setAccessibleName("Mapping group and lookup template")
        for template in MAPPING_LOOKUP_TEMPLATES:
            self.mapping_combo.addItem(template.label, template.key)
        self.mapping_combo.currentIndexChanged.connect(self._update_relation_summary)
        self.attribute_input = QLineEdit()
        self.attribute_input.setAccessibleName("Mapping attribute")
        self.relation_label = QLabel()
        self.relation_label.setWordWrap(True)
        self.relation_label.setAccessibleName("Mapping trigger and rule")
        self.mapping_group_label = QLabel("Mapping group")
        self.mapping_attribute_label = QLabel("Mapping attribute")
        self.relation_form_label = QLabel("Trigger / rule")
        self.form.addRow(self.mapping_group_label, self.mapping_combo)
        self.form.addRow(self.mapping_attribute_label, self.attribute_input)
        self.form.addRow(self.relation_form_label, self.relation_label)
        self.notes_input = QLineEdit()
        self.notes_input.setAccessibleName("Definition notes")
        self.form.addRow("Notes", self.notes_input)
        layout.addLayout(self.form)

        self.error_label = QLabel()
        self.error_label.setAccessibleName("Add Definition validation feedback")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)
        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.setAccessibleName(f"Cancel {self.windowTitle()}")
        cancel.clicked.connect(self.reject)
        self.apply_button = QPushButton("Apply to Draft")
        self.apply_button.setAccessibleName(f"Apply {self.windowTitle()} to Draft")
        self.apply_button.setDefault(True)
        self.apply_button.clicked.connect(self._apply)
        actions.addWidget(cancel)
        actions.addWidget(self.apply_button)
        layout.addLayout(actions)

    def _update_intent_fields(self) -> None:
        mapping = self._standalone or self.intent_combo.currentData() == "mapping_predict"
        for widget in (
            self.mapping_group_label,
            self.mapping_combo,
            self.mapping_attribute_label,
            self.attribute_input,
            self.relation_form_label,
            self.relation_label,
        ):
            widget.setVisible(mapping)
        self.visible_label.setVisible(not self._standalone)
        self.visible_checkbox.setVisible(not self._standalone)
        self._update_relation_summary()

    def _update_relation_summary(self) -> None:
        template = mapping_template(str(self.mapping_combo.currentData()))
        if template is None:
            self.relation_label.setText("Unsupported template")
            return
        rule = template.rule_id or "simple lookup"
        self.relation_label.setText(f"Trigger: {template.trigger_column}  |  Rule: {rule}")

    def _apply(self) -> None:
        accepted, message = self._on_apply(self.intent())
        self.error_label.setText("" if accepted else message)
        if accepted:
            self.accept()
