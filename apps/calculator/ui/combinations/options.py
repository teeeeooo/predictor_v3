"""Context option controls; a measurement-mode change selects another session."""
import tkinter as tk
from tkinter import ttk
from .presentation import field_label


class OptionsPanel(ttk.Frame):
    def __init__(self, parent, manager, context):
        super().__init__(parent)
        self.controls = []
        self.variables = {}
        self.context = context
        for index, (key, value) in enumerate(context.options):
            if isinstance(value, bool) and key != "measured_h3_low":
                variable = tk.BooleanVar(self, value=value)
                self.variables[key] = variable
                widget = ttk.Checkbutton(self, text=field_label(key), variable=variable,
                                         command=lambda: manager.change_options({**dict(context.options), **{k:v.get() for k,v in self.variables.items()}}))
                self.controls.append(widget)
            else:
                widget = ttk.Label(self, text=f"{field_label(key)}: {value}")
            widget.grid(row=index//3, column=index%3, sticky="w")
        ttk.Label(self, text="시험 모드 변경은 별도 세션에 보관됩니다. H3Low는 운전 범위에서 자동 결정됩니다.").grid(row=len(context.options)//3+1, column=0, columnspan=3, sticky="w")

    def lock(self, locked):
        for widget in self.controls:
            widget.state(["disabled" if locked else "!disabled"])
