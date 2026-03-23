## Execution Order

Tasks are grouped by dependency. Groups must be completed in order (1 before 2, etc.). Within a group, items can be parallelized unless noted.

## 1. Project Setup
- [x] 1.1 Create `pyproject.toml` with all dependencies pinned to latest stable: fastapi, sqlmodel, pydantic, networkx, lxml, click, alembic, psycopg2-binary, uvicorn, pytest, httpx, ruff, ty
- [x] 1.2 Initialize uv project (`uv sync`) and verify lock file
- [x] 1.3 Configure ruff and ty settings in `pyproject.toml`
- [x] 1.4 Create `docker-compose.yml` for PostgreSQL container
- [x] 1.5 Add `__init__.py` files to `app/`, `app/services/`, `app/tests/`, `app/cli/`

## 2. Database Layer (depends on: 1)
- [x] 2.1 Define SQLModel models in `app/models.py`: `GraphDB`, `NodeDB`, `EdgeDB` with composite primary keys via `__table_args__` and composite foreign keys
- [x] 2.2 Implement `app/db.py`: engine creation from config, session factory (`get_session` generator), FastAPI `Depends` wrapper
- [x] 2.3 Set up Alembic: `alembic init`, configure `env.py` to import SQLModel metadata, set `sqlalchemy.url` from config
- [x] 2.4 Generate initial Alembic migration from SQLModel models

## 3. Schema Layer (depends on: 1; can parallel with 2)
- [x] 3.1 Define Pydantic request schemas in `app/schemas.py`: `PathQuery`, `CheapestQuery`, `QueryItem` (union discriminator), `QueryRequest`
- [x] 3.2 Define Pydantic response schemas: `NodePaths`, `CheapestPath` (with `path: list[str] | bool`), `AnswerItem`, `QueryResponse`
- [x] 3.3 Handle `from` keyword aliasing via Pydantic `Field(alias="from")` and `populate_by_name=True`
- [x] 3.4 Add Pydantic validator for `CheapestPath.path` to ensure `False` serialization (not `None`)

## 4. Service Layer (depends on: 2, 3)
- [x] 4.1 Implement `GraphService.__init__(self, session: Session)` and `get_graph(graph_id: str)` — fetch graph with eagerly loaded nodes and edges
- [x] 4.2 Implement helper method to build `networkx.DiGraph` from graph nodes/edges with `cost` as edge weight
- [x] 4.3 Implement `get_paths(graph, start, end) -> NodePaths` using `networkx.all_simple_paths` (DFS)
- [x] 4.4 Implement `get_cheapest_path(graph, start, end) -> CheapestPath` using `networkx.all_shortest_paths` with Dijkstra + fewest-nodes tiebreaker
- [x] 4.5 Handle edge cases: start==end returns `[start]`, no path returns `path=False`, self-loops excluded from all-paths results

## 5. API Layer (depends on: 4)
- [x] 5.1 Create FastAPI app in `app/main.py` with lifespan or startup
- [x] 5.2 Implement `POST /query/{graph_id}` endpoint: validate request, delegate to GraphService, return structured response
- [x] 5.3 Return HTTP 404 with detail message when graph_id not found

## 6. Tests (depends on: 5)
- [x] 6.1 Create `app/tests/conftest.py`: test DB engine, session fixtures, TestClient with dependency override, seed helper to insert sample graph data
- [x] 6.2 Write `app/tests/test_schemas.py`: test `CheapestPath` serialization for `path: list[str] | bool` (both `False` and valid list cases), test `from` alias serialization
- [x] 6.3 Write `app/tests/test_graph_service.py`: unit tests for `get_paths` (multiple paths, no path, self-loop exclusion) and `get_cheapest_path` (basic, tiebreaker by fewest nodes, no path returns false, start==end)
- [x] 6.4 Write `app/tests/test_api.py`: functional tests calling `POST /query/{graph_id}` with sample_graph_1 data and verifying against expected output
- [x] 6.5 Write `app/tests/test_api.py`: functional test with sample_graph_3 data (equal-cost tiebreaker scenario)
- [x] 6.6 Write `app/tests/test_api.py`: functional test for 404 on non-existent graph

## 7. Documentation (depends on: 6)
- [x] 7.1 Write `README.md` with: project setup (uv), Docker PostgreSQL, Alembic migration commands, running the API, running tests, seeding database with sample data
