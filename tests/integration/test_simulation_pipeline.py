"""Integration tests: End-to-end simulation pipeline.

Tests the complete flow:
    Create World → Add Entities → Add Forces → Simulate →
    Record States → Extract Trajectories → Export Data
"""

import json

from physengine.analysis.recorder import StateRecorder
from physengine.core.simulation import Simulation, SimulationStatus
from physengine.core.world import World
from physengine.io.serialization import load_world, save_world
from physengine.math.vector import Vector2
from physengine.mechanics.forces import Spring, UniformGravity
from physengine.mechanics.particle import Particle
from physengine.solvers.rk4 import RK4Integrator


class TestFullPipeline:
    def test_freefall_pipeline(self):
        """End-to-end: create → simulate → record → analyze."""
        # 1. Create world
        world = World(gravity=9.81)
        ball = Particle(mass=1.0, position=(0, 100), name="ball")
        world.add(ball)
        world.add_force(UniformGravity())

        # 2. Configure
        world.config.timestep = 0.001
        world.config.duration = 2.0

        # 3. Simulate
        sim = Simulation(world, integrator=RK4Integrator())
        history = sim.run()

        # 4. Verify state
        assert sim.status == SimulationStatus.COMPLETED
        assert sim.clock.time > 1.9
        assert len(history) > 100

        # 5. Analyze
        recorder = StateRecorder(history)
        traj = recorder.get_trajectory("ball")

        assert traj.num_points > 100
        assert traj.duration > 1.9

        # Ball should have fallen
        assert traj.positions[-1].y < traj.positions[0].y

        # Velocity should increase in magnitude (falling)
        assert abs(traj.velocities[-1].y) > abs(traj.velocities[0].y)

    def test_spring_pipeline(self):
        """Spring-mass oscillator: energy should be approximately conserved."""
        world = World(gravity=0)  # No gravity, just spring
        ball = Particle(mass=1.0, position=(5, 0), velocity=(0, 0), name="mass")
        world.add(ball)

        spring = Spring(stiffness=10.0, anchor=Vector2.zero(), rest_length=0.0)
        world.add_force_to(ball, spring)

        world.config.timestep = 0.001
        world.config.duration = 10.0

        sim = Simulation(world, integrator=RK4Integrator())
        sim.run()

        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("mass")

        # Should oscillate: x should cross zero multiple times
        x_positions = traj.x_positions()
        sign_changes = sum(
            1 for i in range(1, len(x_positions))
            if x_positions[i] * x_positions[i - 1] < 0
        )
        assert sign_changes >= 10  # At least 5 full oscillations

    def test_multi_entity(self):
        """Multiple particles in the same world."""
        world = World(gravity=9.81)
        for i in range(5):
            p = Particle(
                mass=float(i + 1),
                position=(float(i), 10 + i * 5),
                name=f"ball_{i}",
            )
            world.add(p)
        world.add_force(UniformGravity())
        world.config.timestep = 0.01
        world.config.duration = 1.0

        sim = Simulation(world, integrator=RK4Integrator())
        sim.run()

        assert sim.world.entity_count == 5

        recorder = StateRecorder(sim.history)
        for i in range(5):
            traj = recorder.get_trajectory(f"ball_{i}")
            assert traj.num_points > 50
            # All balls should fall (y decreases)
            assert traj.positions[-1].y < traj.positions[0].y


class TestSaveLoad:
    def test_round_trip(self, tmp_path):
        """Save a world and load it back."""
        world = World(gravity=9.81)
        ball = Particle(mass=2.5, position=(3, 7), velocity=(1, -2), name="ball")
        world.add(ball)

        file_path = tmp_path / "test_world.json"
        save_world(world, file_path)

        loaded = load_world(file_path)

        assert loaded.entity_count == 1
        entity = loaded.get_entity("ball")
        assert abs(entity.rigid_body.mass - 2.5) < 1e-10
        assert entity.position.close_to(Vector2(3, 7))
        assert entity.velocity.close_to(Vector2(1, -2))


class TestTrajectoryExport:
    def test_csv_export(self, tmp_path):
        """Export a trajectory to CSV."""
        world = World(gravity=9.81)
        ball = Particle(mass=1.0, position=(0, 10), name="ball")
        world.add(ball)
        world.add_force(UniformGravity())
        world.config.timestep = 0.01
        world.config.duration = 1.0

        sim = Simulation(world, integrator=RK4Integrator())
        sim.run()

        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("ball")

        csv_path = tmp_path / "trajectory.csv"
        traj.to_csv(csv_path)

        assert csv_path.exists()
        lines = csv_path.read_text().strip().split("\n")
        assert len(lines) > 50  # header + data rows

    def test_json_export(self, tmp_path):
        """Export a trajectory to JSON."""
        world = World(gravity=9.81)
        ball = Particle(mass=1.0, position=(0, 10), name="ball")
        world.add(ball)
        world.add_force(UniformGravity())
        world.config.timestep = 0.01
        world.config.duration = 1.0

        sim = Simulation(world, integrator=RK4Integrator())
        sim.run()

        recorder = StateRecorder(sim.history)
        traj = recorder.get_trajectory("ball")

        json_path = tmp_path / "trajectory.json"
        traj.to_json(json_path)

        assert json_path.exists()
        data = json.loads(json_path.read_text())
        assert data["entity_name"] == "ball"
        assert len(data["data"]) > 50


class TestSimulationControl:
    def test_reset(self):
        """Resetting should restore initial state."""
        world = World(gravity=9.81)
        ball = Particle(mass=1.0, position=(0, 100), name="ball")
        world.add(ball)
        world.add_force(UniformGravity())
        world.config.timestep = 0.01

        sim = Simulation(world)
        sim.run(duration=1.0)

        # Ball has fallen
        assert ball.position.y < 100

        # Reset
        sim.reset()

        # Ball should be back at original position
        assert ball.position.close_to(Vector2(0, 100))
        assert sim.clock.time == 0.0
        assert sim.status == SimulationStatus.IDLE
