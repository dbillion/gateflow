# Gateflow — Oludayo's Airport Operations 3D

> Live 3D Airport Operations Dashboard built with Three.js (World 01 from World Prompt Pack)

[![Live Demo](https://img.shields.io/badge/Demo-GitHub%20Pages-FF6A1A?style=for-the-badge&logo=github)](https://dbillion.github.io/gateflow/)

---

## How 3D Polygons are Generated & Exported into a Single HTML File

A key architectural feature of **Gateflow** is that **zero external 3D asset files** (`.gltf`, `.glb`, `.obj`, or `.fbx`) are used. Instead, all 3D polygons, geometries, and spatial assemblies are procedurally generated in JavaScript using Three.js mathematical primitives directly embedded within [`index.html`](index.html).

### 1. Mathematical Polygon Generation
Every physical airport asset is assembled from parametric Three.js geometry classes:
- **Aircraft Airframe**:
  - Fuselage: Cylindrical hull via `THREE.CylinderGeometry(2.1, 2.1, 28, 16)` with rounded cap meshes.
  - Nose & Tail: Aerodynamic fairings generated via `THREE.ConeGeometry(2.1, 5.5, 16)` and `ConeGeometry(2.1, 8.5, 16)`.
  - Swept Wings & Sharklets: Thin extruded boxes `THREE.BoxGeometry(9, 0.45, 26)` angled with sweepback and canted vertical winglets.
  - Turbofan Engines: Hollow intake cowlings `THREE.CylinderGeometry(1.5, 1.4, 5.5, 14, 1, true)` with spinning interior spinner cones.
  - Tricycle Landing Gear: Retractable struts and rotating wheel cylinders (`THREE.CylinderGeometry(0.55, 0.55, 0.6, 10)`).
- **Cargo Terminal & Boeing 777F Freighter**:
  - Widebody cargo fuselage (38m length, 5.6m diameter) with main deck cargo loading door and high-bypass GE90 engine nacelles.
  - Active Cargo Forklift: Chassis, protective roll cage, and animated vertical lifting mast carrying standard aviation LD3/AKE ULD containers.
- **Terminal & Infrastructure**:
  - Clay modular terminal body with rooftop HVAC chillers, illuminated gate rotundas, and 5 articulated telescopic jet bridges.
  - ATC Tower: 38m clay shaft, 360° tinted observation cab, and an animated radar antenna array.
  - Active Runway (09L/27R): High-friction asphalt strip with threshold piano keys, touchdown zone stripes, and illuminated dual edge lights.

### 2. Scene Graph Hierarchy & Materials
- All sub-components are attached to parent `THREE.Group` nodes. When the aircraft translates, rolls, pitches, or yaws, all child elements (engines, landing gear, doors, wings, lights) transform in coordinated local coordinate spaces.
- Materials use clay-style `THREE.MeshStandardMaterial` with soft roughness (0.65–0.85) and subtle metalness (0.05–0.1) paired with ACESFilmic tone mapping and directional PCF soft shadow maps.

### 3. Git & GitHub Single-File Deployment
Because all geometry is programmatic code rather than heavy binary 3D assets:
- The entire application (3D engine, models, animation state machine, and glassmorphic UI) resides in a lightweight self-contained file (`index.html`).
- Changes are instantly version-controlled in Git, diffable in pull requests, and deployable to GitHub Pages with zero build pipeline or bundler requirements.

---

## Kinematics & Simulation Features

- **Continuous Flight Trajectories**:
  - **Runway 09L Takeoff**: Full-throttle acceleration roll ➔ rotation pitch-up (-12°) ➔ gear retraction ➔ climbing right-hand departure turn ➔ high-altitude circuit pattern.
  - **Final Approach & Landing**: Intercepts 3-degree glide slope straight down the extended runway centerline ➔ flare touchdown ➔ rollout deceleration with thrust reversers ➔ 90° taxiway fillet turn.
- **Dedicated Cargo Operations**:
  - Boeing 777F Freighter docked at Cargo Bay C1.
  - Active Heavy Forklift transporting ULD cargo containers with animated vertical mast tines.
- **Performance & Zero-Freeze Architecture**:
  - All scratch vectors are pre-allocated and reused across frames, eliminating garbage collection pauses.
  - CCTV security monitor rendering is throttled to an authentic 10 FPS, preventing GPU command buffer stalls.
  - Turnaround state transitions and table rendering are throttled to event ticks.

---

## Live Links
- **GitHub Pages**: [https://dbillion.github.io/gateflow/](https://dbillion.github.io/gateflow/)
- **Repository**: [https://github.com/dbillion/gateflow](https://github.com/dbillion/gateflow)
