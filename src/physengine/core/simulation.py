"""
physengine.core.simulation
==========================

The Simulation is the main entry point for running physics.

It orchestrates the simulation loop:

    Initialize → Create World → Add Objects → Apply Forces →
    Calculate Acceleration → Integrate → Update State → Record → Repeat

The simulation is renderer-agnostic.  ``simulation.step(dt)`` works
perfectly fine without Manim or any visualization library installed.

Usage:
    >>> world = World(gravity=9.81)
    >>> world.add(Particle(mass=1, position=(0, 10), name="ball"))
    >>> sim = Simulation(world)
    >>> sim.run(duration=5.0)
    >>> trajectory = sim.history.get_entity_positions("ball")
"""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

from physengine.core.config import SimulationConfig
from physengine.core.entity import Entity, RigidBodyComponent, Transform
from physengine.core.events import (
    SimulationReset,
    SimulationStarted,
    SimulationStopped,
    StepCompleted,
)
from physengine.core.state import EntityState, SimulationState, StateHistory
from physengine.core.world import World
from physengine.math.vector import Vector2

if TYPE_CHECKING:
    from physengine.solvers.base import Integrator


class SimulationStatus(Enum):
    """Current state of the simulation."""

    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()


class Clock:
    """Simulation time tracker.

    Keeps track of current time, step count, and timestep.
    """

    __slots__ = ("_time", "_step", "_dt")

    def __init__(self, dt: float) -> None:
        self._time: float = 0.0
        self._step: int = 0
        self._dt: float = dt

    @property
    def time(self) -> float:
        """Current simulation time in seconds."""
        return self._time

    @property
    def step(self) -> int:
        """Current step number."""
        return self._step

    @property
    def dt(self) -> float:
        """Timestep size."""
        return self._dt

    @dt.setter
    def dt(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"Timestep must be positive, got {value}")
        self._dt = value

    def advance(self) -> None:
        """Advance the clock by one timestep."""
        self._time += self._dt
        self._step += 1

    def reset(self) -> None:
        """Reset clock to t=0, step=0."""
        self._time = 0.0
        self._step = 0


