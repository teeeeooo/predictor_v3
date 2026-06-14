#calculator_en14825.py

"""
EN 14825:2012 SEER/SCOP 계산 엔진
대상: Non-ducted, Air-to-Air, Variable capacity 1:1 (Reversible)
제약: numpy/pandas 금지, 순수 파이썬만 사용
참고 규격: BS EN 14825:2012 (E)
"""

import json
import os

T_DESIGN_C = 35
CD_DEFAULT = 0.25

class EN14825Calculator:
    """EN 14825:2012 SEER/SCOP 계산기"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "data", "region_configs", "en14825.json")

        self.config_path = config_path
        loaded_config = self._load_config(config_path)
        self.config, self.seer_config, self.scop_config = self._split_config(loaded_config)

    def _load_config(self, config_path: str) -> dict:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"EN14825 config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _split_config(self, config: dict) -> tuple:
        if "seer" not in config or "scop" not in config:
            raise ValueError("EN14825 config must include 'seer' and 'scop' sections.")
        return config, config["seer"], config["scop"]

    def _get_seer_design_value(self, key: str) -> float:
        try:
            return float(self.seer_config["design"][key])
        except KeyError as exc:
            raise ValueError(f"Missing SEER design config key: {key}") from exc

    def _get_seer_default_value(self, key: str) -> float:
        try:
            return float(self.seer_config["defaults"][key])
        except KeyError as exc:
            raise ValueError(f"Missing SEER default config key: {key}") from exc

    def _get_seer_test_point_temps(self) -> dict:
        point_temps = self.seer_config.get("test_point_temps", {})
        required = ("A", "B", "C", "D")
        missing = [key for key in required if key not in point_temps]
        if missing:
            raise ValueError(f"Missing SEER test point temperature(s): {missing}")
        return {key: float(point_temps[key]) for key in required}

    def _get_seer_bin_data(self) -> tuple:
        try:
            bin_data = self.seer_config["bin_data"]
            temps = bin_data["temps"]
            hours = bin_data["hours"]
        except KeyError as exc:
            raise ValueError("Missing SEER cooling bin data config.") from exc
        if len(temps) != len(hours):
            raise ValueError("SEER cooling bin temperature/hour length mismatch.")
        return temps, hours

    def _safe_div(self, num: float, den: float, fallback: float = 0.0) -> float:
        return num / den if den != 0 else fallback

    def _linear(self, x: float, x1: float, y1: float, x2: float, y2: float) -> float:
        if x1 == x2:
            return y1
        return y1 + (y2 - y1) * self._safe_div(x - x1, x2 - x1)

    def _validate_test_points(self, test_points: dict):
        """테스트 포인트 데이터의 무결성 검증 (피드백 4)"""
        required_keys = ["A", "B", "C", "D"]
        for k in required_keys:
            if k not in test_points:
                raise ValueError(f"Missing test point: {k}")
            capa, power = test_points[k]
            if capa <= 0 or power <= 0:
                raise ValueError(f"Invalid value at {k}: capa={capa}, power={power}")

    def _cooling_load_at_temp(self, tj: float, p_design_c: float, t_design_c: float) -> float:
        if p_design_c <= 0:
            raise ValueError(f"p_design_c must be > 0 for SEER calculation: {p_design_c}")
        if t_design_c == 16:
            raise ValueError("t_design_c cannot be 16°C for SEER cooling load line.")
        return max(0.0, p_design_c * (tj - 16.0) / (t_design_c - 16.0))

    def _cooling_condition_load(self, condition_temp: float, p_design_c: float, t_design_c: float) -> float:
        return self._cooling_load_at_temp(condition_temp, p_design_c, t_design_c)

    def _part_load_performance(
        self,
        capacity: float,
        power: float,
        load: float,
        cd: float,
        apply_degradation: bool = True,
    ) -> dict:
        if capacity <= 0 or power <= 0:
            raise ValueError(f"Invalid declared point: capacity={capacity}, power={power}")
        if load < 0:
            raise ValueError(f"Declared point load must not be negative: {load}")

        full_load_efficiency = capacity / power
        if apply_degradation and capacity > load:
            cr = self._safe_div(load, capacity)
            degradation_factor = max(0.0, 1.0 - cd * (1.0 - cr))
            part_load_efficiency = full_load_efficiency * degradation_factor
        else:
            cr = 1.0
            part_load_efficiency = full_load_efficiency
            degradation_factor = 1.0

        return {
            "full_load_efficiency": full_load_efficiency,
            "part_load_efficiency": part_load_efficiency,
            "cr": cr,
            "degradation_factor": degradation_factor,
        }

    def _eer_pl_at_declared_point(
        self,
        capacity: float,
        power: float,
        load: float,
        cd: float,
        apply_degradation: bool = True,
    ) -> dict:
        data = self._part_load_performance(capacity, power, load, cd, apply_degradation)
        return {
            "eer_dc": data["full_load_efficiency"],
            "eer_pl": data["part_load_efficiency"],
            "cr": data["cr"],
            "degradation_factor": data["degradation_factor"],
        }

    def _build_cooling_eerpl_points(
        self,
        test_points: dict,
        p_design_c: float,
        t_design_c: float,
        cd: float,
    ) -> list:
        point_temps = self._get_seer_test_point_temps()
        points = []
        for key in ("D", "C", "B", "A"):
            temp = float(point_temps[key])
            capacity, power = test_points[key]
            load = self._cooling_condition_load(temp, p_design_c, t_design_c)
            perf = self._eer_pl_at_declared_point(
                float(capacity),
                float(power),
                load,
                cd,
                apply_degradation=(key != "A"),
            )
            points.append({
                "key": key,
                "temp_c": temp,
                "value": perf["eer_pl"],
                "load": load,
                "capacity": float(capacity),
                "power": float(power),
                "eer_dc": perf["eer_dc"],
                "cr": perf["cr"],
                "degradation_factor": perf["degradation_factor"],
            })
        return points

    def _interpolate_from_points(
        self,
        tj: float,
        points: list,
        value_key: str = "value",
        extrapolate_upper: bool = False,
    ) -> tuple:
        if not points:
            raise ValueError("Interpolation requires at least one point.")

        ordered = sorted(points, key=lambda point: point["temp_c"])
        if tj <= ordered[0]["temp_c"]:
            point = ordered[0]
            return point[value_key], f"clamped_to_{point.get('key', point['temp_c'])}"
        if tj >= ordered[-1]["temp_c"]:
            if extrapolate_upper and len(ordered) >= 2:
                low = ordered[-2]
                high = ordered[-1]
                value = self._linear(tj, low["temp_c"], low[value_key], high["temp_c"], high[value_key])
                return value, f"extrapolated_{low.get('key', low['temp_c'])}_{high.get('key', high['temp_c'])}"
            point = ordered[-1]
            return point[value_key], f"clamped_to_{point.get('key', point['temp_c'])}"

        for i in range(len(ordered) - 1):
            low = ordered[i]
            high = ordered[i + 1]
            if low["temp_c"] <= tj <= high["temp_c"]:
                if tj == low["temp_c"]:
                    return low[value_key], f"direct_{low.get('key', low['temp_c'])}"
                if tj == high["temp_c"]:
                    return high[value_key], f"direct_{high.get('key', high['temp_c'])}"
                value = self._linear(tj, low["temp_c"], low[value_key], high["temp_c"], high[value_key])
                return value, f"linear_{low.get('key', low['temp_c'])}_{high.get('key', high['temp_c'])}"

        raise ValueError(f"Interpolation failed at Tj={tj}")

    # [버그 2 수정]: p_design_c 인자 추가 및 내부 할당 코드 삭제
    def _calculate_seer_on(
        self,
        test_points: dict,
        p_design_c: float,
        t_design_c: float,
        cd: float,
    ) -> float:
        """
        SEERon 계산 (규격 식 3)
        """
        numerator   = 0.0  # Σ(hj × Pc(Tj))
        denominator = 0.0  # Σ(hj × Pc(Tj) / EERpl(Tj))
        eer_points = self._build_cooling_eerpl_points(test_points, p_design_c, t_design_c, cd)
        bin_temps, bin_hours = self._get_seer_bin_data()

        for tj, hj in zip(bin_temps, bin_hours):
            if hj == 0:
                continue

            pc = self._cooling_load_at_temp(float(tj), p_design_c, t_design_c)
            eer_pl, _ = self._interpolate_from_points(float(tj), eer_points)

            if pc <= 0:
                continue

            if eer_pl <= 0:
                raise ValueError(f"Calculated EERpl is <= 0 at Tj={tj}")

            numerator   += hj * pc
            denominator += hj * (pc / eer_pl)

        if denominator == 0:
            raise ValueError("SEERon 계산 오류: 분모가 0입니다. test_points 값을 확인하세요.")

        return numerator / denominator

    def _get_seer_operational_hours(self, appliance_type: str) -> dict:
        operational_hours = self.seer_config.get("operational_hours", {})
        if appliance_type not in operational_hours:
            raise ValueError(
                f"Unknown SEER appliance_type: {appliance_type}. "
                f"Expected one of {sorted(operational_hours.keys())}"
            )
        return operational_hours[appliance_type]

    # [버그 1 수정]: 들여쓰기 4칸 정렬
    def calculate_seer(self, test_points: dict, p_to: float, p_sb: float, p_ck: float, p_off: float,
                       p_design_c: float, # A포인트와 분리하여 독립적으로 받음
                       t_design_c: float = None, cd: float = None, *,
                       appliance_type: str = None) -> dict:
        """
        EN 14825 SEER 계산
        """
        self._validate_test_points(test_points)
        if t_design_c is None:
            t_design_c = self._get_seer_design_value("t_design_c")
        if cd is None:
            cd = self._get_seer_default_value("degradation_coefficient")
        if appliance_type is None:
            try:
                appliance_type = self.seer_config["defaults"]["appliance_type"]
            except KeyError as exc:
                raise ValueError("Missing SEER default config key: appliance_type") from exc
        operational_hours = self._get_seer_operational_hours(appliance_type)

        # 1. 연간 냉방수요 Qc (kWh) — 입력받은 설계 부하 사용
        qc_kwh = p_design_c * operational_hours["h_ce"]
        
        # 2. SEERon 계산 — 보간 로직에 p_design_c 전달
        seer_on = self._calculate_seer_on(test_points, p_design_c, t_design_c, cd)        
       
        standby_kwh = (
            operational_hours["h_to"] * p_to
            + operational_hours["h_sb"] * p_sb
            + operational_hours["h_ck"] * p_ck
            + operational_hours["h_off"] * p_off
        )
        
        active_kwh   = qc_kwh / seer_on
        total_kwh    = active_kwh + standby_kwh
        seer = qc_kwh / total_kwh

        return {
            "seer":     round(seer, 3),
            "seer_on":  round(seer_on, 3),
            "qc_kwh":   round(qc_kwh, 2),
        }

    def _normalize_climate(self, climate: str) -> str:
        if not isinstance(climate, str):
            raise ValueError("climate must be one of: average, warmer, colder")
        climate_key = climate.strip().lower()
        aliases = {
            "avg": "average",
            "a": "average",
            "w": "warmer",
            "c": "colder",
        }
        return aliases.get(climate_key, climate_key)

    def _get_scop_climate_data(self, climate: str) -> dict:
        climate_key = self._normalize_climate(climate)
        climates = self.scop_config.get("climates", {})
        if climate_key not in climates:
            raise ValueError(f"Unknown SCOP climate: {climate}. Expected one of {sorted(climates.keys())}")

        climate_data = climates[climate_key]
        temps = climate_data.get("heating_bin_temps_c", [])
        hours = climate_data.get("heating_bin_hours", [])
        if len(temps) != len(hours):
            raise ValueError(f"SCOP climate {climate_key} bin temperature/hour length mismatch.")
        if any(h < 0 for h in hours):
            raise ValueError(f"SCOP climate {climate_key} bin hours must not contain negative values.")

        expected_total = climate_data.get("heating_bin_hours_total")
        if expected_total is not None and sum(hours) != expected_total:
            raise ValueError(
                f"SCOP climate {climate_key} bin hour total mismatch: "
                f"actual={sum(hours)}, expected={expected_total}"
            )

        return climate_data

    def _get_scop_operational_hours(self, climate: str, appliance_type: str) -> dict:
        climate_key = self._normalize_climate(climate)
        hours_by_type = self.scop_config.get("operational_hours", {})
        if appliance_type not in hours_by_type:
            raise ValueError(
                f"Unknown SCOP appliance_type: {appliance_type}. "
                f"Expected one of {sorted(hours_by_type.keys())}"
            )
        try:
            return hours_by_type[appliance_type][climate_key]
        except KeyError as exc:
            raise ValueError(f"Missing SCOP operational hours for {appliance_type}/{climate_key}") from exc

    def _get_scop_point_contract(self) -> dict:
        try:
            return self.scop_config["point_contract"]
        except KeyError as exc:
            raise ValueError("Missing SCOP point contract config.") from exc

    def _get_scop_standard_point_temps(self) -> dict:
        schema = self.scop_config.get("heating_test_point_schema", {})
        point_temps = {}
        for key in ("A", "B", "C", "D"):
            try:
                point_temps[key] = float(schema[key]["outdoor_db_c"])
            except KeyError as exc:
                raise ValueError(f"Missing SCOP schema temperature for point {key}") from exc
        return point_temps

    def _first_nonzero_heating_bin_temp(self, climate_data: dict) -> float:
        for temp, hours in zip(climate_data.get("heating_bin_temps_c", []), climate_data.get("heating_bin_hours", [])):
            if hours > 0:
                return float(temp)
        raise ValueError("SCOP climate has no nonzero heating bin hours.")

    def _parse_scop_point(self, test_points: dict, key: str) -> dict:
        if key not in test_points:
            raise ValueError(f"Missing SCOP test point: {key}")

        value = test_points[key]
        if isinstance(value, dict):
            if "capacity" not in value or "power" not in value:
                raise ValueError(f"SCOP test point {key} must include capacity and power.")
            capacity = float(value["capacity"])
            power = float(value["power"])
            temp_c = value.get("temp_c", value.get("outdoor_db_c"))
        else:
            capacity, power = value
            capacity = float(capacity)
            power = float(power)
            temp_c = None

        if capacity <= 0 or power <= 0:
            raise ValueError(f"Invalid SCOP test point {key}: capacity={capacity}, power={power}")

        return {
            "capacity": capacity,
            "power": power,
            "cop_pl": self._safe_div(capacity, power),
            "temp_c": float(temp_c) if temp_c is not None else None,
        }

    def _conditional_scop_point_required(
        self,
        temp_c: float,
        source_key: str,
        active_standard_temps: dict,
        first_nonzero_bin_temp: float,
    ) -> bool:
        if source_key is not None:
            return False
        if temp_c == first_nonzero_bin_temp:
            return True
        if temp_c < first_nonzero_bin_temp:
            upper_temps = [temp for temp in active_standard_temps.values() if temp >= first_nonzero_bin_temp]
            if not upper_temps:
                return False
            return temp_c < first_nonzero_bin_temp < min(upper_temps)
        return True

    def _resolve_scop_point_contract(
        self,
        climate_key: str,
        climate_data: dict,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        contract = self._get_scop_point_contract()
        standard_points = tuple(contract.get("standard_points", ("A", "B", "C", "D")))
        conditional_points = tuple(contract.get("conditional_points", ("TOL", "Tbiv")))
        climate_points = contract.get("climate_standard_points", {})
        active_standard_points = tuple(climate_points.get(climate_key, standard_points))

        standard_temps = self._get_scop_standard_point_temps()
        active_standard_temps = {
            key: standard_temps[key]
            for key in active_standard_points
            if key in standard_temps
        }
        resolved_temps = {key: standard_temps[key] for key in standard_points}
        resolved_temps["Tbiv"] = float(tbiv_temp_c if tbiv_temp_c is not None else climate_data["tbiv_max_c"])
        resolved_temps["TOL"] = float(tol_temp_c if tol_temp_c is not None else climate_data["tol_max_c"])

        required = list(active_standard_points)
        mapped = {}
        inactive = [key for key in standard_points if key not in active_standard_points]
        first_nonzero = self._first_nonzero_heating_bin_temp(climate_data)

        for key in conditional_points:
            temp_c = resolved_temps[key]
            source_key = None
            for point_key, point_temp in active_standard_temps.items():
                if temp_c == point_temp:
                    source_key = point_key
                    break
            if source_key is not None:
                mapped[key] = source_key
                continue
            if self._conditional_scop_point_required(temp_c, source_key, active_standard_temps, first_nonzero):
                required.append(key)
            else:
                inactive.append(key)

        curve_point_keys = tuple(
            key for key in required
            if key in standard_points or key in conditional_points
        )
        return {
            "active_standard_points": active_standard_points,
            "required_independent_points": tuple(required),
            "mapped_points": mapped,
            "inactive_points": tuple(inactive),
            "resolved_temperatures": resolved_temps,
            "curve_point_keys": curve_point_keys,
        }

    def _validate_scop_points(
        self,
        test_points: dict,
        climate_key: str,
        climate_data: dict,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        contract = self._resolve_scop_point_contract(climate_key, climate_data, tbiv_temp_c, tol_temp_c)
        required_keys = contract["required_independent_points"]
        points = {}
        for key in required_keys:
            point = self._parse_scop_point(test_points, key)
            point["temp_c"] = contract["resolved_temperatures"][key]
            points[key] = point

        for key, source_key in contract["mapped_points"].items():
            if source_key not in points:
                raise ValueError(f"Mapped SCOP point {key} source is missing: {source_key}")
            point = dict(points[source_key])
            point["temp_c"] = contract["resolved_temperatures"][key]
            point["mapped_from"] = source_key
            points[key] = point

        for key in contract["inactive_points"]:
            if key not in points:
                points[key] = {
                    "temp_c": contract["resolved_temperatures"][key],
                    "inactive": True,
                }

        if points["Tbiv"]["temp_c"] > climate_data["tbiv_max_c"]:
            raise ValueError(
                f"Tbiv exceeds climate maximum: {points['Tbiv']['temp_c']} > {climate_data['tbiv_max_c']}"
            )
        if points["TOL"]["temp_c"] > climate_data["tol_max_c"]:
            raise ValueError(
                f"TOL exceeds climate maximum: {points['TOL']['temp_c']} > {climate_data['tol_max_c']}"
            )
        if points["TOL"]["temp_c"] > points["Tbiv"]["temp_c"]:
            raise ValueError(
                f"TOL must be <= Tbiv for SCOP heating calculation: "
                f"TOL={points['TOL']['temp_c']}, Tbiv={points['Tbiv']['temp_c']}"
            )
        return {
            "points": points,
            "contract": contract,
        }

    def _heating_part_load(self, tj: float, p_design_h: float, t_design_h: float) -> float:
        if p_design_h <= 0:
            raise ValueError(f"p_design_h must be > 0 for SCOP calculation: {p_design_h}")
        if t_design_h == 16:
            raise ValueError("t_design_h cannot be 16°C for SCOP heating load line.")

        ph = p_design_h * (tj - 16.0) / (t_design_h - 16.0)
        return max(0.0, ph)

    def _scop_pl_at_declared_point(self, point: dict, load: float, cd: float) -> dict:
        capacity = point["capacity"]
        load_gap_ratio = self._safe_div(capacity - load, load) if load > 0 else 0.0
        # EN 14825 Clause 7.4.2.2 allows variable-capacity units to use the
        # closest capacity control step within +/-10%. With the current
        # declared-point-only input schema, raw capacity-control step candidates
        # are unavailable, so complete closest-step selection is not possible.
        # This condition treats a declared capacity above the required load but
        # within 10% as the acceptable closest step without Cd degradation; if
        # the gap exceeds 10%, it represents cycling at the lowest step above
        # the load. Replace this with actual closest-step selection when a raw
        # step schema is added.
        data = self._part_load_performance(
            capacity,
            point["power"],
            load,
            cd,
            apply_degradation=(capacity > load and load_gap_ratio > 0.10),
        )
        return {
            "cop_dc": data["full_load_efficiency"],
            "cop_pl": data["part_load_efficiency"],
            "cr": data["cr"],
            "degradation_factor": data["degradation_factor"],
        }

    def _build_scop_points(self, point_resolution: dict, climate_data: dict, p_design_h: float, cd: float) -> dict:
        t_design_h = float(climate_data["t_design_h_c"])
        points = point_resolution["points"]
        contract = point_resolution["contract"]
        resolved = {}
        for key, source_point in points.items():
            if source_point.get("inactive"):
                resolved[key] = dict(source_point)
                resolved[key]["key"] = key
                continue
            point = dict(source_point)
            load = self._heating_part_load(point["temp_c"], p_design_h, t_design_h)
            perf = self._scop_pl_at_declared_point(point, load, cd)
            point.update({
                "key": key,
                "load": load,
                "cop_dc": perf["cop_dc"],
                "cop_pl": perf["cop_pl"],
                "cr": perf["cr"],
                "degradation_factor": perf["degradation_factor"],
                "value": perf["cop_pl"],
            })
            resolved[key] = point

        return {
            "points": resolved,
            "capacity_curve": self._scop_capacity_curve_points(resolved, contract["curve_point_keys"]),
            "coppl_curve": self._scop_coppl_curve_points(resolved, contract["curve_point_keys"]),
        }

    def _scop_capacity_curve_points(self, points: dict, curve_point_keys: tuple) -> list:
        by_temp = {}
        for key in curve_point_keys:
            point = points[key]
            if point.get("inactive"):
                continue
            temp = point["temp_c"]
            if temp not in by_temp:
                by_temp[temp] = {
                    "key": key,
                    "temp_c": temp,
                    "value": point["capacity"],
                    "capacity": point["capacity"],
                }
        return sorted(by_temp.values(), key=lambda point: point["temp_c"])

    def _scop_coppl_curve_points(self, points: dict, curve_point_keys: tuple) -> list:
        by_temp = {}
        for key in curve_point_keys:
            point = points[key]
            if point.get("inactive"):
                continue
            temp = point["temp_c"]
            if temp not in by_temp:
                by_temp[temp] = {
                    "key": key,
                    "temp_c": temp,
                    "value": point["cop_pl"],
                    "cop_pl": point["cop_pl"],
                }
        return sorted(by_temp.values(), key=lambda point: point["temp_c"])

    def _capacity_at_temp_for_scop(self, tj: float, scop_points: dict) -> tuple:
        return self._interpolate_from_points(tj, scop_points["capacity_curve"])

    def _coppl_at_temp_for_scop(self, tj: float, scop_points: dict) -> tuple:
        return self._interpolate_from_points(tj, scop_points["coppl_curve"], extrapolate_upper=True)

    def _calculate_scop_on(self, scop_points: dict, climate_data: dict, p_design_h: float, cd: float) -> dict:
        temps = climate_data["heating_bin_temps_c"]
        hours = climate_data["heating_bin_hours"]
        t_design_h = float(climate_data["t_design_h_c"])
        tol_temp = scop_points["points"]["TOL"]["temp_c"]

        numerator = 0.0
        denominator = 0.0
        bin_details = []

        for tj, hj in zip(temps, hours):
            if hj <= 0:
                continue

            ph = self._heating_part_load(float(tj), p_design_h, t_design_h)
            if ph <= 0:
                continue

            if float(tj) < tol_temp:
                pdh = 0.0
                cop_pl = 0.0
                heat_pump_load = 0.0
                elbu = ph
                operating_case = "below_tol_electric_backup_only"
                capacity_source = "below_tol_heat_pump_off"
                cop_source = "below_tol_heat_pump_off"
                cr = 0.0
                denominator_contribution = hj * elbu
            else:
                pdh, capacity_source = self._capacity_at_temp_for_scop(float(tj), scop_points)
                cop_pl, cop_source = self._coppl_at_temp_for_scop(float(tj), scop_points)
                if pdh >= ph:
                    elbu = 0.0
                    heat_pump_load = ph
                    operating_case = "heat_pump_covers_load"
                else:
                    elbu = ph - pdh
                    heat_pump_load = pdh
                    operating_case = "capacity_shortfall_with_backup"
                cr = self._safe_div(heat_pump_load, pdh) if pdh > 0 else 0.0
                denominator_contribution = hj * (self._safe_div(heat_pump_load, cop_pl) + elbu)

            if heat_pump_load > 0 and cop_pl <= 0:
                raise ValueError(f"SCOP COPPL must be > 0 at Tj={tj}")

            numerator += hj * ph
            denominator += denominator_contribution

            bin_details.append({
                "temp_c": tj,
                "hours": hj,
                "ph": round(ph, 6),
                "pdh": round(pdh, 6),
                "cop_pl": round(cop_pl, 6) if cop_pl > 0 else 0.0,
                "equivalent_power": round(self._safe_div(pdh, cop_pl), 6) if cop_pl > 0 else 0.0,
                "cop_bin": round(cop_pl, 6) if cop_pl > 0 else 0.0,
                "cr": round(cr, 6),
                "degradation_factor": 1.0,
                "capacity_source": capacity_source,
                "cop_source": cop_source,
                "denominator_contribution": round(denominator_contribution, 6),
                "heat_pump_load": round(heat_pump_load, 6),
                "elbu": round(elbu, 6),
                "operating_case": operating_case,
                "interpolation": f"capacity={capacity_source}; cop={cop_source}",
            })

        if numerator <= 0:
            raise ValueError("SCOPon calculation error: heating demand numerator must be > 0.")
        if denominator <= 0:
            raise ValueError("SCOPon calculation error: energy denominator must be > 0.")

        return {
            "scop_on": numerator / denominator,
            "active_heating_kwh": numerator,
            "active_energy_kwh": denominator,
            "bin_details": bin_details,
        }

    def calculate_scop(
        self,
        test_points: dict,
        p_to: float,
        p_sb: float,
        p_ck: float,
        p_off: float,
        p_design_h: float,
        climate: str,
        cd: float = None,
        appliance_type: str = None,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        """
        EN 14825 / EU 206/2012 SCOP calculation path.

        Required test_points: A, B, C, D, TOL, Tbiv.
        Each value may be either (capacity, power) or
        {"capacity": kW, "power": kW, "temp_c": optional outdoor dry-bulb}.
        """
        climate_key = self._normalize_climate(climate)
        climate_data = self._get_scop_climate_data(climate_key)
        defaults = self.scop_config.get("defaults", {})
        if cd is None:
            try:
                cd = defaults["degradation_coefficient"]
            except KeyError as exc:
                raise ValueError("Missing SCOP default config key: degradation_coefficient") from exc
        if appliance_type is None:
            try:
                appliance_type = defaults["appliance_type"]
            except KeyError as exc:
                raise ValueError("Missing SCOP default config key: appliance_type") from exc

        point_resolution = self._validate_scop_points(test_points, climate_key, climate_data, tbiv_temp_c, tol_temp_c)
        scop_points = self._build_scop_points(point_resolution, climate_data, p_design_h, cd)
        operational_hours = self._get_scop_operational_hours(climate_key, appliance_type)
        scop_on_data = self._calculate_scop_on(scop_points, climate_data, p_design_h, cd)

        q_h = p_design_h * operational_hours["h_he"]
        if q_h <= 0:
            raise ValueError(f"Reference annual heating demand must be > 0: {q_h}")

        standby_kwh = (
            operational_hours["h_to"] * p_to
            + operational_hours["h_sb"] * p_sb
            + operational_hours["h_ck"] * p_ck
            + operational_hours["h_off"] * p_off
        )
        active_kwh = self._safe_div(q_h, scop_on_data["scop_on"])
        total_kwh = active_kwh + standby_kwh
        if total_kwh <= 0:
            raise ValueError("SCOP calculation error: total annual heating energy must be > 0.")

        scop = q_h / total_kwh
        return {
            "scop": round(scop, 3),
            "SCOP": round(scop, 3),
            "scop_on": round(scop_on_data["scop_on"], 3),
            "qh_kwh": round(q_h, 3),
            "active_kwh": round(active_kwh, 3),
            "standby_kwh": round(standby_kwh, 3),
            "total_kwh": round(total_kwh, 3),
            "climate": climate_key,
            "appliance_type": appliance_type,
            "p_design_h": p_design_h,
            "operational_hours": operational_hours,
            "source": self.scop_config.get("source", {}),
            "bin_details": scop_on_data["bin_details"],
            "unimplemented_notes": [
                "The current API treats user-entered A/B/C/D/TOL/Tbiv capacity and power as already resolved part-load declared points for EN 14825 Clause 7.4.",
                "If raw capacity-control step data is required, Clause 7.4.2.2 variable-capacity closest-step and +/-10% logic needs an expanded input schema.",
                "SCOPnet from Equation (10) is not returned because the requested output is SCOP.",
            ],
        }

if __name__ == "__main__":
    # 검증용 예시: 5kW 기기, 조건A EER=3.0 가정
    calc = EN14825Calculator()
    test_pts = {
        "A": (5.000, 5.000 / 3.00),  # EER 3.0
        "B": (3.700, 3.700 / 3.50),  # EER 3.5
        "C": (2.350, 2.350 / 4.10),  # EER 4.1
        "D": (1.050, 1.050 / 4.80),  # EER 4.8
    }
    
    # [버그 3 수정]: p_design_c 인자 추가
    result = calc.calculate_seer(
        test_points=test_pts,
        p_to=0.030,   # thermostat-off 소비전력 (kW)
        p_sb=0.005,   # standby (kW)
        p_ck=0.010,   # crankcase heater (kW)
        p_off=0.000,  # off (reversible이므로 0)
        p_design_c=5.000 # 5kW 기기로 가정
    )
    print("=== EN 14825 SEER 계산 결과 ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
