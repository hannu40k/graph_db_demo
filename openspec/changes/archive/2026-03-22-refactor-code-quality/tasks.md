# Tasks: refactor-code-quality

Tasks are ordered by priority. Each can be implemented and verified independently.

## P1 – Config value validation

- [x] 1.1 Convert `LogLevel` and `LogOutput` from bare `Literal` aliases to a
      validated type (Pydantic `BaseModel` field or `enum.Enum`) in `app/config.py`
- [x] 1.2 Update `LoggingConfig` construction in `load_config` and
      `_apply_log_env_overrides` to raise `ValueError` on invalid values
- [x] 1.3 Add tests: invalid `level` value raises `ValueError`; invalid `output`
      value raises `ValueError`; valid values still load correctly
- [x] 1.4 Run `uv run ruff check app && uv run ty check app && uv run pytest`

## P2 – Remove `_rename_pathname_to_source` processor

- [x] 2.1 Remove the `_rename_pathname_to_source` function from `app/logging.py`
- [x] 2.2 Remove its reference from the `ProcessorFormatter` processors list in
      `configure_logging`
- [x] 2.3 Update `app/tests/test_logging.py:179` — change `"source"` assertion to
      `"pathname"`
- [x] 2.4 Run `uv run ruff check app && uv run ty check app && uv run pytest`

## P3 – Extract query-dispatch helper in `main.py`

- [x] 3.1 Extract the repeated `for query_item in request.queries` loop into a
      private function (e.g., `_execute_queries(graph, request, graph_service)`)
      in `app/main.py`
- [x] 3.2 Replace both inline copies with calls to the new helper
- [x] 3.3 Run `uv run ruff check app && uv run ty check app && uv run pytest`

## P4 – XML path constants in `graph_service.py`

- [x] 4.1 Define module-level constants for each distinct path list used in
      `XmlGraphParser.from_xml_file` (e.g., `_PATH_GRAPH_EDGES`,
      `_PATH_GRAPH_NODES_NODE`, `_PATH_GRAPH_EDGES_NODE`, etc.)
- [x] 4.2 Replace all inline list literals in `from_xml_file` with the constants
- [x] 4.3 Run `uv run ruff check app && uv run ty check app && uv run pytest`

## P5 – Extract `_insert_graph` test helper in `conftest.py`

- [x] 5.1 Add a private helper `_insert_graph(session, graph, nodes, edges)` to
      `app/tests/conftest.py` that encapsulates the add/flush/commit pattern
- [x] 5.2 Refactor `make_sample_graph_1` and `make_sample_graph_3` to use the
      helper
- [x] 5.3 Run `uv run pytest`
