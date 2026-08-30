"""
physengine.math.constants
=========================

Physical and mathematical constants used throughout the engine.

All physical constants are in **SI units**.

Sources:
    - CODATA 2018 recommended values (NIST)
    - IAU 2015 nominal values where applicable
"""

from __future__ import annotations

import math

# ===========================================================================
#  Mathematical Constants
# ===========================================================================
PI: float = math.pi
"""π ≈ 3.14159265..."""

TAU: float = 2.0 * math.pi
"""τ = 2π ≈ 6.28318530..."""

E: float = math.e
"""Euler's number ≈ 2.71828182..."""

GOLDEN_RATIO: float = (1.0 + math.sqrt(5.0)) / 2.0
"""φ ≈ 1.61803398..."""

DEG_TO_RAD: float = PI / 180.0
"""Multiply degrees by this to get radians."""

RAD_TO_DEG: float = 180.0 / PI
"""Multiply radians by this to get degrees."""


# ===========================================================================
#  Fundamental Physical Constants (SI)
# ===========================================================================
SPEED_OF_LIGHT: float = 299_792_458.0
"""Speed of light in vacuum, c (m/s). Exact."""

GRAVITATIONAL_CONSTANT: float = 6.674_30e-11
"""Newtonian gravitational constant, G (m³ kg⁻¹ s⁻²)."""

PLANCK_CONSTANT: float = 6.626_070_15e-34
"""Planck constant, h (J·s). Exact since 2019 SI redefinition."""

REDUCED_PLANCK: float = PLANCK_CONSTANT / (2.0 * PI)
"""Reduced Planck constant, ℏ = h / 2π (J·s)."""

BOLTZMANN_CONSTANT: float = 1.380_649e-23
"""Boltzmann constant, k_B (J/K). Exact since 2019 SI redefinition."""

ELEMENTARY_CHARGE: float = 1.602_176_634e-19
"""Elementary charge, e (C). Exact since 2019 SI redefinition."""

AVOGADRO_NUMBER: float = 6.022_140_76e23
"""Avogadro constant, N_A (mol⁻¹). Exact since 2019 SI redefinition."""

GAS_CONSTANT: float = BOLTZMANN_CONSTANT * AVOGADRO_NUMBER
"""Molar gas constant, R = k_B × N_A (J mol⁻¹ K⁻¹)."""

STEFAN_BOLTZMANN: float = 5.670_374_419e-8
"""Stefan–Boltzmann constant, σ (W m⁻² K⁻⁴)."""


# ===========================================================================
#  Electromagnetic Constants (SI)
# ===========================================================================
VACUUM_PERMITTIVITY: float = 8.854_187_8128e-12
"""Vacuum permittivity, ε₀ (F/m)."""

VACUUM_PERMEABILITY: float = 1.256_637_062_12e-6
"""Vacuum permeability, μ₀ (H/m)."""

COULOMB_CONSTANT: float = 1.0 / (4.0 * PI * VACUUM_PERMITTIVITY)
"""Coulomb constant, k_e = 1/(4πε₀) (N m² C⁻²)."""


# ===========================================================================
#  Earth / Gravitational Defaults
# ===========================================================================
STANDARD_GRAVITY: float = 9.806_65
"""Standard acceleration of gravity, g₀ (m/s²). Exact by definition."""

EARTH_MASS: float = 5.972_37e24
"""Mass of Earth (kg)."""

EARTH_RADIUS: float = 6.371_0e6
"""Mean radius of Earth (m)."""

MOON_MASS: float = 7.342e22
"""Mass of the Moon (kg)."""

SUN_MASS: float = 1.989_1e30
"""Mass of the Sun (kg)."""


# ===========================================================================
#  Atomic / Particle Constants
# ===========================================================================
ELECTRON_MASS: float = 9.109_383_7015e-31
"""Electron rest mass (kg)."""

PROTON_MASS: float = 1.672_621_923_69e-27
"""Proton rest mass (kg)."""

NEUTRON_MASS: float = 1.674_927_498_04e-27
"""Neutron rest mass (kg)."""


# ===========================================================================
#  Common Defaults (for simulation convenience)
# ===========================================================================
DEFAULT_GRAVITY_2D: tuple[float, float] = (0.0, -STANDARD_GRAVITY)
"""Default gravity vector for 2D simulations (pointing downward)."""

DEFAULT_GRAVITY_3D: tuple[float, float, float] = (0.0, -STANDARD_GRAVITY, 0.0)
"""Default gravity vector for 3D simulations (pointing downward along y)."""

DEFAULT_TIMESTEP: float = 1.0 / 60.0
"""Default simulation timestep ≈ 16.67ms (60 FPS equivalent)."""

DEFAULT_SUBSTEPS: int = 10
"""Default number of substeps per frame for accuracy."""

AIR_DENSITY_STP: float = 1.225
"""Air density at sea level and 15°C (kg/m³)."""

WATER_DENSITY: float = 997.0
"""Water density at 25°C (kg/m³)."""
