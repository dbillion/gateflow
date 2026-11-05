import io, re
p = "/home/deeone/Documents/mobilewars/index.html"
s = io.open(p, encoding="utf-8").read()

# 0. viewport meta
s = s.replace('maximum-scale=1.0, user-scalable=no">', 'maximum-scale=1.0, user-scalable=no, viewport-fit=cover">', 1)

# 1. replace the old (broken) mobile block with the adaptive CSS
a = s.index("    @media (max-width: 900px) {")
b = s.index("  </style>", a)
css = r'''    /* ==========================================================================
       ADAPTIVE LAYOUT  (large desktop > laptop/tablet > compact phone)
       ========================================================================== */
    html, body { height: 100%; overscroll-behavior: none; -webkit-tap-highlight-color: transparent; }
    @supports (height: 100dvh) { html, body { height: 100dvh; } }
    #webgl-canvas { touch-action: none; }
    #search-toggle, #mobile-tabs { display: none; }

    /* Large / ultrawide screens */
    @media (min-width: 1800px) {
      body { font-size: 14px; }
      #detail-panel { width: 360px; max-height: calc(100vh - 80px - 14px - 280px - 12px); }
      #live-table-panel { width: 620px; max-height: 280px; }
      #turnaround-panel { width: 560px; }
    }

    /* Laptops and tablets in landscape */
    @media (max-width: 1180px) {
      .brand-text span { display: none; }
      .search-box { width: 150px; }
      .search-box input:focus { width: 190px; }
      .nav-btn { padding: 6px 9px; }
      .select-dropdown { max-width: 128px; text-overflow: ellipsis; }
      #turnaround-panel { width: min(480px, 44vw); }
      #live-table-panel { width: min(520px, calc(56vw - 28px)); }
    }

    /* Search collapses into a button when the header gets tight */
    @media (max-width: 1000px), (max-height: 480px) {
      .search-box { display: none; }
      #search-toggle { display: flex; }
      body.search-open .search-box {
        display: block; position: absolute; top: calc(100% + 8px); left: 0; width: min(340px, 100%); z-index: 40;
      }
      body.search-open .search-box input,
      body.search-open .search-box input:focus { width: 100%; background: rgba(18, 22, 31, 0.96); }
    }

    /* Compact: phones, small tablets, landscape phones */
    @media (max-width: 820px), (max-height: 480px) {
      #top-bar {
        top: calc(8px + env(safe-area-inset-top));
        left: calc(8px + env(safe-area-inset-left));
        right: calc(8px + env(safe-area-inset-right));
        height: auto; flex-wrap: wrap; justify-content: space-between;
        padding: 6px 10px; gap: 6px 8px;
      }
      .tool-group { display: contents; }
      .logo-group { order: 1; margin-right: auto; min-width: 0; }
      .brand-text h1 { font-size: 14px; }
      .tool-group > .icon-btn { order: 3; width: 32px; height: 32px; }
      .live-clock { order: 4; font-size: 12px; padding: 5px 8px; }
      .nav-pills {
        order: 10; flex: 1 1 calc(100% - 108px); min-width: 0;
        overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none;
      }
      .nav-pills::-webkit-scrollbar { display: none; }
      .nav-btn { flex: 0 0 auto; padding: 7px 11px; }
      .select-dropdown { order: 11; width: 100px; max-width: 100px; padding: 6px 4px; font-size: 11px; }

      #kpi-row {
        top: calc(var(--top-h, 100px) + 8px);
        left: calc(8px + env(safe-area-inset-left));
        right: calc(8px + env(safe-area-inset-right));
        gap: 6px;
      }
      .kpi-card { flex: 1 1 0; min-width: 0; padding: 6px 8px; }
      .kpi-header { font-size: 9px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .kpi-value { font-size: 15px; gap: 4px; }
      .kpi-delta { font-size: 10px; }

      /* One bottom sheet at a time, switched from the tab bar */
      #detail-panel, #live-table-panel, #turnaround-panel {
        display: none; position: fixed; top: auto; width: auto; max-width: none;
        left: calc(8px + env(safe-area-inset-left));
        right: calc(8px + env(safe-area-inset-right));
        bottom: calc(62px + env(safe-area-inset-bottom));
        max-height: 46vh; max-height: min(46dvh, 400px);
        overflow-y: auto; overflow-x: auto;
      }
      body[data-sheet="detail"] #detail-panel { display: flex; }
      body[data-sheet="table"] #live-table-panel { display: block; }
      body[data-sheet="turn"] #turnaround-panel { display: block; }

      #mobile-tabs {
        display: flex; position: fixed; z-index: 20; gap: 4px; padding: 4px; height: 46px;
        left: calc(8px + env(safe-area-inset-left));
        right: calc(8px + env(safe-area-inset-right));
        bottom: calc(8px + env(safe-area-inset-bottom));
      }
      #mobile-tabs button {
        flex: 1; border: 0; border-radius: 9px; background: transparent; color: var(--text-secondary);
        font-size: 12px; font-weight: 600; font-family: inherit; cursor: pointer; pointer-events: auto;
      }
      #mobile-tabs button.active { background: var(--accent); color: #fff; }

      #alert-toast {
        bottom: auto; top: calc(var(--top-h, 100px) + 8px);
        max-width: calc(100vw - 24px); z-index: 30;
      }
    }

    /* Landscape phones: sheets sit at the left, KPIs hidden to save height */
    @media (max-height: 480px) {
      #kpi-row { display: none; }
      #detail-panel, #live-table-panel, #turnaround-panel {
        right: auto; width: min(460px, 60vw);
        max-height: calc(100vh - var(--top-h, 70px) - 84px);
      }
      #mobile-tabs { right: auto; width: min(460px, 60vw); }
    }
'''
s = s[:a] + css + s[b:]

