"""Constrained Add intent dialog for Data Definition."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

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
from apps.train.ui.data_definition.dialog_support import (
    add_labeled_row,
    configure_validation_summary,
    schedule_initial_focus,
    show_validation_summary,
)
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
        initial_intent: Literal["manual_predict", "mapping_predict"] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_apply = on_apply
        self._standalone = standalone_mapping_attribute
        self._initial_intent = initial_intent
        title = {
            "manual_predict": "Add Manual Predict Input",
            "mapping_predict": "Add Mapping-backed Predict Input",
        }.get(initial_intent or "")
        self.setWindowTitle(title or (
            "Add Mapping Attribute" if standalone_mapping_attribute else "Add Definition"
        ))
        self.setAccessibleName(self.windowTitle())
        self.setModal(True)
        self._build()
        if initial_intent is not None:
            self.intent_combo.setCurrentIndex(self.intent_combo.findData(initial_intent))
            self.intent_label.setVisible(False)
            self.intent_combo.setVisible(False)
        self._update_intent_fields()
        self.setMinimumWidth(520)
        schedule_initial_focus(
            self.label_input
            if self._standalone or self._initial_intent is not None
            else self.intent_combo
        )

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
        self.intent_label = add_labeled_row(self.form, "Intent", self.intent_combo)
        self.intent_label.setVisible(not self._standalone)
        self.intent_combo.setVisible(not self._standalone)

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
        add_labeled_row(self.form, "Label", self.label_input)
        add_labeled_row(self.form, "Internal key", self.key_input)
        add_labeled_row(self.form, "Data type", self.data_type_combo)
        self.visible_label = QLabel("Visibility")
        self.visible_label.setBuddy(self.visible_checkbox)
        self.form.addRow(self.visible_label, self.visible_checkbox)
        add_labeled_row(self.form, "Requirement", self.required_checkbox)

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
        self.mapping_group_label.setBuddy(self.mapping_combo)
        self.mapping_attribute_label = QLabel("Mapping attribute")
        self.mapping_attribute_label.setBuddy(self.attribute_input)
        self.relation_form_label = QLabel("Trigger / rule")
        self.relation_form_label.setBuddy(self.relation_label)
        self.form.addRow(self.mapping_group_label, self.mapping_combo)
        self.form.addRow(self.mapping_attribute_label, self.attribute_input)
        self.form.addRow(self.relation_form_label, self.relation_label)
        self.notes_input = QLineEdit()
        self.notes_input.setAccessibleName("Definition notes")
        add_labeled_row(self.form, "Notes", self.notes_input)
        layout.addLayout(self.form)

        self.error_label = QLabel()
        configure_validation_summary(
            self.error_label,
            "Add Definition validation summary",
        )
        layout.addWidget(self.error_label)
        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.setAccessibleName(f"Cancel {self.windowTitle()}")
        cancel.clicked.connect(self.reject)
        self.apply_button = QPushButton("Apply")
        self.apply_button.setAccessibleName(f"Apply {self.windowTitle()} to Draft")
        self.apply_button.setDefault(True)
        self.apply_button.clicked.connect(self._apply)
        actions.addWidget(cancel)
        actions.addWidget(self.apply_button)
        layout.addLayout(actions)

        self.setTabOrder(self.intent_combo, self.label_input)
        self.setTabOrder(self.label_input, self.key_input)
        self.setTabOrder(self.key_input, self.data_type_combo)
        self.setTabOrder(self.data_type_combo, self.visible_checkbox)
        self.setTabOrder(self.visible_checkbox, self.required_checkbox)
        self.setTabOrder(self.required_checkbox, self.mapping_combo)
        self.setTabOrder(self.mapping_combo, self.attribute_input)
        self.setTabOrder(self.attribute_input, self.notes_input)
        self.setTabOrder(self.notes_input, cancel)
        self.setTabOrder(cancel, self.apply_button)

    def _update_intent_fields(self) -> None:
        mapping = self._standalone or self.intent_combo.currentData() == "mapping_predict"
        hidden_focus = self.focusWidget() in {
            self.mapping_combo,
            self.attribute_input,
            self.relation_label,
        }
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
        if hidden_focus and not mapping:
            self.notes_input.setFocus()

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
        else:
            show_validation_summary(self.error_label, message)
