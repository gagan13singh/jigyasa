# Contributing to PhysEngine

## Setup

```bash
git clone <repo-url>
cd PhysicsEngine
pip install -e ".[dev]"
```

## Code Style

- **Type hints**: All function signatures must have type annotations
- **Docstrings**: Google-style with Args/Returns/Raises
- **Line length**: 100 characters max
- **Imports**: Use `from __future__ import annotations` in every module
- **Linting**: Run `ruff check src/ tests/`

## Testing

Every feature needs tests:

- **Unit tests** in `tests/unit/` — individual functions and classes
- **Physics tests** in `tests/physics/` — numerical vs analytical validation
- **Integration tests** in `tests/integration/` — full pipeline

```bash
pytest                    # Run all
pytest -x                 # Stop on first failure
pytest --tb=long          # Verbose tracebacks
pytest -k "test_vector"   # Run specific tests
```

## Architecture Rules

1. **Never import rendering libraries** in `src/physengine/` (no manim, matplotlib, etc.)
2. **Forces are pure functions** — `calculate()` returns a Vector2, never mutates state
3. **Vectors are immutable** — operations return new instances
4. **Entity-Component over inheritance** — compose objects from components
5. **State snapshots are frozen** — recording creates deep copies

## Pull Request Checklist

- [ ] Tests pass: `pytest`
- [ ] Lint passes: `ruff check src/ tests/`
- [ ] Docstrings for all public APIs
- [ ] Type hints for all function signatures
- [ ] Updated MEMORY.md if architecture changed
- [ ] Added example if introducing a new feature
