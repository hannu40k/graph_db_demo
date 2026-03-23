## MODIFIED Requirements

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
