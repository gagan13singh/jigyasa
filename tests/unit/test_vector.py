"""Unit tests for Vector2 and Vector3."""

import math

import pytest

from physengine.math.vector import EPSILON, Vector2, Vector3


class TestVector2Creation:
    def test_default(self):
        v = Vector2()
        assert v.x == 0.0
        assert v.y == 0.0

    def test_with_values(self):
        v = Vector2(3.0, 4.0)
        assert v.x == 3.0
        assert v.y == 4.0

    def test_zero(self):
        v = Vector2.zero()
        assert v.x == 0.0 and v.y == 0.0

    def test_unit_x(self):
        v = Vector2.unit_x()
        assert v.x == 1.0 and v.y == 0.0

    def test_unit_y(self):
        v = Vector2.unit_y()
        assert v.x == 0.0 and v.y == 1.0

    def test_from_angle(self):
        v = Vector2.from_angle(math.pi / 2, 2.0)
        assert abs(v.x) < 1e-10
        assert abs(v.y - 2.0) < 1e-10

    def test_from_array(self):
        import numpy as np
        v = Vector2.from_array(np.array([3.0, 4.0]))
        assert v.x == 3.0 and v.y == 4.0

    def test_immutable(self):
        v = Vector2(1, 2)
        with pytest.raises(AttributeError):
            v.x = 5


class TestVector2Properties:
    def test_magnitude(self):
        v = Vector2(3, 4)
        assert abs(v.magnitude - 5.0) < EPSILON

    def test_magnitude_squared(self):
        v = Vector2(3, 4)
        assert abs(v.magnitude_squared - 25.0) < EPSILON

    def test_angle(self):
        v = Vector2(1, 0)
        assert abs(v.angle) < EPSILON
        v2 = Vector2(0, 1)
        assert abs(v2.angle - math.pi / 2) < EPSILON

    def test_is_zero(self):
        assert Vector2.zero().is_zero
        assert not Vector2(1, 0).is_zero


class TestVector2Operations:
    def test_normalize(self):
        v = Vector2(3, 4).normalize()
        assert abs(v.magnitude - 1.0) < EPSILON

    def test_normalize_zero(self):
        v = Vector2.zero().normalize()
        assert v.is_zero

    def test_dot(self):
        a = Vector2(1, 2)
        b = Vector2(3, 4)
        assert abs(a.dot(b) - 11.0) < EPSILON

    def test_cross(self):
        a = Vector2(1, 0)
        b = Vector2(0, 1)
        assert abs(a.cross(b) - 1.0) < EPSILON

    def test_distance(self):
        a = Vector2(0, 0)
        b = Vector2(3, 4)
        assert abs(a.distance_to(b) - 5.0) < EPSILON

    def test_angle_between(self):
        a = Vector2(1, 0)
        b = Vector2(0, 1)
        assert abs(a.angle_between(b) - math.pi / 2) < 1e-10

    def test_project_onto(self):
        a = Vector2(3, 4)
        b = Vector2(1, 0)
        proj = a.project_onto(b)
        assert abs(proj.x - 3.0) < EPSILON
        assert abs(proj.y) < EPSILON

    def test_reflect(self):
        v = Vector2(1, -1)
        normal = Vector2(0, 1)
        reflected = v.reflect(normal)
        assert abs(reflected.x - 1.0) < EPSILON
        assert abs(reflected.y - 1.0) < EPSILON

    def test_rotate(self):
        v = Vector2(1, 0)
        rotated = v.rotate(math.pi / 2)
        assert abs(rotated.x) < 1e-10
        assert abs(rotated.y - 1.0) < 1e-10

    def test_perpendicular(self):
        v = Vector2(1, 0)
        p = v.perpendicular()
        assert abs(v.dot(p)) < EPSILON

    def test_lerp(self):
        a = Vector2(0, 0)
        b = Vector2(10, 10)
        mid = a.lerp(b, 0.5)
        assert abs(mid.x - 5.0) < EPSILON
        assert abs(mid.y - 5.0) < EPSILON


