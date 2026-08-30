"""
physengine.rendering.base
=========================

Abstract renderer interface and coordinate mapping.

This module defines the contracts that any renderer must implement.
The physics engine NEVER imports Manim, matplotlib, or any other
rendering library here.  Only abstract base classes.

Concrete renderers (ManimRenderer, WebRenderer, etc.) live in
separate packages and implement these interfaces.

Key principle:
    Physics Engine → Renderer Interface → Concrete Renderer
    The physics engine knows NOTHING about how rendering works.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from physengine.math.vector import Vector2

if TYPE_CHECKING:
    from physengine.core.simulation import Simulation
    from physengine.core.state import StateHistory


# ===========================================================================
#  Coordinate Mapping
# ===========================================================================
class CoordinateMapper:
    """Maps between physics coordinates and renderer coordinates.

    Physics uses SI units (meters). Renderers use their own units
    (Manim scene units, pixels, WebGL world units, etc.).

    Usage:
        >>> mapper = CoordinateMapper(scale=0.5, offset=Vector2(4, 3))
        >>> mapper.to_render(Vector2(10, 0))  # Vector2(9, 3)
    """

    def __init__(
        self,
        scale: float = 1.0,
        offset: Vector2 | None = None,
        flip_y: bool = False,
    ) -> None:
        """
        Args:
            scale: Multiplier from physics units to render units.
                   e.g., 0.5 means 1 meter = 0.5 render units.
            offset: Translation offset in render coordinates.
            flip_y: If True, negate y-axis (common for screen coordinates).
        """
        self.scale = scale
        self.offset = offset or Vector2.zero()
        self.flip_y = flip_y

    def to_render(self, physics_pos: Vector2) -> Vector2:
        """Convert physics position to renderer position."""
        y = -physics_pos.y if self.flip_y else physics_pos.y
        return Vector2(
            physics_pos.x * self.scale + self.offset.x,
            y * self.scale + self.offset.y,
        )

    def to_physics(self, render_pos: Vector2) -> Vector2:
        """Convert renderer position back to physics position."""
        x = (render_pos.x - self.offset.x) / self.scale
        y = (render_pos.y - self.offset.y) / self.scale
        if self.flip_y:
            y = -y
        return Vector2(x, y)

    def scale_value(self, physics_value: float) -> float:
        """Scale a distance/size from physics to render units."""
        return physics_value * self.scale


# ===========================================================================
#  Renderable Hints (what to draw)
# ===========================================================================
@dataclass
class RenderHint:
    """Visual hint for rendering an entity.

    Attached to entities to tell the renderer how to draw them.
    These are suggestions — the renderer may interpret them differently.
    """

    shape: str = "circle"  # "circle", "square", "arrow", "point", "custom"
    color: str = "#4A90D9"  # Hex color
    radius: float = 0.15  # Size in physics units
    show_trail: bool = False  # Draw trajectory trail
    trail_color: str = "#4A90D9"
    trail_width: float = 2.0
    show_velocity_arrow: bool = False
    show_acceleration_arrow: bool = False
    show_force_arrows: bool = False
    label: str = ""  # Text label
    opacity: float = 1.0
    z_index: int = 0  # Draw order


# ===========================================================================
#  Abstract Renderer
# ===========================================================================
class Renderer(ABC):
    """Abstract base class for all renderers.

    A renderer takes simulation data and produces visual output.
    It does NOT run the simulation — it only visualizes recorded states.
    """

    def __init__(self, coordinate_mapper: CoordinateMapper | None = None) -> None:
        self.mapper = coordinate_mapper or CoordinateMapper()

    @abstractmethod
    def render(self, simulation: Simulation) -> None:
        """Render a completed simulation.

        Args:
            simulation: The simulation (with recorded history) to visualize.
        """
        ...

    @abstractmethod
    def render_frame(self, simulation: Simulation, time: float) -> None:
        """Render a single frame at the given simulation time.

        Args:
            simulation: The simulation.
            time: The simulation time to render.
        """
        ...

    def render_history(self, history: StateHistory) -> None:
        """Render from a StateHistory (no Simulation needed).

        Default implementation raises NotImplementedError.
        Override in concrete renderers that support this.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not support render_history()"
        )
