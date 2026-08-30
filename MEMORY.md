# Project Memory & Architecture Context

## 1. Engine Mission & Principle
- **Core Principle**: "Physics should know nothing about Manim. Manim should know nothing about how the physics is calculated."
- **Target Audience**: High school students & teachers (Classes 9–12, CBSE/ICSE/JEE/NEET).
- **Core Framework**: Python RK4 physical simulation engine + Zero-lag 60 FPS client-side interactive visualizer + Manim export pipeline.

---

## 2. Package Architecture
```
src/physengine/
├── core/               # World, Simulation, Particle, RigidBody, Integrators (Euler, Verlet, RK4)
├── math/               # Vector2, Vector3, Quantity, Unit, Physical Constants
├── mechanics/          # Pulley, Rotational dynamics, Collisions, Fluids & Drag
├── oscillations/       # SHM, Pendulum, Damped & Forced vibrations
├── electromagnetism/   # Coulomb force, Uniform E-field, Lorentz force, Cyclotron
├── curriculum/         # 40-Topic complete Class 9-12 Physics Derivation catalog
├── visualizer/         # Live 3D interactive web visualizer (template.html & server.py)
└── rendering/          # Manim video export script generator
```

---

## 3. 6-Level Derivation Curriculum
- **Level 1**: Fundamental Mechanics (Newton's 2nd Law, Impulse-Momentum theorem, Momentum conservation, 4 Kinematic equations, Newton's 3rd Law).
- **Level 2**: Friction & Inclines (Limiting static friction, Kinetic friction, Angle of friction, Angle of repose, Incline acceleration, Horizontal pull, Angle pull, Min force, Optimum pull angle).
- **Level 3**: Circular Motion & Banking (Centripetal force, Road banking frictionless, Road banking with friction, Vertical circle tension, Critical loop speed).
- **Level 4**: Work, Energy & Power (Constant force work, Variable force work, Work-Energy theorem, Kinetic energy, Gravitational PE, Mechanical energy conservation, Spring PE, Spring work, Mechanical power).
- **Level 5**: Collisions & Restitution (1D elastic collision, Coefficient of restitution, Perfectly inelastic collision, KE loss, Wall collision).
- **Level 6**: Projectile Motion (Horizontal range, Max height, Time of flight, Trajectory equation, Max range at 45°, Complementary angles property).

---

## 4. Test Suite & Verification
- **172 automated unit & physics validation tests passing** in `3.36s` (`pytest tests/`).
- **0 lint errors** (`ruff check src/ tests/ examples/`).
