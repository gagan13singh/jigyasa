"""Physics validation: Projectile motion vs analytical solution."""

import math

import pytest

from physengine.analysis.measurements import compare_trajectory_with_analytical
from physengine.analysis.recorder import StateRecorder
from physengine.core.simulation import Simulation
from physengine.core.world import World
from physengine.kinematics.projectile import ProjectileMotion
from physengine.mechanics.forces import UniformGravity
from physengine.mechanics.particle import Particle
from physengine.solvers.rk4 import RK4Integrator
from physengine.solvers.verlet import VelocityVerletIntegrator


def make_projectile_sim(integrator, v0=20, angle_deg=45, dt=0.001, duration=None):
    """Create a projectile simulation."""
    angle_rad = math.radians(angle_deg)
    vx = v0 * math.cos(angle_rad)
    vy = v0 * math.sin(angle_rad)

    world = World(gravity=9.81)
    ball = Particle(
        mass=1.0,
        position=(0, 0),
        velocity=(vx, vy),
        name="projectile",
    )
    world.add(ball)
    world.add_force(UniformGravity())
    world.config.timestep = dt

    # Use analytical time of flight if duration not specified
    if duration is None:
        proj = ProjectileMotion(v0, angle_deg)
        duration = proj.time_of_flight + 0.1

    world.config.duration = duration

    sim = Simulation(world, integrator=integrator)
    sim.run()
    return sim


@pytest.mark.physics
class TestProjectileRK4:
    def test_trajectory_accuracy(self):
        g = 9.81
        proj = ProjectileMotion(v0=20, angle=45, g=g)
        sim = make_projectile_sim(RK4Integrator(), v0=20, angle_deg=45, dt=0.001)

        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("projectile")

        result = compare_trajectory_with_analytical(traj, proj.position_at)

        assert result["max_error"] < 0.01, f"Max error: {result['max_error']}"
        assert result["rmse"] < 0.001

    def test_range(self):
        v0, angle_deg, g = 20, 45, 9.81
        proj = ProjectileMotion(v0, angle_deg, g=g)
        sim = make_projectile_sim(
            RK4Integrator(), v0=v0, angle_deg=angle_deg, dt=0.001, duration=proj.time_of_flight
        )

        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("projectile")

        # Position at the end of time of flight
        final_x = traj.positions[-1].x

        # Should be close to analytical range
        assert abs(final_x - proj.range) / proj.range < 0.01  # Within 1%

    def test_max_height(self):
        v0, angle_deg, g = 20, 60, 9.81
        proj = ProjectileMotion(v0, angle_deg, g=g)
        sim = make_projectile_sim(RK4Integrator(), v0=v0, angle_deg=angle_deg, dt=0.001)

        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("projectile")

        numerical_max_y = max(p.y for p in traj.positions)

        # Within 1% of analytical
        assert abs(numerical_max_y - proj.max_height) / proj.max_height < 0.01


@pytest.mark.physics
class TestProjectileVerlet:
    def test_trajectory_accuracy(self):
        g = 9.81
        proj = ProjectileMotion(v0=20, angle=45, g=g)
        sim = make_projectile_sim(VelocityVerletIntegrator(), v0=20, angle_deg=45, dt=0.001)

        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("projectile")

        result = compare_trajectory_with_analytical(traj, proj.position_at)

        assert result["max_error"] < 0.01


@pytest.mark.physics
class TestProjectileAnalytical:
    def test_45_degree_range(self):
        proj = ProjectileMotion(v0=20, angle=45)
        # R = v²sin(2θ)/g = 400*1/9.81 ≈ 40.775
        expected = 20 * 20 * math.sin(math.radians(90)) / 9.80665
        assert abs(proj.range - expected) < 0.1

    def test_max_height(self):
        proj = ProjectileMotion(v0=20, angle=90)
        # H = v²/(2g) = 400/(2*9.80665) ≈ 20.394
        expected = 20 * 20 / (2 * 9.80665)
        assert abs(proj.max_height - expected) < 0.1

    def test_time_of_flight_vertical(self):
        proj = ProjectileMotion(v0=10, angle=90)
        # T = 2v₀/g = 20/9.80665 ≈ 2.039
        expected = 2 * 10 / 9.80665
        assert abs(proj.time_of_flight - expected) < 0.01

    def test_summary(self):
        proj = ProjectileMotion(v0=20, angle=45)
        summary = proj.summary()
        assert "Range" in summary
        assert "Max height" in summary
