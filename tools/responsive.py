import json, time, itertools
from playwright.sync_api import sync_playwright

SIZES = [  # name, w, h, mobile
    ("phone-portrait", 390, 844, True), ("phone-small", 320, 568, True), ("phone-landscape", 844, 390, True),
    ("tablet-portrait", 768, 1024, True), ("tablet-landscape", 1024, 768, False),
    ("laptop", 1366, 768, False), ("fullhd", 1920, 1080, False), ("ultrawide", 2560, 1080, False)]
IDS = ["top-bar", "kpi-row", "detail-panel", "turnaround-panel", "live-table-panel", "mobile-tabs"]
JS = """() => { const o = {}; for (const id of %s) { const e = document.getElementById(id); if (!e || !e.getClientRects().length) continue;
  const b = e.getBoundingClientRect(); o[id] = [Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]; }
  return {r: o, vw: innerWidth, vh: innerHeight, hscroll: document.documentElement.scrollWidth > innerWidth, sheet: document.body.dataset.sheet}; }""" % json.dumps(IDS)

def overlaps(r):
    bad = []
    for (a, ra), (b, rb) in itertools.combinations(r.items(), 2):
        ox = min(ra[2], rb[2]) - max(ra[0], rb[0]); oy = min(ra[3], rb[3]) - max(ra[1], rb[1])
        if ox > 1 and oy > 1: bad.append("%s x %s (%dx%d)" % (a, b, ox, oy))
    return bad

def offscreen(r, vw, vh):
    return [k for k, v in r.items() if v[0] < -1 or v[1] < -1 or v[2] > vw + 1 or v[3] > vh + 1]

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    for name, w, h, mob in SIZES:
        ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob, has_touch=mob, device_scale_factor=1)
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://localhost:8085/index.html?nocache=R%d" % time.time())
        pg.wait_for_timeout(3500)
        compact = pg.evaluate("isCompactLayout()")
        res = {"size": "%s %dx%d" % (name, w, h), "compact": compact}
        if compact:
            for sh in ["detail", "table", "turn", "none"]:
                pg.evaluate("document.querySelectorAll('#mobile-tabs button[data-sheet=%s]')[0] && window.toggleSheet && (document.body.dataset.sheet !== '%s' ? setSheet('%s') : 0)" % (sh, sh, sh))
                pg.evaluate("window.selectEntityById('FL-01')") if sh == "detail" else None
                pg.evaluate("setSheet('%s')" % sh); pg.wait_for_timeout(500)
                m = pg.evaluate(JS)
                res["sheet:" + sh] = {"overlap": overlaps(m["r"]), "offscreen": offscreen(m["r"], m["vw"], m["vh"]), "hscroll": m["hscroll"]}
                if name in ("phone-portrait", "phone-landscape", "tablet-portrait") and sh in ("detail", "table"):
                    pg.screenshot(path="tools/shots/resp_%s_%s.png" % (name, sh), timeout=150000)
        else:
            pg.evaluate("window.selectEntityById('FL-01')"); pg.wait_for_timeout(600)
            m = pg.evaluate(JS)
            res["desktop"] = {"overlap": overlaps(m["r"]), "offscreen": offscreen(m["r"], m["vw"], m["vh"]), "hscroll": m["hscroll"]}
            pg.evaluate("document.body.classList.add('search-open')") if w <= 1000 else None
            if name in ("tablet-landscape", "fullhd"):
                pg.screenshot(path="tools/shots/resp_%s.png" % name, timeout=150000)
        res["errors"] = errs[:2]
        print(json.dumps(res)); ctx.close()
    b.close()
