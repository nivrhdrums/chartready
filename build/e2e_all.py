import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required','--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto('file:///tmp/claude-0/build/test.html'); await pg.wait_for_timeout(800)
        n=0
        async def shot(tag):
            nonlocal n; n+=1; await pg.screenshot(path=f'/tmp/claude-0/build/a{n:02d}.png'); print(n,tag)
        async def pops(tab):
            keys=await pg.evaluate("[...new Set([...document.querySelectorAll('[data-pop]')].filter(e=>e.offsetParent).map(e=>e.dataset.pop))]")
            for k in keys:
                await pg.evaluate(f"[...document.querySelectorAll('[data-pop=\"{k}\"]')].find(e=>e.offsetParent).click()"); await pg.wait_for_timeout(350); await shot(f'{tab}:{k}')
                await pg.evaluate("document.getElementById('popClose').click()"); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
        await shot('gen'); await pops('gen')
        await pg.click('#dynTile'); await pg.wait_for_timeout(300); await shot('dyn popup'); await pg.evaluate("document.getElementById('dynOn').click()"); await pg.click('#popClose'); await pg.wait_for_timeout(200); await shot('dyn on')
        await pg.click('#play'); await pg.wait_for_timeout(2500); await shot('playing'); await pg.click('#play'); await pg.wait_for_timeout(300)
        for t in ['tabMet','tabTr']:
            await pg.click('#'+t); await pg.wait_for_timeout(400); await shot(t); await pops(t)
        await pg.click('#tabMet'); await pg.click('#play'); await pg.wait_for_timeout(1500); await shot('met playing'); await pg.click('#play')
        await pg.click('#tabSet'); await pg.wait_for_timeout(400); await shot('settings')
        tabs=await pg.evaluate("[...document.querySelectorAll('#sheet [role=tab], #sheet .stab')].map((e,i)=>i)")
        for i in tabs:
            await pg.evaluate(f"[...document.querySelectorAll('#sheet [role=tab], #sheet .stab')][{i}].click()"); await pg.wait_for_timeout(300); await shot(f'settab{i}')
        print('ERR',errs); await b.close()
asyncio.run(main())
