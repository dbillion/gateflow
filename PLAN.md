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
- [ ] B. Day/night + season shared state: ambient/hemi/dir light not restored after night->day; rain persists when
      season changed at night; night ignores season. Fix = one `applyEnvironment()` computing everything from
      `(AppState.isNight, AppState.season)`; `toggleDayNight` and `changeSeason` only set state then call it.
- [ ] C. Detail panel stale values: `selectEntity()` only overwrites fields when present, so a stand/facility shows the
      previous aircraft's origin/fuel/pax. Reset every field per entity type (aircraft / vehicle / stand / facility).
- [ ] D. Click vs drag: selection fires on `pointerdown`, so starting an orbit drag selects. Select on `pointerup`
      only if the pointer moved < ~5 px since `pointerdown`.
- [ ] E. Hangar interior hidden by roof: fade roof (low opacity) while hangar view or hangar selection is active.

## Backlog (not started, from the full-file review)
- Detail-panel telemetry (speed/alt/status) is not live; per-flight origin/dest data is shared across aircraft.
- Table counts in tab labels (Stands 5 / Vehicles 12 / Flights 10) do not match rows; times (STA/STD, tracker steps,
  header clock) are not on one simulated clock; table `selected` row is hard-coded.
- Search only matches a few hard-coded strings.
- CCTV feeds are 2D fakes unrelated to the live scene.
- README claims to re-check: rain "streaks", de-icing trucks in snow, hangar contents, landside vehicle loop.
- Night: runway/taxiway lights are unlit MeshBasicMaterial with no glow.