class TestVector2Arithmetic:
    def test_add(self):
        assert Vector2(1, 2) + Vector2(3, 4) == Vector2(4, 6)

    def test_sub(self):
        assert Vector2(3, 4) - Vector2(1, 2) == Vector2(2, 2)

    def test_mul_scalar(self):
        assert Vector2(1, 2) * 3 == Vector2(3, 6)

    def test_rmul_scalar(self):
        assert 3 * Vector2(1, 2) == Vector2(3, 6)

    def test_div_scalar(self):
        assert Vector2(6, 4) / 2 == Vector2(3, 2)

    def test_div_zero(self):
        with pytest.raises(ZeroDivisionError):
            Vector2(1, 2) / 0

    def test_neg(self):
        assert -Vector2(1, -2) == Vector2(-1, 2)

    def test_abs(self):
        assert abs(abs(Vector2(3, 4)) - 5.0) < EPSILON


class TestVector2Comparison:
    def test_eq(self):
        assert Vector2(1.0, 2.0) == Vector2(1.0, 2.0)

    def test_ne(self):
        assert Vector2(1, 2) != Vector2(1, 3)

    def test_close_to(self):
        a = Vector2(1.0, 2.0)
        b = Vector2(1.0000001, 2.0000001)
        assert a.close_to(b, tolerance=1e-5)

    def test_hash(self):
        a = Vector2(1.0, 2.0)
        b = Vector2(1.0, 2.0)
        assert hash(a) == hash(b)


class TestVector2Iteration:
    def test_iter(self):
        v = Vector2(3, 4)
        assert list(v) == [3.0, 4.0]

    def test_len(self):
        assert len(Vector2(1, 2)) == 2

    def test_getitem(self):
        v = Vector2(3, 4)
        assert v[0] == 3.0
        assert v[1] == 4.0

    def test_getitem_out_of_range(self):
        with pytest.raises(IndexError):
            Vector2(1, 2)[2]


class TestVector2Conversion:
    def test_to_array(self):
        v = Vector2(3, 4)
        arr = v.to_array()
        assert arr[0] == 3.0 and arr[1] == 4.0

    def test_to_tuple(self):
        v = Vector2(3, 4)
        assert v.to_tuple() == (3.0, 4.0)

    def test_to_vector3(self):
        v = Vector2(3, 4)
        v3 = v.to_vector3(z=5.0)
        assert isinstance(v3, Vector3)
        assert v3.x == 3.0 and v3.y == 4.0 and v3.z == 5.0


class TestVector3:
    def test_creation(self):
        v = Vector3(1, 2, 3)
        assert v.x == 1.0 and v.y == 2.0 and v.z == 3.0

    def test_magnitude(self):
        v = Vector3(1, 2, 2)
        assert abs(v.magnitude - 3.0) < EPSILON

    def test_normalize(self):
        v = Vector3(0, 0, 5).normalize()
        assert abs(v.magnitude - 1.0) < EPSILON

    def test_dot(self):
        a = Vector3(1, 2, 3)
        b = Vector3(4, 5, 6)
        assert abs(a.dot(b) - 32.0) < EPSILON

    def test_cross(self):
        i = Vector3.unit_x()
        j = Vector3.unit_y()
        k = i.cross(j)
        assert k == Vector3.unit_z()

    def test_add(self):
        assert Vector3(1, 2, 3) + Vector3(4, 5, 6) == Vector3(5, 7, 9)

    def test_sub(self):
        assert Vector3(4, 5, 6) - Vector3(1, 2, 3) == Vector3(3, 3, 3)

    def test_mul(self):
        assert Vector3(1, 2, 3) * 2 == Vector3(2, 4, 6)

    def test_immutable(self):
        v = Vector3(1, 2, 3)
        with pytest.raises(AttributeError):
            v.x = 5

    def test_to_vector2(self):
        v = Vector3(1, 2, 3).to_vector2()
        assert isinstance(v, Vector2)
        assert v.x == 1.0 and v.y == 2.0
