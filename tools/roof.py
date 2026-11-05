from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1100, "height": 700})
    pg.goto("http://localhost:8085/index.html?nocache=r%d" % time.time())
    pg.wait_for_timeout(3000)
    fps = pg.evaluate("new Promise(r => { let n = 0; const t0 = performance.now(); const f = () => { n++; if (performance.now() - t0 > 2000) r(n / 2); else requestAnimationFrame(f); }; f(); })")
    print("fps in this headless browser:", fps)
    pg.evaluate("window.selectEntityById('MRO-01')")
    for i in range(4):
        pg.wait_for_timeout(4000); print("open  t=%ds roof=%.2f" % ((i + 1) * 4, pg.evaluate("hangarRoof.material.opacity")))
    pg.evaluate("window.flyToArea('runway')"); pg.evaluate("AppState.selectedObject = null")
    for i in range(4):
        pg.wait_for_timeout(4000); print("close t=%ds roof=%.2f" % ((i + 1) * 4, pg.evaluate("hangarRoof.material.opacity")))
    b.close()
