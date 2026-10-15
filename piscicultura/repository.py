"""SQLite con FK, unicidad, recibos y lotes atómicos."""
import json
import os
import platform
import sqlite3
import threading
from functools import wraps
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime,timezone


def dumps(obj): return json.dumps(obj,ensure_ascii=False,allow_nan=False,separators=(',',':'))


def process_owner():
    try: stamp=Path(f'/proc/{os.getpid()}/stat').read_text().split()[21]
    except OSError: stamp='unknown'
    return f'{platform.node()}:{os.getpid()}:{stamp}'


def owner_alive(owner):
    try:
        host,pid,stamp=owner.split(':')
        if host!=platform.node(): return True  # no afirmar muerte de un proceso remoto
        return Path(f'/proc/{pid}/stat').read_text().split()[21]==stamp
    except (OSError,ValueError,IndexError): return False


def serialized(method):
    @wraps(method)
    def wrapped(self,*args,**kwargs):
        with self.lock: return method(self,*args,**kwargs)
    return wrapped


class SQLiteRepository:
    def __init__(self,path='work/piscicultura.sqlite'):
        self.lock=threading.RLock()
        self.path=str(path)
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(self.path,check_same_thread=False)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=NORMAL')
        self.db.row_factory=sqlite3.Row
        self.fail_after=None
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY,config TEXT NOT NULL,noise TEXT NOT NULL,environment TEXT NOT NULL,status TEXT NOT NULL,cause TEXT NOT NULL,time_s REAL NOT NULL,step INTEGER NOT NULL,state TEXT NOT NULL,termination_state TEXT,owner TEXT NOT NULL,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS samples(run_id TEXT REFERENCES runs(run_id),sample_index INTEGER,time_s REAL,payload TEXT NOT NULL,PRIMARY KEY(run_id,sample_index));
        CREATE TABLE IF NOT EXISTS decisions(run_id TEXT REFERENCES runs(run_id),decision_index INTEGER,payload TEXT NOT NULL,PRIMARY KEY(run_id,decision_index));
        CREATE TABLE IF NOT EXISTS actuator_records(run_id TEXT REFERENCES runs(run_id),actuator_id TEXT,record_index INTEGER,payload TEXT NOT NULL,PRIMARY KEY(run_id,actuator_id,record_index));
        CREATE TABLE IF NOT EXISTS events(run_id TEXT REFERENCES runs(run_id),event_seq INTEGER,payload TEXT NOT NULL,PRIMARY KEY(run_id,event_seq));
        CREATE TABLE IF NOT EXISTS metrics(run_id TEXT REFERENCES runs(run_id),metric_key TEXT,payload TEXT NOT NULL,PRIMARY KEY(run_id,metric_key));
        CREATE TABLE IF NOT EXISTS command_receipts(run_id TEXT REFERENCES runs(run_id),command_id TEXT,expected_step INTEGER,result TEXT NOT NULL,PRIMARY KEY(run_id,command_id));
        CREATE TABLE IF NOT EXISTS comparisons(comparison_id TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS comparison_members(comparison_id TEXT REFERENCES comparisons(comparison_id),strategy TEXT,run_id TEXT REFERENCES runs(run_id),PRIMARY KEY(comparison_id,strategy));
        CREATE TABLE IF NOT EXISTS acknowledgments(run_id TEXT REFERENCES runs(run_id),event_seq INTEGER,acknowledged_at TEXT,PRIMARY KEY(run_id,event_seq),FOREIGN KEY(run_id,event_seq) REFERENCES events(run_id,event_seq));
        ''')
        self.mark_orphans()

    @serialized
    def mark_orphans(self):
        with self.db:
            for row in self.db.execute("SELECT run_id,owner FROM runs WHERE status IN ('RUNNING','PAUSED')").fetchall():
                if not owner_alive(row['owner']):
                    self.db.execute("UPDATE runs SET status='INTERRUPTED',cause='PROCESO_PROPIETARIO_AUSENTE' WHERE run_id=?",(row['run_id'],))

    @serialized
    def prepare(self,rid,c,noise,runtime,environment):
        with self.db:
            self.db.execute('INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(rid,c.document,dumps(noise.tolist()),dumps(environment),runtime.status,'',0,0,dumps(runtime.state.tolist()),None,process_owner(),datetime.now(timezone.utc).isoformat()))

    @serialized
    def position(self,rid):
        row=self.db.execute('SELECT step,status,time_s FROM runs WHERE run_id=?',(rid,)).fetchone()
        if row is None: raise KeyError('Corrida desconocida')
        return dict(row)

    @serialized
    def get(self,rid):
        row=self.db.execute('SELECT * FROM runs WHERE run_id=?',(rid,)).fetchone()
        if row is None: raise KeyError('Corrida desconocida')
        out=dict(row)
        for key in ['config','noise','environment','state','termination_state']:
            out[key]=json.loads(out[key]) if out[key] else None
        return out

    @serialized
    def list(self): return [dict(r) for r in self.db.execute('SELECT run_id,status,cause,time_s,step,created_at FROM runs ORDER BY created_at DESC')]

    @serialized
    def records(self,rid,table):
        orders={'samples':'sample_index','decisions':'decision_index','actuator_records':'record_index,actuator_id','events':'event_seq','metrics':'metric_key'}
        if table not in orders: raise ValueError('Tabla no consultable')
        return [json.loads(r[0]) for r in self.db.execute(f'SELECT payload FROM {table} WHERE run_id=? ORDER BY {orders[table]}',(rid,))]

    @serialized
    def receipt(self,rid,command):
        row=self.db.execute('SELECT result FROM command_receipts WHERE run_id=? AND command_id=?',(rid,command)).fetchone()
        return json.loads(row[0]) if row else None

    @serialized
    def commit_step(self,rid,command,expected,r,batch):
        with self.db:
            current=self.db.execute('SELECT step,status FROM runs WHERE run_id=?',(rid,)).fetchone()
            if current['step']!=expected or current['status'] not in ['PREPARED','RUNNING']: raise ValueError('Conflicto de paso o estado persistido')
            count=0
            def insert(sql,args):
                nonlocal count
                self.db.execute(sql,args);count+=1
                if self.fail_after is not None and count>=self.fail_after: raise sqlite3.OperationalError('FALLO_DE_ESCRITURA_INYECTADO')
            for row in batch['samples']: insert('INSERT INTO samples VALUES (?,?,?,?)',(rid,row['sample_index'],row['time_s'],dumps(row)))
            for row in batch['decisions']: insert('INSERT INTO decisions VALUES (?,?,?)',(rid,row['decision_index'],dumps(row)))
            for row in batch['actions']: insert('INSERT INTO actuator_records VALUES (?,?,?,?)',(rid,row['actuator_id'],row['record_index'],dumps(row)))
            for row in batch['events']: insert('INSERT INTO events VALUES (?,?,?)',(rid,row['event_seq'],dumps(row)))
            self.db.execute('UPDATE runs SET status=?,cause=?,time_s=?,step=?,state=?,termination_state=? WHERE run_id=?',(r.status,r.cause,r.time_s,r.k,dumps(r.state.tolist()),dumps(r.termination_state) if r.termination_state else None,rid))
            result=dict(run_id=rid,command_id=command,expected_step=expected,step=r.k,time_s=r.time_s,status=r.status,cause=r.cause)
            self.db.execute('INSERT INTO command_receipts VALUES (?,?,?,?)',(rid,command,expected,dumps(result)))
        return result

    @serialized
    def set_status(self,rid,status,cause=''):
        with self.db: self.db.execute('UPDATE runs SET status=?,cause=? WHERE run_id=?',(status,cause,rid))

    @serialized
    def save_metrics(self,rid,payload):
        with self.db: self.db.execute('INSERT OR REPLACE INTO metrics VALUES (?,?,?)',(rid,'summary',dumps(payload)))

    @serialized
    def save_comparison(self,cid,payload,members):
        with self.db:
            self.db.execute('INSERT INTO comparisons VALUES (?,?)',(cid,dumps(payload)))
            for strategy,rid in members.items(): self.db.execute('INSERT INTO comparison_members VALUES (?,?,?)',(cid,strategy,rid))

    @serialized
    def acknowledge(self,rid,seq):
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO acknowledgments VALUES (?,?,?)',(rid,seq,datetime.now(timezone.utc).isoformat()))

    @serialized
    def close(self): self.db.close()
