"""
physengine — Industry-Grade Physics Simulation Engine
=====================================================

A production-ready, renderer-agnostic physics engine designed for
education (Scientia, Vidyastra) and research.

Quick Start::

    from physengine import World, Particle, Simulation, UniformGravity

    world = World(gravity=9.81)
    world.add(Particle(mass=1, position=(0, 10), name="ball"))
    world.add_force(UniformGravity())

    sim = Simulation(world)
    sim.run(duration=5.0)

    # Analyze results
    positions = sim.history.get_entity_positions("ball")

Architecture:
    Physics Core → Public API → Renderers (Manim, Web, etc.)
    The engine knows NOTHING about rendering.

Modules:
    math        — Vector2, Vector3, constants, interpolation
    units       — Quantity, Dimension, dimensional analysis
    core        — Entity, World, Simulation, Events, State
    mechanics   — Particle, Forces, Momentum, Energy
    kinematics  — Analytical motion equations, projectile motion
    solvers     — Euler, Verlet, RK4 integrators
    analysis    — Recorder, Trajectory, Measurements
    rendering   — Abstract Renderer interface
    io          — Save/Load, CSV/JSON export
"""

__version__ = "0.1.0"

# -- Core (always available) ------------------------------------------------
from physengine.core.config import SimulationConfig
from physengine.core.entity import (
    Component,
    Entity,
    Material,
    RigidBodyComponent,
    Transform,
)
from physengine.core.events import (
    CollisionDetected,
    Event,
    EventBus,
    StepCompleted,
)
from physengine.core.simulation import Simulation, SimulationStatus
from physengine.core.state import EntityState, SimulationState, StateHistory
from physengine.core.world import World

# -- Electromagnetism -------------------------------------------------------
from physengine.electromagnetism import (
    CoulombForce,
    CyclotronMotion,
    ElectricChargeComponent,
    ElectronDeflectionInEField,
    UniformElectricField,
    UniformLorentzForce,
    VelocitySelector,
)

# -- I/O & Visualization ---------------------------------------------------
from physengine.io.export import export_html_animation

# -- Math -------------------------------------------------------------------
from physengine.math.vector import Vector2, Vector3

# -- Mechanics --------------------------------------------------------------
from physengine.mechanics.collisions import (
    BallisticPendulum,
    resolve_collision_1d,
    resolve_collision_2d,
)
from physengine.mechanics.fluids import (
    BuoyantForce,
    StokesDrag,
    terminal_velocity_stokes,
)
from physengine.mechanics.forces import (
    CompositeForce,
    ConstantForce,
    Drag,
    Force,
    Friction,
    PointGravity,
    Spring,
    UniformGravity,
)
from physengine.mechanics.particle import Particle, StaticBody
from physengine.mechanics.pulley import AtwoodMachine, TablePulleySystem
from physengine.mechanics.rotational import (
    InertiaShape,
    RollingBodyOnIncline,
    RotationalComponent,
    moment_of_inertia,
    parallel_axis_theorem,
    perpendicular_axis_theorem,
    torque_from_force,
)

# -- Oscillations -----------------------------------------------------------
from physengine.oscillations import (
    CompoundPendulum,
    DampedOscillator,
    DampingRegime,
    DrivenOscillator,
    SimpleHarmonicMotion,
    SimplePendulum,
    TorsionalPendulum,
)

# -- Scientia Learning Integration ------------------------------------------
from physengine.scientia import (
    DPASolution,
    PhysicsKnowledgeGraph,
    ProblemSolver,
    ProblemSpec,
    ScientiaPhysicsClient,
    ScientiaPhysicsService,
    SimulationMetadata,
    SimulationRegistry,
    SystemType,
)

# -- Solvers ----------------------------------------------------------------
from physengine.solvers import (
    EulerIntegrator,
    Integrator,
    RK4Integrator,
    SemiImplicitEulerIntegrator,
    VelocityVerletIntegrator,
)

# -- Visualization & I/O ---------------------------------------------------
from physengine.visualizer.server import start_visualizer

__all__ = [
    # Version
    "__version__",
    # Math
    "Vector2",
    "Vector3",
    # Core
    "Component",
    "Entity",
    "Material",
    "RigidBodyComponent",
    "Transform",
    "World",
    "Simulation",
    "SimulationConfig",
    "SimulationStatus",
    "Event",
    "EventBus",
    "StepCompleted",
    "CollisionDetected",
    "EntityState",
    "SimulationState",
    "StateHistory",
    # Mechanics & Forces
    "Particle",
    "StaticBody",
    "Force",
    "UniformGravity",
    "PointGravity",
    "Drag",
    "Spring",
    "Friction",
    "ConstantForce",
    "CompositeForce",
    # Collisions
    "resolve_collision_1d",
    "resolve_collision_2d",
    "BallisticPendulum",
    # Rotational
    "InertiaShape",
    "RotationalComponent",
    "moment_of_inertia",
    "parallel_axis_theorem",
    "perpendicular_axis_theorem",
    "torque_from_force",
    "RollingBodyOnIncline",
    # Fluids
    "BuoyantForce",
    "StokesDrag",
    "terminal_velocity_stokes",
    # Pulley
    "AtwoodMachine",
    "TablePulleySystem",
    # Oscillations
    "SimpleHarmonicMotion",
    "SimplePendulum",
    "CompoundPendulum",
    "TorsionalPendulum",
    "DampedOscillator",
    "DampingRegime",
    "DrivenOscillator",
    # Electromagnetism
    "ElectricChargeComponent",
    "CoulombForce",
    "UniformElectricField",
    "UniformLorentzForce",
    "CyclotronMotion",
    "VelocitySelector",
    "ElectronDeflectionInEField",
    # Solvers
    "Integrator",
    "EulerIntegrator",
    "SemiImplicitEulerIntegrator",
    "VelocityVerletIntegrator",
    "RK4Integrator",
    # Visualization & I/O
    "export_html_animation",
    "start_visualizer",
    # Scientia Learning Integration
    "ScientiaPhysicsClient",
    "ScientiaPhysicsService",
    "SimulationRegistry",
    "SimulationMetadata",
    "ProblemSpec",
    "ProblemSolver",
    "DPASolution",
    "PhysicsKnowledgeGraph",
    "SystemType",
]

