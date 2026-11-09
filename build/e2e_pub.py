import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/release/ChartReady-ציבורי/index.html'); await pg.wait_for_timeout(800)
        await pg.click('#filmBtn'); await pg.wait_for_timeout(200); await pg.click('#filmBtn'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='/tmp/claude-0/build/p1.png')
        await pg.click('#toast button, #toast .act'); await pg.wait_for_timeout(300)
        for i in range(5):
            for d in '135246':
                await pg.evaluate(f"kpPress&&0") if False else None
                await pg.click(f'#kpWrap [data-k="{d}"]')
            await pg.wait_for_timeout(400)
            print(i+1, await pg.evaluate("document.getElementById('kpHint').textContent"))
        await pg.screenshot(path='/tmp/claude-0/build/p2.png')
        print('film opened?', await pg.evaluate("!!(window.FILM&&FILM.on)"))
        print('ERR',errs); await b.close()
asyncio.run(main())
