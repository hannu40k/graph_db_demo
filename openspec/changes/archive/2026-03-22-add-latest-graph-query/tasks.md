# Tasks: add-latest-graph-query

## Ordered Work Items

1. - [x] **Add `get_latest_graph` to `GraphService`**
   - Query `GraphDB` ordered by `created_at DESC`, limit 1
   - Return `GraphDB | None`
   - Validation: unit test — returns `None` when no graphs exist, returns the newest graph when multiple exist

2. - [x] **Add `POST /query` route to `app/main.py`**
   - Call `graph_service.get_latest_graph()`
   - Return HTTP 404 with detail `"No graphs in database"` when result is `None`
   - Delegate to same per-query logic as `POST /query/{graph_id}`
   - Validation: functional API test covering success and 404 cases

3. - [x] **Run quality gates**
   - `uv run ruff check app` — passed
   - `uv run ty check app` — pre-existing errors only (none introduced by this change); also fixed pre-existing `[tool.ty]` → `[tool.ty.environment]` config key
   - `uv run pytest` — 72 passed

## Dependencies
- Tasks 1 and 2 are sequential (route depends on service method)
- Task 3 runs after both are done
