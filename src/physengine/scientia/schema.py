"""
physengine.scientia.schema
==========================

Data Models and Structured Physics Representation Schema for Scientia DPA
(Dynamic Problem Architecture) & Course Integration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class SystemType(str, Enum):
    """Supported physical system archetypes."""

    BLOCK_HORIZONTAL = "block_horizontal"
    BLOCK_INCLINE = "block_incline"
    TWO_BODY_PULLEY = "two_body_pulley"
    TWO_BODY_TETHER = "two_body_tether"
    PROJECTILE = "projectile"
    CIRCULAR_BANKING = "circular_banking"
    SPRING_MASS = "spring_mass"
    COLLISION_1D = "collision_1d"
    VERTICAL_CIRCLE = "vertical_circle"
    FREE_FALL = "free_fall"


@dataclass
class PhysicsObjectSpec:
    """Specification of an entity/object in the physics problem."""

    name: str
    mass: float
    position: tuple[float, float] = (0.0, 0.0)
    velocity: tuple[float, float] = (0.0, 0.0)
    dimensions: tuple[float, float] = (1.0, 1.0)
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ForceSpec:
    """Specification of an active force in the problem."""

    force_type: str  # "applied_force", "friction", "gravity", "normal", "spring", "tension"
    magnitude: float = 0.0
    direction: tuple[float, float] = (1.0, 0.0)
    coefficient: float = 0.0  # friction coefficient μ or restitution e
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProblemSpec:
    """
    Structured representation of a student DPA problem.
    This intermediate schema decouples LLMs / CMS from numerical physics math.
    """

    problem_id: str
    raw_question: str
    system_type: SystemType
    objects: list[PhysicsObjectSpec] = field(default_factory=list)
    forces: list[ForceSpec] = field(default_factory=list)
    parameters: dict[str, float] = field(default_factory=dict)
    target_unknown: str = (
        "acceleration"  # "acceleration", "normal_force", "friction_force", "time_to_stop", etc.
    )
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["system_type"] = self.system_type.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProblemSpec:
        """Construct ProblemSpec from dictionary."""
        sys_type = SystemType(data.get("system_type", "block_horizontal"))
        objects = [PhysicsObjectSpec(**obj) for obj in data.get("objects", [])]
        forces = [ForceSpec(**f) for f in data.get("forces", [])]
        return cls(
            problem_id=data.get("problem_id", "custom-problem"),
            raw_question=data.get("raw_question", ""),
            system_type=sys_type,
            objects=objects,
            forces=forces,
            parameters=data.get("parameters", {}),
            target_unknown=data.get("target_unknown", "acceleration"),
            tags=data.get("tags", []),
        )


@dataclass
class FBDVectorSpec:
    """Free-Body Diagram force vector specification for UI rendering."""

    name: str
    label_latex: str
    magnitude_n: float
    origin: tuple[float, float]
    vector: tuple[float, float]  # normalized direction * display length
    color: str = "#38bdf8"


@dataclass
class DPASolutionStep:
    """Step in the verified step-by-step mathematical solution."""

    step_number: int
    title: str
    latex_formula: str
    description: str
    values: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationSnapshot:
    """State of simulation at time t."""

    t: float
    entities: dict[str, dict[str, Any]]
    telemetry: dict[str, Any] = field(default_factory=dict)


@dataclass
class DPASolution:
    """
    Combined output of PhysEngine for Scientia:
    Contains verified step-by-step math, FBD vectors, and exact simulation time-series.
    """

    problem_id: str
    system_type: str
    target_unknown: str
    answer_value: float
    answer_unit: str
    answer_latex: str
    steps: list[DPASolutionStep]
    fbd_vectors: list[FBDVectorSpec]
    numerical_results: dict[str, float]
    simulation_timeline: list[dict[str, Any]]
    concepts_used: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "system_type": self.system_type,
            "target_unknown": self.target_unknown,
            "answer_value": self.answer_value,
            "answer_unit": self.answer_unit,
            "answer_latex": self.answer_latex,
            "steps": [asdict(s) for s in self.steps],
            "fbd_vectors": [asdict(v) for v in self.fbd_vectors],
            "numerical_results": self.numerical_results,
            "simulation_timeline": self.simulation_timeline,
            "concepts_used": self.concepts_used,
        }
