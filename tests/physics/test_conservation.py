"""Physics validation: Conservation laws.

Tests that the engine correctly conserves energy and momentum
in appropriate scenarios.
"""

import pytest

from physengine.analysis.measurements import energy_drift, momentum_conservation
from physengine.analysis.recorder import StateRecorder
from physengine.core.simulation import Simulation
from physengine.core.world import World
from physengine.mechanics.forces import UniformGravity
from physengine.mechanics.particle import Particle
from physengine.solvers.rk4 import RK4Integrator
from physengine.solvers.verlet import VelocityVerletIntegrator


@pytest.mark.physics
class TestEnergyConservation:
    def test_freefall_energy_rk4(self):
        """In freefall (conservative force only), total energy should be conserved."""
        world = World(gravity=9.81)
        ball = Particle(mass=1.0, position=(0, 50), name="ball")
        world.add(ball)
        world.add_force(UniformGravity())
        world.config.timestep = 0.001
        world.config.duration = 3.0

        sim = Simulation(world, integrator=RK4Integrator())
        sim.run()

        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("ball")

        # Compute total energy (KE + PE) at each step
        g = 9.81
        kes = traj.kinetic_energies
        pes = [1.0 * g * p.y for p in traj.positions]  # m*g*h

        result = energy_drift(kes, pes)

        # Energy drift should be very small with RK4
        assert result["relative_drift"] < 0.001, \
            f"Energy drift: {result['relative_drift']:.6f}"

    def test_freefall_energy_verlet(self):
        """Verlet should have even better energy conservation (symplectic)."""
        world = World(gravity=9.81)
        ball = Particle(mass=1.0, position=(0, 50), name="ball")
        world.add(ball)
        world.add_force(UniformGravity())
        world.config.timestep = 0.001
        world.config.duration = 3.0

        sim = Simulation(world, integrator=VelocityVerletIntegrator())
        sim.run()

        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("ball")

        g = 9.81
        kes = traj.kinetic_energies
        pes = [1.0 * g * p.y for p in traj.positions]

        result = energy_drift(kes, pes)
        assert result["relative_drift"] < 0.001


@pytest.mark.physics
class TestMomentumConservation:
    def test_no_force_momentum(self):
        """With no forces, total momentum should be exactly conserved."""
        world = World(gravity=0)  # No gravity
        p1 = Particle(mass=1.0, velocity=(5, 3), name="p1")
        p2 = Particle(mass=2.0, velocity=(-1, 2), name="p2")
        world.add(p1)
        world.add(p2)
        # No forces added
        world.config.timestep = 0.01
        world.config.duration = 5.0

        sim = Simulation(world, integrator=RK4Integrator())
        sim.run()

        momenta = sim.history.total_momenta()
        result = momentum_conservation(momenta)

        # Should be exactly conserved (no forces)
        assert result["max_deviation"] < 1e-10, \
            f"Momentum deviation: {result['max_deviation']}"
