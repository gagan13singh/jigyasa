"""
Example 09: Scientia Physics REST Microservice (FastAPI)
========================================================

Standalone HTTP REST API microservice for Scientia platform.
Provides endpoints for Course Embeds, DPA Problem Solvers, and Knowledge Graph.

To run:
    pip install fastapi uvicorn
    python examples/09_scientia_fastapi_microservice.py
"""

from __future__ import annotations

from typing import Any

from physengine import ProblemSpec, ScientiaPhysicsService

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
except ImportError:
    FastAPI = None  # type: ignore


if FastAPI is not None:
    app = FastAPI(
        title="Scientia Physics Service (Jigyasa)",
        version="1.0.0",
        description="Renderer-Agnostic Physics Solver & Simulation Kernel for Scientia Learning Platform",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    service = ScientiaPhysicsService()

    class DPASolveRequest(BaseModel):
        problem_id: str = "dpa-001"
        raw_question: str = ""
        system_type: str = "block_horizontal"
        parameters: dict[str, float] = {}
        target_unknown: str = "acceleration"

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "service": "Scientia Physics Service (Jigyasa)",
            "status": "online",
            "docs": "/docs",
        }

    @app.get("/api/v1/simulations")
    def list_simulations(chapter: str | None = None) -> list[dict[str, Any]]:
        if chapter:
            return service.get_simulations_for_chapter(chapter)
        return service.get_catalog()

    @app.get("/api/v1/simulations/{sim_id}")
    def get_simulation(sim_id: str) -> dict[str, Any]:
        sim = service.get_simulation_metadata(sim_id)
        if not sim:
            raise HTTPException(status_code=404, detail=f"Simulation '{sim_id}' not found")
        return sim

    @app.get("/api/v1/courses/embed/{sim_id}")
    def get_course_embed_card(sim_id: str) -> dict[str, Any]:
        card = service.generate_lesson_embed_card(sim_id)
        if "error" in card:
            raise HTTPException(status_code=404, detail=card["error"])
        return card

    @app.post("/api/v1/dpa/solve")
    def solve_dpa_problem(req: DPASolveRequest) -> dict[str, Any]:
        problem = ProblemSpec.from_dict(req.model_dump())
        solution = service.solve_and_visualize(problem)
        concepts = service.get_concepts_for_dpa(problem)
        return {
            "solution": solution.to_dict(),
            "suggested_concepts": concepts,
        }

    @app.get("/api/v1/knowledge-graph")
    def get_knowledge_graph() -> dict[str, Any]:
        return service.knowledge_graph.export_graph()


def main() -> None:
    if FastAPI is None:
        print("To run the Scientia Physics REST Microservice, please install fastapi & uvicorn:")
        print("    pip install fastapi uvicorn")
        print("\nUsing in-process ScientiaPhysicsService directly instead...")
        srv = ScientiaPhysicsService()
        print(f"Catalog contains {len(srv.get_catalog())} registered curriculum simulations.")
        return

    print("🚀 Starting Scientia Physics Service on http://127.0.0.1:8080 ...")
    uvicorn.run("09_scientia_fastapi_microservice:app", host="127.0.0.1", port=8080, reload=True)


if __name__ == "__main__":
    main()
