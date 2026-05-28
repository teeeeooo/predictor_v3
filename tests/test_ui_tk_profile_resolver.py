"""Pure-Python tests for ``ui_tk.profile_resolver``.

The resolver must be importable without Tkinter or PyQt. These tests
guard the UI label → ``profile_id`` boundary that keeps ``profile_id`` /
``calculator_id`` / ``config_path`` out of the UI.
"""

import importlib
import sys

import pytest

from ui_tk import profile_resolver


def test_region_labels_contains_hong_kong():
    assert "Hong Kong" in profile_resolver.region_labels()


def test_calculation_mode_labels_keep_2point_default_then_hong_kong_profile():
    assert profile_resolver.calculation_mode_labels() == (
        "ISO / ISEER 2-point",
        "Hong Kong",
    )


def test_supported_metrics_for_hong_kong_label():
    assert profile_resolver.supported_metrics_for("Hong Kong") == ("CSPF", "HSPF")


def test_supported_metrics_for_internal_key():
    assert profile_resolver.supported_metrics_for("hong_kong") == ("CSPF", "HSPF")


def test_supported_metrics_for_unknown_returns_empty():
    assert profile_resolver.supported_metrics_for("Atlantis") == ()


def test_resolve_profile_id_hong_kong_cspf():
    assert profile_resolver.resolve_profile_id("Hong Kong", "CSPF") == "hong_kong_cspf"


def test_resolve_profile_id_hong_kong_hspf():
    assert profile_resolver.resolve_profile_id("Hong Kong", "HSPF") == "hong_kong_hspf"


def test_resolve_profile_id_accepts_internal_key():
    assert profile_resolver.resolve_profile_id("hong_kong", "CSPF") == "hong_kong_cspf"


def test_resolve_profile_id_case_insensitive_metric():
    assert profile_resolver.resolve_profile_id("Hong Kong", "cspf") == "hong_kong_cspf"
    assert profile_resolver.resolve_profile_id("Hong Kong", "Hspf") == "hong_kong_hspf"


def test_resolve_profile_id_unsupported_raises():
    with pytest.raises(ValueError):
        profile_resolver.resolve_profile_id("Korea", "CSPF")


def test_resolve_profile_id_unsupported_metric_raises():
    with pytest.raises(ValueError):
        profile_resolver.resolve_profile_id("Hong Kong", "SEER")


def test_two_point_profile_labels_are_user_visible():
    assert profile_resolver.two_point_profile_labels() == (
        "ISO 16358-1",
        "India ISEER",
    )


def test_resolve_two_point_profile_ids_from_display_labels():
    assert (
        profile_resolver.resolve_two_point_profile_id("ISO 16358-1")
        == "iso_t1_default_2point_cspf"
    )
    assert (
        profile_resolver.resolve_two_point_profile_id("India ISEER")
        == "india_iseer_cspf"
    )


def test_resolve_two_point_profile_id_unsupported_raises():
    with pytest.raises(ValueError):
        profile_resolver.resolve_two_point_profile_id("SASO T3")


def test_resolver_module_does_not_require_tkinter_or_pyqt():
    """Re-import the resolver after removing tkinter / PyQt5 from
    ``sys.modules`` and ensure the import path itself does not pull
    those modules back in."""
    # Drop anything already cached so importlib reloads cleanly.
    for name in list(sys.modules):
        if name.startswith("tkinter") or name.startswith("PyQt5") or name == "ui_tk.profile_resolver":
            del sys.modules[name]

    importlib.import_module("ui_tk.profile_resolver")

    tkinter_loaded = any(
        name == "tkinter" or name.startswith("tkinter.") for name in sys.modules
    )
    pyqt_loaded = any(name.startswith("PyQt5") for name in sys.modules)
    assert not tkinter_loaded, "profile_resolver must not import tkinter"
    assert not pyqt_loaded, "profile_resolver must not import PyQt5"
