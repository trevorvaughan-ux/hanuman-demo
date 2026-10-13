import asyncio,json
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    res={}
    for w,h in [(1280,900),(390,844)]:
      pg=await b.new_page(viewport={'width':w,'height':h});errs=[]
      pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None);pg.on('pageerror',lambda e:errs.append(str(e)))
      pg.on('requestfailed',lambda r:errs.append('FAIL '+r.url))
      await pg.goto('http://localhost:8931/');await pg.wait_for_timeout(1500)
      print(w,'h264',await pg.evaluate("document.createElement('video').canPlayType('video/mp4; codecs=\"avc1.640028\"')"))
      print(w,'scrollW',await pg.evaluate('document.documentElement.scrollWidth'))
      await pg.screenshot(path=f'test/board_{w}.png',full_page=True)
      for ch in ['SEL','Yoga']:
        await pg.click(f'.chip[data-f="{ch}"]');print(w,ch,await pg.locator('.card:visible').count())
      await pg.click('.chip[data-f="all"]')
      keys=await pg.eval_on_selector_all('.card','e=>e.map(x=>x.dataset.key)')
      for i,k in enumerate(keys):
        await pg.click(f'.card[data-key="{k}"]')
        r=await pg.evaluate('''()=>new Promise(res=>{const v=document.getElementById('vid');v.muted=true;v.play().catch(()=>{});const t0=Date.now();
          const c=()=>{if(v.readyState>=1&&v.currentTime>1)res({d:v.duration,t:v.currentTime,err:v.error&&v.error.code});else if(Date.now()-t0>10000)res({d:v.duration,t:v.currentTime,rs:v.readyState,err:v.error&&v.error.code});else setTimeout(c,200)};c();})''')
        res[(w,k)]=r
        if i==0: await pg.screenshot(path=f'test/player_{w}.png')
        await pg.click('#cl')
      print(w,'errors',errs)
    for k,v in res.items(): print(k,v)
    await b.close()
asyncio.run(main())
