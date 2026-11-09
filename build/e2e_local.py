import asyncio,json,urllib.request
from playwright.async_api import async_playwright
async def main():
    lan=json.load(urllib.request.urlopen('http://localhost:8799/lan'))['url']
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required','--no-proxy-server'])
        errs=[]
        h=await b.new_page(viewport={'width':1280,'height':760}); h.on('pageerror',lambda e:errs.append('H '+str(e)))
        await h.goto('http://localhost:8799/'); await h.wait_for_timeout(800)
        await h.click('#tabSet'); await h.wait_for_timeout(300)
        print('unlocked', await h.evaluate("document.getElementById('remLock').textContent"))
        await h.evaluate("document.getElementById('remLock').click()"); await h.wait_for_timeout(200)
        await h.evaluate("document.getElementById('remPair').click()"); await h.wait_for_timeout(1500)
        url=await h.evaluate("document.getElementById('remUrl').textContent"); print('qr url',url)
        await h.screenshot(path='/tmp/claude-0/build/l1.png')
        ph=await b.new_page(viewport={'width':390,'height':844}); ph.on('pageerror',lambda e:errs.append('P '+str(e)))
        await ph.goto(url); await ph.wait_for_timeout(2000)
        print('phone status', await ph.evaluate("document.getElementById('remStatus')?document.getElementById('remStatus').textContent:''"))
        print('host status', await h.evaluate("document.getElementById('remStatus')?document.getElementById('remStatus').textContent:''"))
        bpm0=await h.evaluate("document.getElementById('qBpm').textContent")
        await ph.evaluate("document.getElementById('play').click()"); await ph.wait_for_timeout(800)
        print('host playing after phone play:', await h.evaluate("document.getElementById('screen').classList.contains('playing')"))
        await ph.screenshot(path='/tmp/claude-0/build/l2.png')
        print('ERR',errs); await b.close()
asyncio.run(main())
