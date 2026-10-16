"""Inline settings using the main calculator's matrix and control widgets."""
from tkinter import ttk

from apps.calculator.ui.layout_constants import (
    CONTROL_ROW_PADY, CONTROL_GROUP_GAP, ISO_SECTION_BLOCK_GAP,
    METRIC_TABLE_COMPACT_ROW_HEADER_CHARS, METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from .options import OptionsPanel
from .presentation import field_label
from .table_controller import CombinationTableController


def numeric_groups(context):
    """Keep design, power, rated capacity and stage ranges in familiar rows."""
    values = dict(context.values)
    groups = []
    if context.kind.startswith("en_"):
        design = (("p_design_c_w", "t_design_c", "cd") if context.kind == "en_seer"
                  else ("p_design_h_w", "tbiv_temp_c", "tol_temp_c", "cd"))
        groups.extend((("설계 사양", design),
                       ("보조 전력", ("p_to_w", "p_sb_w", "p_ck_w", "p_off_w"))))
    else:
        groups.append(("계산 조건", (
            "cd", "cd_low", "cd_full", "cd_boost", "defrost_credit", "cut_out_c", "cut_in_c",
            "defrost_factor", "defrost_test_minutes", "defrost_max_minutes",
            "defrost_t_test_minutes", "defrost_t_max_minutes", "low_stage_lockout_temp_f", "low_stage_lockout_temp_c",
        )))
        groups.append(("정격 냉방능력", ("declared_capacity", "rated_cooling_capacity", "a2_capacity")))
        groups.append(("운전 범위", tuple(f"{stage}_{edge}_c" for stage in ("low", "full", "boost")
                                      for edge in ("min", "max"))))
    seen = {"appliance_type"}
    for title, keys in groups:
        present = tuple(key for key in keys if key in values)
        seen.update(present)
        if present:
            yield title, present
    remaining = tuple(key for key in values if key not in seen)
    if remaining:
        yield "계산 조건", remaining


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
        for title, keys in numeric_groups(session.context):
            group = ttk.LabelFrame(self, text=title)
            group.grid(row=row, column=0, sticky="w", pady=(0, CONTROL_ROW_PADY))
            table = MetricInputTable(
                group, columns=tuple((key, field_label(key)) for key in keys),
                rows=(("value", "입력값"),), editable_cells={("value", key): key for key in keys},
                row_header_chars=METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
                data_column_chars=METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
                viewport=viewport,
            )
            table.grid(row=0, column=0, sticky="w")
            if self.options is None:
                self.options = OptionsPanel(group, session.context, changed, options_changed)
                self.options.grid(row=0, column=1, sticky="w", padx=(CONTROL_GROUP_GAP, 0))
            table.locked = False
            table.set_values_batch({key: values[key] for key in keys})
            table.set_values_changed_callback(self._numeric_changed)
            self.tables.append(table)
            self.field_tables.update({key: table for key in keys})
            self.controllers.append(CombinationTableController(table))
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
        self.options.refresh(points, locked=self.locked)
        inactive = inactive_fields(self.session.context)
        for table, controller in zip(self.tables, self.controllers):
            table.locked = self.locked
            readonly = frozenset(address for address, key in table.editable_cells.items()
                                 if self.locked or key in inactive)
            display = {address: "" for address, key in table.editable_cells.items() if key in inactive}
            state = (readonly, display)
            if self._readonly.get(table) != state:
                table.set_readonly_addresses(readonly, display_values=display)
                controller.refresh()
                self._readonly[table] = state

    def lock(self, locked, points):
        self.locked = locked
        self.refresh(points)
