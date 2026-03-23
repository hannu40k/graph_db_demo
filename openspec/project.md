# Project Context

## Purpose
A CLI + REST API application for parsing directed weighted graphs from XML files, storing them in PostgreSQL, and answering path-finding queries (all paths via DFS, cheapest path via Dijkstra) against the stored graphs.

## Tech Stack
- Python 3.12.3
- FastAPI (REST API framework)
- SQLModel (ORM for database access)
- Pydantic (request/response schemas, JSON serialization)
- PostgreSQL (database, runs in Docker)
- Alembic (database migrations)
- Click (CLI framework)
- lxml (XML parsing with `etree.iterparse` for large files)
- networkx (graph algorithms: DFS for all paths, Dijkstra for cheapest path)
- uv (Python project management)
- ruff (linting)
- ty (type checking)
- pytest (testing)

## Project Conventions

### Code Style
- Type hints required throughout
- Linting via `ruff`, type checking via `ty`
- Pydantic models for all API request/response schemas
- SQLModel models for all database tables
- Domain types (Graph, Node, Edge) separate from DB models

### Architecture Patterns
- **Service layer**: Business logic in `app/services/` (e.g., `GraphService`), receives DB session as constructor parameter
- **Modular structure**: CLI tools in `app/cli/`, services in `app/services/`, DB models in `app/models.py`, schemas in `app/schemas.py`, domain types in `app/types.py`
- **Configuration**: TOML config file (`config.toml`) with environment variable overrides (`APP_DB_*`)
- **Database access**: SQLModel ORM for Python code; raw SQL for the cycle-detection CLI tool
- **XML parsing**: `lxml.etree.iterparse` for streaming large files; validation happens during iteration

### Testing Strategy
- All tests live in a top-level `tests/` directory mirroring the source tree (e.g. `app/services/graph_service.py` → `tests/app/services/test_graph_service.py`)
- Shared fixtures (DB engine, session, TestClient) are defined in `tests/conftest.py`
- Functional API tests hit a real PostgreSQL test database (`graphdb_test`)
- CLI and parser unit tests run without a database
- Each XML validation rule must have at least one test case
- Explicit test cases for tricky Pydantic serialization (e.g., `path: list[str] | bool`)

### Quality Gates

Before completing any task or change request, always run and fix all of the following:

```bash
uv run ruff check app      # linting
uv run ty check app        # type checking
uv run pytest              # tests
```

All checks must pass. Fix any errors before declaring the task done.

### Git Workflow
- Feature branches with pull requests

## Domain Context
- Graphs are directed and weighted (edges have a non-negative `cost`, defaulting to 0)
- Graphs can contain self-loops, but self-loops are excluded from path results
- The `POST /query/{graph_id}` endpoint accepts multiple queries (paths/cheapest) in one request
- `cheapest.path` returns `false` (JSON boolean) when no path exists
- Cheapest path ties broken by: lowest cost → fewest nodes → first found
- If start == end for cheapest path, return `["a"]`
- Node and edge IDs are scoped per graph (composite primary keys)

## Important Constraints
- Python 3.12.3 specifically
- All other packages pinned to latest stable versions
- PostgreSQL runs in Docker (via docker-compose)
- XML `<nodes>` group must appear before `<edges>` group
- XML `<edges>` contains `<node>` elements (not `<edge>`), representing edges
- No authentication on the API endpoint

## External Dependencies
- PostgreSQL via Docker Compose (port 5432, db: `graphdb`, user: `graphuser`)
- Test database: `graphdb_test` (created manually via `docker compose exec`)
