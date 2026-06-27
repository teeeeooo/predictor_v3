import json
from pathlib import Path

from core.calculators.standards.ahri_seer2 import (
    AHRICalculator,
    get_default_ahri_seer2_config,
)


def test_import_does_not_create_root_usa_json():
    assert not Path("usa.json").exists()


def test_default_ahri_seer2_config_smoke(tmp_path):
    config_path = tmp_path / "usa_seer2.json"
    config_path.write_text(
        json.dumps(get_default_ahri_seer2_config()),
        encoding="utf-8",
    )
    calculator = AHRICalculator(str(config_path))

    result = calculator.calculate_seer2(
        {
            "A_Full": (36000, 3000),
            "B_Full": (30000, 2200),
            "B_Low": (18000, 1200),
            "E_Int": (24000, 1700),
            "F_Low": (12000, 900),
        }
    )

    assert result["SEER2"] == 13.677
    assert result["EER2_A_Full"] == 12.0
    assert result["EER2_B_Low"] == 15.0
    assert result["total_cooling_Btu"] == 11961.491
    assert result["total_energy_Wh"] == 874.552
    assert result["system_type"] == "HP"
    assert len(result["bin_details"]) == 8
