"""Shared test fixtures for physengine tests."""

import pytest

from physengine.core.config import SimulationConfig
from physengine.core.world import World
from physengine.math.vector import Vector2
from physengine.mechanics.forces import UniformGravity
from physengine.mechanics.particle import Particle


@pytest.fixture
def zero_vector():
    return Vector2.zero()


@pytest.fixture
def unit_x():
    return Vector2.unit_x()


@pytest.fixture
def unit_y():
    return Vector2.unit_y()


@pytest.fixture
def simple_world():
    """A simple world with standard gravity."""
    return World(gravity=9.81)


@pytest.fixture
def freefall_world():
    """World with a single particle in freefall."""
    world = World(gravity=9.81)
    ball = Particle(mass=1.0, position=(0, 10), name="ball")
    world.add(ball)
    world.add_force(UniformGravity())
    return world


@pytest.fixture
def projectile_world():
    """World with a projectile launched at 45 degrees."""
    world = World(gravity=9.81)
    import math
    v0 = 20.0
    angle = math.radians(45)
    vx = v0 * math.cos(angle)
    vy = v0 * math.sin(angle)
    ball = Particle(
        mass=1.0,
        position=(0, 0),
        velocity=(vx, vy),
        name="projectile",
    )
    world.add(ball)
    world.add_force(UniformGravity())
    return world


@pytest.fixture
def config_small_dt():
    """Configuration with very small timestep for accuracy."""
    return SimulationConfig(timestep=0.0001, duration=2.0, integrator_name="rk4")
