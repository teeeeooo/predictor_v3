"""Shared spreadsheet controller for inputs locked during a combination run."""
from apps.calculator.ui.table.controller import TkTableController


class CombinationTableController(TkTableController):
    def _undo_last(self, event=None):
        if self.table.locked:
            return "break"
        return super()._undo_last(event)
