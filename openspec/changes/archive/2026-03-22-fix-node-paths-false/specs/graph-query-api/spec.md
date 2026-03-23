## MODIFIED Requirements
### Requirement: All Paths Query
The system SHALL compute all simple paths between two nodes in a directed weighted graph using Depth-First Search (DFS). Self-loops SHALL NOT appear in path results. When no paths exist between the requested nodes, the `paths` field SHALL be the boolean value `false`, not an empty list.

#### Scenario: Multiple paths exist
- **WHEN** a `paths` query requests paths from (example request) "a" to "e" in sample_graph_1 (edges: a->e, a->b, b->e, c->d, a->a)
- **THEN** the result contains `paths: [["a","b","e"], ["a","e"]]`

#### Scenario: No path exists between disconnected nodes
- **WHEN** a `paths` query requests paths between nodes with no connecting route
- **THEN** the result contains `paths: false` (JSON boolean, not `[]`)

#### Scenario: Self-loops excluded
- **WHEN** a graph contains a self-loop (e.g., a->a) and paths from "a" are requested
- **THEN** the self-loop does not appear as a path in the results

## MODIFIED Requirements
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
