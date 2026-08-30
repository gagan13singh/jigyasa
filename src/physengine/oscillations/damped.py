"""
physengine.oscillations.damped
==============================

Damped and Forced Harmonic Oscillations for Class 11 & Advanced Physics.

Differential Equation:
    m * x'' + γ * x' + k * x = F₀ * cos(ω_drive * t)

Regimes:
- Underdamped (γ² < 4mk): Decaying oscillations with frequency ω_d = √(ω₀² - β²)
- Critically Damped (γ² = 4mk): Fastest return to equilibrium without oscillating
- Overdamped (γ² > 4mk): Sluggish return to equilibrium
- Driven / Forced Resonance: Steady-state amplitude peak at resonance
"""

from __future__ import annotations

import enum
import math


class DampingRegime(enum.Enum):
    UNDERDAMPED = "underdamped"
    CRITICALLY_DAMPED = "critically_damped"
    OVERDAMPED = "overdamped"


class DampedOscillator:
    """Exact analytical solver for damped harmonic oscillators."""

    def __init__(
        self,
        mass: float,
        stiffness: float,
        damping_coefficient: float,
        initial_displacement: float = 1.0,
        initial_velocity: float = 0.0,
    ) -> None:
        self.m = mass
        self.k = stiffness
        self.gamma = damping_coefficient # damping constant c or gamma (N·s/m)
        self.x0 = initial_displacement
        self.v0 = initial_velocity

        self.omega_0 = math.sqrt(stiffness / mass)
        self.beta = damping_coefficient / (2.0 * mass) # damping factor beta

        disc = (self.beta ** 2) - (self.omega_0 ** 2)

        if abs(disc) < 1e-9:
            self.regime = DampingRegime.CRITICALLY_DAMPED
            self.omega_d = 0.0
        elif disc < 0:
            self.regime = DampingRegime.UNDERDAMPED
            self.omega_d = math.sqrt(-disc) # damped angular frequency
        else:
            self.regime = DampingRegime.OVERDAMPED
            self.omega_d = math.sqrt(disc)

    @property
    def quality_factor(self) -> float:
        """Q factor = omega_0 / (2 * beta)."""
        return self.omega_0 / (2.0 * self.beta) if self.beta > 0 else float("inf")

    def position_at(self, t: float) -> float:
        """Exact displacement x(t) based on the damping regime."""
        b = self.beta
        if self.regime == DampingRegime.UNDERDAMPED:
            wd = self.omega_d
            # x(t) = e^(-βt) * [x0 * cos(wd*t) + ((v0 + β*x0)/wd) * sin(wd*t)]
            c1 = self.x0
            c2 = (self.v0 + b * self.x0) / wd
            return math.exp(-b * t) * (c1 * math.cos(wd * t) + c2 * math.sin(wd * t))

        elif self.regime == DampingRegime.CRITICALLY_DAMPED:
            # x(t) = e^(-βt) * [x0 + (v0 + β*x0) * t]
            c1 = self.x0
            c2 = self.v0 + b * self.x0
            return math.exp(-b * t) * (c1 + c2 * t)

        else: # OVERDAMPED
            r = self.omega_d
            # Roots: -beta + r and -beta - r
            r1 = -b + r
            r2 = -b - r
            # x(t) = A * e^(r1*t) + B * e^(r2*t)
            # x(0) = A + B = x0
            # v(0) = r1*A + r2*B = v0
            A = (self.v0 - r2 * self.x0) / (r1 - r2)
            B = self.x0 - A
            return A * math.exp(r1 * t) + B * math.exp(r2 * t)


class DrivenOscillator:
    """Steady-state response for a driven harmonic oscillator with periodic force."""

    def __init__(
        self,
        mass: float,
        stiffness: float,
        damping_coefficient: float,
        drive_force_amplitude: float,
        drive_frequency: float,
    ) -> None:
        self.m = mass
        self.k = stiffness
        self.gamma = damping_coefficient
        self.F0 = drive_force_amplitude
        self.omega_drive = drive_frequency

        self.omega_0 = math.sqrt(stiffness / mass)

    @property
    def steady_state_amplitude(self) -> float:
        """A = (F0/m) / sqrt((omega_0² - omega_drive²)² + (gamma*omega_drive/m)²)."""
        w0_sq = self.omega_0 ** 2
        wd_sq = self.omega_drive ** 2
        term1 = (w0_sq - wd_sq) ** 2
        term2 = (self.gamma * self.omega_drive / self.m) ** 2
        return (self.F0 / self.m) / math.sqrt(term1 + term2)

    @property
    def resonance_frequency(self) -> float:
        """Resonant frequency for maximum displacement amplitude: ω_res = √(ω₀² - 2β²)."""
        beta = self.gamma / (2.0 * self.m)
        disc = (self.omega_0 ** 2) - 2.0 * (beta ** 2)
        return math.sqrt(disc) if disc > 0 else 0.0
