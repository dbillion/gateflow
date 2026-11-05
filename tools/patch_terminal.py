import io
p = "/home/deeone/Documents/mobilewars/index.html"
s = io.open(p, encoding="utf-8").read()

# ---------------------------------------------------------------- 1. hollow shell
a = s.index("      const bodyGeo = new THREE.BoxGeometry(130, 9, 26);")
b = s.index("      const trimGeo = new THREE.BoxGeometry(134.4, 0.5, 0.8);")
shell = r'''      const clayMat = new THREE.MeshStandardMaterial({
        color: PALETTE.clayWall,
        roughness: 0.75,
        metalness: 0.05
      });

      // Hollow shell (walls share one fading material) so the interior can be revealed.
      terminalWallMat = clayMat.clone();
      terminalWallMat.transparent = true;
      const terminalPickables = [];
      const addWall = (w, h, d, x, y, z) => {
        const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), terminalWallMat);
        m.position.set(x, y, z);
        m.castShadow = true;
        m.receiveShadow = true;
        terminalGroup.add(m);
        terminalPickables.push(m);
        return m;
      };
      addWall(130, 9, 0.8, 0, 4.5, -24.6);      // back wall
      addWall(0.8, 9, 26, -64.6, 4.5, -12);     // west end
      addWall(0.8, 9, 26, 64.6, 4.5, -12);      // east end
      addWall(130, 0.8, 1.4, 0, 0.4, 0.3);      // front plinth
      addWall(130, 0.8, 1.4, 0, 8.6, 0.3);      // front band

      const groundFloor = new THREE.Mesh(
        new THREE.BoxGeometry(130, 0.2, 26),
        new THREE.MeshStandardMaterial({ color: 0xD6D3CD, roughness: 0.9 })
      );
      groundFloor.position.set(0, 0.1, -12);
      groundFloor.receiveShadow = true;
      terminalGroup.add(groundFloor);

      // Solid fill behind the glass; hidden while the cutaway is open.
      terminalFill = new THREE.Mesh(new THREE.BoxGeometry(126, 7.6, 0.4), clayMat);
      terminalFill.position.set(0, 4.5, -0.6);
      terminalGroup.add(terminalFill);

      terminalGlassMat = new THREE.MeshPhysicalMaterial({
        color: PALETTE.glassBlue,
        metalness: 0.2,
        roughness: 0.15,
        transparent: true,
        opacity: 0.75,
        reflectivity: 0.9,
        depthWrite: false
      });
      const facade = new THREE.Mesh(new THREE.BoxGeometry(126, 7.5, 1.2), terminalGlassMat);
      facade.position.set(0, 4.5, 0.5);
      terminalGroup.add(facade);

      terminalRoofMat = new THREE.MeshStandardMaterial({ color: 0xE2E8F0, roughness: 0.5, transparent: true });
      const roof = new THREE.Mesh(new THREE.BoxGeometry(134, 1.4, 30), terminalRoofMat);
      roof.position.set(0, 9.4, -12);
      roof.castShadow = true;
      terminalGroup.add(roof);
      terminalPickables.push(roof);
      terminalRoofMesh = roof;

'''
s = s[:a] + shell + s[b:]

# HVAC units: remember them so they can hide with the roof
s = s.replace("        hvac.position.set(rx, 11, -12);\n        hvac.castShadow = true;\n        terminalGroup.add(hvac);",
              "        hvac.position.set(rx, 11, -12);\n        hvac.castShadow = true;\n        terminalGroup.add(hvac);\n        terminalHvac.push(hvac);")

# ---------------------------------------------------------------- 2. interior + entity, before scene.add(terminalGroup)
tail = "      scene.add(terminalGroup);\n    }\n\n    /* --------------------------------------------------------------------------\n       CONTROL TOWER"
assert tail in s
extra = r'''      buildTerminalInterior(terminalGroup);

      const anchor = new THREE.Object3D();
      anchor.position.set(0, 9, -12);
      terminalGroup.add(anchor);
      const terminalData = {
        id: 'TERMINAL',
        name: 'Main Terminal Building',
        hudLabel: 'Terminal',
        category: 'Facility',
        type: 'Terminal',
        stats: '3 floors · 2 lifts · 5 gates',
        mesh: anchor
      };
      terminalPickables.forEach(m => { m.userData = terminalData; clickableObjects.push(m); });
      entityRegistry.set('TERMINAL', terminalData);

'''
s = s.replace(tail, extra + tail, 1)

