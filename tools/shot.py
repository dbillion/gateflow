import sys, json
from playwright.sync_api import sync_playwright

sizes = [(1366, 650)]
tag = sys.argv[1] if len(sys.argv) > 1 else "before"
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    for w, h in sizes:
        pg = b.new_page(viewport={"width": w, "height": h})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://localhost:8085/index.html?nocache=%s%d" % (tag, w))
        pg.wait_for_timeout(3000)
        pg.evaluate("window.selectEntityById('FL-01')")
        pg.wait_for_timeout(2500)
        info = pg.evaluate("""() => {
          const r = id => { const e = document.getElementById(id); if(!e) return null; const b = e.getBoundingClientRect(); return {id, l:Math.round(b.left), t:Math.round(b.top), r:Math.round(b.right), b:Math.round(b.bottom), vis: e.offsetParent!==null}; };
          return ['detail-panel','live-table-panel','turnaround-panel','kpi-row','hud-anchor','top-bar'].map(r);
        }""")
        print(w, h, json.dumps(info), "errors:", errs[:3])
        pg.screenshot(path="tools/shots/shot_%s_%d.png" % (tag, w))
        pg.close()
    b.close()
