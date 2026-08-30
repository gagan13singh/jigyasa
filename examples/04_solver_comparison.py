#!/usr/bin/env python3
"""
Example 04: Solver Comparison
==============================

Compare all integrators (Euler, Semi-Implicit Euler, Verlet, RK4)
on the same projectile problem.

Shows error metrics, energy drift, and helps understand
WHY higher-order methods matter.

This is exactly the kind of analysis Scientia can use to
teach numerical methods.
"""

import math

from physengine import Particle, Simulation, UniformGravity, World
from physengine.analysis.measurements import (
    compare_trajectory_with_analytical,
)
from physengine.analysis.recorder import StateRecorder
from physengine.kinematics.projectile import ProjectileMotion
from physengine.solvers.euler import EulerIntegrator, SemiImplicitEulerIntegrator
from physengine.solvers.rk4 import RK4Integrator
from physengine.solvers.verlet import VelocityVerletIntegrator


def run_with_integrator(integrator, dt=0.01):
    """Run the standard projectile simulation."""
    v0, angle_deg = 20.0, 45.0
    angle_rad = math.radians(angle_deg)

    world = World(gravity=9.81)
    ball = Particle(
        mass=1.0,
        position=(0, 0),
        velocity=(v0 * math.cos(angle_rad), v0 * math.sin(angle_rad)),
        name="ball",
    )
    world.add(ball)
    world.add_force(UniformGravity())
    world.config.timestep = dt
    world.config.duration = 3.0

    sim = Simulation(world, integrator=integrator)
    sim.run()
    return sim


def main():
    print("PhysEngine - Solver Comparison")
    print("=" * 70)

    proj = ProjectileMotion(v0=20, angle=45, g=9.81)

    integrators = [
        ("Forward Euler (1st order)", EulerIntegrator()),
        ("Semi-Implicit Euler (1st order, symplectic)", SemiImplicitEulerIntegrator()),
        ("Velocity Verlet (2nd order, symplectic)", VelocityVerletIntegrator()),
        ("RK4 (4th order)", RK4Integrator()),
    ]

    for dt in [0.01, 0.001]:
        print(f"\n{'-' * 70}")
        print(f"  Timestep: dt = {dt} s")
        print(f"{'-' * 70}")
        print()
        print(
            f"  {'Integrator':<45} "
            f"{'RMSE (m)':>12} "
            f"{'Max Error (m)':>14}"
        )
        print(f"  {'-' * 73}")

        for name, integ in integrators:
            sim = run_with_integrator(integ, dt=dt)
            recorder = StateRecorder(sim.history)
            traj = recorder.get_trajectory("ball")

            result = compare_trajectory_with_analytical(traj, proj.position_at)

            print(
                f"  {name:<45} "
                f"{result['rmse']:>12.2e} "
                f"{result['max_error']:>14.2e}"
            )

    # -- Key Takeaway ---------------------------------------------------
    print(f"\n{'-' * 70}")
    print("  Key Takeaways:")
    print("  * RK4 has drastically less error than Euler for the same dt")
    print("  * Reducing dt by 10x reduces Euler error by ~10x (1st order)")
    print("  * Verlet is symplectic -> excellent for long-term simulations")
    print("  * Forward Euler is never recommended for production use")
    print(f"{'-' * 70}")
    print()
    print("[SUCCESS] Solver comparison complete!")


if __name__ == "__main__":
    main()
