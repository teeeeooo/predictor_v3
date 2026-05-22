"""Tkinter calculator-only UI — feasibility spike.

This module is the FIRST cut of a lightweight calculator-only UI shell.
It is intentionally minimal and does NOT replace ``ui/calc_window.py``
or ``app_calculator.py``. Goals:

- Run on stdlib Tkinter (no PyQt5 import anywhere in this module).
- Reach the existing core calculator via
  ``core.calculator_dispatcher.create_calculator_for_profile``.
- Wire the ISO 16358 tab with a Hong Kong region selector and render
  both CSPF and HSPF metric sections together (see
  ``docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md``).

If you are looking for the production / reference PyQt calculator UI,
see ``ui/calc_window.py`` and ``app_calculator.py``. That code remains
the source of truth until the lightweight direction is decided.
"""

from __future__ import annotations

from typing import Callable, Dict, Mapping, Optional, Tuple

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile


REGION_BY_LABEL: Dict[str, str] = {
    "Hong Kong": "hong_kong",
}


METRIC_SECTIONS_BY_REGION: Dict[str, Tuple[str, ...]] = {
    "hong_kong": ("CSPF", "HSPF"),
}


def resolve_profile_id(region: str, metric: str) -> str:
    """Map (region, metric_section) → profile_id without exposing the
    routing concept in the UI.

    ``region`` is either the display label (``"Hong Kong"``) or the
    internal key (``"hong_kong"``); ``metric`` is the section name
    (``"CSPF"`` / ``"HSPF"``).

    Raises ``ValueError`` for combinations the spike does not wire.
    """
    region_key = REGION_BY_LABEL.get(region, region).casefold()
    metric_key = metric.casefold()

    if region_key == "hong_kong" and metric_key == "cspf":
        return "hong_kong_cspf"
    if region_key == "hong_kong" and metric_key == "hspf":
        return "hong_kong_hspf"

    raise ValueError(
        f"Unsupported (region, metric) pair for MVP: ({region!r}, {metric!r})"
    )


class _NumericEntryRow:
    """One labeled numeric entry. Returns ``None`` if blank."""

    def __init__(self, parent: tk.Widget, label: str, *, width: int = 12) -> None:
        self._frame = ttk.Frame(parent)
        ttk.Label(self._frame, text=label, width=22, anchor="w").pack(side=tk.LEFT)
        self._entry = ttk.Entry(self._frame, width=width)
        self._entry.pack(side=tk.LEFT)

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def get_value(self, *, allow_empty: bool = False) -> Optional[float]:
        text = self._entry.get().strip().replace(",", "")
        if not text:
            if allow_empty:
                return None
            raise ValueError("값이 비어 있습니다.")
        return float(text)

    def set_value(self, text: str) -> None:
        self._entry.delete(0, tk.END)
        self._entry.insert(0, text)


class _CspfSection:
    """Hong Kong CSPF section — 35_full / 35_half capacity + power.

    Matches the ``"measure"`` points declared in
    ``data/region_configs/hong_kong.json``.
    """

    def __init__(self, parent: tk.Widget, on_result: Callable[[str], None]) -> None:
        self._on_result = on_result
        self._frame = ttk.LabelFrame(parent, text="CSPF (Hong Kong)")

        self._declared = _NumericEntryRow(self._frame, "정격 능력 [W]")
        self._declared.set_value("3500")
        self._declared.grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=2)

        self._full_cap = _NumericEntryRow(self._frame, "35_full 능력 [W]")
        self._full_cap.set_value("3600")
        self._full_cap.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self._full_pow = _NumericEntryRow(self._frame, "35_full 전력 [W]")
        self._full_pow.set_value("900")
        self._full_pow.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        self._half_cap = _NumericEntryRow(self._frame, "35_half 능력 [W]")
        self._half_cap.set_value("1700")
        self._half_cap.grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self._half_pow = _NumericEntryRow(self._frame, "35_half 전력 [W]")
        self._half_pow.set_value("380")
        self._half_pow.grid(row=2, column=1, sticky="w", padx=4, pady=2)

        ttk.Button(self._frame, text="CSPF 계산", command=self._on_calculate).grid(
            row=3, column=0, sticky="w", padx=4, pady=4
        )

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def _read_inputs(self) -> Tuple[Mapping[str, Mapping[str, float]], float]:
        measured = {
            "35_full": {
                "capacity": self._full_cap.get_value(),
                "power": self._full_pow.get_value(),
            },
            "35_half": {
                "capacity": self._half_cap.get_value(),
                "power": self._half_pow.get_value(),
            },
        }
        declared = self._declared.get_value()
        return measured, declared

    def _on_calculate(self) -> None:
        try:
            measured, declared = self._read_inputs()
            calc = create_calculator_for_profile(profile_id=resolve_profile_id("Hong Kong", "CSPF"))
            result = calc.calculate_cspf(measured, declared_capacity=declared)
        except Exception as exc:
            self._on_result(f"[CSPF 오류] {type(exc).__name__}: {exc}")
            return
        cspf = result.get("cspf")
        cstl = result.get("cstl_wh", result.get("cstl"))
        csec = result.get("csec_wh", result.get("csec"))
        self._on_result(
            "[CSPF]\n"
            f"  CSPF = {cspf}\n"
            f"  CSTL = {cstl}\n"
            f"  CSEC = {csec}"
        )


