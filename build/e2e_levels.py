# path ladder: every level renders without errors; prints which patterns appear; screenshots a few levels
import asyncio,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' and 'lan' not in m.text else None)
        await pg.goto('file:///tmp/claude-0/build/test.html'); await pg.wait_for_timeout(600)
        for tr in ['d','t','dt']:
            res=await pg.evaluate("""(tr)=>{ const N=__nb,S=N.S; S.mode='path'; S.trkD=tr.includes('d'); S.trkT=tr.includes('t'); S.num=4; S.den=4; S.bars=4; const out={};
              for(let L=1;L<=13;L++){ S.level=L; const seen={}; let ties=0,tin=0,tout=0;
                for(let k=0;k<25;k++){ const r=N.genRhythm(); r.bars.forEach(bar=>{ bar.forEach(bt=>{ const c=N.beatCode(bt); seen[c]=(seen[c]||0)+1; }); if(bar.ti) tin++; });
                  N.setR(r); const h=document.getElementById('score').innerHTML; ties+=(h.match(/class="tie"/g)||[]).length; }
                out[L]={n:Object.keys(seen).length,codes:Object.entries(seen).sort((a,b)=>b[1]-a[1]).map(x=>x[0]).join(' '),ties,tieInBars:tin}; }
              return JSON.stringify(out); }""",tr)
            print('== track',tr)
            for L,v in json.loads(res).items(): print(L,v['n'],'ties',v['ties'],'barTies',v['tieInBars'],'|',v['codes'][:150])
        for L in [1,5,9,11,13]:
            await pg.evaluate(f"(()=>{{const S=__nb.S; S.trkD=true; S.trkT=true; S.level={L}; __nb.setR(__nb.genRhythm());}})()")
            await pg.screenshot(path=f'lv{L}.png')
        print('ERR',errs); await b.close()
asyncio.run(main())