# 2. HTML: search toggle + tab bar
s = s.replace('    <div class="tool-group">\n      <select id="season-select"',
 '    <div class="tool-group">\n      <button class="icon-btn" id="search-toggle" title="Search" onclick="window.toggleSearch()">🔍</button>\n      <select id="season-select"', 1)
tabs = '''  <!-- MOBILE TAB BAR (compact layouts only) -->
  <div id="mobile-tabs" class="glass">
    <button data-sheet="detail" onclick="window.toggleSheet('detail')">ℹ Details</button>
    <button data-sheet="table" onclick="window.toggleSheet('table')">▦ Table</button>
    <button data-sheet="turn" onclick="window.toggleSheet('turn')">⏱ Turnaround</button>
    <button onclick="window.toggleSheet(document.body.dataset.sheet)">▾ Hide</button>
  </div>

'''
s = s.replace('  <!-- NOTIFICATION TOAST -->', tabs + '  <!-- NOTIFICATION TOAST -->', 1)

# 3. JS
js = r'''    /* --------------------------------------------------------------------------
       ADAPTIVE LAYOUT HELPERS
       -------------------------------------------------------------------------- */
    const COMPACT_MQ = window.matchMedia('(max-width: 820px), (max-height: 480px)');
    function isCompactLayout() { return COMPACT_MQ.matches; }

    function setSheet(name) {
      document.body.dataset.sheet = name || 'none';
      document.querySelectorAll('#mobile-tabs button[data-sheet]').forEach(b =>
        b.classList.toggle('active', b.dataset.sheet === name));
      refreshHudObstacles();
    }
    window.toggleSheet = function(name) { setSheet(document.body.dataset.sheet === name ? 'none' : name); };
    window.toggleSearch = function() {
      const open = document.body.classList.toggle('search-open');
      if (open) { const i = document.getElementById('obj-search'); if (i) i.focus(); }
    };

    function syncTopBarHeight() {
      const bar = document.getElementById('top-bar');
      if (!bar) return;
      document.documentElement.style.setProperty('--top-h', Math.round(bar.getBoundingClientRect().bottom) + 'px');
    }

    function setupResponsive() {
      syncTopBarHeight();
      const bar = document.getElementById('top-bar');
      if (window.ResizeObserver && bar) new ResizeObserver(syncTopBarHeight).observe(bar);
      const relayout = () => { syncTopBarHeight(); onWindowResize(); refreshHudObstacles(); };
      window.addEventListener('resize', relayout);
      window.addEventListener('orientationchange', () => setTimeout(relayout, 250));
      if (window.visualViewport) window.visualViewport.addEventListener('resize', relayout);
      document.addEventListener('pointerdown', () => { AppState.interacted = true; }, { once: true, capture: true });
      setSheet('none');
    }

'''
marker = "    function setupInteraction() {"
s = s.replace(marker, js + marker, 1)
s = s.replace("      setInterval(() => renderTableData(false), 1000);", "      setInterval(() => renderTableData(false), 1000);\n      setupResponsive();", 1)

# hooks
s = s.replace("      refreshHudObstacles();\n      renderTableData(true);\n    }\n\n    /* --------------------------------------------------------------------------\n       INTERACTION",
              "      if (AppState.interacted && isCompactLayout()) setSheet('detail');\n      refreshHudObstacles();\n      renderTableData(true);\n    }\n\n    /* --------------------------------------------------------------------------\n       INTERACTION", 1)
s = s.replace("    window.flyToArea = function(areaKey, btn) {", "    window.flyToArea = function(areaKey, btn) {\n      if (isCompactLayout()) setSheet('none');", 1)
s = s.replace("    window.filterTable = function(tabName) {", "    window.filterTable = function(tabName) {\n      if (isCompactLayout()) setSheet('table');", 1)
s = s.replace("        .filter(el => el && el.offsetParent !== null)", "        .filter(el => el && el.getClientRects().length > 0)", 1)
s = s.replace("['top-bar', 'kpi-row', 'detail-panel', 'turnaround-panel', 'live-table-panel']", "['top-bar', 'kpi-row', 'detail-panel', 'turnaround-panel', 'live-table-panel', 'mobile-tabs']", 1)
s = s.replace("renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));",
              "renderer.setPixelRatio(Math.min(window.devicePixelRatio, window.matchMedia('(max-width: 820px), (max-height: 480px)').matches ? 1.5 : 1.75));", 1)

# 4. terminal label fixes
s = s.replace("      g.font = 'bold 26px Arial, sans-serif';", "      g.font = 'bold ' + Math.min(26, Math.floor(236 / (text.length * 0.64))) + 'px Arial, sans-serif';", 1)
s = s.replace("makeLabelSprite(fi === 1 ? 'FLOOR 1 · DEPARTURE LOUNGE' : 'FLOOR 2 · PREMIUM LOUNGE', 11, '#FDE68A');\n          lab.position.set(sx * 36.9, fy + 2.0, -9.4);",
              "makeLabelSprite(fi === 1 ? 'FLOOR 1 LOUNGE' : 'FLOOR 2 PREMIUM', 6.5, '#FDE68A');\n          lab.position.set(sx * 36.9, fy + 1.5, -9.4);", 1)
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
