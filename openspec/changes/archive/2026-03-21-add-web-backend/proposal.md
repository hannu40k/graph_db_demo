# Change: Add FastAPI Web Backend for Graph Queries

## Why
The project needs a REST API that accepts graph path queries (all paths, cheapest path) and returns computed results from directed weighted graph data stored in PostgreSQL. This is Component 1 and establishes the shared foundation (DB models, connection, project config) that CLI components will reuse.

## What Changes
- Create `pyproject.toml` with pinned dependencies and project configuration for uv, ruff, ty
- Define SQLModel database models for graph, node, edge tables (`app/models.py`)
- Implement database connection and session management (`app/db.py`)
- Define Pydantic request/response schemas (`app/schemas.py`)
- Implement GraphService with path-finding business logic using networkx (`app/services/graph_service.py`)
- Create FastAPI application with `POST /query/{graph_id}` endpoint (`app/main.py`)
- Set up Alembic with initial migration (`alembic/`)
- Add unit and functional tests (`app/tests/`)
- Add Docker Compose for PostgreSQL
- Add `README.md` with setup instructions

## Impact
- Affected specs: `graph-query-api` (new capability)
- Affected code: `app/models.py`, `app/db.py`, `app/main.py`, `app/schemas.py`, `app/services/graph_service.py`, `alembic/`, `pyproject.toml`, `docker-compose.yml`
