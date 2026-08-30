"""Unit tests for Force implementations."""



from physengine.core.world import World
from physengine.math.vector import Vector2
from physengine.mechanics.forces import (
    CompositeForce,
    ConstantForce,
    Drag,
    Spring,
    UniformGravity,
)
from physengine.mechanics.particle import Particle


class TestUniformGravity:
    def test_default_uses_world_gravity(self):
        world = World(gravity=9.81)
        ball = Particle(mass=2.0, name="ball")
        world.add(ball)

        force = UniformGravity()
        f = force.calculate(ball, world, 0.01)
        # F = m * g = 2 * -9.81 = -19.62 (downward)
        assert abs(f.x) < 1e-10
        assert abs(f.y - (-2.0 * 9.81)) < 1e-10

    def test_custom_gravity(self):
        world = World(gravity=9.81)
        ball = Particle(mass=1.0, name="ball")
        world.add(ball)

        force = UniformGravity(g=1.62)  # Moon gravity
        f = force.calculate(ball, world, 0.01)
        assert abs(f.y - (-1.62)) < 1e-10

    def test_with_vector(self):
        world = World()
        ball = Particle(mass=1.0, name="ball")
        world.add(ball)

        force = UniformGravity(g=Vector2(1, -2))
        f = force.calculate(ball, world, 0.01)
        assert abs(f.x - 1.0) < 1e-10
        assert abs(f.y - (-2.0)) < 1e-10


class TestSpring:
    def test_at_rest_length(self):
        world = World()
        anchor = Vector2(0, 0)
        ball = Particle(mass=1.0, position=(5, 0), name="ball")
        world.add(ball)

        spring = Spring(stiffness=100, anchor=anchor, rest_length=5.0)
        f = spring.calculate(ball, world, 0.01)
        # At rest length → zero force
        assert abs(f.magnitude) < 1e-10

    def test_stretched(self):
        world = World()
        anchor = Vector2(0, 0)
        ball = Particle(mass=1.0, position=(10, 0), name="ball")
        world.add(ball)

        spring = Spring(stiffness=100, anchor=anchor, rest_length=5.0)
        f = spring.calculate(ball, world, 0.01)
        # F = -k * (10 - 5) * direction = -100 * 5 * (1,0) = (-500, 0)
        assert abs(f.x - (-500.0)) < 1e-10
        assert abs(f.y) < 1e-10

    def test_compressed(self):
        world = World()
        anchor = Vector2(0, 0)
        ball = Particle(mass=1.0, position=(2, 0), name="ball")
        world.add(ball)

        spring = Spring(stiffness=100, anchor=anchor, rest_length=5.0)
        f = spring.calculate(ball, world, 0.01)
        # F = -k * (2 - 5) * direction = -100 * (-3) * (1,0) = (300, 0)
        assert abs(f.x - 300.0) < 1e-10


class TestDrag:
    def test_zero_velocity_no_drag(self):
        world = World()
        ball = Particle(mass=1.0, velocity=(0, 0), name="ball")
        world.add(ball)

        drag = Drag(drag_coefficient=0.47, cross_section_area=0.01)
        f = drag.calculate(ball, world, 0.01)
        assert f.is_zero

    def test_drag_opposes_motion(self):
        world = World()
        ball = Particle(mass=1.0, velocity=(10, 0), name="ball")
        world.add(ball)

        drag = Drag(drag_coefficient=0.47, cross_section_area=0.01)
        f = drag.calculate(ball, world, 0.01)
        # Force should be in -x direction
        assert f.x < 0
        assert abs(f.y) < 1e-10


class TestConstantForce:
    def test_constant(self):
        world = World()
        ball = Particle(mass=1.0, name="ball")
        world.add(ball)

        force = ConstantForce(Vector2(10, -5))
        f = force.calculate(ball, world, 0.01)
        assert f == Vector2(10, -5)


class TestCompositeForce:
    def test_sum_of_forces(self):
        world = World()
        ball = Particle(mass=1.0, name="ball")
        world.add(ball)

        f1 = ConstantForce(Vector2(10, 0))
        f2 = ConstantForce(Vector2(0, -5))
        composite = CompositeForce(f1, f2)

        f = composite.calculate(ball, world, 0.01)
        assert f == Vector2(10, -5)
