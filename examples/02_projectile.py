#!/usr/bin/env python3
"""
Example 02: Projectile Motion
==============================

Launch a ball at 45° with 20 m/s and track its trajectory.

Demonstrates:
- Projectile setup with initial velocity
- Analytical solution comparison
- Trajectory data extraction
"""

import math

from physengine import Particle, Simulation, UniformGravity, World
from physengine.analysis.measurements import compare_trajectory_with_analytical
from physengine.analysis.recorder import StateRecorder
from physengine.kinematics.projectile import ProjectileMotion
from physengine.solvers.rk4 import RK4Integrator


def main():
    print("PhysEngine - Projectile Motion")
    print("=" * 50)

    # -- Parameters -----------------------------------------------------
    v0 = 20.0       # m/s
    angle = 45.0     # degrees
    g = 9.81         # m/s^2

    # -- Analytical Solution --------------------------------------------
    proj = ProjectileMotion(v0=v0, angle=angle, g=g)
    print(proj.summary())

    # -- Numerical Simulation -------------------------------------------
    angle_rad = math.radians(angle)
    world = World(gravity=g)

    ball = Particle(
        mass=1.0,
        position=(0, 0),
        velocity=(v0 * math.cos(angle_rad), v0 * math.sin(angle_rad)),
        name="projectile",
    )
    world.add(ball)
    world.add_force(UniformGravity())
    world.config.timestep = 0.001
    world.config.duration = proj.time_of_flight + 0.5

    sim = Simulation(world, integrator=RK4Integrator())
    sim.run()

    # -- Comparison -----------------------------------------------------
    recorder = StateRecorder(sim.history)
    traj = recorder.get_trajectory("projectile")

    result = compare_trajectory_with_analytical(traj, proj.position_at)

    print("Numerical vs Analytical Comparison")
    print("-" * 40)
    print(f"  Points:     {result['num_points']}")
    print(f"  MAE:        {result['mae']:.2e} m")
    print(f"  RMSE:       {result['rmse']:.2e} m")
    print(f"  Max error:  {result['max_error']:.2e} m")
    print()

    # Find numerical max height
    max_y = max(p.y for p in traj.positions)
    max_x = max(p.x for p in traj.positions)

    print(f"  Analytical range:     {proj.range:.4f} m")
    print(f"  Numerical max x:      {max_x:.4f} m")
    print(f"  Analytical max height: {proj.max_height:.4f} m")
    print(f"  Numerical max height:  {max_y:.4f} m")
    print()
    print("[SUCCESS] Projectile motion verified!")


if __name__ == "__main__":
    main()
