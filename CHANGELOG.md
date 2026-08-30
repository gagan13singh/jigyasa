# Changelog

All notable changes to PhysEngine are documented here.

## [0.1.0] — 2026-08-30

### 🎉 Initial Release — Stage 0 + Stage 1 (Foundation + Particle Engine)

#### Added
- **Mathematical Foundation**
  - `Vector2` and `Vector3` immutable vector classes with full operator overloading
  - Physical constants (CODATA 2018) and mathematical constants
  - Interpolation utilities: lerp, smoothstep, Catmull-Rom splines, easing functions

- **Units System**
  - `Quantity` class with automatic dimensional analysis
  - `Dimension` type with SI base-unit exponent representation
  - 60+ pre-registered units (length, mass, time, velocity, force, energy, etc.)
  - `DimensionalError` for type-safe unit arithmetic

- **Simulation Infrastructure**
  - Entity-Component architecture (`Entity`, `Component`, `Transform`, `RigidBodyComponent`)
  - `World` container with entity and force management
  - `Simulation` kernel with configurable timestep, duration, and recording
  - `Clock` for time management
  - `EventBus` with pub/sub pattern and lifecycle events
  - `SimulationConfig` with sensible defaults

- **Classical Mechanics**
  - `Particle` convenience class (Entity + Transform + RigidBody)
  - Forces: `UniformGravity`, `PointGravity`, `Drag`, `Spring`, `Friction`, `ConstantForce`, `CompositeForce`
  - Energy calculations: kinetic, gravitational PE, spring PE, total mechanical
  - Momentum: linear, impulse, center of mass

- **Kinematics**
  - Analytical 1D/2D motion equations
  - `ProjectileMotion` class with complete analytical solution (range, max height, time of flight, trajectory)

- **Numerical Solvers**
  - `EulerIntegrator` (1st order, forward)
  - `SemiImplicitEulerIntegrator` (1st order, symplectic)
  - `VelocityVerletIntegrator` (2nd order, symplectic)
  - `RK4Integrator` (4th order)

- **Analysis Layer**
  - `StateRecorder` for trajectory extraction
  - `Trajectory` class with CSV/JSON export
  - Scientific validation: energy drift, momentum conservation, analytical comparison (MAE, RMSE)

- **Rendering Interface**
  - Abstract `Renderer` base class
  - `CoordinateMapper` for physics ↔ renderer coordinate conversion
  - `RenderHint` for visual styling

- **I/O Layer**
  - Save/load `World` to JSON with version tagging
  - Export trajectories to CSV and JSON

- **Tests**
  - 100+ unit tests for vectors, quantities, particles, forces, integrators, events
  - Physics validation: freefall, projectile, energy conservation, momentum conservation
  - Numerical accuracy: integrator error ordering (RK4 < Verlet < Euler)
  - Integration tests: full pipeline, spring oscillator, save/load, export

- **Documentation**
  - `MEMORY.md` — AI agent context file
  - `ARCHITECTURE.md` — 5-layer architecture with diagrams
  - `README.md` — Quick start, feature table, examples
  - `CONTRIBUTING.md` — Code style, testing, architecture rules

- **Examples**
  - `01_freefall.py` — Ball under gravity with analytical comparison
  - `02_projectile.py` — Projectile at 45° with trajectory analysis
  - `03_spring.py` — Spring-mass oscillator with energy conservation
  - `04_solver_comparison.py` — Compare all 4 integrators
