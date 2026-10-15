"""Casos de uso: tiempo por comando, publicación atómica y comparación."""
import uuid
import json
import sqlite3
import platform
import importlib.metadata
import numpy as np
import threading
from . import __version__
from .repository import serialized
from .config import RunConfig
from .engine import initial,advance
from .scenarios import noise_table
from .metrics import evaluate

TERMINAL={'COMPLETED','FAILED','STOPPED','INTERRUPTED'}


def environment():
    return dict(python=platform.python_version(),platform=platform.platform(),sqlite=sqlite3.sqlite_version,code=__version__,packages={p:importlib.metadata.version(p) for p in ['numpy','scipy','pandas','plotly','streamlit','pytest']})


class SimulationService:
    def __init__(self,repository): self.lock=threading.RLock();self.repo=repository;self.active={}

    @serialized
    def prepare(self,draft,noise=None):
        cfg=RunConfig.freeze(draft); c=cfg.data;runtime=initial(c)
        noise=noise_table(c) if noise is None else np.array(noise,copy=True)
        expected=(int(c['time']['horizon_s']/c['time']['control_interval_s'])+1,5)
        if noise.shape!=expected or not np.isfinite(noise).all() or np.max(abs(noise))>3: raise ValueError('Tabla de ruido inválida')
        noise.setflags(write=False)
        rid=uuid.uuid4().hex
        self.repo.prepare(rid,cfg,noise,runtime,environment())
        self.active[rid]=(c,noise,runtime)
        return rid

    @serialized
    def advance(self,rid,command_id,expected_step):
        receipt=self.repo.receipt(rid,command_id)
        if receipt:
            if receipt['expected_step']!=expected_step: raise ValueError('command_id reutilizado con otro paso')
            return receipt
        if rid not in self.active: raise ValueError('Corrida disponible solo para consulta; sin sesión activa')
        c,noise,old=self.active[rid]
        if old.status not in ['PREPARED','RUNNING'] or old.k!=expected_step: raise ValueError('Conflicto de estado o paso esperado')
        if self.repo.position(rid)['step']!=old.k: raise ValueError('Conflicto del propietario')
        new,batch=advance(old,c,noise)
        try: result=self.repo.commit_step(rid,command_id,expected_step,new,batch)
        except sqlite3.Error as exc:
            old.status='FAILED';old.cause='ERROR_PERSISTENCIA: '+str(exc)
            try: self.repo.set_status(rid,'FAILED',old.cause)
            except sqlite3.Error: pass
            raise RuntimeError(old.cause) from exc
        self.active[rid]=(c,noise,new)
        if new.status in TERMINAL: self.compute_metrics(rid)
        return result

    @serialized
    def pause(self,rid):
        c,n,r=self.active[rid]
        if r.status!='RUNNING': raise ValueError('Solo se pausa una corrida en ejecución')
        self.repo.set_status(rid,'PAUSED');r.status='PAUSED'

    @serialized
    def resume(self,rid):
        c,n,r=self.active[rid]
        if r.status!='PAUSED': raise ValueError('Corrida no pausada')
        self.repo.set_status(rid,'RUNNING');r.status='RUNNING'

    @serialized
    def stop(self,rid):
        c,n,r=self.active[rid]
        if r.status not in ['PREPARED','RUNNING','PAUSED']: raise ValueError('Corrida terminal')
        self.repo.set_status(rid,'STOPPED','DETENCION_SOLICITADA');r.status='STOPPED';r.cause='DETENCION_SOLICITADA';self.compute_metrics(rid)

    @serialized
    def run_all(self,rid):
        c,n,r=self.active[rid]
        while r.status in ['PREPARED','RUNNING']:
            self.advance(rid,f'interval-{r.k}',r.k);r=self.active[rid][2]
        return self.repo.get(rid)

    @serialized
    def compute_metrics(self,rid):
        result=evaluate(self.repo.get(rid),self.repo.records(rid,'samples'),self.repo.records(rid,'actuator_records'))
        self.repo.save_metrics(rid,result)
        return result

    @serialized
    def compare(self,draft):
        from copy import deepcopy
        members={};table=noise_table(draft)
        for strategy in ['open','closed']:
            c=deepcopy(draft);c['strategy']=strategy
            rid=self.prepare(c,table);self.run_all(rid);members[strategy]=rid
        cid=uuid.uuid4().hex
        common=min(self.repo.get(r)['time_s'] for r in members.values())
        payload=dict(comparison_id=cid,members=members,authorized_differences=['strategy'],requested_horizon_s=draft['time']['horizon_s'],common_duration_s=common,common={},full={},limitations=['No declarar ganadora una corrida fallida; energía parcial; parámetros demostrativos'])
        for strategy,rid in members.items():
            run=self.repo.get(rid); samples=self.repo.records(rid,'samples');actions=self.repo.records(rid,'actuator_records')
            payload['common'][strategy]=evaluate(run,samples,actions,common)
            payload['full'][strategy]=dict(status=run['status'],cause=run['cause'],time_s=run['time_s'],metrics=self.compute_metrics(rid))
        self.repo.save_comparison(cid,payload,members)
        return payload
