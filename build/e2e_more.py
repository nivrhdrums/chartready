import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto('file:///tmp/claude-0/build/test.html'); await pg.wait_for_timeout(800)
        n=0
        async def shot(t):
            nonlocal n; n+=1; await pg.screenshot(path=f'/tmp/claude-0/build/m{n:02d}.png'); print(n,t)
        bx=await pg.locator('#dynTile').bounding_box()
        await pg.mouse.move(bx['x']+30,bx['y']+30); await pg.mouse.down(); await pg.wait_for_timeout(800); await pg.mouse.up(); await pg.wait_for_timeout(400); await shot('dyn long')
        await pg.click('#popClose'); await pg.wait_for_timeout(300)
        await pg.click('#rulerNum'); await pg.wait_for_timeout(400); await shot('tempo')
        for d in '3','5','0': await pg.click(f'#pop [data-t="{d}"]')
        await pg.wait_for_timeout(200); await shot('tempo 350')
        await pg.click('#pop [data-t="ok"]'); await pg.wait_for_timeout(300); print('bpm',await pg.evaluate("document.getElementById('qBpm').textContent"))
        await pg.click('#tabSet'); await pg.wait_for_timeout(300)
        for st in ['snd','view','about']:
            await pg.click(f'#stabs [data-st="{st}"]'); await pg.wait_for_timeout(300); await shot('set '+st)
        await pg.click('#remLock'); await pg.wait_for_timeout(300); await shot('secret panel')
        await pg.click('#stabs [data-st="read"]'); await pg.click('#sheet .go, #calBtn', timeout=2000); await pg.wait_for_timeout(500); await shot('calib')
        print('ERR',errs); await b.close()
asyncio.run(main())
