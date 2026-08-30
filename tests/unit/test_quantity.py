"""Unit tests for the Quantity and units system."""

import pytest

from physengine.units.dimensions import (
    ACCELERATION,
    FORCE,
    LENGTH,
    MASS,
    TIME,
    VELOCITY,
    Dimension,
)
from physengine.units.quantity import DimensionalError, Quantity


class TestDimension:
    def test_dimensionless(self):
        d = Dimension()
        assert d.is_dimensionless

    def test_length(self):
        assert not LENGTH.is_dimensionless
        assert LENGTH.length == 1

    def test_multiply(self):
        velocity = LENGTH / TIME
        assert velocity == VELOCITY

    def test_force(self):
        force = MASS * ACCELERATION
        assert force == FORCE

    def test_power(self):
        area = LENGTH ** 2
        assert area.length == 2
        assert area.mass == 0

    def test_inverse(self):
        inv_time = ~TIME
        assert inv_time.time == -1


class TestQuantity:
    def test_creation_with_unit(self):
        q = Quantity(5.0, "m")
        assert q.value == 5.0
        assert q.dimension == LENGTH

    def test_creation_km_to_si(self):
        q = Quantity(1.0, "km")
        assert abs(q.value - 1000.0) < 1e-10

    def test_creation_km_h_to_si(self):
        q = Quantity(72.0, "km/h")
        assert abs(q.value - 20.0) < 1e-10

    def test_display_value(self):
        q = Quantity(72.0, "km/h")
        assert abs(q.display_value - 72.0) < 1e-10

    def test_conversion(self):
        q = Quantity(100, "m")
        converted = q.to("km")
        assert abs(converted.display_value - 0.1) < 1e-10

    def test_add_same_dimension(self):
        a = Quantity(5.0, "m")
        b = Quantity(3.0, "m")
        result = a + b
        assert abs(result.value - 8.0) < 1e-10

    def test_add_different_dimension_raises(self):
        a = Quantity(5.0, "m")
        b = Quantity(3.0, "s")
        with pytest.raises(DimensionalError):
            a + b

    def test_subtract(self):
        a = Quantity(10.0, "m")
        b = Quantity(3.0, "m")
        result = a - b
        assert abs(result.value - 7.0) < 1e-10

    def test_multiply(self):
        mass = Quantity(10.0, "kg")
        acc = Quantity(9.81, "m/s²")
        force = mass * acc
        assert force.dimension == FORCE
        assert abs(force.value - 98.1) < 1e-10

    def test_divide(self):
        distance = Quantity(100.0, "m")
        time = Quantity(10.0, "s")
        speed = distance / time
        assert speed.dimension == VELOCITY
        assert abs(speed.value - 10.0) < 1e-10

    def test_comparison(self):
        a = Quantity(5.0, "m")
        b = Quantity(3.0, "m")
        assert a > b
        assert b < a

    def test_comparison_different_dimension(self):
        a = Quantity(5.0, "m")
        b = Quantity(3.0, "s")
        with pytest.raises(DimensionalError):
            _ = a < b

    def test_float_extraction(self):
        q = Quantity(9.81, "m/s²")
        assert abs(float(q) - 9.81) < 1e-10

    def test_negation(self):
        q = Quantity(5.0, "m")
        neg = -q
        assert abs(neg.value - (-5.0)) < 1e-10

    def test_power(self):
        length = Quantity(3.0, "m")
        area = length ** 2
        assert area.dimension.length == 2
        assert abs(area.value - 9.0) < 1e-10
