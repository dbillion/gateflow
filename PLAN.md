# Gateflow — correction plan (handoff)

Source brief: `/home/deeone/Downloads/Telegram Desktop/World_Prompt_Pack.pdf` (World 01).
App: single file `index.html` (+ `js/three.min.js`, `js/OrbitControls.js`). Repo `dbillion/gateflow`, branch `main`,
live: https://dbillion.github.io/gateflow/ (GitHub Pages, legacy build from `main`, ~40 s after push).
Local dir is `/home/deeone/Documents/mobilewars/` (folder name differs from repo name).

## How to verify any step
1. `python3 -m http.server 8085` in the project dir (restart if dead).
2. Extract the main `<script>` and run `node --check` on it.
3. Playwright: open `http://localhost:8085/index.html?nocache=N`, register `window.addEventListener('error', ...)`,
   drive `window.selectEntityById(id)`, `toggleCameraFollow()`, `flyToArea(key)`, `changeSeason(s)`, `toggleDayNight()`;
   expect 0 errors. Screenshot to eyeball.
4. `git add -A && git commit` (pre-commit runs gitleaks + shellcheck) then `git push origin main`, poll the live URL.

## Done
- [x] Patch 1-3: smoother flight kinematics, cargo freighter + forklift, freeze fix (commit dcaf4bf)
- [x] HUD crash on stands/gates/facilities: `getEntityWorldPos()` + mesh refs, off-screen tag hidden (commit 47e79e4)

## This round
- [x] A. Forklift (FL-01) panel overlap: the detail panel was covered by the live table on screens < ~730px tall. Fixed with a
      `max-height` + scroll on `#detail-panel` (reserves the table's height); table hides under 560px height. Verified 0px overlap
      at 1440x900, 1366x650, 1280x720 with `python3 tools/shot.py <tag>`.
- [x] Rebrand: airport is now "Oludayo's Airport" (OLU). Airlines: Ethiopian (ET-742), Kenya Airways (KQ-203), Air Peace (P4-315),
      Turkish (TK-816), EgyptAir (MS-821), Emirates SkyCargo (EK-992). No Indian / Estonian / UK carriers remain.
- [x] B. Day/night + season shared state: ambient/hemi/dir light not restored after night->day; rain persists when
      season changed at night; night ignores season. Fix = one `applyEnvironment()` computing everything from
      `(AppState.isNight, AppState.season)`; `toggleDayNight` and `changeSeason` only set state then call it.
- [x] C. Detail panel stale values: `selectEntity()` only overwrites fields when present, so a stand/facility shows the
      previous aircraft's origin/fuel/pax. Reset every field per entity type (aircraft / vehicle / stand / facility).
- [x] D. Click vs drag: selection fires on `pointerdown`, so starting an orbit drag selects. Select on `pointerup`
      only if the pointer moved < ~5 px since `pointerdown`.
- [x] E. Hangar interior hidden by roof: fade roof (low opacity) while hangar view or hangar selection is active.

## Verified this session (tools/verify.py, tools/tables.py, tools/roof.py)
- B/C/D/E all pass in a real browser: night->day restores light values, stand panel has no stale aircraft values,
  a drag does not change the selection, hangar roof fades open and closes again (frame-rate dependent easing).
- Tables are now built from live simulation data (standList, aircraftList, vehicles, freighter): tab counts equal row counts,
  selected row follows the selection, stand status/turnaround countdown are live, tables pause refreshing while hovered.
- Each flight has its own origin/pax/fuel (`FLIGHT_META`); freighter state shown as "Loading".

## Backlog (not started)
- Detail-panel telemetry (speed/alt) is not live; vehicle speeds in the table are static values.
- Times are not on one simulated clock: STA/STD in detail panel, tracker step times (18:12...), header clock (real time).
- Search only matches a few hard-coded strings (see `handleSearch`); should search entityRegistry ids/names/airlines.
- Only 2 A320s are simulated, so stands A2/A4/A5 are always Free; add more aircraft or fewer stands.
- CCTV feeds are 2D fakes unrelated to the live scene.
- README claims to re-check: rain "streaks", de-icing trucks in snow, landside vehicle loop.
- Night: runway/taxiway lights are unlit MeshBasicMaterial with no glow.
- Test note: headless Chromium runs this scene at ~1.5 fps; use `pg.mouse` (not `pg.click`) and long waits.
