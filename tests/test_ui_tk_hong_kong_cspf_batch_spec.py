from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.sections.hong_kong_cspf_batch_spec import (
    CSEC,
    CSPF,
    DECLARED,
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    STATUS,
    HONG_KONG_CSPF_BATCH_SPEC,
    HongKongCspfBatchHandler,
)
from ui_tk.sections.iso16358_helpers import build_cspf_input
from ui_tk.sections.result_formatting import summarize_cspf_result


def _default_row() -> dict[str, str]:
    return dict(HONG_KONG_CSPF_BATCH_SPEC.default_rows[0])


def test_hong_kong_cspf_batch_row_matches_single_case_core_path():
    row = _default_row()
    handler = HongKongCspfBatchHandler("Hong Kong")

    batch_result = handler.calculate_row(row)

    measured, declared = build_cspf_input(
        full_capacity=3600,
        full_power=900,
        half_capacity=1700,
        half_power=380,
        declared_capacity=3500,
    )
    profile_id = resolve_profile_id("Hong Kong", "CSPF")
    calc = create_calculator_for_profile(profile_id=profile_id)
    single_result = calc.calculate_cspf(measured, declared_capacity=declared)
    fields = dict(summarize_cspf_result(single_result).fields)

    assert batch_result.values[CSPF] == fields["CSPF"] == "4.939"
    assert batch_result.values[CSEC] == fields["CSEC [kWh]"]
    assert batch_result.values[STATUS] == "OK"


def test_hong_kong_cspf_batch_row_reports_invalid_input_as_status():
    row = _default_row()
    row[FULL_POWER] = "not-a-number"
    handler = HongKongCspfBatchHandler("Hong Kong")

    batch_result = handler.calculate_row(row)

    assert batch_result.values[CSPF] == ""
    assert batch_result.values[CSEC] == ""
    assert batch_result.values[STATUS].startswith("Error: 35 Full Power")


def test_hong_kong_cspf_batch_spec_has_expected_columns():
    assert HONG_KONG_CSPF_BATCH_SPEC.input_keys == (
        "case",
        DECLARED,
        FULL_CAPACITY,
        FULL_POWER,
        HALF_CAPACITY,
        HALF_POWER,
    )
    assert HONG_KONG_CSPF_BATCH_SPEC.result_keys == (CSPF, CSEC)
    assert HONG_KONG_CSPF_BATCH_SPEC.status_keys == (STATUS,)
