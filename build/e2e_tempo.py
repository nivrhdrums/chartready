import asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('http://localhost:8799/test.html'); await pg.wait_for_timeout(600)
        for tab,setup in [('tabMet',"__nb.S.mSub=1"),('tabGen',"__nb.S.countIn=false;__nb.S.noteSound=false")]:
            await pg.click('#'+tab); await pg.evaluate(setup+";__nb.setBpm(60)")
            await pg.evaluate("window.__log=[]; const T=__nb; setInterval(()=>{ T.TRK.forEach(x=>{ if(!x.seen){ x.seen=1; window.__log.push(+x.t.toFixed(4)); } }); },5)")
            await pg.click('#play'); await pg.wait_for_timeout(2300)
            t=await pg.evaluate("__nb.ctx.currentTime"); await pg.evaluate("__nb.setBpm(120)"); await pg.wait_for_timeout(2600)
            await pg.click('#play'); await pg.wait_for_timeout(200)
            L=await pg.evaluate("window.__log"); now=t
            # what was actually left after the change: drop cancelled entries (they were queued past the change)
            print(tab,'change at',round(now,3))
            print(' clicks:',[round(x-now,3) for x in L])
        print('ERR',errs); await b.close()
asyncio.run(main())
