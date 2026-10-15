import argparse
from pathlib import Path
import json
from .config import make_config,RunConfig
from .repository import SQLiteRepository
from .service import SimulationService
from .export import export_bytes


def main():
    p=argparse.ArgumentParser(description='Simulador académico local de piscicultura')
    p.add_argument('--scenario',default='S2');p.add_argument('--profile',type=int,choices=[0,1,2],default=0)
    p.add_argument('--strategy',choices=['open','closed'],default='closed')
    p.add_argument('--config',type=Path);p.add_argument('--db',default='work/piscicultura.sqlite')
    p.add_argument('--output',type=Path,default=Path('work/exports'));p.add_argument('--compare',action='store_true')
    args=p.parse_args();c=json.loads(args.config.read_text()) if args.config else make_config(args.profile,args.scenario,args.strategy)
    repo=SQLiteRepository(args.db);s=SimulationService(repo);args.output.mkdir(parents=True,exist_ok=True)
    if args.compare:
        result=s.compare(c);(args.output/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
        ids=result['members'].values()
    else:
        rid=s.prepare(c);result=s.run_all(rid);ids=[rid]
    for rid in ids:
        (args.output/(rid+'.zip')).write_bytes(export_bytes(repo,rid));run=repo.get(rid)
        print(rid,run['status'],run['time_s'],run['cause'])
    repo.close()

if __name__=='__main__': main()
