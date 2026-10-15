from dataclasses import replace
import pytest

from apps.calculator.application.combinations.adapters import StandardAdapter, seed_session
from apps.calculator.application.combinations.models import Candidate, Context, Score
from apps.calculator.application.combinations.service import start, preflight, ValidationError


def iso_session():
    return seed_session(Context("iso", profile="ISO 16358-1", values=tuple(dict(
        full_capacity="3500", full_power="1000", half_capacity="1750", half_power="400").items())), StandardAdapter())


def finish(run):
    while run.status == "running":
        run.step()
    return run


def test_pairs_numeric_sort_replay_stale_and_csv():
    from apps.calculator.ui.combinations.export import export_rows
    session = iso_session()
    session.pools["35_full"] = [Candidate(label=f"시험 {i},\n쌍", capacity=str(3500+i), power=str(900+i*100)) for i in range(3)]
    session.pools["35_half"] = [Candidate(label=str(i), capacity=str(1750+i), power=str(380+i*20)) for i in range(5)]
    adapter = StandardAdapter()
    run = finish(start(session, adapter))
    assert run.processed == run.succeeded == 15
    for row in run.results:
        assert adapter.project(run.snapshot.context, run.detail(row)) == row.score
    scores = [row.score.value for _, row in run.ranked()]
    assert scores == sorted(scores, reverse=True)
    prior = run.detail(run.results[0])
    session.pools["35_full"].clear()
    session.changed()
    assert session.stale
    assert prior == run.detail(run.results[0])
    headers, rows = export_rows(run)
    assert len(rows) == 15
    assert rows[0][headers.index("STD 성능 [W]")] == "3500.0"


def test_preflight_cap_blanks_exclusion_and_old_run():
    session = iso_session()
    adapter = StandardAdapter()
    old = finish(start(session, adapter))
    session.pools["35_full"].append(Candidate(capacity="1"))
    with pytest.raises(ValidationError, match="power"):
        start(session, adapter)
    assert session.run is old
    session.pools["35_full"][-1] = replace(session.pools["35_full"][-1], included=False)
    assert preflight(session, adapter).planned == 1
    session.pools["35_full"] = [Candidate(capacity="3500", power="1000") for _ in range(10000)]
    assert preflight(session, adapter).planned == 10000
    session.pools["35_full"].append(Candidate(capacity="3500", power="1000"))
    with pytest.raises(ValidationError, match="10,001"):
        start(session, adapter)


def test_ties_errors_cancellation_and_failed_orchestration():
    session = iso_session()
    session.pools["35_full"] *= 1
    session.pools["35_full"] = [Candidate(capacity="3500", power=str(v)) for v in (900,900,1000,1100)]
    class Adapter(StandardAdapter):
        def execute(self, context, values):
            if values["full_power"] == "1100.0":
                raise ValueError("domain failure")
            return values
        def project(self, context, result):
            return Score(10000/float(result["full_power"]), "CSPF", "W/W")
    run = finish(start(session, Adapter()))
    assert [rank for rank, _ in run.ranked()] == [1,1,3,None]
    assert run.status == "completed-with-errors"
    run = start(session, Adapter())
    run.step(max_cases=2)
    run.cancel()
    run.step()
    assert run.status == "cancelled" and run.processed == 2 and run.partial
    class Broken(Adapter):
        def execute(self, *args):
            raise RuntimeError("orchestrator failure")
    assert finish(start(session, Broken())).status == "failed"


@pytest.mark.parametrize("bad",["", "0", "-1", "nan", "inf", "text"])
def test_invalid_included_values_fail_before_any_execution(bad):
    calls=[]
    adapter=StandardAdapter(lambda *args:calls.append(args))
    session=iso_session()
    base=session.pools["35_full"][0]
    session.pools["35_full"][0]=replace(base,power=bad)
    with pytest.raises(ValidationError):
        start(session,adapter)
    assert calls==[]
    session.pools["35_full"][0]=base
    assert preflight(session,adapter).planned==1


def test_blank_duplicates_independent_zero_pools_and_immutable_context():
    session=iso_session();adapter=StandardAdapter()
    session.pools["35_full"].append(Candidate())
    assert preflight(session,adapter).planned==1
    session.pools["35_full"].append(Candidate(capacity="3500",power="1000"))
    run=finish(start(session,adapter))
    assert run.succeeded==2 and [rank for rank,row in run.ranked()]==[1,1]
    assert run.snapshot.pools[0][0].id!=run.snapshot.pools[0][1].id
    session.pools["35_half"]=[]
    with pytest.raises(ValidationError):
        start(session,adapter)
    assert session.run is run
    assert dict(run.snapshot.context.values)=={}


def test_common_invalid_preflight_keeps_old_run_and_snapshot_is_frozen():
    from .seeds import contexts
    adapter=StandardAdapter()
    context=next(c for c in contexts() if c.kind=="hong_kong_cspf")
    session=seed_session(context,adapter)
    old=finish(start(session,adapter))
    for bad in ("nan","inf","0","-1","text"):
        session.context=replace(session.context,values=(("declared_capacity",bad),))
        with pytest.raises(ValueError):
            start(session,adapter)
        assert session.run is old
    assert dict(old.snapshot.context.values)["declared_capacity"]=="3500"
