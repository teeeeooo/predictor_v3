"""Golden parity and DAG execution tests for the shared Derived evaluator."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from core.data_definition import (
    AddDerivedIntent,
    SetDerivedActiveIntent,
    apply_derived_command,
    build_data_definition_draft,
)
from core.data_definition.contract import bootstrap_manifest, candidate_manifest_from_draft
from core.data_definition.derived.evaluator import evaluate_derived_features, evaluation_snapshot
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


@pytest.mark.parametrize("mutation", [
    lambda frame: frame.drop(columns=["Comp EER"]),
    lambda frame: frame.assign(**{"Comp EER": ["2"]}),
])
def test_missing_and_non_numeric_fail_exactly_like_frozen_production(mutation):
    data = _one_row()
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


def test_train_and_predict_adapters_use_identical_shared_outputs():
    frame = _one_row()
    config = {"targets": [], "mandatory_features": ["Cool_Capa_per_EER"]}
    train_x, _train_y = prepare_pipeline(frame, config)
    predict_frame = build_input_df(
        frame.iloc[0].to_dict(), required_features=["Cool_Capa_per_EER"]
    )
    for name in _DERIVED_NAMES:
        assert train_x[name].iloc[0] == predict_frame[name].iloc[0]


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
