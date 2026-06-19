"""Focused headless tests for EN14825 batch specifications and handlers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps.calculator.ui.batch.matrix_models import (
    MatrixCellKind,
    MatrixPhysicalRowType,
)
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.en14825.seer_adapter import SeerAdapter
from apps.calculator.ui.en14825.seer_batch import (
    EN14825_SEER_BATCH_SPEC,
    En14825SeerBatchCommonInputs,
    En14825SeerBatchHandler,
)
from apps.calculator.ui.en14825.scop_adapter import ScopAdapter
from apps.calculator.ui.en14825.scop_batch import (
    En14825ScopBatchCommonInputs,
    En14825ScopBatchHandler,
    build_en14825_scop_batch_spec,
)


VALID_CASE = {
    "p_design_c": "3500",
    "a_capacity": "3500",
    "a_power": "900",
    "b_capacity": "3200",
    "b_power": "800",
    "c_capacity": "2800",
    "c_power": "680",
    "d_capacity": "2400",
    "d_power": "560",
}

VALID_SCOP_AVERAGE_CASE = {
    "p_design_h": "3000",
    "a_capacity": "3600",
    "a_power": "900",
    "b_capacity": "2650",
    "b_power": "576",
    "c_capacity": "1700",
    "c_power": "315",
    "d_capacity": "1200",
    "d_power": "194",
    "tol_capacity": "800",
    "tol_power": "400",
    "tbiv_capacity": "2650",
    "tbiv_power": "576",
}


class FakeSeerAdapter:
    def __init__(self, *, status_code: str = "complete") -> None:
        self.status_code = status_code
        self.calls: list[dict] = []
        self.raise_error = False

    def calculate(self, **kwargs):
        self.calls.append(kwargs)
        if self.raise_error:
            raise ValueError("adapter failure")
        return SimpleNamespace(
            status_code=self.status_code,
            tested_seer=5.126,
            tested_qc_kwh=1234.56,
        )


class FakeScopAdapter:
    def __init__(self, required_points=("B", "C", "D")) -> None:
        self.required_points = required_points
        self.calls: list[dict] = []
        self.raise_error = False

    def resolve_point_availability(self, climate, tbiv_temp_c, tol_temp_c):
        temperatures = {
            "A": -7.0,
            "B": 2.0,
            "C": 7.0,
            "D": 12.0,
            "TOL": tol_temp_c if tol_temp_c is not None else -11.0,
            "Tbiv": tbiv_temp_c if tbiv_temp_c is not None else 2.0,
        }
        return {
            "required_independent_points": self.required_points,
            "resolved_temperatures": temperatures,
        }

    def calculate(self, **kwargs):
        self.calls.append(kwargs)
        if self.raise_error:
            raise ValueError("adapter failure")
        return SimpleNamespace(
            status_code="complete",
            tested_scop=4.126,
            tested_qh_kwh=2345.67,
        )


@pytest.fixture
def common_inputs() -> En14825SeerBatchCommonInputs:
    return En14825SeerBatchCommonInputs(
        t_design_c=35.0,
        cd=0.25,
        appliance_type="cooling_only",
        p_to_w=10.0,
        p_sb_w=20.0,
        p_ck_w=30.0,
        p_off_w=40.0,
    )


def test_seer_batch_spec_shape_and_keys() -> None:
    spec = EN14825_SEER_BATCH_SPEC

    assert spec.profile_key == "en14825_seer"
    assert spec.physical_rows == (
        MatrixPhysicalRowType.CAPACITY,
        MatrixPhysicalRowType.POWER,
    )
    assert tuple(point.key for point in spec.measurement_points) == (
        "p_design_c",
        "a",
        "b",
        "c",
        "d",
    )
    assert tuple(point.label for point in spec.measurement_points) == (
        "Pdesignc",
        "A (35°C)",
        "B (30°C)",
        "C (25°C)",
        "D (20°C)",
    )
    assert spec.input_keys == tuple(VALID_CASE)
    assert spec.result_keys == ("seer", "qc_kwh")


def test_seer_batch_spec_cell_roles() -> None:
    spec = EN14825_SEER_BATCH_SPEC

    assert spec.resolve_cell((0, 2)).input_key == "p_design_c"
    assert spec.resolve_cell((1, 2)).kind is MatrixCellKind.NOT_APPLICABLE
    assert spec.resolve_cell((0, 3)).input_key == "a_capacity"
    assert spec.resolve_cell((1, 3)).input_key == "a_power"
    assert spec.resolve_cell((0, 7)).kind is MatrixCellKind.RESULT
    assert spec.resolve_cell((1, 7)).kind is MatrixCellKind.BLANK_READ_ONLY


def test_seer_batch_handler_maps_tested_inputs_and_common_values(
    common_inputs: En14825SeerBatchCommonInputs,
) -> None:
    adapter = FakeSeerAdapter()
    handler = En14825SeerBatchHandler(common_inputs, adapter=adapter)

    result = handler.calculate_row(VALID_CASE)

    assert result.state is BatchRowState.OK
    assert result.values == {"seer": "5.13", "qc_kwh": "1234.6"}
    assert len(adapter.calls) == 1
    call = adapter.calls[0]
    assert call["p_design_c_w"] == 3500.0
    assert call["t_design_c"] == 35.0
    assert call["cd"] == 0.25
    assert call["appliance_type"] == "cooling_only"
    assert (call["p_to_w"], call["p_sb_w"], call["p_ck_w"], call["p_off_w"]) == (
        10.0,
        20.0,
        30.0,
        40.0,
    )
    assert tuple(call["inputs"]) == ("A", "B", "C", "D")
    assert call["inputs"]["A"].declared_capacity is None
    assert call["inputs"]["A"].declared_eer is None
    assert call["inputs"]["A"].tested_capacity == 3500.0
    assert call["inputs"]["A"].tested_power == 900.0


def test_seer_batch_handler_runs_real_adapter_and_config() -> None:
    adapter = SeerAdapter()
    defaults = adapter.get_seer_defaults()
    common_inputs = En14825SeerBatchCommonInputs(
        t_design_c=defaults["t_design_c"],
        cd=defaults["degradation_coefficient"],
        appliance_type=defaults["appliance_type"],
    )
    handler = En14825SeerBatchHandler(common_inputs, adapter=adapter)

    result = handler.calculate_row(VALID_CASE)

    assert result.state is BatchRowState.OK
    assert float(result.values["seer"]) > 0.0
    assert float(result.values["qc_kwh"]) > 0.0


def test_seer_batch_handler_distinguishes_blank_partial_and_invalid_rows(
    common_inputs: En14825SeerBatchCommonInputs,
) -> None:
    adapter = FakeSeerAdapter()
    handler = En14825SeerBatchHandler(common_inputs, adapter=adapter)

    blank = handler.calculate_row({})
    partial = handler.calculate_row({"p_design_c": "3500"})
    invalid = handler.calculate_row({**VALID_CASE, "a_capacity": "bad"})

    assert blank.state is BatchRowState.PENDING
    assert partial.state is BatchRowState.PENDING
    assert invalid.state is BatchRowState.ERROR
    assert blank.values == partial.values == invalid.values == {
        "seer": "",
        "qc_kwh": "",
    }
    assert adapter.calls == []


@pytest.mark.parametrize("failure", ("status", "exception", "missing_result"))
def test_seer_batch_handler_returns_error_for_adapter_failure(
    failure: str,
    common_inputs: En14825SeerBatchCommonInputs,
) -> None:
    adapter = FakeSeerAdapter(status_code="tested_error" if failure == "status" else "complete")
    if failure == "exception":
        adapter.raise_error = True
    handler = En14825SeerBatchHandler(common_inputs, adapter=adapter)
    if failure == "missing_result":
        adapter.calculate = lambda **_kwargs: SimpleNamespace(
            status_code="complete",
            tested_seer=None,
            tested_qc_kwh=1234.56,
        )

    result = handler.calculate_row(VALID_CASE)

    assert result.state is BatchRowState.ERROR
    assert result.values == {"seer": "", "qc_kwh": ""}


def test_scop_batch_spec_uses_adapter_required_points() -> None:
    adapter = FakeScopAdapter()

    spec = build_en14825_scop_batch_spec(
        "warmer",
        2.0,
        -11.0,
        adapter=adapter,
    )

    assert spec.profile_key == "en14825_scop"
    assert tuple(point.key for point in spec.measurement_points) == (
        "p_design_h",
        "B",
        "C",
        "D",
    )
    assert tuple(point.label for point in spec.measurement_points) == (
        "Pdesignh",
        "B (2°C)",
        "C (7°C)",
        "D (12°C)",
    )
    assert spec.input_keys == (
        "p_design_h",
        "b_capacity",
        "b_power",
        "c_capacity",
        "c_power",
        "d_capacity",
        "d_power",
    )
    assert spec.result_keys == ("scop", "qh_kwh")
    assert spec.resolve_cell((1, 2)).kind is MatrixCellKind.NOT_APPLICABLE
    assert spec.resolve_cell((0, 3)).input_key == "b_capacity"
    assert spec.resolve_cell((1, 3)).input_key == "b_power"


def test_scop_batch_handler_maps_tested_inputs_and_common_values() -> None:
    adapter = FakeScopAdapter()
    common = En14825ScopBatchCommonInputs(
        climate="warmer",
        tbiv_temp_c=2.0,
        tol_temp_c=-11.0,
        cd=0.25,
        appliance_type="reversible",
        p_to_w=10.0,
        p_sb_w=20.0,
        p_ck_w=30.0,
        p_off_w=40.0,
    )
    handler = En14825ScopBatchHandler(common, adapter=adapter)
    row = {
        "p_design_h": "1300",
        "b_capacity": "1329.3",
        "b_power": "254.2",
        "c_capacity": "908.3",
        "c_power": "154.0",
        "d_capacity": "929.9",
        "d_power": "123.1",
    }

    result = handler.calculate_row(row)

    assert result.state is BatchRowState.OK
    assert result.values == {"scop": "4.13", "qh_kwh": "2345.7"}
    call = adapter.calls[0]
    assert call["p_design_h_w"] == 1300.0
    assert call["climate"] == "warmer"
    assert (call["tbiv_temp_c"], call["tol_temp_c"]) == (2.0, -11.0)
    assert (call["cd"], call["appliance_type"]) == (0.25, "reversible")
    assert (call["p_to_w"], call["p_sb_w"], call["p_ck_w"], call["p_off_w"]) == (
        10.0,
        20.0,
        30.0,
        40.0,
    )
    assert tuple(call["inputs"]) == ("B", "C", "D")
    assert call["inputs"]["B"].declared_capacity is None
    assert call["inputs"]["B"].declared_cop is None
    assert call["inputs"]["B"].tested_capacity == 1329.3
    assert call["inputs"]["B"].tested_power == 254.2


def test_scop_batch_handler_runs_real_adapter_and_config() -> None:
    common = En14825ScopBatchCommonInputs(
        climate="average",
        tbiv_temp_c=-10.0,
        tol_temp_c=-11.0,
        p_to_w=50.0,
        p_sb_w=5.0,
        p_ck_w=10.0,
    )
    handler = En14825ScopBatchHandler(common, adapter=ScopAdapter())

    result = handler.calculate_row(VALID_SCOP_AVERAGE_CASE)

    assert result.state is BatchRowState.OK
    assert float(result.values["scop"]) > 0.0
    assert float(result.values["qh_kwh"]) > 0.0


def test_scop_batch_handler_keeps_blank_and_partial_rows_pending() -> None:
    adapter = FakeScopAdapter()
    handler = En14825ScopBatchHandler(
        En14825ScopBatchCommonInputs(climate="warmer"),
        adapter=adapter,
    )
    complete = {
        "p_design_h": "1300",
        "b_capacity": "1329.3",
        "b_power": "254.2",
        "c_capacity": "908.3",
        "c_power": "154.0",
        "d_capacity": "929.9",
        "d_power": "123.1",
    }

    blank = handler.calculate_row({})
    partial = handler.calculate_row({"p_design_h": "1300"})
    invalid = handler.calculate_row({**complete, "b_capacity": "bad"})

    assert blank.state is BatchRowState.PENDING
    assert partial.state is BatchRowState.PENDING
    assert invalid.state is BatchRowState.ERROR
    assert blank.values == partial.values == invalid.values == {
        "scop": "",
        "qh_kwh": "",
    }
    assert adapter.calls == []


def test_scop_batch_handler_returns_error_for_adapter_failure() -> None:
    adapter = FakeScopAdapter()
    adapter.raise_error = True
    handler = En14825ScopBatchHandler(
        En14825ScopBatchCommonInputs(climate="warmer"),
        adapter=adapter,
    )
    row = {
        "p_design_h": "1300",
        "b_capacity": "1329.3",
        "b_power": "254.2",
        "c_capacity": "908.3",
        "c_power": "154.0",
        "d_capacity": "929.9",
        "d_power": "123.1",
    }

    result = handler.calculate_row(row)

    assert result.state is BatchRowState.ERROR
    assert result.values == {"scop": "", "qh_kwh": ""}
