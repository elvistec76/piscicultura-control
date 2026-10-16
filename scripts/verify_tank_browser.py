"""Optional Chromium QA. Uses production records/rendering, isolated under work/.

python -m pip install playwright
python -m playwright install chromium
python scripts/verify_tank_browser.py [--browser /usr/bin/chromium]
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from piscicultura.config import make_config
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService, environment
from piscicultura.tank_view import SHAPES, render_html, snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', help='Optional installed Chromium executable')
    parser.add_argument('--out', type=Path, default=ROOT / 'work/tank-browser')
    parser.add_argument('--port', type=int, default=8503)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    report = dict(environment=environment(), checks=[], screenshots=[], errors=[], external_requests=[])
    repo = SQLiteRepository(out / 'fixtures.sqlite')
    service = SimulationService(repo)
    c = make_config(0, 'S2', 'closed')
    rid = service.prepare(c)
    service.advance(rid, 'first', 0)
    samples, actions, events = [repo.records(rid, t) for t in ('samples', 'actuator_records', 'events')]
    fixtures = {}
    for shape in SHAPES:
        data = snapshot(repo.get(rid), samples, actions, events, shape)
        fixtures[shape] = data
        (out / f'{shape}.html').write_text(render_html(data), encoding='utf-8')
    service.pause(rid)
    (out / 'paused.html').write_text(render_html(snapshot(repo.get(rid), samples, actions, events)), encoding='utf-8')
    repo.close()

    def check(condition, label):
        assert condition, label
        report['checks'].append(label)
        print('PASS: ' + label, flush=True)

    with sync_playwright() as p:
        options = dict(headless=True, args=['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        if args.browser:
            options['executable_path'] = args.browser
        browser = p.chromium.launch(**options)
        report['browser'] = browser.version
        # File fixtures run with all network access disabled, including CDN access.
        context = browser.new_context(viewport=dict(width=1440, height=1050), offline=True)
        page = context.new_page()
        page.on('pageerror', lambda error: report['errors'].append(str(error)))
        page.on('request', lambda request: report['external_requests'].append(request.url) if request.url.startswith(('http:', 'https:')) else None)
        for shape in SHAPES:
            page.set_content((out / f'{shape}.html').read_text(encoding='utf-8'))
            page.wait_for_function('window.__aquacontrol !== undefined')
            check(page.evaluate('window.__aquacontrol.mode') == '3D', shape + ' WebGL offline')
            check(page.locator('.sensor').count() == 5 and page.locator('.actuator-row').count() == 8, shape + ' five sensors/eight actuators')
            check(page.evaluate('window.__aquacontrol.snapshot') == fixtures[shape], shape + ' unmodified confirmed snapshot')
            before = page.evaluate('window.__aquacontrol.camera.position.toArray()')
            page.get_by_role('button', name='Rotar a la derecha', exact=True).click()
            page.get_by_role('button', name='Acercar', exact=True).click()
            check(page.evaluate('window.__aquacontrol.camera.position.toArray()') != before, shape + ' rotation and zoom')
            page.get_by_role('button', name='Restablecer cámara', exact=True).click()
            page.locator('.dashboard').screenshot(path=str(out / f'{shape}-3D.png'))
            report['screenshots'].append(f'{shape}-3D.png')
            page.wait_for_function('window.__aquacontrol.frames >= 2')
            check(page.evaluate('window.__aquacontrol.snapshot.state_time_s') == 60, shape + ' animation leaves physical time fixed')
            # Actual context loss must switch to SVG without changing data.
            page.evaluate("window.__aquacontrol.renderer.getContext().getExtension('WEBGL_lose_context').loseContext()")
            page.wait_for_function("window.__aquacontrol.mode === '2.5D'")
            check(page.locator('#fallback svg').count() == 1, shape + ' fallback after context loss')
            page.close()
            page = context.new_page()
            page.on('pageerror', lambda error: report['errors'].append(str(error)))
            page.on('request', lambda request: report['external_requests'].append(request.url) if request.url.startswith(('http:', 'https:')) else None)
        page.set_content((out / 'paused.html').read_text(encoding='utf-8'))
        page.wait_for_function('window.__aquacontrol !== undefined')
        page.wait_for_function('window.__aquacontrol.frames >= 2')
        check(page.evaluate('!window.__aquacontrol.static'), 'paused snapshot supports decorative ambient motion')
        # WebGL unavailable from startup: exercise automatic fallback for both shapes.
        no_gl = browser.new_context(viewport=dict(width=1440, height=1050), offline=True)
        for shape in SHAPES:
            # set_content does not execute add_init_script, so create a fresh
            # document with the WebGL guard before the complete local renderer.
            content = (out / f'{shape}.html').read_text(encoding='utf-8')
            guard = "<script>const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return type.includes('webgl')?null:original.call(this,type,...args);};</script>"
            fallback_page = no_gl.new_page()
            fallback_page.set_content(content.replace('<head>', '<head>' + guard, 1))
            fallback_page.wait_for_function("window.__aquacontrol?.mode === '2.5D'")
            check(fallback_page.locator('#fallback svg').count() == 1, shape + ' automatic fallback without WebGL')
            fallback_page.locator('.dashboard').screenshot(path=str(out / f'{shape}-2.5D.png'))
            report['screenshots'].append(f'{shape}-2.5D.png')
            fallback_page.close()
        # A real Streamlit process and new DB: switch native widgets repeatedly.
        env = dict(os.environ, PISCICULTURA_DB=str(out / f'ui-{time.time_ns()}.sqlite'))
        log = (out / 'streamlit.log').open('w')
        server = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', str(ROOT / 'app.py'), '--server.port', str(args.port), '--server.fileWatcherType', 'none'], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            base = f'http://127.0.0.1:{args.port}'
            deadline = time.monotonic() + 30
            while True:
                try:
                    with urllib.request.urlopen(base + '/_stcore/health', timeout=1) as response:
                        if response.status == 200: break
                except OSError:
                    if time.monotonic() > deadline: raise
                    time.sleep(.2)
            ui_context = browser.new_context(viewport=dict(width=1600, height=1100))
            ui_context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(base) else route.abort())
            ui = ui_context.new_page()
            ui.on('pageerror', lambda error: report['errors'].append(str(error)))
            ui.goto(base)
            def idle():
                ui.wait_for_function("document.querySelector('[data-testid=stApp]')?.getAttribute('data-test-script-state') === 'notRunning'", timeout=30000)
            ui.get_by_role('button', name='Validar y preparar corrida').wait_for(timeout=30000)
            idle()
            ui.get_by_role('combobox', name='Escenario', exact=True).click()
            ui.get_by_role('option', name='S2 · Recuperación', exact=True).click()
            idle()
            ui.get_by_role('button', name='Validar y preparar corrida').click()
            idle()
            ui.get_by_role('tab', name='Ejecución y evolución', exact=True).click()
            ui.get_by_role('button', name='Avanzar un intervalo', exact=True).click()
            idle()
            ui.get_by_role('tab', name='Vista del estanque', exact=True).click()
            def frame():
                f = ui.get_by_title('AquaControl: estanque, sensores y actuadores').content_frame
                f.locator('#state-time').filter(has_text='60 s').wait_for(timeout=30000)
                return f
            for shape in ['Rectangular', 'Circular', 'Rectangular', 'Circular']:
                ui.get_by_role('combobox', name='Representación', exact=True).click()
                ui.get_by_role('option', name=shape, exact=True).click()
                f = frame()
                f.locator('#shape-label').filter(has_text=shape).wait_for()
                idle()
                check(f.locator('#run-badge').inner_text() == 'EN EJECUCIÓN', 'Streamlit switch ' + shape + ' keeps running')
            ui.get_by_role('combobox', name='Representación', exact=True).click()
            ui.get_by_role('option', name='Rectangular', exact=True).click()
            frame().locator('#shape-label').filter(has_text='Rectangular').wait_for()
            idle()
            ui.get_by_role('tab', name='Ejecución y evolución', exact=True).click()
            ui.get_by_role('button', name='Pausar', exact=True).click()
            idle()
            ui.get_by_role('tab', name='Vista del estanque', exact=True).click()
            frame().locator('#run-badge').filter(has_text='PAUSADA').wait_for()
            check('Modo ambiente' in frame().locator('#motion-label').inner_text(), 'Streamlit pause retains optional decorative motion')
            check(ui.get_by_test_id('stException').count() == 0, 'Streamlit repeated renders have no exception')
            # Capture after interactions: scrolling a tall iframe into view for
            # a screenshot can displace an open native select popover.
            ui.get_by_title('AquaControl: estanque, sensores y actuadores').screenshot(path=str(out / 'Streamlit-Rectangular.png'))
            report['screenshots'].append('Streamlit-Rectangular.png')
            ui_context.close()
        finally:
            server.terminate()
            server.wait(timeout=15)
            log.close()
        context.close()
        no_gl.close()
        browser.close()
    check(not report['external_requests'], 'no external requests in offline scenes')
    check(not report['errors'], 'no browser JavaScript exceptions')
    report['source_sha256'] = {str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [ROOT/'app.py',ROOT/'piscicultura/tank_view.py',*sorted((ROOT/'piscicultura/tank_assets').rglob('*'))] if path.is_file()}
    (out / 'browser-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(checks=len(report['checks']), screenshots=report['screenshots'], errors=report['errors'], report=str(out/'browser-results.json')),ensure_ascii=False))


if __name__ == '__main__':
    main()
