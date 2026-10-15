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
