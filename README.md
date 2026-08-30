# ✨ Jigyasa — A Part of Scientia Learning

**Interactive 2D Blueprint & 3D Volumetric Physics Simulation & Derivation Engine for Classes 9–12 / JEE / NEET.**

Jigyasa is an industry-grade, renderer-agnostic physics lab and derivation engine developed as part of **Scientia Learning** (powering [Scientia](https://github.com/gagandeep/scientia) and [Vidyastra](https://github.com/gagandeep/vidyastra)). It delivers exact mathematical derivations with live numerical substitution, complete NCERT Class 9–12 physics curricula, and real-time interactive 60 FPS simulations.

## Quick Start

```python
from physengine import World, Particle, Simulation, UniformGravity

# Create a world with gravity
world = World(gravity=9.81)

# Add a ball at height 100m
ball = Particle(mass=1.0, position=(0, 100), name="ball")
world.add(ball)
world.add_force(UniformGravity())

# Simulate for 4 seconds
sim = Simulation(world)
sim.run(duration=4.0)

# Analyze results
positions = sim.history.get_entity_positions("ball")
print(f"Final position: {positions[-1]}")
```

## Features

| Feature | Status |
|---------|--------|
| 2D Vector Mathematics | ✅ |
| 3D Vector Mathematics | ✅ |
| Units & Dimensional Analysis | ✅ |
| Entity-Component Architecture | ✅ |
| Simulation Kernel | ✅ |
| Event System | ✅ |
| Forward Euler Integrator | ✅ |
| Semi-Implicit Euler (Symplectic) | ✅ |
| Velocity Verlet Integrator | ✅ |
| RK4 Integrator | ✅ |
| Gravity, Spring, Drag, Friction | ✅ |
| Kinetic/Potential Energy | ✅ |
| Momentum Conservation | ✅ |
| Analytical Projectile Motion | ✅ |
| Trajectory Recording & Export | ✅ |
| Scientific Validation Suite | ✅ |
| Save/Load Simulations (JSON) | ✅ |
| Abstract Renderer Interface | ✅ |
| Collision Detection | 🚧 |
| Rigid Body Dynamics | 🚧 |
| Manim Renderer | 🚧 |
| Web Renderer | 📋 |

## Installation

```bash
pip install -e ".[dev]"
```

## Interactive 2D Visualizer

You can launch the live interactive simulation visualizer in your web browser:

```bash
python visualize.py
```

This opens a dark-mode, 60fps simulation playground with:
- **Real-Time Animation**: Smooth rendering with glowing particles and vector arrows ($\vec{v}$ in cyan, $\vec{a}$ in amber).
- **Trajectory Trails**: Trace lines showing the exact kinematic path.
- **Interactive Telemetry HUD**: Live metrics for position, speed, acceleration, and kinetic energy.
- **Timeline & Controls**: Play, pause, restart, scrub timeline, and adjust playback speed (0.25× to 2.0×).
- **Simulation Presets**: Projectile Motion, Freefall, Spring-Mass SHM Oscillator, and 2-Body Gravitational Orbit.
- **Custom Parameters**: Tweak initial speed, launch angle, gravity, air resistance, and numerical integrators (RK4, Verlet, Euler) live!

### Export Standalone Offline HTML Animations

Export self-contained `.html` animations from your Python scripts:

```bash
python examples/05_interactive_web.py
```

## Running Examples

```bash
python examples/01_freefall.py
python examples/02_projectile.py
python examples/03_spring.py
python examples/04_solver_comparison.py
python examples/05_interactive_web.py
```

## Running Tests

```bash
pytest                          # All tests
pytest tests/unit/              # Unit tests only
pytest tests/physics/           # Physics validation
pytest tests/integration/       # End-to-end pipeline
```

## Architecture

```
Physics Engine → Public API → Renderers (Manim, Web, etc.)
```

The engine knows **nothing** about rendering. `simulation.step(dt)` works perfectly fine without Manim installed. See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## For AI Agents

See [MEMORY.md](MEMORY.md) for full project context, module map, coding conventions, and integration patterns.

## License

MIT
