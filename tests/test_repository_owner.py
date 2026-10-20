import subprocess
import sys

from piscicultura.config import make_config
from piscicultura.repository import SQLiteRepository, owner_alive, process_owner
from piscicultura.service import SimulationService


def test_live_owner_and_second_reader_keep_running_state(tmp_path):
    assert owner_alive(process_owner())
    path=tmp_path/'live.sqlite'
    repo=SQLiteRepository(path)
    service=SimulationService(repo)
    rid=service.prepare(make_config(0,'S0','closed'))
    service.advance(rid,'first',0)
    before=repo.get(rid)
    observer=SQLiteRepository(path)
    assert observer.get(rid)==before
    service.pause(rid)
    another=SQLiteRepository(path)
    assert another.get(rid)['status']=='PAUSED'
    another.close();observer.close();repo.close()


def test_closed_process_is_interrupted_on_reopen(tmp_path):
    path=tmp_path/'orphan.sqlite'
    code='''
import sys
from piscicultura.config import make_config
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
repo=SQLiteRepository(sys.argv[1])
service=SimulationService(repo)
rid=service.prepare(make_config(0,'S0','closed'))
service.advance(rid,'first',0)
repo.close()
'''
    subprocess.run([sys.executable,'-c',code,str(path)],check=True)
    repo=SQLiteRepository(path)
    assert repo.list()[0]['status']=='INTERRUPTED'
    assert repo.list()[0]['cause']=='PROCESO_PROPIETARIO_AUSENTE'
    repo.close()


def test_unknown_permissions_and_reused_pid_are_distinguished(monkeypatch):
    owner=process_owner()
    monkeypatch.setattr('piscicultura.repository.process_stamp',lambda pid:'another-start')
    assert not owner_alive(owner)
    def denied(pid): raise PermissionError('protected process')
    monkeypatch.setattr('piscicultura.repository.process_stamp',denied)
    assert owner_alive(owner)
