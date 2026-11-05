from playwright.sync_api import sync_playwright
import time, sys
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1100, "height": 650})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
    pg.goto("http://localhost:8085/index.html?nocache=T%d" % time.time())
    pg.wait_for_timeout(4000)
    pg.screenshot(path="tools/shots/term_solid.png", timeout=150000)
    print("solid: cut=%.2f interior=%s" % (pg.evaluate("terminalCut"), pg.evaluate("terminalInterior.visible")))
    pg.evaluate("window.flyToArea('terminal')")
    pg.wait_for_timeout(16000)
    print("open: cut=%.2f interior=%s roof=%.2f" % (pg.evaluate("terminalCut"), pg.evaluate("terminalInterior.visible"), pg.evaluate("terminalRoofMat.opacity")))
    pg.screenshot(path="tools/shots/term_open.png", timeout=150000)
    print("lifts:", pg.evaluate("terminalLifts.map(l => [l.state, l.floorIdx, +l.cab.position.y.toFixed(2)])"))
    pg.evaluate("window.selectEntityById('TERMINAL')")
    pg.wait_for_timeout(1500)
    print("panel title:", pg.evaluate("document.getElementById('dp-title').innerText"), "| errors:", errs[:4])
    if len(sys.argv) > 1:   # close-up of the lifts / waiting centre
        pg.evaluate("AppState.cameraFollowing=false; AppState.cameraTargetPos.set(0, 12, -4); AppState.cameraTargetLook.set(0, 3.5, -18); AppState.isCameraTransitioning=true")
        pg.wait_for_timeout(14000)
        pg.screenshot(path="tools/shots/term_lifts.png", timeout=150000)
    b.close()
