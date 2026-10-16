"""Product-relevant inline selectors and flags, matching main-page controls."""
import tkinter as tk
from tkinter import ttk
from apps.calculator.ui.layout_constants import (
    CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS, CONTROL_DETAIL_SERIES_SELECTOR_WIDTH_CHARS,
    CONTROL_GROUP_GAP, CONTROL_LABEL_GAP, CONTROL_ROW_PADY,
)
from .presentation import field_label


def flag_keys(context):
    if context.kind == "m_hspf":
        return ("measured_h12", "measured_h22", "h1n_same_speed_as_h32", "demand_defrost", "automatic_cutout")
    if context.kind == "seer2" and context.product == "dual_stage":
        return ("low_stage_lockout_enabled",)
    if context.kind == "hspf2":
        if context.product == "variable_capacity":
            return ("measured_h42", "measured_h12", "measured_h22", "h1n_same_speed_as_h32", "minimum_speed_limited")
        if context.product == "dual_stage":
            return ("measured_h4_full", "measured_h2_low", "low_stage_lockout_enabled")
        return ("measured_h2_low", "measured_h2_boost", "measured_h3_low")
    return ()


class OptionsPanel(ttk.Frame):
    def __init__(self, parent, context, values_changed, options_changed):
        super().__init__(parent)
        self.context, self.options_changed = context, options_changed
        self.controls = []
        self.variables = {}
        self.flag_controls = {}
        self.selectors = {}
        self.locked = False
        options = dict(context.options)
        flags = ttk.Frame(self)
        flags.grid(row=0, column=0, sticky="w")
        for key in flag_keys(context):
            variable = tk.BooleanVar(self, value=options.get(key, False))
            self.variables[key] = variable
            widget = ttk.Checkbutton(flags, text=field_label(key), variable=variable, command=self._change_options)
            widget.pack(side="left", padx=(0, CONTROL_GROUP_GAP), pady=CONTROL_ROW_PADY)
            self.controls.append(widget)
            self.flag_controls[key] = widget
        if context.kind.startswith("en_"):
            choices = ("reversible", "cooling_only" if context.kind == "en_seer" else "heating_only")
            variable = tk.StringVar(self, value=dict(context.values)["appliance_type"])
            self._selector("appliance_type", "Type", variable, choices,
                           CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS,
                           lambda _event: values_changed({"appliance_type": variable.get()}))
        if context.kind == "hspf2" and context.product != "variable_capacity":
            variable = tk.StringVar(self, value=options.get("defrost_mode", "explicit_override"))
            self.variables["defrost_mode"] = variable
            self._selector("defrost_mode", "Defrost", variable,
                           ("none", "explicit_override", "calculated_from_timing"),
                           CONTROL_DETAIL_SERIES_SELECTOR_WIDTH_CHARS, lambda _event: self._change_options())

    def _selector(self, key, label, variable, choices, width, callback):
        frame = ttk.Frame(self)
        frame.grid(row=1, column=0, sticky="w", pady=(0, CONTROL_ROW_PADY))
        ttk.Label(frame, text=label).pack(side="left", padx=(0, CONTROL_LABEL_GAP))
        widget = ttk.Combobox(frame, textvariable=variable, values=choices, state="readonly", width=width)
        widget.pack(side="left")
        widget.bind("<<ComboboxSelected>>", callback)
        self.controls.append(widget)
        self.selectors[key] = widget

    def _change_options(self):
        if not self.locked:
            self.options_changed({**dict(self.context.options), **{key: var.get() for key, var in self.variables.items()}})

    def refresh(self, points, *, locked):
        self.locked = locked
        derived = {}
        if self.context.product == "triple_capacity_northern":
            derived = {"measured_" + point.key.lower().replace("low", "_low"): point.independent
                       for point in points if point.key in ("H2Low", "H3Low")}
        for key, widget in self.flag_controls.items():
            if key in derived:
                self.variables[key].set(derived[key])
            widget.state(["disabled" if locked or key in derived else "!disabled"])
        for widget in self.selectors.values():
            widget.configure(state="disabled" if locked else "readonly")
