"""Golden parity and DAG execution tests for the shared Derived evaluator."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from core.data_definition import (
    AddDefinitionIntent,
    AddDerivedIntent,
    SetDerivedActiveIntent,
    apply_derived_command,
    apply_add_definition_command,
    build_data_definition_draft,
)
from core.data_definition.contract import bootstrap_manifest, candidate_manifest_from_draft
from core.data_definition.derived.evaluator import (
    evaluate_derived_features,
    evaluation_snapshot,
    missing_evaluator_input_ml_names,
    project_derived_input_dependencies,
)
from core.ml.preprocessing import calculate_derived_features
from core.ml.preprocessing import prepare_pipeline
from core.ml.inference import build_input_df


def test_shared_evaluator_preserves_frozen_production_formula_semantics():
    data = pd.DataFrame({
        "prefix": [1, 2, 3, 4, 5],
        "Cooling Capa": [10.0, -8.0, 0.0, np.nan, np.inf],
        "Heating Capa": [12.5, -9.0, 0.0, np.inf, -np.inf],
        "Comp EER": [2.0, -4.0, 0.0, np.nan, np.inf],
        "Cond Area": [5.0, 0.0, 2.5, np.inf, -np.inf],
        "Evap Area": [4.0, -2.0, 0.0, np.nan, 2.0],
        "Comp cc": [2.5, 1.5, 0.0, np.inf, -3.0],
        "suffix": [9, 8, 7, 6, 5],
    })
    before = data.copy(deep=True)
    with np.errstate(invalid="ignore"):
        expected = _frozen_production_evaluator(data)
        actual = calculate_derived_features(data)
    pdt.assert_frame_equal(actual, expected)
    pdt.assert_frame_equal(data, before)
    assert actual is not data
    assert actual.columns[-8:].tolist() == _DERIVED_NAMES
    assert all(str(actual[name].dtype) == "float64" for name in _DERIVED_NAMES)


def test_missing_input_is_actionable_before_evaluator_key_error():
    with pytest.raises(ValueError, match="Comp EER"):
        calculate_derived_features(_one_row().drop(columns=["Comp EER"]))


def test_non_numeric_still_fails_like_frozen_production():
    data = _one_row()
    mutation = lambda frame: frame.assign(**{"Comp EER": ["2"]})
    with pytest.raises(Exception) as legacy:
        _frozen_production_evaluator(mutation(data.copy()))
    with pytest.raises(type(legacy.value)) as shared:
        calculate_derived_features(mutation(data.copy()))
    assert str(shared.value) == str(legacy.value)


def test_derived_to_derived_chain_executes_in_deterministic_topological_order():
    manifest = bootstrap_manifest()
    draft = build_data_definition_draft(manifest=manifest)
    added = apply_derived_command(draft, AddDerivedIntent(
        "Ratio_chain",
        manifest.derived[0].identity,
        manifest.derived[0].denominator_identity,
    ))
    enabled = apply_derived_command(
        added.draft, SetDerivedActiveIntent(added.identity, True)
    )
    assert added.accepted and enabled.accepted
    candidate = candidate_manifest_from_draft(enabled.draft, manifest)
    snapshot = evaluation_snapshot(candidate)
    assert snapshot.definitions[-1].output_ml_name == "Ratio_chain"
    actual = evaluate_derived_features(_one_row(), snapshot)
    assert actual["Ratio_chain"].iloc[0] == pytest.approx((10.0 / 2.0) / 2.0)


def test_preexisting_output_keeps_column_position_and_inactive_is_not_evaluated():
    manifest = bootstrap_manifest()
    first = manifest.derived[0]
    inactive = replace(
        manifest,
        derived=(replace(first, active=False), *manifest.derived[1:]),
        ordering=replace(
            manifest.ordering,
            ml=tuple(item for item in manifest.ordering.ml if item != first.identity),
        ),
    )
    frame = _one_row().assign(Cool_Capa_per_CondArea=[999.0])
    position = frame.columns.get_loc("Cool_Capa_per_CondArea")
    actual = evaluate_derived_features(frame, evaluation_snapshot(inactive))
    assert "Cool_Capa_per_EER" not in actual
    assert actual.columns.get_loc("Cool_Capa_per_CondArea") == position
    inactive_snapshot = evaluation_snapshot(inactive)
    inactive_projection = project_derived_input_dependencies(
        inactive_snapshot,
        [first.ml_name],
    )
    assert inactive_projection.definition_identities == ()
    assert inactive_projection.base_inputs == ()


def test_train_and_predict_adapters_use_identical_shared_outputs():
    frame = _one_row()
    config = {"targets": [], "mandatory_features": ["Cool_Capa_per_EER"]}
    train_x, _train_y = prepare_pipeline(frame, config)
    predict_frame = build_input_df(
        frame.iloc[0].to_dict(), required_features=_DERIVED_NAMES
    )
    for name in _DERIVED_NAMES:
        assert train_x[name].iloc[0] == predict_frame[name].iloc[0]


def test_dependency_projection_is_transitive_deduplicated_and_deterministic(monkeypatch):
    manifest = bootstrap_manifest()
    draft = build_data_definition_draft(manifest=manifest)
    feature = apply_add_definition_command(draft, AddDefinitionIntent(
        "ml_only",
        "Ambient Temperature",
        "ambient_temperature",
        "number",
        model_input_enabled=True,
        ml_name="Ambient Temperature",
    ))
    assert feature.accepted
    source_identity = feature.identity[1]
    first = apply_derived_command(feature.draft, AddDerivedIntent(
        "Ambient_per_EER",
        source_identity,
        manifest.derived[0].denominator_identity,
    ))
    first_active = apply_derived_command(
        first.draft, SetDerivedActiveIntent(first.identity, True)
    )
    second = apply_derived_command(first_active.draft, AddDerivedIntent(
        "Ambient_chain",
        first.identity[1],
        source_identity,
    ))
    second_active = apply_derived_command(
        second.draft, SetDerivedActiveIntent(second.identity, True)
    )
    assert all(item.accepted for item in (first, first_active, second, second_active))
    candidate = candidate_manifest_from_draft(second_active.draft, manifest)
    snapshot = evaluation_snapshot(candidate)

    direct = project_derived_input_dependencies(snapshot, ["Ambient_per_EER"])
    direct_by_identity = project_derived_input_dependencies(
        snapshot,
        [first.identity[1]],
    )
    chain = project_derived_input_dependencies(snapshot, ["Ambient_chain"])
    repeated = project_derived_input_dependencies(snapshot, ["Ambient_chain", "Ambient_chain"])
    none = project_derived_input_dependencies(snapshot, ["Cooling Power"])
    assert [item.ml_name for item in direct.base_inputs] == [
        "Comp EER", "Ambient Temperature"
    ]
    assert direct_by_identity == replace(
        direct,
        requested_outputs=(first.identity[1],),
    )
    assert [item.ml_name for item in chain.base_inputs] == [
        "Comp EER", "Ambient Temperature"
    ]
    assert repeated == chain
    assert none.base_inputs == () and none.definition_identities == ()

    monkeypatch.setattr(
        "core.ml.inference.current_derived_evaluation_snapshot",
        lambda: snapshot,
    )
    row = {"Comp EER": 2.0, "Ambient Temperature": 30.0}
    predicted = build_input_df(row, required_features=["Ambient_chain"])
    assert predicted["Ambient_per_EER"].iloc[0] == pytest.approx(15.0)
    assert predicted["Ambient_chain"].iloc[0] == pytest.approx(0.5)
    with pytest.raises(ValueError, match="Ambient Temperature"):
        build_input_df({"Comp EER": 2.0}, required_features=["Ambient_chain"])
    assert missing_evaluator_input_ml_names(
        row.keys(), chain
    ) == ()


def test_existing_eight_dependency_projection_keeps_six_base_input_order():
    snapshot = evaluation_snapshot(bootstrap_manifest())
    projection = project_derived_input_dependencies(
        snapshot,
        [item.output_ml_name for item in snapshot.definitions],
    )

    assert [item.ml_name for item in projection.base_inputs] == [
        "Cooling Capa",
        "Heating Capa",
        "Evap Area",
        "Cond Area",
        "Comp EER",
        "Comp cc",
    ]


_DERIVED_NAMES = [
    "Cool_Capa_per_EER", "Cool_Capa_per_CondArea", "Cool_Capa_per_EvapArea",
    "Cool_Capa_per_cc", "Heat_Capa_per_EER", "Heat_Capa_per_CondArea",
    "Heat_Capa_per_EvapArea", "Heat_Capa_per_cc",
]


def _one_row():
    return pd.DataFrame([{
        "Cooling Capa": 10.0, "Heating Capa": 12.0, "Comp EER": 2.0,
        "Cond Area": 5.0, "Evap Area": 4.0, "Comp cc": 2.5,
    }])


def _frozen_production_evaluator(df):  # noqa: ANN001
    result = df.copy()
    pairs = (
        ("Cool_Capa_per_EER", "Cooling Capa", "Comp EER"),
        ("Cool_Capa_per_CondArea", "Cooling Capa", "Cond Area"),
        ("Cool_Capa_per_EvapArea", "Cooling Capa", "Evap Area"),
        ("Cool_Capa_per_cc", "Cooling Capa", "Comp cc"),
        ("Heat_Capa_per_EER", "Heating Capa", "Comp EER"),
        ("Heat_Capa_per_CondArea", "Heating Capa", "Cond Area"),
        ("Heat_Capa_per_EvapArea", "Heating Capa", "Evap Area"),
        ("Heat_Capa_per_cc", "Heating Capa", "Comp cc"),
    )
    for output, numerator, denominator in pairs:
        result[output] = np.where(
            result[denominator] != 0,
            result[numerator] / result[denominator],
            0,
        )
    return result
