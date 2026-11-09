# filming → editor → export every file. needs: SECRET_OPEN=true python3 build.py; python3 -m http.server 8799 (in this folder)
import asyncio,base64,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream','--autoplay-policy=no-user-gesture-required'])
        c=await b.new_context(viewport={'width':390,'height':844},permissions=['camera','microphone'],accept_downloads=True)
        pg=await c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto('http://localhost:8799/test.html'); await pg.evaluate("localStorage.setItem('chartready',JSON.stringify({fmMode:'one',bpm:120,fmMic:true,fmCam:true,fmLay:'bubble',hpLag:0.05,hpMeas:0.05,fmBars:2,noteSound:true,clickOn:true,mix:{main:90,notes:80,acc:100,click:85,bell:70}}))"); await pg.reload(); await pg.wait_for_timeout(700)
        await pg.click('#filmBtn'); await pg.wait_for_timeout(1200)
        await pg.click('#fsGo'); await pg.wait_for_timeout(1500)
        await pg.click('#fGo'); await pg.wait_for_timeout(3000); await pg.screenshot(path='r1.png')
        await pg.wait_for_function("__nb.ED&&__nb.ED.ready",timeout=40000)
        print('placed', await pg.evaluate("(()=>{const ED=__nb.ED;return JSON.stringify({D:ED.D,how:ED.how,hp:ED.hp,dur:ED.dur,log:ED.meta.log.length,cap:ED.meta.cap&&ED.meta.cap.L.length,click:ED.clickBuf&&ED.clickBuf.duration,mic:!!ED.micBuf,hasCam:ED.hasCam})})()"))
        await pg.screenshot(path='r2.png')
        await pg.click('[data-tool=mix]'); await pg.wait_for_timeout(300); await pg.screenshot(path='r3.png')
        await pg.evaluate("document.getElementById('edPlay').click()"); await pg.wait_for_timeout(1500)
        print('preview drift', await pg.evaluate("JSON.stringify({t:__nb.edNow(),vb:document.getElementById('edBase').currentTime,vc:document.getElementById('edCam').currentTime,camT:__nb.edCamT(__nb.edNow())})"))
        await pg.evaluate("document.getElementById('edPlay').click()"); await pg.wait_for_timeout(300)
        await pg.click('#edSave'); await pg.wait_for_timeout(300)
        await pg.evaluate("document.querySelectorAll('#edOutList input:not(:disabled)').forEach(i=>{ if(!i.checked) i.click(); })"); await pg.wait_for_timeout(200)
        await pg.screenshot(path='r4.png')
        await pg.click('#edOutGo'); await pg.wait_for_timeout(1500); await pg.screenshot(path='r5.png')
        await pg.wait_for_function("!document.getElementById('fRes').hidden",timeout=90000)
        await pg.screenshot(path='r6.png')
        info=await pg.evaluate("""(async()=>{ const FILM=__nb.FILM, ctx=__nb.ctx, S=__nb.S, ED=__nb.ED; const r=[]; for(const x of FILM.out){ const o={k:x.key,type:x.blob.type,size:x.blob.size};
           try{ const ab=await ctx.decodeAudioData(await x.blob.arrayBuffer()); o.adur=+ab.duration.toFixed(3);
             // first loud moment in the track (ms)
             const d=ab.getChannelData(0); let i=0; while(i<d.length&&Math.abs(d[i])<0.05) i++; o.first=Math.round(i/ab.sampleRate*1000); }catch(e){ o.adur=null; }
           const v=document.createElement('video'); v.src=URL.createObjectURL(x.blob); await new Promise(res=>{ v.onloadedmetadata=res; v.onerror=res; setTimeout(res,3000); });
           if(!isFinite(v.duration)){ v.currentTime=1e9; await new Promise(res=>{ v.ontimeupdate=res; setTimeout(res,2000); }); }
           o.vdur=+(v.duration||0).toFixed(3); o.w=v.videoWidth; o.h=v.videoHeight; r.push(o); }
           const dec=async k=>{ const x=FILM.out.find(y=>y.key===k); return x?await ctx.decodeAudioData(await x.blob.arrayBuffer()):null; };
           const F=await dec('full'), A=await dec('app'), C=await dec('camera'), M=await dec('mic');
           const sh=(p,q)=>{ if(!p||!q) return null; const a=__nb.onsetsOf(__nb.envOf(p)), b=__nb.onsetsOf(__nb.envOf(q)); let best=-1,bd=0; for(let D=-600;D<=600;D++){ let s=0; for(let t=0;t<a.length;t++){ const u=t+D; if(u>=0&&u<b.length) s+=a[t]*b[u]; } if(s>best){best=s;bd=D;} } return bd; };
           const exp=async g=>await __nb.edMix(ED.trim.a+ED.lastExport.st,ED.trim.b-ED.trim.a,g); const XF=await exp({click:.85,notes:.8,mic:1}), XM=await exp({click:0,notes:0,mic:1}); const lagF=sh(XF,F), lagC=sh(XM,C), lagMW=sh(XM,M), lagAW=sh(await exp({click:1,notes:1,mic:0}),A);
           const lg=ED.meta.log, st=ED.lastExport.st, ex=ED.lastExport.ex;
           const evF=F?__nb.lagToTimes(__nb.onsetsOf(__nb.envOf(F)),lg.map(e=>(e.t-st)*1000).filter(t=>t>50),-300,500):null;
           const evA=A?__nb.lagToTimes(__nb.onsetsOf(__nb.envOf(A)),lg.map(e=>(e.t-(st-ex))*1000).filter(t=>t>50),-300,500):null; return JSON.stringify({files:r,exLag:S.exLag,last:ED.lastExport,lag_full:lagF,lag_cam:lagC,lag_micwav:lagMW,lag_appwav:lagAW,shift_full_vs_app:sh(F,A),shift_cam_vs_micwav:sh(C,M),events_in_full_ms:evF,events_in_appwav_ms:evA}); })()""")
        print(info)
        print('ERR',[e for e in errs if 'file:///lan' not in e and '/lan' not in e]); await b.close()
asyncio.run(main())
