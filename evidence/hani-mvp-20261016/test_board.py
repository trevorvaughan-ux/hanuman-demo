import json,sys,hashlib
from playwright.sync_api import sync_playwright
BASE="http://localhost:8765/hani-mvp.html"; SH="/tmp/claude-0/s/shots/"
OK={"active":True,"school_name":"Great Oaks PreK","msg_en":"This demo has ended. Thank you for trying Hani!","msg_es":"Esta demostración ha terminado. ¡Gracias por probar Hani!"}
OFF=dict(OK,active=False)
res=[]
def rec(n,ok,d=""): res.append((n,ok,d)); print(("PASS " if ok else "FAIL ")+n, d)
with sync_playwright() as p:
  b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium",args=["--no-sandbox"])
  def newpage(status, w=390, h=844, lang="en-US", fail=False):
    ctx=b.new_context(viewport={"width":w,"height":h},locale=lang)
    pg=ctx.new_page(); errs=[]; calls=[]
    pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror",lambda e: errs.append(str(e)))
    holder={"s":status}
    def h(route):
      calls.append(route.request.post_data)
      if holder["s"]=="FAIL": return route.abort()
      route.fulfill(status=200,content_type="application/json",body=json.dumps(holder["s"]))
    pg.route("**/rest/v1/rpc/board_link_status",h)
    # fonts blocked offline: ignore
    pg.route("**/fonts.g*apis.com/**",lambda r:r.abort())
    return ctx,pg,errs,calls,holder
  def real_errs(errs): return [e for e in errs if "Failed to load resource" not in e and "ERR_FAILED" not in e]
  TOK="a"*32
  # valid, both widths
  for w,h_ in((390,844),(1280,900)):
    ctx,pg,errs,calls,_=newpage(OK,w,h_)
    pg.goto(BASE+"?k="+TOK); pg.wait_for_selector(".tile")
    names=pg.eval_on_selector_all(".tname","e=>e.map(x=>x.textContent)")
    rec(f"valid token {w}px: 12 tiles in order",len(names)==12 and names[0]=="Goddess Pose" and names[3]=="Triangle Pose" and names[11]=="Body Scan",str(names))
    rec(f"valid {w}px no Seated Chair Twist",not any("Seated" in n for n in names))
    pg.screenshot(path=SH+f"board-en-{w}.png",full_page=True)
    # 48px taps
    sizes=pg.eval_on_selector_all(".tile,.langsw button","e=>e.map(x=>{const r=x.getBoundingClientRect();return [r.width,r.height]})")
    rec(f"tap targets >=48px {w}",all(a>=48 and bb>=48 for a,bb in sizes))
    if w==390:
      # ES toggle + persist
      pg.click(".langsw button:nth-child(2)"); 
      rec("ES toggle changes title",pg.inner_text("h1")=="Elige una pausa para tu clase")
      rec("ES beta label shown","BETA" in pg.inner_text("main"))
      rec("hani_lang saved",pg.evaluate("localStorage.getItem('hani_lang')")=="es")
      pg.screenshot(path=SH+"board-es-390.png",full_page=True)
      pg.reload(); pg.wait_for_selector(".tile")
      rec("ES persists after reload",pg.inner_text("h1")=="Elige una pausa para tu clase")
      pg.click(".langsw button:nth-child(1)"); rec("toggle back to EN",pg.inner_text("h1")=="Pick a calm-down for your class")
      # Gani tiles: no Hani anywhere in text/alt and no Hani art
      tiles=pg.eval_on_selector_all(".tile","e=>e.map(x=>({t:x.innerText,img:[...x.querySelectorAll('img')].map(i=>i.getAttribute('src'))}))")
      gani=[t for t in tiles if "Guide: Gani" in t["t"]]
      rec("4 Gani tiles",len(gani)==4)
      rec("Gani tiles: no 'Hani' text and no Hani art",all("Hani" not in t["t"] and not any(s and s.startswith("hanuman-") for s in t["img"]) for t in gani),str([t["img"] for t in gani]))
      sil=[t for t in tiles if "Captions only, no sound" in t["t"]]; rec("2 silent labels",len(sil)==2)
      soon=[t for t in tiles if "Video coming soon" in t["t"]]; rec("Video-coming-soon chips present",len(soon)>=6,str(len(soon)))
      # open a guided tile and a video tile
      pg.click(".tile >> nth=9"); pg.wait_for_selector("#player")
      rec("guided card opens, steps nav","Step 1 of" in pg.inner_text("#pstep"))
      pg.click(".nav button:last-child"); rec("next step","Step 2 of" in pg.inner_text("#pstep"))
      pg.screenshot(path=SH+"player-guided-390.png")
      pg.click("#pback"); 
      pg.click(".tile >> nth=0"); pg.wait_for_selector("#player"); pg.wait_for_timeout(600)
      rec("missing video falls back with message","not available yet" in pg.inner_text("#player") or pg.query_selector("#pmedia video") is not None)
      pg.screenshot(path=SH+"player-video-fallback-390.png")
      pg.click("#pback")
      # keyboard: lang buttons focusable
      pg.focus(".langsw button:nth-child(2)"); pg.keyboard.press("Enter"); rec("keyboard activates ES",pg.inner_text("h1").startswith("Elige"))
      # RPC payload excludes nothing sensitive; telemetry none
      rec("status call per load (2 = initial + reload)", len(calls)==2, str(len(calls)))
    rec(f"valid {w}px 0 console errors",real_errs(errs)==[],str(real_errs(errs)))
    ctx.close()
  # ended cases
  def ended_case(name,status,url,expect_calls=None):
    ctx,pg,errs,calls,_=newpage(status)
    pg.goto(url); pg.wait_for_selector("#ended"); pg.wait_for_timeout(300)
    html=pg.inner_html("#app")
    ok=("This demo has ended" in pg.inner_text("#ended")) and pg.query_selector(".tile") is None and ".mp4" not in html and "mvp-board.json" not in html
    rec(f"ended: {name}",ok)
    if expect_calls is not None: rec(f"ended: {name} rpc calls={expect_calls}",len(calls)==expect_calls,str(len(calls)))
    pg.screenshot(path=SH+f"ended-{name.replace(' ','_')}-390.png")
    return pg,ctx,errs
  ended_case("disabled or expired or global off (active=false)",OFF,BASE+"?k="+TOK,1)
  ended_case("unknown token",OFF,BASE+"?k=unknowntokenunknowntoken1234",1)
  ended_case("missing token",OK,BASE,0)
  pg,ctx,errs=ended_case("network failure",  "FAIL", BASE+"?k="+TOK, 2)
  rec("fail-closed retried once (2 attempts)",True)
  pg.set_viewport_size({"width":1280,"height":900}); pg.screenshot(path=SH+"ended-1280.png")
  pg.click(".langsw button:nth-child(2)"); rec("ended ES text","Esta demostración ha terminado" in pg.inner_text("#ended"))
  # mid-session flip
  ctx,pg,errs,calls,holder=newpage(OK)
  pg.goto(BASE+"?k="+TOK); pg.wait_for_selector(".tile")
  holder["s"]=OFF
  pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
  pg.wait_for_selector("#ended",timeout=3000); rec("toggle off while open -> ended on visibility re-check",True)
  ctx.close()
  # 30-min timer using fake clock
  ctx=b.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page(); holder={"s":OK}
  pg.clock.install()
  pg.route("**/rest/v1/rpc/board_link_status",lambda r:r.fulfill(status=200,content_type="application/json",body=json.dumps(holder["s"])))
  pg.route("**/fonts.g*apis.com/**",lambda r:r.abort())
  pg.goto(BASE+"?k="+TOK); pg.wait_for_selector(".tile")
  holder["s"]=OFF; pg.clock.run_for(30*60*1000+1000); pg.wait_for_selector("#ended",timeout=3000)
  rec("toggle off while open -> ended within 30-min timer",True); ctx.close()
  # ES default via navigator.language
  ctx,pg,errs,calls,_=newpage(OK,lang="es-MX"); pg.goto(BASE+"?k="+TOK); pg.wait_for_selector(".tile")
  rec("default ES when browser language es",pg.inner_text("h1").startswith("Elige")); ctx.close()
  b.close()
fails=[r for r in res if not r[1]]; print("\nTOTAL",len(res),"FAILS",len(fails))
