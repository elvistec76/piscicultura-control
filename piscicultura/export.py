"""Exportación autónoma con configuración, ruido autoritativo y unidades."""
import csv
import io
import json
import zipfile
import hashlib
from .config import VARIABLES,UNITS
from .repository import dumps


def csv_text(rows):
    if not rows: return ''
    keys=list(dict.fromkeys(k for row in rows for k in row))
    buf=io.StringIO(newline='');writer=csv.DictWriter(buf,fieldnames=keys);writer.writeheader()
    for row in rows: writer.writerow({k:dumps(v) if isinstance(v,(list,dict,tuple)) else v for k,v in row.items()})
    return buf.getvalue()


def export_bytes(repo,rid):
    run=repo.get(rid);samples=repo.records(rid,'samples')
    flat=[]
    for s in samples:
        row=dict(run_id=rid,sample_index=s['sample_index'],time_s=s['time_s'])
        for j,(name,unit) in enumerate(zip(VARIABLES,UNITS)):
            row['x_'+name]=s['x'][j];row['y_'+name]=s['values'][j];row['quality_'+name]=s['qualities'][j]
        flat.append(row)
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        def write(name,obj): z.writestr(name,json.dumps(obj,ensure_ascii=False,allow_nan=False,indent=2))
        write('config.json',run['config'])
        noise_csv=csv_text([dict(sample_index=k,**dict(zip(VARIABLES,row))) for k,row in enumerate(run['noise'])])
        z.writestr('noise.csv',noise_csv)
        z.writestr('samples.csv',csv_text(flat))
        for name,table in [('decisions','decisions'),('actions','actuator_records'),('events','events')]:
            rows=[dict(run_id=rid,**s) for s in repo.records(rid,table)]
            z.writestr(name+'.csv',csv_text(rows))
        write('metrics.json',repo.records(rid,'metrics'))
        write('metadata.json',{k:v for k,v in run.items() if k not in ['noise','config']})
        write('manifest.json',dict(run_id=rid,metrics_status=run['metrics_status'],metrics_cause=run['metrics_cause'],spec_id=run['config']['spec_id'],spec_version=run['config']['spec_version'],model_version=run['config']['model_version'],units=dict(zip(VARIABLES,UNITS)),time_unit='s',missing='CSV vacío / JSON null, acompañado de quality',noise_sha256=hashlib.sha256(noise_csv.encode()).hexdigest(),noise_authority='noise.csv clipped epsilon; PCG64; sin generación en RK45',action_units='normalizada; medias por intervalo',ph='Modelo empírico; acciones en segundos normalizados, sin dosis reales',turbidity='Índice empírico, sin conversión a sólidos',notice='Simulación académica sin validación productiva'))
    return buf.getvalue()
