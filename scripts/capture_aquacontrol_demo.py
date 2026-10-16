"""Capture a real stored QA run, responsive fallback and an optional short video.

All generated data/assets stay in work/. No functional database is opened.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from piscicultura.config import make_config,event
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from piscicultura.replay import load_history
from piscicultura.tank_view import snapshot,render_html,SHAPES


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser',default='/usr/bin/chromium')
    parser.add_argument('--out',type=Path,default=ROOT/'work/aquacontrol-demo')
    parser.add_argument('--video',action='store_true')
    args=parser.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    repo=SQLiteRepository(out/f'qa-{time.time_ns()}.sqlite')
    try:
        c=make_config(0,'S2','closed');c['time']['horizon_s']=3600
        c['events'].append(event('feed','water',120,600,2.,'1'))
        service=SimulationService(repo);rid=service.prepare(c);service.run_all(rid)
        before='\n'.join(repo.db.iterdump());history=load_history(repo.path,rid)
        from playwright.sync_api import sync_playwright
        report=dict(run_id=rid,fixture='S2 closed, 1 h, registered feed at [120,600) s; QA data, not field observations',screenshots=[],checks=[],video=None,errors=[],external_requests=[],rnf10='PENDIENTE')
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=args.browser,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
            context=browser.new_context(viewport=dict(width=1440,height=1240),offline=True)
            page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
            page.on('request',lambda r:report['external_requests'].append(r.url) if r.url.startswith(('http:','https:')) else None)
            for shape in SHAPES:
                data=snapshot(history['run'],history['samples'],history['actuator_records'],history['events'],shape);data['history']=history
                page.set_content(render_html(data));page.wait_for_function("window.__aquacontrol?.mode==='3D'")
                page.locator('#quality').select_option('low');page.evaluate('__aquacontrol.seek(600)')
                page.locator('#guide').select_option('1')
                page.evaluate('__aquacontrol.seek(600)')
                assert page.locator('#guide').input_value()=='' # no stale guide step after a manual seek
                page.locator('#ambient').uncheck()
                page.screenshot(path=str(out/f'{shape}-demostracion.png'),full_page=True)
                report['screenshots'].append(f'{shape}-demostracion.png')
                if shape=='Circular':
                    page.locator('a[href="#decision-detail"]').click();assert page.locator('#decision-detail').evaluate('e=>e.open')
                    page.locator('#decision-detail').screenshot(path=str(out/'decisiones.png'));report['screenshots'].append('decisiones.png')
                report['checks'].append(shape+' stored closed-loop dashboard and coherent guide selection')
            # Reduced-motion changes must stop already scheduled decorative frames.
            page.evaluate('window.scrollTo(0,0)');page.locator('#ambient').check();page.emulate_media(reduced_motion='reduce')
            page.wait_for_function('__aquacontrol.static');assert not page.locator('#ambient').is_checked()
            count=page.evaluate('__aquacontrol.frames');page.wait_for_timeout(250);assert page.evaluate('__aquacontrol.frames')==count
            report['checks'].append('dynamic system reduced motion cancels pending animation')
            page.emulate_media(reduced_motion='no-preference')
            if args.video and shutil.which('ffmpeg'):
                page.evaluate('window.scrollTo(0,0)');page.locator('#ambient').check();page.locator('#speed').select_option('300')
                page.locator('#restart').click();page.locator('#play').click();page.evaluate('window.scrollTo(0,0)')
                frames=out/'frames';frames.mkdir(exist_ok=True)
                for index in range(24):
                    page.wait_for_timeout(200);page.screenshot(path=str(frames/f'frame_{index:03d}.png'))
                page.locator('#pause').click()
                subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','4','-i',str(frames/'frame_%03d.png'),'-c:v','libx264','-pix_fmt','yuv420p',str(out/'demostracion.mp4')],check=True)
                report['video']='demostracion.mp4';report['video_note']='6-second sequence of browser captures; rendering speed is not an RNF10 measurement'
            context.close()
            mobile=browser.new_context(viewport=dict(width=390,height=900),offline=True)
            mobile_page=mobile.new_page()
            data=snapshot(history['run'],history['samples'],history['actuator_records'],history['events'],'Circular',True);data['history']=history
            mobile_page.set_content(render_html(data));mobile_page.wait_for_function("window.__aquacontrol?.mode==='2.5D'")
            assert mobile_page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
            assert mobile_page.locator('.sensor').count()==5 and mobile_page.locator('.actuator-row').count()==8
            mobile_page.screenshot(path=str(out/'movil-2.5D.png'),full_page=True);report['screenshots'].append('movil-2.5D.png')
            report['checks'].append('390px responsive fallback without horizontal document overflow')
            mobile.close();browser.close()
        assert '\n'.join(repo.db.iterdump())==before
        assert not report['errors'] and not report['external_requests']
        report['checks'].extend(['no SQLite changes during captures','no JavaScript errors or external requests'])
        (out/'demo-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False,indent=2))
    finally:
        repo.close()


if __name__=='__main__':main()
