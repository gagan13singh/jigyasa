"""
physengine.scientia.registry
============================

Simulation Registry for Scientia Learning Platform.
Catalogs all interactive physics simulations with structured metadata,
parameter schemas, chapter mappings, and concept tags.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ParameterSchema:
    """Definition of an interactive parameter for a simulation."""

    name: str
    label: str
    unit: str
    min_value: float
    max_value: float
    default_value: float
    step: float
    description: str


@dataclass
class SimulationMetadata:
    """Metadata specification for a simulation registered in PhysEngine."""

    id: str
    title: str
    chapter: str
    class_grade: int
    subject: str = "physics"
    simulation_type: str = "particle_dynamics"
    level: int = 1
    level_name: str = "Fundamental Mechanics"
    tags: list[str] = field(default_factory=list)
    key_formula_latex: str = ""
    derivation_steps_latex: list[str] = field(default_factory=list)
    description: str = ""
    parameters: list[ParameterSchema] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SimulationRegistry:
    """Central registry of all curriculum simulations available to Scientia."""

    def __init__(self) -> None:
        self._simulations: dict[str, SimulationMetadata] = {}
        self._populate_default_catalog()

    def register(self, metadata: SimulationMetadata) -> None:
        """Register a simulation in the catalog."""
        self._simulations[metadata.id] = metadata

    def get(self, sim_id: str) -> SimulationMetadata | None:
        """Retrieve simulation metadata by its unique ID."""
        return self._simulations.get(sim_id)

    def list_all(self) -> list[SimulationMetadata]:
        """List all registered simulations."""
        return list(self._simulations.values())

    def find_by_chapter(self, chapter: str) -> list[SimulationMetadata]:
        """Find simulations for a specific NCERT/curriculum chapter."""
        chapter_norm = chapter.strip().lower()
        return [s for s in self._simulations.values() if chapter_norm in s.chapter.lower()]

    def find_by_class(self, class_grade: int) -> list[SimulationMetadata]:
        """Find simulations for a specific school grade (9, 10, 11, 12)."""
        return [s for s in self._simulations.values() if s.class_grade == class_grade]

    def find_by_tag(self, tag: str) -> list[SimulationMetadata]:
        """Find simulations containing a specific physics concept tag."""
        tag_norm = tag.strip().lower()
        return [s for s in self._simulations.values() if any(tag_norm == t.lower() for t in s.tags)]

    def search(self, query: str) -> list[SimulationMetadata]:
        """Search simulations by title, description, chapter, or tags."""
        q = query.strip().lower()
        results = []
        for s in self._simulations.values():
            if (
                q in s.id.lower()
                or q in s.title.lower()
                or q in s.chapter.lower()
                or q in s.description.lower()
                or any(q in t.lower() for t in s.tags)
            ):
                results.append(s)
        return results

    def to_json(self, indent: int = 2) -> str:
        """Export the registry catalog as JSON."""
        return json.dumps([s.to_dict() for s in self._simulations.values()], indent=indent)

    def _populate_default_catalog(self) -> None:
        """Populate standard Class 9-12 curriculum simulation entries."""
        # Standard parameters
        p_force = ParameterSchema(
            "force", "Applied Force", "N", 1.0, 100.0, 25.0, 1.0, "External force applied to body"
        )
        p_mass = ParameterSchema(
            "mass", "Mass", "kg", 0.5, 20.0, 2.0, 0.5, "Mass of the primary particle/body"
        )
        p_v0 = ParameterSchema(
            "velocity",
            "Initial Velocity",
            "m/s",
            1.0,
            40.0,
            20.0,
            1.0,
            "Initial velocity magnitude",
        )
        p_angle = ParameterSchema(
            "angle", "Launch Angle", "deg", 15.0, 85.0, 45.0, 1.0, "Angle above horizontal"
        )
        p_incline = ParameterSchema(
            "incline", "Incline Angle", "deg", 5.0, 60.0, 30.0, 1.0, "Angle of inclined plane"
        )
        p_friction = ParameterSchema(
            "friction", "Friction Coeff (mu)", "", 0.0, 0.9, 0.3, 0.05, "Coefficient of friction"
        )
        p_radius = ParameterSchema(
            "radius", "Radius (R)", "m", 2.0, 25.0, 10.0, 0.5, "Radius of circular curvature"
        )
        p_spring = ParameterSchema(
            "spring", "Spring Constant (k)", "N/m", 10.0, 200.0, 50.0, 5.0, "Stiffness of spring"
        )
        p_restitution = ParameterSchema(
            "restitution",
            "Restitution Coeff (e)",
            "",
            0.0,
            1.0,
            0.8,
            0.05,
            "Coefficient of restitution",
        )

        catalog = [
            # ── Level 1: Laws of Motion ──
            SimulationMetadata(
                id="newton-second-law",
                title="Newton's Second Law of Motion",
                chapter="Laws of Motion",
                class_grade=11,
                level=1,
                level_name="Fundamental Mechanics",
                tags=["force", "mass", "acceleration", "momentum", "fbd"],
                key_formula_latex=r"\vec{F} = m\vec{a}",
                derivation_steps_latex=[
                    r"\vec{p} = m\vec{v} \quad \text{(Linear Momentum)}",
                    r"\vec{F} = \frac{d\vec{p}}{dt} = \frac{d(m\vec{v})}{dt}",
                    r"\vec{F} = m\frac{d\vec{v}}{dt} = m\vec{a}",
                ],
                description="Interactive dynamic simulation of F = ma with variable applied force and mass.",
                parameters=[p_force, p_mass],
            ),
            SimulationMetadata(
                id="impulse-momentum",
                title="Impulse-Momentum Theorem",
                chapter="Laws of Motion",
                class_grade=11,
                level=1,
                level_name="Fundamental Mechanics",
                tags=["impulse", "momentum", "force", "collision"],
                key_formula_latex=r"\vec{J} = \int \vec{F}\,dt = \Delta\vec{p}",
                derivation_steps_latex=[
                    r"\vec{J} = \int_{t_1}^{t_2} \vec{F}\,dt",
                    r"\vec{F} = \frac{d\vec{p}}{dt} \implies \vec{F}\,dt = d\vec{p}",
                    r"\vec{J} = \int d\vec{p} = \vec{p}_2 - \vec{p}_1 = \Delta\vec{p}",
                ],
                description="Simulates force sensor wall collision measuring integral of force over impact time.",
                parameters=[p_mass, p_v0],
            ),
            SimulationMetadata(
                id="momentum-conservation",
                title="Conservation of Linear Momentum",
                chapter="Laws of Motion",
                class_grade=11,
                level=1,
                level_name="Fundamental Mechanics",
                tags=["momentum", "conservation", "collisions", "two-body"],
                key_formula_latex=r"m_1\vec{u}_1 + m_2\vec{u}_2 = m_1\vec{v}_1 + m_2\vec{v}_2",
                derivation_steps_latex=[
                    r"\vec{F}_{12} = -\vec{F}_{21} \quad \text{(Newton's Third Law)}",
                    r"\frac{d\vec{p}_1}{dt} = -\frac{d\vec{p}_2}{dt} \implies \frac{d}{dt}(\vec{p}_1 + \vec{p}_2) = 0",
                    r"\Sigma\vec{p} = \text{constant}",
                ],
                description="Two dynamic colliding carts on frictionless air track verifying momentum conservation.",
                parameters=[p_mass, p_v0, p_restitution],
            ),
            SimulationMetadata(
                id="equations-of-motion",
                title="Kinematic Equations of Motion",
                chapter="Motion in a Straight Line",
                class_grade=11,
                level=1,
                level_name="Fundamental Mechanics",
                tags=["kinematics", "velocity", "acceleration", "displacement"],
                key_formula_latex=r"v = u + at, \quad s = ut + \frac{1}{2}at^2, \quad v^2 = u^2 + 2as",
                derivation_steps_latex=[
                    r"a = \frac{dv}{dt} \implies v = u + at",
                    r"v = \frac{ds}{dt} \implies s = ut + \frac{1}{2}at^2",
                    r"a = v\frac{dv}{ds} \implies v^2 = u^2 + 2as",
                ],
                description="Simulates 1D uniformly accelerated particle with live distance, velocity, and graphs.",
                parameters=[p_force, p_mass, p_v0],
            ),
            # ── Level 2: Friction & Inclines ──
            SimulationMetadata(
                id="static-friction",
                title="Limiting Static Friction & Break-Away",
                chapter="Laws of Motion",
                class_grade=11,
                level=2,
                level_name="Friction & Inclines",
                tags=["friction", "static-friction", "normal-force", "threshold"],
                key_formula_latex=r"f_s \le f_{\max} = \mu_s N = \mu_s mg",
                derivation_steps_latex=[
                    r"N = mg \quad \text{(Vertical Equilibrium)}",
                    r"f_{\max} = \mu_s N = \mu_s mg",
                    r"F_{\text{applied}} \le f_{\max} \implies a = 0",
                    r"F_{\text{applied}} > f_{\max} \implies a = \frac{F - \mu_k mg}{m}",
                ],
                description="Ramping applied force against static friction demonstrating limiting threshold and break-away.",
                parameters=[p_mass, p_friction],
            ),
            SimulationMetadata(
                id="angle-of-repose",
                title="Angle of Repose on Incline",
                chapter="Laws of Motion",
                class_grade=11,
                level=2,
                level_name="Friction & Inclines",
                tags=["incline", "friction", "angle-of-repose", "static-equilibrium"],
                key_formula_latex=r"\theta_{\text{repose}} = \tan^{-1}(\mu_s) = \lambda",
                derivation_steps_latex=[
                    r"N = mg\cos\theta, \quad f_s = mg\sin\theta",
                    r"\text{At limiting equilibrium: } f_s = \mu_s N",
                    r"mg\sin\theta_r = \mu_s mg\cos\theta_r \implies \tan\theta_r = \mu_s",
                ],
                description="Incline tilts upward until gravitational component overcomes static friction at θ = tan⁻¹(μ).",
                parameters=[p_mass, p_friction],
            ),
            SimulationMetadata(
                id="incline-acceleration",
                title="Acceleration Down a Rough Incline",
                chapter="Laws of Motion",
                class_grade=11,
                level=2,
                level_name="Friction & Inclines",
                tags=["incline", "friction", "acceleration", "gravity"],
                key_formula_latex=r"a = g(\sin\theta - \mu_k\cos\theta)",
                derivation_steps_latex=[
                    r"F_{\parallel} = mg\sin\theta, \quad N = mg\cos\theta",
                    r"f_k = \mu_k N = \mu_k mg\cos\theta",
                    r"F_{\text{net}} = mg\sin\theta - \mu_k mg\cos\theta = ma",
                    r"a = g(\sin\theta - \mu_k\cos\theta)",
                ],
                description="Simulates block accelerating down inclined wedge with kinetic friction resistance.",
                parameters=[p_mass, p_incline, p_friction],
            ),
            # ── Level 3: Circular Motion & Banking ──
            SimulationMetadata(
                id="centripetal-force",
                title="Centripetal Force & Whirling Tether",
                chapter="Laws of Motion",
                class_grade=11,
                level=3,
                level_name="Circular & Banking",
                tags=["circular-motion", "centripetal-force", "tension", "rotation"],
                key_formula_latex=r"F_c = \frac{m v^2}{R} = m \omega^2 R",
                derivation_steps_latex=[
                    r"\vec{a}_c = -\frac{v^2}{R}\hat{r} = -\omega^2 R \hat{r}",
                    r"\vec{F}_c = m\vec{a}_c = -\frac{mv^2}{R}\hat{r}",
                    r"T = \frac{mv^2}{R} \quad \text{(Tension in cord)}",
                ],
                description="Tethered particle orbiting on a circular path under central tension.",
                parameters=[p_mass, p_v0, p_radius],
            ),
            SimulationMetadata(
                id="banking-frictionless",
                title="Frictionless Road Banking (Design Speed)",
                chapter="Laws of Motion",
                class_grade=11,
                level=3,
                level_name="Circular & Banking",
                tags=["banking", "circular-motion", "normal-force", "roads"],
                key_formula_latex=r"v_{\text{opt}} = \sqrt{R g \tan\theta}",
                derivation_steps_latex=[
                    r"N\cos\theta = mg \implies N = \frac{mg}{\cos\theta}",
                    r"N\sin\theta = \frac{mv^2}{R}",
                    r"\tan\theta = \frac{v^2}{Rg} \implies v_{\text{opt}} = \sqrt{Rg\tan\theta}",
                ],
                description="Banked turn where the horizontal component of normal force supplies centripetal acceleration.",
                parameters=[p_mass, p_incline, p_radius],
            ),
            SimulationMetadata(
                id="banking-with-friction",
                title="Road Banking with Friction (Safe Speed Envelope)",
                chapter="Laws of Motion",
                class_grade=11,
                level=3,
                level_name="Circular & Banking",
                tags=["banking", "friction", "safe-speed", "circular-motion"],
                key_formula_latex=r"v_{\max} = \sqrt{Rg\left(\frac{\tan\theta + \mu}{1 - \mu\tan\theta}\right)}",
                derivation_steps_latex=[
                    r"N\cos\theta - f_s\sin\theta = mg",
                    r"N\sin\theta + f_s\cos\theta = \frac{mv^2}{R}",
                    r"f_s = \mu N \implies v_{\max} = \sqrt{Rg\left(\frac{\tan\theta + \mu}{1 - \mu\tan\theta}\right)}",
                    r"v_{\min} = \sqrt{Rg\left(\frac{\tan\theta - \mu}{1 + \mu\tan\theta}\right)}",
                ],
                description="Complete 3D banked curved racetrack with live safe velocity gauge [v_min, v_max].",
                parameters=[p_mass, p_v0, p_incline, p_friction, p_radius],
            ),
            # ── Level 4: Work, Energy & Power ──
            SimulationMetadata(
                id="work-energy-theorem",
                title="Work-Energy Theorem",
                chapter="Work, Energy and Power",
                class_grade=11,
                level=4,
                level_name="Work, Energy & Power",
                tags=["work", "kinetic-energy", "work-energy-theorem", "power"],
                key_formula_latex=r"W_{\text{net}} = \Delta K = K_f - K_i = \frac{1}{2}m v_f^2 - \frac{1}{2}m v_i^2",
                derivation_steps_latex=[
                    r"W = \int \vec{F}\cdot d\vec{r} = \int m\frac{dv}{dt} v\,dt",
                    r"W = m \int_{v_i}^{v_f} v\,dv = \frac{1}{2}mv_f^2 - \frac{1}{2}mv_i^2 = \Delta K",
                ],
                description="Work done by net force directly converting into particle kinetic energy.",
                parameters=[p_force, p_mass, p_v0],
            ),
            SimulationMetadata(
                id="spring-potential-energy",
                title="Elastic Potential Energy of a Spring",
                chapter="Work, Energy and Power",
                class_grade=11,
                level=4,
                level_name="Work, Energy & Power",
                tags=["spring", "potential-energy", "hooke-law", "shm"],
                key_formula_latex=r"U = \frac{1}{2}k x^2, \quad W_{\text{spring}} = -\frac{1}{2}k(x_2^2 - x_1^2)",
                derivation_steps_latex=[
                    r"F_s = -kx \quad \text{(Hooke's Law)}",
                    r"W = \int_0^x (-kx')\,dx' = -\frac{1}{2}kx^2",
                    r"\Delta U = -W \implies U(x) = \frac{1}{2}kx^2",
                ],
                description="Simulates horizontal spring-mass oscillator with continuous KE ↔ PE conversion.",
                parameters=[p_mass, p_spring],
            ),
            # ── Level 5: Collisions ──
            SimulationMetadata(
                id="elastic-collision-1d",
                title="1D Elastic Collision (Velocity Exchange)",
                chapter="Work, Energy and Power",
                class_grade=11,
                level=5,
                level_name="Collisions & Restitution",
                tags=["collision", "elastic", "momentum", "kinetic-energy"],
                key_formula_latex=r"v_1 = \frac{m_1 - m_2}{m_1 + m_2}u_1 + \frac{2m_2}{m_1 + m_2}u_2",
                derivation_steps_latex=[
                    r"m_1 u_1 + m_2 u_2 = m_1 v_1 + m_2 v_2 \quad \text{(Momentum)}",
                    r"\frac{1}{2}m_1 u_1^2 + \frac{1}{2}m_2 u_2^2 = \frac{1}{2}m_1 v_1^2 + \frac{1}{2}m_2 v_2^2 \quad \text{(KE)}",
                    r"v_2 - v_1 = u_1 - u_2 \implies e = 1",
                ],
                description="Head-on elastic collision with mass ratios and complete velocity exchange when m1 = m2.",
                parameters=[p_mass, p_v0, p_restitution],
            ),
            # ── Level 6: Projectile Motion ──
            SimulationMetadata(
                id="projectile-motion",
                title="2D Projectile Motion & Parabolic Trajectory",
                chapter="Motion in a Plane",
                class_grade=11,
                level=6,
                level_name="Projectile Motion",
                tags=["projectile", "parabola", "range", "flight-time", "max-height"],
                key_formula_latex=r"R = \frac{u^2\sin 2\theta}{g}, \quad H = \frac{u^2\sin^2\theta}{2g}, \quad T = \frac{2u\sin\theta}{g}",
                derivation_steps_latex=[
                    r"u_x = u\cos\theta, \quad u_y = u\sin\theta",
                    r"v_y = u_y - gt = 0 \implies t_{\text{apex}} = \frac{u\sin\theta}{g}",
                    r"T = 2t_{\text{apex}} = \frac{2u\sin\theta}{g}",
                    r"R = u_x T = (u\cos\theta)\frac{2u\sin\theta}{g} = \frac{u^2\sin 2\theta}{g}",
                    r"H = u_y t_{\text{apex}} - \frac{1}{2}g t_{\text{apex}}^2 = \frac{u^2\sin^2\theta}{2g}",
                ],
                description="Parabolic trajectory of launched projectile with live vector decomposition and landing coordinates.",
                parameters=[p_v0, p_angle, p_mass],
            ),
        ]

        for s in catalog:
            self.register(s)
