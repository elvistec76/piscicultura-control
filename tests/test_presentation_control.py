from piscicultura.charts import figures
from piscicultura.config import make_config
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from piscicultura.tank_view import snapshot


def test_turbidity_display_matches_one_sided_acceptance_rule(tmp_path):
    repo=SQLiteRepository(tmp_path/'presentation.sqlite')
    service=SimulationService(repo)
    c=make_config(0,'S0','open')
    c['x0'][3]=2.
    c['profile']['operating_bands'][3]=[5.,20.]
    rid=service.prepare(c)
    service.advance(rid,'first',0)
    run=repo.get(rid);samples=repo.records(rid,'samples');actions=repo.records(rid,'actuator_records')
    data=snapshot(run,samples,actions,repo.records(rid,'events'))
    assert data['sensors'][3]['value']<5
    assert data['sensors'][3]['in_band'] is True
    assert data['horizon_s']==c['time']['horizon_s']
    plots=figures(run,samples,actions)
    assert plots[3].layout.shapes[0].y0==0
    assert plots[3].layout.shapes[0].y1==20
    assert plots[0].layout.shapes[1].line.color=='#fbbf24'
    assert plots[-1].layout.yaxis.tickformat=='.0%'
    repo.close()
