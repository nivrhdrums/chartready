import asyncio,sys
from playwright.async_api import async_playwright
async def main():
    url='file:///tmp/claude-0/build/test.html'
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto(url); await pg.wait_for_timeout(700)
        steps=sys.argv[1:] or ['shot:/tmp/s0.png']
        for s in steps:
            k,v=s.split(':',1)
            if k=='shot': await pg.screenshot(path=v)
            elif k=='click': await pg.click(v)
            elif k=='js': print(await pg.evaluate(v))
            elif k=='wait': await pg.wait_for_timeout(int(v))
            elif k=='size':
                w,h=v.split('x'); await pg.set_viewport_size({'width':int(w),'height':int(h)})
        print('ERR',errs)
        await b.close()
asyncio.run(main())
