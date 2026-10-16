"""Inline settings using the main calculator's matrix and control widgets."""
from tkinter import ttk

from apps.calculator.ui.layout_constants import (
    CONTROL_ROW_PADY, CONTROL_GROUP_GAP, ISO_SECTION_BLOCK_GAP,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from .options import OptionsPanel
from .setting_specs import numeric_groups
from .table_controller import CombinationTableController


def inactive_fields(context):
    """Mirror the originating setting controls' conditional editability."""
    options = dict(context.options)
    inactive = set()
    if context.kind == "m_hspf":
        if not options.get("demand_defrost"):
            inactive.update(("defrost_test_minutes", "defrost_max_minutes"))
        if not options.get("automatic_cutout"):
            inactive.update(("cut_out_c", "cut_in_c"))
    if context.kind == "seer2" and not options.get("low_stage_lockout_enabled"):
        inactive.add("low_stage_lockout_temp_f")
    if context.kind == "hspf2" and context.product != "variable_capacity":
        mode = options.get("defrost_mode", "explicit_override")
        if mode != "explicit_override":
            inactive.add("defrost_factor")
        if mode != "calculated_from_timing":
            inactive.update(("defrost_t_test_minutes", "defrost_t_max_minutes"))
        if not options.get("low_stage_lockout_enabled"):
            inactive.add("low_stage_lockout_temp_c")
    return inactive


class SettingsPanel(ttk.Frame):
    def __init__(self, parent, session, *, viewport, changed, options_changed):
        super().__init__(parent)
        self.session, self.changed = session, changed
        self.locked = False
        self.tables = []
        self.field_tables = {}
        self.controllers = []
        self._readonly = {}
        self.options = None
        row = 0
        if not session.context.kind.startswith("en_"):
            self.options = OptionsPanel(self, session.context, changed, options_changed)
            if self.options.controls:
                self.options.grid(row=row, column=0, sticky="w", pady=(0, CONTROL_ROW_PADY))
                row += 1
        values = dict(session.context.values)
        for spec in numeric_groups(session.context):
            inline = session.context.kind == "seer2" and session.context.product == "dual_stage"
            if inline:
                group = self.options.numeric_parent
            else:
                group = ttk.LabelFrame(self, text=spec.title) if spec.title else ttk.Frame(self)
                group.grid(row=row, column=0, sticky="w", pady=(0, CONTROL_ROW_PADY))
            table = MetricInputTable(
                group, columns=spec.columns,
                rows=(("value", spec.row_label),),
                editable_cells={("value", key): key for key, _ in spec.columns if key in values},
                row_header_chars=spec.row_chars, data_column_chars=spec.data_chars,
                viewport=viewport,
            )
            if inline:
                table.pack(side="left", padx=(0, CONTROL_ROW_PADY), pady=CONTROL_ROW_PADY)
            else:
                table.grid(row=0, column=0, sticky="w", padx=CONTROL_ROW_PADY if spec.title else 0,
                           pady=CONTROL_ROW_PADY if spec.title else 0)
            if spec.type_selector:
                self.options = OptionsPanel(group, session.context, changed, options_changed)
                self.options.grid(row=0, column=1, sticky="w", padx=(CONTROL_GROUP_GAP, CONTROL_ROW_PADY))
            table.locked = False
            table.set_values_batch({key: values[key] for key in table.field_order})
            table.set_values_changed_callback(self._numeric_changed)
            self.tables.append(table)
            self.field_tables.update({key: table for key in table.field_order})
            self.controllers.append(CombinationTableController(table))
            if not inline:
                row += 1
        if self.options is None:
            self.options = OptionsPanel(self, session.context, changed, options_changed)
        self.has_fields = bool(row)
        if self.has_fields:
            ttk.Separator(self).grid(row=row, column=0, sticky="ew", pady=(0, ISO_SECTION_BLOCK_GAP))

    def _numeric_changed(self):
        if not self.locked:
            self.changed({key: value for table in self.tables for key, value in table.get_text_values().items()})

    def commit(self):
        for controller in self.controllers:
            controller._commit_edit()

    def refresh(self, points):
        self.options.refresh(points, context=self.session.context, locked=self.locked)
        inactive = inactive_fields(self.session.context)
        for table, controller in zip(self.tables, self.controllers):
            table.locked = self.locked
            readonly = frozenset(address for address, key in table.editable_cells.items()
                                 if self.locked or key in inactive)
            display = {address: "" for address, key in table.editable_cells.items() if key in inactive}
            if self.session.context.kind == "m_hspf":
                display.update({address: "N/A" if key.startswith("defrost_") else "No cutout"
                                for address, key in table.editable_cells.items() if key in inactive})
                table.set_static_text(("value", "defrost_credit"), self._defrost_credit_text())
            state = (readonly, display)
            if self._readonly.get(table) != state:
                table.set_readonly_addresses(readonly, display_values=display)
                controller.refresh()
                self._readonly[table] = state

    def _defrost_credit_text(self):
        if not dict(self.session.context.options).get("demand_defrost"):
            return "1.000"
        run = self.session.run
        if run is not None and not self.session.stale and run.status != "running":
            score = next((row.score for row in run.results if row.score is not None), None)
            value = dict(score.summary).get("f_def") if score else None
            if value is not None:
                return f"{value:.3f}"
        return "계산 대기"

    def lock(self, locked, points):
        self.locked = locked
        self.refresh(points)
