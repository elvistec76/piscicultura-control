"""Offline Chromium verification using genuine records in an isolated QA DB.

Not an RNF10 benchmark. Requires optional Playwright and installed Chromium.
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
from piscicultura.config import event, make_config
from piscicultura.replay import load_history
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from piscicultura.tank_view import render_html, snapshot, SHAPES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', default='/usr/bin/chromium')
    parser.add_argument('--out', type=Path, default=ROOT / 'work/replay-browser')
    parser.add_argument('--skip-ui', action='store_true')
    args = parser.parse_args()
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    report = dict(checks=[], errors=[], external_requests=[], screenshots=[], rnf10='PENDIENTE', platform=sys.platform)

    def check(condition, label):
        assert condition, label
        report['checks'].append(label); print('PASS: '+label, flush=True)

    repo = SQLiteRepository(out / f'fixtures-{time.time_ns()}.sqlite')
    service = SimulationService(repo)
    c = make_config(0, 'S0', 'open'); c['time']['horizon_s'] = 3600
    c['events'] = [event('missing', 1, 60, 120, 1, '1'), event('availability', 2, 60, 120, 0, '1')]
    rid = service.prepare(c); service.run_all(rid)
    history = load_history(repo.path, rid)
    before = '\n'.join(repo.db.iterdump()); changes = repo.db.total_changes
    for shape in SHAPES:
        data = snapshot(history['run'], history['samples'], history['actuator_records'], history['events'], shape)
        data['history'] = history
        (out / f'{shape}.html').write_text(render_html(data), encoding='utf-8')

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=args.browser, headless=True, args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
            report['browser'] = browser.version
            context = browser.new_context(viewport=dict(width=1440, height=1300), offline=True)
            for shape in SHAPES:
                page = context.new_page()
                page.on('pageerror', lambda e: report['errors'].append(str(e)))
                page.on('request', lambda r: report['external_requests'].append(r.url) if r.url.startswith(('http:', 'https:')) else None)
                page.set_content((out / f'{shape}.html').read_text(encoding='utf-8'))
                page.wait_for_function("window.__aquacontrol?.mode==='3D'")
                check(page.locator('.sensor').count()==5 and page.locator('.actuator-row').count()==8, shape+' five variables / eight actuators')
                check(page.evaluate('window.__aquacontrol.snapshot.status')=='COMPLETED', shape+' completed stored run')
                page.wait_for_function('window.__aquacontrol.frames>2')
                initial = page.evaluate('({fish:__aquacontrol.fish[0].group.position.toArray(),tail:__aquacontrol.fish[0].tail.rotation.y,water:Array.from(__aquacontrol.surface.geometry.attributes.position.array),h:__aquacontrol.surface.position.y,time:__aquacontrol.snapshot.state_time_s})')
                frame_start=page.evaluate('__aquacontrol.frames')
                page.wait_for_function(f'__aquacontrol.frames>={frame_start+2}')
                after = page.evaluate('({fish:__aquacontrol.fish[0].group.position.toArray(),tail:__aquacontrol.fish[0].tail.rotation.y,water:Array.from(__aquacontrol.surface.geometry.attributes.position.array),h:__aquacontrol.surface.position.y,time:__aquacontrol.snapshot.state_time_s})')
                displacement = sum((a-b)**2 for a,b in zip(initial['fish'], after['fish']))**.5
                check(displacement>.025 and initial['tail']!=after['tail'], shape+' perceptible swimming and tail motion')
                check(initial['water']!=after['water'] and initial['h']==after['h'] and initial['time']==after['time'], shape+' waves move / exact level and time fixed')
                page.locator('#ambient').uncheck()
                page.wait_for_timeout(200)
                frozen=page.evaluate('__aquacontrol.frames'); page.wait_for_timeout(300)
                check(page.evaluate('__aquacontrol.frames')==frozen, shape+' ambient off stops frame scheduling')
                page.evaluate('__aquacontrol.seek(90)')
                check(page.evaluate('__aquacontrol.snapshot.sample_time_s')==60, shape+' retained sample time')
                check(page.evaluate('__aquacontrol.snapshot.sensors[1].value') is None, shape+' missing measurement stays missing')
                check(page.evaluate('__aquacontrol.bubbles.every(b=>!b.mesh.visible)'), shape+' failed aeration has no bubbles')
                page.locator('#selected-time').fill('30');page.locator('#selected-time').press('Tab')
                check(page.evaluate('__aquacontrol.player.time')==30, shape+' precise instant input')
                page.locator('#next').click(); check(page.evaluate('__aquacontrol.player.time')==60, shape+' next registered instant')
                page.locator('#previous').click(); check(page.evaluate('__aquacontrol.player.time')==0, shape+' previous registered instant')
                page.locator('#speed').select_option('10');page.locator('#play').click()
                page.wait_for_function('__aquacontrol.player.time>2')
                page.locator('#pause').click(); paused=page.evaluate('__aquacontrol.player.time'); page.wait_for_timeout(250)
                check(page.evaluate('__aquacontrol.player.time')==paused, shape+' playback pause')
                page.locator('#restart').click();check(page.evaluate('__aquacontrol.player.time')==0 and page.evaluate('__aquacontrol.player.elapsed')==0, shape+' restart resets both clocks')
                page.evaluate('__aquacontrol.seek(120)')
                page.wait_for_function("document.getElementById('state-chart').layout.shapes[0].x0===120")
                check(page.evaluate("document.getElementById('action-chart').layout.shapes[0].x0") == 120, shape+' synchronized chart cursors')
                page.evaluate("document.getElementById('state-chart').emit('plotly_click',{points:[{x:600}]})")
                check(page.evaluate('__aquacontrol.player.time')==600, shape+' chart point selects time')
                for q,shadow,count in [('low',False,5),('medium',False,9),('high',True,13)]:
                    state=page.evaluate('JSON.stringify(__aquacontrol.snapshot.state)')
                    page.locator('#quality').select_option(q)
                    check(page.evaluate('__aquacontrol.renderer.shadowMap.enabled')==shadow and page.evaluate('__aquacontrol.fish.filter(f=>f.group.visible).length')==count and page.evaluate('JSON.stringify(__aquacontrol.snapshot.state)')==state, shape+' visual-only quality '+q)
                page.locator('#quality').select_option('medium');page.locator('#ambient').check()
                page.locator('#presentation').click()
                check(page.locator('body').evaluate("e=>e.classList.contains('presentation')"), shape+' presentation enter')
                page.locator('#presentation').click()
                check(not page.locator('body').evaluate("e=>e.classList.contains('presentation')"), shape+' presentation exit')
                page.locator('#guide-next').click();check(page.evaluate('__aquacontrol.player.time')==0, shape+' guided initial state')
                page.locator('#guide-next').click();check(page.evaluate('__aquacontrol.player.time')==60, shape+' guided existing injection')
                page.evaluate('__aquacontrol.seek(600)');page.evaluate('window.scrollTo(0,0)')
                page.screenshot(path=str(out / f'{shape}-dashboard.png'), full_page=True);report['screenshots'].append(f'{shape}-dashboard.png')
                # Visibility of the entire iframe, including when a Streamlit tab is hidden.
                page.evaluate("document.body.style.display='none'");page.wait_for_function('__aquacontrol.suspended')
                frame=page.evaluate('__aquacontrol.frames');page.wait_for_timeout(250)
                check(page.evaluate('__aquacontrol.frames')==frame, shape+' hidden view stops scheduling')
                page.evaluate("document.body.style.display=''")
                page.wait_for_function('!__aquacontrol.suspended')
                page.evaluate("__aquacontrol.renderer.getContext().getExtension('WEBGL_lose_context').loseContext()")
                page.wait_for_function("__aquacontrol.mode==='2.5D'")
                page.evaluate('__aquacontrol.seek(90)')
                check(page.locator('#fallback svg').count()==1 and page.evaluate('__aquacontrol.snapshot.sample_time_s')==60, shape+' context loss preserves replay in 2.5D')
                page.screenshot(path=str(out / f'{shape}-2.5D.png'),full_page=True);report['screenshots'].append(f'{shape}-2.5D.png')
                page.close()
            reduced=browser.new_context(viewport=dict(width=1440,height=1100),offline=True,reduced_motion='reduce')
            page=reduced.new_page();page.set_content((out/'Circular.html').read_text(encoding='utf-8'));page.wait_for_function("window.__aquacontrol?.mode==='3D'")
            page.wait_for_timeout(250);check(page.evaluate('__aquacontrol.frames')==0 and not page.locator('#ambient').is_checked(),'system reduced motion respected')
            page.locator('#play').click();page.wait_for_function('__aquacontrol.player.time>1');page.locator('#pause').click()
            check(page.evaluate('__aquacontrol.fish[0].tail.rotation.y')==0,'reduced motion allows replay without decorative tail motion')
            page.close();reduced.close();context.close()
            if not args.skip_ui:
                verify_streamlit(browser, out, repo.path, rid, check, report)
            browser.close()
        check(repo.db.total_changes==changes and '\n'.join(repo.db.iterdump())==before,'playback leaves all SQLite records unchanged')
        check(not report['external_requests'],'offline renderer makes no external requests')
        check(not report['errors'],'no JavaScript exceptions')
    finally:
        repo.close()
        report['source_sha256']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'app.py',ROOT/'piscicultura/replay.py',ROOT/'piscicultura/tank_view.py',*sorted((ROOT/'piscicultura/tank_assets').glob('*.*'))]}
        (out/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')


def verify_streamlit(browser,out,db,rid,check,report):
    env=dict(os.environ,PISCICULTURA_DB=str(db))
    with (out/'streamlit.log').open('w') as log:
        server=subprocess.Popen([sys.executable,'-m','streamlit','run',str(ROOT/'app.py'),'--server.port','8504','--server.fileWatcherType','none'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        try:
            base='http://127.0.0.1:8504';deadline=time.monotonic()+30
            while True:
                try:
                    urllib.request.urlopen(base+'/_stcore/health',timeout=1).close();break
                except OSError:
                    if time.monotonic()>deadline:raise
                    time.sleep(.2)
            context=browser.new_context(viewport=dict(width=1600,height=1100))
            context.set_default_timeout(90000)
            context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(base) else route.abort())
            page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
            page.on('request',lambda r:report['external_requests'].append(r.url) if r.url.startswith(('http:','https:')) and not r.url.startswith(base) else None)
            page.goto(base)
            page.get_by_role('tab',name='Vista del estanque',exact=True).click()
            frame=page.get_by_title('AquaControl: estanque, sensores y actuadores').content_frame
            frame.locator('#run-badge').filter(has_text='COMPLETADA').wait_for(timeout=90000)
            check(frame.locator('.sensor').count()==5,'Streamlit historical run rendered from SQLite')
            frame.locator('#ambient').uncheck();frame.locator('#restart').click();frame.locator('#play').click()
            frame.locator('#pause').click();check(frame.locator('#playback-status').inner_text()=='EN PAUSA','Streamlit playback controls')
            page.get_by_role('tab',name='Configuración',exact=True).click()
            # Use the frame itself: visibility is propagated across a hidden tab.
            handle=page.frames[1]
            handle.wait_for_function('__aquacontrol.suspended')
            check(handle.evaluate('__aquacontrol.suspended'),'Streamlit hidden tab suspends renderer')
            page.get_by_role('tab',name='Vista del estanque',exact=True).click()
            # Streamlit's visible label covers the native input. Exercise its
            # supported keyboard interaction instead of clicking through it.
            page.get_by_label('Modo presentación académica',exact=True).focus()
            page.get_by_label('Modo presentación académica',exact=True).press('Space')
            page.wait_for_function("document.querySelectorAll('[role=tab]').length===0")
            check(page.get_by_role('button',name='Validar y preparar corrida',exact=True).count()==0,'Streamlit presentation hides forms')
            frame=page.get_by_title('AquaControl: estanque, sensores y actuadores').content_frame
            frame.locator('#run-badge').filter(has_text='COMPLETADA').wait_for(timeout=90000)
            check(frame.locator('.sensor').count()==5 and frame.locator('.actuator-row').count()==8,'Streamlit presentation preserves variables and channels')
            page.get_by_label('Modo presentación académica',exact=True).focus()
            page.get_by_label('Modo presentación académica',exact=True).press('Space')
            page.get_by_role('tab',name='Vista del estanque',exact=True).wait_for()
            check(page.get_by_role('tab').count()==5,'Streamlit presentation returns to all tabs')
            page.get_by_role('tab',name='Vista del estanque',exact=True).click()
            page.get_by_title('AquaControl: estanque, sensores y actuadores').screenshot(path=str(out/'Streamlit-dashboard.png'))
            report['screenshots'].append('Streamlit-dashboard.png')
            check(page.get_by_test_id('stException').count()==0,'Streamlit no exceptions')
            context.close()
        finally:
            server.terminate();server.wait(timeout=15)


if __name__=='__main__':
    main()
