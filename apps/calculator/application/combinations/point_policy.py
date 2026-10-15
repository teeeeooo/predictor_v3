"""Project existing standard point policies into independent candidate axes."""
from apps.calculator.application.ahri.seer2_adapter import AHRI_SEER2_PRODUCT_POINT_ORDER
from apps.calculator.application.ahri.hspf2_adapter import AHRI_HSPF2_POINT_ORDER, AHRI_HSPF2_OPTIONAL_POINTS
from apps.calculator.application.ahri.hspf2_multicapacity_adapter import (
    AhriHspf2Options, AHRI_HSPF2_DUAL_POINT_ORDER, AHRI_HSPF2_TRIPLE_POINT_ORDER,
    dual_h3_low_required, triple_h3_low_required, _optional_point_state,
)
from apps.calculator.application.ahri_m.seer_adapter import AHRI_M_SEER_POINT_ORDER
from apps.calculator.application.ahri_m.hspf_adapter import AHRI_M_HSPF_POINT_ORDER, AHRI_M_HSPF_OPTIONAL_POINTS
from apps.calculator.application.en14825.scop_adapter import ScopAdapter
from .models import Point


def resolve_points(context, scop_adapter=None):
    kind, values, options = context.kind, dict(context.values), dict(context.options)
    if kind in ("iso", "hong_kong_cspf", "hong_kong_hspf", "brazil", "korea_cspf", "korea_hspf", "saso"):
        if kind == "saso":
            fields = [("46_full", "full_46"), ("35_full", "full_35"), ("35_half", "half_35"), ("35_min", "min_35")]
        elif kind in ("hong_kong_hspf", "korea_hspf"):
            fields = [("7_full", "full"), ("7_half", "half")]
            if kind == "korea_hspf":
                fields += [("7_min", "min"), ("defrost", "defrost"), ("-7_max", "max")]
        else:
            fields = [("35_full", "full"), ("35_half", "half")]
            if kind == "brazil": fields += [("29_half", "half_29")]
            if kind == "korea_cspf": fields += [("29_min", "min")]
        return tuple(Point(key, prefix+"_capacity", prefix+"_power",
                           role="inactive" if key=="35_min" and context.mode!="with_optional_test" else "required") for key, prefix in fields)
    if kind == "en_seer":
        return tuple(Point(key, "tested_capacity_"+key, "tested_power_"+key) for key in "ABCD")
    if kind == "en_scop":
        adapter = scop_adapter or ScopAdapter()
        availability = adapter.resolve_point_availability(context.climate, float(values["tbiv_temp_c"]) if values.get("tbiv_temp_c", "").strip() else None, float(values["tol_temp_c"]) if values.get("tol_temp_c", "").strip() else None)
        return tuple(Point(key, "tested_capacity_"+key, "tested_power_"+key,
                           role=state["state"], source=state["mapped_from"] or "") for key, state in availability["points"].items())
    inactive = {}
    if kind == "m_seer":
        order = AHRI_M_SEER_POINT_ORDER
    elif kind == "m_hspf":
        order = AHRI_M_HSPF_POINT_ORDER
        inactive = {key: not options.get("measured_"+key.lower(), False) for key in AHRI_M_HSPF_OPTIONAL_POINTS}
    elif kind == "seer2":
        order = AHRI_SEER2_PRODUCT_POINT_ORDER[context.product]
    elif kind == "hspf2":
        opts = AhriHspf2Options(**options)
        if context.product == "variable_capacity":
            order = AHRI_HSPF2_POINT_ORDER
            inactive = {key: not getattr(opts, "measured_"+key.lower()) for key in AHRI_HSPF2_OPTIONAL_POINTS}
        else:
            order = AHRI_HSPF2_DUAL_POINT_ORDER if context.product == "dual_stage" else AHRI_HSPF2_TRIPLE_POINT_ORDER
            h3 = dual_h3_low_required(values, lockout_enabled=opts.low_stage_lockout_enabled) if context.product=="dual_stage" else triple_h3_low_required(values)
            inactive = {key: not active for key, active in _optional_point_state(opts, h3_low_required=h3).items()}
    else:
        raise ValueError(f"Unsupported combination context: {kind}")
    return tuple(Point(key, "capacity_"+key, "power_"+key, "Btu/h",
                       role="inactive" if inactive.get(key, False) else "required") for key in order)
