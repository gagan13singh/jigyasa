"""
physengine.math.vector
======================

Production-grade vector mathematics for 2D and 3D physics simulations.

Features:
    - Immutable Vector2 and Vector3 with full operator overloading
    - Dot product, cross product, projection, reflection, rotation
    - NumPy interoperability
    - Rich comparison with configurable tolerance
    - __slots__ for memory efficiency

Design Decisions:
    - Vectors are VALUE TYPES: operations return NEW vectors, never mutate
    - Zero-overhead: __slots__ eliminates per-instance __dict__
    - NumPy used internally for batch operations; public API is pure Python
    - Tolerance-based equality for floating-point safety

Usage:
    >>> from physengine.math import Vector2, Vector3
    >>> v = Vector2(3, 4)
    >>> v.magnitude  # 5.0
    >>> v.normalize()  # Vector2(0.6, 0.8)
    >>> Vector2(1, 0).angle_between(Vector2(0, 1))  # 1.5707... (π/2)
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from typing import overload

import numpy as np
from numpy.typing import NDArray

# ---------------------------------------------------------------------------
# Tolerance for floating-point comparison
# ---------------------------------------------------------------------------
EPSILON: float = 1e-10


# ===========================================================================
#  Vector2
# ===========================================================================
class Vector2:
    """Immutable 2D vector for physics calculations.

    All arithmetic operations return **new** Vector2 instances.

    Attributes:
        x: The x component.
        y: The y component.
    """

    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        object.__setattr__(self, "x", float(x))
        object.__setattr__(self, "y", float(y))

    # -- Immutability --------------------------------------------------------
    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"Vector2 is immutable; cannot set '{name}'")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"Vector2 is immutable; cannot delete '{name}'")

    # -- Factory methods -----------------------------------------------------
    @classmethod
    def zero(cls) -> Vector2:
        """Return the zero vector (0, 0)."""
        return cls(0.0, 0.0)

    @classmethod
    def one(cls) -> Vector2:
        """Return the unit-one vector (1, 1)."""
        return cls(1.0, 1.0)

    @classmethod
    def unit_x(cls) -> Vector2:
        """Return the unit vector along x-axis (1, 0)."""
        return cls(1.0, 0.0)

    @classmethod
    def unit_y(cls) -> Vector2:
        """Return the unit vector along y-axis (0, 1)."""
        return cls(0.0, 1.0)

    @classmethod
    def from_angle(cls, angle: float, magnitude: float = 1.0) -> Vector2:
        """Create a vector from an angle (radians) and optional magnitude.

        Args:
            angle: Angle in radians measured counter-clockwise from +x axis.
            magnitude: Length of the resulting vector.
        """
        return cls(magnitude * math.cos(angle), magnitude * math.sin(angle))

    @classmethod
    def from_array(cls, arr: NDArray[np.floating] | list[float] | tuple[float, ...]) -> Vector2:
        """Create a Vector2 from a numpy array, list, or tuple."""
        return cls(float(arr[0]), float(arr[1]))

    # -- Conversion ----------------------------------------------------------
    def to_array(self) -> NDArray[np.float64]:
        """Convert to a numpy array [x, y]."""
        return np.array([self.x, self.y], dtype=np.float64)

    def to_tuple(self) -> tuple[float, float]:
        """Convert to a (x, y) tuple."""
        return (self.x, self.y)

    def to_vector3(self, z: float = 0.0) -> Vector3:
        """Promote to a Vector3 with the given z component."""
        return Vector3(self.x, self.y, z)

    # -- Properties ----------------------------------------------------------
    @property
    def magnitude(self) -> float:
        """Euclidean length of the vector."""
        return math.hypot(self.x, self.y)

    @property
    def magnitude_squared(self) -> float:
        """Squared length (avoids sqrt; useful for comparisons)."""
        return self.x * self.x + self.y * self.y

    @property
    def angle(self) -> float:
        """Angle in radians measured counter-clockwise from the +x axis.

        Returns a value in (-π, π].
        """
        return math.atan2(self.y, self.x)

    @property
    def is_zero(self) -> bool:
        """True if both components are within EPSILON of zero."""
        return abs(self.x) < EPSILON and abs(self.y) < EPSILON

    # -- Core operations -----------------------------------------------------
    def normalize(self) -> Vector2:
        """Return the unit vector in the same direction.

        Returns the zero vector if this vector has near-zero magnitude.
        """
        mag = self.magnitude
        if mag < EPSILON:
            return Vector2.zero()
        return Vector2(self.x / mag, self.y / mag)

    def dot(self, other: Vector2) -> float:
        """Scalar dot product: a · b = ax*bx + ay*by."""
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vector2) -> float:
        """2D cross product (scalar): ax*by - ay*bx.

        This gives the signed area of the parallelogram formed by the two
        vectors.  Positive → *other* is counter-clockwise from *self*.
        """
        return self.x * other.y - self.y * other.x

    def distance_to(self, other: Vector2) -> float:
        """Euclidean distance to another vector."""
        return math.hypot(self.x - other.x, self.y - other.y)

    def distance_squared_to(self, other: Vector2) -> float:
        """Squared Euclidean distance (avoids sqrt)."""
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

    def angle_between(self, other: Vector2) -> float:
        """Unsigned angle between two vectors in radians [0, π].

        Raises:
            ValueError: If either vector has zero magnitude.
        """
        d = self.magnitude * other.magnitude
        if d < EPSILON:
            raise ValueError("Cannot compute angle with a zero-length vector.")
        cos_val = max(-1.0, min(1.0, self.dot(other) / d))
        return math.acos(cos_val)

    def signed_angle_to(self, other: Vector2) -> float:
        """Signed angle from *self* to *other* in radians (-π, π].

        Positive means counter-clockwise rotation.
        """
        return math.atan2(self.cross(other), self.dot(other))

    def project_onto(self, other: Vector2) -> Vector2:
        """Vector projection of *self* onto *other*.

        Returns the component of *self* that lies along *other*.
        """
        denom = other.magnitude_squared
        if denom < EPSILON:
            return Vector2.zero()
        scalar = self.dot(other) / denom
        return Vector2(other.x * scalar, other.y * scalar)

    def reject_from(self, other: Vector2) -> Vector2:
        """Component of *self* perpendicular to *other*."""
        return self - self.project_onto(other)

    def reflect(self, normal: Vector2) -> Vector2:
        """Reflect this vector about the given normal.

        The normal should be a unit vector for correct results.
        """
        d = 2.0 * self.dot(normal)
        return Vector2(self.x - d * normal.x, self.y - d * normal.y)

    def rotate(self, angle: float) -> Vector2:
        """Rotate the vector counter-clockwise by *angle* radians."""
        c = math.cos(angle)
        s = math.sin(angle)
        return Vector2(self.x * c - self.y * s, self.x * s + self.y * c)

    def perpendicular(self) -> Vector2:
        """Return a vector perpendicular to this one (rotated 90° CCW)."""
        return Vector2(-self.y, self.x)

    def clamp_magnitude(self, max_magnitude: float) -> Vector2:
        """Return a vector in the same direction clamped to *max_magnitude*."""
        if max_magnitude < 0:
            raise ValueError("max_magnitude must be non-negative")
        mag_sq = self.magnitude_squared
        if mag_sq <= max_magnitude * max_magnitude:
            return Vector2(self.x, self.y)
        mag = math.sqrt(mag_sq)
        scale = max_magnitude / mag
        return Vector2(self.x * scale, self.y * scale)

    def lerp(self, other: Vector2, t: float) -> Vector2:
        """Linear interpolation between *self* and *other*.

        Args:
            other: Target vector.
            t: Interpolation parameter (0 → self, 1 → other).
        """
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )

    # -- Arithmetic operators ------------------------------------------------
    def __add__(self, other: object) -> Vector2:
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other: object) -> Vector2:
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        return NotImplemented

    @overload
    def __mul__(self, other: float) -> Vector2: ...
    @overload
    def __mul__(self, other: int) -> Vector2: ...

    def __mul__(self, other: object) -> Vector2:
        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)
        return NotImplemented

    def __rmul__(self, other: object) -> Vector2:
        return self.__mul__(other)

    def __truediv__(self, other: object) -> Vector2:
        if isinstance(other, (int, float)):
            if abs(other) < EPSILON:
                raise ZeroDivisionError("Cannot divide vector by zero.")
            inv = 1.0 / other
            return Vector2(self.x * inv, self.y * inv)
        return NotImplemented

    def __neg__(self) -> Vector2:
        return Vector2(-self.x, -self.y)

    def __pos__(self) -> Vector2:
        return Vector2(self.x, self.y)

    def __abs__(self) -> float:
        return self.magnitude

    # -- Comparison ----------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector2):
            return abs(self.x - other.x) < EPSILON and abs(self.y - other.y) < EPSILON
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result  # type: ignore[return-value]
        return not result

    def __hash__(self) -> int:
        # Round to avoid hash inconsistency with tolerance-based __eq__
        return hash((round(self.x, 8), round(self.y, 8)))

    def close_to(self, other: Vector2, tolerance: float = 1e-6) -> bool:
        """Check if two vectors are component-wise within *tolerance*."""
        return abs(self.x - other.x) < tolerance and abs(self.y - other.y) < tolerance

    # -- Iteration / indexing ------------------------------------------------
    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def __len__(self) -> int:
        return 2

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError(f"Vector2 index out of range: {index}")

    # -- Representation ------------------------------------------------------
    def __repr__(self) -> str:
        return f"Vector2({self.x:.6g}, {self.y:.6g})"

    def __str__(self) -> str:
        return f"({self.x:.4g}, {self.y:.4g})"

    def __bool__(self) -> bool:
        return not self.is_zero

    # -- Copy ----------------------------------------------------------------
    def __copy__(self) -> Vector2:
        return Vector2(self.x, self.y)

    def __deepcopy__(self, memo: dict) -> Vector2:
        return Vector2(self.x, self.y)


# ===========================================================================
#  Vector3
# ===========================================================================
class Vector3:
    """Immutable 3D vector for physics calculations.

    All arithmetic operations return **new** Vector3 instances.

    Attributes:
        x: The x component.
        y: The y component.
        z: The z component.
    """

    __slots__ = ("x", "y", "z")

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        object.__setattr__(self, "x", float(x))
        object.__setattr__(self, "y", float(y))
        object.__setattr__(self, "z", float(z))

    # -- Immutability --------------------------------------------------------
    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"Vector3 is immutable; cannot set '{name}'")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"Vector3 is immutable; cannot delete '{name}'")

    # -- Factory methods -----------------------------------------------------
    @classmethod
    def zero(cls) -> Vector3:
        """Return the zero vector (0, 0, 0)."""
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def one(cls) -> Vector3:
        """Return the unit-one vector (1, 1, 1)."""
        return cls(1.0, 1.0, 1.0)

    @classmethod
    def unit_x(cls) -> Vector3:
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def unit_y(cls) -> Vector3:
        return cls(0.0, 1.0, 0.0)

    @classmethod
    def unit_z(cls) -> Vector3:
        return cls(0.0, 0.0, 1.0)

    @classmethod
    def from_array(cls, arr: NDArray[np.floating] | list[float] | tuple[float, ...]) -> Vector3:
        """Create a Vector3 from a numpy array, list, or tuple."""
        return cls(float(arr[0]), float(arr[1]), float(arr[2]))

    # -- Conversion ----------------------------------------------------------
    def to_array(self) -> NDArray[np.float64]:
        """Convert to a numpy array [x, y, z]."""
        return np.array([self.x, self.y, self.z], dtype=np.float64)

    def to_tuple(self) -> tuple[float, float, float]:
        """Convert to an (x, y, z) tuple."""
        return (self.x, self.y, self.z)

    def to_vector2(self) -> Vector2:
        """Project down to a Vector2, discarding the z component."""
        return Vector2(self.x, self.y)

    # -- Properties ----------------------------------------------------------
    @property
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    @property
    def magnitude_squared(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

    @property
    def is_zero(self) -> bool:
        return abs(self.x) < EPSILON and abs(self.y) < EPSILON and abs(self.z) < EPSILON

    # -- Core operations -----------------------------------------------------
    def normalize(self) -> Vector3:
        """Return the unit vector in the same direction."""
        mag = self.magnitude
        if mag < EPSILON:
            return Vector3.zero()
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    def dot(self, other: Vector3) -> float:
        """Scalar dot product: a · b."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3) -> Vector3:
        """3D cross product: a × b.

        Returns a vector perpendicular to both *self* and *other*.
        """
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def distance_to(self, other: Vector3) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def distance_squared_to(self, other: Vector3) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return dx * dx + dy * dy + dz * dz

    def angle_between(self, other: Vector3) -> float:
        """Unsigned angle between two 3D vectors in radians [0, π]."""
        d = self.magnitude * other.magnitude
        if d < EPSILON:
            raise ValueError("Cannot compute angle with a zero-length vector.")
        cos_val = max(-1.0, min(1.0, self.dot(other) / d))
        return math.acos(cos_val)

    def project_onto(self, other: Vector3) -> Vector3:
        """Vector projection of *self* onto *other*."""
        denom = other.magnitude_squared
        if denom < EPSILON:
            return Vector3.zero()
        scalar = self.dot(other) / denom
        return Vector3(other.x * scalar, other.y * scalar, other.z * scalar)

    def reject_from(self, other: Vector3) -> Vector3:
        """Component of *self* perpendicular to *other*."""
        return self - self.project_onto(other)

    def reflect(self, normal: Vector3) -> Vector3:
        """Reflect this vector about the given normal."""
        d = 2.0 * self.dot(normal)
        return Vector3(self.x - d * normal.x, self.y - d * normal.y, self.z - d * normal.z)

    def clamp_magnitude(self, max_magnitude: float) -> Vector3:
        """Return a vector clamped to *max_magnitude*."""
        if max_magnitude < 0:
            raise ValueError("max_magnitude must be non-negative")
        mag_sq = self.magnitude_squared
        if mag_sq <= max_magnitude * max_magnitude:
            return Vector3(self.x, self.y, self.z)
        mag = math.sqrt(mag_sq)
        scale = max_magnitude / mag
        return Vector3(self.x * scale, self.y * scale, self.z * scale)

    def lerp(self, other: Vector3, t: float) -> Vector3:
        """Linear interpolation between *self* and *other*."""
        return Vector3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
        )

    # -- Arithmetic operators ------------------------------------------------
    def __add__(self, other: object) -> Vector3:
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented

    def __sub__(self, other: object) -> Vector3:
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        return NotImplemented

    @overload
    def __mul__(self, other: float) -> Vector3: ...
    @overload
    def __mul__(self, other: int) -> Vector3: ...

    def __mul__(self, other: object) -> Vector3:
        if isinstance(other, (int, float)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        return NotImplemented

    def __rmul__(self, other: object) -> Vector3:
        return self.__mul__(other)

    def __truediv__(self, other: object) -> Vector3:
        if isinstance(other, (int, float)):
            if abs(other) < EPSILON:
                raise ZeroDivisionError("Cannot divide vector by zero.")
            inv = 1.0 / other
            return Vector3(self.x * inv, self.y * inv, self.z * inv)
        return NotImplemented

    def __neg__(self) -> Vector3:
        return Vector3(-self.x, -self.y, -self.z)

    def __pos__(self) -> Vector3:
        return Vector3(self.x, self.y, self.z)

    def __abs__(self) -> float:
        return self.magnitude

    # -- Comparison ----------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector3):
            return (
                abs(self.x - other.x) < EPSILON
                and abs(self.y - other.y) < EPSILON
                and abs(self.z - other.z) < EPSILON
            )
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result  # type: ignore[return-value]
        return not result

    def __hash__(self) -> int:
        return hash((round(self.x, 8), round(self.y, 8), round(self.z, 8)))

    def close_to(self, other: Vector3, tolerance: float = 1e-6) -> bool:
        """Check if two vectors are component-wise within *tolerance*."""
        return (
            abs(self.x - other.x) < tolerance
            and abs(self.y - other.y) < tolerance
            and abs(self.z - other.z) < tolerance
        )

    # -- Iteration / indexing ------------------------------------------------
    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y
        yield self.z

    def __len__(self) -> int:
        return 3

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        if index == 2:
            return self.z
        raise IndexError(f"Vector3 index out of range: {index}")

    # -- Representation ------------------------------------------------------
    def __repr__(self) -> str:
        return f"Vector3({self.x:.6g}, {self.y:.6g}, {self.z:.6g})"

    def __str__(self) -> str:
        return f"({self.x:.4g}, {self.y:.4g}, {self.z:.4g})"

    def __bool__(self) -> bool:
        return not self.is_zero

    # -- Copy ----------------------------------------------------------------
    def __copy__(self) -> Vector3:
        return Vector3(self.x, self.y, self.z)

    def __deepcopy__(self, memo: dict) -> Vector3:
        return Vector3(self.x, self.y, self.z)
