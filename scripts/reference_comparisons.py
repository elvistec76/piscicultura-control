"""Vincular corridas observadas, conservar tramo común y exportar comparaciones."""
import json
from pathlib import Path
from piscicultura.repository import SQLiteRepository
from piscicultura.metrics import evaluate


def main():
    out=Path('evidence/comparisons');out.mkdir(exist_ok=True)
    index=json.loads(Path('evidence/run_index.json').read_text());repo=SQLiteRepository('work/acceptance.sqlite')
    for profile in range(3):
        for scenario in ['S1','S2','S3','S4','S5','S6','S7','S9']:
            keys={s:f'{scenario}_p{profile}_{s}' for s in ['open','closed']}
            if not all(k in index for k in keys.values()): continue
            runs={s:repo.get(index[k]['run_id']) for s,k in keys.items()}
            c0=runs['open']['config'].copy();c1=runs['closed']['config'].copy();c0.pop('strategy');c1.pop('strategy');assert c0==c1
            assert runs['open']['noise']==runs['closed']['noise']
            cid=f'{scenario}_p{profile}';common=min(r['time_s'] for r in runs.values())
            result=dict(comparison_id=cid,base_equal_except_strategy=True,noise_tables_equal=True,authorized_differences=['strategy'],common_duration_s=common,requested_horizon_s=c0['time']['horizon_s'],members={s:r['run_id'] for s,r in runs.items()},archives={s:'../'+index[k]['archive'] for s,k in keys.items()},full={},common={},limitations=['No declarar ganadora una corrida fallida; energía parcial; parámetros demostrativos'])
            for s,r in runs.items():
                samples=repo.records(r['run_id'],'samples');actions=repo.records(r['run_id'],'actuator_records')
                result['full'][s]=dict(status=r['status'],cause=r['cause'],time_s=r['time_s'],metrics=index[keys[s]]['metrics'])
                result['common'][s]=evaluate(r,samples,actions,common)
            (out/(cid+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
            if not repo.db.execute('SELECT 1 FROM comparisons WHERE comparison_id=?',(cid,)).fetchone(): repo.save_comparison(cid,result,result['members'])
    repo.close()

if __name__=='__main__':main()
