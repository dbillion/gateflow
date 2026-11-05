from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://localhost:8085/index.html?nocache=t%d" % time.time())
    pg.wait_for_timeout(3500)
    for t in ["Stands", "Vehicles", "Flights"]:
        pg.evaluate("window.switchTableTab('%s', document.querySelector('.table-tab-btn'))" % t)
        pg.wait_for_timeout(300)
        print(t, "::", pg.evaluate("[...document.querySelectorAll('#live-table-panel tbody tr')].map(r=>r.innerText.replace(/\\s+/g,' ')).join('\\n')"))
    # clicking a row selects it and highlights it
    pg.evaluate("window.switchTableTab('Flights')"); pg.wait_for_timeout(300)
    bb = pg.evaluate("(() => { const r = document.querySelector('#live-table-panel tbody tr:nth-child(2)').getBoundingClientRect(); return [r.x + r.width/2, r.y + r.height/2]; })()"); pg.mouse.move(bb[0], bb[1]); pg.mouse.down(); pg.mouse.up(); pg.wait_for_timeout(2500)
    print("selected:", pg.evaluate("AppState.selectedObject.id"), "| highlighted:", pg.evaluate("document.querySelector('#live-table-panel tr.selected')?.innerText.slice(0,30)"))
    pg.screenshot(path="tools/shots/tables.png")
    print("errors:", errs[:3])
    b.close()
