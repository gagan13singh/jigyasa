# Architecture — PhysEngine

## 5-Layer Architecture

```
┌─────────────────────────────────┐
│        Applications             │
│  Scientia  │  Vidyastra  │ CLI  │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│          Public API             │
│  World · Particle · Simulation  │
│  Forces · Solvers · Analysis    │
└──────────────┬──────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌──────────────┐  ┌──────────────┐
│ Physics Core │  │ Visualization│
│              │  │              │
│ Vectors      │  │ Renderer     │
│ Bodies       │  │ (abstract)   │
│ Forces       │  │              │
│ Solvers      │  │ Manim        │
│ Collisions   │  │ Web          │
└──────┬───────┘  └──────────────┘
       │
       ▼
┌─────────────────────────────────┐
│   Simulation Infrastructure    │
│  Entity · World · State · Clock │
│  Events · Config · Recording    │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Mathematical Foundation      │
│  Vector2/3 · Constants          │
│  Interpolation · Units          │
└─────────────────────────────────┘
```

## Data Flow

```
Initialize World
       │
Add Entities + Forces
       │
  ┌────▼────────────┐
  │  Simulation Loop │◄──── Clock
  │                  │
  │  For each entity:│
  │    Accumulate    │
  │    forces        │
  │    ↓             │
  │    net_force/m   │
  │    = acceleration│
  │    ↓             │
  │    Integrator    │
  │    .step()       │
  │    ↓             │
  │    Update state  │
  │    ↓             │
  │    Record        │
  │    snapshot      │
  └────┬─────────────┘
       │
  StateHistory
       │
  ┌────┴────┐
  │         │
Analysis  Renderer
  │         │
Metrics  Animation
```

## Module Dependencies

```
math ──────► (no dependencies)
units ─────► math
core ──────► math, units
mechanics ─► math, core
kinematics ► math
solvers ───► math
analysis ──► math, core
rendering ─► math, core (abstract only)
io ────────► core, analysis, mechanics
```

## Key Invariants

1. **No circular imports** — dependency graph is a DAG
2. **No renderer in core** — `rendering/` only has abstract base classes
3. **Immutable vectors** — all Vector operations return new instances
4. **Frozen state** — EntityState and SimulationState are immutable
5. **SI units internally** — all physics in meters, kilograms, seconds
6. **Forces are pure functions** — calculate() receives state, returns vector
