"""Read-only command-specific impact preview and confirmation dialog."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from apps.common.ui import style
from core.data_definition import FeatureImpactPreview


class FeatureCommandPreviewDialog(QDialog):
    def __init__(self, preview: FeatureImpactPreview, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{preview.action} Impact Preview")
        self.setAccessibleName(self.windowTitle())
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.outer")] * 4))
        title = QLabel(self.windowTitle())
        title.setObjectName("PanelTitle")
        title.setFont(style.qfont("font.window_title"))
        layout.addWidget(title)
        summary = QLabel(preview.summary)
        summary.setAccessibleName("Feature command impact summary")
        summary.setWordWrap(True)
        layout.addWidget(summary)
        details = (
            f"Predict projection: {_changed(preview.predict_projection_changed)}\n"
            f"Ordered ML projection: {_changed(preview.ordered_ml_projection_changed)}\n"
            f"Mapping requirements: {_changed(preview.mapping_requirements_changed)}\n"
            f"Derived semantics: {_changed(preview.derived_semantics_changed)}\n"
            f"Model compatibility: {_changed(preview.model_compatibility_changed)}\n"
            f"Retraining required: {'Yes' if preview.requires_retraining else 'No'}\n"
            f"Save possible: {'Yes' if preview.save_allowed else 'No'}"
        )
        evidence = QLabel(details)
        evidence.setAccessibleName("Feature command impact evidence")
        evidence.setWordWrap(True)
        layout.addWidget(evidence)
        if preview.target_evidence is not None:
            target = preview.target_evidence
            before_visible = target.before[3] if target.before is not None else None
            after_visible = target.after[3] if target.after is not None else None
            target_label = QLabel(
                f"Target identity: {target.target_identity}\n"
                f"Result Feature: {target.result_feature_identity}\n"
                f"Shape: {target.before or 'new'} → {target.after or 'removed'}\n"
                f"Predict visible: {_optional_bool(before_visible)} → {_optional_bool(after_visible)}\n"
                f"Model group: {target.model_group_before or 'none'} → {target.model_group_after or 'none'}\n"
                f"Policy: {target.policy_before or 'none'} → {target.policy_after or 'none'}\n"
                f"Final training inputs: {', '.join(target.training_inputs_before) or 'none'} → "
                f"{', '.join(target.training_inputs_after) or 'none'}\n"
                f"Active Train Targets: {', '.join(target.active_targets_before)} → "
                f"{', '.join(target.active_targets_after)}\n"
                f"Presentation fingerprint changed: {target.presentation_fingerprint_changed}; "
                f"registry fingerprint changed: {target.registry_fingerprint_changed}"
            )
            target_label.setAccessibleName("Target registry policy and training input impact")
            target_label.setWordWrap(True)
            layout.addWidget(target_label)
        if preview.one_hot_evidence:
            one_hot = QLabel("\n".join(
                f"• {item.group_key} / {item.source_value or '<group>'} → "
                f"{item.emitted_ml_name or '<no emitted Feature>'}; "
                f"order {item.order_before} → {item.order_after}; "
                f"active {item.active_before} → {item.active_after}; "
                f"selector {item.selector_column_key or '<missing>'}; "
                f"takeover fields: {', '.join(item.selector_changed_fields) or 'none'}; "
                f"restore: {'available' if item.selector_restore_available else 'not available'}; "
                f"Predict available {item.predict_available_before} → {item.predict_available_after}; "
                f"binding {item.source_binding_before or 'none'} → "
                f"{item.source_binding_after or 'none'}; "
                f"dropdown/encoder owner: canonical One-hot group "
                f"(parity: {'Yes' if item.encoder_dropdown_parity else 'No'}); "
                f"options: {item.available_option_count}; "
                f"provider revision: {item.provider_snapshot_revision or 'none'}; "
                f"dependencies: {', '.join(item.affected_dependency_summaries) or 'none'}; "
                f"owner: {item.vocabulary_owner}; Mapping values changed: No"
                for item in preview.one_hot_evidence
            ))
            one_hot.setAccessibleName("One-hot identity source order and owner evidence")
            one_hot.setWordWrap(True)
            layout.addWidget(one_hot)
        if preview.one_hot_drift_evidence:
            drift = QLabel("\n".join(
                f"• {item.code}: {item.source_binding}/{item.source_value or '<unavailable>'}. "
                f"{item.resolution}"
                for item in preview.one_hot_drift_evidence
            ))
            drift.setAccessibleName("One-hot Mapping and provider drift evidence")
            drift.setWordWrap(True)
            layout.addWidget(drift)
        if preview.execution_order_before or preview.execution_order_after:
            order = QLabel(
                "Execution order before: " + ", ".join(preview.execution_order_before)
                + "\nExecution order after: " + ", ".join(preview.execution_order_after)
                + "\nDownstream identities: "
                + (", ".join(preview.downstream_identities) or "None")
                + "\nDerived semantics fingerprint: "
                + (preview.derived_semantics_fingerprint or "Unavailable")
            )
            order.setAccessibleName("Derived dependency and execution order evidence")
            order.setWordWrap(True)
            layout.addWidget(order)
        affected = QLabel("\n".join(
            _evidence_line(item) for item in preview.evidence
        ) or "No affected Feature or dependency references.")
        affected.setAccessibleName("Affected Feature and dependency evidence")
        affected.setWordWrap(True)
        layout.addWidget(affected)
        blockers = QLabel("\n".join(
            f"• {item.message}" + (f" Next: {item.resolution}" if item.resolution else "")
            for item in preview.blockers
        ) or "No command or Save blockers.")
        blockers.setAccessibleName("Feature command blockers and resolutions")
        blockers.setWordWrap(True)
        layout.addWidget(blockers)
        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.setAccessibleName("Cancel Feature command")
        cancel.clicked.connect(self.reject)
        self.apply_button = QPushButton("Apply to Draft")
        self.apply_button.setAccessibleName("Apply previewed command to Draft")
        self.apply_button.setEnabled(preview.command_accepted)
        self.apply_button.setDefault(preview.command_accepted)
        self.apply_button.clicked.connect(self.accept)
        actions.addWidget(cancel)
        actions.addWidget(self.apply_button)
        layout.addLayout(actions)


def _changed(value: bool) -> str:
    return "Changed" if value else "Unchanged"


def _optional_bool(value: bool | None) -> str:
    return "none" if value is None else str(value).lower()


def _evidence_line(item) -> str:  # noqa: ANN001
    changes = []
    if item.predict_key_change:
        changes.append(f"Predict key {item.predict_key_change[0]} → {item.predict_key_change[1]}")
    if item.ml_name_change:
        changes.append(f"ML name {item.ml_name_change[0]} → {item.ml_name_change[1]}")
    if item.automatically_updated:
        changes.append("reference updated automatically")
    if item.blocked:
        changes.append("blocked")
    detail = "; ".join(changes)
    resolution = f" Resolution: {item.resolution}" if item.resolution else ""
    return (
        f"• {item.feature_display_name} [{item.feature_identity}] → "
        f"{item.dependency_owner}/{item.dependency_code} "
        f"[{item.reference_identity}]"
        + (f": {detail}" if detail else "")
        + resolution
    )
