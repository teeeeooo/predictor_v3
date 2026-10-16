from dataclasses import replace
import pytest
from apps.calculator.application.combinations.adapters import StandardAdapter, seed_session
from apps.calculator.application.combinations.models import Candidate
from apps.calculator.application.combinations.service import preflight, start
from apps.calculator.ui.combinations.export import export_rows
from core.calculators.capability import execute_standard_calculation, build_builtin_capability_registry
from .seeds import contexts
from .test_service import finish


@pytest.mark.parametrize("context", contexts(), ids=lambda c:"/".join((c.kind,c.profile,c.product,c.climate,c.system_type,c.mode)))
def test_all_current_contexts_sweep_numeric_gateway_replay(context):
    calls=[]
    def execute(operation, request):
        calls.append((operation,request))
        return execute_standard_calculation(operation,request)
    adapter=StandardAdapter(execute)
    session=seed_session(context,adapter)
    active=[p for p in adapter.points(context) if p.independent]
    for point,factors in zip(active, ((.97,1,1.03),(.96,.98,1,1.02,1.04))):
        base=session.pools[point.key][0]
        session.pools[point.key]=[Candidate(label=str(i),capacity=base.capacity,power=str(float(base.power)*factor)) for i,factor in enumerate(factors)]
    preflight(session,adapter)
    assert calls==[]
    run=finish(start(session,adapter))
    assert run.succeeded==15, [(r.error_code,r.error_message) for r in run.results if r.score is None]
    assert len(calls)==15
    for row,(operation,request) in zip(run.results,calls[:]):
        assert adapter.project(context,execute_standard_calculation(operation,request))==row.score
        assert adapter.project(context,run.detail(row))==row.score
    assert len({row.selections for row in run.results})==15


def test_scop_and_triple_policy():
    adapter=StandardAdapter()
    warmer=next(c for c in contexts() if c.climate=="warmer")
    points={p.key:p for p in adapter.points(warmer)}
    assert [p.key for p in points.values() if p.independent]==["B","C","D"]
    assert points["Tbiv"].source=="B"
    triple=next(c for c in contexts() if c.product=="triple_capacity_northern")
    assert sum(p.independent for p in adapter.points(triple))==8
    values=dict(triple.values);values["low_min_c"]="0"
    changed=replace(triple,values=tuple(values.items()))
    assert sum(p.independent for p in adapter.points(changed))==9
    assert next(p for p in adapter.points(changed) if p.key=="H2Low").role=="inactive"


@pytest.mark.parametrize("kind,product,climate",[("en_scop","","colder"),("hspf2","variable_capacity",""),("hspf2","triple_capacity_northern","")])
def test_real_10000_runs(kind,product,climate):
    context=next(c for c in contexts() if c.kind==kind and c.product==product and c.climate==climate)
    adapter=StandardAdapter(); session=seed_session(context,adapter)
    for point in [p for p in adapter.points(context) if p.independent][:4]:
        base=session.pools[point.key][0]
        session.pools[point.key]=[Candidate(capacity=base.capacity,power=str(float(base.power)*(.99+i*.02/9))) for i in range(10)]
    run=finish(start(session,adapter))
    assert run.snapshot.planned==run.succeeded==10000


def test_operation_inventory_and_optional_product_paths():
    adapter=StandardAdapter()
    assert {adapter.operation(c) for c in contexts()} == set(build_builtin_capability_registry().capability_ids)
    for kind,product,expected,flags,extra in (
        ("m_hspf","",7,dict(measured_h12=True,measured_h22=True,demand_defrost=True),{}),
        ("hspf2","variable_capacity",8,dict(measured_h42=True,measured_h12=True,measured_h22=True),{}),
        ("hspf2","dual_stage",8,dict(measured_h4_full=True,measured_h2_low=True),dict(capacity_H4Full="15000",power_H4Full="2200")),
        ("hspf2","triple_capacity_northern",9,dict(measured_h2_boost=True),dict(low_min_c="0")),
        ("hspf2","triple_capacity_northern",7,dict(measured_h2_boost=False),{}),
    ):
        base=next(c for c in contexts() if c.kind==kind and c.product==product)
        context=replace(base,options=tuple({**dict(base.options),**flags}.items()),values=tuple({**dict(base.values),**extra}.items()))
        session=seed_session(context,adapter)
        assert sum(p.independent for p in adapter.points(context))==expected
        run=finish(start(session,adapter))
        assert run.succeeded==1,run.results
        assert not any(p.key in ("A2","AFull") for p in run.snapshot.points)
    for mode in ("none","calculated_from_timing"):
        base=next(c for c in contexts() if c.product=="triple_capacity_northern")
        context=replace(base,options=tuple({**dict(base.options),"defrost_mode":mode}.items()))
        assert finish(start(seed_session(context,adapter),adapter)).succeeded==1


