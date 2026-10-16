"""Historical presentation input. Opens SQLite read-only, never a service/repository.

One read transaction keeps samples, decisions, intervals and events coherent even
when the execution tab is committing another interval. No model/control imports.
"""
import json
import sqlite3
from contextlib import closing
from pathlib import Path


def load_history(path, run_id):
    uri = Path(path).resolve().as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True)) as db:
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        row = db.execute('SELECT run_id,config,status,cause,time_s,state FROM runs WHERE run_id=?', (run_id,)).fetchone()
        if row is None:
            raise KeyError('Corrida desconocida')
        run = dict(row)
        for key in ('config', 'state'):
            run[key] = json.loads(run[key])
        result = dict(run=run)
        for table, order in [('samples', 'sample_index'), ('decisions', 'decision_index'),
                             ('actuator_records', 'record_index,actuator_id'), ('events', 'event_seq')]:
            result[table] = [json.loads(r[0]) for r in db.execute(
                f'SELECT payload FROM {table} WHERE run_id=? ORDER BY {order}', (run_id,))]
        return result
