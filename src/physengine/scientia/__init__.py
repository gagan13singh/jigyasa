"""
physengine.scientia
===================

Scientia Integration Layer for PhysEngine (Jigyasa).
Provides Simulation Registry, DPA Structured Problem Solvers,
Physics Knowledge Graph, and the Unified ScientiaPhysicsService Gateway.
"""

from __future__ import annotations

from physengine.scientia.client import ScientiaPhysicsClient
from physengine.scientia.knowledge_graph import (
    PhysicsConceptNode,
    PhysicsKnowledgeGraph,
)
from physengine.scientia.registry import (
    ParameterSchema,
    SimulationMetadata,
    SimulationRegistry,
)
from physengine.scientia.schema import (
    DPASolution,
    DPASolutionStep,
    FBDVectorSpec,
    ForceSpec,
    PhysicsObjectSpec,
    ProblemSpec,
    SimulationSnapshot,
    SystemType,
)
from physengine.scientia.service import ScientiaPhysicsService
from physengine.scientia.solver import ProblemSolver

__all__ = [
    "DPASolution",
    "DPASolutionStep",
    "FBDVectorSpec",
    "ForceSpec",
    "ParameterSchema",
    "PhysicsConceptNode",
    "PhysicsKnowledgeGraph",
    "PhysicsObjectSpec",
    "ProblemSolver",
    "ProblemSpec",
    "ScientiaPhysicsClient",
    "ScientiaPhysicsService",
    "SimulationMetadata",
    "SimulationRegistry",
    "SimulationSnapshot",
    "SystemType",
]