@pytest.mark.parametrize("kind,factors,expected", [
    ("m_seer", (1, 1.00001, 0.9), 18.05),
    ("brazil", (1, 0.99999, 1.1), 5.72),
])
def test_reported_ties_keep_input_order_and_csv_rank(kind, factors, expected):
    adapter = StandardAdapter()
    context = next(c for c in contexts() if c.kind == kind)
    session = seed_session(context, adapter)
    point = next(p for p in adapter.points(context) if p.independent)
    base = session.pools[point.key][0]
    session.pools[point.key] = [
        Candidate(capacity=base.capacity, power=str(float(base.power) * factor))
        for factor in factors
    ]
    run = finish(start(session, adapter))
    assert run.succeeded == 3
    details = [run.detail(row) for row in run.results[:2]]
    raw = [detail.three_point_exact_cspf if kind == "brazil" else detail["raw_seer"]
           for detail in details]
    # The second candidate is better before rounding, but its report ties.
    assert raw[0] < raw[1]
    assert [row.score.value for row in run.results[:2]] == [expected, expected]
    assert run.results[2].score.value < expected
    assert [(rank, row.ordinal) for rank, row in run.ranked()] == [(1, 1), (1, 2), (3, 3)]
    _, rows = export_rows(run)
    assert [row[0] for row in rows] == ["1", "1", "3"]
    assert [row[1] for row in rows[:2]] == [str(expected), str(expected)]


def test_korea_hspf_ranks_the_existing_rounded_report():
    adapter = StandardAdapter()
    context = next(c for c in contexts() if c.kind == "korea_hspf")
    run = finish(start(seed_session(context, adapter), adapter))
    result = run.detail(run.results[0])
    assert result["hspf"] != result["rounded_hspf"]
    assert run.results[0].score.value == result["rounded_hspf"] == 2.874


def test_brazil_ng_is_rankable():
    adapter=StandardAdapter()
    brazil=next(c for c in contexts() if c.kind=="brazil")
    values=dict(brazil.values);values["half_29_power"]="1000"
    brazil=replace(brazil,values=tuple(values.items()))
    run=finish(start(seed_session(brazil,adapter),adapter))
    assert run.succeeded==1
    assert dict(run.results[0].score.summary)["rule_2"]=="NG"
    # Final uses the existing OR rule; isolate the presentation boundary with
    # an explicit domain NG outcome instead of inventing an expected formula.
    result=run.detail(run.results[0])
    ng=replace(result,rule_1=replace(result.rule_1,passed=False),
               rule_2=replace(result.rule_2,passed=False),final_passed=False)
    ng_adapter=StandardAdapter(lambda *args:ng)
    ng_run=finish(start(seed_session(brazil,ng_adapter),ng_adapter))
    assert ng_run.succeeded==1
    assert dict(ng_run.results[0].score.summary)["final"]=="NG"


@pytest.mark.parametrize("kind", ["en_seer", "en_scop", "seer2"])
def test_existing_thousands_separator_input_policy(kind):
    adapter=StandardAdapter()
    context=next(c for c in contexts() if c.kind==kind)
    expected=finish(start(seed_session(context,adapter),adapter)).results[0].score
    values=dict(context.values)
    for point in adapter.points(context):
        if point.independent:
            for key in (point.capacity_field,point.power_field):
                values[key]=f"{float(values[key]):,.2f}"
    for key in ("p_design_c_w", "p_design_h_w"):
        if key in values:
            values[key]="3,500"
    grouped=replace(context,values=tuple(values.items()))
    run=finish(start(seed_session(grouped,adapter),adapter))
    assert run.results[0].score==expected
