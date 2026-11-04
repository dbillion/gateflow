# Gateflow — Sanjai International Airport Operations 3D

> Live 3D Airport Operations Dashboard built with Three.js (World 01 from World Prompt Pack)

[![Live Demo](https://img.shields.io/badge/Demo-GitHub%20Pages-FF6A1A?style=for-the-badge&logo=github)](https://dbillion.github.io/gateflow/)

## Features

- **Procedural 3D Airport (No external 3D models)**:
  - Terminal building with frosted glass facade and 5 gates with articulated jet bridges (A1 to A5).
  - Active Runway (09L/27R) with threshold piano keys, touchdown zone stripes, and illuminated edge lights.
  - Air Traffic Control Tower with rotating radar dish and 360° tinted cab.
  - Cargo Terminal with Boeing 777F freighter and colorful ULD container stacks.
  - Open MRO Maintenance Hangar with interior worklights.
  - Landside forecourt with vehicle loop, parking bays with parked cars, and palm trees.

- **Life & Continuous Simulation**:
  - Two procedural A320neo aircraft cycling forever through: Approach ➔ Touchdown ➔ Rollout ➔ Taxi to Gate ➔ Turnaround ➔ Tug Pushback ➔ Taxi to Holding Point ➔ Takeoff Roll ➔ Gear Retraction ➔ Circuit.
  - Autonomous GSE: Pushback tug, baggage train with luggage carts, and catering hi-lift truck with scissor-lift box.

- **Glassmorphic Strategy Dashboard**:
  - Top Bar with area switcher (Overview, Terminal, Runway, Cargo, Hangar, Landside), live search, seasons selector, day/night toggle, and real-time clock.
  - 3 KPI Cards: Flights Today (142), Passengers (24,580), Cargo (612 t).
  - Right Detail Panel with live procedural CCTV radar/apron feed with switchable cameras (A3, RWY, TWR, Cargo) and flight telemetry.
  - Bottom-Left 6-step Turnaround Tracker with real-time countdown.
  - Bottom-Right live operations table for Stands, Vehicles, and Flights.
  - Dynamic 3D floating HUD tag and camera follow mode.

- **Environmental & Seasons Controls**:
  - Summer (Clear golden light)
  - Monsoon (Rain streaks & lightning flashes)
  - Winter (CAT III Dense Fog)
  - Snow (Snowflakes & de-icing procedures)
  - Day / Night cycle with glowing runway lights and floodlights.

## Tech Stack
- HTML5 / CSS3 (Frosted Glassmorphism)
- [Three.js](https://threejs.org/) (Procedural Low-Poly 3D Engine)
- [OrbitControls](https://threejs.org/docs/#examples/en/controls/OrbitControls)

## Running Locally
Simply open `index.html` in any browser, or run:
```bash
python3 -m http.server 8085
```
and navigate to `http://localhost:8085`.
