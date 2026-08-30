from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure src/ is on sys.path for serverless environments (Vercel)
src_dir = str(Path(__file__).resolve().parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from physengine.scientia.service import ScientiaPhysicsService
from physengine.visualizer.server import get_html_content, run_preset_simulation

app = FastAPI(
    title="Jigyasa — Scientia Physics Engine",
    description="Physics Simulation, DPA Step-by-Step Solver, and Interactive Visualizer API",
    version="1.0.0",
)

# Enable CORS for web apps (e.g. Scientia LMS React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = ScientiaPhysicsService()


@app.get("/", response_class=HTMLResponse)
def home():
    """Serves the interactive 2D & 3D physics visualizer lab."""
    return get_html_content()


@app.get("/health")
@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Jigyasa Physics Engine (Scientia)",
        "version": "1.0.0",
    }


@app.get("/api/catalog")
def get_catalog():
    """List all available simulations mapped to Class 9-12 / JEE / NEET curriculum."""
    return service.get_catalog()


@app.get("/api/manifest")
def get_manifest():
    """Export full Scientia integration manifest and supported systems."""
    return service.export_api_manifest()


@app.get("/api/simulations/{sim_id}")
def get_simulation(sim_id: str):
    """Retrieve metadata and parameters for a specific simulation."""
    sim = service.get_simulation_metadata(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail=f"Simulation '{sim_id}' not found")
    return sim


@app.get("/api/embed/{sim_id}")
def get_embed_card(sim_id: str):
    """Generate embeddable HTML widget card for Scientia Course Notes."""
    return service.generate_lesson_embed_card(sim_id)


@app.post("/api/dpa/solve")
def solve_dpa_problem(problem: dict[str, Any]):
    """
    Solve a structured physics problem with:
    1. Pedagogical step-by-step LaTeX derivation
    2. Free-Body Diagram force vectors
    3. 60 FPS verified numerical trajectory
    """
    try:
        solution = service.solve_and_visualize(problem)
        return solution.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/dpa/concepts")
def get_dpa_concepts(problem: dict[str, Any]):
    """Retrieve relevant physics concept links and recommendations for a problem."""
    try:
        return service.get_concepts_for_dpa(problem)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/simulate")
def simulate(payload: dict[str, Any]):
    """
    Run numerical integration for interactive presets
    (projectile, cliff_projectile, freefall, car_braking, river_swimmer,
     incline, atwood, collision, rolling_race, pendulum, spring, vertical_circle,
     stokes, buoyancy, orbit, cyclotron, electron_deflection, rutherford).
    """
    try:
        preset = payload.get("preset", "projectile")
        return run_preset_simulation(preset, payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
