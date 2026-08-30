"""Physics validation: Numerical error comparison across integrators.

Demonstrates that higher-order integrators produce smaller errors,
which is extremely valuable for educational content (Scientia).
"""

import math

import pytest

from physengine.analysis.measurements import compare_trajectory_with_analytical
from physengine.analysis.recorder import StateRecorder
from physengine.core.simulation import Simulation
from physengine.core.world import World
from physengine.kinematics.projectile import ProjectileMotion
from physengine.math.vector import Vector2
from physengine.mechanics.forces import Spring, UniformGravity
from physengine.mechanics.particle import Particle
from physengine.solvers.euler import EulerIntegrator, SemiImplicitEulerIntegrator
from physengine.solvers.rk4 import RK4Integrator
from physengine.solvers.verlet import VelocityVerletIntegrator


def run_harmonic_oscillator_sim(integrator, dt=0.01, k=10.0, m=1.0, x0=5.0, duration=3.0):
    """Run a 1D harmonic oscillator simulation with the given integrator."""
    world = World(gravity=0)
    mass = Particle(
        mass=m,
        position=(x0, 0),
        velocity=(0, 0),
        name="mass",
    )
    world.add(mass)
    spring = Spring(stiffness=k, anchor=Vector2.zero(), rest_length=0.0)
    world.add_force_to(mass, spring)
    world.config.timestep = dt
    world.config.duration = duration

    sim = Simulation(world, integrator=integrator)
    sim.run()
    return sim


def run_projectile_sim(integrator, dt=0.01, g=9.81):
    """Run a standard projectile simulation with the given integrator."""
    v0 = 20
    angle = 45
    angle_rad = math.radians(angle)

    world = World(gravity=g)
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


@pytest.mark.numerical
class TestIntegratorErrorOrdering:
    def test_rk4_beats_verlet_beats_euler(self):
        """RK4 error < Verlet error < Euler error on harmonic oscillator."""
        dt = 0.05
        k, m, x0 = 10.0, 1.0, 5.0
        omega = math.sqrt(k / m)

        def analytical_pos(t: float) -> Vector2:
            return Vector2(x0 * math.cos(omega * t), 0.0)

        sims = {
            "euler": run_harmonic_oscillator_sim(
                EulerIntegrator(), dt=dt, k=k, m=m, x0=x0
            ),
            "verlet": run_harmonic_oscillator_sim(
                VelocityVerletIntegrator(), dt=dt, k=k, m=m, x0=x0
            ),
            "rk4": run_harmonic_oscillator_sim(
                RK4Integrator(), dt=dt, k=k, m=m, x0=x0
            ),
        }

        errors = {}
        for name, sim in sims.items():
            recorder = StateRecorder(sim.history)
            traj = recorder.get_trajectory("mass")
            result = compare_trajectory_with_analytical(traj, analytical_pos)
            errors[name] = result["rmse"]

        # RK4 error < Verlet error
        assert errors["rk4"] < errors["verlet"], (
            f"RK4 ({errors['rk4']:.6e}) should be less than Verlet ({errors['verlet']:.6e})"
        )

        # Verlet error < Euler error
        assert errors["verlet"] < errors["euler"], (
            f"Verlet ({errors['verlet']:.6e}) should be less than Euler ({errors['euler']:.6e})"
        )

    def test_error_decreases_with_dt(self):
        """Reducing dt should reduce error for all integrators."""
        g = 9.81
        proj = ProjectileMotion(v0=20, angle=45, g=g)

        for integrator_cls in [EulerIntegrator, SemiImplicitEulerIntegrator]:
            sim_coarse = run_projectile_sim(integrator_cls(), dt=0.01, g=g)
            sim_fine = run_projectile_sim(integrator_cls(), dt=0.001, g=g)

            rec_c = StateRecorder(sim_coarse.history)
            rec_f = StateRecorder(sim_fine.history)

            traj_c = rec_c.get_trajectory("ball")
            traj_f = rec_f.get_trajectory("ball")

            err_c = compare_trajectory_with_analytical(traj_c, proj.position_at)["rmse"]
            err_f = compare_trajectory_with_analytical(traj_f, proj.position_at)["rmse"]

            assert err_f < err_c, (
                f"{integrator_cls.__name__}: fine ({err_f:.6e}) < coarse ({err_c:.6e})"
            )
