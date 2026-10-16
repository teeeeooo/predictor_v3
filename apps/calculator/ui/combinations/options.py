"""Main-page selectors and flags, bound to the current combination draft."""
import tkinter as tk
from tkinter import ttk
from apps.calculator.ui.ahri.settings_presentation import DEFROST_CHOICES
from apps.calculator.ui.layout_constants import (
    CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS, CONTROL_DEFROST_SELECTOR_WIDTH_CHARS,
    CONTROL_GROUP_GAP, CONTROL_LABEL_GAP, CONTROL_ROW_PADY, CONTROL_COMPACT_GAP,
)
from .setting_specs import flag_groups


class OptionsPanel(ttk.Frame):
    def __init__(self, parent, context, values_changed, options_changed):
        super().__init__(parent)
        self.context, self.options_changed = context, options_changed
        self.controls, self.variables, self.flag_controls, self.selectors = [], {}, {}, {}
        self.locked = False
        options = dict(context.options)
        title, groups = flag_groups(context)
        host = ttk.LabelFrame(self, text=title) if title else ttk.Frame(self)
        host.pack(side="left")
        self.numeric_parent = host
        if context.kind == "m_hspf" or (context.kind == "hspf2" and context.product == "variable_capacity"):
            ttk.Label(host, text="Region: IV").pack(side="left", padx=(CONTROL_ROW_PADY, CONTROL_GROUP_GAP))
        for group_label, fields in groups:
            if group_label:
                ttk.Label(host, text=group_label).pack(side="left", padx=(CONTROL_ROW_PADY, CONTROL_COMPACT_GAP))
            for key, label in fields:
                variable = tk.BooleanVar(self, value=options.get(key, False))
                self.variables[key] = variable
                widget = ttk.Checkbutton(host, text=label, variable=variable, command=self._change_options)
                widget.pack(side="left", padx=(0, CONTROL_COMPACT_GAP), pady=CONTROL_ROW_PADY)
                self.controls.append(widget)
                self.flag_controls[key] = widget
        if context.kind.startswith("en_"):
            choices = ("reversible", "cooling_only" if context.kind == "en_seer" else "heating_only")
            variable = tk.StringVar(self, value=dict(context.values)["appliance_type"])
            self._selector(host, "appliance_type", "Type", variable, choices,
                           CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS,
                           lambda _event: values_changed({"appliance_type": variable.get()}))
        if context.kind == "hspf2" and context.product != "variable_capacity":
            variable = tk.StringVar(self, value=options.get("defrost_mode", "explicit_override"))
            self.variables["defrost_mode"] = variable
            self._selector(host, "defrost_mode", "Defrost", variable, DEFROST_CHOICES,
                           CONTROL_DEFROST_SELECTOR_WIDTH_CHARS, lambda _event: self._change_options())

    def _selector(self, parent, key, label, variable, choices, width, callback):
        ttk.Label(parent, text=label).pack(side="left", padx=(CONTROL_GROUP_GAP, CONTROL_LABEL_GAP))
        widget = ttk.Combobox(parent, textvariable=variable, values=choices, state="readonly", width=width)
        widget.pack(side="left", padx=(0, CONTROL_ROW_PADY), pady=CONTROL_ROW_PADY)
        widget.bind("<<ComboboxSelected>>", callback)
        self.controls.append(widget)
        self.selectors[key] = widget

    def _change_options(self):
        if not self.locked:
            self.options_changed({**dict(self.context.options), **{key: var.get() for key, var in self.variables.items()}})

    def refresh(self, points, *, context, locked):
        self.context, self.locked = context, locked
        derived = {}
        if context.product == "triple_capacity_northern":
            keys = {"H2Low": "measured_h2_low", "H3Low": "measured_h3_low"}
            derived = {keys[point.key]: point.independent for point in points if point.key in keys}
        for key, widget in self.flag_controls.items():
            self.variables[key].set(derived.get(key, dict(context.options).get(key, False)))
            widget.state(["disabled" if locked or key in derived else "!disabled"])
        for widget in self.selectors.values():
            widget.configure(state="disabled" if locked else "readonly")
