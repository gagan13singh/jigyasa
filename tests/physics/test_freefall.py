"""Physics validation: Freefall simulation vs analytical solution.

Tests that a ball dropped from height h under gravity g follows
the exact kinematic equations within acceptable numerical error.
"""


import pytest

from physengine.analysis.measurements import compare_trajectory_with_analytical
from physengine.analysis.recorder import StateRecorder
from physengine.core.simulation import Simulation
from physengine.core.world import World
from physengine.kinematics.motion import position_2d
from physengine.math.vector import Vector2
from physengine.mechanics.forces import UniformGravity
from physengine.mechanics.particle import Particle
from physengine.solvers.euler import EulerIntegrator
from physengine.solvers.rk4 import RK4Integrator
from physengine.solvers.verlet import VelocityVerletIntegrator


def make_freefall_sim(integrator, dt=0.001, duration=2.0):
    """Create a standard freefall simulation."""
    world = World(gravity=9.81)
    ball = Particle(mass=1.0, position=(0, 100), name="ball")
    world.add(ball)
    world.add_force(UniformGravity())
    world.config.timestep = dt
    world.config.duration = duration

    sim = Simulation(world, integrator=integrator)
    sim.run()
    return sim


def analytical_freefall(t):
    """Analytical position for freefall from y=100."""
    return position_2d(
        pos0=Vector2(0, 100),
        vel0=Vector2.zero(),
        acc=Vector2(0, -9.81),
        t=t,
    )


@pytest.mark.physics
class TestFreefallRK4:
    def test_position_accuracy(self):
        sim = make_freefall_sim(RK4Integrator(), dt=0.001, duration=2.0)
        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("ball")

        result = compare_trajectory_with_analytical(traj, analytical_freefall)

        # RK4 with dt=0.001 should be extremely accurate for constant acceleration
        assert result["max_error"] < 1e-4, f"Max error: {result['max_error']}"
        assert result["rmse"] < 1e-5, f"RMSE: {result['rmse']}"

    def test_final_position(self):
        sim = make_freefall_sim(RK4Integrator(), dt=0.001, duration=2.0)
        ball = sim.world.get_entity("ball")

        # Analytical: y = 100 - 0.5 * 9.81 * 4 = 100 - 19.62 = 80.38
        expected_y = 100 - 0.5 * 9.81 * 2.0 * 2.0
        assert abs(ball.position.y - expected_y) < 0.01

    def test_final_velocity(self):
        sim = make_freefall_sim(RK4Integrator(), dt=0.001, duration=2.0)
        ball = sim.world.get_entity("ball")

        # v = 0 + (-9.81) * 2 = -19.62
        expected_vy = -9.81 * 2.0
        assert abs(ball.velocity.y - expected_vy) < 0.01


@pytest.mark.physics
class TestFreefallVerlet:
    def test_position_accuracy(self):
        sim = make_freefall_sim(VelocityVerletIntegrator(), dt=0.001, duration=2.0)
        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("ball")

        result = compare_trajectory_with_analytical(traj, analytical_freefall)
        # Verlet should be very accurate for constant acceleration
        assert result["max_error"] < 1e-3


@pytest.mark.physics
class TestFreefallEuler:
    def test_position_converges(self):
        """Euler with small dt should still give reasonable results."""
        sim = make_freefall_sim(EulerIntegrator(), dt=0.0001, duration=1.0)
        ball = sim.world.get_entity("ball")

        expected_y = 100 - 0.5 * 9.81 * 1.0
        # Euler has more error but should be within 1%
        assert abs(ball.position.y - expected_y) < 0.5
