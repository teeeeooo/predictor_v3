import csv
from dataclasses import replace
import pytest

from apps.calculator.application.combinations.models import Candidate
from apps.calculator.application.combinations.adapters import StandardAdapter, seed_session
from apps.calculator.application.combinations.service import start
from apps.calculator.ui.combinations.export import export_rows, export_filename
from apps.calculator.ui.table_csv_export import write_csv
from .test_service import iso_session, finish
from .seeds import contexts


def test_full_csv_is_concise_and_uses_pinned_measurements(tmp_path):
    session = iso_session()
    session.pools["35_full"] = [Candidate(label="사용자 이름", capacity="3500", power=str(900+i)) for i in range(101)]
    run = finish(start(session, StandardAdapter()))
    session.pools["35_full"][0] = Candidate(capacity="9999", power="999")
    session.changed()
    headers, rows = export_rows(run)
    assert headers == ("순위", "값", "지표", "STD 성능 [W]", "STD 전력 [W]",
                       "HALF 성능 [W]", "HALF 전력 [W]", "annual_cooling_kwh", "annual_power_kwh")
    path = tmp_path/"전체.csv"
    write_csv(path, headers, rows)
    assert path.read_bytes().startswith(b'\xef\xbb\xbf')
    with path.open(encoding="utf-8-sig", newline="") as handle:
        records = list(csv.DictReader(handle))
    assert len(records) == 101
    assert all(r["STD 성능 [W]"] == "3500.0" for r in records)
    assert {float(r["STD 전력 [W]"]) for r in records} == set(range(900, 1001))
    assert [float(r["값"]) for r in records] == sorted((float(r["값"]) for r in records), reverse=True)
    assert export_filename(run, stale=session.stale) == "calculator_combinations_stale.csv"


def test_excluded_columns_and_later_deletions_do_not_change_export_pairs():
    session = iso_session()
    candidates = [Candidate(capacity="3500", power=str(power)) for power in (900, 1000, 1100)]
    candidates[1] = replace(candidates[1], included=False)
    session.pools["35_full"] = candidates
    run = finish(start(session, StandardAdapter()))
    assert [value.number for value in run.snapshot.pools[0]] == [1, 3]
    session.pools["35_full"].pop(0)
    session.changed()
    headers, rows = export_rows(run)
    records = [dict(zip(headers, row)) for row in rows]
    assert {row["STD 전력 [W]"] for row in records} == {"900.0", "1100.0"}


@pytest.mark.parametrize("context", contexts())
def test_all_context_csv_contains_pairs_and_additional_results_without_recalculation(context):
    adapter = StandardAdapter()
    run = finish(start(seed_session(context, adapter), adapter))
    assert run.succeeded == 1
    def unexpected_execution(*args):
        raise AssertionError("Export must use stored results")
    adapter.execute = unexpected_execution
    headers, rows = export_rows(run)
    score = run.results[0].score
    assert rows[0][:3] == ("1", str(score.value), score.metric)
    pair_end = 3 + 2*len(run.snapshot.independent_points)
    assert rows[0][3:pair_end] == tuple(str(value) for pool in run.snapshot.pools
                                      for value in (pool[0].capacity, pool[0].power))
    assert all("성능 [" in h or "전력 [W]" in h for h in headers[3:pair_end])
    extras = headers[pair_end:]
    assert extras, context
    assert rows[0][pair_end:] == tuple(str(dict(score.summary)[key]) for key in extras)
    assert not {"run_id", "context_json", "basis", "system_type", "raw_base_value", "presentation_value"}.intersection(headers)
    if context.kind == "en_seer":
        assert extras == ("seer_on", "qc_kwh")
    if context.kind == "en_scop":
        assert extras == ("scop_on", "qh_kwh", "active_kwh", "standby_kwh", "total_kwh")


def test_errors_are_retained_with_one_conditional_column_and_csv_quoting(tmp_path):
    message = '한글, "오류"\n다음 줄'
    class Adapter(StandardAdapter):
        def execute(self, context, values):
            if values["full_power"] == "1100.0":
                raise ValueError(message)
            return super().execute(context, values)
    session = iso_session()
    session.pools["35_full"] = [Candidate(capacity="3500", power=str(power)) for power in (900, 1100)]
    run = finish(start(session, Adapter()))
    headers, rows = export_rows(run)
    assert headers[-1] == "오류"
    assert rows[0][-1] == "" and message in rows[1][-1]
    assert rows[1][:3] == ("", "", "CSPF")
    assert rows[1][3:7] == ("3500.0", "1100.0", "1750.0", "400.0")
    path = tmp_path/"오류.csv"
    write_csv(path, headers, rows)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        assert tuple(tuple(row) for row in csv.reader(handle)) == (headers, *rows)


def test_partial_and_stale_are_visible_in_filename():
    session = iso_session()
    session.pools["35_full"].append(Candidate(capacity="3500", power="1000"))
    run = start(session, StandardAdapter())
    run.step(max_cases=1)
    run.cancel()
    run.step()
    assert export_filename(run, stale=False) == "calculator_combinations_partial.csv"
    assert export_filename(run, stale=True) == "calculator_combinations_partial_stale.csv"
    session = seed_session(next(c for c in contexts() if c.kind == "hspf2" and c.product == "dual_stage"), StandardAdapter())
    run = finish(start(session, StandardAdapter()))
    assert export_filename(run, stale=False) == "calculator_combinations.csv"
