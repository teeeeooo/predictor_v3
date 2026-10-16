"""Route through standard application request builders; never parse displayed scores."""
from math import isfinite
from dataclasses import replace, fields, is_dataclass
from collections.abc import Mapping
from apps.calculator.application.profile_resolver import resolve_two_point_profile_id
from core.calculators.capability import execute_standard_calculation
from apps.calculator.application.iso_iseer_2point.usecase import IsoIseer2PointUseCase
from apps.calculator.application.hong_kong_cspf.usecase import HongKongCspfUseCase
from apps.calculator.application.hong_kong_hspf.usecase import HongKongHspfUseCase
from apps.calculator.application.saso_t3.usecase import SasoT3UseCase
from apps.calculator.application.brazil_cspf.usecase import BrazilCspfUseCase
from apps.calculator.application.korea.usecase import KoreaCspfUseCase
from apps.calculator.application.korea.hspf_usecase import KoreaHspfUseCase
from apps.calculator.application.en14825.seer_adapter import SeerAdapter, SeerPointInput
from apps.calculator.application.en14825.scop_adapter import ScopAdapter, ScopPointInput
from apps.calculator.application.ahri_m.seer_adapter import AhriSeerAdapter
from apps.calculator.application.ahri_m.hspf_adapter import AhriHspfAdapter, AhriHspfOptions
from apps.calculator.application.ahri.seer2_adapter import AhriSeer2Adapter, AhriSeer2Options
from apps.calculator.application.ahri.hspf2_adapter import AhriHspf2Adapter, AhriHspf2Options
from .models import Candidate, Score, Session
from .point_policy import resolve_points

OPERATIONS = dict(iso="iso16358.cspf", hong_kong_cspf="iso16358.cspf", hong_kong_hspf="iso16358.hspf",
                  saso="iso16358.cspf", brazil="brazil.cspf_compliance", korea_cspf="ks_c9306.cspf",
                  korea_hspf="ks_c9306.hspf", en_seer="en14825.seer", en_scop="en14825.scop",
                  m_seer="ahri210240.seer", m_hspf="ahri210240.hspf", seer2="ahri210240.seer2", hspf2="ahri210240.hspf2")
PROFILES = dict(hong_kong_cspf="hong_kong_cspf", hong_kong_hspf="hong_kong_hspf", saso="saso_t3_cspf",
                brazil="brazil_cspf_compliance", korea_cspf="ks_c9306_cspf", korea_hspf="ks_c9306_hspf",
                en_seer="en14825_seer", en_scop="en14825_scop", m_seer="ahri_usa_m_seer",
                m_hspf="ahri_usa_m_hspf", seer2="ahri_usa_seer2", hspf2="ahri_usa_hspf2")
OWNERS = dict(iso=IsoIseer2PointUseCase, hong_kong_cspf=HongKongCspfUseCase, hong_kong_hspf=HongKongHspfUseCase,
              saso=SasoT3UseCase, brazil=BrazilCspfUseCase, korea_cspf=KoreaCspfUseCase, korea_hspf=KoreaHspfUseCase,
              en_seer=SeerAdapter, en_scop=ScopAdapter, m_seer=AhriSeerAdapter, m_hspf=AhriHspfAdapter,
              seer2=AhriSeer2Adapter, hspf2=AhriHspf2Adapter)