# ---------------------------------------------------------------- 3. interior builder + cutaway (inserted before CONTROL TOWER banner)
banner = "    /* --------------------------------------------------------------------------\n       CONTROL TOWER"
interior = r'''    /* --------------------------------------------------------------------------
       TERMINAL INTERIOR: 3 floors (G, 1, 2), chairs, waiting centres, lifts
       -------------------------------------------------------------------------- */
    var terminalWallMat, terminalRoofMat, terminalGlassMat, terminalFill, terminalRoofMesh;
    var terminalInterior = null, terminalHvac = [], terminalLifts = [], terminalCut = 0;
    const TERMINAL_CENTER = new THREE.Vector3(0, 5, -12);
    const TERMINAL_FLOORS = [
      { label: 'G', y: 0.2 },
      { label: '1', y: 3.1 },
      { label: '2', y: 6.0 }
    ];

    function makeLabelSprite(text, widthUnits, color) {
      const c = document.createElement('canvas');
      c.width = 256; c.height = 64;
      const g = c.getContext('2d');
      g.fillStyle = 'rgba(15,23,42,0.82)';
      g.beginPath(); g.roundRect ? g.roundRect(4, 4, 248, 56, 14) : g.rect(4, 4, 248, 56); g.fill();
      g.fillStyle = color || '#F8FAFC';
      g.font = 'bold 26px Arial, sans-serif';
      g.textAlign = 'center'; g.textBaseline = 'middle';
      g.fillText(text, 128, 34);
      const tex = new THREE.CanvasTexture(c);
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false }));
      sp.scale.set(widthUnits, widthUnits / 4, 1);
      return sp;
    }

    // Lift floor indicator: a tall strip, one marker per real floor height, current floor lit.
    function drawLiftIndicator(lift) {
      const g = lift.ctx, W = 64, H = 512, top = 8.6, span = 8.4;
      g.clearRect(0, 0, W, H);
      g.fillStyle = 'rgba(15,23,42,0.85)'; g.fillRect(0, 0, W, H);
      g.fillStyle = 'rgba(148,163,184,0.5)'; g.fillRect(30, 8, 4, H - 16);
      TERMINAL_FLOORS.forEach((f, i) => {
        const cy = (top - f.y) / span * H;
        const here = lift.floorIdx === i && lift.state === 'dwell';
        const near = lift.nearFloor === i;
        g.fillStyle = here ? '#FF6A1A' : (near ? '#F59E0B' : '#334155');
        g.fillRect(8, cy - 18, 48, 36);
        g.fillStyle = '#fff'; g.font = 'bold 26px Arial'; g.textAlign = 'center'; g.textBaseline = 'middle';
        g.fillText(f.label, 32, cy + 1);
      });
      if (lift.state === 'move') {
        g.fillStyle = '#FBBF24'; g.font = 'bold 22px Arial'; g.textAlign = 'center';
        const cy = (top - lift.cab.position.y) / span * H;
        g.fillText(lift.dir > 0 ? '▲' : '▼', 32, Math.min(H - 20, Math.max(20, cy - 34)));
      }
      lift.tex.needsUpdate = true;
    }

    function buildTerminalInterior(parent) {
      const root = new THREE.Group();
      terminalInterior = root;
      parent.add(root);

      // ---- upper floors (semi-transparent so lower floors stay readable) ----
      const slabMat = new THREE.MeshStandardMaterial({ color: 0xE5E7EB, roughness: 0.85, transparent: true, opacity: 0.55, depthWrite: false });
      const railMat = new THREE.MeshPhysicalMaterial({ color: 0x93C5FD, transparent: true, opacity: 0.3, depthWrite: false });
      [1, 2].forEach(fi => {
        const fy = TERMINAL_FLOORS[fi].y;
        [-1, 1].forEach(sx => {
          const slab = new THREE.Mesh(new THREE.BoxGeometry(53.8, 0.25, 14.8), slabMat);
          slab.position.set(sx * 36.9, fy - 0.125, -16.4);
          slab.receiveShadow = true;
          root.add(slab);
          const rail = new THREE.Mesh(new THREE.BoxGeometry(53.8, 0.7, 0.08), railMat);
          rail.position.set(sx * 36.9, fy + 0.35, -9.05);
          root.add(rail);
          const lab = makeLabelSprite(fi === 1 ? 'FLOOR 1 · DEPARTURE LOUNGE' : 'FLOOR 2 · PREMIUM LOUNGE', 11, '#FDE68A');
          lab.position.set(sx * 36.9, fy + 2.0, -9.4);
          root.add(lab);
        });
      });

      // ---- chairs (instanced) ----
      const chairs = [];
      const row = (x0, y, z, n, sp, color) => { for (let i = 0; i < n; i++) chairs.push([x0 + i * sp, y, z, color]); };
      const BLUE = 0x3B82F6, AMBER = 0xF59E0B, TEAL = 0x14B8A6, ROSE = 0xFB7185;
      [-50, -25, 0, 25, 50].forEach(gx => {                 // gate lounges, facing the apron
        row(gx - 2.4, 0.2, -3.0, 6, 0.95, BLUE);
        row(gx - 2.4, 0.2, -4.6, 6, 0.95, BLUE);
      });
      [-1, 1].forEach(sx => {
        const x0 = sx < 0 ? -59 : 45.7;
        for (let r = 0; r < 3; r++) row(x0, 0.2, -9 - r * 1.6, 14, 0.95, AMBER);     // waiting centres (G)
        for (let r = 0; r < 3; r++) row(sx < 0 ? -58 : 43, TERMINAL_FLOORS[1].y, -12 - r * 1.6, 16, 0.95, TEAL);   // floor 1
        for (let r = 0; r < 2; r++) row(sx < 0 ? -58 : 43, TERMINAL_FLOORS[2].y, -12 - r * 1.8, 16, 0.95, ROSE);   // floor 2
      });

      const seatGeo = new THREE.BoxGeometry(0.7, 0.12, 0.7);
      const backGeo = new THREE.BoxGeometry(0.7, 0.65, 0.1);
      const legGeo = new THREE.BoxGeometry(0.12, 0.5, 0.12);
      const white = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.7 });
      const seats = new THREE.InstancedMesh(seatGeo, white, chairs.length);
      const backs = new THREE.InstancedMesh(backGeo, white, chairs.length);
      const legs = new THREE.InstancedMesh(legGeo, new THREE.MeshStandardMaterial({ color: 0x334155 }), chairs.length);
      const m4 = new THREE.Matrix4(), col = new THREE.Color();
      chairs.forEach((c, i) => {
        col.setHex(c[3]);
        m4.makeTranslation(c[0], c[1] + 0.55, c[2]); seats.setMatrixAt(i, m4); seats.setColorAt(i, col);
        m4.makeTranslation(c[0], c[1] + 0.9, c[2] - 0.3); backs.setMatrixAt(i, m4); backs.setColorAt(i, col);
        m4.makeTranslation(c[0], c[1] + 0.25, c[2]); legs.setMatrixAt(i, m4);
      });
      [seats, backs, legs].forEach(m => { m.castShadow = false; root.add(m); });

      // ---- check-in desks + info desk (ground floor) ----
      const deskPos = [];
      [-1, 1].forEach(sx => { for (let k = 0; k < 6; k++) deskPos.push(sx * (16 + k * 7)); });
      const desks = new THREE.InstancedMesh(new THREE.BoxGeometry(5, 1.1, 1.4), new THREE.MeshStandardMaterial({ color: 0xCBD5E1 }), deskPos.length);
      const tops = new THREE.InstancedMesh(new THREE.BoxGeometry(5.2, 0.1, 1.6), new THREE.MeshStandardMaterial({ color: 0x1E293B }), deskPos.length);
      deskPos.forEach((x, i) => {
        m4.makeTranslation(x, 0.75, -21); desks.setMatrixAt(i, m4);
        m4.makeTranslation(x, 1.35, -21); tops.setMatrixAt(i, m4);
      });
      root.add(desks, tops);
      [-34, 34].forEach(x => { const l = makeLabelSprite('CHECK-IN', 7, '#FFFFFF'); l.position.set(x, 3.4, -23.2); root.add(l); });

      const info = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 1.8, 1.1, 20), new THREE.MeshStandardMaterial({ color: 0xFF6A1A }));
      info.position.set(0, 0.75, -15);
      root.add(info);
      const infoLab = makeLabelSprite('INFORMATION', 6.5, '#FFFFFF'); infoLab.position.set(0, 3.0, -15); root.add(infoLab);
      [[-52, -9.0, 'WAITING CENTRE'], [52, -9.0, 'WAITING CENTRE']].forEach(w => {
        const l = makeLabelSprite(w[2], 8, '#FDE68A'); l.position.set(w[0], 2.6, -13.8); root.add(l);
      });
      [-50, -25, 0, 25, 50].forEach((gx, i) => {
        const l = makeLabelSprite('GATE A' + (i + 1), 5.2, '#93C5FD'); l.position.set(gx, 2.6, -2.2); root.add(l);
      });

      // ---- two glass lifts serving G / 1 / 2 ----
      const glass = new THREE.MeshPhysicalMaterial({ color: 0x93C5FD, transparent: true, opacity: 0.16, depthWrite: false });
      const frameMat = new THREE.MeshStandardMaterial({ color: 0x475569 });
      [{ x: -8.6, name: 'LIFT A', start: 0 }, { x: 8.6, name: 'LIFT B', start: 2 }].forEach(cfg => {
        const lz = -18;
        const shaft = new THREE.Mesh(new THREE.BoxGeometry(2.4, 8.8, 2.4), glass);
        shaft.position.set(cfg.x, 4.4, lz);
        root.add(shaft);
        [[-1.2, -1.2], [1.2, -1.2], [-1.2, 1.2], [1.2, 1.2]].forEach(c => {
          const post = new THREE.Mesh(new THREE.BoxGeometry(0.12, 8.8, 0.12), frameMat);
          post.position.set(cfg.x + c[0], 4.4, lz + c[1]);
          root.add(post);
        });
        const cab = new THREE.Mesh(new THREE.BoxGeometry(2.0, 2.3, 2.0), new THREE.MeshStandardMaterial({ color: 0xFF6A1A, transparent: true, opacity: 0.88 }));
        root.add(cab);

        const cvs = document.createElement('canvas'); cvs.width = 64; cvs.height = 512;
        const tex = new THREE.CanvasTexture(cvs);
        const panel = new THREE.Mesh(new THREE.PlaneGeometry(0.95, 7.6), new THREE.MeshBasicMaterial({ map: tex, transparent: true }));
        panel.position.set(cfg.x, 4.55, lz + 1.26);
        root.add(panel);
        const nm = makeLabelSprite(cfg.name, 3.2, '#FFFFFF'); nm.position.set(cfg.x, 9.6, lz); root.add(nm);

        const lift = { cab: cab, ctx: cvs.getContext('2d'), tex: tex, floorIdx: cfg.start, dir: cfg.start === 2 ? -1 : 1,
                       state: 'dwell', timer: 1 + cfg.start, nearFloor: -1 };
        cab.position.set(cfg.x, TERMINAL_FLOORS[cfg.start].y + 1.15, lz);
        drawLiftIndicator(lift);
        terminalLifts.push(lift);
      });

      root.visible = false;
    }

    function updateLifts(dt) {
      terminalLifts.forEach(l => {
        const before = l.state + l.floorIdx + l.nearFloor;
        if (l.state === 'dwell') {
          l.timer -= dt;
          if (l.timer <= 0) {
            if (l.floorIdx + l.dir < 0 || l.floorIdx + l.dir > 2) l.dir = -l.dir;
            l.target = l.floorIdx + l.dir;
            l.state = 'move';
          }
        } else {
          const ty = TERMINAL_FLOORS[l.target].y + 1.15;
          const dy = ty - l.cab.position.y;
          const step = Math.sign(dy) * Math.min(Math.abs(dy), 2.4 * dt);
          l.cab.position.y += step;
          l.nearFloor = l.target;
          if (Math.abs(ty - l.cab.position.y) < 0.01) {
            l.floorIdx = l.target; l.nearFloor = -1; l.state = 'dwell'; l.timer = 2.2;
          }
        }
        // redraw the indicator when something visible changed (moving: ~8x per second)
        l.acc = (l.acc || 0) + dt;
        const changed = before !== (l.state + l.floorIdx + l.nearFloor);
        if (changed || (l.state === 'move' && l.acc > 0.12)) { l.acc = 0; drawLiftIndicator(l); }
      });
    }

    // Terminal cutaway: walls and roof fade near the camera or when the terminal is selected.
    function updateTerminalCutaway(dt) {
      if (!terminalRoofMat) return;
      const sel = AppState.selectedObject;
      const inspecting = !!sel && sel.id === 'TERMINAL';
      const cut = inspecting || camera.position.distanceTo(TERMINAL_CENTER) < 100;
      terminalCut += ((cut ? 1 : 0) - terminalCut) * Math.min(1, dt * 4);
      const t = terminalCut;
      terminalRoofMat.opacity = 1 - 0.94 * t;
      terminalWallMat.opacity = 1 - 0.72 * t;
      terminalGlassMat.opacity = 0.75 - 0.57 * t;
      const solidRoof = t < 0.03;
      terminalRoofMat.depthWrite = solidRoof;
      terminalWallMat.depthWrite = t < 0.03;
      terminalRoofMesh.castShadow = t < 0.5;
      terminalFill.visible = t < 0.5;
      terminalHvac.forEach(h => { h.visible = t < 0.5; });
      terminalInterior.visible = t > 0.03;
      if (terminalInterior.visible) updateLifts(dt);
    }

'''
s = s.replace(banner, interior + banner, 1)

# ---------------------------------------------------------------- 4. hook into loop + camera preset
s = s.replace("      updateHangarCutaway(delta);", "      updateHangarCutaway(delta);\n      updateTerminalCutaway(delta);", 1)
s = s.replace("terminal: { pos: [0, 40, 66], look: [0, 0, 16] },", "terminal: { pos: [0, 36, 46], look: [0, 2, -10] },")
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
