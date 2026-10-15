import csv
import json
from dataclasses import replace
from apps.calculator.application.combinations.models import Candidate
from apps.calculator.application.combinations.adapters import StandardAdapter
from apps.calculator.application.combinations.service import start
from apps.calculator.ui.combinations.export import export_rows
from apps.calculator.ui.table_csv_export import write_csv
from .test_service import iso_session, finish


def test_full_csv_quotes_context_and_old_measurements(tmp_path):
    session=iso_session()
    session.pools["35_full"]=[Candidate(label='한글, "시험"\n다음 줄',capacity="3500",power=str(900+i)) for i in range(101)]
    run=finish(start(session,StandardAdapter()))
    session.pools["35_full"][0]=Candidate(capacity="9999",power="999")
    session.changed()
    headers,rows=export_rows(run,stale=session.stale)
    path=tmp_path/"전체.csv";write_csv(path,headers,rows)
    assert path.read_bytes().startswith(b'\xef\xbb\xbf')
    with path.open(encoding="utf-8-sig",newline="") as handle:
        records=list(csv.DictReader(handle))
    assert len(records)==101
    assert all(r["35_full.capacity"]=="3500.0" for r in records)
    assert records[0]["35_full.label"]=='한글, "시험"\n다음 줄'
    assert all(r["stale"]=="True" for r in records)
    assert json.loads(records[0]["context_json"])["context"]["values"]==[]
    assert records[0]["profile"]=="iso_t1_default_2point_cspf"


def test_result_candidate_numbers_keep_excluded_columns_and_stale_provenance():
    session = iso_session()
    candidates = [Candidate(capacity="3500", power=str(power)) for power in (900, 1000, 1100)]
    candidates[1] = replace(candidates[1], included=False)
    expected_numbers = {candidates[0].id: "1", candidates[2].id: "3"}
    session.pools["35_full"] = candidates
    run = finish(start(session, StandardAdapter()))
    assert [value.number for value in run.snapshot.pools[0]] == [1, 3]

    # A later deletion renumbers the live grid, not the completed run or CSV.
    session.pools["35_full"].pop(0)
    session.changed()
    headers, rows = export_rows(run, stale=session.stale)
    records = [dict(zip(headers, row)) for row in rows]
    assert {row["35_full.candidate_id"]: row["35_full.candidate_number"] for row in records} == expected_numbers
    assert all(row["35_full.label"] == "" and row["stale"] == "True" for row in records)
