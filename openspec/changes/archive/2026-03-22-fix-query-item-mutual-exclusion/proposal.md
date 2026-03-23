# Change: Enforce mutual exclusion of paths/cheapest in QueryItem

## Why
`QueryItem` currently allows both `paths` and `cheapest` to be set simultaneously without any validation error. The design spec requires that each query item contains **one or the other, but not both**. Additionally, the auto-generated OpenAPI/Swagger schema currently shows an example request containing both keys in the same query item, which is misleading. Using a Pydantic discriminated union (or model validator) will enforce mutual exclusion both at parse time and in the OpenAPI schema example.

Source: `app/main.py:23` — `# TODO CLAUDE FIX: Add validation that a single query item only contains a "paths" or a "cheapest" key, but not both...`

## What Changes
- **`app/schemas.py`**: Refactor `QueryItem` to enforce exactly one of `paths`/`cheapest`:
  - Preferred approach: Use a Pydantic discriminated union so OpenAPI reflects the constraint (e.g. `QueryItem = Annotated[PathsQueryItem | CheapestQueryItem, Field(discriminator=...)]`)
  - Alternative: Add a `@model_validator(mode='after')` to `QueryItem` that raises `ValueError` if both or neither fields are set
- **`app/main.py:23–41`**: Remove the `# TODO CLAUDE FIX` comment and the illustrative docstring block that showed the bad OpenAPI example
- **`app/tests/test_api.py`**: Add test asserting the endpoint returns HTTP 422 when a query item has both `paths` and `cheapest` keys set

## Impact
- Affected specs: `graph-query-api`
- Affected code: `app/schemas.py`, `app/main.py`, `app/tests/test_api.py`
- **BREAKING**: Requests containing both `paths` and `cheapest` in a single query item now return HTTP 422 instead of silently ignoring one
