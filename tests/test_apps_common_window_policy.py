"""Focused tests for shared PySide initial-window placement policy."""

import pytest

from apps.common.ui.window_policy import initial_window_rect


def test_initial_window_rect_centers_and_caps_to_available_work_area():
    target = initial_window_rect(
        (1800, 1200),
        (0, 24, 1440, 876),
    )

    assert target.width == int(1440 * 0.86)
    assert target.height == int(876 * 0.82)
    assert target.x == (1440 - target.width) // 2
    assert target.y == 24 + (876 - target.height) // 2


def test_initial_window_rect_preserves_negative_monitor_origin():
    target = initial_window_rect(
        (1200, 760),
        (-1920, 0, 1920, 1080),
    )

    assert target == type(target)(-1560, 160, 1200, 760)


@pytest.mark.parametrize("ratio", (0, -0.1, 1.1))
def test_initial_window_rect_rejects_invalid_cap_ratio(ratio):
    with pytest.raises(ValueError, match="window cap ratios"):
        initial_window_rect(
            (1200, 760),
            (0, 0, 1920, 1080),
            max_width_ratio=ratio,
        )
