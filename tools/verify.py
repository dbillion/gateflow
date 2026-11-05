import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://localhost:8085/index.html?nocache=verify%d" % __import__("time").time())
    pg.wait_for_timeout(3000)
    out = {}
    # B: day/night + season state
    snap = "() => ({bg: scene.background.getHex(), dir: dirLight.intensity, hemi: hemiLight.intensity, amb: ambientLight.intensity, rain: particleMat.opacity})"
    try:
        out["day0"] = pg.evaluate(snap)
        pg.evaluate("window.toggleDayNight()"); out["night"] = pg.evaluate(snap)
        pg.evaluate("window.toggleDayNight()"); out["day_again"] = pg.evaluate(snap)
        pg.evaluate("window.changeSeason('monsoon')"); pg.evaluate("window.toggleDayNight()")
        pg.evaluate("window.changeSeason('summer')"); out["night_summer_rain"] = pg.evaluate(snap)
        pg.evaluate("window.toggleDayNight()")
    except Exception as ex:
        out["B_error"] = str(ex)[:200]
    # C: stale detail values
    def panel():
        return pg.evaluate("() => [...document.querySelectorAll('#detail-panel .telemetry-item')].map(e => e.innerText.replace(/\\n/g,': ')).join(' | ')")
    pg.evaluate("window.selectEntityById('ET-742')"); pg.wait_for_timeout(300); out["C_aircraft"] = panel()
    pg.evaluate("window.focusStand('A4')"); pg.wait_for_timeout(300); out["C_stand_A4"] = panel()
    out["C_title"] = pg.evaluate("document.getElementById('dp-title').innerText")
    # D: drag must not select, click must
    pg.evaluate("window.selectEntityById('FL-01')"); pg.wait_for_timeout(300)
    pg.mouse.move(500, 400); pg.mouse.down(); pg.mouse.move(560, 430, steps=6); pg.mouse.up(); pg.wait_for_timeout(300)
    out["D_after_drag_selected"] = pg.evaluate("AppState.selectedObject && AppState.selectedObject.id")
    # E: hangar roof
    pg.evaluate("window.selectEntityById('MRO-01')"); pg.wait_for_timeout(2500)
    out["E_roof_opacity"] = pg.evaluate("hangarRoof.material.opacity")
    # tab counts vs rows
    labels = pg.evaluate("[...document.querySelectorAll('.table-tab-btn')].map(b=>b.innerText.replace(/\\s+/g,' '))")
    rows = {}
    for t in ["Stands", "Vehicles", "Flights"]:
        pg.evaluate("window.switchTableTab('%s')" % t)
        rows[t] = pg.evaluate("document.querySelectorAll('#live-table-panel tbody tr').length")
    out["tab_labels"] = labels; out["rows"] = rows
    print(json.dumps(out, indent=1)); print("errors:", errs[:3])
    b.close()