class _HspfSection:
    """Hong Kong HSPF section — rated heating capacity + 7_full / 7_half.

    Mirrors the inputs used by
    ``tests/test_iso16358_hspf_hong_kong_config.py`` (golden case 1).
    """

    def __init__(self, parent: tk.Widget, on_result: Callable[[str], None]) -> None:
        self._on_result = on_result
        self._frame = ttk.LabelFrame(parent, text="HSPF (Hong Kong)")

        self._rated = _NumericEntryRow(self._frame, "정격 난방 능력 [W]")
        self._rated.set_value("6300")
        self._rated.grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=2)

        self._full_cap = _NumericEntryRow(self._frame, "7_full 능력 [W]")
        self._full_cap.set_value("6300")
        self._full_cap.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self._full_pow = _NumericEntryRow(self._frame, "7_full 전력 [W]")
        self._full_pow.set_value("1500")
        self._full_pow.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        self._half_cap = _NumericEntryRow(self._frame, "7_half 능력 [W]")
        self._half_cap.set_value("3200")
        self._half_cap.grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self._half_pow = _NumericEntryRow(self._frame, "7_half 전력 [W]")
        self._half_pow.set_value("800")
        self._half_pow.grid(row=2, column=1, sticky="w", padx=4, pady=2)

        ttk.Button(self._frame, text="HSPF 계산", command=self._on_calculate).grid(
            row=3, column=0, sticky="w", padx=4, pady=4
        )

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def _read_inputs(self) -> Mapping[str, object]:
        return {
            "rated_heating_capacity": self._rated.get_value(),
            "7_full": {
                "capacity": self._full_cap.get_value(),
                "power": self._full_pow.get_value(),
            },
            "7_half": {
                "capacity": self._half_cap.get_value(),
                "power": self._half_pow.get_value(),
            },
        }

    def _on_calculate(self) -> None:
        try:
            measured = self._read_inputs()
            calc = create_calculator_for_profile(profile_id=resolve_profile_id("Hong Kong", "HSPF"))
            result = calc.calculate_hspf(measured)
        except Exception as exc:
            self._on_result(f"[HSPF 오류] {type(exc).__name__}: {exc}")
            return
        hspf = result.get("hspf")
        hstl = result.get("hstl_wh")
        hsec = result.get("hsec_wh")
        self._on_result(
            "[HSPF]\n"
            f"  HSPF = {hspf}\n"
            f"  HSTL_Wh = {hstl}\n"
            f"  HSEC_Wh = {hsec}"
        )


class _ResultPanel:
    """Read-only multi-line result text + copy-to-clipboard button."""

    def __init__(self, parent: tk.Widget) -> None:
        self._frame = ttk.LabelFrame(parent, text="결과")
        self._text = tk.Text(self._frame, height=10, width=60, wrap="word")
        self._text.configure(state=tk.DISABLED)
        self._text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)
        ttk.Button(self._frame, text="결과 복사", command=self._copy).pack(
            side=tk.LEFT, padx=4, pady=4
        )
        ttk.Button(self._frame, text="결과 지우기", command=self.clear).pack(
            side=tk.LEFT, padx=4, pady=4
        )

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def append(self, text: str) -> None:
        self._text.configure(state=tk.NORMAL)
        if self._text.get("1.0", tk.END).strip():
            self._text.insert(tk.END, "\n")
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)

    def clear(self) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.configure(state=tk.DISABLED)

    def _copy(self) -> None:
        contents = self._text.get("1.0", tk.END).rstrip()
        if not contents:
            return
        widget = self._text
        widget.clipboard_clear()
        widget.clipboard_append(contents)


class _Iso16358Tab(ttk.Frame):
    """ISO 16358 standard tab.

    MVP wires one region (Hong Kong). Selecting the region shows the
    metric sections that region supports — for Hong Kong, both CSPF
    and HSPF appear in the same screen (per the IA decision in the
    feasibility design doc).
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        region_row = ttk.Frame(self)
        region_row.pack(side=tk.TOP, anchor="w", padx=4, pady=4)
        ttk.Label(region_row, text="지역").pack(side=tk.LEFT, padx=(0, 4))
        self._region_combo = ttk.Combobox(
            region_row,
            values=list(REGION_BY_LABEL.keys()),
            state="readonly",
            width=20,
        )
        self._region_combo.set("Hong Kong")
        self._region_combo.pack(side=tk.LEFT)
        self._region_combo.bind("<<ComboboxSelected>>", self._on_region_changed)

        self._sections_holder = ttk.Frame(self)
        self._sections_holder.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)

        self._result_panel = _ResultPanel(self)
        self._result_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._render_region("Hong Kong")

    def _on_region_changed(self, _event=None) -> None:
        label = self._region_combo.get()
        self._render_region(label)

    def _render_region(self, label: str) -> None:
        for child in self._sections_holder.winfo_children():
            child.destroy()

        region_key = REGION_BY_LABEL.get(label)
        if region_key is None:
            return

        sections = METRIC_SECTIONS_BY_REGION.get(region_key, ())
        for metric in sections:
            if metric == "CSPF":
                section = _CspfSection(self._sections_holder, self._result_panel.append)
            elif metric == "HSPF":
                section = _HspfSection(self._sections_holder, self._result_panel.append)
            else:
                continue
            section.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)


class CalculatorTkApp:
    """Top-level Tkinter calculator app (spike).

    Construction does not call ``mainloop()``; tests can build the
    widget tree on a withdrawn root, and ``run()`` shows the window.
    """

    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        self.root = root if root is not None else tk.Tk()
        self.root.title("Calculator (Tkinter spike)")

        notebook = ttk.Notebook(self.root)
        notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.iso_tab = _Iso16358Tab(notebook)
        notebook.add(self.iso_tab, text="ISO 16358")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    CalculatorTkApp().run()


if __name__ == "__main__":
    main()
