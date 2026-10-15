"""Real owner sample inputs, with current application common defaults."""
from dataclasses import asdict
from apps.calculator.application.combinations.models import Context
from apps.calculator.application.ahri.hspf2_multicapacity_adapter import AhriHspf2Options
from apps.calculator.application.ahri.seer2_adapter import AhriSeer2Options, AHRI_SEER2_DUAL_DEFAULTS
from apps.calculator.application.ahri_m.hspf_adapter import AhriHspfOptions
from apps.calculator.application.ahri.product_defaults import AHRI_HSPF2_COMMON_DEFAULTS, AHRI_HSPF2_TRIPLE_RANGE_DEFAULTS
from apps.calculator.application.combinations.adapters import PROFILES
from tests.calculator_ui_sample_values import (
    ISO_TWO_POINT_SAMPLE_VALUES, HONG_KONG_CSPF_SAMPLE_VALUES, HONG_KONG_HSPF_SAMPLE_VALUES,
    SASO_T3_SAMPLE_VALUES, EN14825_SEER_SAMPLE_VALUES, EN14825_SCOP_SAMPLE_VALUES, HSPF2_SAMPLE_VALUES,
)
from tests.test_calculator_korea_cspf_usecase import KOREA_CSPF_SAMPLE_VALUES
from tests.test_calculator_korea_hspf_usecase import KOREA_HSPF_SAMPLE_VALUES
from tests.test_apps_calculator_ui_ahri_seer2 import SAMPLE_VALUES
from tests.test_ahri_m_seer_hspf import SEER_POINTS, HSPF_POINTS
from tests.test_ahri_multicapacity_2026 import DUAL_SEER_POINTS, DUAL_HSPF_POINTS, TRIPLE_POINTS


def pair_values(points):
    return {f"{kind}_{key}": str(value) for key,pair in points.items() for kind,value in zip(("capacity","power"),pair) if key != "AFull" or len(points)==4}


def contexts():
    def ctx(kind, values, options=None, **kwargs):
        return Context(kind, profile=PROFILES.get(kind, ""), values=tuple(values.items()),
                       options=tuple(asdict(options).items()) if options else (), **kwargs)
    result = [Context("iso", profile=label, values=tuple(ISO_TWO_POINT_SAMPLE_VALUES.items())) for label in ("ISO 16358-1", "India ISEER")]
    for kind, values in (("hong_kong_cspf",HONG_KONG_CSPF_SAMPLE_VALUES), ("hong_kong_hspf",HONG_KONG_HSPF_SAMPLE_VALUES),
                         ("korea_cspf",KOREA_CSPF_SAMPLE_VALUES), ("korea_hspf",KOREA_HSPF_SAMPLE_VALUES),
                         ("brazil",{**ISO_TWO_POINT_SAMPLE_VALUES,"half_29_capacity":"1700","half_29_power":"300"})):
        result.append(ctx(kind, values))
    result += [ctx("saso",SASO_T3_SAMPLE_VALUES, mode=mode) for mode in ("required_only","with_optional_test")]
    common = dict(p_to_w="0",p_sb_w="0",p_ck_w="0",p_off_w="0",cd="0.25",appliance_type="reversible")
    result.append(ctx("en_seer", {**EN14825_SEER_SAMPLE_VALUES, **common,"p_design_c_w":"3500","t_design_c":"35"}))
    for climate,tbiv,tol in (("average",-10,-11),("warmer",2,-11),("colder",-15,-22)):
        result.append(ctx("en_scop",{**EN14825_SCOP_SAMPLE_VALUES,**common,"p_design_h_w":"3500","tbiv_temp_c":str(tbiv),"tol_temp_c":str(tol)},climate=climate))
    result.append(ctx("m_seer",{**pair_values(SEER_POINTS),"cd":"0.25"}))
    result.append(ctx("m_hspf",{**pair_values(HSPF_POINTS),"capacity_H22":"10000","power_H22":"990","cd":"0.25","cut_out_c":"-17.8","cut_in_c":"-15","defrost_test_minutes":"90","defrost_max_minutes":"720"},AhriHspfOptions()))
    for product, values in (("variable_capacity",SAMPLE_VALUES),("dual_stage",{**pair_values(DUAL_SEER_POINTS),**AHRI_SEER2_DUAL_DEFAULTS})):
        for system in ("HP","AC"):
            result.append(ctx("seer2",values,AhriSeer2Options(product_classification=product),product=product,system_type=system))
    result.append(ctx("hspf2",{**HSPF2_SAMPLE_VALUES,"cd":"0.25","defrost_credit":"1","cut_out_c":"-17.8","cut_in_c":"-15"},AhriHspf2Options(),product="variable_capacity"))
    for product,points in (("dual_stage",DUAL_HSPF_POINTS),("triple_capacity_northern",TRIPLE_POINTS)):
        result.append(ctx("hspf2",{**pair_values(points),**AHRI_HSPF2_COMMON_DEFAULTS,**(AHRI_HSPF2_TRIPLE_RANGE_DEFAULTS if product.startswith("triple") else {}),"a2_capacity":"30000"},AhriHspf2Options(product_classification=product),product=product))
    return result
