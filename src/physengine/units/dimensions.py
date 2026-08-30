"""
physengine.units.dimensions
===========================

SI dimensional analysis framework.

Every physical quantity has a **dimension** expressed as a 7-tuple of exponents
over the SI base dimensions:

    (Length, Mass, Time, Current, Temperature, Amount, Luminosity)

For example:
    - Velocity    = (1, 0, -1, 0, 0, 0, 0)   →  m/s
    - Force       = (1, 1, -2, 0, 0, 0, 0)   →  kg⋅m/s²
    - Energy      = (2, 1, -2, 0, 0, 0, 0)   →  kg⋅m²/s²

This module defines the Dimension type, common derived dimensions,
and a registry of units with their conversion factors to SI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


# ===========================================================================
#  Dimension (7-tuple of SI exponents)
# ===========================================================================
@dataclass(frozen=True, slots=True)
class Dimension:
    """Represents a physical dimension as SI base-unit exponents.

    Each attribute is the exponent for that base dimension.
    A dimensionless quantity has all exponents equal to zero.
    """

    length: int = 0
    mass: int = 0
    time: int = 0
    current: int = 0
    temperature: int = 0
    amount: int = 0
    luminosity: int = 0

    # -- Arithmetic on dimensions (for combining quantities) -----------------
    def __mul__(self, other: object) -> Dimension:
        """Multiply dimensions (add exponents)."""
        if isinstance(other, Dimension):
            return Dimension(
                self.length + other.length,
                self.mass + other.mass,
                self.time + other.time,
                self.current + other.current,
                self.temperature + other.temperature,
                self.amount + other.amount,
                self.luminosity + other.luminosity,
            )
        return NotImplemented

    def __truediv__(self, other: object) -> Dimension:
        """Divide dimensions (subtract exponents)."""
        if isinstance(other, Dimension):
            return Dimension(
                self.length - other.length,
                self.mass - other.mass,
                self.time - other.time,
                self.current - other.current,
                self.temperature - other.temperature,
                self.amount - other.amount,
                self.luminosity - other.luminosity,
            )
        return NotImplemented

    def __pow__(self, exponent: int) -> Dimension:
        """Raise dimension to an integer power."""
        return Dimension(
            self.length * exponent,
            self.mass * exponent,
            self.time * exponent,
            self.current * exponent,
            self.temperature * exponent,
            self.amount * exponent,
            self.luminosity * exponent,
        )

    def __invert__(self) -> Dimension:
        """Inverse dimension (negate exponents)."""
        return self ** -1

    @property
    def is_dimensionless(self) -> bool:
        """True if all exponents are zero."""
        return (
            self.length == 0
            and self.mass == 0
            and self.time == 0
            and self.current == 0
            and self.temperature == 0
            and self.amount == 0
            and self.luminosity == 0
        )

    def is_compatible(self, other: Dimension) -> bool:
        """True if both dimensions are the same."""
        return self == other

    def to_tuple(self) -> tuple[int, ...]:
        return (
            self.length,
            self.mass,
            self.time,
            self.current,
            self.temperature,
            self.amount,
            self.luminosity,
        )

    def __repr__(self) -> str:
        parts: list[str] = []
        names = ["L", "M", "T", "I", "Θ", "N", "J"]
        for name, exp in zip(names, self.to_tuple(), strict=True):
            if exp != 0:
                if exp == 1:
                    parts.append(name)
                else:
                    parts.append(f"{name}^{exp}")
        return f"Dim({' '.join(parts) if parts else '1'})"


# ===========================================================================
#  Standard Dimensions
# ===========================================================================

# Base dimensions
DIMENSIONLESS = Dimension()
LENGTH = Dimension(length=1)
MASS = Dimension(mass=1)
TIME = Dimension(time=1)
CURRENT = Dimension(current=1)
TEMPERATURE = Dimension(temperature=1)
AMOUNT = Dimension(amount=1)
LUMINOSITY = Dimension(luminosity=1)

# Derived dimensions — Mechanics
AREA = LENGTH ** 2
VOLUME = LENGTH ** 3
VELOCITY = LENGTH / TIME
ACCELERATION = VELOCITY / TIME
MOMENTUM = MASS * VELOCITY
FORCE = MASS * ACCELERATION
ENERGY = FORCE * LENGTH
POWER = ENERGY / TIME
PRESSURE = FORCE / AREA
DENSITY = MASS / VOLUME
FREQUENCY = ~TIME  # T⁻¹

# Derived dimensions — Rotational
ANGULAR_VELOCITY = ~TIME  # rad/s (dimensionless angle)
ANGULAR_ACCELERATION = ANGULAR_VELOCITY / TIME
TORQUE = FORCE * LENGTH
MOMENT_OF_INERTIA = MASS * AREA
ANGULAR_MOMENTUM = MOMENT_OF_INERTIA * ANGULAR_VELOCITY

# Derived dimensions — Electromagnetic
CHARGE = CURRENT * TIME
VOLTAGE = ENERGY / CHARGE
RESISTANCE = VOLTAGE / CURRENT
CAPACITANCE = CHARGE / VOLTAGE
MAGNETIC_FLUX = VOLTAGE * TIME
MAGNETIC_FIELD = MAGNETIC_FLUX / AREA

# Derived dimensions — Thermodynamics
SPECIFIC_HEAT = ENERGY / (MASS * TEMPERATURE)
ENTROPY = ENERGY / TEMPERATURE


# ===========================================================================
#  Unit Definition
# ===========================================================================
@dataclass(frozen=True, slots=True)
class UnitDef:
    """Definition of a named unit.

    Attributes:
        name: Human-readable name (e.g. "meter").
        symbol: Short symbol (e.g. "m").
        dimension: The physical dimension this unit measures.
        to_si: Multiply by this factor to convert to SI base unit.
        offset: Additive offset for temperature-like conversions (default 0).
    """

    name: str
    symbol: str
    dimension: Dimension
    to_si: float
    offset: float = 0.0


# ===========================================================================
#  Unit Registry
# ===========================================================================
class UnitRegistry:
    """Singleton registry of all known units.

    Units are looked up by symbol string (e.g. "m", "km/h", "N").
    """

    _instance: ClassVar[UnitRegistry | None] = None
    _units: dict[str, UnitDef]

    def __new__(cls) -> UnitRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._units = {}
            cls._instance._register_defaults()
        return cls._instance

    def register(self, unit: UnitDef) -> None:
        """Register a unit definition."""
        self._units[unit.symbol] = unit

    def get(self, symbol: str) -> UnitDef:
        """Look up a unit by symbol.

        Raises:
            KeyError: If the symbol is not registered.
        """
        if symbol not in self._units:
            raise KeyError(f"Unknown unit symbol: '{symbol}'")
        return self._units[symbol]

    def has(self, symbol: str) -> bool:
        """Check if a symbol is registered."""
        return symbol in self._units

    def all_symbols(self) -> list[str]:
        """Return all registered symbols."""
        return list(self._units.keys())

    def _register_defaults(self) -> None:
        """Register standard SI and common derived units."""
        defs = [
            # Length
            UnitDef("meter", "m", LENGTH, 1.0),
            UnitDef("kilometer", "km", LENGTH, 1000.0),
            UnitDef("centimeter", "cm", LENGTH, 0.01),
            UnitDef("millimeter", "mm", LENGTH, 0.001),
            UnitDef("micrometer", "μm", LENGTH, 1e-6),
            UnitDef("nanometer", "nm", LENGTH, 1e-9),
            UnitDef("inch", "in", LENGTH, 0.0254),
            UnitDef("foot", "ft", LENGTH, 0.3048),
            UnitDef("mile", "mi", LENGTH, 1609.344),
            UnitDef("astronomical unit", "AU", LENGTH, 1.495_978_707e11),
            UnitDef("light-year", "ly", LENGTH, 9.460_730_472_58e15),
            # Mass
            UnitDef("kilogram", "kg", MASS, 1.0),
            UnitDef("gram", "g", MASS, 0.001),
            UnitDef("milligram", "mg", MASS, 1e-6),
            UnitDef("tonne", "t", MASS, 1000.0),
            UnitDef("pound", "lb", MASS, 0.453_592_37),
            UnitDef("ounce", "oz", MASS, 0.028_349_523_125),
            UnitDef("atomic mass unit", "u", MASS, 1.660_539_066_60e-27),
            # Time
            UnitDef("second", "s", TIME, 1.0),
            UnitDef("millisecond", "ms", TIME, 0.001),
            UnitDef("microsecond", "μs", TIME, 1e-6),
            UnitDef("nanosecond", "ns", TIME, 1e-9),
            UnitDef("minute", "min", TIME, 60.0),
            UnitDef("hour", "h", TIME, 3600.0),
            UnitDef("day", "d", TIME, 86400.0),
            UnitDef("year", "yr", TIME, 365.25 * 86400.0),
            # Velocity
            UnitDef("meters per second", "m/s", VELOCITY, 1.0),
            UnitDef("kilometers per hour", "km/h", VELOCITY, 1.0 / 3.6),
            UnitDef("miles per hour", "mph", VELOCITY, 0.447_04),
            UnitDef("feet per second", "ft/s", VELOCITY, 0.3048),
            UnitDef("knot", "kn", VELOCITY, 0.514_444),
            # Acceleration
            UnitDef("meters per second squared", "m/s²", ACCELERATION, 1.0),
            UnitDef("standard gravity", "g₀", ACCELERATION, 9.806_65),
            # Force
            UnitDef("newton", "N", FORCE, 1.0),
            UnitDef("kilonewton", "kN", FORCE, 1000.0),
            UnitDef("dyne", "dyn", FORCE, 1e-5),
            UnitDef("pound-force", "lbf", FORCE, 4.448_222),
            # Energy
            UnitDef("joule", "J", ENERGY, 1.0),
            UnitDef("kilojoule", "kJ", ENERGY, 1000.0),
            UnitDef("megajoule", "MJ", ENERGY, 1e6),
            UnitDef("calorie", "cal", ENERGY, 4.184),
            UnitDef("kilocalorie", "kcal", ENERGY, 4184.0),
            UnitDef("electronvolt", "eV", ENERGY, 1.602_176_634e-19),
            UnitDef("kilowatt-hour", "kWh", ENERGY, 3.6e6),
            UnitDef("erg", "erg", ENERGY, 1e-7),
            # Power
            UnitDef("watt", "W", POWER, 1.0),
            UnitDef("kilowatt", "kW", POWER, 1000.0),
            UnitDef("horsepower", "hp", POWER, 745.699_872),
            # Pressure
            UnitDef("pascal", "Pa", PRESSURE, 1.0),
            UnitDef("kilopascal", "kPa", PRESSURE, 1000.0),
            UnitDef("megapascal", "MPa", PRESSURE, 1e6),
            UnitDef("atmosphere", "atm", PRESSURE, 101_325.0),
            UnitDef("bar", "bar", PRESSURE, 1e5),
            # Frequency
            UnitDef("hertz", "Hz", FREQUENCY, 1.0),
            UnitDef("kilohertz", "kHz", FREQUENCY, 1000.0),
            UnitDef("megahertz", "MHz", FREQUENCY, 1e6),
            # Charge
            UnitDef("coulomb", "C", CHARGE, 1.0),
            # Voltage
            UnitDef("volt", "V", VOLTAGE, 1.0),
            # Current
            UnitDef("ampere", "A", CURRENT, 1.0),
            # Angle (dimensionless)
            UnitDef("radian", "rad", DIMENSIONLESS, 1.0),
            UnitDef("degree", "deg", DIMENSIONLESS, 0.017_453_292_519_943_295),
            # Temperature (with offset)
            UnitDef("kelvin", "K", TEMPERATURE, 1.0),
            UnitDef("celsius", "°C", TEMPERATURE, 1.0, offset=273.15),
        ]

        for unit_def in defs:
            self.register(unit_def)


# Module-level convenience
_registry = UnitRegistry()


def get_unit(symbol: str) -> UnitDef:
    """Look up a unit by symbol from the global registry."""
    return _registry.get(symbol)


def register_unit(unit: UnitDef) -> None:
    """Register a custom unit in the global registry."""
    _registry.register(unit)
