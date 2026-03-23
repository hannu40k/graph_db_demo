# graph-query-api Specification

## Purpose
TBD - created by archiving change add-web-backend. Update Purpose after archive.
## Requirements
### Requirement: Graph Query Endpoint
The system SHALL expose a `POST /query/{graph_id}` endpoint that accepts a JSON body containing a list of graph queries and returns computed answers. The endpoint is public and requires no authentication.

The system SHALL additionally expose a `POST /query` endpoint (no graph ID) that accepts the same JSON body and executes queries against the most recently inserted graph in the database.

#### Scenario: Successful mixed query
- **WHEN** a valid request with `paths` and `cheapest` queries is sent to `POST /query/{graph_id}` for an existing graph
- **THEN** the response contains an `answers` array with one result per query, in request order

#### Scenario: Graph not found
- **WHEN** a request is sent to `POST /query/{graph_id}` with a `graph_id` that does not exist in the database
- **THEN** the system SHALL return HTTP 404

#### Scenario: Latest graph query — success
- **WHEN** a valid request is sent to `POST /query` and at least one graph exists in the database
- **THEN** the system executes the queries against the graph with the most recent `created_at` timestamp and returns an `answers` array

#### Scenario: Latest graph query — no graphs
- **WHEN** a request is sent to `POST /query` and no graphs exist in the database
- **THEN** the system SHALL return HTTP 404

### Requirement: All Paths Query
The system SHALL compute all simple paths between two nodes in a directed weighted graph using Depth-First Search (DFS). Self-loops SHALL NOT appear in path results.

#### Scenario: Multiple paths exist
- **WHEN** a `paths` query requests paths from (example request) "a" to "e" in sample_graph_1 (edges: a->e, a->b, b->e, c->d, a->a)
- **THEN** the result contains `paths: [["a","b","e"], ["a","e"]]`

#### Scenario: No path exists between disconnected nodes
- **WHEN** a `paths` query requests paths between nodes with no connecting route
- **THEN** the result contains `paths: []`

#### Scenario: Self-loops excluded
- **WHEN** a graph contains a self-loop (e.g., a->a) and paths from "a" are requested
- **THEN** the self-loop does not appear as a path in the results

### Requirement: Cheapest Path Query
The system SHALL compute the cheapest (lowest total edge cost) path between two nodes using Dijkstra's algorithm. When multiple paths share the minimum cost, the path with fewest nodes SHALL be returned. If multiple paths have equal cost and equal node count, the first path found SHALL be returned.

#### Scenario: Single cheapest path
- **WHEN** a `cheapest` query requests the cheapest path from "a" to "e" in sample_graph_1 (a->e costs 42, a->b->e costs 54.2)
- **THEN** the result contains `path: ["a", "e"]`

#### Scenario: Equal cost tiebreaker by fewest nodes
- **WHEN** a `cheapest` query requests the cheapest path from "a" to "e" in sample_graph_3 (three paths all costing 4, with 5, 4, and 3 nodes respectively)
- **THEN** the result contains `path: ["a", "d", "e"]` (the path with fewest nodes)

#### Scenario: No path exists
- **WHEN** a `cheapest` query requests a path between disconnected nodes (e.g., "a" to "h" in sample_graph_1)
- **THEN** the `path` field SHALL be the boolean value `false`, not `null` or an empty list

#### Scenario: Start equals end
- **WHEN** a `cheapest` query has the same node for start and end (e.g., start="a", end="a")
- **THEN** the result contains `path: ["a"]`

### Requirement: Graph Database Schema
The system SHALL store graphs in PostgreSQL using three tables: `graph` (VARCHAR(32) primary key, name, created_at), `node` (composite PK of id + graph_id, name, created_at), `edge` (composite PK of id + graph_id, from_node_id, to_node_id, cost as NUMERIC, created_at). Foreign keys SHALL enforce referential integrity. Migrations SHALL be managed by Alembic.

#### Scenario: Graph with nodes and edges persisted and retrieved
- **WHEN** a graph with nodes and weighted edges is inserted into the database
- **THEN** it can be retrieved by graph_id with all associated nodes and edges intact

### Requirement: API Request Format
The system SHALL accept requests with a `queries` array where each item contains **exactly one** of: a `paths` key or a `cheapest` key. Each key holds an object with `start` and `end` string fields identifying node IDs. A query item with both keys set, or with neither key set, SHALL be rejected with HTTP 422. The API schema (OpenAPI) SHALL reflect this constraint so that generated examples do not show both keys simultaneously.

#### Scenario: Mixed query types in single request
- **WHEN** a request contains both `paths` and `cheapest` query items (one per item)
- **THEN** all queries are processed and answered in order

#### Scenario: Query item with both paths and cheapest rejected
- **WHEN** a request contains a query item with both `paths` and `cheapest` keys set
- **THEN** the system SHALL return HTTP 422 with a descriptive validation error

#### Scenario: Query item with neither key rejected
- **WHEN** a request contains a query item with neither `paths` nor `cheapest` key set
- **THEN** the system SHALL return HTTP 422 with a descriptive validation error

### Requirement: API Response Format
The system SHALL return responses with an `answers` array where each item contains **exactly one** of: a `paths` key (with `from`, `to`, `paths` fields) or a `cheapest` key (with `from`, `to`, `path` fields). The `from`/`to` fields echo the requested start/end nodes. Keys that are absent from the query result SHALL be **omitted** from the answer item — they MUST NOT appear as `null`.

#### Scenario: Response matches request order
- **WHEN** three queries are sent (paths a->e, cheapest a->e, cheapest a->h)
- **THEN** three answers are returned in the same order with matching query types

#### Scenario: Paths-only answer omits cheapest key
- **WHEN** a query item contains only a `paths` query
- **THEN** the corresponding answer item contains a `paths` key and NO `cheapest` key (not even `null`)

#### Scenario: Cheapest-only answer omits paths key
- **WHEN** a query item contains only a `cheapest` query
- **THEN** the corresponding answer item contains a `cheapest` key and NO `paths` key (not even `null`)

### Requirement: Pydantic Union Serialization
The `CheapestPath` response type SHALL correctly serialize the union type `path: list[str] | bool` where boolean `false` represents no path found. The `NodePaths` response type SHALL correctly serialize the union type `paths: list[list[str]] | bool` where boolean `false` represents no paths found.

#### Scenario: CheapestPath.path serializes as false
- **WHEN** no path exists between requested nodes
- **THEN** the JSON output contains `"path": false` (not `null`, not `[]`, not `"false"`)

#### Scenario: CheapestPath.path serializes as list
- **WHEN** a valid path exists between requested nodes
- **THEN** the JSON output contains the path as a list in the format (example) `"path": ["a", "b", "e"]` as a JSON array of strings

#### Scenario: NodePaths.paths serializes as false
- **WHEN** no paths exist between requested nodes
- **THEN** the JSON output contains `"paths": false` (not `null`, not `[]`, not `"false"`)

#### Scenario: NodePaths.paths serializes as list of lists
- **WHEN** valid paths exist between requested nodes
- **THEN** the JSON output contains the paths as a list of lists in the format (example) `"paths": [["a","b","e"], ["a","e"]]`

