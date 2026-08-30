"""
physengine.math
===============

Mathematical foundation for the physics engine.

Re-exports:
    Vector2, Vector3 — immutable 2D/3D vectors
    EPSILON          — floating-point comparison tolerance
"""

from physengine.math.vector import EPSILON, Vector2, Vector3

__all__ = [
    "EPSILON",
    "Vector2",
    "Vector3",
]
