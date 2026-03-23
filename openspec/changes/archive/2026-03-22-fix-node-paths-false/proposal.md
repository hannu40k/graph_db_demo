# Change: Fix NodePaths.paths to support boolean false when no paths found

## Why
`NodePaths.paths` is currently typed as `list[list[str]]`, which means it can only serialize as a JSON array. When no valid path exists between two nodes, the design spec requires the value to be the JSON boolean `false` (not `[]`). This is the same pattern already used by `CheapestPath.path: list[str] | bool`. The schema and service must be updated to reflect this, along with the relevant spec, tests, and comments.

Source: `app/schemas.py:37` — `# TODO CLAUDE FIX: If no valid path is not found for the path request, the type of "paths" attribute will be bool, and its value will be false.`

## What Changes
- **`app/schemas.py`**: Change `NodePaths.paths` from `list[list[str]]` to `list[list[str]] | bool`
- **`app/services/graph_service.py`**: Update `get_paths` to return `False` instead of `[]` when no paths found
- **`app/tests/test_schemas.py`**: Add test `test_paths_serializes_as_false_when_no_paths`; update `test_empty_paths` or clarify its intent (empty list is a distinct case from no paths found)
- **`app/tests/test_graph_service.py`**: Update tests that assert `get_paths` returns `[]` for disconnected nodes to assert it returns `False`
- **`app/tests/test_api.py`**: Add/update test asserting the API response contains `paths: false` for disconnected nodes
- **`app/schemas.py:37`**: Remove the TODO CLAUDE FIX comment after fix is applied
- **Spec delta**: Update "All Paths Query" requirement scenario for no-path case

## Impact
- Affected specs: `graph-query-api`
- Affected code: `app/schemas.py`, `app/services/graph_service.py`, `app/tests/test_schemas.py`, `app/tests/test_graph_service.py`, `app/tests/test_api.py`
- **BREAKING**: Changes the serialized JSON value from `[]` to `false` for disconnected-node path queries
