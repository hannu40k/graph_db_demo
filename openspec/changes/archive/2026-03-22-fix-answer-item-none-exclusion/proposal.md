# Change: Fix AnswerItem to exclude absent query keys from JSON response

## Why
`AnswerItem` has two optional fields: `paths: NodePaths | None` and `cheapest: CheapestPath | None`. When a query item requests only a `paths` query, the answer should contain only the `paths` key — the `cheapest` key must be **absent** from the JSON, not present as `null`. Currently Pydantic serializes both fields, yielding e.g. `{"paths": {...}, "cheapest": null}` when it should yield `{"paths": {...}}`. This mismatch breaks the API contract and the sample output files.

Source: `app/schemas.py:53` — `# TODO CLAUE FIX: If the request query did not include a "cheapest" query at all, the answer section should not include a response for "cheapest" at all (not just a null value, but the answer item for cheapest should be omitted.)`

## What Changes
- **`app/schemas.py`**: Add `model_config = ConfigDict(exclude_none=True)` to `AnswerItem` so that `None`-valued fields are omitted from JSON output
- **`app/schemas.py:53`**: Remove the TODO CLAUDE FIX comment after fix is applied
- **`app/tests/test_schemas.py`**: Add tests verifying that `AnswerItem` with only `paths` set omits the `cheapest` key, and vice versa
- **`app/tests/test_api.py`**: Ensure existing API tests verify no unexpected null keys appear in answer items
- **Spec delta**: Update "API Response Format" requirement to make this behavior explicit

## Impact
- Affected specs: `graph-query-api`
- Affected code: `app/schemas.py`, `app/tests/test_schemas.py`, `app/tests/test_api.py`
- **BREAKING**: Changes serialized output from `{"paths": {...}, "cheapest": null}` to `{"paths": {...}}`
