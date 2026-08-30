"""
physengine.scientia.knowledge_graph
===================================

Physics Knowledge Graph for Scientia Learning Platform.
Models the relational graph of NCERT/JEE Physics Chapters, Core Concepts,
Governing Formulas, Simulation IDs, and DPA Problem Archetypes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PhysicsConceptNode:
    """A node representing a discrete physical concept in the curriculum."""

    id: str
    name: str
    chapter: str
    class_grade: int
    key_formula: str
    description: str
    simulation_ids: list[str] = field(default_factory=list)
    dpa_system_types: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PhysicsKnowledgeGraph:
    """Graph database mapping physics concepts, formulas, and simulations."""

    def __init__(self) -> None:
        self._nodes: dict[str, PhysicsConceptNode] = {}
        self._populate_knowledge_graph()

    def add_concept(self, node: PhysicsConceptNode) -> None:
        """Register a concept node."""
        self._nodes[node.id] = node

    def get_concept(self, concept_id: str) -> PhysicsConceptNode | None:
        """Retrieve concept node by ID."""
        return self._nodes.get(concept_id)

    def get_concepts_for_chapter(self, chapter: str) -> list[PhysicsConceptNode]:
        """List all concepts belonging to a chapter."""
        chap_lower = chapter.strip().lower()
        return [n for n in self._nodes.values() if chap_lower in n.chapter.lower()]

    def get_simulations_for_concept(self, concept_id: str) -> list[str]:
        """Get all interactive simulation IDs connected to this concept."""
        node = self._nodes.get(concept_id)
        return node.simulation_ids if node else []

    def get_prerequisites(self, concept_id: str) -> list[PhysicsConceptNode]:
        """Get full prerequisite nodes for a given concept."""
        node = self._nodes.get(concept_id)
        if not node:
            return []
        return [self._nodes[p] for p in node.prerequisites if p in self._nodes]

    def get_dpa_concepts(self, system_type: str) -> list[PhysicsConceptNode]:
        """Find concepts exercised by a specific DPA system type."""
        return [n for n in self._nodes.values() if system_type in n.dpa_system_types]

    def export_graph(self) -> dict[str, Any]:
        """Export the full graph topology as JSON-serializable dictionary."""
        return {
            "concepts": [n.to_dict() for n in self._nodes.values()],
            "total_nodes": len(self._nodes),
        }

    def to_json(self, indent: int = 2) -> str:
        """Export graph as formatted JSON."""
        return json.dumps(self.export_graph(), indent=indent)

    def _populate_knowledge_graph(self) -> None:
        """Build the default NCERT Class 11 Physics Knowledge Graph."""
        concepts = [
            PhysicsConceptNode(
                id="newton_second_law",
                name="Newton's Second Law of Motion",
                chapter="Laws of Motion",
                class_grade=11,
                key_formula=r"\vec{F} = m\vec{a}",
                description="The rate of change of momentum is proportional to applied net force.",
                simulation_ids=["newton-second-law"],
                dpa_system_types=["block_horizontal", "block_incline", "two_body_pulley"],
                prerequisites=["kinematics_acceleration", "momentum"],
                related_concepts=["fbd", "static_friction", "kinetic_friction"],
            ),
            PhysicsConceptNode(
                id="fbd",
                name="Free Body Diagram & Normal Force",
                chapter="Laws of Motion",
                class_grade=11,
                key_formula=r"\Sigma \vec{F} = 0 \implies N = mg",
                description="Isolating bodies to resolve orthogonal contact and field forces.",
                simulation_ids=["newton-second-law", "static-friction", "angle-of-repose"],
                dpa_system_types=["block_horizontal", "block_incline", "two_body_pulley"],
                prerequisites=["vector_resolution"],
                related_concepts=["newton_second_law", "static_friction"],
            ),
            PhysicsConceptNode(
                id="static_friction",
                name="Limiting Static Friction",
                chapter="Laws of Motion",
                class_grade=11,
                key_formula=r"f_s \le f_{\max} = \mu_s N",
                description="Self-adjusting friction opposing impending relative motion up to limiting threshold.",
                simulation_ids=["static-friction", "angle-of-repose"],
                dpa_system_types=["block_horizontal", "block_incline"],
                prerequisites=["newton_second_law", "fbd"],
                related_concepts=["kinetic_friction", "angle_of_repose"],
            ),
            PhysicsConceptNode(
                id="kinetic_friction",
                name="Kinetic Friction",
                chapter="Laws of Motion",
                class_grade=11,
                key_formula=r"f_k = \mu_k N",
                description="Constant opposing force acting during relative sliding contact.",
                simulation_ids=["static-friction", "incline-acceleration"],
                dpa_system_types=["block_horizontal", "block_incline"],
                prerequisites=["static_friction"],
                related_concepts=["work_energy_theorem"],
            ),
            PhysicsConceptNode(
                id="angle_of_repose",
                name="Angle of Repose & Inclines",
                chapter="Laws of Motion",
                class_grade=11,
                key_formula=r"\tan\theta_r = \mu_s",
                description="Maximum slope angle at which a body remains in static equilibrium on an inclined plane.",
                simulation_ids=["angle-of-repose", "incline-acceleration"],
                dpa_system_types=["block_incline"],
                prerequisites=["static_friction", "fbd"],
                related_concepts=["kinetic_friction"],
            ),
            PhysicsConceptNode(
                id="centripetal_force",
                name="Centripetal Force & Acceleration",
                chapter="Laws of Motion",
                class_grade=11,
                key_formula=r"F_c = \frac{m v^2}{R}",
                description="Inward radial force necessary to maintain uniform circular motion.",
                simulation_ids=[
                    "centripetal-force",
                    "banking-frictionless",
                    "banking-with-friction",
                ],
                dpa_system_types=["circular_banking", "vertical_circle"],
                prerequisites=["newton_second_law", "circular_kinematics"],
                related_concepts=["banking_of_roads"],
            ),
            PhysicsConceptNode(
                id="banking_of_roads",
                name="Banking of Curved Roads",
                chapter="Laws of Motion",
                class_grade=11,
                key_formula=r"v_{\text{opt}} = \sqrt{Rg\tan\theta}",
                description="Super-elevation of outer road edge to provide centripetal force via normal reaction.",
                simulation_ids=["banking-frictionless", "banking-with-friction"],
                dpa_system_types=["circular_banking"],
                prerequisites=["centripetal_force", "fbd", "static_friction"],
                related_concepts=["safe_speed_envelope"],
            ),
            PhysicsConceptNode(
                id="work_energy_theorem",
                name="Work-Energy Theorem",
                chapter="Work, Energy and Power",
                class_grade=11,
                key_formula=r"W_{\text{net}} = \Delta K",
                description="Net work done by all acting forces equals the change in kinetic energy.",
                simulation_ids=["work-energy-theorem"],
                dpa_system_types=["block_horizontal", "block_incline", "spring_mass"],
                prerequisites=["newton_second_law", "kinetic_energy"],
                related_concepts=["potential_energy", "conservation_of_energy"],
            ),
            PhysicsConceptNode(
                id="spring_oscillator",
                name="Elastic Potential Energy & Hooke's Law",
                chapter="Work, Energy and Power",
                class_grade=11,
                key_formula=r"U = \frac{1}{2}kx^2, \quad F = -kx",
                description="Restoring force proportional to displacement and stored elastic strain energy.",
                simulation_ids=["spring-potential-energy"],
                dpa_system_types=["spring_mass"],
                prerequisites=["work_energy_theorem"],
                related_concepts=["shm"],
            ),
            PhysicsConceptNode(
                id="momentum_conservation",
                name="Conservation of Linear Momentum",
                chapter="Laws of Motion",
                class_grade=11,
                key_formula=r"\Sigma \vec{p}_i = \Sigma \vec{p}_f",
                description="Total linear momentum of an isolated system is invariant in time.",
                simulation_ids=["momentum-conservation", "elastic-collision-1d"],
                dpa_system_types=["collision_1d"],
                prerequisites=["newton_third_law", "impulse_momentum"],
                related_concepts=["elastic_collision"],
            ),
            PhysicsConceptNode(
                id="projectile_motion",
                name="2D Projectile Motion",
                chapter="Motion in a Plane",
                class_grade=11,
                key_formula=r"R = \frac{u^2\sin 2\theta}{g}, \quad H = \frac{u^2\sin^2\theta}{2g}",
                description="Two-dimensional motion under uniform gravitational acceleration forming a parabolic trajectory.",
                simulation_ids=["projectile-motion"],
                dpa_system_types=["projectile"],
                prerequisites=["equations_of_motion", "vector_resolution"],
                related_concepts=["flight_time", "maximum_range"],
            ),
        ]

        for c in concepts:
            self.add_concept(c)
