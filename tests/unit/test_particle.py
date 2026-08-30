"""Unit tests for Particle and Entity."""

import pytest

from physengine.core.entity import Entity, RigidBodyComponent, Transform
from physengine.math.vector import Vector2
from physengine.mechanics.particle import Particle, StaticBody


class TestEntity:
    def test_creation(self):
        e = Entity("test")
        assert e.name == "test"
        assert len(e.id) == 12

    def test_add_component(self):
        e = Entity("test")
        e.add_component(Transform())
        assert e.has_component(Transform)

    def test_get_component(self):
        e = Entity("test")
        t = Transform(position=Vector2(1, 2))
        e.add_component(t)
        assert e.get_component(Transform).position == Vector2(1, 2)

    def test_get_missing_component(self):
        e = Entity("test")
        with pytest.raises(KeyError):
            e.get_component(Transform)

    def test_remove_component(self):
        e = Entity("test")
        e.add_component(Transform())
        e.remove_component(Transform)
        assert not e.has_component(Transform)

    def test_chaining(self):
        e = Entity("test").add_component(Transform()).add_component(
            RigidBodyComponent(mass=5.0)
        )
        assert e.has_component(Transform)
        assert e.has_component(RigidBodyComponent)

    def test_tags(self):
        e = Entity("test").add_tag("ball").add_tag("dynamic")
        assert e.has_tag("ball")
        assert e.has_tag("dynamic")
        assert not e.has_tag("wall")


class TestRigidBodyComponent:
    def test_creation(self):
        rb = RigidBodyComponent(mass=5.0)
        assert rb.mass == 5.0
        assert rb.velocity == Vector2.zero()

    def test_inverse_mass(self):
        rb = RigidBodyComponent(mass=2.0)
        assert abs(rb.inverse_mass - 0.5) < 1e-10

    def test_static_inverse_mass(self):
        rb = RigidBodyComponent(mass=1.0, is_static=True)
        assert rb.inverse_mass == 0.0

    def test_invalid_mass(self):
        with pytest.raises(ValueError):
            RigidBodyComponent(mass=-1.0)

    def test_invalid_restitution(self):
        with pytest.raises(ValueError):
            RigidBodyComponent(restitution=1.5)


class TestParticle:
    def test_creation(self):
        p = Particle(mass=2.0, position=(3, 4), velocity=(1, 0), name="ball")
        assert p.mass == 2.0
        assert p.position == Vector2(3, 4)
        assert p.velocity == Vector2(1, 0)
        assert p.name == "ball"

    def test_from_vector2(self):
        p = Particle(position=Vector2(5, 10))
        assert p.position == Vector2(5, 10)

    def test_kinetic_energy(self):
        p = Particle(mass=2.0, velocity=(3, 4))
        # KE = 0.5 * 2 * (3² + 4²) = 0.5 * 2 * 25 = 25
        assert abs(p.kinetic_energy - 25.0) < 1e-10

    def test_momentum(self):
        p = Particle(mass=2.0, velocity=(3, 0))
        assert p.momentum == Vector2(6, 0)

    def test_speed(self):
        p = Particle(velocity=(3, 4))
        assert abs(p.speed - 5.0) < 1e-10

    def test_has_particle_tag(self):
        p = Particle(name="test")
        assert p.has_tag("particle")

    def test_is_entity(self):
        p = Particle()
        assert isinstance(p, Entity)
        assert p.has_component(Transform)
        assert p.has_component(RigidBodyComponent)


class TestStaticBody:
    def test_is_static(self):
        s = StaticBody(position=(0, 0), name="floor")
        assert s.rigid_body.is_static
        assert s.rigid_body.inverse_mass == 0.0
        assert s.has_tag("static")
