# Graph Query API

A FastAPI service that answers path-finding queries against directed weighted graphs stored in PostgreSQL.

## backend_code_challenge_v1.2 requirements / questions

1) JSON parsing and serialization library

Pydantic, because it is tightly coupled with FastAPI, which the backend is based on. It is a good choice anyway due to performance and validation capabilities.

2) Algorithm choices - How I solved "find all paths" and "cheapest path"

Python package NetworkX was used as the technical solution to find all paths and the cheapest path between requested nodes. It is how I would approach a real-world backend problem, i.e. not implement well known algorithms myself.

I did research the most suitable methods to solve the problems, which eventually landed me on the NetworkX package which has implementations for desired algorithms.

- Finding all paths: Use Depth First Search (DFS) (`nx.all_simple_paths`). The optimal solution appears to depend heavily on graph characteristics, but DFS enjoys a position as a standard good starting point. Considering that the task spec is not heavy on details, DFS is a reasonable choice.
- Finding cheapest path: Use Dijkstra's algorithm, since all the weights (`cost` attribute) are non-negative, and it should be the most efficient for the purpose, and it does not revisit already visited nodes. `nx.all_shortest_paths` uses Dijkstra by default.

3) Proposed SQL schema

In file `sql/migration.sql`. Modeled also in `app/models.py`.

4) Find cycles SQL script

In file `sql/find_cycles.sql`.

5) Expose REST API

The FastAPI app in `app/`.

7) Chosen XML parsing library

Chose `lxml`, as it is battle tested industry standard, and has good streaming capabilities for large files.

8) Minimal SQL schema migration / seed

Ran automatically when services start. Can also run the migration manually from `sql/migration.sql`.


## Requirements

- Docker + Docker Compose

## Setup

### 1. Start the application

```bash
docker compose up -d
```

This starts PostgreSQL, runs the SQL migration, and starts the web backend on port 8000.

### 2. Interact with the API

Use any HTTP client (e.g. `curl`) to send requests, or navigate to `http://localhost:8000` for the web UI. Interactive API docs are at `http://localhost:8000/docs`.

### 3. Populate the database with sample data

Build the CLI tool and import sample graphs:

```bash
docker build -f Dockerfile.cli -t parse-graph .
docker run --network host --rm parse-graph --file-path=samples/good/sample_graph_1.xml --insert
docker run --network host --rm parse-graph --file-path=samples/good/sample_graph_3.xml --insert
```

The sample XML files contain graph data with graph IDs `g1` and `g3` (yes, no `g2`). Refer to the sample files for node data.

To parse an XML file from your host machine (rather than the bundled samples inside the container), mount it as a volume:

```bash
docker run --network host --rm -v /path/to/your/file.xml:/data/file.xml parse-graph --file-path=/data/file.xml --insert
```

Replace `/path/to/your/file.xml` with the absolute path on your host. The `-v` flag maps the host file into the container at `/data/file.xml`, which you then reference via `--file-path`.

### 4. Tear down and restart

To remove all containers and volumes (including database data) and start fresh:

```bash
docker compose down -v
docker compose up -d
```

## API Usage

### POST /query

Same as below endpoint, but targets the latest inserted graph (no need to provide graph_id).

### POST /query/{graph_id}

Query a graph for paths between nodes.

**Request body:**
```json
{
  "queries": [
    {"paths": {"start": "a", "end": "e"}},
    {"cheapest": {"start": "a", "end": "e"}}
  ]
}
```

**Response:**
```json
{
  "answers": [
    {"paths": {"from": "a", "to": "e", "paths": [["a", "e"], ["a", "b", "e"]]}},
    {"cheapest": {"from": "a", "to": "e", "path": ["a", "e"]}}
  ]
}
```

- `paths` returns all simple paths (DFS, no revisiting nodes). value is `false` when there are no paths.
- `cheapest` returns the lowest-cost path using Dijkstra; ties broken by fewest nodes
- `cheapest.path` is `false` (JSON boolean) when no path exists

Returns HTTP 404 if the graph_id is not found.

## Testing `find_cycles.sql`

Insert test data and run the cycle-finding script. Replace `<container_name>` with your PostgreSQL container name (find it with `docker ps`):

```bash
cat sql/insert_graph_with_cycles_1.sql | docker exec -i <container_name> psql -U graphuser -d graphdb
cat sql/insert_graph_with_cycles_2.sql | docker exec -i <container_name> psql -U graphuser -d graphdb
cat sql/insert_graph_with_cycles_3.sql | docker exec -i <container_name> psql -U graphuser -d graphdb
cat sql/find_cycles.sql | docker exec -i <container_name> psql -U graphuser -d graphdb
```

> **Note:** By default, `find_cycles.sql` finds cycles in the first graph. To test with other graphs, modify the script manually to change the graph name.

## Running Tests

Run:

```bash
uv run pytest
```

## Project Structure

```
├── app/                          # Main application package
│   ├── main.py                   # FastAPI app, routes, and startup
│   ├── config.py                 # App configuration (from config.toml)
│   ├── db.py                     # Database connection and session management
│   ├── models.py                 # SQLAlchemy ORM models (Graph, Node, Edge)
│   ├── schemas.py                # Pydantic request/response schemas
│   ├── types.py                  # Shared type definitions
│   ├── logging.py                # Structured logging setup
│   ├── cli/
│   │   └── parse_graph.py        # CLI tool for parsing XML graphs and inserting into DB
│   └── services/
│       └── graph_service.py      # Graph query logic (paths, cheapest path via NetworkX)
├── tests/                        # Test suite (mirrors app/ structure)
│   ├── conftest.py               # Shared fixtures (test DB, sample graphs)
│   └── app/
│       ├── test_api.py           # API endpoint tests
│       ├── test_config.py        # Configuration tests
│       ├── test_logging.py       # Logging tests
│       ├── test_schemas.py       # Schema validation tests
│       ├── cli/
│       │   ├── test_parse_graph_cli.py  # CLI integration tests
│       │   └── test_xml_parser.py       # XML parsing unit tests
│       └── services/
│           └── test_graph_service.py    # Graph service tests
├── sql/
│   ├── migration.sql             # Database schema creation
│   ├── find_cycles.sql           # Cycle detection query (recursive CTE)
│   └── insert_graph_with_cycles_*.sql  # Test data for cycle detection
├── alembic/                      # Alembic migration framework
│   └── versions/
│       └── 0001_initial_schema.py
├── samples/
│   ├── good/                     # Valid sample XML graphs and expected I/O
│   └── invalid/                  # Invalid XML files for parser error testing
├── openspec/                     # OpenSpec change management
│   ├── project.md                # Project-level spec overview
│   └── specs/                    # Component specifications
├── config.toml                   # Runtime configuration
├── docker-compose.yml            # PostgreSQL + web backend orchestration
├── Dockerfile                    # Web backend container
├── Dockerfile.cli                # CLI tool container
├── entrypoint.sh                 # Container entrypoint (runs migrations)
└── pyproject.toml                # Python project config (uv, ruff, pytest)
```