class Simulation:
    """The main simulation kernel.

    Connects the World (entities + forces) with an Integrator (numerical solver)
    and records state history for analysis and rendering.

    Attributes:
        world: The World containing entities and forces.
        clock: Time tracker.
        history: Recorded state snapshots.
        status: Current simulation status.
    """

    def __init__(
        self,
        world: World,
        integrator: Integrator | None = None,
        config: SimulationConfig | None = None,
    ) -> None:
        """
        Args:
            world: The simulation world.
            integrator: Numerical integrator. If None, uses the integrator
                        specified in world.config or defaults to RK4.
            config: Override configuration. If None, uses world.config.
        """
        self.world = world
        self.config = config or world.config
        self.clock = Clock(self.config.effective_dt)
        self.history = StateHistory(max_size=self.config.max_history_size)
        self.status = SimulationStatus.IDLE

        # Resolve integrator
        self._integrator = integrator or self._create_default_integrator()

        # Store initial state for reset
        self._initial_entity_data: list[dict] = []

    def _create_default_integrator(self) -> Integrator:
        """Create integrator from config name."""
        from physengine.solvers.euler import EulerIntegrator, SemiImplicitEulerIntegrator
        from physengine.solvers.rk4 import RK4Integrator
        from physengine.solvers.verlet import VelocityVerletIntegrator

        integrators = {
            "euler": EulerIntegrator,
            "semi_implicit_euler": SemiImplicitEulerIntegrator,
            "verlet": VelocityVerletIntegrator,
            "rk4": RK4Integrator,
        }

        name = self.config.integrator_name.lower()
        if name not in integrators:
            raise ValueError(
                f"Unknown integrator '{name}'. "
                f"Available: {list(integrators.keys())}"
            )
        return integrators[name]()

    # -- Main simulation loop ------------------------------------------------
    def run(self, duration: float | None = None) -> StateHistory:
        """Run the simulation for the given duration.

        Args:
            duration: Time to simulate in seconds. If None, uses config.duration.

        Returns:
            The recorded StateHistory.
        """
        duration = duration if duration is not None else self.config.duration

        # Save initial state for reset
        self._save_initial_state()

        self.status = SimulationStatus.RUNNING
        self.world.event_bus.emit(SimulationStarted(duration=duration))

        # Record initial state
        if self.config.enable_recording:
            self._record_state()

        dt = self.clock.dt
        target_time = self.clock.time + duration

        while self.clock.time < target_time - dt * 0.5:
            if self.status != SimulationStatus.RUNNING:
                break
            self.step(dt)

        self.status = SimulationStatus.COMPLETED
        self.world.event_bus.emit(SimulationStopped(
            timestamp=self.clock.time, reason="completed"
        ))

        return self.history

    def step(self, dt: float | None = None) -> None:
        """Advance the simulation by one timestep.

        This is the core simulation step:
            1. Accumulate forces → net acceleration for each entity
            2. Integrate (advance position and velocity)
            3. Record state
            4. Emit StepCompleted event

        Args:
            dt: Timestep override. Uses clock.dt if None.
        """
        dt = dt if dt is not None else self.clock.dt

        for entity in self.world.dynamic_entities:
            rb = entity.get_component(RigidBodyComponent)
            transform = entity.get_component(Transform)

            # 1. Accumulate forces → acceleration
            net_force = self._compute_net_force(entity)
            acceleration = net_force * rb.inverse_mass

            # 2. Integrate
            new_pos, new_vel = self._integrator.step(
                position=transform.position,
                velocity=rb.velocity,
                acceleration=acceleration,
                dt=dt,
                acceleration_fn=lambda pos, vel, e=entity: self._compute_acceleration_at(
                    e, pos, vel
                ),
            )

            # Update components
            transform.position = new_pos
            rb.velocity = new_vel
            rb.acceleration = acceleration

            # Linear damping
            if rb.linear_damping > 0.0:
                rb.velocity = rb.velocity * (1.0 - rb.linear_damping * dt)

        # ── Step 3: Advance clock ──────────────────────────────────
        self.clock.advance()

        # ── Step 4: Record & Notify ────────────────────────────────
        # Record state
        if self.config.enable_recording and self.clock.step % self.config.record_interval == 0:
            self._record_state()

        # Emit event
        self.world.event_bus.emit(StepCompleted(
            timestamp=self.clock.time,
            step_number=self.clock.step,
            dt=dt,
        ))

    def _compute_net_force(self, entity: Entity) -> Vector2:
        """Calculate the total force on an entity from all sources."""

        net = Vector2.zero()
        forces = self.world.get_forces_for(entity)

        for force in forces:
            f = force.calculate(entity, self.world, self.clock.dt)
            net = net + f

        return net

    def _compute_acceleration_at(
        self,
        entity: Entity,
        position: Vector2,
        velocity: Vector2,
    ) -> Vector2:
        """Compute acceleration for a hypothetical state.

        Used by multi-step integrators (RK4) that evaluate forces at
        intermediate positions/velocities.
        """

        rb = entity.get_component(RigidBodyComponent)

        # Temporarily set position/velocity for force evaluation
        original_pos = entity.transform.position
        original_vel = rb.velocity

        entity.transform.position = position
        rb.velocity = velocity

        net_force = self._compute_net_force(entity)
        accel = net_force * rb.inverse_mass

        # Restore original state
        entity.transform.position = original_pos
        rb.velocity = original_vel

        return accel

    def _record_state(self) -> None:
        """Capture a SimulationState snapshot."""
        entity_states: dict[str, EntityState] = {}
        total_ke = 0.0
        total_momentum = Vector2.zero()

        for entity in self.world.entities:
            es = EntityState.from_entity(entity)
            entity_states[entity.id] = es
            total_ke += es.kinetic_energy
            total_momentum = total_momentum + es.momentum

        state = SimulationState(
            time=self.clock.time,
            step=self.clock.step,
            entities=entity_states,
            total_kinetic_energy=total_ke,
            total_momentum=total_momentum,
        )

        self.history.record(state)

    # -- Control -------------------------------------------------------------
    def pause(self) -> None:
        """Pause the simulation."""
        if self.status == SimulationStatus.RUNNING:
            self.status = SimulationStatus.PAUSED
            self.world.event_bus.emit(SimulationStopped(
                timestamp=self.clock.time, reason="paused"
            ))

    def resume(self) -> None:
        """Resume a paused simulation."""
        if self.status == SimulationStatus.PAUSED:
            self.status = SimulationStatus.RUNNING

    def reset(self) -> None:
        """Reset simulation to initial state."""
        self._restore_initial_state()
        self.clock.reset()
        self.history.clear()
        self.status = SimulationStatus.IDLE
        self.world.event_bus.emit(SimulationReset(timestamp=0.0))

    def _save_initial_state(self) -> None:
        """Save entity states for reset."""
        self._initial_entity_data.clear()
        for entity in self.world.entities:
            data: dict = {"id": entity.id}
            if entity.has_component(Transform):
                t = entity.get_component(Transform)
                data["position"] = Vector2(t.position.x, t.position.y)
                data["rotation"] = t.rotation
            if entity.has_component(RigidBodyComponent):
                rb = entity.get_component(RigidBodyComponent)
                data["velocity"] = Vector2(rb.velocity.x, rb.velocity.y)
                data["acceleration"] = Vector2.zero()
            self._initial_entity_data.append(data)

    def _restore_initial_state(self) -> None:
        """Restore entity states from saved data."""
        for data in self._initial_entity_data:
            try:
                entity = self.world._entities[data["id"]]
            except KeyError:
                continue
            if "position" in data and entity.has_component(Transform):
                entity.get_component(Transform).position = data["position"]
                entity.get_component(Transform).rotation = data.get("rotation", 0.0)
            if "velocity" in data and entity.has_component(RigidBodyComponent):
                rb = entity.get_component(RigidBodyComponent)
                rb.velocity = data["velocity"]
                rb.acceleration = data.get("acceleration", Vector2.zero())

    # -- Properties ----------------------------------------------------------
    @property
    def current_time(self) -> float:
        """Current simulation time."""
        return self.clock.time

    @property
    def step_count(self) -> int:
        """Number of steps executed."""
        return self.clock.step

    @property
    def integrator(self) -> Integrator:
        """The numerical integrator in use."""
        return self._integrator

    @integrator.setter
    def integrator(self, value: Integrator) -> None:
        self._integrator = value

    # -- Representation ------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"Simulation(status={self.status.name}, "
            f"t={self.clock.time:.4f}s, "
            f"steps={self.clock.step}, "
            f"entities={self.world.entity_count}, "
            f"integrator={type(self._integrator).__name__})"
        )
