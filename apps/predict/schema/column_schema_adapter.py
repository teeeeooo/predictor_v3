"""Qt-free predictor column schema adapter."""

from dataclasses import dataclass
from collections.abc import Sequence

from apps.predict.application.runtime_columns import (
    PredictRuntimeColumnDescriptor,
)
from apps.predict.application.runtime_snapshot import (
    compatibility_predict_runtime_snapshot,
)
from core.predictor_schema.presentation import presentation_metadata


@dataclass(frozen=True)
class PredictColumn:
    """Predict table column descriptor derived from core schema metadata."""

    index: int
    feature_identity: str
    display_order: int
    key: str
    header: str
    role: str
    group: str
    classification: str
    visible: bool
    active: bool
    width: int
    editable: bool
    dropdown: bool
    editor: str
    data_type: str
    required: bool
    readonly: bool
    value_source: str
    mapping_entity: str
    mapping_attribute: str
    trigger_column: str
    rule_id: str
    model_input_enabled: bool
    one_hot_group: str
    mapping: str
    dropdown_target: str
    ml_feature: str
    ml_target: str
    source: str
    mapping_key: str
    bg_color: str

    @property
    def is_input(self) -> bool:
        """Return whether this column belongs to user input."""
        return self.group == "input"

    @property
    def is_auto(self) -> bool:
        """Return whether this column belongs to auto-filled inputs."""
        return self.group == "auto"

    @property
    def is_result(self) -> bool:
        """Return whether this column belongs to prediction results."""
        return self.group == "result"


def build_predict_column_schema(
    descriptors: Sequence[PredictRuntimeColumnDescriptor] | None = None,
) -> tuple[PredictColumn, ...]:
    """Return active visible predictor columns in generation display order."""
    runtime_descriptors = (
        tuple(descriptors)
        if descriptors is not None
        else compatibility_predict_runtime_snapshot().column_descriptors
    )
    visible = tuple(
        sorted(
            (
                item for item in runtime_descriptors
                if item.active
                and item.visible
                and item.classification in {"input", "auto", "result"}
            ),
            key=lambda item: item.display_order,
        )
    )
    return tuple(
        _column_from_descriptor(index, descriptor)
        for index, descriptor in enumerate(visible)
    )


def build_input_column_schema(
    descriptors: Sequence[PredictRuntimeColumnDescriptor] | None = None,
) -> tuple[PredictColumn, ...]:
    """Return user-input and auto-filled columns for the input table."""
    columns = build_predict_column_schema(descriptors)
    return tuple(column for column in columns if column.group in {"input", "auto"})


def build_result_column_schema(
    descriptors: Sequence[PredictRuntimeColumnDescriptor] | None = None,
) -> tuple[PredictColumn, ...]:
    """Return result columns for the result table."""
    return tuple(
        column for column in build_predict_column_schema(descriptors)
        if column.is_result
    )


def dropdown_columns() -> tuple[PredictColumn, ...]:
    """Return dropdown-capable input columns."""
    return tuple(column for column in build_input_column_schema() if column.dropdown)


def column_by_key(key: str) -> PredictColumn:
    """Return one column descriptor by schema key."""
    try:
        return _COLUMNS_BY_KEY[key]
    except KeyError as exc:
        raise KeyError(f"unknown predictor column key: {key}") from exc


def _column_from_descriptor(
    index: int,
    descriptor: PredictRuntimeColumnDescriptor,
) -> PredictColumn:
    presentation = presentation_metadata(descriptor.key, descriptor.role)
    dropdown = descriptor.editor == "dropdown"
    editable = descriptor.role == "input" and not descriptor.readonly
    return PredictColumn(
        index=index,
        feature_identity=descriptor.feature_identity,
        display_order=descriptor.display_order,
        key=descriptor.key,
        header=descriptor.label,
        role=descriptor.role,
        group=descriptor.classification,
        classification=descriptor.classification,
        visible=descriptor.visible,
        active=descriptor.active,
        width=int(presentation.get("width", 100)),
        editable=editable,
        dropdown=dropdown,
        editor=descriptor.editor,
        data_type=descriptor.data_type,
        required=descriptor.required,
        readonly=descriptor.readonly or descriptor.role == "result",
        value_source=descriptor.value_source,
        mapping_entity=descriptor.mapping_entity,
        mapping_attribute=descriptor.mapping_attribute,
        trigger_column=descriptor.trigger_column,
        rule_id=descriptor.rule_id,
        model_input_enabled=descriptor.model_input_enabled,
        one_hot_group=descriptor.one_hot_group,
        mapping=descriptor.key if dropdown else "",
        dropdown_target=descriptor.key if dropdown else "",
        ml_feature=(
            descriptor.ml_name
            if descriptor.role in {"input", "auto"}
            and descriptor.model_input_enabled
            else ""
        ),
        ml_target=(
            descriptor.ml_name
            if descriptor.role == "result"
            and descriptor.value_source == "result"
            else ""
        ),
        source=descriptor.trigger_column if descriptor.role == "auto" else "",
        mapping_key=(
            descriptor.mapping_attribute if descriptor.role == "auto" else ""
        ),
        bg_color=str(presentation.get("bg_color", "")),
    )


_COLUMNS_BY_KEY = {column.key: column for column in build_predict_column_schema()}
