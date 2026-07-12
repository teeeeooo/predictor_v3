"""ISO 16358-2 building-load context."""


class HSPFLoadContextMixin:
    def _iso_hspf_common_load_line(
        self,
        hspf_cfg: dict,
        rated_heating_capacity: float | None,
        resolved: dict | None = None
    ) -> dict:
        load_line_cfg = hspf_cfg.get("load_line", {})
        required_fields = (
            "zero_load_temp",
            "full_load_temp",
            "rated_capacity_factor",
        )
        if any(field not in load_line_cfg for field in required_fields):
            raise ValueError(
                "Invalid ISO 16358-2 HSPF load_line: zero_load_temp, "
                "full_load_temp, and rated_capacity_factor are required."
            )

        zero_load_temp = float(load_line_cfg["zero_load_temp"])
        full_load_temp = float(load_line_cfg["full_load_temp"])
        rated_capacity_factor = float(load_line_cfg["rated_capacity_factor"])
        if zero_load_temp == full_load_temp:
            raise ValueError(
                "Invalid ISO 16358-2 HSPF load_line: zero_load_temp and full_load_temp must differ."
            )
        if rated_capacity_factor <= 0:
            raise ValueError(
                "Invalid ISO 16358-2 HSPF load_line: rated_capacity_factor must be positive."
            )

        source = load_line_cfg.get("source")
        if source == "rated_heating_capacity":
            if rated_heating_capacity is None:
                raise ValueError(
                    "rated_heating_capacity must be provided explicitly in "
                    "measured_inputs for ISO 16358-2 HSPF."
                )
            reference_capacity = float(rated_heating_capacity)
            if reference_capacity <= 0:
                raise ValueError("rated_heating_capacity must be positive.")
        elif source == "measured_point_capacity":
            if resolved is None:
                raise ValueError(
                    "Invalid ISO 16358-2 HSPF load_line: resolved measured points are required."
                )
            point_key = load_line_cfg.get("point_key")
            field = load_line_cfg.get("field", "capacity")
            if not point_key or not field:
                raise ValueError(
                    "Invalid ISO 16358-2 HSPF load_line: point_key and field are required "
                    "for measured_point_capacity."
                )
            try:
                reference_capacity = float(resolved[point_key][field])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    "Invalid ISO 16358-2 HSPF load_line: measured_point_capacity "
                    f"requires measured point '{point_key}' field '{field}'."
                ) from exc
            if reference_capacity <= 0:
                raise ValueError(
                    "Invalid ISO 16358-2 HSPF load_line: measured_point_capacity "
                    f"for point '{point_key}' field '{field}' must be positive."
                )
        else:
            raise ValueError(
                f"Unsupported or missing load_line source '{source}' for ISO 16358-2 HSPF."
            )

        l_h_ref = reference_capacity * rated_capacity_factor
        denominator = zero_load_temp - full_load_temp
        return {
            "zero_load_temp": zero_load_temp,
            "full_load_temp": full_load_temp,
            "rated_capacity_factor": rated_capacity_factor,
            "source": source,
            "l_h_ref": l_h_ref,
            "line": (
                -l_h_ref / denominator,
                l_h_ref * zero_load_temp / denominator,
            ),
        }
