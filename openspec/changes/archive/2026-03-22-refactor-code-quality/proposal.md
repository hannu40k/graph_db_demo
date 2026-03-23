# Change: Refactor code quality improvements

## Why
Five TODOs left in the codebase signal correctness gaps and maintenance debt: invalid
config values are silently accepted, a redundant log processor adds overhead on every
log call, and repeated query-dispatching logic between two endpoints risks diverging
silently. The remaining issues reduce readability in the XML parser and test fixtures.

## What Changes

Ordered by priority (P1 = highest):

- **P1 – Config value validation** (`app/config.py`): Replace bare `Literal` type
  aliases for `LogLevel` and `LogOutput` with a Pydantic model (or enum) so that
  invalid values received from TOML or env vars raise a `ValueError` at config load
  time rather than silently propagating.

- **P2 – Remove `_rename_pathname_to_source` processor** (`app/logging.py`): The
  processor is unnecessary — `pathname` is a perfectly fine key. Its presence adds
  overhead on every structured log call. Remove it and update the one test that
  asserts `"source" in data` to expect `"pathname"` instead.

- **P3 – Extract query-dispatch helper in `main.py`**: The 8-line
  `for query_item in request.queries` loop is duplicated verbatim in
  `query_latest_graph` and `query_graph`. Extract it into a private helper function
  in the same file. No new tests required; existing endpoint tests cover the behavior.

- **P4 – XML path constants in `graph_service.py`**: List literals like
  `["graph", "nodes", "node"]` are repeated inline in `from_xml_file`. Define
  module-level constants (e.g., `_PATH_GRAPH_NODE = ["graph", "nodes", "node"]`)
  to reduce typo risk and improve readability.

- **P5 – Extract `_insert_graph` helper in `conftest.py`**: `make_sample_graph_1`
  and `make_sample_graph_3` repeat the same add/flush pattern for graphs, nodes,
  and edges. Extract a private `_insert_graph(session, graph, nodes, edges)` helper
  and call it from both functions. No separate test case required.

## Impact
- Affected specs: `app-config` (new runtime validation requirement for log config)
- Affected code: `app/config.py`, `app/logging.py`, `app/main.py`,
  `app/services/graph_service.py`, `app/tests/conftest.py`,
  `app/tests/test_logging.py`
