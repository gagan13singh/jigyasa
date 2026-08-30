"""
physengine.core.events
======================

Publish/subscribe event system for simulation lifecycle events.

The EventBus allows decoupled communication between engine subsystems.
Physics, rendering, analysis, and application layers can all react to
simulation events without knowing about each other.

Usage:
    >>> bus = EventBus()
    >>> bus.subscribe(CollisionDetected, my_handler)
    >>> bus.emit(CollisionDetected(entity_a="ball", entity_b="wall", ...))
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from dataclasses import dataclass, field


# ===========================================================================
#  Base Event
# ===========================================================================
@dataclass
class Event:
    """Base class for all simulation events.

    Attributes:
        timestamp: Simulation time when the event occurred.
        consumed: If True, the event has been handled and should not
                  propagate further.
    """

    timestamp: float = 0.0
    consumed: bool = field(default=False, repr=False)

    def consume(self) -> None:
        """Mark this event as consumed to stop propagation."""
        self.consumed = True


# ===========================================================================
#  Built-in Events
# ===========================================================================
@dataclass
class SimulationStarted(Event):
    """Emitted when the simulation begins running."""

    duration: float = 0.0


@dataclass
class SimulationStopped(Event):
    """Emitted when the simulation stops (paused or completed)."""

    reason: str = "completed"


@dataclass
class SimulationReset(Event):
    """Emitted when the simulation is reset to initial state."""

    pass


@dataclass
class StepCompleted(Event):
    """Emitted after each simulation step."""

    step_number: int = 0
    dt: float = 0.0


@dataclass
class EntityAdded(Event):
    """Emitted when an entity is added to the world."""

    entity_id: str = ""
    entity_name: str = ""


@dataclass
class EntityRemoved(Event):
    """Emitted when an entity is removed from the world."""

    entity_id: str = ""
    entity_name: str = ""


@dataclass
class CollisionDetected(Event):
    """Emitted when a collision is detected between two entities."""

    entity_a: str = ""
    entity_b: str = ""
    normal_x: float = 0.0
    normal_y: float = 0.0
    penetration: float = 0.0


@dataclass
class ThresholdReached(Event):
    """Emitted when a monitored value crosses a threshold.

    Useful for triggering educational explanations at key moments.
    """

    quantity_name: str = ""
    threshold_value: float = 0.0
    actual_value: float = 0.0
    entity_id: str = ""


@dataclass
class EnergyMilestone(Event):
    """Emitted when total energy changes significantly."""

    total_energy: float = 0.0
    kinetic_energy: float = 0.0
    potential_energy: float = 0.0


# ===========================================================================
#  Event Handler Type
# ===========================================================================
EventHandler = Callable[[Event], None]


# ===========================================================================
#  Event Bus
# ===========================================================================
class EventBus:
    """Thread-safe publish/subscribe event dispatcher.

    Handlers are called in the order they were subscribed.
    If a handler calls ``event.consume()``, subsequent handlers for
    that event type are skipped.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[Event], list[EventHandler]] = {}
        self._global_handlers: list[EventHandler] = []

    def subscribe(
        self,
        event_type: type[Event],
        handler: EventHandler,
    ) -> None:
        """Subscribe a handler to a specific event type.

        Args:
            event_type: The Event subclass to listen for.
            handler: Callable that receives the Event instance.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribe a handler that receives ALL events."""
        self._global_handlers.append(handler)

    def unsubscribe(self, event_type: type[Event], handler: EventHandler) -> None:
        """Remove a handler from a specific event type."""
        if event_type in self._handlers:
            with contextlib.suppress(ValueError):
                self._handlers[event_type].remove(handler)

    def unsubscribe_all(self, handler: EventHandler) -> None:
        """Remove a global handler."""
        with contextlib.suppress(ValueError):
            self._global_handlers.remove(handler)

    def emit(self, event: Event) -> None:
        """Dispatch an event to all subscribed handlers.

        Handlers are called in subscription order.  If any handler calls
        ``event.consume()``, remaining handlers are skipped.

        Args:
            event: The event instance to dispatch.
        """
        # Type-specific handlers
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            if event.consumed:
                break
            handler(event)

        # Global handlers
        for handler in self._global_handlers:
            if event.consumed:
                break
            handler(event)

    def clear(self) -> None:
        """Remove all handlers."""
        self._handlers.clear()
        self._global_handlers.clear()

    @property
    def handler_count(self) -> int:
        """Total number of registered handlers."""
        total = sum(len(h) for h in self._handlers.values())
        return total + len(self._global_handlers)

    def has_handlers(self, event_type: type[Event]) -> bool:
        """Check if any handlers are registered for an event type."""
        return bool(self._handlers.get(event_type)) or bool(self._global_handlers)
