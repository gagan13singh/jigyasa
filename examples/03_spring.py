#!/usr/bin/env python3
"""
Example 03: Spring-Mass Oscillator
====================================

A mass on a spring oscillates back and forth (simple harmonic motion).

Demonstrates:
- Spring force (Hooke's law)
- Energy conservation in oscillatory systems
- Comparing symplectic vs non-symplectic integrators
"""

import math

from physengine import Particle, Simulation, Vector2, World
from physengine.analysis.measurements import energy_drift
from physengine.analysis.recorder import StateRecorder
from physengine.mechanics.forces import Spring
from physengine.solvers.euler import EulerIntegrator
from physengine.solvers.rk4 import RK4Integrator
from physengine.solvers.verlet import VelocityVerletIntegrator


def run_spring(integrator, dt=0.001, duration=20.0):
    """Run a spring-mass simulation."""
    world = World(gravity=0)  # No gravity, just spring

    mass = Particle(mass=1.0, position=(5, 0), velocity=(0, 0), name="mass")
    world.add(mass)

    spring = Spring(stiffness=10.0, anchor=Vector2.zero(), rest_length=0.0)
    world.add_force_to(mass, spring)

    world.config.timestep = dt
    world.config.duration = duration

    sim = Simulation(world, integrator=integrator)
    sim.run()
    return sim


def main():
    print("PhysEngine - Spring-Mass Oscillator")
    print("=" * 50)

    # -- Analytical Properties ------------------------------------------
    k = 10.0
    m = 1.0
    x0 = 5.0
    omega = math.sqrt(k / m)
    period = 2 * math.pi / omega

    print(f"\nSpring constant:  k = {k} N/m")
    print(f"Mass:             m = {m} kg")
    print(f"Initial displacement: x0 = {x0} m")
    print(f"Angular frequency: omega = {omega:.4f} rad/s")
    print(f"Period:           T = {period:.4f} s")
    print(f"Expected amplitude: A = {x0} m")
    print()

    # -- Compare Integrators --------------------------------------------
    integrators = {
        "Forward Euler": EulerIntegrator(),
        "Velocity Verlet": VelocityVerletIntegrator(),
        "RK4": RK4Integrator(),
    }

    print(f"{'Integrator':<20} {'Energy Drift':>15} {'Max Deviation':>15}")
    print("-" * 55)

    for name, integ in integrators.items():
        sim = run_spring(integ, dt=0.001, duration=20.0)
        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("mass")

        # Energy = 0.5*k*x^2 + 0.5*m*v^2
        ke = traj.kinetic_energies
        pe = [0.5 * k * p.x * p.x for p in traj.positions]

        result = energy_drift(ke, pe)

        print(
            f"  {name:<18} "
            f"{result['relative_drift']:>14.2e} "
            f"{result['max_deviation']:>14.2e}"
        )

    print()
    print("Note: Forward Euler's energy GROWS -> the oscillation spirals outward.")
    print("      Verlet and RK4 keep energy bounded -> stable oscillations.")
    print()
    print("[SUCCESS] Spring oscillator comparison complete!")


if __name__ == "__main__":
    main()
