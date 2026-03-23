## 1. Schema
- [x] 1.1 Refactor `QueryItem` in `app/schemas.py` to enforce mutual exclusion of `paths` and `cheapest` — evaluate discriminated union vs `@model_validator`; prefer discriminated union if it produces a clean OpenAPI schema
- [x] 1.2 Ensure the updated `QueryItem` also rejects query items where **neither** `paths` nor `cheapest` is set (empty query item)

## 2. Endpoint cleanup
- [x] 2.1 Remove the `# TODO CLAUDE FIX` comment block at `app/main.py:23–41` (including the illustrative docstring showing the bad OpenAPI example) after validation is in the schema

## 3. Tests
- [x] 3.1 Add test in `app/tests/test_api.py` asserting HTTP 422 is returned when a query item contains both `paths` and `cheapest` keys
- [x] 3.2 Add test in `app/tests/test_api.py` asserting HTTP 422 is returned when a query item contains neither `paths` nor `cheapest` (empty object `{}`)
