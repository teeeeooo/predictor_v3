"""KS C 9306 ROUND_HALF_UP input preparation."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class KSInputPreparationMixin:
    def _round_test_value(self, value: float) -> int:
        """KS C 9306 시험값 정수 반올림 helper.

        Python ``round()``의 banker's rounding을 피하기 위해 ROUND_HALF_UP을
        사용한다. KS 측 선전처리를 반복 호출해도 정수 -> 정수 idempotent
        결과로 동일 값을 유지한다.
        """
        return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    def _prepare_measured_inputs(self, measured_inputs: dict) -> dict:
        """KS CSPF 시험값 dict의 capacity/power만 정수화한 새 dict를 반환한다.

        ``self.config["round_test_values"]``가 truthy일 때만 정수화하며,
        그렇지 않으면 원본 dict를 그대로 돌려준다. unknown field는 보존하고,
        원본 dict는 mutate하지 않는다.
        """
        if not self.config.get("round_test_values", False):
            return measured_inputs

        prepared = {}
        for point_key, point_data in measured_inputs.items():
            if not isinstance(point_data, dict):
                prepared[point_key] = point_data
                continue

            prepared[point_key] = {}
            for data_key, value in point_data.items():
                if data_key in ("capacity", "power"):
                    try:
                        prepared[point_key][data_key] = self._round_test_value(value)
                    except (InvalidOperation, ValueError, TypeError):
                        prepared[point_key][data_key] = value
                else:
                    prepared[point_key][data_key] = value

        return prepared
