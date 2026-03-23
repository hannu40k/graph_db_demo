## Context
Greenfield FastAPI backend for querying directed weighted graphs stored in PostgreSQL. Must be modular so CLI components (Components 2, 3) can reuse DB models, session handling, and services. All app files exist as empty stubs.

## Goals / Non-Goals
- Goals: Working `POST /query/{graph_id}` endpoint, shared DB layer, clean separation of concerns, comprehensive tests
- Non-Goals: Authentication, rate limiting, async DB access, CLI components (separate changes)

## Decisions

### Pydantic schemas in `app/schemas.py`
API request/response types are distinct from SQLModel DB types. A dedicated file prevents circular imports and keeps `models.py` focused on DB concerns. CLI components will import from `models.py` for DB access.

### SQLModel composite keys via `sa_column` and `__table_args__`
SQLModel doesn't natively support composite primary keys. Use `sa_column=Column(...)` with SQLAlchemy primitives for the `node` and `edge` tables. Define `__table_args__` for composite PKs and composite FKs.

### `path: list[str] | bool` serialization
Define `CheapestPath.path` as `list[str] | bool`. Use a Pydantic model validator to ensure `False` (not `None` or `[]`) is returned when no path exists. Explicit test case required per design.md spec.

### `from` field aliasing
"from" is a Python reserved word. Use Pydantic field alias: `from_: str = Field(alias="from", serialization_alias="from")` with `model_config = ConfigDict(populate_by_name=True)`.

### GraphService design
- `__init__(self, session: Session)` for DB access methods (`get_graph`, `insert_graph`)
- `get_paths(graph, start, end)` and `get_cheapest_path(graph, start, end)` take graph data as parameters (no DB access needed), making them unit-testable without a database

### networkx graph construction
Build a `networkx.DiGraph` from the edge list. Store `cost` as edge weight attribute. This conversion happens inside GraphService when processing queries.

### Algorithm choices
- **All paths**: `networkx.all_simple_paths(G, start, end)` — DFS-based, simple paths naturally exclude self-loops (no revisits)
- **Cheapest path**: `networkx.all_shortest_paths(G, start, end, weight='cost')` returns all minimum-cost paths; pick `min(paths, key=len)` for the fewest-nodes tiebreaker. Wrap in try/except for `NetworkXNoPath`. For start==end, return `[start]` directly.

### Test database strategy
Use a test PostgreSQL instance (same Docker setup). Create/drop a test database per test session via pytest fixtures. Use SQLModel `create_all` for schema setup. Functional tests use FastAPI `TestClient` with dependency override for DB session.

### Project file layout
```
app/
├── __init__.py
├── db.py                  # get_engine(), get_session(), FastAPI Depends
├── main.py                # FastAPI app, POST /query/{graph_id}
├── models.py              # SQLModel: GraphDB, NodeDB, EdgeDB
├── schemas.py             # Pydantic: request/response + domain types
├── services/
│   ├── __init__.py
│   └── graph_service.py   # GraphService class
└── tests/
    ├── __init__.py
    ├── conftest.py         # DB fixtures, TestClient setup
    ├── test_api.py         # Functional endpoint tests
    ├── test_graph_service.py  # Unit tests for service logic
    └── test_schemas.py     # Pydantic serialization tests
```

## Risks / Trade-offs
- SQLModel composite key handling is verbose — necessary tradeoff for matching the specified schema
- `list[str] | bool` union type requires careful Pydantic configuration — mitigated by explicit test case
- Dijkstra tiebreaker requires enumerating all shortest paths — acceptable for typical graph sizes

## Open Questions
- None blocking for implementation
