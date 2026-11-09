import asyncio,base64
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream','--autoplay-policy=no-user-gesture-required'])
        c=await b.new_context(viewport={'width':390,'height':844},permissions=['camera','microphone'])
        pg=await c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('http://localhost:8799/test.html')
        await pg.evaluate("localStorage.setItem('chartready',JSON.stringify({fmRec:true,fmCam:true,fmMic:false,fmMode:'one',fmCount:true,bpm:120,bars:4,fmClean:false,level:5}))")
        await pg.reload(); await pg.wait_for_timeout(500)
        await pg.click('#filmBtn'); await pg.wait_for_timeout(1500)
        await pg.click('#fGo'); await pg.wait_for_timeout(13000)
        print('editor open', not await pg.evaluate("document.getElementById('fEd').hidden"))
        print('info', await pg.evaluate('__edInfo()'))
        await pg.click('[data-tool=lay]'); await pg.wait_for_timeout(200)
        await pg.click('[data-lay=half]'); await pg.wait_for_timeout(500)
        await pg.screenshot(path='h1.png')
        await pg.click('#edSave'); await pg.wait_for_timeout(16000)
        print('recLag', await pg.evaluate("__nb.S.recLag"))
        data=await pg.evaluate("(async()=>{const b=__nb.FILM.blob; if(!b) return ''; const a=new Uint8Array(await b.arrayBuffer()); let s=''; for(let i=0;i<a.length;i++) s+=String.fromCharCode(a[i]); return btoa(s)})()")
        open('/tmp/claude-0/build/out_half.webm','wb').write(base64.b64decode(data)) if data else print('no blob')
        print('ERR',errs); await b.close()
asyncio.run(main())
