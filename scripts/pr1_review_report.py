"""Contrastar la regresión nueva con los artefactos históricos, sin sobrescribirlos."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import numpy as np


def load(path): return json.loads(path.read_text())

def xml_result(path):
    root=ET.parse(path).getroot();cases=root.findall('.//testcase')
    return dict(tests=len(cases),failures=sum(c.find('failure') is not None for c in cases),errors=sum(c.find('error') is not None for c in cases),skipped=sum(c.find('skipped') is not None for c in cases),duration_s=sum(float(s.attrib.get('time',0)) for s in root.findall('testsuite')),summed_case_duration_s=sum(float(c.attrib.get('time',0)) for c in cases))


def series(path):
    with zipfile.ZipFile(path) as z:
        samples=list(csv.DictReader(io.StringIO(z.read('samples.csv').decode())))
        metrics=json.loads(z.read('metrics.json'))[0]
    columns=['x_temperature_C','x_oxygen_mg_L','x_ph','x_turbidity_NTU','x_level_m']
    return np.array([[float(r[c]) for c in columns] for r in samples]),metrics


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence-dir',type=Path,default=Path('evidence/correcciones_pr1'));args=parser.parse_args();out=args.evidence_dir
    original=load(Path('evidence/run_index.json'));current=load(out/'regression/run_index.json')
    differences={}
    for key,run in current.items():
        old_x,old_m=series(Path('evidence')/original[key]['archive']);new_x,new_m=series(out/'regression'/run['archive'])
        assert old_x.shape==new_x.shape
        dx=np.max(abs(old_x-new_x),axis=0)
        delta_j=abs(new_m['J']-old_m['J'])
        win_error=np.max(abs(np.array(new_m['window_4_12h']['iae'])-np.array(old_m['window_4_12h']['iae']))) if old_m['window_4_12h'] else None
        differences[key]=dict(max_abs_x=dx.tolist(),delta_J=delta_j,max_abs_window_iae=win_error)
        assert np.all(dx<=np.array([1e-5,1e-5,1e-6,1e-4,1e-7]))
    preserved={}
    for p,digest in load(Path('evidence/archive_manifest.json')).items():
        assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest
        preserved[p]=digest
    work_commit=subprocess.check_output(['git','rev-parse','6ac325a'],text=True).strip()
    files=subprocess.check_output(['git','ls-tree','-r','--name-only',work_commit],text=True).splitlines()
    work_files={}
    for name in files:
        expected=subprocess.check_output(['git','show',work_commit+':'+name]);data=Path(name).read_bytes()
        assert expected==data,name
        work_files[name]=hashlib.sha256(data).hexdigest()
    (out/'preservation_manifest.json').write_text(json.dumps(dict(work_commit=work_commit,work_files=work_files,original_archives=preserved,original_suite=hashlib.sha256(Path('evidence/pytest.xml').read_bytes()).hexdigest()),ensure_ascii=False,indent=2))
    code_paths=[Path('app.py'),Path('.gitignore'),Path('.streamlit/config.toml'),Path('requirements.txt'),Path('requirements-lock.txt')]
    for folder in ['piscicultura','tests','scripts']:code_paths.extend(sorted(Path(folder).glob('*.py')))
    source={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in code_paths}
    (out/'source_manifest.json').write_text(json.dumps(dict(production_commit=subprocess.check_output(['git','rev-parse','9568cc8'],text=True).strip(),files=source),indent=2))
    archives={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*.zip'))}
    (out/'archive_manifest.json').write_text(json.dumps(archives,indent=2))
    result=dict(full_suite=xml_result(out/'pytest.xml'),short_suite=xml_result(out/'pruebas_cortas.xml'),before_regressions=xml_result(out/'regresiones_antes.xml'),first_corrected_regressions=xml_result(out/'regresiones_despues.xml'),work_reproducer_after=load(out/'observaciones_despues.json'),reference_runs_compared=len(differences),differences=differences,benchmark=load(out/'regression/observations.json')['AC20'],pending=['OBS05/RNF10: falta equipo local con SSD y protocolo acreditado','Nueva revisión de Work; PR sigue en borrador, sin integración'],scientific_limits='pH y turbidez empíricos; sin validación de campo ni dosificación productiva')
    assert result['full_suite']['failures']==result['full_suite']['errors']==0
    (out/'verification_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='differences'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