class StandardAdapter:
    def __init__(self, executor=execute_standard_calculation):
        self.executor = executor
        self._owners = {}

    def owner(self, context):
        if context.kind not in self._owners:
            self._owners[context.kind] = OWNERS[context.kind]()
        return self._owners[context.kind]

    def operation(self, context):
        return OPERATIONS[context.kind]

    def profile(self, context):
        return resolve_two_point_profile_id(context.profile) if context.kind == "iso" else PROFILES[context.kind]

    def metric(self, context):
        if context.kind == "iso" and context.profile == "India ISEER":
            return "ISEER"
        return self.operation(context).rsplit(".",1)[1].replace("cspf_compliance", "cspf").upper()

    def points(self, context):
        return resolve_points(context, self.owner(context) if context.kind == "en_scop" else None)

    def draft_points(self, context):
        """Keep an invalid temperature draft editable; preflight still rejects it."""
        try:
            return self.points(context)
        except (ValueError, TypeError):
            if context.kind != "en_scop":
                raise
            values = dict(context.values)
            values.update(tbiv_temp_c="", tol_temp_c="")
            return self.points(replace(context, values=tuple(values.items())))

    def request(self, context, values):
        owner = self.owner(context)
        opts = dict(context.options)
        if context.kind == "iso":
            request = owner.build_request(values, profile_label=context.profile)
        elif context.kind == "saso":
            request = owner.build_request(values, test_selection=context.mode)
        elif context.kind.startswith("en_"):
            settings = {}
            point_keys = {field for point in self.points(context) for field in (point.capacity_field, point.power_field)}
            for key, value in values.items():
                if key in point_keys or key.startswith("declared_"):
                    continue
                if key in ("tbiv_temp_c", "tol_temp_c") and not value.strip():
                    settings[key] = None
                    continue
                settings[key] = value if key == "appliance_type" else float(value.replace(",", ""))
                if isinstance(settings[key], float) and not isfinite(settings[key]):
                    raise ValueError(f"{key}: 유한 숫자 필요")
            model = SeerPointInput if context.kind=="en_seer" else ScopPointInput
            inputs = {p.key: model(tested_capacity=float(values[p.capacity_field].replace(",", "")), tested_power=float(values[p.power_field].replace(",", "")))
                      for p in self.points(context) if p.independent}
            if context.kind == "en_scop":
                settings["climate"] = context.climate
            request = owner.build_tested_request(inputs, **settings)
        elif context.kind == "m_hspf":
            request = owner.build_request(values, options=AhriHspfOptions(**opts))
        elif context.kind == "seer2":
            request = owner.build_request(values, system_type=context.system_type, product_classification=context.product,
                                          options=AhriSeer2Options(**opts))
        elif context.kind == "hspf2":
            request = owner.build_request(values, options=AhriHspf2Options(**opts))
        else:
            request = owner.build_request(values)
        if request is None:
            raise ValueError("공통 설정 또는 필수 입력이 불완전합니다")
        _validate_request_numbers(request)
        return self.operation(context), request

    def execute(self, context, values):
        operation, request = self.request(context, values)
        return self.executor(operation, request)

    def project(self, context, result):
        metric = self.metric(context)
        if context.kind == "brazil":
            # Match the main Brazil report's two-decimal CSPF; rules stay exact.
            return Score(round(result.three_point_exact_cspf, 2), metric, "W/W", summary=(
                ("two_point_cspf", result.two_point_exact_cspf), ("rule_1", "OK" if result.rule_1.passed else "NG"),
                ("rule_2", "OK" if result.rule_2.passed else "NG"), ("final", "OK" if result.final_passed else "NG")))
        key = "cspf" if metric == "ISEER" else metric.lower()
        raw, published = result.get("raw_"+key), result.get("published_"+key)
        if context.kind == "korea_hspf":
            value = result.get("rounded_hspf")
        else:
            value = result.get(metric) if context.kind in ("m_seer", "m_hspf", "seer2", "hspf2") else result.get(key)
        if value is None:
            raise ValueError(f"Missing reported numeric {metric}")
        summary = tuple((k,v) for k,v in result.items() if isinstance(v,(int,float,str,bool)) and k not in (key,metric,"raw_"+key,"published_"+key))
        return Score(float(value), metric, "Btu/Wh" if context.kind in ("m_seer","m_hspf","seer2","hspf2") else "W/W",
                     raw, published, summary)


def seed_session(context, adapter):
    values = dict(context.values)
    fields = {field for point in adapter.draft_points(context) for field in (point.capacity_field, point.power_field)}
    if context.kind in ("en_seer", "en_scop"):
        # Declared inputs belong to the main page comparison, not Tested runs.
        fields.update(key for key in values if key.startswith("declared_"))
    session = Session(replace(context, values=tuple((k,v) for k,v in context.values if k not in fields)))
    for point in adapter.draft_points(context):
        session.pools[point.key] = [Candidate(capacity=values.get(point.capacity_field, ""),
                                             power=values.get(point.power_field, ""))]
    return session


def _validate_request_numbers(value, key="request"):
    """Reject non-finite common settings before any engine call."""
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{key}: 유한 숫자 필요")
    if key in ("declared_capacity", "rated_cooling_capacity") and value is not None and value <= 0:
        raise ValueError(f"{key}: 양수 입력 필요")
    if is_dataclass(value):
        for field in fields(value):
            _validate_request_numbers(getattr(value, field.name), field.name)
    elif isinstance(value, Mapping):
        for name, item in value.items():
            _validate_request_numbers(item, name)
    elif isinstance(value, (tuple, list)):
        for item in value:
            _validate_request_numbers(item, key)
