"""
physengine.units
================

Unit system with dimensional analysis.

Re-exports:
    Quantity, DimensionalError — unit-aware quantities
    Dimension — SI dimension representation
"""

from physengine.units.dimensions import Dimension, UnitDef, get_unit, register_unit
from physengine.units.quantity import (
    DimensionalError,
    Quantity,
    joules,
    kilograms,
    meters,
    meters_per_second,
    newtons,
    seconds,
)

__all__ = [
    "Dimension",
    "DimensionalError",
    "Quantity",
    "UnitDef",
    "get_unit",
    "joules",
    "kilograms",
    "meters",
    "meters_per_second",
    "newtons",
    "register_unit",
    "seconds",
]
