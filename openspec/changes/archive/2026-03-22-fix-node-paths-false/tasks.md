## 1. Schema
- [x] 1.1 Update `NodePaths.paths` in `app/schemas.py` from `list[list[str]]` to `list[list[str]] | bool`
- [x] 1.2 Add `model_config = ConfigDict(populate_by_name=True)` if not already present (consistent with `CheapestPath`)
- [x] 1.3 Remove the `# TODO CLAUDE FIX` comment at `app/schemas.py:37`

## 2. Service
- [x] 2.1 Update `GraphService.get_paths` in `app/services/graph_service.py` to return `False` (not `[]`) when no paths exist between nodes
- [x] 2.2 Update return type annotation of `get_paths` to reflect `list[list[str]] | bool`

## 3. Tests
- [x] 3.1 Add test `TestNodePathsSerialization.test_paths_serializes_as_false_when_no_paths` in `app/tests/test_schemas.py`
- [x] 3.2 Update or annotate `test_empty_paths` in `app/tests/test_schemas.py` — clarify whether empty list `[]` is still a valid state or should be replaced with `False` (consult service behavior)
- [x] 3.3 Update `app/tests/test_graph_service.py` — any test asserting `get_paths` returns `[]` for disconnected nodes must now assert `False`
- [x] 3.4 Add/update test in `app/tests/test_api.py` asserting `paths: false` in API response for a disconnected-node query
