"""
physengine.core
===============

Simulation infrastructure: entities, world, simulation kernel, events, state.
"""

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
    EntityAdded,
    EntityRemoved,
    Event,
    EventBus,
    SimulationReset,
    SimulationStarted,
    SimulationStopped,
    StepCompleted,
    ThresholdReached,
)
from physengine.core.simulation import Clock, Simulation, SimulationStatus
from physengine.core.state import EntityState, SimulationState, StateHistory
from physengine.core.world import World

__all__ = [
    "Clock",
    "CollisionDetected",
    "Component",
    "Entity",
    "EntityAdded",
    "EntityRemoved",
    "EntityState",
    "Event",
    "EventBus",
    "Material",
    "RigidBodyComponent",
    "Simulation",
    "SimulationConfig",
    "SimulationReset",
    "SimulationStarted",
    "SimulationState",
    "SimulationStatus",
    "SimulationStopped",
    "StateHistory",
    "StepCompleted",
    "ThresholdReached",
    "Transform",
    "World",
]
