"""
physengine.units.quantity
=========================

Unit-aware physical quantities with automatic dimensional checking.

A Quantity wraps a numeric value with a Dimension, enabling:
    - Type-safe arithmetic: ``meters + seconds`` raises DimensionalError
    - Auto-conversion: ``speed.to("km/h")``
    - Rich display: ``Quantity(9.81, "m/s²")``

Design:
    - Quantities store values in **SI base units** internally.
    - Conversion happens on input (from user unit) and output (to display unit).
    - The Quantity is immutable.

Usage:
    >>> from physengine.units import Quantity
    >>> v = Quantity(72, "km/h")
    >>> v.to("m/s")     # Quantity(20.0, m/s)
    >>> v + Quantity(5, "m/s")  # works: same dimension
    >>> v + Quantity(5, "kg")   # raises DimensionalError
"""

from __future__ import annotations

from dataclasses import dataclass

from physengine.units.dimensions import (
    DIMENSIONLESS,
    Dimension,
    UnitRegistry,
)


class DimensionalError(TypeError):
    """Raised when an operation combines incompatible dimensions.

    Example:
        ``Quantity(5, "m") + Quantity(3, "s")`` → DimensionalError
    """

    pass


@dataclass(frozen=True, slots=True)
class Quantity:
    """A physical quantity: a numeric value with a physical dimension.

    Internally, the value is always stored in SI base units.

    Attributes:
        value: The numeric value in SI base units.
        dimension: The physical dimension of this quantity.
        _display_symbol: The symbol of the unit used at creation time
                         (for display purposes).
    """

    value: float
    dimension: Dimension
    _display_symbol: str = ""

    # -- Construction --------------------------------------------------------
    def __init__(
        self,
        value: float,
        unit: str | Dimension = "",
    ) -> None:
        """Create a Quantity.

        Args:
            value: Numeric value.
            unit: Either a unit symbol string (e.g. "m/s") which will be
                  looked up in the registry, or a Dimension object directly.
                  If empty string, quantity is dimensionless.

        Raises:
            KeyError: If the unit symbol is not recognized.
        """
        if isinstance(unit, Dimension):
            object.__setattr__(self, "value", float(value))
            object.__setattr__(self, "dimension", unit)
            object.__setattr__(self, "_display_symbol", "")
        elif unit == "":
            object.__setattr__(self, "value", float(value))
            object.__setattr__(self, "dimension", DIMENSIONLESS)
            object.__setattr__(self, "_display_symbol", "")
        else:
            registry = UnitRegistry()
            unit_def = registry.get(unit)
            # Convert to SI
            si_value = value * unit_def.to_si + unit_def.offset
            object.__setattr__(self, "value", si_value)
            object.__setattr__(self, "dimension", unit_def.dimension)
            object.__setattr__(self, "_display_symbol", unit)

    # -- Conversion ----------------------------------------------------------
    def to(self, unit_symbol: str) -> Quantity:
        """Convert this quantity to a different unit.

        Args:
            unit_symbol: Target unit symbol (e.g. "km/h").

        Returns:
            A new Quantity with the converted value and updated display symbol.

        Raises:
            DimensionalError: If the target unit has a different dimension.
            KeyError: If the unit symbol is not recognized.
        """
        registry = UnitRegistry()
        target = registry.get(unit_symbol)

        if not self.dimension.is_compatible(target.dimension):
            raise DimensionalError(
                f"Cannot convert {self.dimension} to unit '{unit_symbol}' "
                f"with dimension {target.dimension}"
            )

        result = Quantity.__new__(Quantity)
        object.__setattr__(result, "value", self.value)
        object.__setattr__(result, "dimension", self.dimension)
        object.__setattr__(result, "_display_symbol", unit_symbol)
        return result

    @property
    def si_value(self) -> float:
        """Value in SI base units."""
        return self.value

    @property
    def display_value(self) -> float:
        """Value in the display unit (the unit used at construction or conversion)."""
        if not self._display_symbol:
            return self.value
        registry = UnitRegistry()
        unit_def = registry.get(self._display_symbol)
        return (self.value - unit_def.offset) / unit_def.to_si

    # -- Arithmetic ----------------------------------------------------------
    def _check_compatible(self, other: Quantity, op: str) -> None:
        if not self.dimension.is_compatible(other.dimension):
            raise DimensionalError(
                f"Cannot {op} quantities with dimensions "
                f"{self.dimension} and {other.dimension}"
            )

    def __add__(self, other: object) -> Quantity:
        if isinstance(other, Quantity):
            self._check_compatible(other, "add")
            return Quantity(self.value + other.value, self.dimension)
        if isinstance(other, (int, float)):
            if not self.dimension.is_dimensionless:
                raise DimensionalError(
                    f"Cannot add dimensionless scalar to {self.dimension}"
                )
            return Quantity(self.value + other, self.dimension)
        return NotImplemented

    def __radd__(self, other: object) -> Quantity:
        return self.__add__(other)

    def __sub__(self, other: object) -> Quantity:
        if isinstance(other, Quantity):
            self._check_compatible(other, "subtract")
            return Quantity(self.value - other.value, self.dimension)
        if isinstance(other, (int, float)):
            if not self.dimension.is_dimensionless:
                raise DimensionalError(
                    f"Cannot subtract dimensionless scalar from {self.dimension}"
                )
            return Quantity(self.value - other, self.dimension)
        return NotImplemented

    def __rsub__(self, other: object) -> Quantity:
        if isinstance(other, (int, float)):
            if not self.dimension.is_dimensionless:
                raise DimensionalError(
                    f"Cannot subtract {self.dimension} from dimensionless scalar"
                )
            return Quantity(other - self.value, self.dimension)
        return NotImplemented

    def __mul__(self, other: object) -> Quantity:
        if isinstance(other, Quantity):
            new_dim = self.dimension * other.dimension
            return Quantity(self.value * other.value, new_dim)
        if isinstance(other, (int, float)):
            return Quantity(self.value * other, self.dimension)
        return NotImplemented

    def __rmul__(self, other: object) -> Quantity:
        return self.__mul__(other)

    def __truediv__(self, other: object) -> Quantity:
        if isinstance(other, Quantity):
            if abs(other.value) < 1e-30:
                raise ZeroDivisionError("Division by zero quantity")
            new_dim = self.dimension / other.dimension
            return Quantity(self.value / other.value, new_dim)
        if isinstance(other, (int, float)):
            if abs(other) < 1e-30:
                raise ZeroDivisionError("Division by zero")
            return Quantity(self.value / other, self.dimension)
        return NotImplemented

    def __rtruediv__(self, other: object) -> Quantity:
        if isinstance(other, (int, float)):
            if abs(self.value) < 1e-30:
                raise ZeroDivisionError("Division by zero quantity")
            inv_dim = self.dimension ** -1
            return Quantity(other / self.value, inv_dim)
        return NotImplemented

    def __pow__(self, exponent: int) -> Quantity:
        new_dim = self.dimension ** exponent
        return Quantity(self.value ** exponent, new_dim)

    def __neg__(self) -> Quantity:
        return Quantity(-self.value, self.dimension)

    def __pos__(self) -> Quantity:
        return Quantity(self.value, self.dimension)

    def __abs__(self) -> Quantity:
        return Quantity(abs(self.value), self.dimension)

    # -- Comparison ----------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Quantity):
            if not self.dimension.is_compatible(other.dimension):
                return False
            return abs(self.value - other.value) < 1e-10
        return NotImplemented

    def __lt__(self, other: Quantity) -> bool:
        self._check_compatible(other, "compare")
        return self.value < other.value

    def __le__(self, other: Quantity) -> bool:
        self._check_compatible(other, "compare")
        return self.value <= other.value

    def __gt__(self, other: Quantity) -> bool:
        self._check_compatible(other, "compare")
        return self.value > other.value

    def __ge__(self, other: Quantity) -> bool:
        self._check_compatible(other, "compare")
        return self.value >= other.value

    # -- Display -------------------------------------------------------------
    def __repr__(self) -> str:
        if self._display_symbol:
            dv = self.display_value
            return f"Quantity({dv:.6g}, {self._display_symbol!r})"
        return f"Quantity({self.value:.6g}, {self.dimension})"

    def __str__(self) -> str:
        if self._display_symbol:
            return f"{self.display_value:.4g} {self._display_symbol}"
        if self.dimension.is_dimensionless:
            return f"{self.value:.4g}"
        return f"{self.value:.4g} [{self.dimension}]"

    def __float__(self) -> float:
        """Extract raw SI value for use in calculations."""
        return self.value

    def __hash__(self) -> int:
        return hash((round(self.value, 8), self.dimension))


# ===========================================================================
#  Convenience constructors
# ===========================================================================
def meters(value: float) -> Quantity:
    """Create a length quantity in meters."""
    return Quantity(value, "m")


def kilograms(value: float) -> Quantity:
    """Create a mass quantity in kilograms."""
    return Quantity(value, "kg")


def seconds(value: float) -> Quantity:
    """Create a time quantity in seconds."""
    return Quantity(value, "s")


def newtons(value: float) -> Quantity:
    """Create a force quantity in newtons."""
    return Quantity(value, "N")


def joules(value: float) -> Quantity:
    """Create an energy quantity in joules."""
    return Quantity(value, "J")


def meters_per_second(value: float) -> Quantity:
    """Create a velocity quantity in m/s."""
    return Quantity(value, "m/s")
