"""Repeatable native Tk resize/page probe; run as a module from the repo root.

python -m tests.apps.calculator.performance.benchmark --output /tmp/calculator.json

Requires a native desktop and a Python build with Tk. Measures geometry + event
flush latency, not physical mouse-drag FPS. Calculation is completed before UI
timing. Keep Python/Tk, display, window size and repeats the same for comparisons.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
import platform
from pathlib import Path
from statistics import mean, median, quantiles
import subprocess
from time import perf_counter
import tkinter as tk

from apps.calculator.application.combinations.adapters import StandardAdapter, seed_session
from apps.calculator.application.combinations.models import Candidate
from apps.calculator.application.combinations.service import start
from apps.calculator.ui.calculator_app import CalculatorTkApp
from apps.calculator.ui.combinations.manager import CombinationManager
from apps.calculator.ui.theme import apply_calculator_theme
from tests.apps.calculator.combinations.seeds import contexts


def descendants(widget):
    yield widget
    for child in widget.winfo_children():
        yield from descendants(child)


def summary(samples):
    return dict(mean_ms=round(mean(samples), 3), p50_ms=round(median(samples), 3),
                p95_ms=round(quantiles(samples, n=100, method="inclusive")[94], 3),
                samples_ms=[round(value, 3) for value in samples])


def measure(root, window, repeats):
    def resize(width, height):
        window.geometry(f"{width}x{height}")
        root.update()

    window.geometry("800x650+50+50")
    window.deiconify()
    root.update()
    # Warm up both axes before recording, including the first native draw.
    for i in range(12):
        resize(800 + (i % 3)*8, 650 + (i % 2)*8)
    report = {}
    for axis in ("width", "height"):
        samples = []
        for _ in range(repeats):
            for i in (*range(1, 7), *range(5, -1, -1)):
                width, height = (800+i*8, 650) if axis == "width" else (800, 650+i*8)
                before = perf_counter()
                resize(width, height)
                samples.append((perf_counter()-before)*1000)
        report[axis] = summary(samples)
    widgets = tuple(descendants(window))
    report["widgets"] = len(widgets)
    report["mapped_widgets"] = sum(bool(w.winfo_ismapped()) for w in widgets)
    report["canvas_items"] = sum(len(w.find_all()) for w in widgets if isinstance(w, tk.Canvas))
    return report


def combination_cases():
    available = contexts()
    ahri = next(c for c in available if c.product == "triple_capacity_northern")
    ahri = replace(ahri, values=tuple({**dict(ahri.values), "low_min_c": "0"}.items()),
                   options=tuple({**dict(ahri.options), "measured_h2_boost": True}.items()))
    return (("combo_iso_initial", available[0], (3, 5), False),
            ("combo_iso_15", available[0], (3, 5), True),
            ("combo_iso_10000", available[0], (100, 100), True),
            ("combo_ahri_10000", ahri, (10, 10, 10, 10), True))


def run(root, repeats, selected):
    reports = []

    def record(name, window, **extra):
        report = dict(case=name, **extra, **measure(root, window, repeats))
        reports.append(report)
        print(json.dumps({k: v for k, v in report.items() if k not in ("width", "height")}
                         | {axis: {k: v for k, v in report[axis].items() if k != "samples_ms"}
                            for axis in ("width", "height")}), flush=True)
        return report

    main_cases = ("main_iso", "main_en_scop", "main_ahri_hspf2")
    if not selected or any(name in selected for name in main_cases):
        app = CalculatorTkApp(root)
        root.update()
        for name in main_cases:
            if selected and name not in selected:
                continue
            if name == "main_en_scop":
                app.notebook.select(app.en14825_tab)
                app.en14825_tab._standard_notebook.select(app.en14825_tab._scop_frame)
            elif name == "main_ahri_hspf2":
                app.notebook.select(app.ahri210240_tab)
                app.ahri210240_tab.metric_notebook.select(app.ahri210240_tab.hspf2_frame)
            root.update()
            record(name, root)
        app.notebook.destroy()
        root.withdraw()
        root.update()

    adapter = StandardAdapter()
    for name, context, counts, completed in combination_cases():
        if selected and name not in selected:
            continue
        session = seed_session(context, adapter)
        points = [point for point in adapter.points(context) if point.independent]
        for point, count in zip(points, counts):
            original = session.pools[point.key][0]
            session.pools[point.key] = [Candidate(capacity=original.capacity, power=original.power)
                                       for _ in range(count)]
        if completed:
            result = start(session, adapter)
            while result.status == "running":
                result.step()
            assert result.failed == 0
        manager = CombinationManager(root, lambda: [context])
        manager.sessions[context.identity] = session
        before = perf_counter()
        manager.open()
        root.update()
        open_ms = (perf_counter()-before)*1000
        shell = manager.handle.dialog
        panel = shell._adapter.results
        report = record(name, shell.window, open_ms=round(open_ms, 3),
                        result_count=len(session.run.results) if session.run else 0,
                        independent_points=len(points))
        if session.run and len(session.run.results) > 100:
            samples = []
            for page in range(1, 11):
                before = perf_counter()
                panel.page = page
                panel.refresh()
                root.update()
                samples.append((perf_counter()-before)*1000)
            report["page"] = summary(samples)
            print(json.dumps(dict(case=name, page={k: v for k, v in report["page"].items()
                                                   if k != "samples_ms"})), flush=True)
        manager.handle.dispose()
        root.update()
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--case", action="append", choices=("main_iso", "main_en_scop", "main_ahri_hspf2",
                        *(case[0] for case in combination_cases())))
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    root = tk.Tk()
    root.withdraw()
    apply_calculator_theme(root)  # Also when --case selects only a dialog.
    errors = []
    root.report_callback_exception = lambda *error: errors.append(repr(error))
    try:
        report = dict(platform=platform.platform(), python=platform.python_version(),
                      tk=root.tk.call("info", "patchlevel"), scaling=root.tk.call("tk", "scaling"),
                      screen=[root.winfo_screenwidth(), root.winfo_screenheight()], repeats=args.repeats,
                      revision=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                      dirty=bool(subprocess.check_output(["git", "status", "--porcelain"], text=True)),
                      cases=run(root, args.repeats, args.case), callback_errors=errors)
        args.output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
        assert not errors, errors
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
