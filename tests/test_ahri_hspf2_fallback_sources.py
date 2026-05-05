from core.calculator_ahri_hspf2 import AHRIHSPF2Calculator


def calculator():
    return AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")


def canonical_points():
    return {
        "H01": (12500, 980),
        "H11": (12000, 1000),
        "H12": (24000, 2200),
        "H1N": (22000, 2000),
        "H22": (23200, 2160),
        "H2Int": (13000, 1200),
        "H32": (22000, 2100),
        "H42": (18000, 1900),
        "A_Full": (24000, 2500),
    }


def ahri_kwargs(**overrides):
    kwargs = {
        "t_off": -10,
        "t_on": -5,
        "defrost_t_test_minutes": 90,
        "defrost_t_max_minutes": 720,
    }
    kwargs.update(overrides)
    return kwargs


def metadata_for(points, **kwargs):
    result = calculator().calculate_hspf2_v3(points, **ahri_kwargs(**kwargs))
    return result["summary"]["metadata"]


def test_hspf2_v3_h12_tested_source_metadata():
    metadata = metadata_for(canonical_points())

    assert metadata["h12_source"] == "tested"


def test_hspf2_v3_h12_eq_11_183_source_metadata():
    points = canonical_points()
    points.pop("H12")

    metadata = metadata_for(points, h1n_same_speed_as_h3=True)

    assert metadata["h12_source"] == "eq_11_183"


def test_hspf2_v3_h12_eq_11_185_source_metadata():
    points = canonical_points()
    points.pop("H12")

    metadata = metadata_for(points, h1n_same_speed_as_h3=False)

    assert metadata["h12_source"] == "eq_11_185"


def test_hspf2_v3_h22_tested_source_metadata():
    metadata = metadata_for(canonical_points())

    assert metadata["h22_source"] == "tested"


def test_hspf2_v3_h22_eq_11_44_11_50_source_metadata():
    points = canonical_points()
    points.pop("H22")

    metadata = metadata_for(points)

    assert metadata["h22_source"] == "eq_11_44_11_50"
