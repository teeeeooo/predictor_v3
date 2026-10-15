"""Collect existing section drafts; measurement parsing stays in application owners."""
from dataclasses import asdict
from apps.calculator.application.combinations.models import Context
from apps.calculator.application.profile_resolver import two_point_profile_labels

from apps.calculator.application.combinations.adapters import PROFILES


def collect(section, kind):
    def context(values, **kwargs):
        return Context(kind, profile=PROFILES.get(kind, ""), values=tuple(values.items()), **kwargs)
    if kind == "iso":
        return [Context(kind, profile=label, values=tuple(section.input_table.get_text_values().items())) for label in two_point_profile_labels()]
    if kind.startswith("en_"):
        common = {key+"_w": value for key,value in section._common_input_values().items()}
        common.update(cd=section._cd_var.get(), appliance_type=section._appliance_type_var.get())
        if kind == "en_seer":
            return [context({**section.input_table.get_text_values(), **common,
                             "p_design_c_w": section._p_design_var.get(), "t_design_c": section._t_design_var.get()})]
        return [context({**section.input_tables[climate].get_text_values(), **common,
                         "p_design_h_w": section.p_design_h_vars[climate].get(),
                         "tbiv_temp_c": section.tbiv_vars[climate].get(), "tol_temp_c": section.tol_vars[climate].get()}, climate=climate)
                for climate in section.climates]
    if kind == "seer2":
        return [context(section._surface.text_values(), product=section.product_classification, system_type=section.type_var.get(),
                        options=tuple(asdict(section._surface.options()).items()))]
    if kind == "hspf2":
        return [context(section._active_values(), product=section.product_classification,
                        options=tuple(asdict(section._options()).items()))]
    if kind in ("m_seer", "m_hspf"):
        table = section.input_table if kind=="m_seer" else section.heating_table
        options = () if kind=="m_seer" else tuple(asdict(section.options).items())
        return [context({**section.numeric_table.get_text_values(), **table.get_text_values()}, options=options)]
    values = section.input_table.get_text_values()
    if kind in ("hong_kong_cspf", "korea_cspf", "korea_hspf"):
        values.update(section.rated_table.get_text_values())
    if kind=="saso":
        return [context(values, mode=mode) for mode in ("required_only", "with_optional_test")]
    return [context(values)]


def install(section, kind):
    from .manager import add_combination_action
    add_combination_action(section, lambda: collect(section, kind))
