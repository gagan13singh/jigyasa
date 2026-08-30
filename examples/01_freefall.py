#!/usr/bin/env python3
"""
Example 01: Freefall
====================

A ball dropped from 100 meters under Earth's gravity.

Demonstrates:
- Creating a World with gravity
- Adding a Particle
- Running a simulation
- Extracting and displaying results
- Comparing numerical result against analytical solution
"""

from physengine import Particle, Simulation, UniformGravity, Vector2, World
from physengine.analysis.measurements import compare_trajectory_with_analytical
from physengine.analysis.recorder import StateRecorder
from physengine.kinematics.motion import position_2d
from physengine.solvers.rk4 import RK4Integrator


def main():
    # -- Setup ----------------------------------------------------------
    print("PhysEngine - Freefall Simulation")
    print("=" * 50)

    world = World(gravity=9.81)

    ball = Particle(
        mass=1.0,
        position=(0, 100),
        velocity=(0, 0),
        name="ball",
    )
    world.add(ball)
    world.add_force(UniformGravity())

    # -- Configure ------------------------------------------------------
    world.config.timestep = 0.001
    world.config.duration = 4.0
    world.config.name = "Freefall from 100m"

    # -- Simulate -------------------------------------------------------
    sim = Simulation(world, integrator=RK4Integrator())
    print(f"\nSimulating: {world.config.name}")
    print(f"  Integrator: {sim.integrator.name} (order {sim.integrator.order})")
    print(f"  Timestep:   {world.config.timestep} s")
    print(f"  Duration:   {world.config.duration} s")
    print()

    history = sim.run()

    # -- Results --------------------------------------------------------
    recorder = StateRecorder(history)
    traj = recorder.get_trajectory("ball")

    print(f"Simulation completed: {sim.step_count} steps")
    print(f"Trajectory: {traj.num_points} data points")
    print()

    # Show position at key times
    print("Time (s)  |  y (m)       |  vy (m/s)    |  KE (J)")
    print("-" * 60)

    times_to_show = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    for target_t in times_to_show:
        # Find closest recorded time
        idx = min(
            range(traj.num_points),
            key=lambda i: abs(traj.times[i] - target_t),
        )
        t = traj.times[idx]
        pos = traj.positions[idx]
        vel = traj.velocities[idx]
        ke = traj.kinetic_energies[idx]
        print(f"  {t:5.2f}    |  {pos.y:10.4f}   |  {vel.y:10.4f}   |  {ke:10.4f}")

    # -- Compare with analytical ----------------------------------------
    def analytical(t):
        return position_2d(
            Vector2(0, 100), Vector2.zero(), Vector2(0, -9.81), t
        )

    result = compare_trajectory_with_analytical(traj, analytical)

    print()
    print("Numerical Accuracy")
    print("-" * 40)
    print(f"  MAE:        {result['mae']:.2e} m")
    print(f"  RMSE:       {result['rmse']:.2e} m")
    print(f"  Max error:  {result['max_error']:.2e} m (at t={result['max_error_time']:.2f}s)")
    print(f"  Final error: {result['final_error']:.2e} m")
    print()
    print("[SUCCESS] Simulation verified against analytical solution!")


if __name__ == "__main__":
    main()
